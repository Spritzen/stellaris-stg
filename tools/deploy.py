#!/usr/bin/env python3
"""Link Star Trek Galaxies into the live Paradox mod folder.

The mod folder gets a SYMLINK to stg-build/, not a copy of it. A copy was a
16 GB write on every rebuild, and the failure it caused is the reason this is a
link: on 2026-08-02 the deployed copy sat five hours behind the built tree, so
the next live run would have measured the pre-repair build and nothing would
have said so. A link cannot go stale. Decision 12.

The Stellaris launcher runs on the host, outside this container, so the `path`
written into the .mod file has to make sense to IT -- /paradox/stellaris/mod is
a container path that does not exist out there.

Which host path it understands depends on which build of the game is installed,
so this script asks rather than assumes: `launcher-settings.json:gameDataPath`
names `%USER_DOCUMENTS%` for the Windows build and `$LINUX_DATA_HOME` for the
native Linux one. Both forms are live code because Steam's compatibility toggle
flips between them -- see .docs/decisions/14-native-linux-runtime.md.

    native Linux  path="/home/<user>/.local/share/Paradox Interactive/Stellaris/mod/<mod_id>"
    Windows/Proton path="C:/users/steamuser/Documents/Paradox Interactive/Stellaris/mod/<mod_id>"

Either way we start by translating the container path back to the host directory
it is bind-mounted from (the mount in .devcontainer/devcontainer.json is the
single source of truth; $HOST_PARADOX_MOD_DIR overrides). For Proton we then swap
the prefix's pfx/drive_c stem for C:. $MOD_PATH overrides the result outright.

The symlink target is a host path for the same reason, which means it reads as
BROKEN from inside the container and is correct to the game. Do not "fix" it.

The Proton form was confirmed against a live run -- see
.docs/decisions/06-launcher-local-mod-registration.md, which settled the
derivation and is still the reasoning behind it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "stg-build"


def game_platform() -> str | None:
    """Which build of Stellaris is installed: "linux", "windows", or unknown.

    Read from the game's own launcher-settings.json rather than sniffed from the
    binary, because gameDataPath is the exact thing we need to agree with: it is
    where the launcher puts its user data, and its token differs per platform.
    Steam's "force compatibility tool" checkbox swaps the whole depot, so this
    can change under us -- on 2026-08-02 it did. Decision 14.
    """
    settings = Path(os.environ.get("STELLARIS_GAME_DIR", "/stellaris")) \
        / "launcher-settings.json"
    try:
        data_path = json.loads(settings.read_text(encoding="utf-8-sig"))["gameDataPath"]
    except (OSError, ValueError, KeyError):
        return None
    if "$LINUX_DATA_HOME" in data_path:
        return "linux"
    if "%USER_DOCUMENTS%" in data_path:
        return "windows"
    return None


def host_mod_dir(container_dir: Path) -> str | None:
    """Translate a container path back to its host path via the bind mounts.

    Reads devcontainer.json rather than hardcoding a username. Matches the
    longest mount target that is a prefix of container_dir and appends the
    remainder, so a path *inside* a mount resolves too -- /paradox/stellaris/mod
    is reached through the /paradox/stellaris bind, not a mount of its own.
    """
    override = os.environ.get("HOST_PARADOX_MOD_DIR")
    if override:
        return override.rstrip("/")

    dc = REPO / ".devcontainer" / "devcontainer.json"
    if not dc.is_file():
        return None

    mounts = re.findall(r'source=([^,"]+),\s*target=([^,"]+)',
                        dc.read_text(encoding="utf-8"))
    best: tuple[int, str] | None = None
    for source, target in mounts:
        target = target.rstrip("/")
        try:
            rest = container_dir.relative_to(target)
        except ValueError:
            continue
        host = source.rstrip("/")
        if str(rest) != ".":
            host = f"{host}/{rest.as_posix()}"
        if best is None or len(target) > best[0]:
            best = (len(target), host)
    return best[1] if best else None


def windows_path(host_dir: str | None, mod_id: str) -> str | None:
    """Render the deploy target as a Proton-side launcher sees it.

    Under Proton the launcher is Windows-side and reads Windows paths. A Wine
    prefix maps `<prefix>/pfx/drive_c` to `C:`, so a host path inside the prefix
    translates by swapping that stem for the drive letter. Forward slashes: that
    is what this launcher writes in its own .mod files
    (`path="S:/workshop/content/281990/819148835"`), even though it stores
    backslashes in launcher-v2.sqlite.

    Returns None when the target is not inside a prefix, leaving the caller to
    fall back to the user-dir-relative form.
    """
    if not host_dir:
        return None
    m = re.search(r"/pfx/drive_([a-z])/(.*)$", host_dir)
    if not m:
        return None
    return f"{m.group(1).upper()}:/{m.group(2)}/{mod_id}"


def launcher_path(host_dir: str | None, mod_id: str, platform: str | None) -> str | None:
    """Render the deploy target as the installed launcher reads paths.

    Native Linux wants the plain host path -- that is the form the 33 Workshop
    .mod files written during this machine's native era carry, and decision 06
    warned only against reading them as evidence about *Proton*, which is no
    longer what is installed.
    """
    if platform == "linux":
        return f"{host_dir}/{mod_id}" if host_dir else None
    return windows_path(host_dir, mod_id)


def check_mount_matches_platform(host_dir: str | None, platform: str | None) -> str | None:
    """Return an error when the mounted user-data folder is the wrong one.

    The mount is fixed at container build time and the game's platform is not,
    so flipping Steam's compatibility toggle leaves them disagreeing until the
    container is rebuilt. Deploying across that disagreement writes a perfectly
    correct mod folder into a directory nothing reads -- which is precisely the
    failure decision 06 cost a session to diagnose. Fail loudly instead.
    """
    if not host_dir or platform is None:
        return None
    in_prefix = "/pfx/drive_" in host_dir
    if platform == "linux" and in_prefix:
        return ("the installed game is the NATIVE LINUX build, but "
                f"{host_dir}\n       is inside the Proton prefix — a folder it "
                "never reads.")
    if platform == "windows" and not in_prefix:
        return ("the installed game is the WINDOWS build under Proton, but "
                f"{host_dir}\n       is outside the prefix — a folder it never "
                "reads.")
    return None


def parse_descriptor(path: Path) -> dict[str, object]:
    """Pull name/version/supported_version/tags out of descriptor.mod."""
    text = path.read_text(encoding="utf-8-sig")
    out: dict[str, object] = {}
    for key in ("name", "version", "supported_version", "picture"):
        m = re.search(rf'^\s*{key}\s*=\s*"([^"]*)"', text, re.M)
        if m:
            out[key] = m.group(1)
    tags = re.search(r"tags\s*=\s*\{(.*?)\}", text, re.S)
    out["tags"] = re.findall(r'"([^"]+)"', tags.group(1)) if tags else []
    return out


def render_mod_file(desc: dict[str, object], rel_path: str) -> str:
    lines = [f'name="{desc.get("name", "Unnamed Mod")}"']
    if desc.get("version"):
        lines.append(f'version="{desc["version"]}"')
    tags = desc.get("tags") or []
    if tags:
        lines.append("tags={")
        lines.extend(f'\t"{t}"' for t in tags)  # type: ignore[union-attr]
        lines.append("}")
    if desc.get("supported_version"):
        lines.append(f'supported_version="{desc["supported_version"]}"')
    lines.append(f'path="{rel_path}"')
    return "\n".join(lines) + "\n"


def remove(path: Path) -> None:
    """Delete a deploy target, whatever shape it is in.

    Checked explicitly rather than trusting rmtree: getting this wrong on a
    symlink that points into the workspace deletes the repo.
    """
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clean", action="store_true", help="remove the linked mod and exit")
    ap.add_argument("--mod-file", action="store_true",
                    help="rewrite only the .mod descriptor, without relinking")
    args = ap.parse_args()

    mod_id = os.environ.get("MOD_ID", "star_trek_galaxies")
    mod_root = Path(os.environ.get("PARADOX_MOD_DIR", "/paradox/stellaris/mod"))
    host_ws = os.environ.get("HOST_WORKSPACE")

    if not mod_root.is_dir():
        print(f"error: paradox mod dir not mounted at {mod_root}", file=sys.stderr)
        return 1

    dest = mod_root / mod_id
    mod_file = mod_root / f"{mod_id}.mod"

    if args.clean:
        for p in (dest, mod_file):
            remove(p)
        print(f"removed {dest} and {mod_file}")
        return 0

    descriptor = BUILD / "descriptor.mod"
    if not descriptor.is_file():
        print("error: stg-build/descriptor.mod not found -- run: make vendor",
              file=sys.stderr)
        return 1
    desc = parse_descriptor(descriptor)

    host_dir = host_mod_dir(mod_root)
    platform = game_platform()
    override = os.environ.get("MOD_PATH")

    # $MOD_PATH means the caller has decided; skip the guard rather than block
    # the escape hatch the guard's own message points at.
    if not override:
        mismatch = check_mount_matches_platform(host_dir, platform)
        if mismatch:
            print(f"error: {mismatch}\n"
                  "       Point the /paradox/stellaris mount in "
                  ".devcontainer/devcontainer.json at the\n"
                  "       folder that build uses and rebuild the container "
                  "(decision 14),\n"
                  "       or override with $PARADOX_MOD_DIR and $MOD_PATH.",
                  file=sys.stderr)
            return 1

    mod_path = override or launcher_path(host_dir, mod_id, platform) \
        or f"mod/{mod_id}"

    if args.mod_file:
        mod_file.write_text(render_mod_file(desc, mod_path), encoding="utf-8")
        print(f"wrote   {mod_file}\n        path=\"{mod_path}\"\n"
              f"        on host: {host_dir or '?'}/{mod_id}")
        return 0

    if not host_ws:
        print("error: HOST_WORKSPACE is not set, so the host path the symlink "
              "must point at cannot be derived.\n"
              "       It comes from .devcontainer/devcontainer.json — rebuild "
              "the container, or set it by hand.", file=sys.stderr)
        return 1

    remove(dest)
    # One link to one directory: stg-build/ is the whole mod, so there is no
    # exclude list to forget an entry from (decision 12). The target is a HOST
    # path -- broken from inside the container, correct to the game. Do not
    # "fix" it.
    dest.symlink_to(f"{host_ws}/stg-build")
    print(f"linked  {dest}\n     -> {host_ws}/stg-build")

    mod_file.write_text(render_mod_file(desc, mod_path), encoding="utf-8")
    print(f"wrote   {mod_file}\n        path=\"{mod_path}\"")
    print(f"\n{desc.get('name')} v{desc.get('version')} "
          f"(supports {desc.get('supported_version')}) is ready.")
    print("Enable it in the Stellaris launcher under Mods.\n"
          "This is a link, so `make vendor` alone updates what the game reads — "
          "run it again only if the mod folder is wiped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
