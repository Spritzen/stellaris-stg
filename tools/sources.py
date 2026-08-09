#!/usr/bin/env python3
"""Snapshot the source mods into `.source/`, and diff them against `/workshop`.

`/workshop` is Steam's directory: it changes under us whenever a mod author
publishes, and it disappears entirely if we unsubscribe. Building straight out
of it means every rebuild silently picks up whatever Steam did last, and an
unsubscribe destroys the ability to rebuild at all.

So `make vendor` no longer reads `/workshop`. It reads `.source/<id>/`, a
byte-exact copy of each source mod that we take deliberately:

    /workshop/<id>          upstream, read-only, changes whenever Steam says so
      |  make sources-sync  (deliberate, reviewable)
    .source/<id>            our pinned copy -- the input to `make vendor`
      |  make vendor
    common/ gfx/ ...        the mod tree

The gap between the two is the point. `make sources-status` reports it and
`make sources-diff ID=<id>` shows it file by file, so a source-mod update is a
change you read and accept rather than one that happens to you.

    make sources-sync                  snapshot every source (or: ID=<id> for one)
    make sources-status                what changed upstream since the snapshot
    make sources-diff ID=<id>          the actual diff, file by file
    make sources-list                  what .source/ currently holds

Disk cost is near zero. `/workshop` and this repo are the same btrfs subvolume,
so the copy is a reflink -- the whole snapshot in about a second, sharing
extents with the original until one side changes. On a filesystem without
reflinks this falls back to a real copy and really does cost the full size
(22 GB across 51 sources today); `make sources-status` will tell you either way.

Metadata lives in `.source/.meta/<id>.json` (every file, with a hash), never
inside `.source/<id>/`, which stays a pure mirror. `sources.lock.yml` at the
repo root is the short human-readable version: one entry per source, with the
tree hash that identifies exactly which upstream revision is pinned.
"""

from __future__ import annotations

import argparse
import difflib
import filecmp
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from vendor import GRN, RED, YEL, CYA, DIM, OFF, die, human, load_manifest

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / ".source"
META = SOURCE / ".meta"
LOCK = REPO / "sources.lock.yml"

# Snapshots are hashed raw: they are byte copies of upstream, so there is no
# CRLF asymmetry to normalise away. Diffs DO normalise (see render_diff) --
# several sources ship CRLF and a naive diff reports every line as changed.
TEXT_SUFFIXES = {
    ".txt", ".gui", ".gfx", ".asset", ".yml", ".yaml", ".csv", ".json",
    ".mod", ".settings", ".dlc", ".md", ".shader", ".fxh", ".lua", ".ini",
}


# ── shared helpers ────────────────────────────────────────────────────────────


def sources_of(data: dict) -> list[dict]:
    return [{"id": str(s["id"]), "name": s.get("name", str(s["id"]))}
            for s in data["sources"]]


def select(data: dict, ids: list[str]) -> list[dict]:
    """Narrow the source list to the ids given, erroring on unknown ones."""
    all_sources = sources_of(data)
    if not ids:
        return all_sources
    known = {s["id"] for s in all_sources}
    for i in ids:
        if i not in known:
            die(f"'{i}' is not a source in vendor.yml. `make sources-list` shows "
                f"the {len(known)} that are.")
    return [s for s in all_sources if s["id"] in ids]


def scan(root: Path) -> dict[str, os.stat_result]:
    """Every file under root, keyed by posix path relative to it."""
    out: dict[str, os.stat_result] = {}
    if not root.is_dir():
        return out
    for path in root.rglob("*"):
        if path.is_file():
            out[path.relative_to(root).as_posix()] = path.stat()
    return out


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def hash_tree(root: Path, rels: list[str], jobs: int) -> dict[str, str]:
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        return dict(zip(rels, pool.map(lambda r: sha256(root / r), rels)))


def tree_hash(hashes: dict[str, str]) -> str:
    """One hash identifying a whole snapshot, for pinning in sources.lock.yml."""
    h = hashlib.sha256()
    for rel in sorted(hashes):
        h.update(f"{hashes[rel]}  {rel}\n".encode())
    return h.hexdigest()


def descriptor_version(root: Path) -> str:
    """The `version` a mod declares, when it declares one. Best update signal."""
    desc = root / "descriptor.mod"
    if not desc.is_file():
        return ""
    try:
        text = desc.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""
    m = re.search(r'^\s*version\s*=\s*"([^"]*)"', text, re.M)
    return m.group(1) if m else ""


def read_meta(sid: str) -> dict | None:
    path = META / f"{sid}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except ValueError:
        return None


