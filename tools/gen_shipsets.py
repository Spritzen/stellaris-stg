#!/usr/bin/env python3
"""Generate STG's Trek shipsets: one graphical culture per species class, and
the vanilla-shaped ship entities each culture needs.

STNH's ship art is *not* drop-in for a vanilla chassis. Measured across all 104
of STNH's ship directories, every Trek culture declares exactly one of vanilla's
four military hull entities (`<culture>_corvette_entity`) and none of the 40
per-culture section entities: STNH replaced destroyer/cruiser/battleship/titan
with its own ship-size ladder (strike, saber, steamrunner, assault_cruiser,
adv_cruiser, exploration_cruiser, sovereign, super_battleship), each a
single-slot hull with `coreA`/`coreB`/`coreC` section variants. Pointing
`graphical_culture` at an STNH directory therefore buys Trek civilian ships and
vanilla warships. See .docs/decisions/17-stnh-shipsets-on-a-vanilla-chassis.md,
and 18-walshicus-shipsets-replace-stnh-hulls.md for why this now covers five
cultures rather than fourteen.

This script closes the gap by declaring the vanilla names on top of STNH's
entities:

  * hull frames   -- `clone` of the STNH hull chosen for that vanilla size,
                     plus the `part2`/`part3` attach points vanilla's multi-slot
                     sizes require and STNH's single-slot meshes do not carry.
  * bow sections  -- `clone` of that hull's coreA/coreB/coreC, so choosing a bow
                     section in the designer swaps the Trek hull variant.
  * other slots   -- `stg_empty_section_entity`, a no-mesh section, so the
                     mid/stern slots contribute weapons and no geometry rather
                     than bolting mammalian_01 parts onto a Trek hull.
  * stations      -- borrowed from a donor culture, since most STNH directories
                     have none.

Every cloned section also gets `locator` blocks for the gun mount points its
vanilla section templates name and its STNH mesh does not have, each carrying a
POSITION spread through the hull's bounding box. All three inputs are READ --
the wanted mounts out of common/section_templates/, the mounts already baked and
the bounding box out of the .mesh binary -- so this follows the game rather than
a memory of it.

A mount declared without a position sits at the model origin, which is the middle
of the ship; that is what put every Trek gun at the hull centre until
2026-08-03. See .docs/decisions/28-weapon-locator-positions.md.

## Everything lands in ONE file, and that is the whole point

`clone` resolves against entities the engine has ALREADY loaded, and it walks
`gfx/models/ships/` as a single alphabetical sequence with files and directories
interleaved. The first version of this script wrote one file per culture next to
the art it cloned, which cost 537 records in the 2026-08-03 live run:
`stg_vulcan_01_*.asset` sorts before `vulcan_01_sovereign_frame.asset`, so the
Vulcan and Tholian shipsets -- the two culture directories whose names sort after
`stg` -- did not render at all, and every cross-culture borrow from a directory
later in the alphabet failed the same way.

`zz_stg_shipsets.asset` sorts after every directory in that tree (`zahl_01` is
the last one) and after every file, so every clone target is loaded by the time
it is read. **Do not split this file up.**

Run from the repo root. Idempotent.
"""
import re
import sys
from pathlib import Path

STNH_ROOT = Path(".source/688086068")
STNH = STNH_ROOT / "gfx/models/ships"
VANILLA_ROOT = Path("/stellaris")
VANILLA = VANILLA_ROOT / "gfx/models/ships"
SECTIONS = VANILLA_ROOT / "common/section_templates"

OUT = Path("src/gfx/models/ships/zz_stg_shipsets.asset")
OUT_CULTURE = Path("src/common/graphical_culture/stg_graphical_culture.txt")

# Ours, so it takes the stg_ prefix -- unlike everything else this script emits.
EMPTY = "stg_empty_section_entity"
REFERENCE_CULTURE = "mammalian_01"

# Species class -> the STNH art directory its ships come from. The culture key
# MUST equal the directory name: the engine resolves ship art as
# `<graphical_culture>_<entity>`, so the key is STNH's to choose, not ours.
#
# NINE OF THE ORIGINAL FOURTEEN ARE GONE, and this list is the whole of what is
# left. Walshicus' standalone shipsets cover FED, VUL, KDF, ROM, CAR, FER, THO,
# DOM and BRG natively on vanilla's chassis, so nothing needs generating for
# them -- see .docs/decisions/18-walshicus-shipsets-replace-stnh-hulls.md. The
# five below have no such set, so they stay on STNH art through this script.
CULTURES = [
    ("BAJ", "bajoran_01",      "Bajoran Republic"),
    ("TRI", "federation_32",   "Trill -- no Trill art in STNH; a Federation variant set"),
    ("ADR", "andorian_01",     "Andorian Empire"),
    ("BOL", "bolian_01",       "Bolian Union"),
    ("BRE", "breen_01",        "Breen Confederacy"),

    # ── Shared hulls for the minor powers ──────────────────────────────────
    # No species class of their own: 35 of the AI-only minors in
    # src/prescripted_countries/stg_minor_powers.txt point at one of these five
    # STNH directories, which were already harvested as donor art for the five
    # above. Declaring them as cultures is what makes those 35 fly Trek hulls
    # instead of falling back to mammalian_01, and costs no new files.
    (None,  "generic_01",      "Minor powers -- shared hulls (alpha/gamma)"),
    (None,  "generic_02",      "Minor powers -- shared hulls (alpha/gamma)"),
    (None,  "generic_05",      "Minor powers -- shared hulls (beta)"),
    (None,  "generic_06",      "Minor powers -- shared hulls (alpha/delta)"),
    (None,  "generic_07",      "Minor powers -- shared hulls (beta/delta)"),
]

