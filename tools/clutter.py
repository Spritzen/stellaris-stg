#!/usr/bin/env python3
"""The dual of every check in validate.py: is this FILE referenced by anything?

    make clutter              census the built tree
    make clutter-vanilla      the same closure over /stellaris -- the floor
    make clutter ARGS=--list  every orphan, path by path

tools/validate.py asks the forward question -- does this reference resolve? --
in a dozen forms, and it has been asked about mesh names, mesh files, textures,
`.anim` and `attach`. Nothing has ever asked the reverse, which is why the tree
carries a fourth, unnamed class of file: content that arrived because it was
inside a directory we included, and that nothing anywhere refers to.

Every file lands in exactly one of four classes:

  reachable   a root the engine enters names it, directly or through a chain
  shadowing   it sits at a vanilla path on purpose, so vanilla's own references
              reach it (decision 08) -- nothing of ours needs to name it
  kept        `clutter_keep:` in vendor.yml names it, with a written reason
  orphan      none of the above

See .docs/validation/clutter.md and .docs/decisions/45-clutter-pass.md.

THE ONE THING TO UNDERSTAND BEFORE TRUSTING A FINDING. This closure deletes,
where every other check here only reports, so its two errors are not
symmetrical: an edge type it fails to follow becomes a deleted file that
rendered perfectly. So it is deliberately GENEROUS at every choice -- a
reference resolves by exact path, then by filename, then by stem, against the
built tree and vanilla at once; a declaration file is a root wherever it sits;
a `.mesh` is scanned as bytes because it names its textures inside the binary.
Over-approximating reachability costs a file left in the tree. The other
direction costs a screen going blank, and that is the failure decisions 24, 34
and 37 already record three times over, one file type further down each time.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from fnmatch import fnmatch
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "stg-build"
MANIFEST = REPO / "vendor.yml"
GAME_DIR = Path(os.environ.get("STELLARIS_GAME_DIR", "/stellaris"))

RED, YEL, GRN, CYA, DIM, OFF = (
    "\033[31m", "\033[33m", "\033[32m", "\033[36m", "\033[2m", "\033[0m",
)

# ── what the engine reads ─────────────────────────────────────────────────────
#
# The top-level directories a Stellaris mod can contribute to. The vanilla
# calibration run is restricted to these so the two trees are compared like with
# like: /stellaris also carries dlc/, pdx_launcher/, previewer_assets/ and
# licenses/, none of which a mod tree has or the engine's script loader reads.
MOD_DIRS = {
    "common", "events", "flags", "fonts", "gfx", "interface", "localisation",
    "map", "music", "prescripted_countries", "sound", "unchecked_defines",
}

# Extensions the engine reads as DECLARATIONS, and which it finds by walking a
# directory rather than by being told a filename. Every one of these is a root.
#
# Generous on purpose, and cheap to be: a declaration file that is genuinely
# unreferenced is worth a few KB, while treating one as an orphan would delete
# the thing that makes a whole directory of art reachable. The junk tier
# (.bak, .wip, .pdn) is handled by `global_excludes:` in vendor.yml instead --
# see .docs/decisions/45-clutter-pass.md phase 1 -- precisely because it is not a reachability
# question and this closure should not be asked to answer it.
DECLARATION_EXTS = {
    ".txt", ".gfx", ".gui", ".asset", ".yml", ".shader", ".fxh", ".settings",
    ".mod", ".dlc", ".json",
}

# Leaf content: named by a declaration, never found by walking. These are what
# the closure is actually about -- 20,600 of the built tree's 23,555 files.
ASSET_EXTS = {
    ".dds", ".tga", ".png", ".jpg", ".bmp", ".mesh", ".anim", ".animsm",
    ".wav", ".ogg", ".mp3", ".flac", ".m4r", ".ttf", ".otf", ".ttc", ".fnt",
    ".cur", ".ani", ".swatch",
}

# Directories whose every file the engine picks up by EXISTENCE or by deriving
# the path from a database key, with no file naming it. THIS IS THE LIST THAT
# DELETES CONTENT IF IT IS WRONG, so every entry carries the vanilla count that
# put it here -- measured by running this closure over /stellaris alone, where
# a convention the closure cannot see shows up as a directory that is almost
# entirely unreferenced. See .docs/validation/clutter.md on the root set.
ROOT_DIRS = (
    # Random pick by directory: vanilla ships 21 loading screens, and no file
    # in the tree names one.
    "gfx/loadingscreens/*",
    # Enumerated per category directory -- vanilla's 1,047 flag files are named
    # by nothing, and the empire designer lists the folder.
    "flags/*",
    # Fixed filenames the engine opens itself (pdxmesh.shader is the one
    # decision 34 turned on), plus the .fxh chain they include.
    "gfx/FX/*",
    "fonts/*",
    "gfx/fonts/*",
    "gfx/cursors/*",
    # Path derived from a database key, in a dozen databases at once:
    # gfx/interface/icons/deposits/d_ash_storms.dds is `d_ash_storms` in
    # common/deposits, and 1,600 of vanilla's 4,579 unreferenced icons are
    # literally a depth-0 key in some common/ file. The rest are the same
    # convention with an affix the closure cannot reconstruct -- achievements
    # carry a `_locked` twin, and no achievement database exists on disk at all.
    "gfx/interface/icons/*",
    # <graphical_culture>_city_l0N[_devastated].dds, from common/graphical_culture.
    # Vanilla: 361 unreferenced against 1 reachable.
    "gfx/portraits/city_sets/*",
    # pc_<planet_class>_sky*.dds, from common/planet_classes. 152 against 2.
    "gfx/portraits/environments/*",
    # Planet-view backdrops picked by arkship stage. 20 against 0.
    "gfx/portraits/arkships/*",
    # Galaxy-map art the renderer opens by fixed name (hexgrid, galaxycolor,
    # edge, dust) plus star_classes/<key>.dds from common/star_classes.
    # 38 against 39 -- the whole directory is half convention.
    "gfx/map/*",
    # Matched against the mesh or entity it animates: 99 of vanilla's 100
    # .animsm files are named by nothing anywhere, and the one .gfx that shares
    # a stem with one names the .mesh, never the state machine. The sibling
    # .editordata is deliberately NOT a root -- vanilla ships 99 of those and
    # they are editor output, which is a finding rather than a blind spot.
    "gfx/animation_state_machines/*.animsm",
)

# Single files the engine opens by a name compiled into it.
ROOT_FILES = {
    "descriptor.mod",
    "gfx/lenscolor.dds", "gfx/lensdirt.dds", "gfx/transparent.dds",
    "gfx/exe_icon.bmp",
}

# ── reference extraction ──────────────────────────────────────────────────────
#
# ONE regex over every text file, rather than one per keyword. validate.py's
# forward checks each target a specific field (`file =`, `texture_diffuse =`,
# `texturefile =`) because they must not report a false dangling reference. The
# reverse question wants the opposite bias: any token in any file that looks
# like an asset filename is treated as naming it. `entity = "x"` and
# `shader = "y"` are NOT followed and do not need to be -- they name
# declarations, and every declaration file is already a root.
_EXT_ALT = "|".join(sorted(e[1:] for e in ASSET_EXTS))
_REF_RE = re.compile(rf'[\w\-./\\]+\.(?:{_EXT_ALT})\b', re.IGNORECASE)
# A reference that omits the extension, which the engine supplies. `.anim` and
# `.animsm` are named this way constantly -- vanilla's portrait entities ask for
# `animation = "avian_01_happy_animation"` and its state machines are named
# without a suffix anywhere. Resolved by STEM only (see resolve()), so this is
# the loosest edge here and deliberately so: it reached 1,332 files the
# extension form missed, 170 of them the whole gfx/animation_state_machines
# tier, and being loose only ever leaves a file in the tree.
_QUOTED_RE = re.compile(r'"([\w\-./\\]{2,120})"')
# Printable runs inside a binary. A .mesh names its textures in plain ASCII --
# vanilla's danielsfinatestskepp.mesh carries "ship_mask.dds", "nonormal.dds"
# and "nospec.dds" and no text file in the tree mentions them.
_ASCII_RUN = re.compile(rb"[\x20-\x7e]{4,}")


def read_text(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8", "replace")
    except OSError:
        return ""


def refs_from_text(path: Path) -> set[str]:
    text = read_text(path)
    return set(_REF_RE.findall(text)) | set(_QUOTED_RE.findall(text))


def refs_from_binary(path: Path) -> set[str]:
    try:
        blob = path.read_bytes()
    except OSError:
        return set()
    out: set[str] = set()
    for run in _ASCII_RUN.findall(blob):
        out.update(_REF_RE.findall(run.decode("ascii", "replace")))
    return out


# Binaries worth scanning for names. A .dds or .wav names nothing.
BINARY_REF_EXTS = {".mesh", ".anim", ".animsm"}


def references(path: Path) -> set[str]:
    ext = path.suffix.lower()
    if ext in BINARY_REF_EXTS:
        return refs_from_binary(path)
    if ext in ASSET_EXTS:
        return set()
    return refs_from_text(path)


# ── the tree ──────────────────────────────────────────────────────────────────


class Tree:
    """Every file in one tree, indexed the three ways a reference can resolve."""

    def __init__(self, root: Path, dirs: set[str] | None = None):
        self.root = root
        self.files: list[str] = []
        for top in sorted(root.iterdir()):
            if dirs is not None and top.name not in dirs:
                continue
            if top.is_file():
                self.files.append(top.name)
                continue
            for p in top.rglob("*"):
                if p.is_file():
                    self.files.append(p.relative_to(root).as_posix())
        self.files.sort()

        self.by_path: dict[str, str] = {}
        self.by_name: dict[str, list[str]] = defaultdict(list)
        self.by_stem: dict[str, list[str]] = defaultdict(list)
        for rel in self.files:
            low = rel.lower()
            self.by_path[low] = rel
            name = low.rsplit("/", 1)[-1]
            self.by_name[name].append(rel)
            self.by_stem[name.rsplit(".", 1)[0]].append(rel)


def resolve(ref: str, home: str, *trees: Tree) -> list[tuple[Tree, str]]:
    """Every file any tree holds that this reference could name.

    Three forms, tried in order and returning at the first that hits anywhere:

      1. a path from the mod root -- `file = "gfx/models/x/y.mesh"`
      2. the same path taken relative to the declaring file's own directory
      3. the bare filename, then the bare STEM, against every file loaded

    Form 3 is decision 24's finding turned around: the engine keeps one global
    texture index keyed by basename and says so itself when two directories
    collide under one name, so a bare `texture_diffuse = "foo.dds"` reaches a
    file anywhere in the tree. Matching the stem as well as the name is
    vanilla's own behaviour -- its _other_meshes.gfx asks for five `.tga` files
    it ships only as `.dds`.
    """
    ref = ref.replace("\\", "/").lstrip("/").lower()
    candidates = [ref]
    if home:
        candidates.append(f"{home}/{ref}")
    hits: list[tuple[Tree, str]] = []
    for cand in candidates:
        for tree in trees:
            got = tree.by_path.get(cand)
            if got:
                hits.append((tree, got))
        if hits:
            return hits

    name = ref.rsplit("/", 1)[-1]
    for index in ("by_name", "by_stem"):
        key = name if index == "by_name" else name.rsplit(".", 1)[0]
        for tree in trees:
            for got in getattr(tree, index).get(key, ()):
                hits.append((tree, got))
        if hits:
            return hits
    return []


def is_root(rel: str) -> bool:
    if rel in ROOT_FILES:
        return True
    # fnmatch's '*' spans '/', so one trailing star covers a whole subtree.
    if any(fnmatch(rel, pat) for pat in ROOT_DIRS):
        return True
    ext = "." + rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
    return ext in DECLARATION_EXTS


# ── the closure ───────────────────────────────────────────────────────────────


def closure(target: Tree, *index: Tree) -> set[str]:
    """Every file in `target` some root reaches. Breadth-first over references.

    Resolution reads `index` as well as `target` so that a reference satisfied
    by vanilla is not chased into the built tree by accident -- but a hit is
    recorded for every tree that has one, because a mod file and a vanilla file
    at one basename are both plausible targets and this closure guesses in the
    direction that keeps files.
    """
    trees = (target, *index)
    reached: set[str] = set()
    queue: list[str] = []
    for rel in target.files:
        if is_root(rel):
            reached.add(rel)
            queue.append(rel)

    while queue:
        rel = queue.pop()
        home = rel.rsplit("/", 1)[0] if "/" in rel else ""
        for ref in references(target.root / rel):
            for tree, hit in resolve(ref, home, *trees):
                if tree is target and hit not in reached:
                    reached.add(hit)
                    queue.append(hit)
    return reached


# ── classification ────────────────────────────────────────────────────────────


def tier(rel: str) -> str:
    """The reporting bucket. Calibration is per tier, because the vanilla floor
    is not one number: a tier whose floor is near zero can gate, and one whose
    floor is high can only report."""
    parts = rel.split("/")
    if parts[0] in ("gfx", "common") and len(parts) > 2:
        return f"{parts[0]}/{parts[1]}"
    return parts[0]


# ── calibration ───────────────────────────────────────────────────────────────
#
# THE FALSE-POSITIVE FLOOR, measured 2026-08-07 by `make clutter-vanilla`:
# this exact closure over /stellaris alone, where every finding is by
# construction a file vanilla ships and vanilla itself never names.
#
#   42,335 files examined, 1,132 unreferenced -- 2.67% overall
#
# The residue is real: 99 `.editordata` (animation-editor output), 6 `.bak`,
# 2 `.ods` spreadsheets in common/component_templates, 2 `.csv`, and ~950
# meshes, anims, textures and wavs Paradox shipped and stopped using --
# gfx/models/portraits/avian/avian_05_portrait_sad_2.anim is there, and
# vanilla's own _avian_portrait_animations.asset declares avian_01, 02, 04 and
# 06 while shipping 05's four anims. So this is not blindness in the closure;
# it is that vanilla has the fourth class too.
#
# {tier: (orphans, files)} -- the ratio, not the count, is what a finding is
# read against, and it is per tier because it varies 30-fold between them.
VANILLA_FLOOR = {
    "gfx/models": (695, 14049),           # 4.9%
    "gfx/interface": (199, 12019),        # 1.7%
    "sound": (110, 7005),                 # 1.6%
    "gfx/particles": (17, 1276),          # 1.3%
    "gfx/event_pictures": (2, 639),       # 0.3%
    "gfx/portraits": (0, 797),            # 0.0%  (after the three root dirs)
    "gfx/worldgfx": (1, 41),
    "interface": (0, 320),
    "music": (0, 44),
    "flags": (0, 1047),
    "localisation": (0, 2320),
    "events": (0, 170),
    "map": (0, 7),
    "prescripted_countries": (0, 20),
}

# Tiers the prune is allowed to DELETE from, and nothing else. Scope is a
# calibration result, not a convenience filter (.docs/validation/check-design.md rule 11), so the ratio that
# earned each entry is written beside it and the tiers left out say why.
#
# The stg-build column is the measurement that EARNED each verdict, taken on
# 2026-08-07 before the prune first ran. `make clutter` prints today's figures;
# the three PRUNE tiers now sit at zero by construction, which is the point.
#
#   tier                floor    stg-build    verdict
#   gfx/event_pictures   0.3%   813 / 1,434   prune -- 190x the floor, and the
#                                             edge is a single hop: a texture
#                                             no spriteType names cannot draw
#   gfx/portraits        0.0%    72 / 3,919   prune -- floor is zero over 797
#                                             non-convention vanilla files
#   sound                1.6%   107 /   886   prune -- 7.5x. STNH ships 73
#                                             weapon .wav files and declares
#                                             none of them in any .asset, in
#                                             its own tree or anywhere in
#                                             /workshop
#   gfx/models           4.9%   634 / 11,943  REPORT -- that is 5.3% against
#                                             vanilla's own 4.9%; at that rate
#                                             the check cannot tell our
#                                             leftovers from Paradox's
#   gfx/interface        1.7%    24 /  2,254  REPORT -- 1.1%, below the floor
#   gfx/particles        1.3%    22 /    591  REPORT -- 3.7%, same order
#   gfx/ui_overhaul_qhd    --    28 /    412  REPORT -- mod-only path, so there
#                                             is no vanilla floor to read it
#                                             against at all
PRUNE_TIERS = ("gfx/event_pictures", "gfx/portraits", "sound")


def load_keeps() -> list[dict]:
    if not MANIFEST.is_file():
        return []
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    keeps = data.get("clutter_keep") or []
    for i, entry in enumerate(keeps):
        if not isinstance(entry, dict) or not entry.get("path"):
            raise SystemExit(f"{RED}error{OFF} vendor.yml: clutter_keep[{i}] "
                             f"needs a 'path'")
        if not entry.get("why"):
            raise SystemExit(
                f"{RED}error{OFF} vendor.yml: clutter_keep[{i}] "
                f"({entry['path']}) has no 'why'. A kept file with no recorded "
                f"reason is indistinguishable from one nobody looked at -- and "
                f"the reason must be a correctness argument, never a cost "
                f"estimate. See .docs/validation/acks.md.")
    return keeps


def kept_by(rel: str, keeps: list[dict]) -> str | None:
    for entry in keeps:
        pat = entry["path"]
        if rel == pat or fnmatch(rel, pat) or rel.startswith(pat.rstrip("/") + "/"):
            return " ".join(str(entry["why"]).split())
    return None


def classify(target: Tree, vanilla: Tree | None, keeps: list[dict]) -> dict[str, str]:
    """rel -> one of reachable / shadowing / kept / orphan."""
    reached = closure(target, *( (vanilla,) if vanilla else () ))
    out: dict[str, str] = {}
    for rel in target.files:
        if rel in reached:
            out[rel] = "reachable"
        elif vanilla and rel.lower() in vanilla.by_path:
            out[rel] = "shadowing"
        elif kept_by(rel, keeps):
            out[rel] = "kept"
        else:
            out[rel] = "orphan"
    return out


# ── reporting ─────────────────────────────────────────────────────────────────


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}GB"


def size_of(root: Path, rel: str) -> int:
    try:
        return (root / rel).stat().st_size
    except OSError:
        return 0


def report(root: Path, verdicts: dict[str, str], *, title: str,
           list_orphans, calibrated: bool) -> int:
    rows: dict[str, dict[str, int]] = defaultdict(
        lambda: {"reachable": 0, "shadowing": 0, "kept": 0, "orphan": 0,
                 "bytes": 0})
    for rel, verdict in verdicts.items():
        row = rows[tier(rel)]
        row[verdict] += 1
        row["files"] = row.get("files", 0) + 1
        if verdict == "orphan":
            row["bytes"] += size_of(root, rel)

    print(f"\n{title}\n")
    head = (f"  {'tier':<24} {'reach':>7} {'shadow':>7} {'kept':>6} "
            f"{'ORPHAN':>7} {'size':>9}")
    if calibrated:
        head += f"  {'rate':>6} {'floor':>6}  scope"
    print(head)
    print(f"  {'-' * (len(head) + 4)}")
    total: dict[str, int] = defaultdict(int)
    for name in sorted(rows, key=lambda t: -rows[t]["orphan"]):
        r = rows[name]
        for k, v in r.items():
            total[k] += v
        mark = YEL if r["orphan"] else DIM
        line = (f"  {name:<24} {r['reachable']:>7} {r['shadowing']:>7} "
                f"{r['kept']:>6} {mark}{r['orphan']:>7}{OFF} "
                f"{human(r['bytes']):>9}")
        if calibrated:
            got, seen = VANILLA_FLOOR.get(name, (0, 0))
            floor = f"{got / seen:.1%}" if seen else "—"
            scope = "PRUNE" if name in PRUNE_TIERS else "report"
            line += (f"  {r['orphan'] / max(r['files'], 1):>6.1%} "
                     f"{floor:>6}  {scope}")
        print(line)
    print(f"  {'-' * (len(head) + 4)}")
    print(f"  {'total':<24} {total['reachable']:>7} {total['shadowing']:>7} "
          f"{total['kept']:>6} {total['orphan']:>7} {human(total['bytes']):>9}")

    if list_orphans:
        print()
        for rel in sorted(r for r, v in verdicts.items() if v == "orphan"):
            if list_orphans is True or tier(rel).startswith(list_orphans):
                print(f"  {rel}")
    return total["orphan"]


def build_verdicts() -> tuple[Tree, dict[str, str]]:
    """The census tools/vendor.py and tools/validate.py both read."""
    van = Tree(GAME_DIR, MOD_DIRS) if GAME_DIR.is_dir() else None
    tree = Tree(BUILD)
    return tree, classify(tree, van, load_keeps())


def prunable(verdicts: dict[str, str]) -> list[str]:
    """Orphans inside the calibrated prune scope, and nothing else."""
    return sorted(r for r, v in verdicts.items()
                  if v == "orphan" and tier(r) in PRUNE_TIERS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vanilla", action="store_true",
                    help="run the closure over /stellaris alone -- the "
                         "false-positive floor every finding is read against")
    ap.add_argument("--list", nargs="?", const=True, metavar="TIER",
                    help="print every orphan path, optionally one tier only")
    args = ap.parse_args()

    if args.vanilla:
        if not GAME_DIR.is_dir():
            raise SystemExit(f"{RED}error{OFF} no vanilla tree at {GAME_DIR}")
        van = Tree(GAME_DIR, MOD_DIRS)
        verdicts = classify(van, None, [])
        n = report(GAME_DIR, verdicts,
                   title=f"{CYA}vanilla floor{OFF} — the same closure over "
                         f"{GAME_DIR}, nothing else loaded",
                   list_orphans=args.list, calibrated=False)
        print(f"\n  {len(van.files):,} files examined, {n:,} unreferenced "
              f"({n / max(len(van.files), 1):.2%})")
        print(f"{DIM}  Every finding here is a false positive by construction. "
              f"Copy the per-tier numbers into VANILLA_FLOOR when they move."
              f"{OFF}")
        return 0

    if not BUILD.is_dir():
        raise SystemExit(f"{RED}error{OFF} no build tree — run `make vendor`")
    tree, verdicts = build_verdicts()
    n = report(BUILD, verdicts, title=f"{CYA}stg-build{OFF} — reachability census",
               list_orphans=args.list, calibrated=True)
    left = prunable(verdicts)
    print(f"\n  {len(tree.files):,} files examined, {n:,} in no class "
          f"({n / max(len(tree.files), 1):.2%})")
    if left:
        print(f"  {YEL}{len(left)} of them inside the prune scope{OFF} — "
              f"`make vendor` removes those. Anything outside it is a report.")
    else:
        print(f"  {GRN}nothing unreferenced inside the prune scope{OFF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
