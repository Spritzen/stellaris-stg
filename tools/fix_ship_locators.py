#!/usr/bin/env python3
"""Give a vendored shipset's weapon mounts real positions, as an src/ override.

THE DEFECT. Most of the Trek ship art declares its guns in the .asset rather
than baking them into the .mesh, and declares them either with a `rotation` and
no `position` or at an explicit `position = { 0 0 0 }`. Either way the gun sits
at the model origin, which is the middle of the ship. A live run of the
Klingon start showed every mount on the starting ships firing from the hull
centre. See .docs/decisions/26-weapon-locator-positions.md.

THE FIX, per entity and per mount:

  * mount IS baked into the mesh -- drop the bare .asset declaration and let the
    baked position stand. Safe whether or not a bare declaration overrides one.
  * mount is NOT baked, and the section has other mounts that ARE placed --
    share the artist's own points out over the missing mounts, round-robin.
  * mount is NOT baked and the section has none placed, but the MESH bakes some
    other hardpoint -- borrow those instead, same round-robin.
  * mount is NOT baked and the mesh bakes no hardpoint at all -- only then, a
    position spread through the mesh's own bounding box, in the band belonging
    to the section's slot.

Nothing is invented: the wanted mounts come out of common/section_templates/,
and the geometry out of the .mesh binary's `min`/`max` properties.

THE SECOND DEFECT, and a different question: a mount is no use on a section
that never attaches. Every Trek hull above corvette borrows
`molluscoid_01_corvette_frame_mesh`, a corvette's frame, which has no `part3`
and no `frame_ship` -- so on a cruiser those sections are hung on a point that
does not exist, and on a destroyer `part2` is a corvette's, ~3 units of z from
`part1` on a hull scaled at 6. The 2026-08-10 Federation run reported the
destroyer's stern mounts as plainly wrong and the log named all eight points.
hull_entities() declares the slots past the first onto `part1`, where the
`empty_mesh` sections' whole-hull gun coordinates already assume they are. See
.docs/planning/ufp-run-remediation.md, item 1.

THE MIDDLE RULE IS THE 2026-08-08 ONE, and it exists because the bounding-box
spread was still a guess wherever the artist had already answered the question.
The Starfleet TNG corvette bakes small_gun_01 and small_gun_02 on the centreline
at the bow -- the forward phaser strip -- and the spread put small_gun_03
starboard and amidships, which is where a live run noticed it: two mounts right,
the third plausible and clearly not the artist's. Doubling a gun onto a point
somebody drew beats inventing a third. See
.docs/decisions/57-mounts-share-existing-points.md.

WHY src/ AND NOT A vendor.yml PATCH. A patch is literal find-and-replace, and
these files declare the same bare line for a dozen different entities that each
need a different position; no `from` string distinguishes them without quoting
the whole block. Owning the file is the honest version of that. The cost is the
one .docs/validation/check-design.md names -- an upstream fix to this art is now masked -- so the
override carries a header saying so, and `make validate` enforces the header.

    python3 tools/fix_ship_locators.py --all [--dry-run]
    python3 tools/fix_ship_locators.py klingon romulan

Every shipset is fixed, not the one someone happens to be flying: the defect is
in the art, and each of STG's playable empires reaches a different set of it.

TO RE-DERIVE THE PLACEMENTS AFTER CHANGING A RULE, delete the generated
overrides first:

    find src/gfx/models/ships -type f \\
      -exec sh -c 'head -1 "$1" | grep -q "^# OVERRIDE of "' _ {} \\; -delete
    make vendor && python3 tools/fix_ship_locators.py --all && make vendor

It reads the BUILT tree, and `make vendor` copies src/ into it -- so a plain
re-run sees its own already-corrected output, finds every mount placed, and
writes nothing at all. That is not idempotence, it is a no-op, and it looks
identical in the output. The five files under src/gfx/models/ships/ that this
tool did NOT write (zz_stg_shipsets.asset, the restored-entity declarations,
stg_stnh_restored_station_meshes.gfx) carry no `# OVERRIDE of` header, which is
what the `head -1` test above is for.
"""
import argparse
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "stg-build"
GAME = Path("/stellaris")
SHIPS = "gfx/models/ships"

# Same bands and spreads as tools/gen_shipsets.py, and for the same reason:
# -Z is the nose in this art, as vanilla's own meshes say.
_SLOT_Z = {"bow": (-0.75, -0.20), "mid": (-0.25, +0.25), "stern": (+0.20, +0.70)}
_SPREAD_X = 0.55
_SPREAD_Y = 0.30

_BBOX_RE = {t: re.compile(b"!\x03" + t + b"f\x03\x00\x00\x00") for t in (b"min", b"max")}