# Vanilla military size -> STNH hulls that could carry it, best first, ordered by
# displacement along STNH's own ladder.
HULL_PREFERENCE = {
    "corvette":   ["corvette", "shuttle", "strike"],
    "destroyer":  ["saber", "strike", "steamrunner", "attack_ship", "corvette"],
    "cruiser":    ["adv_cruiser", "assault_cruiser", "exploration_cruiser",
                   "steamrunner", "saber"],
    "battleship": ["sovereign", "super_battleship", "exploration_cruiser",
                   "adv_cruiser", "assault_cruiser"],
    "titan":      ["super_battleship", "sovereign"],
    "juggernaut": ["super_battleship", "sovereign"],
}
# Applied only when the culture has no hull bigger than its battleship's.
OVERSIZE = {"titan": 1.5, "juggernaut": 2.0}

# Stations and civilian craft are simply absent from most STNH directories --
# eight of the fourteen cultures declare two or fewer of the eight station hulls.
# Falling back would put vanilla starbases over Trek space, so each culture names
# the cultures it borrows from, most thematic first.
THEMATIC = {
    "federation":    ["federation_32"],
    "federation_32": ["federation"],
    "vulcan_01":     ["federation"],
    "bolian_01":     ["federation"],
    "andorian_01":   ["federation"],
    "bajoran_01":    ["federation"],
    "klingon":       ["klingon_houses"],
    "romulan":       ["reman_01"],
    "ferengi_01":    ["orion_01"],
    "dominion_01":   ["karemma_01"],
    "borg_01":       ["borg_02"],
}
DONOR_TAIL = ["generic_05", "generic_01", "generic_02", "suliban_01", "karemma_01",
              "cytherian_01", "voth_01", "fesarian_01", "andromedan_01",
              "generic_07", "generic_06"]
DONORS = {c: THEMATIC.get(c, []) + [d for d in DONOR_TAIL if d != c]
          for _, c, _ in CULTURES}

# Which of the reference culture's names are worth borrowing. Turrets, guns and
# megastructures are deliberately absent: shared art whose fallback to vanilla
# costs nothing visible. `_test` entities are vanilla's own test assets.
BORROW = re.compile(
    r"^(military_station|mining_station|research_station|observation_station"
    r"|orbital_station|outpost_station|terraform_station|colony|colonizer"
    r"|sponsored_colonizer|guided_sapience_colonizer"
    r"|construction|constructor|science|transport|droppod|fighter|bomber)"
    r"[a-z0-9_]*_entity$"
)
BORROW_SKIP = re.compile(r"_test_entity$|^construction_platform")

NAME_RE = re.compile(r'\bname\s*=\s*"([^"]+)"')


# ── reading the trees ────────────────────────────────────────────────────────

def _lines(f):
    return [l.split("#", 1)[0] for l in f.read_text("utf-8", errors="replace").splitlines()]


def declared_entities(root: Path) -> set:
    out = set()
    for f in root.rglob("*"):
        if f.is_file() and f.suffix.lower() in (".asset", ".gfx"):
            for line in _lines(f):
                for m in NAME_RE.finditer(line):
                    if m.group(1).endswith("_entity"):
                        out.add(m.group(1))
    return out


def entity_meshes(root: Path) -> dict:
    """entity name -> pdxmesh name, for every .asset under root."""
    out, cur = {}, None
    for f in root.rglob("*.asset"):
        for line in _lines(f):
            m = NAME_RE.search(line)
            if m and m.group(1).endswith("_entity"):
                cur = m.group(1)
            m2 = re.search(r'\bpdxmesh\s*=\s*"([^"]+)"', line)
            if m2 and cur and cur not in out:
                out[cur] = m2.group(1)
    return out


_VAR_DECL = re.compile(r"^[ \t]*@(\w+)\s*=\s*(-?[\d.]+)\s*$", re.M)
_VAR_REF = re.compile(r"@(\w+)")


