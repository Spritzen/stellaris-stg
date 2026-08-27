#!/usr/bin/env python3
"""Replay vendor.yml into the mod tree.

Star Trek Galaxies is standalone: it carries its own copy of every source mod
it uses, so there is no runtime load order to lean on. This tool resolves that
merge at build time, in the order vendor.yml declares, and records the outcome
so a future session can audit it.

    make vendor         rebuild the tree from .source/ + src/
    make provenance     regenerate .docs/provenance.md from the last build
    make clean-vendor   remove every generated file, leaving hand-written ones

The input is `.source/`, not `/workshop`. `/workshop` is Steam's directory and
changes whenever a mod author publishes; building from it means every rebuild
silently absorbs whatever Steam did last. `.source/<id>/` is our pinned copy,
refreshed only by `make sources-sync` — see tools/sources.py.

Three invariants hold everything together:

  * The build reads only `.source/` and `src/`. A source that has not been
    snapshotted is an error, never a silent fallback to /workshop.

  * Every generated path is recorded in .vendor-manifest.json with a checksum.
    tools/validate.py compares against it, so a hand-edit to a vendored file is
    an error rather than a change silently lost on the next rebuild.
  * src/ is applied last and always wins. It is the only place hand-written
    content belongs.

Checksums normalise line endings on text files before hashing. Several sources
ship CRLF, and without normalising, a rerun would report every line of those
files as changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import statistics
import struct
import subprocess
import sys
import time
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from fnmatch import fnmatch
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
# The mod tree. The repo root is NOT the mod root: the game's directory layout
# lives under stg-build/, so "generated" and "hand-written" are separable by
# path rather than by memory, and the deploy is one symlink to one directory.
# Decision 12. Everything in here is regenerable -- never hand-edit it.
BUILD = REPO / "stg-build"
MANIFEST = REPO / "vendor.yml"
STATE = REPO / ".vendor-manifest.json"
CACHE = REPO / ".vendor-cache"
PROVENANCE = REPO / ".docs" / "provenance.md"
DEFAULT_SOURCE_ROOT = ".source"
# Read by `renames:`, to check a new filename against the files it has to
# out-sort -- vanilla's are in the same read sequence and usually the ones that
# matter -- and by `resample_to_vanilla:`, which takes its target dimensions
# from the vanilla file being shadowed. Nothing is ever written here.
GAME_DIR = Path(os.environ.get("STELLARIS_GAME_DIR", "/stellaris"))

# Suffixes hashed with line endings normalised. Everything else is hashed raw.
TEXT_SUFFIXES = {
    ".txt", ".gui", ".gfx", ".asset", ".yml", ".yaml", ".csv",
    ".json", ".mod", ".settings", ".dlc", ".md", ".shader", ".fxh",
}

RED, YEL, GRN, CYA, DIM, OFF = (
    "\033[31m", "\033[33m", "\033[32m", "\033[36m", "\033[2m", "\033[0m",
)


def die(msg: str) -> None:
    print(f"{RED}error{OFF} {msg}", file=sys.stderr)
    raise SystemExit(1)


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}GB"


# ── manifest ──────────────────────────────────────────────────────────────────


def load_manifest() -> dict:
    if not MANIFEST.is_file():
        die(f"{MANIFEST.name} not found at the repo root")
    try:
        data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        die(f"{MANIFEST.name}: {exc}")
    if not isinstance(data, dict) or not data.get("sources"):
        die(f"{MANIFEST.name}: no 'sources' declared")

    seen: set[str] = set()
    for src in data["sources"]:
        sid = str(src.get("id", ""))
        if not sid:
            die(f"{MANIFEST.name}: a source is missing its 'id'")
        if sid in seen:
            die(f"{MANIFEST.name}: source {sid} listed twice")
        seen.add(sid)
    return data


def matches(rel: str, pattern: str) -> bool:
    """Glob match against a source-relative posix path.

    fnmatch's '*' spans '/', so '**/desktop.ini' already matches at any depth;
    the stripped-prefix retry is what lets it also match at the root.
    """
    if fnmatch(rel, pattern):
        return True
    return pattern.startswith("**/") and fnmatch(rel, pattern[3:])


def included(rel: str, prefixes: list[str]) -> bool:
    if not prefixes:
        return True
    return any(rel == p or rel.startswith(p.rstrip("/") + "/") for p in prefixes)


# ── source resolution ─────────────────────────────────────────────────────────


def resolve_source_root(data: dict) -> Path:
    """Where the harvest reads from: `.source/`, unless vendor.yml says otherwise."""
    root = Path(data.get("source_root", DEFAULT_SOURCE_ROOT))
    return root if root.is_absolute() else REPO / root


def source_dir(src: dict, source_root: Path) -> Path:
    """Return the directory to harvest, unpacking the archive if it ships one."""
    sid = str(src["id"])
    mod_dir = source_root / sid
    if not mod_dir.is_dir():
        die(f"source {sid} ({src.get('name', '?')}) has not been snapshotted into "
            f"{source_root.name}/. Run: make sources-sync ID={sid}\n"
            f"      (the build never reads /workshop directly -- see "
            f"tools/sources.py)")

    archive = src.get("zip")
    if not archive:
        return mod_dir

    zip_path = mod_dir / archive
    if not zip_path.is_file():
        die(f"source {sid}: declared zip '{archive}' not found")

    dest = CACHE / sid
    stamp = dest / ".unpacked"
    if stamp.is_file() and stamp.read_text().strip() == str(zip_path.stat().st_mtime):
        return dest

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    stamp.write_text(str(zip_path.stat().st_mtime))
    return dest


def snapshot_meta(source_root: Path, sid: str) -> dict:
    """The snapshot's identity: when it was taken and what revision it pins."""
    path = source_root / ".meta" / f"{sid}.json"
    if not path.is_file():
        return {}
    try:
        meta = json.loads(path.read_text())
    except ValueError:
        return {}
    return {k: meta[k] for k in ("taken", "tree_sha256", "descriptor_version")
            if meta.get(k)}


