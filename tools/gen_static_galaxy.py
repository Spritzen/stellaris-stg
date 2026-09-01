#!/usr/bin/env python3
"""Generate STG's static galaxy scenarios — the three sizes of The Known
Galaxy, the thing that actually puts Trek empires in the galaxy.

WHY THIS EXISTS. Six galaxies contained no Trek AI empire, and three fixes to
the prescripted pool moved the number by nothing, because the pool is not the
mechanism: `prescripted_countries/` is what the PLAYER picks from, and an AI
Trek empire is created by its home system's initializer, which a
`static_galaxy_scenario` puts on the map at a fixed position.
.docs/decisions/84-static-galaxy-is-the-mechanism.md,
.docs/decisions/85-create-country-initializers.md,
.docs/decisions/86-static-galaxy-scenario.md.

WHAT A SYSTEM ENTRY DOES, in three parts that all have to agree:

    system = { id = "2" name = "" position = { x = -66 y = 147 }
               initializer = stg_klingon_empire_home
               spawn_weight = { base = 0 modifier = { add = 100000
                                has_country_flag = stg_klingon_empire } } }

  * `initializer` names the home system, whose capital's `init_effect` creates
    the AI copy of the empire (tools/gen_home_systems.py, `ai_empire_block`);
  * `base = 0` means no empire is placed here by the generator except one the
    modifier matches, which is what pins Qo'noS to the Klingons;
  * the country flag is the empire's own design key, carried by the player's
    copy through src/common/prescripted_flags/stg_empire_flags.txt.

`spawn_design` is the documented alternative and STG does not use it: it names a
prescripted design, so it goes back through the design-database draw that six
galaxies have already shown does not fill a galaxy, and STNH — 22 static maps,
99 to 152 weighted systems each — uses it exactly zero times.

WHERE THE COORDINATES COME FROM. Every position here is harvested, not invented:
STNH's `01 STH_galaxy_default_galaxy_map.txt` places 1,436 systems across all
four quadrants, and CANON below says which of them is each STG empire's home.
(`stnh_all_positions()` returns 1,437: the file carries a sixth `system = {` on
a COMMENTED-OUT line, STNH's disabled second Sol, and the harvest regex does not
strip comments. It costs nothing -- the position is byte-identical to the live
Sol two lines up, so the thinning pass discards it as zero distance from a star
already kept, and no map has ever contained it. Fix the regex only alongside a
regeneration, because the three files are committed output.)
The filler systems are the same map's other positions, thinned to a minimum
separation so the density is even and the quadrant shape survives; the whole
cloud is then scaled by SCALE. Nothing is random and nothing is authored, so a
re-run reproduces the file byte for byte (`make gen-check`).

THREE SIZES OUT OF ONE CLOUD. The same STNH positions and the same 21
canon homes produce a small, a medium and a large galaxy; SIZES below is the
whole difference between them — 95 / 600 / 1,000 systems over a radius of
218 / 399 / 448. MEDIUM AND LARGE ARE VANILLA'S OWN NUMBERS: its `medium` is
600 stars at radius 400 and its `huge` is 1,000 at 450, so STG's two new sizes
match a vanilla galaxy on star count and radius at once, and therefore on
density too. Small is the outlier and stays one — it is the map three live runs
have graded and its file is unchanged.

`separation` is a threshold, so the star count it yields moves in steps and a
round number is not reachable by it alone; `trim` cuts the overshoot, four
stars for medium and eleven for large.

Filler systems carry `name = ""` on purpose. The engine draws their names from
the pool, which is 1,444 Trek star names already
(.docs/decisions/84-static-galaxy-is-the-mechanism.md), and hard-coding STNH's
own names here
would both duplicate that pool and put raw English in a file that should hold
loc keys.

TWO EMPIRES ARE DELIBERATELY ABSENT and both are recorded in decision 86:

  * the Terran Empire, whose home system is Sol and whose planet is Earth —
    the mirror of the Federation's. STNH places it only in its five MIRROR
    maps, never in a prime-universe one, and two systems called Sol on one map
    is not a thing to ship by accident.
  * an AI Federation. Sol here is vanilla's `sol_system_initializer` (Real
    Space's rescaled copy), which STG does not own, so there is nowhere to put
    a `create_country` for it without either owning that file or patching it.
    The player's Federation still starts at Sol; nobody else plays it yet.

Run:  python3 tools/gen_static_galaxy.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STNH_MAP = (REPO / ".source/688086068/map/setup_scenarios"
            / "01 STH_galaxy_default_galaxy_map.txt")
PRESCRIPTED = REPO / "src/prescripted_countries"
OUT_DIR = REPO / "src/map/setup_scenarios"
LOC_OUT = (REPO / "src/localisation/english"
           / "stg_galaxy_maps_l_english.yml")

# Which STNH system is each STG empire's canon home. This is the one content
# judgement in the file -- the coordinates themselves are read off STNH's map
# at generation time, so a Trek galaxy's relative geography is theirs and not
# ours. Ten of these names belong to initializers gen_home_systems.py could not
# convert (STNH builds them procedurally, so STG authored its own geometry);
# their POSITION is still canon and still worth taking.
CANON = {
    "stg_united_federation_of_planets": "human_homeworld",       # Sol
    "stg_confederacy_of_vulcan":        "vulcan_homeworld",      # 40 Eridani
    "stg_klingon_empire":               "klingon_homeworld",     # Qo'noS
    "stg_romulan_star_empire":          "romulan_homeworld",     # Romulus
    "stg_cardassian_union":             "cardassian_homeworld",  # Cardassia
    "stg_andorian_empire":              "andorian_homeworld",    # Procyon
    "stg_bajoran_republic":             "bajoran_homeworld",     # Bajor
    "stg_bolian_union":                 "bolian_homeworld",      # Bolarus
    "stg_breen_confederacy":            "breen_homeworld",
    "stg_ferengi_alliance":             "ferengi_homeworld",
    "stg_tholian_assembly":             "tholian_homeworld",
    "stg_trill_symbiosis":              "trill_homeworld",
    "stg_dominion":                     "founders_homeworld",
    "stg_borg_collective":              "borg_initializer",      # Unimatrix One
    "stg_caitian_empire":               "caitian_homeworld",     # Cait
    "stg_suliban_empire":               "suliban_homeworld",
    "stg_xindi_empire":                 "xindi_homeworld",
    "stg_yridian_empire":               "yridian_homeworld",
    "stg_krenim_empire":                "krenim_homeworld",
    "stg_malon_empire":                 "malon_homeworld",
    "stg_vidiian_empire":               "vidiian_homeworld",
}

# THE THREE SIZES. Star count and radius are the two facts a player reads off
# the picker, so they are what SIZES states outright; `separation` is the
# density knob underneath them.
#
#   `systems`     the EXACT number of stars the map ships with. The picker
#                 advertises it and `check_static_galaxy` counts it, so it is a
#                 target rather than a result -- see `trim` below for the four
#                 and eleven stars that stand between the thinning pass and a
#                 round number.
#   `separation`  minimum gap between filler systems in STNH'S OWN coordinates.
#                 The thinning pass keeps a star only if it is that far from
#                 every star already kept, so LOWERING it admits more of STNH's
#                 1,437 positions. This is the knob that sets DENSITY; it is
#                 chosen to overshoot `systems` by as little as it can.
#   `scale`       multiplies every position on the way out, so it sets the
#                 galaxy's RADIUS: STNH's cloud reaches 605 units, and the
#                 radius of the map is that times `scale`.
#
# WHERE THE NUMBERS COME FROM. Medium and large are vanilla's own scenarios,
# matched on both facts at once:
#
#   | | stars | radius | density |
#   |---|---|---|---|
#   | vanilla `medium` | 600 | 400 | 11.9 |
#   | **STG medium**   | 600 | 399 | 12.0 |
#   | vanilla `huge`   | 1000 | 450 | 15.9 |
#   | **STG large**    | 1000 | 448 | 15.9 |
#
# (density in stars per 10,000 square units.) That is why `scale` is 0.66 and
# 0.74 and not round numbers: 605 x 0.66 = 399 and 605 x 0.74 = 448, which are
# vanilla's 400 and 450. Vanilla's files also carry the ceiling -- `radius = 450`
# under the comment "should be less than 500, preferably less than ~460" -- so
# large is at the top of the ladder and there is no room above it. A bigger STG
# galaxy would have to widen the cloud, not the scale.
#
# SMALL IS NOT ON THAT LADDER AND DELIBERATELY SO. 70 / 0.36 / 95 systems is the
# map three live runs have graded
# (.docs/decisions/106-sealed-system-is-vanilla-content.md), and it was itself
# measured: 95 systems is 4.5 stars per empire, against the 4.7 of STNH's
# smallest canon map (`09 botf`, 468 stars for 99 weighted systems). Nothing
# about it moves here, and its file is byte-identical below the header comment.
# It is therefore a THIRD as dense as vanilla, where medium and large are
# vanilla's own density -- so the three differ in texture as well as in size,
# and small is the one that is unlike the game around it.
#
# What survives that: the lane rule. Mean degree comes out 3.41 / 3.53 / 3.63
# and the longest lane 49 / 41 / 40 units, all three under vanilla's
# `max_hyperlane_distance = 50`, because LANE_NEIGHBOURS is a count and the cap
# only ever binds on the sparse map.
#
# `default` marks the one scenario the setup screen opens on, and exactly one
# row may carry it (.docs/decisions/88-lock-the-galaxy-picker.md). It stays on
# small: that is the map with three live runs behind it, and a new size is not
# graded by being generated.
#
# `priority` orders the picker list, ascending, the way vanilla's own five run
# tiny=0 through huge=4.
SIZES = [
    {"name": "STG_galaxy_alpha_beta",
     "file": "stg_alpha_beta_quadrant.txt",
     "label": "Small",  "systems": 95,   "separation": 70.0, "scale": 0.36,
     "priority": 0, "default": True},
    {"name": "STG_galaxy_alpha_beta_medium",
     "file": "stg_alpha_beta_quadrant_medium.txt",
     "label": "Medium", "systems": 600,  "separation": 19.0, "scale": 0.66,
     "priority": 1, "default": False},
    {"name": "STG_galaxy_alpha_beta_large",
     "file": "stg_alpha_beta_quadrant_large.txt",
     "label": "Large",  "systems": 1000, "separation": 11.0, "scale": 0.74,
     "priority": 2, "default": False},
]

# Modelled on STNH's `04 STH_galaxy_tiny_alpha_beta`, the closest thing in
# .source/ to what this is: a small, canon, static Alpha/Beta map.
#
# `num_empires = { min = 0 max = 0 }` is theirs and it is the point -- every
# empire in the galaxy comes from an initializer, so no randomly generated
# non-Trek empire can appear. Nine of STNH's 22 maps set it.
#
# `random_hyperlanes = no` is theirs. THE LANES ARE NOT, AND COPYING THEIR
# ABSENCE SHIPPED A GALAXY WITH NO LANES AT ALL -- one live run, one save, one
# hyperlane in 98 systems, and that one an accident of a Planetary Diversity
# `spawn_system`. .docs/decisions/87-static-map-lanes-are-generated.md.
#
# 21 of STNH's 22 maps do define no lanes, the exception being the 468-system
# BotF map with 892 of them. What those 21 pair it with is a SCRIPT: their
# `events/STH_start.txt` runs `every_system = { connect_neighbour_stars = yes }`
# at game start, and that effect
# (`common/scripted_effects/STH_system_effects.txt`) walks
# `every_neighbor_system_euclidean` adding a lane to each. STG vendors neither
# the effect nor the start event, so nothing built the network. `random_hyperlanes
# = no` with no lanes and no builder is exactly what it says: no lanes.
#
# STG takes the other road -- BotF's, the only one of the 22 that puts its lanes
# in the file. They are generated below from the same positions, so the graph is
# deterministic, reviewable in the diff, and checked by `make validate` rather
# than trusted to an engine default.
#
# `num_hyperlanes` is the density the setup screen offers for RANDOM generation,
# so with `random_hyperlanes = no` it is inert. 04's live 0.5-1.0 is left exactly
# as it was: the lanes are the one variable this change moves, and the next run
# has to grade them alone. BotF locks it to `{ min = 5 max = 5 }`, which is where
# to look next if that run shows lanes nobody asked for.

# How the lane graph is built. Each system links to its LANE_NEIGHBOURS nearest
# stars, but only within LANE_MAX -- vanilla's own `max_hyperlane_distance`,
# which all five of its scenarios set to 50, against a median nearest neighbour
# of 26 here. That alone can leave islands, so a minimum spanning tree over the
# same points is unioned in: an MST is connected by construction whatever the
# distances, which is what turns "no unreachable component" from a hope into a
# property. `make validate` re-proves it on the written file regardless.
LANE_MAX = 50.0
LANE_NEIGHBOURS = 3
#
# `default = yes` IS set, as of the picker lock
# (.docs/decisions/88-lock-the-galaxy-picker.md). It was deliberately left off
# while YAGEM's `medium.txt` still carried it -- two defaults is worse than
# none -- and YAGEM's twelve maps are now excluded and vanilla's five masked by
# 0-byte files, so the picker holds nothing but STG's own scenarios and the
# default has to be one of them. Now that there are three, `default` is a
# column of SIZES and exactly one row carries it. STNH's
# `01 STH_galaxy_default_galaxy_map.txt` is the precedent for the key on a
# `static_galaxy_scenario` rather than a random `setup_scenario`.
HEADER = """\
# GENERATED by tools/gen_static_galaxy.py — do not hand-edit; regenerate.
#
# STG's static galaxy scenario, {label} of three. Every Trek empire in the
# galaxy is placed here and created by the initializer this file names for it;
# the prescripted pool is the player's roster and has nothing to do with it.
# See .docs/decisions/86-static-galaxy-scenario.md.
#
# The three sizes are one cloud of positions under two knobs, `separation` and
# `scale` in SIZES; this is the {label_lower} row. Nothing else differs between
# them -- same 21 empires, same canon geography, same lane rule.
# See .docs/decisions/111-three-galaxy-sizes.md.
#
# Positions are STNH's, harvested from their default galaxy map, thinned to a
# minimum separation of {separation} in their coordinates, cut to this size's
# star count and scaled by {scale}. Filler systems carry no initializer and no
# name: the engine builds and names them from STG's own Trek star pool.
#
# {homes} empires placed, {filler} filler systems, {total} systems in all,
# joined by {lanes} hyperlanes across a radius of {radius}. The lanes are
# generated from the positions above, not left to the engine:
# `random_hyperlanes = no` builds nothing.