# ── copying ───────────────────────────────────────────────────────────────────


def copy_tree(src: Path, dst: Path) -> str:
    """Copy src to dst, preferring a reflink. Returns the method used.

    Reflinks make a multi-GB snapshot cost near-nothing on btrfs/XFS while
    still being a genuinely independent copy: the two files share extents until
    one is written to, so Steam replacing a file upstream leaves ours intact.
    `--reflink=auto` degrades to a full copy anywhere that is not supported.

    Ownership is deliberately not preserved -- /workshop is owned by the host
    user and we are not root, so `cp -a` would fail on every file.
    """
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)

    cp = shutil.which("cp")
    if cp:
        proc = subprocess.run(
            [cp, "-r", "--reflink=auto", "--preserve=timestamps,mode",
             str(src), str(dst)],
            capture_output=True, text=True,
        )
        if proc.returncode == 0:
            return "reflink"
        print(f"{YEL}warn{OFF}  cp failed ({proc.stderr.strip()[:120]}); "
              f"falling back to a plain copy", file=sys.stderr)
        if dst.exists():
            shutil.rmtree(dst)

    shutil.copytree(src, dst, copy_function=shutil.copy2)
    return "copy"


# ── sync ──────────────────────────────────────────────────────────────────────


def cmd_sync(args: argparse.Namespace) -> int:
    data = load_manifest()
    upstream_root = Path(data.get("workshop_root", "/workshop"))
    targets = select(data, args.ids)
    started = time.time()

    if not args.dry_run:
        META.mkdir(parents=True, exist_ok=True)

    changed = 0
    for src in targets:
        sid, name = src["id"], src["name"]
        upstream = upstream_root / sid
        snapshot = SOURCE / sid
        previous = read_meta(sid)

        if not upstream.is_dir():
            if snapshot.is_dir():
                # Exactly the case the snapshot exists for: unsubscribed on
                # Steam, but we can still rebuild. Keep what we have.
                print(f"  {CYA}{sid:>10}{OFF}  {name:<44} {YEL}upstream gone{OFF} "
                      f"-- keeping the existing snapshot")
                continue
            die(f"source {sid} ({name}) is neither on the {upstream_root} mount "
                f"nor in .source/. Re-subscribe on Steam, or drop it from "
                f"vendor.yml.")

        if args.dry_run:
            stats = scan(upstream)
            total = sum(s.st_size for s in stats.values())
            print(f"  {CYA}{sid:>10}{OFF}  {name:<44} {len(stats):>6} files  "
                  f"{human(total):>8}  {DIM}(dry run){OFF}")
            continue

        method = copy_tree(upstream, snapshot)
        stats = scan(snapshot)
        rels = sorted(stats)
        hashes = hash_tree(snapshot, rels, args.jobs)
        total = sum(stats[r].st_size for r in rels)
        digest = tree_hash(hashes)

        meta = {
            "id": sid,
            "name": name,
            "taken": time.strftime("%Y-%m-%d %H:%M:%S"),
            "upstream": str(upstream),
            "method": method,
            "descriptor_version": descriptor_version(snapshot),
            "files": len(rels),
            "bytes": total,
            "tree_sha256": digest,
            "hashes": hashes,
        }
        (META / f"{sid}.json").write_text(json.dumps(meta, indent=1, sort_keys=True))

        if previous is None:
            state, colour = "new", GRN
        elif previous.get("tree_sha256") != digest:
            state, colour = "updated", YEL
            changed += 1
        else:
            state, colour = "unchanged", DIM
        print(f"  {CYA}{sid:>10}{OFF}  {name:<44} {len(rels):>6} files  "
              f"{human(total):>8}  {colour}{state}{OFF}")

    if args.dry_run:
        print(f"\n{YEL}dry run{OFF} — nothing written")
        return 0

    write_lock(data)
    total_files = sum(m.get("files", 0) for m in all_meta(data))
    total_bytes = sum(m.get("bytes", 0) for m in all_meta(data))
    print(f"\n{GRN}ok{OFF} — .source/ holds {total_files:,} file(s), "
          f"{human(total_bytes)} across {len(all_meta(data))} source(s); "
          f"{changed} updated in {time.time() - started:.0f}s")
    print(f"{DIM}pinned in {LOCK.name}; `make vendor` builds from .source/{OFF}")
    return 0


def all_meta(data: dict) -> list[dict]:
    out = []
    for src in sources_of(data):
        meta = read_meta(src["id"])
        if meta:
            out.append(meta)
    return out