# THREE HARDPOINT STEMS VANILLA DOES NOT HAVE, AND THIS TABLE IS BORROWED
# RATHER THAN DERIVED -- per .docs/validation/check-design.md rule 5, so the next reader knows which of the
# two they are trusting. mount_vocabulary() reads what VANILLA's section
# templates mount on, which answers "what does the game bolt a gun to" and was
# then used to answer "where did the artist draw one". Vanilla's own art uses
# one vocabulary for both, so the gap was invisible; the Trek shipsets name the
# same three things their own way and vanilla never says these words:
#
#   torpedo_NN           a torpedo tube          (vanilla: no stem at all)
#   point_gun_NN         a point-defence mount   (vanilla: pd_gun / pd_turret)
#   extra_large_gun_NN   a spinal mount          (vanilla: xl_gun / extra_large_turret)
#
# 164 meshes bake point_gun_01 and 189 bake torpedo_01, and every one of them
# was invisible as an anchor. See .docs/decisions/64-source-art-hardpoint-names.md.
#
# `support_gun` and `hangarbay` came from the second sweep, which asked the
# question the other way round -- not "does the art use our words" but "what
# does the art bake that we do not recognise". `hangar_NN` IS vanilla's, so
# `hangarbay_NN` is the same emplacement under another name.
_SOURCE_HARDPOINT_STEMS = ("torpedo", "point_gun", "extra_large_gun",
                           "support_gun", "hangarbay", "large_hangarbay")

_INDEXED_RE = re.compile(r"^(.*?)_(\d+)$")

# A SUFFIX THE EXPORTER OR THE ARTIST ADDED, which the name underneath survives:
# `small_gun_01.001` (Blender's duplicate-object numbering), `large_gun_02_r`,
# `medium_gun_01_X`. Stripping one and re-asking is safe BY CONSTRUCTION -- the
# base has to be a hardpoint in its own right, so this can only ever promote a
# name that already means a gun, never invent a new kind of point.
#
# `.NNN` is an artefact rather than part of the name, and the corpus says so:
# 157 of 161 sit in the same mesh as their own base name, at a DIFFERENT
# position -- a second emplacement the artist copied and moved, not a rename.
# `_l` / `_r` is vanilla's own convention (`large_gun_01_l`, `medium_gun_01_r`
# are in its templates); `_X` / `_V` are the Trek art's and are borrowed.
_SUFFIX_RE = re.compile(r"(\.\d{3}|_[A-Za-z0-9]{1,2})$")


def read(p: Path) -> str:
    return p.read_text("utf-8", errors="replace")


def strip_comments(t: str) -> str:
    return re.sub(r"#[^\n]*", "", t)


def mask_comments(t: str) -> str:
    """The same text with comments blanked to spaces -- OFFSETS PRESERVED.

    strip_comments() cannot be used to find an insertion point, because every
    offset past the first `#` is wrong by the length of what it removed. This
    is for scanning: match on the mask, slice from the original.

    It exists because braces inside comments are not braces. STNH's art
    comments out whole `state = { ... }` blocks and leaves the opener behind --
    bajoran_01_standard_ships.asset is +2 on a raw count and balanced on a real
    one -- so a brace-matching parser that does not mask lands its edits in the
    wrong entity.
    """
    out, in_str, i = [], False, 0
    while i < len(t):
        c = t[i]
        if c == '"':
            in_str = not in_str
            out.append(c)
        elif c == "#" and not in_str:
            j = t.find("\n", i)
            j = len(t) if j < 0 else j
            out.append(" " * (j - i))
            i = j
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


# ── geometry ────────────────────────────────────────────────────────────────

_BLOBS: dict[Path, bytes] = {}


def blob(p: Path) -> bytes:
    if p not in _BLOBS:
        _BLOBS[p] = p.read_bytes()
    return _BLOBS[p]


def mesh_bbox(p: Path | None):
    if p is None or not p.is_file():
        return None
    d = blob(p)
    got = {}
    for tag, rx in _BBOX_RE.items():
        pts = [struct.unpack("<3f", d[m.end():m.end() + 12])
               for m in rx.finditer(d) if len(d) >= m.end() + 12]
        if not pts:
            return None
        got[tag] = pts
    lo = tuple(min(q[i] for q in got[b"min"]) for i in range(3))
    hi = tuple(max(q[i] for q in got[b"max"]) for i in range(3))
    if max(hi[i] - lo[i] for i in range(3)) < 1e-4:
        return None
    return lo, hi


def mesh_baked_positions(p: Path | None) -> dict:
    """Locator name -> baked position, for locators the .mesh gives a real one."""
    if p is None or not p.is_file():
        return {}
    d = blob(p)
    i = d.find(b"locator\x00")
    if i < 0:
        return {}
    c = d[i + 8:]
    out = {}
    for m in re.finditer(rb"\[\[([ -~]+?)\x00", c):
        name = m.group(1).decode("ascii", "replace")
        t = c[m.end():]
        q = t.find(b"pf\x03\x00\x00\x00")
        if 0 <= q < 32 and len(t) >= q + 18:
            pos = struct.unpack("<3f", t[q + 6:q + 18])
            if max(abs(v) for v in pos) > 1e-6:
                out[name] = pos
    return out