def resolve_vars(txt: str) -> str:
    """Substitute a file's own `@name = value` declarations into its text.

    `@` variables in a `.asset` are FILE-LOCAL: each source file declares its own
    `@general_scale` at the top and the engine resolves them while reading that
    one file. Entity bodies get copied out of those files into
    zz_stg_shipsets.asset (Emitter.expand), which leaves the declarations behind
    -- 137 `Malformed token: @general_scale` records in the 2026-08-07 live run,
    one per copied entity, every one of them losing its scale. Resolving as the
    body is read keeps the copy meaning what it meant where it came from.

    Per file, never hoisted: `@general_scale` takes 22 different values across the
    source tree and `@corvette_scale` 26, so there is no one value to lift out.
    See .docs/decisions/31-asset-local-variables.md.
    """
    vals = dict(_VAR_DECL.findall(txt))
    if not vals:
        return txt
    return _VAR_REF.sub(lambda m: vals.get(m.group(1), m.group(0)), txt)


def bodies_in(txt: str, out: dict) -> dict:
    """Add every `entity = { … }` body in `txt` to `out`, first declaration wins."""
    txt = resolve_vars(re.sub(r"#.*", "", txt))
    for m in re.finditer(r"\bentity\s*=\s*\{", txt):
        i, depth = m.end(), 1
        while i < len(txt) and depth:
            depth += (txt[i] == "{") - (txt[i] == "}")
            i += 1
        body = txt[m.end():i - 1]
        n = NAME_RE.search(body)
        if n and n.group(1) not in out:
            out[n.group(1)] = body
    return out


def entity_bodies(root: Path) -> dict:
    """entity name -> the raw text inside its `entity = { … }`.

    Kept verbatim because it gets copied out again: see Emitter.expand, which
    reproduces a donor's declaration rather than cloning it.
    """
    out = {}
    for f in root.rglob("*.asset"):
        bodies_in(f.read_text("utf-8", errors="replace"), out)
    return out


def _depth_tagged(body: str):
    """(brace depth at line start, line) for each line of an entity body."""
    depth = 0
    for line in body.splitlines():
        yield depth, line
        depth += line.count("{") - line.count("}")


_POSITION = re.compile(r'position\s*=\s*\{([^}]*)\}')
_ROTATION = re.compile(r'(rotation\s*=\s*\{[^}]*\})')