def write_lock(data: dict) -> None:
    """The short, readable record of what .source/ pins, in harvest order."""
    lines = [
        "# Star Trek Galaxies — source snapshot lock",
        "#",
        "# Generated by `make sources-sync` — do not edit.",
        "#",
        "# What `.source/` currently holds, in vendor.yml's harvest order. This is",
        "# the pinned input to `make vendor`; /workshop is only ever read by",
        "# `make sources-sync`. `tree_sha256` identifies an upstream revision",
        "# exactly — if it is unchanged after a sync, the mod did not update.",
        "#",
        "# Per-file hashes live in .source/.meta/<id>.json.",
        "",
        "version: 1",
        "snapshots:",
    ]
    for src in sources_of(data):
        meta = read_meta(src["id"])
        if not meta:
            lines += [f'  - id: "{src["id"]}"',
                      f"    name: {yaml_str(src['name'])}",
                      "    snapshot: MISSING  # run: make sources-sync"]
            continue
        lines += [
            f'  - id: "{meta["id"]}"',
            f"    name: {yaml_str(meta['name'])}",
            f"    taken: \"{meta['taken']}\"",
            f"    files: {meta['files']}",
            f"    bytes: {meta['bytes']}",
            f"    tree_sha256: {meta['tree_sha256']}",
        ]
        if meta.get("descriptor_version"):
            lines.append(f"    descriptor_version: "
                         f"{yaml_str(meta['descriptor_version'])}")
    LOCK.write_text("\n".join(lines) + "\n", encoding="utf-8")


def yaml_str(value: str) -> str:
    """Quote anything YAML would misread — several mod names start with '!'."""
    if value and re.match(r"^[A-Za-z0-9][\w .()/&+',-]*$", value):
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ── status ────────────────────────────────────────────────────────────────────


def compare(snapshot: Path, upstream: Path, *, deep: bool, jobs: int,
            meta: dict | None) -> dict:
    """Drift between our snapshot and upstream, as three lists of paths.

    Fast path compares size and mtime, which is what a Steam update always
    changes. `deep` hashes both sides instead, catching the rewrite that
    happens to preserve both -- slower, and the only way to be certain.
    """
    snap, up = scan(snapshot), scan(upstream)
    added = sorted(set(up) - set(snap))
    removed = sorted(set(snap) - set(up))
    common = sorted(set(snap) & set(up))

    if deep:
        recorded = (meta or {}).get("hashes") or {}
        missing = [r for r in common if r not in recorded]
        snap_hashes = dict(recorded)
        snap_hashes.update(hash_tree(snapshot, missing, jobs))
        up_hashes = hash_tree(upstream, common, jobs)
        modified = [r for r in common if snap_hashes.get(r) != up_hashes[r]]
    else:
        modified = [
            r for r in common
            if snap[r].st_size != up[r].st_size
            or abs(snap[r].st_mtime - up[r].st_mtime) > 1
        ]

    return {"added": added, "removed": removed, "modified": modified}


def cmd_status(args: argparse.Namespace) -> int:
    data = load_manifest()
    upstream_root = Path(data.get("workshop_root", "/workshop"))
    targets = select(data, args.ids)

    drifted: list[tuple[dict, dict]] = []
    unsnapshotted: list[dict] = []
    orphaned: list[dict] = []
    clean = 0

    for src in targets:
        sid, name = src["id"], src["name"]
        snapshot, upstream = SOURCE / sid, upstream_root / sid

        if not snapshot.is_dir():
            unsnapshotted.append(src)
            continue
        if not upstream.is_dir():
            orphaned.append(src)
            continue

        delta = compare(snapshot, upstream, deep=args.deep, jobs=args.jobs,
                        meta=read_meta(sid))
        if any(delta.values()):
            drifted.append((src, delta))
        else:
            clean += 1

    mode = "sha256" if args.deep else "size+mtime"
    print(f"{DIM}{len(targets)} source(s) declared in vendor.yml, compared by "
          f"{mode} against {upstream_root}{OFF}\n")

    for src in unsnapshotted:
        print(f"{RED}missing{OFF}  {src['id']:>10}  {src['name']}")
        print(f"         not in .source/ — `make vendor` will fail. "
              f"Run: make sources-sync ID={src['id']}")

    for src in orphaned:
        print(f"{YEL}orphan{OFF}   {src['id']:>10}  {src['name']}")
        print(f"         snapshotted, but no longer on {upstream_root} "
              f"(unsubscribed?). The build still works — this is what "
              f".source/ is for.")

    for src, delta in drifted:
        sid = src["id"]
        counts = ", ".join(
            f"{len(delta[k])} {k}" for k in ("modified", "added", "removed")
            if delta[k]
        )
        meta = read_meta(sid) or {}
        was = meta.get("descriptor_version", "")
        now = descriptor_version(upstream_root / sid)
        version = f"  {was or '?'} → {now or '?'}" if was != now else ""
        print(f"{YEL}drift{OFF}    {sid:>10}  {src['name']}{version}")
        print(f"         {counts}   {DIM}snapshot taken "
              f"{meta.get('taken', '?')}{OFF}")
        for kind, mark in (("modified", "M"), ("added", "+"), ("removed", "-")):
            for path in delta[kind][:args.list_limit]:
                print(f"           {mark} {path}")
            extra = len(delta[kind]) - args.list_limit
            if extra > 0:
                print(f"           {DIM}… and {extra} more {kind}{OFF}")
        print(f"         {DIM}see it: make sources-diff ID={sid}   "
              f"accept it: make sources-sync ID={sid}{OFF}")

    if drifted or unsnapshotted or orphaned:
        print()
    print(f"{GRN if not (drifted or unsnapshotted) else YEL}"
          f"{clean} in sync{OFF}, {len(drifted)} drifted, "
          f"{len(unsnapshotted)} missing, {len(orphaned)} orphaned")
    if not args.deep and (drifted or clean):
        print(f"{DIM}size+mtime only; `make sources-status DEEP=1` hashes "
              f"every file{OFF}")

    return 1 if (args.exit_code and (drifted or unsnapshotted)) else 0