def mesh_baked(p: Path) -> set:
    """Locator names baked into a .mesh, with a real position."""
    return set(mesh_baked_positions(p))


def entity_index() -> dict:
    """entity name -> (pdxmesh or None, clone parent or None), vanilla then build.

    An entity that names no `pdxmesh` is not geometry-less: most of this art
    reaches its mesh through a `clone`. Not walking the chain reported 1,989
    mounts as unplaceable, 86 of them in every Walshicus set alike.
    """
    out = {}
    for root in (GAME, BUILD):
        base = root / SHIPS
        if not base.is_dir():
            continue
        for f in base.rglob("*.asset"):
            text = read(f)
            for name, i, j in entity_blocks(text):
                body = strip_comments(text[i:j])
                pm = re.search(r'\bpdxmesh\s*=\s*"([^"]+)"', body)
                cl = re.search(r'\bclone\s*=\s*"([^"]+)"', body)
                out[name] = (pm.group(1) if pm else None,
                             cl.group(1) if cl else None)
    return out


def resolve_mesh(name, ents, meshes, seen=None):
    """The .mesh path an entity ends up using, following `clone`."""
    seen = seen or set()
    if name in seen or name not in ents:
        return None
    seen.add(name)
    mesh, parent = ents[name]
    if mesh and meshes.get(mesh):
        return meshes[mesh]
    return resolve_mesh(parent, ents, meshes, seen) if parent else None


_SIZE_RE = re.compile(
    r"^(?P<stem>.+?_(?:corvette|destroyer|cruiser|battleship|titan|juggernaut|"
    r"colossus|starbase|military_station|orbital_station))"
    r"(?:_(?:bow|mid|stern|core)(?:_.*)?)?_entity$")


def section_bbox(name, ents, meshes):
    """Bounding box to place `name`'s guns in, largest of the plausible sources.

    A mid or stern section is routinely `pdxmesh = "empty_mesh"` -- the art is a
    one-piece hull and only the bow section carries geometry. Its guns still hang
    off the ship, so the hull and its bow sections are the right box. LARGEST
    wins because a hull `_entity` is often a tiny frame rig rather than the ship.
    """
    cands = [name]
    m = _SIZE_RE.match(name)
    if m:
        stem = m.group("stem")
        cands.append(f"{stem}_entity")
        cands += [n for n in ents
                  if n.startswith(stem + "_") and n.endswith("_entity")
                  and ("bow" in n or "core" in n)]
    best = None
    for c in cands:
        box = mesh_bbox(resolve_mesh(c, ents, meshes))
        if box is None:
            continue
        span = max(box[1][i] - box[0][i] for i in range(3))
        if best is None or span > best[0]:
            best = (span, box)
    return best[1] if best else None


def mesh_index() -> dict:
    """pdxmesh name -> .mesh path, over vanilla then the build."""
    out = {}
    for root in (GAME, BUILD):
        base = root / SHIPS
        if not base.is_dir():
            continue
        for f in base.rglob("*.gfx"):
            cur = None
            for line in strip_comments(read(f)).splitlines():
                m = re.search(r'\bname\s*=\s*"([^"]+)"', line)
                if m:
                    cur = m.group(1)
                m2 = re.search(r'\bfile\s*=\s*"([^"]+\.mesh)"', line)
                if m2 and cur:
                    for r2 in (GAME, BUILD):
                        cand = r2 / m2.group(1)
                        if cand.is_file():
                            out[cur] = cand
                            break
    return out


# ── what the templates want ─────────────────────────────────────────────────

def required_locators() -> dict:
    out, src = {}, GAME / "common/section_templates"
    for f in sorted(src.glob("*.txt")):
        cur = None
        for line in strip_comments(read(f)).splitlines():
            m = re.search(r'^\s*entity\s*=\s*"?([A-Za-z0-9_]+)"?', line)
            if m:
                cur = m.group(1)
            m2 = re.search(r'locatorname\s*=\s*"?([A-Za-z0-9_]+)"?', line)
            if m2 and cur:
                out.setdefault(cur, set()).add(m2.group(1))
    return out


def section_slots() -> dict:
    """ship_size -> the attach points its sections are hung on.

    The BUILD's copy wins where it has one, because a vendored mod that
    redefines a size redefines its slots with it.
    """
    out = {}
    for root in (GAME, BUILD):
        d = root / "common/ship_sizes"
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.txt")):
            t = strip_comments(read(f))
            for m in re.finditer(r"^([A-Za-z0-9_]+)\s*=\s*\{", t, re.M):
                i, depth = m.end(), 1
                while i < len(t) and depth:
                    depth += (t[i] == "{") - (t[i] == "}")
                    i += 1
                body = t[m.end():i]
                s = re.search(r"section_slots\s*=\s*\{", body)
                if not s:
                    continue
                j, depth = s.end(), 1
                while j < len(body) and depth:
                    depth += (body[j] == "{") - (body[j] == "}")
                    j += 1
                locs = re.findall(r'locator\s*=\s*"([^"]+)"', body[s.end():j])
                if locs:
                    out[m.group(1)] = set(locs)
    return out