static_galaxy_scenario = {{
\tname = "{name}"
\tpriority = {priority}
{default_line}
\tcolonizable_planet_odds = 1.0
\tprimitive_odds = 1.0

\t# Nobody but the initializers puts an empire in this galaxy.
\tnum_empires = {{ min = 0 max = 0 }}
\tnum_empire_default = 0
\tadvanced_empire_default = 0
\tfallen_empire_default = 0
\tfallen_empire_max = 0
\tcore_radius = 0

\t# The lanes are declared at the bottom of this file. `num_hyperlanes` is
\t# the random-generation density and is inert while this is `no`.
\trandom_hyperlanes = no
\tnum_hyperlanes = {{ min = 0.5 max = 1.0 }}
\tnum_hyperlanes_default = 1.0

\tsupports_shape = elliptical
\tsupports_shape = spiral_2
\tsupports_shape = spiral_3
\tsupports_shape = spiral_4
\tsupports_shape = spiral_6
\tsupports_shape = ring
\tsupports_shape = cartwheel
\tsupports_shape = starburst
\tsupports_shape = bar
\tsupports_shape = spoked

"""


# The picker's own text, generated with the maps so the counts in it cannot
# drift from the counts in them. The engine renders a scenario's `name` as a
# localisation key and lays the whole string out in the setup screen's map
# list, so the line breaks and the £icon£ tokens are deliberate --
# STNH's own map entries read the same way.
LOC_HEADER = """\
l_english:

# GENERATED by tools/gen_static_galaxy.py — do not hand-edit; regenerate.
#
# Star Trek Galaxies — the galaxy-shape picker. One entry per scenario in
# src/map/setup_scenarios/, keyed by the scenario's own `name`.
# See .docs/decisions/86-static-galaxy-scenario.md,
# .docs/decisions/111-three-galaxy-sizes.md.

"""

# True of all three, because all three are the same galaxy.
LOC_BODY = ("The Alpha and Beta Quadrants at their canon positions, with the "
            "Delta and Gamma powers beyond them. Every empire starts on its "
            "own home system: Sol, Qo'noS, Romulus, Cardassia, 40 Eridani, "
            "Bajor. No randomly generated empires.")

# And the one line that is not. Keyed by SIZES' `label`.
LOC_NOTE = {
    "Small":  "The smallest and the sparsest: few stars between one empire and "
              "the next, so first contact comes early and there is little "
              "unclaimed room that somebody else does not already want.",
    "Medium": "A full galaxy at the game's own medium scale \u2014 six times "
              "the stars of the small map, and space to survey and settle for "
              "a long while before the borders meet.",
    "Large":  "The largest that fits: a thousand systems at the density of a "
              "vanilla huge galaxy, with real unexplored distance between the "
              "Alpha powers and the Delta and Gamma ones.",
}

def stnh_positions() -> dict[str, tuple[float, float]]:
    """Every `initializer = X` on STNH's default galaxy map, with its position.

    Positions are written two ways in these files -- `x = 12` and
    `x = { min = 12 max = 12 }` -- and both have to be read or half the map
    silently disappears.
    """
    text = STNH_MAP.read_text(encoding="utf-8", errors="replace")
    out: dict[str, tuple[float, float]] = {}
    for row in re.findall(r"system = \{[^\n]*\}", text):
        init = re.search(r"initializer\s*=\s*(\S+)", row)
        if not init:
            continue
        pos = _position(row)
        if pos:
            out.setdefault(init.group(1), pos)
    return out


def stnh_all_positions() -> list[tuple[float, float]]:
    """Every system position on the same map, in file order."""
    text = STNH_MAP.read_text(encoding="utf-8", errors="replace")
    out = []
    for row in re.findall(r"system = \{[^\n]*\}", text):
        pos = _position(row)
        if pos:
            out.append(pos)
    return out


def _position(row: str) -> tuple[float, float] | None:
    x = re.search(r"x = (?:\{\s*min = )?(-?[\d.]+)", row)
    y = re.search(r"y =\s*(?:\{\s*min = )?(-?[\d.]+)", row)
    return (float(x.group(1)), float(y.group(1))) if x and y else None


def lane_graph(coords: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """The hyperlane graph over the placed systems, as `(from, to)` id pairs.

    Two passes unioned, because neither is sufficient alone:

      * **k-nearest, capped.** Every system links to its LANE_NEIGHBOURS
        closest stars, skipping any hop longer than LANE_MAX. This is what
        gives the map its shape -- short local links, no lane crossing the
        galaxy -- but a cap can strand an outlying cluster behind a gap.
      * **a minimum spanning tree** over the same points, with no cap. An MST
        touches every node and is connected by construction, so unioning it in
        makes an unreachable component impossible however sparse the cloud is.
        It contributes only the few edges the first pass missed.

    Ties break on index and the result is sorted, so the file is reproducible
    byte for byte (`make gen-check`).
    """
    n = len(coords)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = math.dist(coords[i], coords[j])
            dist[i][j] = dist[j][i] = d

    edges: set[tuple[int, int]] = set()

    for i in range(n):
        near = sorted(range(n), key=lambda j: (dist[i][j], j))
        for j in near[1:LANE_NEIGHBOURS + 1]:
            if dist[i][j] <= LANE_MAX:
                edges.add((min(i, j), max(i, j)))

    # Prim's, O(n^2) -- 95 systems, so the simple form is the right one.
    joined = [False] * n
    best = [math.inf] * n
    parent = [-1] * n
    best[0] = 0.0
    for _ in range(n):
        u = min((k for k in range(n) if not joined[k]),
                key=lambda k: (best[k], k))
        joined[u] = True
        if parent[u] >= 0:
            edges.add((min(u, parent[u]), max(u, parent[u])))
        for v in range(n):
            if not joined[v] and dist[u][v] < best[v]:
                best[v] = dist[u][v]
                parent[v] = u

    return sorted(edges)


def empires() -> dict[str, dict[str, str]]:
    """Design key -> its `initializer` and `flag`, read from src/."""
    out: dict[str, dict[str, str]] = {}
    for path in sorted(PRESCRIPTED.glob("stg_*.txt")):
        text = re.sub(r"#.*", "", path.read_text(encoding="utf-8-sig"))
        for m in re.finditer(r"^(stg_\w+) = \{", text, re.M):
            i, depth, j = m.end() - 1, 0, m.end() - 1
            while j < len(text):
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            body = text[i:j]
            init = re.search(r'^\tinitializer = "([^"]+)"', body, re.M)
            flag = re.search(r"^\tflag = (\w+)", body, re.M)
            out[m.group(1)] = {
                "initializer": init.group(1) if init else "",
                "flag": flag.group(1) if flag else "",
            }
    return out


def main() -> int:
    if not STNH_MAP.is_file():
        print(f"missing {STNH_MAP} — run `make sources-sync` first",
              file=sys.stderr)
        return 1

    emp = empires()
    canon = stnh_positions()

    problems = []
    for key, stnh_key in CANON.items():
        if key not in emp:
            problems.append(f"{key}: no such prescripted empire")
        elif not emp[key]["initializer"]:
            problems.append(f"{key}: declares no initializer")
        elif not emp[key]["flag"]:
            problems.append(f"{key}: declares no `flag =` (see "
                            f"tools/gen_empire_flags.py)")
        if stnh_key not in canon:
            problems.append(f"{key}: STNH's {stnh_key} is not on their default "
                            f"galaxy map")
    if problems:
        print("ERROR: the scenario cannot be generated:", file=sys.stderr)
        for p in problems:
            print(f"    {p}", file=sys.stderr)
        return 1

    homes = [(key, canon[CANON[key]]) for key in CANON]
    allpos = stnh_all_positions()

    stats = []
    for size in SIZES:
        s = scenario(size, emp, homes, allpos)
        if s is None:
            return 1
        stats.append(s)

    LOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    LOC_OUT.write_text(localisation(stats), encoding="utf-8-sig")
    print(f"wrote {LOC_OUT.relative_to(REPO)}  "
          f"({len(stats)} scenario name(s))")
    return 0


def trim(coords: list[tuple[int, int]], n_homes: int,
         target: int) -> list[int]:
    """Which systems survive, as indices, once the map is cut to `target`.

    WHY THIS EXISTS. `separation` is a threshold and the star count it yields
    is a step function of it, so a round number is simply not reachable: at
    scale 0.66 the count goes 599 at separation 19.11 and 603 at 19.10, and
    there is no separation between them that gives 600. Measured, not assumed
    -- the search is in .docs/decisions/111-three-galaxy-sizes.md.

    So the separation is chosen to OVERSHOOT by as little as it can and the
    excess is cut here: four stars for medium, eleven for large, none at all
    for small, whose 70 lands on 95 exactly and whose file is unchanged
    because of it.

    WHICH ONES GO. Repeatedly, the filler star currently closest to any other
    surviving star. That is the removal that costs the map least -- a star in
    the tightest pair is the one whose absence is least visible and whose
    presence contributes least reach -- and it makes the minimum spacing go up
    rather than down, so the cut cannot manufacture a pair the lane graph then
    has to join twice. Homes are never candidates: an empire's seat is the one
    thing on this map that is not interchangeable.

    One at a time, re-measuring after each: dropping the n closest in a single
    pass would take BOTH halves of a tight pair and leave the hole the pair was
    filling. Ties break on index, so the result is reproducible
    (`make gen-check`).
    """
    alive = list(range(len(coords)))
    for _ in range(len(coords) - target):
        worst = min(
            ((min(math.dist(coords[i], coords[j])
                  for j in alive if j != i), i)
             for i in alive if i >= n_homes),
            default=None)
        if worst is None:
            break                    # nothing left but empire homes
        alive.remove(worst[1])
    return alive


def scenario(size: dict, emp: dict[str, dict[str, str]],
             homes: list[tuple[str, tuple[float, float]]],
             allpos: list[tuple[float, float]]) -> dict | None:
    """Write one size's scenario file, and report what went into it.

    Thinning is done per size rather than once because the surviving set is not
    a subset relation the caller could share: a star kept at separation 11 can
    be the one that suppresses a different star at 19, so each size has to walk
    STNH's cloud in file order from the empires outward.
    """
    sep, scale, target = size["separation"], size["scale"], size["systems"]

    kept = [pos for _, pos in homes]
    filler: list[tuple[float, float]] = []
    for pos in allpos:
        if all((pos[0] - k[0]) ** 2 + (pos[1] - k[1]) ** 2 >= sep ** 2
               for k in kept):
            kept.append(pos)
            filler.append(pos)

    def place(pos: tuple[float, float]) -> tuple[int, int]:
        return round(pos[0] * scale), round(pos[1] * scale)

    seen: dict[tuple[int, int], str] = {}
    coords: list[tuple[int, int]] = []      # position of each candidate
    owner: list[str] = []                   # its empire key, or "" for filler
    for key, pos in homes:
        xy = place(pos)
        if xy in seen:
            print(f"ERROR: {size['name']}: {key} and {seen[xy]} land on {xy} "
                  f"after scaling; raise this size's `scale`.", file=sys.stderr)
            return None
        seen[xy] = key
        coords.append(xy)
        owner.append(key)
    for pos in filler:
        xy = place(pos)
        if xy in seen:
            continue          # two canon stars rounded onto one point
        seen[xy] = "filler"
        coords.append(xy)
        owner.append("")

    if len(coords) < target:
        print(f"ERROR: {size['name']}: separation {sep} yields "
              f"{len(coords)} systems, short of the {target} it asks for. "
              f"Lower `separation` -- STNH's cloud holds "
              f"{len(allpos)} positions in all.", file=sys.stderr)
        return None
    cut = len(coords) - target
    alive = trim(coords, len(homes), target)
    coords = [coords[i] for i in alive]
    owner = [owner[i] for i in alive]

    rows, sid = [], 0
    for xy, key in zip(coords, owner):
        if key:
            rows.append(
                f'\tsystem = {{ id = "{sid}" name = "" '
                f"position = {{ x = {xy[0]} y = {xy[1]} }} "
                f'initializer = {emp[key]["initializer"]} '
                f"spawn_weight = {{ base = 0 modifier = {{ add = 100000 "
                f"has_country_flag = {key} }} }} }}")
        else:
            rows.append(f'\tsystem = {{ id = "{sid}" name = "" '
                        f"position = {{ x = {xy[0]} y = {xy[1]} }} }}")
        sid += 1

    lanes = lane_graph(coords)
    rows.append("")
    rows += [f'\tadd_hyperlane = {{ from = "{a}" to = "{b}" }}'
             for a, b in lanes]

    span = max(math.hypot(*xy) for xy in coords)
    body = HEADER.format(
        name=size["name"], label=size["label"],
        label_lower=size["label"].lower(), priority=size["priority"],
        default_line="\tdefault = yes\n" if size["default"] else "",
        scale=scale, separation=f"{sep:g}", homes=len(homes),
        filler=sid - len(homes), total=sid, lanes=len(lanes),
        radius=f"{span:.0f}")
    body += "\n".join(rows) + "\n}\n"

    out = OUT_DIR / size["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")

    longest = max(math.dist(coords[a], coords[b]) for a, b in lanes)
    print(f"wrote {out.relative_to(REPO)}")
    print(f"  {len(homes)} empires, {sid - len(homes)} filler, {sid} systems "
          f"({cut} trimmed to hit {target})")
    print(f"  radius {span:.0f} at scale {scale}, separation {sep:g}")
    print(f"  {len(lanes)} hyperlanes, mean degree "
          f"{2 * len(lanes) / sid:.2f}, longest {longest:.0f} "
          f"(cap {LANE_MAX:.0f}, exceeded only by MST edges)")
    return {"size": size, "systems": sid, "empires": len(homes)}


def localisation(stats: list[dict]) -> str:
    """The picker's entry for every size, from the counts just written.

    The engine renders a scenario's `name` as a loc key, so this file is what
    the setup screen actually shows -- and the star count in it is a fact about
    the map file beside it. Generating both from one run is the only way the
    two cannot disagree; the hand-written version of this file said "95 Star
    Systems" and would have gone on saying it.
    """
    out = [LOC_HEADER]
    for s in stats:
        size = s["size"]
        out.append(
            f' {size["name"]}:0 "\u00a7YThe Known Galaxy \u2014 '
            f'{size["label"]}\u00a7!'
            f'\\n\u00a3system\u00a3 {s["systems"]} Star Systems'
            f'\\n\u00a3pops\u00a3 {s["empires"]} Empires'
            f'\\n\\n\u00a7YStatic Galaxy\u00a7!\\n\\n'
            f'{LOC_BODY}\\n\\n{LOC_NOTE[size["label"]]}"\n')
    return "".join(out)


if __name__ == "__main__":
    raise SystemExit(main())