# ── diff ──────────────────────────────────────────────────────────────────────


def read_text(path: Path) -> list[str] | None:
    """Decoded lines with line endings normalised, or None if it is binary."""
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\0" in raw[:8192]:
        return None
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n").splitlines()


def byte_identical(old: Path, new: Path) -> bool:
    """True when two paths have the same bytes — not just the same size+mtime."""
    try:
        return (old.stat().st_size == new.stat().st_size
                and filecmp.cmp(old, new, shallow=False))
    except OSError:
        return False


def render_diff(rel: str, old: Path | None, new: Path | None,
                max_lines: int) -> list[str]:
    """One file's diff. Line endings are normalised first — several sources ship
    CRLF, and without this a 74-line change reports as 16,964 (.docs/architecture/conflict-register.md)."""
    # `status` compares size+mtime for speed, so a file Steam merely re-touched
    # reports as drift. Say outright that there is nothing to accept -- decision
    # 09 exists to keep accepting an upstream change deliberate, and wording
    # that reads like a real change trains the reader to sync reflexively.
    if old and new and byte_identical(old, new):
        return [f"{DIM}{rel}: byte-identical — only the modification time "
                f"differs. Nothing to accept; `make sources-status DEEP=1` "
                f"hashes instead and will call this in sync.{OFF}"]

    old_lines = read_text(old) if old else []
    new_lines = read_text(new) if new else []

    if old_lines is None or new_lines is None:
        old_size = old.stat().st_size if old else 0
        new_size = new.stat().st_size if new else 0
        if old and new and old_size == new_size:
            return [f"{CYA}binary{OFF} {rel}  ({human(new_size)}, same size, "
                    f"contents differ)"]
        return [f"{CYA}binary{OFF} {rel}  {human(old_size)} → {human(new_size)}"]

    diff = list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f"a/{rel}", tofile=f"b/{rel}", lineterm="", n=3,
    ))
    if not diff:
        return [f"{DIM}{rel}: differs on disk but identical once line endings "
                f"are normalised{OFF}"]

    out = []
    for line in diff[:max_lines] if max_lines else diff:
        if line.startswith("+") and not line.startswith("+++"):
            out.append(f"{GRN}{line}{OFF}")
        elif line.startswith("-") and not line.startswith("---"):
            out.append(f"{RED}{line}{OFF}")
        elif line.startswith("@@"):
            out.append(f"{CYA}{line}{OFF}")
        else:
            out.append(line)
    if max_lines and len(diff) > max_lines:
        out.append(f"{DIM}… {len(diff) - max_lines} more diff line(s); "
                   f"raise --max-lines or pass a path to narrow it{OFF}")
    return out