def iter_source_files(root: Path, include: list[str], excludes: list[str]):
    """Yield (rel_posix_path, absolute_path) for everything harvestable.

    Root-level files are never harvested -- descriptor.mod, thumbnails,
    licences, changelogs, and Kammarheit's dead songs.asset all sit there, and
    no Stellaris directory the game reads is a bare root file.
    """
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        for path in sorted(entry.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if not included(rel, include):
                continue
            if any(matches(rel, pat) for pat in excludes):
                continue
            yield rel, path


# ── copying ───────────────────────────────────────────────────────────────────


def copy_and_hash(src_path: Path, dst_path: Path) -> tuple[str, int, float]:
    """Copy a file, hashing it in the same pass. Returns (sha256, size, mtime).

    Text files are hashed with CRLF normalised away, but copied byte-for-byte:
    what the game loads stays exactly what the source mod shipped.
    """
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    normalise = src_path.suffix.lower() in TEXT_SUFFIXES
    size = 0

    with src_path.open("rb") as fh, dst_path.open("wb") as out:
        while chunk := fh.read(1 << 20):
            out.write(chunk)
            size += len(chunk)
            digest.update(chunk.replace(b"\r\n", b"\n") if normalise else chunk)

    shutil.copystat(src_path, dst_path)
    return digest.hexdigest(), size, dst_path.stat().st_mtime


def hash_existing(path: Path) -> str:
    digest = hashlib.sha256()
    normalise = path.suffix.lower() in TEXT_SUFFIXES
    with path.open("rb") as fh:
        while chunk := fh.read(1 << 20):
            digest.update(chunk.replace(b"\r\n", b"\n") if normalise else chunk)
    return digest.hexdigest()


# ── resampling ────────────────────────────────────────────────────────────────
#
# `resample_to_vanilla:` exists for one shape of problem: a source mod replaces
# a vanilla TEXTURE at its own dimensions, while the sprite that declares it and
# the layout that draws it stay vanilla's or another mod's. Nothing dangles --
# every name resolves -- and the picture renders at the wrong size.
# See .docs/decisions/40-event-picture-geometry.md.
#
# The target is always read off the vanilla file being shadowed, never written
# down here: this must keep working across a game patch that re-cuts vanilla art.


def dds_dimensions(path: Path) -> tuple[int, int] | None:
    """(width, height) from a DDS header, or None if it isn't a DDS."""
    with path.open("rb") as fh:
        head = fh.read(20)
    if len(head) < 20 or head[:4] != b"DDS ":
        return None
    height, width = struct.unpack("<II", head[12:20])
    return width, height


def strip_frame_width(width: int, height: int, still_width: int) -> int | None:
    """Frame width if this is an animation strip laid out left to right.

    STNH ships a handful of event pictures as one row of N frames -- 9315x264 is
    15 frames of 621, 12420x264 is 20. Vanilla declares those same sprites with
    no `noOfFrames`, so the engine draws the whole strip: at UIOD's scale = 1.5
    that is ~14,000 px across. We freeze frame 0.

    The frame width is the DIVISOR of the strip width nearest the source's own
    modal still width -- derived from the corpus rather than asserted, because
    guessing it from the aspect ratio alone picks 828 for the 20-frame strips
    (3.13:1 is a plausible picture) and silently bleeds frame 1 into the crop.
    """
    if width <= still_width * 1.5:
        return None
    divisors = [d for d in range(1, width + 1) if width % d == 0]
    best = min(divisors, key=lambda d: abs(d - still_width))
    # A strip has at least two frames and its frames are picture-shaped.
    if best == width or not 0.5 <= best / height <= 5.0:
        return None
    return best


def resample_to(src_path: Path, dst_path: Path, target: tuple[int, int],
                still_width: int, canvas: tuple[int, int] | None = None) -> None:
    """Write src_path into dst_path re-cut to `target`.

    TWO MODES, and which one a pattern wants is a fact about the art, not a
    preference -- so `fit:` is declared in vendor.yml rather than inferred here.

    `fit: crop` (the default) crops to fill at centre gravity. Verified against
    the art rather than assumed: STNH's 620x264 event pictures are the same
    scenes vanilla ships at 450x150, re-rendered taller, so a centre crop back
    to 3:1 recovers vanilla's framing almost exactly. Scaling to fit instead
    would letterbox inside UIOD's frame.

    `fit: canvas` restores the file onto the source mod's OWN canvas first --
    bottom-aligned, transparent fill -- and only then scales to the target. It
    exists for art composited by exact pixel position on a fixed canvas, where
    cropping would delete part of the picture and centring would move it.
    STNH's planet-view city layers are that: vanilla ships all 266 of its
    `*_city_l0N.dds` at 800x400 with each layer's content at its own offset,
    STNH's canvas is 560x280 -- exactly 70% -- and 41 of its files are that
    canvas TOP-TRIMMED, every one of them with its content ending flush at the
    bottom edge. Padding the top back and scaling 10:7 is therefore lossless in
    geometry, where a crop-to-fill would have cut 20% off the width of every
    trimmed layer. See .docs/decisions/55-city-set-geometry.md.

    Written uncompressed. That is vanilla's own format for most of these paths,
    it avoids a second lossy pass over the ~1/3 of STNH's that are already DXT,
    and it sidesteps DXT's 4x4 blocks at widths like 450 that they do not divide.
    """
    tw, th = target
    source = str(src_path)
    dims = dds_dimensions(src_path)
    pre: list[str] = []
    if canvas:
        # Bottom-aligned, because that is where the trims left the content.
        #
        # THE HEIGHT IS THE CANVAS'S, NOT THE FILE'S. Growing it to fit a file
        # taller than the canvas keeps every pixel and then hands `-resize !` a
        # box of the wrong aspect, which scales x and y by different factors:
        # vulcan_01's l06 is 560x367 against a 560x280 canvas and was squashed
        # to 76% of its height, drawing Vulcan's buildings flat and low -- the
        # symptom decisions 55 and 60 exist to remove, arriving through the one
        # door neither of them closed. A file taller than the canvas overflows
        # the source's own frame, so cropping the top is what the source mod
        # itself draws. Width still only ever grows, where a crop would cut art
        # out of the middle of the frame rather than off its top edge.
        # See .docs/decisions/63-city-set-canvas-overflow.md.
        cw = max(canvas[0], dims[0])
        ch = round(canvas[1] * cw / canvas[0])
        pre = ["-background", "transparent", "-gravity", "south",
               "-extent", f"{cw}x{ch}"]
        post = ["-resize", f"{tw}x{th}!"]
    else:
        if dims:
            frame = strip_frame_width(dims[0], dims[1], still_width)
            if frame:
                source = f"{source}[{frame}x{dims[1]}+0+0]"
        post = ["-resize", f"{tw}x{th}^", "-gravity", "center",
                "-extent", f"{tw}x{th}"]

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["convert", source, *pre, *post,
         "-define", "dds:compression=none", str(dst_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not dst_path.is_file():
        die(f"resample failed for {src_path}: {result.stderr.strip() or 'no output'}")
    written = dds_dimensions(dst_path)
    if written != target:
        die(f"resample wrote {written} for {src_path}, expected {target}")


def resample_rules(entries: list) -> list[tuple[str, str, str]]:
    """`resample_to_vanilla:` entries as (glob, fit, target) triples.

    A bare string is `fit: crop`, `target: path`, which is what the event
    pictures have always had; a mapping may name `fit: canvas` and/or
    `target: family` instead. See resample_to() and resample_plan().

    `target: family` WIDENS THE SCOPE FROM SHADOWED FILES TO THE WHOLE PATTERN,
    so it is opt-in per rule rather than global. Vanilla is 266/271 uniform on
    city layers, 91/91 on rooms, 580/580 on top-level event pictures and 59/59
    on origin pictures -- and the last two are one directory, which is why RULE
    ORDER IS LOAD-BEARING here: `*` spans '/', so the narrower origins glob has
    to come first or it never gets a file. See vanilla_families().

    Declaring it per rule keeps a widening readable as the piece of work it is
    -- .docs/validation/check-design.md rule 11, applied to the harvest.
    """
    out = []
    for e in entries:
        if isinstance(e, str):
            out.append((e, "crop", "path"))
            continue
        glob_ = e.get("glob")
        fit, target = e.get("fit", "crop"), e.get("target", "path")
        if not glob_:
            die(f"{MANIFEST.name}: a resample_to_vanilla entry has no 'glob'")
        if fit not in ("crop", "canvas"):
            die(f"{MANIFEST.name}: resample_to_vanilla '{glob_}' has "
                f"fit: {fit!r}; expected 'crop' or 'canvas'")
        if target not in ("path", "family"):
            die(f"{MANIFEST.name}: resample_to_vanilla '{glob_}' has "
                f"target: {target!r}; expected 'path' or 'family'")
        out.append((glob_, fit, target))
    return out


def vanilla_families(
        rules: list[tuple[str, str, str]],
) -> dict[str, tuple[Counter, tuple[int, int] | None]]:
    """Vanilla's own dimensions per family, one entry per `target: family` rule.

    Each entry is (histogram, modal), where `modal` is that family's single
    canonical size or None if vanilla does not agree with itself strongly enough
    to have one. See resample_plan() for what the two halves are used for.

    A VANILLA FILE IS ATTRIBUTED TO THE FIRST RULE WHOSE GLOB MATCHES IT, which
    is the same rule resample_plan() applies to the source's files -- and it has
    to be, or the two halves disagree about what a family is. fnmatch's '*' spans
    '/', so `gfx/event_pictures/*.dds` matches the origins/ subdirectory too, and
    measuring that glob over the raw directory gives 580 of 639 at 450x150: the
    59 stragglers are not scattered stragglers at all, they are vanilla's origin
    pictures, 59 of 59 at 220x115. Two families in one directory, each uniform on
    its own, reading as one family that is 90.8% uniform -- a hair over the floor
    and one game patch away from silently falling under it. Ordering the origins
    rule first makes both measure 100%.
    See .docs/decisions/69-event-picture-families.md.

    UNIFORMITY_FLOOR is a threshold on a measurement, not a guess at an answer:
    vanilla's `*_room.dds` is 91 of 91 at 952x340 and its `*_city_l0N.dds` is
    266 of 271 at 800x400, so a family with a canonical size clears this by a
    mile and one without it -- a directory of genuinely varied art -- falls well
    short and gets no target rather than a plausible wrong one.
    """
    UNIFORMITY_FLOOR = 0.90
    hists: dict[str, Counter] = {g: Counter() for g, _f, t in rules
                                 if t == "family"}
    for path in (GAME_DIR).glob("**/*"):
        if not path.is_file():
            continue
        rel = path.relative_to(GAME_DIR).as_posix()
        owner = next((g for g, _f, _t in rules if matches(rel, g)), None)
        if owner is None or owner not in hists:
            continue
        try:
            dims = dds_dimensions(path)
        except OSError:
            continue
        if dims:
            hists[owner][dims] += 1

    out: dict[str, tuple[Counter, tuple[int, int] | None]] = {}
    for glob_, hist in hists.items():
        if not hist:
            out[glob_] = (hist, None)
            continue
        (top, n), = hist.most_common(1)
        out[glob_] = (hist, top if n / sum(hist.values()) >= UNIFORMITY_FLOOR
                      else None)
    return out


def resample_plan(root: Path, entries: list,
                  todo: list[tuple[str, Path]]):
    """Which of this source's files get re-cut, to what, and how.

    TWO WAYS A FILE GETS A TARGET, and the second exists because the first is
    structurally blind to half the corpus:

    1. Vanilla ships a file at the SAME PATH and the two disagree on pixel
       dimensions. That is decision 40's rule and it is the exact one: the
       target tracks a game patch that re-cuts vanilla art.

    2. Vanilla ships NOTHING at that path, but the rule says `target: family`
       and the pattern names a family vanilla is uniform about, so the family's
       modal size is the target. This case used to `continue`, and that left
       STNH's six own Trek city prefixes -- klingon, vulcan_01, cardassian_01,
       borg_01, tholian_01, undine_01, named by six of our empires -- on a
       560x280 canvas in an 800x400 planet view, drawing the buildings small and
       low on Cardassia Prime while the backdrop behind them was right. Decision
       55 predicted this exactly and could not reach it, because reading the
       target off one vanilla FILE has no answer when there is no such file.
       Reading it off the vanilla FAMILY does, and is still derived rather than
       asserted -- which is the property decision 40 refused to give up.
       See .docs/decisions/55-city-set-geometry.md.

    A SIZE VANILLA ITSELF USES IN THAT FAMILY IS LEFT ALONE, and that is not an
    optimisation. Vanilla ships `ai_01_city_l01..l05` at 4x4 -- its own way of
    saying "this layer is empty" -- so 4x4 is vocabulary in this directory, not
    a defect, and Planetary Diversity's pd_tree_of_life_01 uses it for the same
    purpose. Scaling those up would inflate five blanks to 1.28 MB each and,
    worse, assert that a convention vanilla demonstrates is wrong. Derived from
    vanilla's own usage, per .docs/validation/check-design.md rule 4.

    Returns rel -> (target, canvas_or_None). The canvas for a `fit: canvas`
    pattern is the source's own MODAL dimensions across the files that pattern
    matched -- derived from what the mod actually ships, never written down, so
    it tracks a resync the way the target tracks a game patch. It is computed
    PER PATTERN, because two patterns over one directory are two families with
    two canvases: STNH's city layers sit on 560x280 and its rooms on 952x340,
    and one modal over both would have padded every room onto a city canvas.
    """
    rules = resample_rules(entries)
    families = vanilla_families(rules)

    candidates: list[tuple[str, Path, tuple[int, int], str, str]] = []
    for rel, path in todo:
        rule = next(((g, f, t) for g, f, t in rules if matches(rel, g)), None)
        if rule is None:
            continue
        glob_, fit, target = rule
        try:
            have = dds_dimensions(path)
        except OSError:
            continue
        if not have:
            continue
        vanilla = GAME_DIR / rel
        want = None
        if vanilla.is_file():
            try:
                want = dds_dimensions(vanilla)
            except OSError:
                want = None
        if want is None:
            if target != "family":
                continue
            # No vanilla file at this path: fall back to the family's own
            # canonical size, and only if vanilla is uniform enough to have one.
            hist, modal = families[glob_]
            if have in hist:          # a size vanilla itself uses here
                continue
            want = modal
        if want and want != have:
            candidates.append((rel, path, want, fit, glob_))

    # The modal still width and the canvas are both PER PATTERN, for the same
    # reason: a pattern names one family of art and these are facts about that
    # family. Sharing one still width across the directory would hand the strip
    # heuristic below a 620px event-picture width while it looks at a 952px
    # room, and 952 has a divisor at 476 that passes every test the heuristic
    # applies -- so a room would be re-cut to its own left half.
    canvas_of: dict[str, tuple[int, int] | None] = {}
    still_of: dict[str, int] = {}
    for glob_, fit, _target in rules:
        seen = Counter(dds_dimensions(p) for _, p, _, _, g in candidates
                       if g == glob_ and dds_dimensions(p))
        still_of[glob_] = Counter(
            w for (w, _), n in seen.items() for _ in range(n)).most_common(
                1)[0][0] if seen else 0
        canvas_of[glob_] = (seen.most_common(1)[0][0]
                            if seen and fit == "canvas" else None)

    plan = {rel: (want, canvas_of.get(glob_), still_of.get(glob_, 0))
            for rel, _, want, fit, glob_ in candidates}
    return plan


# ── build ─────────────────────────────────────────────────────────────────────


# ── patches ───────────────────────────────────────────────────────────────────


def apply_patches(data: dict, generated: dict[str, dict], *, dry_run: bool) -> int:
    """Apply `patches:` from vendor.yml to files already laid down in the tree.

    THE MECHANISM .docs/architecture/vendored-merge.md RULE 1 PROMISED AND NOBODY BUILT.
    Until 2026-08-02 the only sanctioned way to change vendored content was an
    `src/` override -- a whole copy of someone else's file to change one line,
    which then goes stale in silence when that source updates. For a one-line
    typo in a 500-line particle asset that cure is worse than the disease.

    A patch is a literal find-and-replace against one generated file, and its
    value is entirely in how it FAILS: if `from` no longer appears, the source
    mod has changed underneath us and the build stops and says so. An `src/`
    copy in the same situation says nothing and quietly keeps shipping our
    version of a file the author has since fixed.

    Applied AFTER all sources and after `src/`, so `src/` still wins outright and
    a patch can also touch an `src/` file if it ever needs to. The recorded
    sha256 is the PATCHED file's, so validate.py's hand-edit detector stays
    correct: the patched bytes are what the manifest declares, and a later hand
    edit still trips it.

    Bytes in, bytes out. Several sources ship CRLF and the game loads what they
    shipped, so no decoding, no line-ending normalisation, no reformatting --
    the patch touches exactly the bytes it names and nothing else.
    """
    patches = data.get("patches") or []
    if not patches:
        return 0

    applied = 0
    for i, patch in enumerate(patches):
        where = f"{MANIFEST.name}: patches[{i}]"
        rel = patch.get("path")
        if not rel:
            die(f"{where} has no 'path'")
        if not patch.get("why"):
            die(f"{where} ({rel}) has no 'why'. A patch to someone else's file "
                f"without a recorded reason is indistinguishable from a bug.")

        info = generated.get(rel)
        if info is None:
            die(f"{where}: '{rel}' is not in the generated tree, so there is "
                f"nothing to patch. Check the path, or whether the source that "
                f"ships it is still in the harvest.")

        expect = patch.get("source")
        if expect and info["source"] != expect:
            die(f"{where}: '{rel}' is declared as coming from '{expect}' but it "
                f"was vendored from '{info['source']}'. Harvest order changed; "
                f"re-check the patch before trusting it.")

        replacements = patch.get("replace") or []
        if not replacements:
            die(f"{where} ({rel}) declares no 'replace' entries")

        path = BUILD / rel
        blob = path.read_bytes()
        original = blob

        for j, rep in enumerate(replacements):
            if "from" not in rep or "to" not in rep:
                die(f"{where}.replace[{j}] ({rel}) needs both 'from' and 'to'")
            frm = str(rep["from"]).encode("utf-8")
            to = str(rep["to"]).encode("utf-8")
            found = blob.count(frm)

            if found == 0:
                die(f"{where}.replace[{j}]: pattern not found in '{rel}'.\n"
                    f"      looking for: {rep['from']!r}\n"
                    f"      This is the patch doing its job: '{info['source']}' "
                    f"has changed and this fix may no longer be needed or may no "
                    f"longer be correct. Re-read the file and update or delete "
                    f"the patch -- do not just make it match again.")

            want = rep.get("count")
            if want is not None and found != want:
                die(f"{where}.replace[{j}]: expected {want} occurrence(s) of "
                    f"{rep['from']!r} in '{rel}', found {found}. The file has "
                    f"changed shape; re-check the patch.")

            blob = blob.replace(frm, to)

        if blob == original:
            die(f"{where} ({rel}) changed nothing -- every 'to' already equals "
                f"its 'from'. Delete the patch.")

        if not dry_run:
            stat = path.stat()
            path.write_bytes(blob)
            os.utime(path, (stat.st_atime, stat.st_mtime))
            info["sha256"] = hash_existing(path)
            info["size"] = len(blob)
            info["mtime"] = path.stat().st_mtime
        info["patched"] = True
        info["patch_why"] = " ".join(str(patch["why"]).split())
        applied += 1

    return applied


# ── renames ───────────────────────────────────────────────────────────────────


def apply_renames(data: dict, generated: dict[str, dict], *, dry_run: bool) -> int:
    """Apply `renames:` from vendor.yml -- change a vendored file's NAME.

    THE ONE THING NEITHER A PATCH NOR AN `src/` OVERRIDE COULD DO. Both of those
    change a file's contents; neither changes which of two files defining the
    same key the engine keeps, because that is decided by FILENAME sort order
    within the directory -- first for FIOS directories, last for LIOS ones
    (.docs/decisions/27-merge-semantics-per-directory.md).

    Harvest order does not decide it. Harvest order settles two sources claiming
    the same PATH; once every source is one mod, two sources shipping the same
    key under different filenames both ship, and the engine picks by name. Before
    this existed the only lever was an `src/` copy of the whole losing file, to
    change nothing but which name it has.

    Borrowed wholesale from Irony Mod Manager, which writes `!!!_` to win FIOS
    and `zzz_` to win LIOS and keeps prepending characters until the name really
    does sort where it needs to. `win:` is that loop turned into an assertion:
    name the outcome you want and the build proves the new name achieves it,
    against vanilla's files as well as ours, or stops. A rename whose whole
    purpose is to win a sort and which is never checked to have won it is the
    kind of change that looks right in a diff forever.

    Applied last -- after sources, after `src/`, after patches -- so `patches:`
    entries keep naming the path their source actually ships, which is what the
    file is called everywhere except here.
    """
    renames = data.get("renames") or []
    if not renames:
        return 0

    applied = 0
    for i, ren in enumerate(renames):
        where = f"{MANIFEST.name}: renames[{i}]"
        rel = ren.get("path")
        if not rel:
            die(f"{where} has no 'path'")
        if not ren.get("why"):
            die(f"{where} ({rel}) has no 'why'. Renaming someone else's file "
                f"changes which mod wins a key; without a recorded reason the "
                f"next reader cannot tell it from a mistake.")

        info = generated.get(rel)
        if info is None:
            die(f"{where}: '{rel}' is not in the generated tree, so there is "
                f"nothing to rename. Check the path, or whether the source that "
                f"ships it is still in the harvest.")

        expect = ren.get("source")
        if expect and info["source"] != expect:
            die(f"{where}: '{rel}' is declared as coming from '{expect}' but it "
                f"was vendored from '{info['source']}'. Harvest order changed; "
                f"re-check the rename before trusting it.")

        to = ren.get("to")
        if not to:
            die(f"{where} ({rel}) has no 'to'")
        if "/" in to or to in (".", ".."):
            die(f"{where} ({rel}): 'to' is a filename, not a path -- got {to!r}. "
                f"Moving a file to another directory moves it to another "
                f"database; that is not what a rename is for.")

        old = Path(rel)
        if to == old.name:
            die(f"{where} ({rel}): 'to' is the name the file already has. "
                f"Delete the rename.")

        new_rel = (old.parent / to).as_posix()
        if new_rel in generated:
            die(f"{where}: renaming '{rel}' to '{to}' would land on "
                f"'{new_rel}', which {generated[new_rel]['source']} already "
                f"claims. That is a silent overwrite, not a rename.")

        # Does the new name actually win? Sorted against every other file in the
        # directory -- ours AND vanilla's, because the engine reads them as one
        # sequence and vanilla's `00_` prefix is exactly the thing a FIOS rename
        # usually has to beat.
        want = ren.get("win")
        if want is not None:
            if want not in ("first", "last"):
                die(f"{where} ({rel}): 'win' must be 'first' or 'last', "
                    f"got {want!r}")
            d = old.parent.as_posix()
            others = {Path(k).name for k in generated
                      if Path(k).parent.as_posix() == d and k != rel}
            van = GAME_DIR / d
            if van.is_dir():
                others |= {f.name for f in van.glob(f"*{old.suffix}")}
            else:
                print(f"{YEL}note{OFF}  {where}: no vanilla {d}/ to compare "
                      f"against; 'win' checked among vendored files only")
            ranked = sorted(others | {to})
            got = ranked[0] if want == "first" else ranked[-1]
            if got != to:
                die(f"{where}: '{to}' does not sort {want} in {d}/ -- "
                    f"'{got}' does. The rename would not win the key it exists "
                    f"to win. Irony's answer is to keep prepending the "
                    f"{'lowest' if want == 'first' else 'highest'} character in "
                    f"the competing names until it does; pick a name that beats "
                    f"'{got}'.")

        if not dry_run:
            dst = BUILD / new_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            (BUILD / rel).replace(dst)
        generated[new_rel] = {**info, "renamed_from": old.name,
                              "rename_why": " ".join(str(ren["why"]).split())}
        del generated[rel]
        applied += 1

    return applied


# ── city-set scale normalisation ──────────────────────────────────────────────

def content_box(path: Path) -> tuple[int, int, int, int] | None:
    """(w, h, x, y) of the non-transparent content, or None if unreadable."""
    r = subprocess.run(["identify", "-format", "%@", str(path)],
                       capture_output=True, text=True)
    m = re.match(r"^(\d+)x(\d+)\+(\d+)\+(\d+)$", r.stdout.strip())
    return tuple(int(g) for g in m.groups()) if m else None


def normalize_city_scale(rule: dict, generated: dict[str, dict], *,
                         dry_run: bool) -> list[tuple[str, int, int]]:
    """Bring an out-of-family city set back into the family's content band.

    THIS IS A RESAMPLE, NOT A CROP. Nothing is cut off: the layer is scaled
    down on the vertical axis only and padded back onto its own 800x400 canvas
    bottom-aligned, so every pixel of the source survives and the transparent
    rows added at the top are sky the environment backdrop draws anyway.

    Why it has to be content-aware, and cannot be a `fit:` mode.
    `fit: canvas` pads a file onto the source mod's canvas and scales the
    CANVAS to vanilla's. That preserves the source's content-to-canvas ratio,
    which is exactly the thing that is wrong here. STNH drew vulcan_01 on a
    560x367 frame with its content filling 227 rows -- 62% of the frame, where
    the sets around it fill 72%. Padding to 560x367 leaves the buildings too
    short; cropping to the 560x280 family canvas (which is what
    decision 63 did) leaves them too tall. No choice of canvas reaches the
    family band, because the ratio itself differs. Only rescaling the content
    does, so the target is read off the content box rather than the canvas.

    The family median is measured over the MERGED tree, not vanilla. Vanilla's
    own humanoid_01 horizon is 328 rows tall, but the built tree's humanoid_01
    is STNH's at 291 -- STNH shadows the vanilla path (decision 07) and every
    Trek set sits beside STNH's, not beside Paradox's. The band a player
    actually sees is therefore the one to measure against.

    Returns (prefix, from_height, to_height) per set changed.
    """
    glob_ = rule.get("glob")
    horizon = rule.get("horizon", "_city_l06")
    tol = float(rule.get("tolerance", 0.10))
    if not glob_:
        die("normalize_city_scale needs a 'glob'")

    # Group the merged tree's city layers by texture prefix.
    sets: dict[str, list[str]] = {}
    for rel in generated:
        if not matches(rel, glob_):
            continue
        stem = Path(rel).name
        m = re.match(r"^(.*?)_city_l\d+", stem)
        if m:
            sets.setdefault(m.group(1), []).append(rel)

    # Measure each set's horizon layer. A layer whose content fills the whole
    # canvas is opaque backdrop art rather than a skyline -- a different kind of
    # layer, with no band to be inside -- and an empty one has no content at all.
    heights: dict[str, int] = {}
    for prefix, rels in sets.items():
        want = f"{prefix}{horizon}.dds"
        rel = next((r for r in rels if Path(r).name == want), None)
        if rel is None:
            continue
        box = content_box(BUILD / rel)
        dims = dds_dimensions(BUILD / rel)
        if not box or not dims or box[1] == 0 or box[1] >= dims[1]:
            continue
        heights[prefix] = box[1]

    if not heights:
        return []
    median = statistics.median(sorted(heights.values()))
    ceiling = median * (1 + tol)

    changed: list[tuple[str, int, int]] = []
    for prefix, h in sorted(heights.items()):
        if h <= ceiling:
            continue
        factor = median / h
        for rel in sorted(sets[prefix]):
            path = BUILD / rel
            dims = dds_dimensions(path)
            if not dims:
                continue
            w, ch = dims
            scaled = round(ch * factor)
            if dry_run or scaled >= ch:
                continue
            stat = path.stat()
            r = subprocess.run(
                ["convert", str(path),
                 "-resize", f"{w}x{scaled}!",
                 "-background", "transparent", "-gravity", "south",
                 "-extent", f"{w}x{ch}",
                 "-define", "dds:compression=none", str(path)],
                capture_output=True, text=True)
            if r.returncode != 0:
                die(f"city scale normalise failed for {rel}: "
                    f"{r.stderr.strip() or 'no output'}")
            os.utime(path, (stat.st_atime, stat.st_mtime))
            info = generated[rel]
            info["sha256"] = hash_existing(path)
            info["size"] = path.stat().st_size
            info["mtime"] = path.stat().st_mtime
            info["city_scaled"] = round(factor, 4)
        changed.append((prefix, h, round(h * factor)))
    return changed


# ── prune ─────────────────────────────────────────────────────────────────────


def apply_prune(generated: dict[str, dict], *, dry_run: bool) -> list[str]:
    """Drop files the reachability closure proves nothing in the tree names.

    THE FOURTH CLASS. Until now every file that arrived because it sat inside a
    directory we included stayed, whether or not anything referred to it —
    23,555 files of which `make clutter` could account for 21,807. Decision 35
    looked straight at 115 such entities and kept them ("trading content for
    tidiness"); this reverses that, and the reversal is the whole of
    .docs/decisions/43-clutter-pass.md.

    NOT AN `exclude:` LIST, deliberately. 813 event-picture paths written down
    here would be correct the day they were written and silently wrong after the
    next `make sources-sync` — which is exactly the artefact decision 22 showed
    cannot track reference edges. The closure re-derives itself every build, so
    a source mod that starts declaring a sprite over one of these gets its
    picture back with no edit here. The cost is that vendor.yml alone no longer
    describes the output; the manifest plus the closure do, and .docs/provenance.md
    lists what went.

    Scoped to tools/clutter.py's PRUNE_TIERS, which is a calibration result and
    not a convenience filter: gfx/models orphans at 5.3% against vanilla's own
    4.9% are indistinguishable from Paradox's leftovers and are reported, never
    removed. `clutter_keep:` in vendor.yml overrides per file, with a reason.

    One pass is enough and cannot cascade: every declaration file is a root in
    the closure and every root is reachable by construction, so nothing this
    removes was making anything else reachable.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import clutter

    tree, verdicts = clutter.build_verdicts()
    doomed = clutter.prunable(verdicts)
    if not doomed or dry_run:
        return doomed

    for rel in doomed:
        path = BUILD / rel
        if path.is_file():
            path.unlink()
        generated.pop(rel, None)

    for rel in sorted(doomed, key=len, reverse=True):
        parent = (BUILD / rel).parent
        while parent != BUILD and parent.is_dir():
            try:
                next(parent.iterdir())
                break
            except StopIteration:
                parent.rmdir()
                parent = parent.parent
    return doomed


def clean_tree(state: dict, *, quiet: bool = False) -> int:
    """Delete every path the last build generated, then prune emptied dirs."""
    removed = 0
    for rel in state.get("generated", {}):
        path = BUILD / rel
        if path.is_file():
            path.unlink()
            removed += 1

    for rel in sorted(state.get("generated", {}), key=len, reverse=True):
        parent = (BUILD / rel).parent
        while parent != BUILD and parent.is_dir():
            try:
                next(parent.iterdir())
                break
            except StopIteration:
                parent.rmdir()
                parent = parent.parent
    if not quiet:
        print(f"  removed {removed} generated file(s)")
    return removed


def vendor(args: argparse.Namespace) -> int:
    data = load_manifest()
    source_root = resolve_source_root(data)
    if not source_root.is_dir():
        die(f"{source_root.name}/ does not exist -- the source mods have never "
            f"been snapshotted. Run: make sources-sync")
    global_excludes = list(data.get("global_excludes", []))
    started = time.time()

    if STATE.is_file() and not args.dry_run:
        print(f"{DIM}clearing the previous build{OFF}")
        clean_tree(json.loads(STATE.read_text()))

    generated: dict[str, dict] = {}
    claimed_by: dict[str, str] = {}
    overwrites: list[tuple[str, str, str]] = []
    skipped: list[tuple[str, str, str]] = []
    per_source: list[dict] = []

    for src in data["sources"]:
        sid, name = str(src["id"]), src.get("name", str(src["id"]))
        root = source_dir(src, source_root)
        excludes = global_excludes + list(src.get("exclude", []))
        include = list(src.get("include", []))
        # `additive_only: yes` covers the whole source (STNH). A LIST scopes it
        # to path prefixes, which is what a source needs when it must beat an
        # earlier one somewhere and lose to it elsewhere: the Walshicus shipsets
        # overwrite STNH's ship directories on purpose (decision 17) and must
        # not overwrite its flags, where STNH is the agreed source and the
        # shipsets carry 13 basenames it has not got.
        additive = src.get("additive_only")
        add_all = additive is True
        add_paths = [p.rstrip("/") for p in additive] if isinstance(additive, list) else []

        todo: list[tuple[str, Path]] = []
        for rel, path in iter_source_files(root, include, excludes):
            scoped = add_all or any(
                rel == p or rel.startswith(p + "/") for p in add_paths)
            if scoped and rel in claimed_by:
                skipped.append((rel, name, claimed_by[rel]))
                continue
            todo.append((rel, path))

        resample_pats = list(src.get("resample_to_vanilla", []))
        recut: dict = {}
        if resample_pats and not args.dry_run:
            recut = resample_plan(root, resample_pats, todo)

        # Paths within one source are distinct, so order inside a source is
        # irrelevant and the copies can overlap. Order BETWEEN sources is the
        # whole point of the manifest and stays strictly sequential.
        def do(item: tuple[str, Path]):
            rel, path = item
            if rel in recut:
                target, canvas, still_width = recut[rel]
                resample_to(path, BUILD / rel, target, still_width, canvas)
                out = BUILD / rel
                return rel, hash_existing(out), out.stat().st_size, out.stat().st_mtime
            sha, size, mtime = copy_and_hash(path, BUILD / rel)
            return rel, sha, size, mtime

        if args.dry_run:
            results = [(rel, "", path.stat().st_size, 0.0) for rel, path in todo]
        else:
            with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                results = list(pool.map(do, todo))

        total = 0
        for rel, sha, size, mtime in results:
            if rel in claimed_by and claimed_by[rel] != name:
                overwrites.append((rel, claimed_by[rel], name))
            claimed_by[rel] = name
            generated[rel] = {"source": name, "id": sid, "sha256": sha,
                              "size": size, "mtime": mtime}
            total += size

        # Pin which snapshot revision produced this, so provenance.md answers
        # "which version of the source mod is in the tree?" and not just "which
        # mod?". Written by tools/sources.py; absent only if someone bypassed it.
        snap = snapshot_meta(source_root, sid)
        per_source.append({"id": sid, "name": name, "files": len(results),
                           "bytes": total, **snap})
        note = f"  {YEL}{len(recut)} re-cut to vanilla{OFF}" if recut else ""
        print(f"  {CYA}{sid:>10}{OFF}  {name:<44} {len(results):>6} files  "
              f"{human(total):>8}{note}")

    # src/ is not a source. It is applied unconditionally, after everything.
    src_dir = REPO / "src"
    src_files = 0
    src_bytes = 0
    if src_dir.is_dir():
        for path in sorted(src_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(src_dir).as_posix()
            if any(matches(rel, pat) for pat in global_excludes):
                continue
            if args.dry_run:
                sha, size, mtime = "", path.stat().st_size, 0.0
            else:
                sha, size, mtime = copy_and_hash(path, BUILD / rel)
            if rel in claimed_by:
                overwrites.append((rel, claimed_by[rel], "src/"))
            claimed_by[rel] = "src/"
            generated[rel] = {"source": "src/", "id": "src", "sha256": sha,
                              "size": size, "mtime": mtime}
            src_files += 1
            src_bytes += size
        per_source.append({"id": "src", "name": "src/ (hand-written)",
                           "files": src_files, "bytes": src_bytes})
        print(f"  {CYA}{'src':>10}{OFF}  {'src/ (hand-written)':<44} "
              f"{src_files:>6} files  {human(src_bytes):>8}")

    # Patches last: after every source AND after src/, so src/ still wins
    # outright and a patch always sees the file the game will actually load.
    patched = apply_patches(data, generated, dry_run=args.dry_run)
    if patched:
        print(f"  {CYA}{'patches':>10}{OFF}  {'vendor.yml patches':<44} "
              f"{patched:>6} files  {'':>8}")

    # Renames after patches, so a `patches:` entry names the path its source
    # ships rather than the name we gave it afterwards.
    renamed = apply_renames(data, generated, dry_run=args.dry_run)
    if renamed:
        print(f"  {CYA}{'renames':>10}{OFF}  {'vendor.yml renames':<44} "
              f"{renamed:>6} files  {'':>8}")

    # After renames, and for the same reason prune runs late: the family band a
    # city set is measured against is a property of the MERGED tree, so it can
    # only be computed once every source and every src/ override has landed.
    city_rule = data.get("normalize_city_scale")
    if city_rule:
        rescaled = normalize_city_scale(city_rule, generated,
                                        dry_run=args.dry_run)
        for prefix, was, now in rescaled:
            print(f"  {CYA}{'cityscale':>10}{OFF}  "
                  f"{prefix + ' horizon ' + str(was) + ' -> ' + str(now) + ' rows':<44} "
                  f"{'':>6}         {'':>8}")

    # Last of all, because it is a question about the MERGED tree: whether a
    # file is referenced can only be asked once every source, src/, every patch
    # and every rename has landed.
    pruned = [] if args.no_prune else apply_prune(generated, dry_run=args.dry_run)
    if pruned:
        freed = sum(1 for _ in pruned)
        print(f"  {CYA}{'prune':>10}{OFF}  {'unreferenced (see make clutter)':<44} "
              f"{RED}-{freed:>5}{OFF} files  {'':>8}")

    state = {
        "built": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source_root": str(source_root.relative_to(REPO))
        if source_root.is_relative_to(REPO) else str(source_root),
        "sources": per_source,
        "overwrites": [{"path": p, "from": a, "to": b} for p, a, b in overwrites],
        "skipped": [{"path": p, "source": s, "claimed_by": c} for p, s, c in skipped],
        "pruned": pruned,
        "generated": generated,
    }
    files = len(generated)
    size = sum(e["size"] for e in generated.values())
    if args.dry_run:
        print(f"\n{YEL}dry run{OFF} — {files} file(s), {human(size)}, "
              f"{len(overwrites)} overwrite(s), {len(skipped)} additive skip(s); "
              f"nothing written")
        return 0

    STATE.write_text(json.dumps(state, indent=1, sort_keys=True))
    write_provenance(state)

    print(f"\n{GRN}ok{OFF} — {files} file(s), {human(size)}, "
          f"{len(overwrites)} overwrite(s), {len(skipped)} additive skip(s) "
          f"in {time.time() - started:.0f}s")
    print(f"{DIM}provenance: {PROVENANCE.relative_to(REPO)}{OFF}")
    return 0


# ── provenance ────────────────────────────────────────────────────────────────


def write_provenance(state: dict) -> None:
    PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    out: list[str] = [
        "# Provenance",
        "",
        "Generated by `make vendor` — do not edit.",
        "",
        f"Built {state['built']} from `vendor.yml`, out of "
        f"`{state.get('source_root', DEFAULT_SOURCE_ROOT)}/`. Every file in the "
        "mod tree is listed here with the source it came from.",
        "",
        "## Sources, in harvest order",
        "",
        "`Snapshot` is when `make sources-sync` last pulled that mod from "
        "`/workshop`, and `Revision` is the hash identifying exactly which "
        "upstream revision is pinned — see `sources.lock.yml`.",
        "",
        "| # | ID | Source | Files | Size | Version | Snapshot | Revision |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, s in enumerate(state["sources"], 1):
        rev = s.get("tree_sha256", "")
        out.append(f"| {i} | `{s['id']}` | {s['name']} | {s['files']:,} | "
                   f"{human(s['bytes'])} | {s.get('descriptor_version') or '—'} | "
                   f"{s.get('taken', '—')} | "
                   f"{'`' + rev[:12] + '`' if rev else '—'} |")

    total_files = len(state["generated"])
    total_bytes = sum(e["size"] for e in state["generated"].values())
    out += ["", f"**Total:** {total_files:,} files, {human(total_bytes)}.", ""]

    out += [
        "## Overwrites",
        "",
        "Paths claimed by more than one source. The winner is whichever applied "
        "last, per the harvest order in .docs/architecture/harvest-order.md — these are settled by order, "
        "not by merge.",
        "",
    ]
    if state["overwrites"]:
        out += ["| Path | Lost to | Winner |", "|---|---|---|"]
        for o in sorted(state["overwrites"], key=lambda x: x["path"]):
            out.append(f"| `{o['path']}` | {o['from']} | {o['to']} |")
    else:
        out.append("*None.*")

    out += [
        "",
        "## Additive-only skips",
        "",
        "Paths a source declined because an earlier source already claimed them. "
        "STNH is vendored art-only and additive-only (.docs/architecture/stnh-art.md), so it loses "
        "every contested path to the mod that owns it.",
        "",
    ]
    if state["skipped"]:
        out += ["| Path | Skipped for | Owner |", "|---|---|---|"]
        for s in sorted(state["skipped"], key=lambda x: x["path"]):
            out.append(f"| `{s['path']}` | {s['source']} | {s['claimed_by']} |")
    else:
        out.append("*None.*")

    patched = {r: e for r, e in state["generated"].items() if e.get("patched")}
    out += ["", "## Patched files", "",
            "Vendored files altered by a `patches:` entry in `vendor.yml`. These "
            "are the only generated files that are not byte-identical to their "
            "source mod. A patch whose `from` text stops matching fails the "
            "build rather than reverting silently.", ""]
    if patched:
        out += ["| File | Source | Why |", "|---|---|---|"]
        for rel in sorted(patched):
            e = patched[rel]
            out.append(f"| `{rel}` | {e['source']} | {e.get('patch_why', '')} |")
    else:
        out.append("*None.*")

    renamed = {r: e for r, e in state["generated"].items() if e.get("renamed_from")}
    out += ["", "## Renamed files", "",
            "Vendored files given a different filename by a `renames:` entry in "
            "`vendor.yml`. The contents are the source mod's; only the name "
            "changed, because within one merged mod the filename is what decides "
            "which of two files defining the same key the engine keeps — see "
            "`.docs/decisions/27-merge-semantics-per-directory.md`.", ""]
    if renamed:
        out += ["| File | Was | Source | Why |", "|---|---|---|---|"]
        for rel in sorted(renamed):
            e = renamed[rel]
            out.append(f"| `{rel}` | `{e['renamed_from']}` | {e['source']} | "
                       f"{e.get('rename_why', '')} |")
    else:
        out.append("*None.*")

    pruned = state.get("pruned") or []
    out += ["", "## Pruned files", "",
            "Files a source shipped, this build laid down, and the reachability "
            "closure then proved nothing in the merged tree names — no sprite, "
            "no entity, no `.asset`, no root the engine enters. Removed after "
            "the merge by `tools/clutter.py`, re-derived on every `make vendor` "
            "rather than listed by hand, and scoped to the tiers where vanilla's "
            "own false-positive floor is near zero. `make clutter` reports the "
            "same census without removing anything; `clutter_keep:` in "
            "`vendor.yml` overrides it per file. See "
            "`.docs/decisions/43-clutter-pass.md`.", ""]
    if pruned:
        by_tier: dict[str, int] = {}
        for rel in pruned:
            key = "/".join(rel.split("/")[:2]) if rel.startswith("gfx/") \
                else rel.split("/")[0]
            by_tier[key] = by_tier.get(key, 0) + 1
        out += ["| Tier | Files |", "|---|---|"]
        for key in sorted(by_tier, key=lambda k: -by_tier[k]):
            out.append(f"| `{key}` | {by_tier[key]:,} |")
        out += ["", f"**{len(pruned):,} files.** In full:", "", "```"]
        out += pruned
        out += ["```"]
    else:
        out.append("*None.*")

    # The rows below belong to this heading, so it has to come after the
    # Patched/Renamed sections rather than before them -- it sat above both and
    # rendered as an empty table with its 23,552 rows under "Patched files".
    out += ["", "## Every file", "", "| Path | Source |", "|---|---|"]
    for rel in sorted(state["generated"]):
        mark = " *(patched)*" if state['generated'][rel].get("patched") else ""
        out.append(f"| `{rel}` | {state['generated'][rel]['source']}{mark} |")

    PROVENANCE.write_text("\n".join(out) + "\n", encoding="utf-8")


# ── entry points ──────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--clean", action="store_true",
                    help="remove every generated file and stop")
    ap.add_argument("--provenance", action="store_true",
                    help="rewrite .docs/provenance.md from the last build")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be written without writing it")
    ap.add_argument("--purge-cache", action="store_true",
                    help="also drop the unpacked-archive cache")
    ap.add_argument("--no-prune", action="store_true",
                    help="keep unreferenced files the closure would remove "
                         "(for calibrating tools/clutter.py against them)")
    ap.add_argument("-j", "--jobs", type=int, default=8,
                    help="parallel copies within a single source (default 8)")
    args = ap.parse_args()

    if args.purge_cache and CACHE.exists():
        shutil.rmtree(CACHE)
        print("  dropped .vendor-cache/")

    if args.clean:
        if not STATE.is_file():
            print("nothing to clean — no previous build recorded")
            return 0
        clean_tree(json.loads(STATE.read_text()))
        STATE.unlink()
        print(f"{GRN}ok{OFF} — tree cleaned")
        return 0

    if args.provenance:
        if not STATE.is_file():
            die("no build recorded — run `make vendor` first")
        write_provenance(json.loads(STATE.read_text()))
        print(f"{GRN}ok{OFF} — {PROVENANCE.relative_to(REPO)}")
        return 0

    return vendor(args)


if __name__ == "__main__":
    raise SystemExit(main())