def _locator_spans(body: str) -> list:
    """Every top-level `locator = { … }`: (name, placed, rotation, start, end).

    Brace-matched rather than line-matched. STNH writes half its locators over
    four lines and vanilla writes them on one; a regex that assumes either form
    silently sees none of the other, which duplicated 29 mounts before this was
    a scanner.

    `placed` is the second question and the one that survives the first: STNH's
    hull entities declare their guns with a rotation and no position, or at
    { 0 0 0 }. The engine is satisfied and the gun fires from the middle of the
    ship -- existence and placement are separate defects and only the first is
    ever logged. See .docs/decisions/28-weapon-locator-positions.md.
    """
    out, depth, i = [], 0, 0
    while i < len(body):
        c = body[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif depth == 0 and body.startswith("locator", i) and \
                re.match(r'locator\s*=\s*\{', body[i:]):
            j = body.index("{", i) + 1
            d = 1
            while j < len(body) and d:
                d += (body[j] == "{") - (body[j] == "}")
                j += 1
            inner = body[body.index("{", i) + 1:j - 1]
            n = NAME_RE.search(inner)
            if n:
                pos = _POSITION.search(inner)
                rot = _ROTATION.search(inner)
                placed = bool(pos) and any(abs(float(v)) > 1e-6
                                           for v in pos.group(1).split())
                out.append((n.group(1), placed, rot.group(1) if rot else "", i, j))
            i = j
            continue
        i += 1
    return out


def _asset_locators(body: str) -> dict:
    """Locator name -> whether it is placed, from an entity's own .asset body.

    These are as real to the engine as the ones baked into the .mesh -- vanilla
    declares 59 section entities' gun mounts this way and none of them is
    reported missing. A `clone` inherits them along with everything else.
    """
    return {n: placed for n, placed, _, _, _ in _locator_spans(body)}


def mesh_files(root: Path, base: Path) -> dict:
    """pdxmesh name -> the .mesh path it points at, for every .gfx under root."""
    out, cur = {}, None
    for f in root.rglob("*.gfx"):
        for line in _lines(f):
            m = NAME_RE.search(line)
            if m:
                cur = m.group(1)
            m2 = re.search(r'\bfile\s*=\s*"([^"]+\.mesh)"', line)
            if m2 and cur:
                out.setdefault(cur, base / m2.group(1))
    return out


def required_locators() -> dict:
    """Section entity name -> the locators its vanilla templates mount guns on."""
    out, cur = {}, None
    for f in sorted(SECTIONS.glob("*.txt")):
        cur = None
        for line in _lines(f):
            m = re.search(r'^\s*entity\s*=\s*"?([A-Za-z0-9_]+)"?', line)
            if m:
                cur = m.group(1)
            m2 = re.search(r'locatorname\s*=\s*"?([A-Za-z0-9_]+)"?', line)
            if m2 and cur:
                out.setdefault(cur, set()).add(m2.group(1))
    return out


_MESH_CACHE = {}

# `!\x03min f \x03\x00\x00\x00` -- the axis-aligned bounding box a .mesh carries
# as two 3-float properties. This is the only geometry this script reads, and it
# is what keeps gun placement derived from the art rather than hard-coded.
_BBOX_RE = {t: re.compile(b"!\x03" + t + b"f\x03\x00\x00\x00") for t in (b"min", b"max")}


def _blob(path: Path):
    key = str(path)
    if key not in _MESH_CACHE:
        _MESH_CACHE[key] = path.read_bytes()
    return _MESH_CACHE[key]


def mesh_bbox(path: Path):
    """(min, max) over every mesh object in the file, or None.

    A .mesh holds one box per object; the hull's extent is their union.
    """
    if path is None or not path.is_file():
        return None
    import struct
    blob = _blob(path)
    got = {}
    for tag, rx in _BBOX_RE.items():
        pts = [struct.unpack("<3f", blob[m.end():m.end() + 12])
               for m in rx.finditer(blob) if len(blob) >= m.end() + 12]
        if not pts:
            return None
        got[tag] = pts
    lo = tuple(min(p[i] for p in got[b"min"]) for i in range(3))
    hi = tuple(max(p[i] for p in got[b"max"]) for i in range(3))
    if max(hi[i] - lo[i] for i in range(3)) < 1e-4:
        return None
    return lo, hi


def mesh_locators(path: Path, candidates: set) -> set:
    """Which of `candidates` appear as standalone tokens in a .mesh binary."""
    if path is None or not path.is_file():
        return set()
    blob = _blob(path)
    found = set()
    for c in candidates:
        b = c.encode()
        i = blob.find(b)
        while i != -1:
            before = blob[i - 1:i]
            after = blob[i + len(b):i + len(b) + 1]
            ok = (not before or not (before.isalnum() or before == b"_")) and \
                 (not after or not (after.isalnum() or after == b"_"))
            if ok:
                found.add(c)
                break
            i = blob.find(b, i + 1)
    return found


# ── emitting ────────────────────────────────────────────────────────────────

def slot_map() -> dict:
    sizes, cur = {}, None
    for f in sorted((VANILLA_ROOT / "common/ship_sizes").glob("*.txt")):
        for line in _lines(f):
            m = re.match(r"^([A-Za-z][A-Za-z0-9_]*)\s*=\s*\{", line)
            if m:
                cur = m.group(1)
            if cur and "section_slots" in line:
                slots = dict(re.findall(r'"(\w+)"\s*=\s*\{\s*locator\s*=\s*"(\w+)"', line))
                if slots:
                    sizes[cur] = slots
    return sizes


def vanilla_names(reference: set, size: str) -> list:
    pre = f"{REFERENCE_CULTURE}_{size}"
    return sorted(n[len(REFERENCE_CULTURE) + 1:] for n in reference
                  if n.startswith(pre + "_") or n == pre + "_entity")


def classify(section: str, slots: dict) -> str:
    for slot in ("bow", "mid", "stern"):
        if f"_{slot}_" in section or section.endswith(f"_{slot}_entity"):
            return slot
    return "mid"


# Gun locators are placed inside the hull's bounding box, never at its centre.
# The fractions are of the box's half-extent, so they follow the art's own scale.
#
# -Z IS THE NOSE. Vanilla's own art says so: mammalian_01_corvette_M1S1.mesh
# spans z -7.35..+5.75 and bakes its forward medium_gun_01 at z = -1.355. So a
# bow section's band is negative and a stern section's is positive.
_SLOT_Z = {                 # (near, far) as fractions of the half-extent
    "bow":   (-0.75, -0.20),
    "mid":   (-0.25, +0.25),
    "stern": (+0.20, +0.70),
}
_SPREAD_X = 0.55            # lateral offset, alternating port/starboard
_SPREAD_Y = 0.30            # dorsal/ventral, alternating


class Emitter:
    """Writes one entity declaration, with weapon mounts its donor hull lacks.

    A `locator` declared here DOES count -- it satisfies the engine's existence
    check, and a `position` on it places the gun -- but ONLY IN AN ENTITY THAT
    DOES NOT ALSO SAY `clone`. See expand() for that, and for what it cost.

    The declaration must carry a position. An earlier version emitted 989 of
    these bare and they left every gun at the model origin; removing them turned
    that silent defect into a logged one and fixed neither.

    Section ATTACH points (`part1`, `part2`, …) stay at `{ 0 0 0 }`, which is
    what vanilla writes for them.

    See .docs/decisions/28-weapon-locator-positions.md.
    """

    def __init__(self, required, meshes, meshpaths, bodies):
        self.required = required
        self.meshes = meshes
        self.meshpaths = meshpaths
        self.bodies = bodies
        self.unmounted = 0     # mounts we placed
        self.unplaced = 0      # mounts we could not place: no geometry to read
        self.expanded = 0      # donors copied out rather than cloned
        # Every locator name any section template mounts on, so a mesh is
        # scanned once for all of them rather than once per section.
        self._all_wanted = set().union(*required.values()) - {"root"} if required else set()
        self._have = {}

    def _bbox_for(self, *entities):
        """Largest bounding box among `entities`, or None.

        LARGEST, not first: a culture's `<hull>_entity` is a frame rig whose mesh
        is a ~0.02-unit placeholder, and the ship people actually see is its
        coreA/B/C section. Taking the first match put every empty-section gun
        within 0.014 of the origin -- the very defect this is here to fix.
        """
        best = None
        for e in entities:
            mesh = self.meshes.get(e)
            if not mesh:
                continue
            box = mesh_bbox(self.meshpaths.get(mesh))
            if box is None:
                continue
            span = max(box[1][i] - box[0][i] for i in range(3))
            if best is None or span > best[0]:
                best = (span, box)
        return best[1] if best else None

    def has_mounts(self, target) -> set:
        """Every locator `target` carries AT A REAL POSITION.

        Two sources, and both are required. Reading only the mesh binary claimed
        79 section entities were missing mounts their donor's .asset declares
        perfectly well. Reading the .asset without asking where the mount SITS
        goes wrong the other way: a donor locator at { 0 0 0 } silences the
        engine and leaves the gun at the model origin, so it does not count as
        carried and expand() replaces it.
        """
        if target not in self._have:
            mesh = self.meshes.get(target)
            baked = mesh_locators(self.meshpaths.get(mesh), self._all_wanted) if mesh else set()
            declared = _asset_locators(self.bodies.get(target, ""))
            self._have[target] = baked | {k for k, placed in declared.items() if placed}
        return self._have[target]

    def missing_mounts(self, vanilla_name, clone_target):
        """Mount points `vanilla_name`'s templates need that `clone_target` lacks."""
        want = self.required.get(vanilla_name, set()) - {"root"}
        if not want:
            return []
        return sorted(want - self.has_mounts(clone_target))

    def _placements(self, missing, box, slot="mid"):
        """Positions for `missing`, spread through `box`. Deterministic.

        Guns land in the band belonging to their section's slot, so a stern
        section's guns sit aft rather than on the nose.
        """
        (lox, loy, loz), (hix, hiy, hiz) = box
        cx, cy = (lox + hix) / 2, (loy + hiy) / 2
        hx, hy = (hix - lox) / 2, (hiy - loy) / 2
        cz, hz = (loz + hiz) / 2, (hiz - loz) / 2
        near, far = _SLOT_Z.get(slot, _SLOT_Z["mid"])
        out = []
        n = max(len(missing) - 1, 1)
        for i, name in enumerate(missing):
            t = i / n if len(missing) > 1 else 0.0
            z = cz + hz * (near + (far - near) * t)
            x = cx + hx * _SPREAD_X * (1 if i % 2 == 0 else -1)
            y = cy + hy * _SPREAD_Y * (1 if (i // 2) % 2 == 0 else -1)
            out.append((name, (x, y, z)))
        return out

    def expand(self, name, target, extra, scale=None):
        """A verbatim copy of `target`'s declaration under `name`, plus `extra`.

        NOT `clone` + `locator`. `clone` is a whole-entity copy applied after the
        block is read, so ANY locator written beside it is discarded -- the
        entity ends up with exactly the donor's mounts and none of ours. That
        cost 1,383 records in the 2026-08-03 live run (877 `ship_design_
        templates.cpp:405` + 506 `section.cpp:311`), across every section entity
        this file declares, while `make validate` reported the mounts placed.

        Vanilla never writes the two together: 0 of 8,429 entity declarations,
        against 210 that clone and 2,160 that declare locators. Copying the
        donor out is what that leaves, and it is behaviour-preserving --
        `clone` would have produced this same body.

        `extra` is (name, (x, y, z)) pairs. Where the donor declares that mount
        already, its line is DROPPED rather than kept alongside: the only reason
        a mount reaches `extra` is that the donor's copy has no real position,
        so keeping both would leave the engine choosing between our placement
        and the origin. Any rotation the donor gave it is carried over.

        See .docs/decisions/28-weapon-locator-positions.md.
        """
        body = self.bodies[target]
        self.expanded += 1
        replacing = dict(extra)
        # Cut the donor's copy of every mount we are about to place, keeping the
        # rotation it gave it. Right to left, so earlier spans stay valid.
        rotation = {}
        for n, _, rot, start, end in reversed(_locator_spans(body)):
            if n in replacing:
                rotation[n] = f" {rot}" if rot else ""
                body = body[:start] + body[end:]
        keep = [line for depth, line in _depth_tagged(body)
                if not (depth == 0 and scale is not None
                        and re.match(r"\s*scale\s*=", line))]
        # The entity's own name is always the first `name =` in its body; drop
        # that one occurrence and nothing nested.
        kept = NAME_RE.sub("", "\n".join(keep), count=1).strip("\n")
        out = [f'entity = {{\n\tname = "{name}"',
               f'\t# copied from "{target}", not cloned -- see Emitter.expand']
        if scale is not None:
            out.append(f"\tscale = {scale}")
        out += [ln for ln in kept.splitlines() if ln.strip()]
        out += [f'\tlocator = {{ name = "{ln}" position = {{ {x:.3f} {y:.3f} {z:.3f} }}'
                f'{rotation.get(ln, "")} }}'
                for ln, (x, y, z) in extra]
        return "\n".join(out) + "\n}"

    def section(self, name, vanilla_name, target, hull=None, slot="mid"):
        """`target`'s declaration under `name`, with a mount per unmounted gun.

        `hull` is the parent hull's entities, used for geometry when `target` is
        the no-mesh empty section -- those guns hang off the hull, so the hull's
        box is the right thing to spread them through.
        """
        missing = self.missing_mounts(vanilla_name, target)
        if not missing:
            return f'entity = {{ name = "{name}" clone = "{target}" }}'
        box = self._bbox_for(target, *(hull or []))
        if box is None:
            self.unplaced += len(missing)
            return f'entity = {{ name = "{name}" clone = "{target}" }}'
        self.unmounted += len(missing)
        return self.expand(name, target, self._placements(missing, box, slot))


HEADER = f"""\
# Star Trek Galaxies -- the five STNH-art Trek shipsets, on vanilla's ship sizes.
#
# ONLY FIVE CULTURES. The other nine come from Walshicus' standalone shipsets,
# which are built on vanilla's chassis and need nothing generated --
# .docs/decisions/18-walshicus-shipsets-replace-stnh-hulls.md.
#
# GENERATED by tools/gen_shipsets.py -- edit the generator, not this file.
#
# Declares the entity names vanilla's ship sizes and section templates look up as
# `<graphical_culture>_<name>`, on top of the STNH hulls vendored under
# gfx/models/ships/. Without it, a Trek empire flies Trek civilian ships and
# mammalian_01 warships: STNH replaced vanilla's ship sizes with its own
# single-slot ladder, so no Trek culture declares a destroyer, cruiser or
# battleship entity at all.
#
# ONE FILE, NAMED TO SORT LAST, ON PURPOSE. `clone` resolves only against
# entities the engine has already loaded, and it walks gfx/models/ships/ as a
# single alphabetical sequence with files and directories interleaved. Split per
# culture, this cost 537 records on 2026-08-03 and left the Vulcan and Tholian
# shipsets -- the two directories sorting after `stg` -- not rendering at all.
# `zz_` sorts after `zahl_01`, the last directory. Do not split it up.
#
# TWO FORMS OF DECLARATION, AND THE DIFFERENCE MATTERS. An entity that needs
# nothing its donor lacks says `clone`. An entity that needs a weapon mount the
# donor has not got carries a full COPY of the donor instead, because `clone` is
# applied as a whole-entity copy and drops any locator written beside it -- 1,383
# records on 2026-08-07, every one of them a mount declared right there. Never
# add a locator to a `clone` block; convert it to a copy.
# See .docs/decisions/30-clone-discards-sibling-locators.md.
#
# A NEW FILENAME, so the vendored STNH files still win their own paths and a
# source update cannot silently revert us -- .docs/architecture/conflict-register.md, "prefer declaring
# to shadowing". The entity NAMES are vanilla's and are not ours to prefix; only
# the file and the empty section take the stg_ prefix.
#
# See .docs/decisions/17-stnh-shipsets-on-a-vanilla-chassis.md.

# The no-geometry section, for the mid and stern slots STNH's single-slot hulls
# have no art for. Vanilla's own `empty_section_entity` is the model for this;
# it is declared here rather than cloned so the file has no external parent.
entity = {{
\tname = "{EMPTY}"
\tscale = 1
\tlocator = {{ name = "root" }}
}}
"""


CULTURE_HEADER = """\
# Star Trek Galaxies -- the graphical cultures backed by STNH art.
#
# FIVE OF FOURTEEN. The other nine species classes name a culture declared by
# the Walshicus shipset that provides it --
# .docs/decisions/18-walshicus-shipsets-replace-stnh-hulls.md.
#
# GENERATED by tools/gen_shipsets.py -- edit the generator, not this file.
#
# KEYS ARE DELIBERATELY UNPREFIXED, for the same reason the species classes are
# (.docs/decisions/10-species-class-keys-unprefixed.md): the engine resolves
# ship art as `<graphical_culture>_<entity>`, so the key has to be the name of
# the vendored STNH art directory. `STG_FEDERATION` would resolve to nothing.
#
# `ship_lighting` and `ship_selection_weight` are vanilla humanoid_01's, copied
# because STNH's own values live in its common/, which STG does not vendor.
#
# `fallback = mammalian_01`: vanilla's only culture declared in full. What still
# falls through to it is listed in
# .docs/decisions/17-stnh-shipsets-on-a-vanilla-chassis.md.
"""

CULTURE_BLOCK = """
# {empire}
{culture} = {{
	ship_kinds = {{
		default_ship
		space_amoeba
		tiyanki
		voidworm
		cutholoid
		crystalline_entity
	}}

	ship_selection_weight = {{
		base = 0
		modifier = {{
			set = 10
			graphical_culture = from
		}}
	}}

	ship_color = yes
	fallback = mammalian_01
	ship_lighting = {{
		cam_light_1_dir = {{ 0.6 -0.2 0.1 }}
		cam_light_2_dir = {{ -0.4 0.0 0.0 }}
		cam_light_3_dir = {{ 0.4 -1.0 -0.1 }}

		intensity_near = 1.0
		intensity_far = 5.0
		near_value = 100
		far_value = 4000
		rim_start_near = 0.5
		rim_stop_near = 0.99
		rim_start_far = 0.3
		rim_stop_far = 0.99
		ambient_near = 0.1
		ambient_far = 0.0
	}}
}}
"""


def emit_culture(culture, have, reference, slots, em):
    out, chosen, gaps = [], {}, []
    for size in ("corvette", "destroyer", "cruiser", "battleship", "titan", "juggernaut"):
        names = vanilla_names(reference, size)
        if not names:
            continue
        hull = next((h for h in HULL_PREFERENCE[size]
                     if f"{culture}_{h}_entity" in have), None)
        if hull is None:
            gaps.append(size)
            continue
        chosen[size] = hull
        core = [c for c in (f"{culture}_{hull}_core{v}_entity" for v in "ABC") if c in have]
        frame = f"{culture}_{size}_entity"
        sections = [n for n in names
                    if n != f"{size}_entity" and n.endswith("_entity")
                    and not n.endswith("_mesh_entity")]

        hull_entity = f"{culture}_{hull}_entity"
        out.append(f"\n# {size} -- STNH's {hull}")
        if frame not in have:
            extra = sorted(set(slots.get(size, {}).values()) - {"part1"})
            scale = (OVERSIZE[size] if size in OVERSIZE
                     and hull == chosen.get("battleship") else None)
            # The titan's core section IS the hull -- vanilla's titan.txt names
            # `titan_entity` as a section entity -- so the frame carries that
            # section's gun mounts itself.
            gun_missing = em.missing_mounts(f"{size}_entity", hull_entity)
            box = em._bbox_for(hull_entity, *core) if gun_missing else None
            mounts = []
            if box:
                em.unmounted += len(gun_missing)
                mounts = em._placements(gun_missing, box, "mid")
            elif gun_missing:
                em.unplaced += len(gun_missing)
            # Section ATTACH points, which vanilla writes at the origin. These
            # are why a frame is expanded rather than cloned even when it needs
            # no guns: beside a `clone` they are dropped like any other locator,
            # and a frame with no `part2` mounts no stern section at all.
            mounts += [(l, (0.0, 0.0, 0.0)) for l in sorted(set(extra))]
            if mounts or scale is not None:
                out.append(em.expand(frame, hull_entity, mounts, scale=scale))
            else:
                out.append(f'entity = {{ name = "{frame}" clone = "{hull_entity}" }}')

        first_slot = "bow" if "bow" in slots.get(size, {}) else "mid"
        i = 0
        for s in sections:
            name = f"{culture}_{s}"
            if name in have:
                continue
            slot = classify(s, slots.get(size, {}))
            if slot == first_slot and core:
                target = core[i % len(core)]
                i += 1
            else:
                target = EMPTY
            out.append(em.section(name, s, target,
                                  hull=[hull_entity] + core, slot=slot))
    return out, chosen, gaps


def emit_borrowed(culture, have, reference, donors, em):
    wanted = sorted(n[len(REFERENCE_CULTURE) + 1:] for n in reference
                    if n.startswith(REFERENCE_CULTURE + "_")
                    and BORROW.match(n[len(REFERENCE_CULTURE) + 1:])
                    and not BORROW_SKIP.search(n[len(REFERENCE_CULTURE) + 1:]))
    out, borrowed, unmet = [], {}, []
    for name in wanted:
        if f"{culture}_{name}" in have:
            continue
        source = next((f"{d}_{name}" for d in DONORS.get(culture, [])
                       if f"{d}_{name}" in donors.get(d, set())), None)
        if source is None and name.endswith("colonizer_entity") \
                and f"{culture}_colonizer_entity" in have:
            source = f"{culture}_colonizer_entity"
        if source is None:
            unmet.append(name)
            continue
        out.append(em.section(f"{culture}_{name}", name, source))
        label = source[:-len(name) - 1] if source.endswith(name) else "own colonizer"
        borrowed[label] = borrowed.get(label, 0) + 1
    if out:
        out.insert(0, "\n# stations and civilian craft this culture does not ship")
    return out, borrowed, unmet


def main():
    if not STNH.is_dir():
        sys.exit(f"missing {STNH} -- run `make sources-sync ID=688086068` first")

    reference = {n for n in declared_entities(VANILLA) if n.startswith(REFERENCE_CULTURE + "_")}
    slots = slot_map()
    required = required_locators()

    # Mesh resolution has to span both trees: STNH .gfx files routinely point at
    # vanilla .mesh files (vulcan_01's turrets are mammalian_01's).
    meshes = {**entity_meshes(VANILLA), **entity_meshes(STNH)}
    meshpaths = {**mesh_files(VANILLA, VANILLA_ROOT), **mesh_files(STNH, STNH_ROOT)}
    # HEADER first: it declares the empty section, which nothing else does and
    # which most mid and stern sections are built from.
    bodies = bodies_in(HEADER, {**entity_bodies(VANILLA), **entity_bodies(STNH)})
    em = Emitter(required, meshes, meshpaths, bodies)

    donors = {d: declared_entities(STNH / d)
              for ds in DONORS.values() for d in ds if (STNH / d).is_dir()}

    body = [HEADER]
    culture_txt = [CULTURE_HEADER]
    report = []
    for cls, culture, empire in CULTURES:
        src = STNH / culture
        if not src.is_dir():
            sys.exit(f"no vendored art directory for {culture}")
        have = declared_entities(src)
        lines, chosen, gaps = emit_culture(culture, have, reference, slots, em)
        blines, borrowed, unmet = emit_borrowed(culture, have, reference, donors, em)
        body.append(f"\n\n# {'=' * 74}\n# {cls} -- {empire}\n# {'=' * 74}")
        body.append("\n".join(lines + blines))
        culture_txt.append(CULTURE_BLOCK.format(culture=culture, empire=f"{cls} -- {empire}"))
        report.append((cls, culture, chosen, gaps, borrowed, unmet))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body) + "\n", encoding="utf-8")
    OUT_CULTURE.parent.mkdir(parents=True, exist_ok=True)
    OUT_CULTURE.write_text("".join(culture_txt), encoding="utf-8")

    # An `@name` that survives into the output is a value the engine cannot read:
    # it reports `Malformed token` and the entity loses that property. The
    # declarations are file-local and stay behind in the donor's file, so this
    # cannot be caught by reading the output alone later -- fail here, where the
    # donor is still known. See resolve_vars.
    written = OUT.read_text()
    unresolved = sorted(set(_VAR_REF.findall(written)))
    if unresolved:
        sys.exit(f"{OUT}: {len(unresolved)} unresolved @variable(s) copied out of "
                 f"donor files whose declarations did not come with them: "
                 f"{' '.join('@' + v for v in unresolved)}. Each is a "
                 f"`Malformed token` at load and a lost property — see resolve_vars.")

    n = written.count("entity = {")
    print(f"  wrote {OUT} ({n} entities, {em.unmounted} gun mount(s) placed from "
          f"hull geometry, {em.unplaced} unplaceable, {em.expanded} donor(s) "
          f"copied out rather than cloned — decisions 28 and 30)")
    print(f"  wrote {OUT_CULTURE} ({len(CULTURES)} cultures)")
    for cls, culture, chosen, gaps, borrowed, unmet in report:
        picks = " ".join(f"{k[0]}={v}" for k, v in chosen.items())
        lend = " ".join(f"{k}:{v}" for k, v in sorted(borrowed.items()))
        print(f"  {cls} {culture:14s} {picks}")
        print(f"       borrowed {lend or '-'}   falls back to vanilla: "
              f"{' '.join(u[:-7] for u in unmet) or '-'}")
        if gaps:
            print(f"       NO HULL: {' '.join(gaps)}")


if __name__ == "__main__":
    main()