def cmd_diff(args: argparse.Namespace) -> int:
    data = load_manifest()
    upstream_root = Path(data.get("workshop_root", "/workshop"))
    src = select(data, [args.id])[0]
    sid = src["id"]
    snapshot, upstream = SOURCE / sid, upstream_root / sid

    if not snapshot.is_dir():
        die(f"{sid} is not snapshotted. Run: make sources-sync ID={sid}")
    if not upstream.is_dir():
        die(f"{sid} is not on the {upstream_root} mount — nothing to diff "
            f"against. The snapshot in .source/{sid} is all we have.")

    delta = compare(snapshot, upstream, deep=args.deep, jobs=args.jobs,
                    meta=read_meta(sid))
    if args.paths:
        keep = lambda p: any(p == q or p.startswith(q.rstrip("/") + "/")
                             for q in args.paths)
        delta = {k: [p for p in v if keep(p)] for k, v in delta.items()}

    total = sum(len(v) for v in delta.values())
    print(f"{DIM}{src['name']} ({sid}): .source/ → {upstream_root}, "
          f"{total} path(s) differ{OFF}\n")
    if not total:
        print(f"{GRN}ok{OFF} — in sync")
        return 0

    if args.stat:
        for kind, mark in (("modified", "M"), ("added", "+"), ("removed", "-")):
            for path in delta[kind]:
                print(f"  {mark} {path}")
        print(f"\n{len(delta['modified'])} modified, {len(delta['added'])} added, "
              f"{len(delta['removed'])} removed")
        return 0

    for path in delta["modified"]:
        print(f"\n{'─' * 78}")
        for line in render_diff(path, snapshot / path, upstream / path,
                                args.max_lines):
            print(line)
    for path in delta["added"]:
        print(f"\n{'─' * 78}\n{GRN}added upstream{OFF}  {path}")
        for line in render_diff(path, None, upstream / path, args.max_lines):
            print(line)
    for path in delta["removed"]:
        print(f"\n{'─' * 78}\n{RED}removed upstream{OFF}  {path}")

    # Only offer the sync when there is something to accept. Every path here can
    # be a file Steam re-touched without changing, and printing "accept all of
    # it" under a screen that says "byte-identical" is how sources-sync becomes
    # a reflex instead of a decision.
    if all(byte_identical(snapshot / p, upstream / p)
           for p in delta["modified"]) and not delta["added"] \
            and not delta["removed"]:
        print(f"\n{GRN}ok{OFF} — every differing path is byte-identical; the "
              f"snapshot is current and there is nothing to accept.")
    else:
        print(f"\n{DIM}accept all of it: make sources-sync ID={sid}{OFF}")
    return 0


# ── list ──────────────────────────────────────────────────────────────────────


def cmd_list(args: argparse.Namespace) -> int:
    data = load_manifest()
    targets = select(data, args.ids)
    print(f"{DIM}{'ID':>10}  {'source':<44} {'files':>7} {'size':>9}  "
          f"{'version':<10} taken{OFF}")
    files = size = 0
    for src in targets:
        meta = read_meta(src["id"])
        if not meta:
            print(f"{src['id']:>10}  {src['name']:<44} {RED}{'not snapshotted':>7}"
                  f"{OFF}")
            continue
        files += meta["files"]
        size += meta["bytes"]
        print(f"{CYA}{meta['id']:>10}{OFF}  {meta['name']:<44} "
              f"{meta['files']:>7,} {human(meta['bytes']):>9}  "
              f"{(meta.get('descriptor_version') or '—'):<10} "
              f"{DIM}{meta['taken']}{OFF}")
    print(f"\n{files:,} file(s), {human(size)} in .source/")
    return 0


# ── entry point ───────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("-j", "--jobs", type=int, default=8,
                    help="parallel hashing workers (default 8)")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("sync", help="snapshot /workshop into .source/")
    p.add_argument("ids", nargs="*", help="Workshop IDs; default all of them")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("status", help="compare /workshop against .source/")
    p.add_argument("ids", nargs="*")
    p.add_argument("--deep", action="store_true",
                   help="hash every file instead of comparing size and mtime")
    p.add_argument("--list-limit", type=int, default=12,
                   help="paths shown per category before eliding (default 12)")
    p.add_argument("--exit-code", action="store_true",
                   help="exit 1 when anything has drifted")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("diff", help="diff one source against upstream")
    p.add_argument("id")
    p.add_argument("paths", nargs="*", help="limit to these source-relative paths")
    p.add_argument("--stat", action="store_true", help="list paths, no diff bodies")
    p.add_argument("--deep", action="store_true")
    p.add_argument("--max-lines", type=int, default=200,
                   help="diff lines shown per file, 0 for all (default 200)")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("list", help="what .source/ currently holds")
    p.add_argument("ids", nargs="*")
    p.set_defaults(func=cmd_list)

    args = ap.parse_args()
    if not getattr(args, "func", None):
        ap.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
