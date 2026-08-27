#!/usr/bin/env python3
"""Generate src/map/setup_scenarios/stg_alpha_beta_quadrant.txt — STG's first
static galaxy scenario, the thing that actually puts Trek empires in the galaxy.

WHY THIS EXISTS. Six galaxies contained no Trek AI empire, and three fixes to
the prescripted pool moved the number by nothing, because the pool is not the
mechanism: `prescripted_countries/` is what the PLAYER picks from, and an AI
Trek empire is created by its home system's initializer, which a
`static_galaxy_scenario` puts on the map at a fixed position.
.docs/decisions/91-static-galaxy-is-the-mechanism.md,
.docs/decisions/92-create-country-initializers.md,
.docs/decisions/93-static-galaxy-scenario.md.

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
The filler systems are the same map's other positions, thinned to a minimum
separation so the density is even and the quadrant shape survives; the whole
cloud is then scaled by SCALE. Nothing is random and nothing is authored, so a
re-run reproduces the file byte for byte (`make gen-check`).

Filler systems carry `name = ""` on purpose. The engine draws their names from
the pool, which is 1,444 Trek star names already
(.docs/decisions/52-trek-star-names.md), and hard-coding STNH's own names here
would both duplicate that pool and put raw English in a file that should hold
loc keys.

TWO EMPIRES ARE DELIBERATELY ABSENT and both are recorded in decision 93:

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
OUT = REPO / "src/map/setup_scenarios/stg_alpha_beta_quadrant.txt"

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

# Minimum separation between filler systems, in STNH's own coordinates, chosen
# by measurement rather than by taste: 70 leaves 95 systems, which is 4.5 stars
# per empire -- STNH's smallest canon map, `09 botf`, is 468 stars for 99
# weighted systems, or 4.7. Raise it for a sparser galaxy, lower it for a
# denser one; the count is printed on every run.
MIN_SEPARATION = 70.0

# STNH's default map is a full 500-radius galaxy and this is a fifth of its
# star count, so the cloud has to come in with it or the empires end up days
# apart. At 0.36 the extent is a radius of ~218 and the median nearest
# neighbour is 26 units, against vanilla's own `max_hyperlane_distance = 50` --
# so every system has a neighbour close enough to reach.
SCALE = 0.36

# Modelled on STNH's `04 STH_galaxy_tiny_alpha_beta`, the closest thing in
# .source/ to what this is: a small, canon, static Alpha/Beta map.
#
# `num_empires = { min = 0 max = 0 }` is theirs and it is the point -- every
# empire in the galaxy comes from an initializer, so no randomly generated
# non-Trek empire can appear. Nine of STNH's 22 maps set it.
#
# `random_hyperlanes = no` with no `add_hyperlane` line anywhere is also
# theirs: 21 of their 22 maps define no lanes at all, the exception being the
# 468-system BotF map with 892 of them. `num_hyperlanes` is the density the
# setup screen offers, and 04's 0.5-1.0 is a live range rather than the
# `{ min = 0 max = 0 }` ten of their maps lock it to -- the safer of the two
# while nobody here has watched a static map generate.
#
# `default = yes` is NOT set. Ariphaos Galaxies' `medium.txt` already carries
# it and two defaults is worse than none; it belongs with the picker lock,
# which .docs/planning/static-galaxy-plan.md deliberately leaves until an STG
# scenario is known to be playable.
HEADER = """\
# GENERATED by tools/gen_static_galaxy.py — do not hand-edit; regenerate.
#
# STG's first static galaxy scenario. Every Trek empire in the galaxy is placed
# here and created by the initializer this file names for it; the prescripted
# pool is the player's roster and has nothing to do with it.
# See .docs/decisions/93-static-galaxy-scenario.md.
#
# Positions are STNH's, harvested from their default galaxy map and scaled by
# {scale}. Filler systems carry no initializer and no name: the engine builds
# and names them from STG's own Trek star pool.
#
# {homes} empires placed, {filler} filler systems, {total} systems in all.

static_galaxy_scenario = {{
\tname = "STG_galaxy_alpha_beta"
\tpriority = 0

\tcolonizable_planet_odds = 1.0
\tprimitive_odds = 1.0

\t# Nobody but the initializers puts an empire in this galaxy.
\tnum_empires = {{ min = 0 max = 0 }}
\tnum_empire_default = 0
\tadvanced_empire_default = 0
\tfallen_empire_default = 0
\tfallen_empire_max = 0
\tcore_radius = 0

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
    kept = [pos for _, pos in homes]
    filler: list[tuple[float, float]] = []
    for pos in stnh_all_positions():
        if all((pos[0] - k[0]) ** 2 + (pos[1] - k[1]) ** 2
               >= MIN_SEPARATION ** 2 for k in kept):
            kept.append(pos)
            filler.append(pos)

    def place(pos: tuple[float, float]) -> tuple[int, int]:
        return round(pos[0] * SCALE), round(pos[1] * SCALE)

    seen: dict[tuple[int, int], str] = {}
    rows, sid = [], 0
    for key, pos in homes:
        xy = place(pos)
        if xy in seen:
            print(f"ERROR: {key} and {seen[xy]} land on {xy} after scaling; "
                  f"raise SCALE.", file=sys.stderr)
            return 1
        seen[xy] = key
        rows.append(
            f'\tsystem = {{ id = "{sid}" name = "" '
            f"position = {{ x = {xy[0]} y = {xy[1]} }} "
            f'initializer = {emp[key]["initializer"]} '
            f"spawn_weight = {{ base = 0 modifier = {{ add = 100000 "
            f"has_country_flag = {key} }} }} }}")
        sid += 1
    for pos in filler:
        xy = place(pos)
        if xy in seen:
            continue          # two canon stars rounded onto one point
        seen[xy] = "filler"
        rows.append(f'\tsystem = {{ id = "{sid}" name = "" '
                    f"position = {{ x = {xy[0]} y = {xy[1]} }} }}")
        sid += 1

    body = HEADER.format(scale=SCALE, homes=len(homes),
                         filler=sid - len(homes), total=sid)
    body += "\n".join(rows) + "\n}\n"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(body, encoding="utf-8")

    span = max(math.hypot(*place(p)) for p in kept)
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"  {len(homes)} empires, {sid - len(homes)} filler, {sid} systems")
    print(f"  radius {span:.0f} at scale {SCALE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