def hull_entities(slots: dict, ents: dict) -> dict:
    """`<culture>_<size>_entity` -> the attach points its sections need.

    THE DEFECT, found by the 2026-08-10 Federation run and the eight
    `pdx_entity.cpp:1217` records it left. Every Trek hull above corvette
    carries `pdxmesh = "molluscoid_01_corvette_frame_mesh"` -- a corvette's
    frame, borrowed for hulls a corvette's rig was never built for. A corvette
    needs `part1` and nothing else, so the borrowed frame has no `part3` and no
    `frame_ship`, the sections hung on those never attach, and their guns are
    placed against nothing. That is what "the stern mounts don't match the
    model" looks like from the outside.

    SCOPED TO HULLS FLYING A BORROWED FRAME. An entity whose mesh is its own
    culture's art has a rig built for it and is left alone -- which is why the
    corvette, the one hull three runs have graded as correct, is not touched.

    AND SCOPED TO THE SLOTS PAST THE FIRST. `part1` is never the one that
    fails: every borrowed frame here is a corvette frame, and a corvette's
    whole job is to have a `part1`. Declaring one anyway would move the bow
    section of 293 entities that render correctly today, to fix nothing. The
    log names `part2`, `part3` and `frame_ship`, and those are what this
    writes. See .docs/planning/ufp-run-remediation.md, item 1.
    """
    out = {}
    for name, (mesh, _clone) in ents.items():
        if not mesh or not name.endswith("_entity"):
            continue
        stem = name[:-len("_entity")]
        # LONGEST size wins. `andorian_01_adv_cruiser_entity` is an
        # `adv_cruiser`, not a `cruiser` that happens to end in one, and the
        # two do not have the same slots.
        size = max((s for s in slots if stem.endswith("_" + s)),
                   key=len, default=None)
        if size is None or _STATION_RE.search("_" + size):
            continue
        culture = stem[:-(len(size) + 1)]
        # The frame is this culture's own art -- not ours to second-guess.
        if mesh.startswith(culture + "_"):
            continue
        want = slots[size] - {"part1", "root"}
        if want:
            out[name] = want
    return out


# Starbases, orbital rings and defence platforms are deliberately OUT OF SCOPE.
# Their sections are `empty_mesh` too, but they bolt onto a modular station with
# no hull to spread guns along -- a citadel wants medium_gun_01..013 and there is
# no bounding box that says where. Placing them from geometry would be inventing,
# which is the one thing decision 26 forbids. Reported, never rewritten.
_STATION_RE = re.compile(
    r"_(starbase|military_station|orbital_station|orbital_ring|ion_cannon"
    r"|defence_platform|shipyard)")


def section_entities(required: dict) -> dict:
    """`<culture>_<template entity>` -> the mounts its templates name.

    The engine looks a section entity up under the graphical culture flying it,
    so this is the whole population of entities whose mounts are the game's
    business rather than the artist's. Cultures are read out of the merged tree.
    """
    cultures = set()
    for d in (BUILD / "common/graphical_culture", GAME / "common/graphical_culture"):
        if d.is_dir():
            for f in d.glob("*.txt"):
                cultures |= set(re.findall(r"^\s*([\w]+)\s*=\s*\{",
                                           strip_comments(read(f)), re.M))
    out = {}
    for key, want in required.items():
        want = want - {"root"}
        if not want:
            continue
        if _STATION_RE.search("_" + key):
            continue
        for c in cultures:
            out[f"{c}_{key}"] = want
    return out


def slot_of(entity: str) -> str:
    for s in ("bow", "mid", "stern"):
        if f"_{s}_" in entity or entity.endswith(f"_{s}_entity"):
            return s
    return "mid"


def share_anchors(missing, anchors):
    """Missing mounts -> a position, spread round-robin over the anchors.

    ANCHORS ARE THE ARTIST'S OWN MOUNT POSITIONS for this same section: the ones
    the .mesh bakes, plus any the .asset already declares somewhere real. A gun
    with nowhere of its own is doubled up on one of them rather than given a
    spot on the model that nobody drew.

    Round-robin over the sorted anchors, so with 2 anchors and 2 missing the two
    extras land on different points rather than stacking on one. Exact
    co-location, not a nudge -- a nudged position is a guessed position, which
    is the thing this replaces.
    """
    order = sorted(anchors)
    return {n: anchors[order[k % len(order)]]
            for k, n in enumerate(sorted(missing))}


def placements(names, box, slot):
    (lox, loy, loz), (hix, hiy, hiz) = box
    cx, cy, cz = (lox + hix) / 2, (loy + hiy) / 2, (loz + hiz) / 2
    hx, hy, hz = (hix - lox) / 2, (hiy - loy) / 2, (hiz - loz) / 2
    near, far = _SLOT_Z.get(slot, _SLOT_Z["mid"])
    out, n = {}, max(len(names) - 1, 1)
    for i, nm in enumerate(names):
        t = i / n if len(names) > 1 else 0.0
        out[nm] = (cx + hx * _SPREAD_X * (1 if i % 2 == 0 else -1),
                   cy + hy * _SPREAD_Y * (1 if (i // 2) % 2 == 0 else -1),
                   cz + hz * (near + (far - near) * t))
    return out


# ── rewriting ───────────────────────────────────────────────────────────────

ENTITY_RE = re.compile(r"^entity\s*=\s*\{", re.M)
LOC_RE = re.compile(r'^([ \t]*)locator\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}[ \t]*$', re.M)
LOC_NAME_RE = re.compile(r'\bname\s*=\s*"?([\w.]+)"?')
LOC_POS_RE = re.compile(r'\bposition\s*=\s*\{\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s*\}')

HEADER = """\
# OVERRIDE of {rel}
# [{source}] -- weapon mount positions only; everything else is the source's.
#
# The source declares its gun locators with a `rotation` and no `position`, or at
# `position = {{ 0 0 0 }}`. Both leave the gun at the model origin -- the middle
# of the ship -- which is what the 2026-08-03 Klingon run showed on every
# mount of the starting ships.
#
# Mounts the .mesh already bakes have had their bare declaration REMOVED so the
# baked position stands. A mount the mesh does not carry SHARES one of the
# artist's own mount points, round-robin -- the section's own first, then any
# other hardpoint the same mesh bakes -- and only where the mesh bakes no mount
# at all does it fall back to a position spread through its bounding box.
# GENERATED by tools/fix_ship_locators.py -- rerun it, do not hand-edit.
#
# See .docs/decisions/57-mounts-share-existing-points.md
# and .docs/decisions/26-weapon-locator-positions.md.

"""


def entity_blocks(text):
    """(name, start, end) for each top-level entity block.

    Braces are matched on a comment-masked copy -- see mask_comments() -- so a
    commented-out `state = {` cannot swallow the rest of the file. Offsets are
    the original text's throughout.
    """
    mask = mask_comments(text)
    for m in ENTITY_RE.finditer(mask):
        i, depth, j = m.end(), 1, m.end()
        while j < len(mask) and depth:
            if mask[j] == "{":
                depth += 1
            elif mask[j] == "}":
                depth -= 1
            j += 1
        body = text[i:j - 1]
        nm = re.search(r'\bname\s*=\s*"([^"]+)"', strip_comments(body))
        if nm:
            yield nm.group(1), i, j - 1


def strip_generated_header(text: str) -> str:
    """Drop a header this tool wrote on a previous run.

    `make vendor` copies src/ into the build, so a second run reads its own
    output. Without this the headers stack one per run.

    Cut at the first BLANK LINE rather than at the header's last sentence. The
    sentence version anchored on a decision link, and the moment that link
    changed (2026-08-08, decision 57) it stopped matching the files already on
    disk while still matching nothing -- so the next run would have stacked a
    second header on every one of the 161 overrides. The header is one
    unbroken comment block by construction; the blank line after it is the
    stable landmark.
    """
    if text.startswith("# OVERRIDE of ") and "\n\n" in text:
        return text.split("\n\n", 1)[1]
    return text


def mount_vocabulary(required: dict) -> set:
    """Every locator name vanilla's own section templates use as a mount.

    Derived from vanilla rather than asserted, per .docs/validation/check-design.md rule 4: it is what tells a
    hardpoint (`medium_gun_03`, `xl_gun_01`, `strike_craft_01`) from the other
    things a .mesh bakes locators for -- `target_locator_01` is an aim point and
    no template names it, so it never becomes somewhere a gun is mounted.
    201 names across vanilla's templates.

    THIS IS THE GAME'S VOCABULARY, NOT THE ARTIST'S, and is_hardpoint() is what
    reads it for the artist's question. Keep the two apart: this set is also
    what says which mounts a section REQUIRES, and widening that would invent
    mounts no template asks for. See decision 64.
    """
    return set().union(*required.values()) - {"root"}


def hardpoint_stems(vocab: set) -> tuple[set, dict]:
    """(bare names, stem -> highest index) from vanilla's mount vocabulary."""
    bare, stems = set(), {}
    for n in vocab:
        m = _INDEXED_RE.match(n)
        if m:
            stems[m.group(1)] = max(stems.get(m.group(1), 0), int(m.group(2)))
        else:
            bare.add(n)
    return bare, stems


def is_hardpoint(name: str, bare: set, stems: dict) -> bool:
    """Did somebody draw a weapon here? -- which is not vanilla's question.

    Three ways to say yes, and only the first two are derived from vanilla:

    1. Vanilla's templates mount on this exact name.
    2. Vanilla mounts on this STEM, at some other index. `small_gun_14`,
       `medium_gun_14` and `large_gun_10..12` are the same kind of point as
       `small_gun_13`; vanilla's own art simply never needed a fourteenth.
    3. The stem is one the Trek art uses and vanilla has no word for --
       _SOURCE_HARDPOINT_STEMS, borrowed and labelled as borrowed.

    Then, only if all three said no, strip one exporter/artist suffix and ask
    again -- see _SUFFIX_RE. Recursing once is enough: the suffixes do not
    stack in this corpus, and a second pass would start eating real names.
    """
    if name in bare or name in stems or name in _SOURCE_HARDPOINT_STEMS:
        return True                     # a stem with no index: `hangar`, `gun`
    m = _INDEXED_RE.match(name)
    if m and (m.group(1) in stems or m.group(1) in _SOURCE_HARDPOINT_STEMS):
        return True
    base = _SUFFIX_RE.sub("", name)
    return base != name and is_hardpoint(base, bare, stems)


def fix_file(path: Path, meshes, ents, sections, vocab, stats, hulls=None):
    """`sections` maps a section ENTITY NAME to the mounts its templates need.

    ONLY those entities and ONLY those mounts are touched. Scoping this by "any
    locator whose name looks like a gun" instead rewrote 8,583 locators across
    230 files -- turret art, weapon component entities, anything -- when the real
    population is the section entities a graphical culture can reach. Most of
    that art is correct as its author drew it and is not ours to move.
    """
    text = strip_generated_header(read(path))
    edits = []
    for name, i, j in entity_blocks(text):
        # THE HULL PASS, and it is a different question from the mount pass
        # below: not "where does this gun go" but "does the point this ship's
        # sections hang on exist, in the place the section was drawn for".
        #
        # ONTO `part1`, not the origin. These hulls carry the whole ship in
        # their bow section and an `empty_mesh` for every other one, so the
        # stern's guns are already in whole-hull coordinates and belong at the
        # same point the bow hangs on. The borrowed corvette frame instead
        # spaces its parts a corvette apart -- ~3 units of z between `part1`
        # and `part2` -- which on a hull scaled at 6 puts the stern guns off
        # the model entirely. Coinciding them fixes the case where the point
        # is missing AND the case where it is merely a corvette's.
        #
        # `part1`'s own position is left exactly as the rig has it, so nothing
        # that renders correctly today moves. See hull_entities().
        hull_want = (hulls or {}).get(name)
        if hull_want:
            declared = {ln.group(1)
                        for m in LOC_RE.finditer(text[i:j])
                        if (ln := LOC_NAME_RE.search(m.group(2)))}
            missing = sorted(hull_want - declared)
            if missing:
                anchor = mesh_baked_positions(
                    resolve_mesh(name, ents, meshes)).get("part1_locator",
                                                          (0.0, 0.0, 0.0))
                x, y, z = anchor
                edits.append((j, j, "".join(
                    f'\tlocator = {{ name = "{n}" '
                    f'position = {{ {x:.3f} {y:.3f} {z:.3f} }} }}\n'
                    for n in missing)))
                stats["anchored"] += len(missing)
        want = sections.get(name)
        if not want:
            continue
        body = text[i:j]
        mpath = resolve_mesh(name, ents, meshes)
        baked_pos = mesh_baked_positions(mpath)
        baked = set(baked_pos)
        bad, declared = [], set()
        # The artist's own mount positions for THIS section, which is what the
        # missing mounts are shared out over. Both halves count: the .mesh's
        # baked locators and any the .asset already puts somewhere real.
        anchors = {n: p for n, p in baked_pos.items() if n in want}
        for m in LOC_RE.finditer(body):
            lb = m.group(2)
            ln = LOC_NAME_RE.search(lb)
            if not ln:
                continue
            declared.add(ln.group(1))
            if ln.group(1) not in want:
                continue
            pos = LOC_POS_RE.search(lb)
            placed = pos and max(abs(float(v)) for v in pos.groups()) > 1e-6
            if not placed:
                bad.append((m, ln.group(1)))
            else:
                anchors.setdefault(ln.group(1),
                                   tuple(float(v) for v in pos.groups()))
        # Mounts the templates name that appear NOWHERE -- not in the mesh, not
        # in the .asset. These are the ones the engine logs as
        # `section.cpp:311`, and they need adding, not correcting.
        absent = sorted(want - declared - baked)
        if not bad and not absent:
            continue
        drop = [(m, n) for m, n in bad if n in baked]
        need = [(m, n) for m, n in bad if n not in baked]
        allnew = [n for _, n in need] + absent
        # SHARE THE ARTIST'S POINTS WHERE THERE ARE ANY, in two tiers.
        #
        # First the section's OWN placed mounts -- the artist's answer to this
        # exact question. Failing that, any other hardpoint the same mesh bakes:
        # a small gun on a mesh's torpedo or medium-gun locator is still a place
        # somebody drew a weapon, and those sit a median 30.7% of the hull span
        # out from the origin, which is a hull position and not the centre.
        # The tiers do not mix: doubling up on the section's own mounts beats
        # borrowing another template's.
        #
        # The bounding-box spread is what is left when the mesh bakes no mount
        # at all -- 1,152 of 1,751, so it is still most of them, but it is now
        # the last resort rather than the rule.
        borrowed = {n: p for n, p in baked_pos.items()
                    if n not in want and is_hardpoint(n, *vocab)}
        pool = anchors or borrowed
        if pool and allnew:
            pl = share_anchors(allnew, pool)
            stats["shared" if anchors else "borrowed"] += len(pl)
        else:
            box = section_bbox(name, ents, meshes)
            pl = placements(allnew, box, slot_of(name)) if box and allnew else {}
            stats["spread"] += len(pl)
        for m, n in drop:
            edits.append((i + m.start(), i + m.end(), None))
            stats["dropped"] += 1
        for m, n in need:
            if n not in pl:
                stats["unplaced"] += 1
                continue
            x, y, z = pl[n]
            edits.append((i + m.start(), i + m.end(),
                          f'{m.group(1)}locator = {{ name = "{n}" '
                          f'position = {{ {x:.3f} {y:.3f} {z:.3f} }} }}'))
            stats["placed"] += 1
        add = []
        for n in absent:
            if n not in pl:
                stats["unplaced"] += 1
                continue
            x, y, z = pl[n]
            add.append(f'\tlocator = {{ name = "{n}" '
                       f'position = {{ {x:.3f} {y:.3f} {z:.3f} }} }}')
            stats["added"] += 1
        if add:
            # Insert just before the entity's closing brace.
            edits.append((j, j, "\n".join(add) + "\n"))
    if not edits:
        return None
    out, last = [], 0
    for a, b, rep in sorted(edits):
        out.append(text[last:a])
        if rep is not None:
            out.append(rep)
        else:
            last2 = b
            while last2 < len(text) and text[last2] == "\n":
                last2 += 1
                break
            b = last2
        last = b
    out.append(text[last:])
    return "".join(out)


def patched_paths() -> set:
    """Build-relative paths `vendor.yml` already owns through a `patches:` entry.

    A file cannot be owned twice. An src/ override REPLACES the vendored copy,
    so writing one over a patch target silently discards the patch -- and the
    build refuses it outright, because a patch declares the source it expects
    to be editing and src/ is not that source. Reported, never taken over.
    """
    text = (REPO / "vendor.yml").read_text("utf-8", errors="replace")
    return set(re.findall(r"^\s*-\s*path:\s*(\S+)\s*$", text, re.M))


_HEADER_SOURCE_RE = re.compile(r"^# \[([^]]+)\] -- weapon mount", re.M)


def header_source(dest: Path, fallback: str) -> str:
    """The source mod this override's CONTENT came from, kept across re-runs.

    provenance() answers "who supplied the file in stg-build", and on a second
    run that is us: `make vendor` copies src/ into the build, so the tool reads
    its own output and the attribution decays to `[src/]`. The content's origin
    has not changed, so the existing header's answer is the right one and this
    prefers it. Only a file with no header falls back to the lookup.
    """
    if dest.is_file():
        m = _HEADER_SOURCE_RE.search(read(dest))
        if m and m.group(1) != "src/":
            return m.group(1)
    return fallback


def provenance() -> dict:
    """gfx/models/ships/<dir> -> the source mod that supplied it.

    SCOPED TO THE `Every file` TABLE, which is the one whose columns are
    `| Path | Source |`. Reading the whole document instead took the first row
    mentioning the directory anywhere, and `Patched files` above it is
    `| File | Source | Why |` -- so once decision 33's 66 station patches landed,
    every Walshicus set's header was written with a patch rationale where the
    mod name belongs. It read as correct for as long as no patch touched the
    directory, which is the worst way for a lookup to be wrong.
    """
    out, prov = {}, REPO / ".docs/provenance.md"
    if not prov.is_file():
        return out
    text = read(prov)
    i = text.find("\n## Every file")
    if i < 0:
        return out
    for line in text[i:].splitlines():
        m = re.search(rf"`{SHIPS}/([^/`]+)/", line)
        if m and line.count("|") == 3:
            out.setdefault(m.group(1), line.rsplit("|", 2)[1].strip())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shipset", nargs="*",
                    help="directories under gfx/models/ships; omit with --all")
    ap.add_argument("--all", action="store_true",
                    help="every shipset directory that needs it")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    base = BUILD / SHIPS
    if not base.is_dir():
        sys.exit(f"no {base} — run `make vendor` first")
    if a.all:
        names = sorted(d.name for d in base.iterdir() if d.is_dir())
    elif a.shipset:
        names = a.shipset
    else:
        ap.error("name at least one shipset, or pass --all")

    meshes, required, prov = mesh_index(), required_locators(), provenance()
    sections = section_entities(required)
    vocab = hardpoint_stems(mount_vocabulary(required))
    ents = entity_index()
    hulls = hull_entities(section_slots(), ents)
    patched = patched_paths()
    skipped = []
    grand = {"placed": 0, "added": 0, "dropped": 0, "unplaced": 0,
             "shared": 0, "borrowed": 0, "spread": 0, "anchored": 0}
    files = 0
    for name in names:
        root = base / name
        if not root.is_dir():
            sys.exit(f"no such shipset: {root}")
        stats = {"placed": 0, "added": 0, "dropped": 0, "unplaced": 0,
                 "shared": 0, "borrowed": 0, "spread": 0, "anchored": 0}
        written = []
        for f in sorted(root.rglob("*.asset")):
            rel_in = str(f.relative_to(BUILD))
            if rel_in in patched:
                skipped.append(rel_in)
                continue
            new = fix_file(f, meshes, ents, sections, vocab, stats, hulls)
            if new is None:
                continue
            rel = f.relative_to(BUILD)
            written.append(rel)
            if not a.dry_run:
                dest = REPO / "src" / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(
                    HEADER.format(rel=rel,
                                  source=header_source(dest,
                                                       prov.get(name, name)))
                    + new, encoding="utf-8")
        if not written and not any(stats.values()):
            continue
        files += len(written)
        for k in grand:
            grand[k] += stats[k]
        print(f"  {name:18s} {len(written):3d} file(s)  {stats['placed']:4d} placed  "
              f"{stats['added']:4d} added  {stats['dropped']:3d} dropped  "
              f"{stats['shared']:4d} shared  {stats['borrowed']:4d} borrowed  "
              f"{stats['spread']:4d} spread  "
              f"{stats['anchored']:3d} hull point(s)  "
              f"{stats['unplaced']:3d} unplaceable")
    verb = "would write" if a.dry_run else "wrote"
    print(f"\n  {verb} {files} src/ override(s): {grand['placed']} mount(s) placed, "
          f"{grand['added']} added, {grand['dropped']} bare declaration(s) "
          f"dropped, {grand['anchored']} hull attach point(s) declared, "
          f"{grand['unplaced']} unplaceable")
    total = grand["shared"] + grand["borrowed"] + grand["spread"]
    if total:
        real = grand["shared"] + grand["borrowed"]
        print(f"  of the positions written, {real} sit on a mount point the "
              f"artist drew ({real / total:.0%}): {grand['shared']} on the "
              f"section's own, {grand['borrowed']} borrowed from another "
              f"hardpoint on the same mesh. {grand['spread']} are a "
              f"bounding-box spread, reached only where the mesh bakes no "
              f"mount at all")
    if skipped:
        print(f"\n  {len(skipped)} file(s) left to their vendor.yml patch, "
              f"not overridden:")
        for s in sorted(skipped):
            print(f"    {s}")
    unrecognised(names)


def unrecognised(shipsets) -> None:
    """THE REVERSE QUESTION, printed where whoever re-derives will read it.

    Every number above counts what the rule DID. None of them can fall when the
    rule stops recognising a kind of point, because a mount it cannot anchor is
    quietly spread instead and still counted. That is how `point_gun_01` -- 164
    meshes -- stayed invisible through decision 57's whole calibration, with a
    docstring naming `torpedo_01` as an example of what it caught.

    So: what do these meshes bake that we do NOT classify as a hardpoint? It is
    a census and not a check, deliberately -- there is no way to derive from
    vanilla that `support_gun_01` is a gun, only a person reading the list. The
    job is to put the list in front of that person. See decision 64.
    """
    vocab = hardpoint_stems(mount_vocabulary(required_locators()))
    seen: dict[str, int] = {}
    for name in shipsets:
        for p in sorted((BUILD / SHIPS / name).rglob("*.mesh")):
            for n in mesh_baked_positions(p):
                if not is_hardpoint(n, *vocab):
                    seen[n] = seen.get(n, 0) + 1
    if not seen:
        return
    top = sorted(seen.items(), key=lambda kv: (-kv[1], kv[0]))
    print(f"\n  {len(seen)} baked locator name(s) NOT treated as a hardpoint "
          f"({sum(seen.values())} occurrences). Read this list: anything here "
          f"that is a place a gun goes belongs in is_hardpoint().")
    print("   ", ", ".join(f"{n}×{k}" for n, k in top[:18]),
          f"…" if len(top) > 18 else "")


if __name__ == "__main__":
    main()
