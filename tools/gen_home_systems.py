#!/usr/bin/env python3
"""One-shot generator: a real home system for every STG prescripted empire.

Writes src/common/solar_system_initializers/stg_home_systems.txt and reports
which empires it could not place. Its CONTENT comes from `.source/`, never from
the built tree -- same rule as tools/gen_shipsets.py. stg-build/ is read for one
question only: which planet and star classes the merge declares, so a `class`
value can be told from an engine keyword. See `declared()`.

WHY THIS EXISTS. Not one STG empire declared `initializer =`, on the strength of
.docs/planning/scope.md's "Trek-named systems in a normally generated galaxy, no hand-placed
homeworlds". The consequence was visible in play: `system_name` and `planet_name`
are only *labels*, so "Sol" was a label on a randomly generated system whose
other planets were named from the Federation name list's `planet_names` pool --
which is a list of Federation MEMBER worlds. Sol therefore contained Bajor and
Andoria. The same was true of all 101 empires.

WHAT IT DOES. Decision 19's pattern, applied to systems instead of empires:
STNH's *identity*, vanilla's *mechanics*. STNH ships 168 home systems with
`usage = custom_empire` -- Qo'noS with Boreth and Gorath, 40 Eridani with Keid
and T'Khut, Romulus with Remus. We take their geometry (system name, star class,
planet names, classes, sizes, orbits, moons, asteroid belts) and drop every line
of STNH's own scripting, because that is what we deliberately do not vendor:
the init_effect blocks set STNH country flags, save STNH event targets and call
STNH species flags, none of which exist here.

The starting planet keeps only what vanilla's own Sol does -- `starting_planet`,
`prevent_anomaly`. The engine generates pops and home-system deposits itself;
vanilla never scripts them in an initializer, and neither do we.

MATCHING is by three passes, in order, because STG's own localisation already
names each empire's system and usually agrees with STNH's:
  1. STG's `system_name` loc VALUE against STNH's initializer `name`
     ("40 Eridani" -> vulcan_homeworld). The pass yields are printed on every
     run -- read them off the output rather than from a figure here.
  2. a species token from the empire key against `<token>_homeworld`
     (stg_minor_nausicaan_tribes -> nausicaan_homeworld).
  3. ALIASES below, for the ones whose STG and STNH names genuinely differ
     (the Dominion is "Omarion Nexus" here and "Founder's Planet" there).

The Federation is deliberately NOT generated: vanilla's own
`sol_system_initializer` is the real solar system, Mercury through Varuna with
Luna, the Galileans, Titan and Triton, and Real Space overrides that same key
with a rescaled copy. Pointing at it beats reproducing it. The mirror Terran
Empire does NOT share it -- it has its own authored Sol below. Sharing an
initializer between two prescripted empires costs both of them and logs nothing;
see SKIP, and .docs/decisions/88-playable-gates-the-design-database.md.

Run:  python3 tools/gen_home_systems.py
"""

from __future__ import annotations

import functools
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STNH = REPO / ".source/688086068/common/solar_system_initializers"
PRESCRIPTED = REPO / "src/prescripted_countries"
LOC = REPO / "src/localisation/english"
OUT = REPO / "src/common/solar_system_initializers/stg_home_systems.txt"
BUILD = REPO / "stg-build"
VANILLA = Path("/stellaris")

# Class names the engine understands without any planet_classes/ declaration:
# `star` is filled in from the system's own star class, `black_hole` and the
# asteroid keywords are built in. They must be emitted BARE -- quoting one
# stops it resolving. See .docs/decisions/27-quoted-class-keyword.md.
CLASS_BUILTINS = {"star", "black_hole"}

# Empires that do not get a generated system, and why.
SKIP = {
    # Real Sol, already in the tree twice over (vanilla + Real Space's rescale).
    "stg_united_federation_of_planets": "sol_system_initializer",
    # The mirror Terran Empire USED to share sol_system_initializer with the
    # Federation. It no longer does: it has its own authored mirror Sol below.
    # Sharing was recorded as a benign race the loser survives -- "confirm
    # against a live run" -- and three live runs falsified it. NEITHER empire
    # spawned in any of them, the Federation not even on `spawn_enabled =
    # always`. Two prescripted empires naming one starting system is a
    # documented engine failure that logs nothing and costs BOTH of them.
    # See .docs/decisions/88-playable-gates-the-design-database.md.
}

# STG name -> STNH initializer key, where the two genuinely disagree.
ALIASES = {
    "stg_dominion": "founders_homeworld",
}

# A NAME STNH ITSELF DUPLICATES. Not a conversion bug -- their own file gives
# both moons of the gas giant S'latas the name "S'latas a", where the rest of
# their Romulan system uses the letter suffix properly. Decision 12 says fix a
# source's errors rather than drop the source, and their own convention says
# what the fix is, so the second moon becomes "S'latas b".
#
# Keyed by STG empire -> name -> the names its occurrences take IN ORDER. Keep
# this table small: it is for a defect in the source, not for a disagreement of
# taste, and `check_home_system_body_names` will report anything new that
# belongs here.
SOURCE_NAME_FIXES = {
    "stg_romulan_star_empire": {"S'latas a": ["S'latas a", "S'latas b"]},
}

# STNH star classes that are STNH's own. 40 Eridani is a K dwarf, a white dwarf
# and a red dwarf, so vanilla's sc_trinary_k_m_d is not an approximation -- it
# is the same three stars.
#
# Each must keep the *number* of stars, because the initializer's own
# `class = star` planets are filled from this class: a binary system given a
# single-star class loses a star. See .docs/decisions/26-home-system-classes.md.
STAR_CLASS = {
    "sc_trinary_kdm": "sc_trinary_k_m_d",
    # STNH's G+K binary; vanilla's g_k binary is the same two stars.
    "sc_binary_gk": "sc_binary_g_k",
    # Denobula's G+F+F. Vanilla has no g_f_f, so a_f_g -- it keeps the G that
    # STNH declares as the system's own class, plus one of the two F's.
    "sc_trinary_gff": "sc_trinary_a_f_g",
}

# STNH uses Trek's own planet taxonomy (Class F, G, N, Y ...). Vanilla has no
# such classes, so each maps to the vanilla class that behaves the same way.
# Habitability is what matters: none of these is a colonisable world in STNH
# either, bar the two noted.
PLANET_CLASS = {
    "pc_i_class": "pc_gas_giant",          # Class I, gas supergiant
    "pc_u_class": "pc_gas_giant",          # Class U, ultragiant
    "pc_y_class": "pc_toxic",              # Class Y, "demon" world
    "pc_n_class_titaic": "pc_toxic",       # Class N, Venus-like runaway
    "pc_f_class": "pc_barren",             # Class F, geometallic
    "pc_g_class": "pc_barren",             # Class G, geocrystalline
    "pc_k_luna_class": "pc_barren",        # Class K, Mars-like
    "pc_k_ares_class": "pc_barren",
    "pc_c_class_aquarian": "pc_frozen",    # Class C, icy
    "pc_thegreatlink": "pc_ocean",         # the Great Link is a liquid world
    "pc_unimatrix": "pc_machine",          # Borg unicomplex
    "pc_helix": "pc_machine",
    "pc_invisible_star": "pc_g_star",      # a structural placeholder star
    # All `colonizable = no` in STNH too, so pc_barren keeps the habitability
    # and the class carries STNH's own icon choice where vanilla has one.
    "pc_d_class_solitanian": "pc_barren",  # Class D sandsea, uninhabitable
    "pc_k_class_adaptable": "pc_barren",   # Class K, as pc_k_luna/ares above
    "pc_k_class_transjovian": "pc_barren",
    "pc_o_class_sulfur": "pc_barren",
    "pc_e_class": "pc_toxic",              # Class E, hot -- STNH's toxic icon
    # The other two colonisable exceptions, alongside pc_thegreatlink. Both are
    # `is_artificial_planet` habitats and both are their empire's capital, whose
    # class the prescripted empire overrides with pc_continental -- so mapping
    # here to pc_continental makes the initializer and the empire agree, which
    # is the same rule the hand-written systems below follow.
    "pc_voth_city_ship": "pc_continental",
    "pc_hunters_lodge": "pc_continental",
}

# STNH asteroid belt types, same story as the classes: STH_asteroid_belts.txt
# adds one to vanilla's six, and we do not vendor STNH's common/.
ASTEROID_BELT = {"icy_asteroid_belt_dispersed": "icy_asteroid_belt"}

# Systems whose STNH star class does not supply enough stars for the number of
# `class = star` planets STNH's own geometry places. Keyed by STG empire.
#
# STNH gets away with it because a `class = star` planet beyond the star
# class's list has nothing to draw from; the count has to match, and vanilla
# never breaks that rule in 40 files. Romulus is the one case here: STNH
# declares `sc_m` and then places **Hobus** — the star that destroys Romulus in
# the 2009 film — as a second star flagged `secondaryStar`. Two M stars keeps
# both STNH's star type and Hobus.
# See .docs/decisions/26-home-system-classes.md.
SYSTEM_STAR_CLASS = {"stg_romulan_star_empire": "sc_binary_m_m"}

# Keys copied straight through from an STNH planet/moon block. Everything else
# is dropped: `entity` names STNH meshes, `modifiers` and `flags` name STNH
# content, and `init_effect` is STNH's empire scripting.
PLANET_KEEP = ("name", "class", "orbit_distance", "orbit_angle", "size",
               "has_ring", "starting_planet")

# Ten playable empires whose STNH home system is procedural (see load_stnh),
# so there is no geometry to convert and it is written here instead. Each is
# vanilla-shaped: a star, an incremental orbit chain, the capital, and enough
# neighbours to make a system worth surveying. The capital's `class` is left to
# the prescripted empire, which overrides the initializer's -- vanilla's
# plantoid_humans does exactly that with Sol -- so these carry the class STG
# already declares, and the two agree.
#
# Canon drives the details rather than decoration: Bolarus IX is the ninth
# planet and so has eight ahead of it; Tholia is a hot, high-radiation world
# around an F star because Tholians are crystalline and live near 450 K; Breen
# is frigid; Malon Prime is ringed by the industrial waste its people export.
AUTHORED: dict[str, str] = {
    "stg_ferengi_alliance": '''\
\tname = "STG_system_name_ferengi"
\tclass = "sc_k"
\tasteroid_belt = { type = rocky_asteroid_belt radius = 110 }

\tplanet = { name = "STG_system_name_ferengi" class = "pc_k_star" orbit_distance = 0 orbit_angle = 1 size = 25 has_ring = no }
\tplanet = { name = "STG_N_FerengiI" class = "pc_molten" orbit_distance = 40 orbit_angle = 70 size = 9 has_ring = no }
\tplanet = { name = "STG_N_FerengiII" class = "pc_barren" orbit_distance = 25 orbit_angle = 190 size = 11 has_ring = no }
\t@CAPITAL@
\tplanet = { name = "STG_N_Gorlack" class = "pc_barren_cold" orbit_distance = 30 orbit_angle = 15 size = 10 has_ring = no }
\tplanet = { name = "STG_N_Clarus" class = "pc_gas_giant" orbit_distance = 55 orbit_angle = 240 size = 27 has_ring = yes }
''',
    "stg_trill_symbiosis": '''\
\tname = "STG_system_name_trill"
\tclass = "sc_g"

\tplanet = { name = "STG_system_name_trill" class = "pc_g_star" orbit_distance = 0 orbit_angle = 1 size = 28 has_ring = no }
\tplanet = { name = "STG_N_TrilliusI" class = "pc_molten" orbit_distance = 45 orbit_angle = 110 size = 8 has_ring = no }
\tplanet = { name = "STG_N_TrilliusII" class = "pc_barren" orbit_distance = 25 orbit_angle = 260 size = 12 has_ring = no }
\t@CAPITAL@
\tplanet = { name = "STG_N_Mak_ala" class = "pc_barren_cold" orbit_distance = 28 orbit_angle = 40 size = 9 has_ring = no }
\tplanet = { name = "STG_N_TrilliusVI" class = "pc_gas_giant" orbit_distance = 60 orbit_angle = 320 size = 26 has_ring = no }
''',
    "stg_bolian_union": '''\
\tname = "STG_system_name_bolian"
\tclass = "sc_g"
\tasteroid_belt = { type = icy_asteroid_belt radius = 420 }

\tplanet = { name = "STG_system_name_bolian" class = "pc_g_star" orbit_distance = 0 orbit_angle = 1 size = 27 has_ring = no }
\tplanet = { name = "STG_N_BolarusI" class = "pc_molten" orbit_distance = 35 orbit_angle = 20 size = 8 has_ring = no }
\tplanet = { name = "STG_N_BolarusII" class = "pc_barren" orbit_distance = 20 orbit_angle = 95 size = 10 has_ring = no }
\tplanet = { name = "STG_N_BolarusIII" class = "pc_toxic" orbit_distance = 18 orbit_angle = 165 size = 12 has_ring = no }
\tplanet = { name = "STG_N_BolarusIV" class = "pc_barren" orbit_distance = 16 orbit_angle = 230 size = 9 has_ring = no }
\tplanet = { name = "STG_N_BolarusV" class = "pc_gas_giant" orbit_distance = 40 orbit_angle = 300 size = 25 has_ring = yes }
\tplanet = { name = "STG_N_BolarusVI" class = "pc_gas_giant" orbit_distance = 35 orbit_angle = 10 size = 23 has_ring = no }
\tplanet = { name = "STG_N_BolarusVII" class = "pc_frozen" orbit_distance = 30 orbit_angle = 75 size = 11 has_ring = no }
\tplanet = { name = "STG_N_BolarusVIII" class = "pc_barren_cold" orbit_distance = 25 orbit_angle = 140 size = 10 has_ring = no }
\t@CAPITAL@
''',
    "stg_breen_confederacy": '''\
\tname = "STG_system_name_breen"
\tclass = "sc_m"
\tasteroid_belt = { type = icy_asteroid_belt radius = 300 }

\tplanet = { name = "STG_system_name_breen" class = "pc_m_star" orbit_distance = 0 orbit_angle = 1 size = 20 has_ring = no }
\tplanet = { name = "STG_N_BreenI" class = "pc_barren" orbit_distance = 30 orbit_angle = 130 size = 9 has_ring = no }
\tplanet = { name = "STG_N_Portas" class = "pc_frozen" orbit_distance = 22 orbit_angle = 210 size = 12 has_ring = no }
\t@CAPITAL@
\tplanet = { name = "STG_N_Dozaria" class = "pc_barren_cold" orbit_distance = 32 orbit_angle = 55 size = 11 has_ring = no }
\tplanet = { name = "STG_N_BreenVI" class = "pc_gas_giant" orbit_distance = 58 orbit_angle = 285 size = 26 has_ring = yes }
''',
    "stg_tholian_assembly": '''\
\tname = "STG_system_name_tholian"
\tclass = "sc_f"
\tasteroid_belt = { type = rocky_asteroid_belt radius = 130 }

\tplanet = { name = "STG_system_name_tholian" class = "pc_f_star" orbit_distance = 0 orbit_angle = 1 size = 30 has_ring = no }
\tplanet = { name = "STG_N_TholiaI" class = "pc_molten" orbit_distance = 35 orbit_angle = 45 size = 10 has_ring = no }
\t@CAPITAL@
\tplanet = { name = "STG_N_TholiaIII" class = "pc_molten" orbit_distance = 26 orbit_angle = 175 size = 9 has_ring = no }
\tplanet = { name = "STG_N_TholiaIV" class = "pc_barren" orbit_distance = 30 orbit_angle = 250 size = 12 has_ring = no }
\tplanet = { name = "STG_N_TholiaV" class = "pc_gas_giant" orbit_distance = 62 orbit_angle = 330 size = 28 has_ring = no }
''',
    "stg_yridian_empire": '''\
\tname = "STG_system_name_yridian"
\tclass = "sc_k"

\tplanet = { name = "STG_system_name_yridian" class = "pc_k_star" orbit_distance = 0 orbit_angle = 1 size = 24 has_ring = no }
\tplanet = { name = "STG_N_YridiaI" class = "pc_molten" orbit_distance = 38 orbit_angle = 60 size = 8 has_ring = no }
\t@CAPITAL@
\tplanet = { name = "STG_N_YridiaIII" class = "pc_barren" orbit_distance = 28 orbit_angle = 200 size = 11 has_ring = no }
\tplanet = { name = "STG_N_YridiaIV" class = "pc_gas_giant" orbit_distance = 55 orbit_angle = 290 size = 25 has_ring = yes }
''',
    "stg_krenim_empire": '''\
\tname = "STG_system_name_krenim"
\tclass = "sc_g"
\tasteroid_belt = { type = rocky_asteroid_belt radius = 120 }

\tplanet = { name = "STG_system_name_krenim" class = "pc_g_star" orbit_distance = 0 orbit_angle = 1 size = 26 has_ring = no }
\tplanet = { name = "STG_N_KyanaI" class = "pc_barren" orbit_distance = 40 orbit_angle = 85 size = 9 has_ring = no }
\t@CAPITAL@
\tplanet = { name = "STG_N_KyanaIII" class = "pc_toxic" orbit_distance = 27 orbit_angle = 220 size = 12 has_ring = no }
\tplanet = { name = "STG_N_KyanaIV" class = "pc_frozen" orbit_distance = 33 orbit_angle = 305 size = 10 has_ring = no }
\tplanet = { name = "STG_N_KyanaV" class = "pc_gas_giant" orbit_distance = 58 orbit_angle = 25 size = 27 has_ring = no }
''',
    "stg_malon_empire": '''\
\tname = "STG_system_name_malon"
\tclass = "sc_g"
\tasteroid_belt = { type = rocky_asteroid_belt radius = 125 }

\tplanet = { name = "STG_system_name_malon" class = "pc_g_star" orbit_distance = 0 orbit_angle = 1 size = 27 has_ring = no }
\tplanet = { name = "STG_N_MalonI" class = "pc_molten" orbit_distance = 42 orbit_angle = 100 size = 9 has_ring = no }
\t@CAPITAL@
\tplanet = { name = "STG_N_Neled" class = "pc_toxic" orbit_distance = 26 orbit_angle = 195 size = 13 has_ring = no }
\tplanet = { name = "STG_N_MalonIV" class = "pc_toxic" orbit_distance = 24 orbit_angle = 265 size = 11 has_ring = no }
\tplanet = { name = "STG_N_MalonV" class = "pc_gas_giant" orbit_distance = 56 orbit_angle = 340 size = 26 has_ring = yes }
''',
    # The mirror Terran Empire's Sol, authored rather than shared. Vanilla's
    # sol_system_initializer carries `sol`, `sol_system`, `planet_earth` and
    # `planet_mars` flags that vanilla events address by name, so a second
    # system cannot copy them -- the geometry comes across, the flags do not.
    # Planet names are vanilla's own NAME_* keys, already localised.
    "stg_terran_empire": '''\
\tname = "STG_system_name_terran"
\tclass = "sc_g"
\tasteroid_belt = { type = rocky_asteroid_belt radius = 145 }

\tplanet = { name = "STG_system_name_terran" class = "pc_g_star" orbit_distance = 0 orbit_angle = 1 size = 30 has_ring = no }
\tplanet = { name = "NAME_Mercury" class = "pc_molten" orbit_distance = 40 orbit_angle = 70 size = 10 has_ring = no }
\tplanet = { name = "NAME_Venus" class = "pc_toxic" orbit_distance = 25 orbit_angle = 190 size = 17 has_ring = no }
\t@CAPITAL@
\tplanet = { name = "NAME_Mars" class = "pc_barren" orbit_distance = 25 orbit_angle = 15 size = 13 has_ring = no }
\tplanet = { name = "NAME_Jupiter" class = "pc_gas_giant" orbit_distance = 40 orbit_angle = 240 size = 35 has_ring = no }
\tplanet = { name = "NAME_Saturn" class = "pc_gas_giant" orbit_distance = 35 orbit_angle = 310 size = 30 has_ring = yes }
''',
    "stg_vidiian_empire": '''\
\tname = "STG_system_name_vidiian"
\tclass = "sc_k"

\tplanet = { name = "STG_system_name_vidiian" class = "pc_k_star" orbit_distance = 0 orbit_angle = 1 size = 25 has_ring = no }
\tplanet = { name = "STG_N_VidiiaI" class = "pc_barren" orbit_distance = 36 orbit_angle = 50 size = 8 has_ring = no }
\t@CAPITAL@
\tplanet = { name = "STG_N_Fina_Prime" class = "pc_barren_cold" orbit_distance = 29 orbit_angle = 180 size = 11 has_ring = no }
\tplanet = { name = "STG_N_VidiiaIV" class = "pc_gas_giant" orbit_distance = 54 orbit_angle = 275 size = 26 has_ring = no }
''',
}

# The capital block every authored system substitutes for @CAPITAL@. `class` is
# deliberately absent: the prescripted empire's `planet_class` supplies it.
CAPITAL = '''\tplanet = {
\t\tname = "@PLANET@"
\t\tclass = "@CLASS@"
\t\torbit_distance = 22
\t\torbit_angle = 145
\t\tsize = 18
\t\tstarting_planet = yes
\t\thas_ring = no
\t\tdeposit_blockers = none
\t\tmodifiers = none
\t\tinit_effect = { prevent_anomaly = yes }
\t\tinit_effect = { generate_empire_home_planet = yes }
@AI_EMPIRE@
\t}'''


# ── parsing ───────────────────────────────────────────────────────────────────

def strip_comments(text: str) -> str:
    return re.sub(r"#.*", "", text)


def top_blocks(text: str) -> dict[str, str]:
    """Depth-0 `key = { … }` blocks, brace-matched. Returns key -> body."""
    out: dict[str, str] = {}
    for m in re.finditer(r"^([A-Za-z_0-9]+)\s*=\s*\{", text, re.M):
        i = m.end() - 1
        depth = 0
        j = i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out[m.group(1)] = text[i + 1:j]
    return out


def sub_blocks(body: str, keyword: str) -> list[str]:
    """Immediate `keyword = { … }` children of `body`, brace-matched.

    IMMEDIATE is the whole point and it used not to be true: the `finditer`
    below scans the entire body, so before the `depth` guard this returned
    matches at EVERY nesting level while claiming in this docstring to return
    one. STNH nests a `planet` inside a `planet` -- Kerkhov is a gas giant
    orbiting the star 40 Eridani C, not the system primary -- and the moon of
    that nested planet was therefore returned as a moon of the STAR as well as
    of its own parent. Both got emitted, so two different bodies in 40 Eridani
    came out named "Kerkhov's Moon". See `planets_flattened` for the other half
    of the repair, and .docs/decisions/84-shipset-descs-and-home-system-names.md.
    """
    out = []
    for m in re.finditer(rf"\b{keyword}\s*=\s*\{{", body):
        i = m.end() - 1
        # How deep is this match? Only depth 0 is an immediate child.
        if body.count("{", 0, i) - body.count("}", 0, i) != 0:
            continue
        depth = 0
        j = i
        while j < len(body):
            if body[j] == "{":
                depth += 1
            elif body[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(body[i + 1:j])
    return out


def planets_flattened(body: str) -> list[str]:
    """Every `planet` block under `body`, promoted to system level.

    STNH sometimes writes a planet as a child of another planet. Stellaris'
    own initializers never do -- a satellite is a `moon` -- and `orbit_distance`
    is relative to whatever the body orbits, so promoting a nested planet to a
    sibling keeps the geometry and drops a nesting the engine has no use for.
    That promotion is what this generator has always done; it just used to fall
    out of `sub_blocks` scanning at every depth, which cost a duplicated moon.
    Doing it explicitly keeps the promotion and loses the duplicate.
    """
    out = []
    for pl in sub_blocks(body, "planet"):
        out.append(pl)
        out.extend(planets_flattened(pl))
    return out


def scalar(body: str, key: str) -> str | None:
    """A scalar `key = value` at the TOP level of `body`.

    Ranges collapse to their midpoint. STNH writes `orbit_angle = { min = 30
    max = 270 }` in places, and an earlier version of this flattened the braces
    away and then matched the *next* key's name as the value -- one system came
    out with `orbit_angle = size`. Look for the block form first, so a range is
    recognised as a range instead of decaying into whatever follows it.
    """
    rng = re.search(rf"\b{key}\s*=\s*\{{\s*min\s*=\s*(-?[\d.]+)\s*max\s*=\s*(-?[\d.]+)\s*\}}",
                    body)
    if rng:
        return str(int((float(rng.group(1)) + float(rng.group(2))) / 2))

    flat = body
    for _ in range(8):
        nxt = re.sub(r"\{[^{}]*\}", " ", flat)
        if nxt == flat:
            break
        flat = nxt
    m = re.search(rf'\b{key}\s*=\s*"([^"]*)"', flat) or \
        re.search(rf"\b{key}\s*=\s*(-?[\w.']+)", flat)
    if not m:
        return None
    val = m.group(1)
    # A bare word that is itself one of our keys means the real value was a
    # block we could not read; treat it as absent rather than emit nonsense.
    return None if val in PLANET_KEEP or val in ("min", "max") else val


def load_loc() -> dict[str, str]:
    loc = {}
    for p in LOC.glob("*.yml"):
        for line in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = re.match(r'\s*([A-Za-z_0-9]+):\d*\s*"(.*)"\s*$', line)
            if m:
                loc[m.group(1)] = m.group(2)
    return loc


def load_empires() -> dict[str, dict]:
    out = {}
    for p in sorted(PRESCRIPTED.glob("stg_*.txt")):
        for key, body in top_blocks(strip_comments(p.read_text(encoding="utf-8",
                                                               errors="replace"))).items():
            out[key] = {
                "file": p.name,
                "body": body,
                "system_key": scalar(body, "system_name"),
                "planet_key": scalar(body, "planet_name"),
                "planet_class": scalar(body, "planet_class"),
            }
    return out


def load_stnh() -> dict[str, str]:
    """STNH home systems we can actually convert: FIXED GEOMETRY only.

    122 of STNH's 156 are procedural -- `class = "rl_starting_stars"`,
    `size = { min max }`, `count = { }` -- and those random lists live in
    STNH's own common/random_lists/, which is exactly the common/ we do not
    vendor. Converting one would mean either vendoring that too or inventing
    the geometry, so they are excluded here and the empires that wanted them
    are reported instead. 34 are fixed, and they are the ones that matter:
    Qo'noS, 40 Eridani, Romulus, Cardassia, Bajor, Procyon, Unimatrix 01.
    """
    out = {}
    for p in sorted(STNH.rglob("*.txt")):
        for key, body in top_blocks(strip_comments(p.read_text(encoding="utf-8",
                                                               errors="replace"))).items():
            if "mirror" in key.lower():
                continue
            if not re.search(r"usage\s*=\s*custom_empire", body):
                continue
            if "rl_" in body or re.search(r"count\s*=\s*\{", body):
                continue                      # procedural -- see docstring
            if "starting_planet" not in body:
                continue                      # a satellite, not a home system
            out.setdefault(key, body)
    return out


# ── conversion ────────────────────────────────────────────────────────────────

def declared(kind: str, prefix: str = "") -> set[str]:
    """Every top-level key declared under common/<kind>/, read from the merged
    build if it has been built and from vanilla otherwise.

    Derived rather than listed, for the reason in .docs/validation/check-design.md rule 4: a hand-kept
    allowlist goes stale against a game patch or a newly harvested source, and
    the failure is silent. Vanilla is the floor because the build is optional
    here -- the generator has to work before the first `make vendor`.
    """
    found: set[str] = set()
    for root in (VANILLA, BUILD):
        d = root / "common" / kind
        if not d.is_dir():
            continue
        for f in d.rglob("*.txt"):
            text = strip_comments(f.read_text(encoding="utf-8-sig", errors="replace"))
            found |= set(re.findall(rf"^\s*({prefix}[a-z0-9_]+)\s*=\s*\{{", text, re.M))
    return found


@functools.cache
def declared_classes() -> frozenset[str]:
    """Every planet and star class name that exists as a declaration.

    A `class` value outside this set is an engine keyword (`star`, `random`,
    `none`, …) rather than a name, and the two are emitted differently.
    See `is_class_keyword`.
    """
    return frozenset(declared("planet_classes") | declared("star_classes"))


def is_class_keyword(val: str) -> bool:
    """Is this `class` value an engine keyword rather than a declared name?

    Quoting decides whether the engine resolves it. Vanilla quotes declared
    names freely -- 891 quoted `pc_*` against 750 bare -- but never quotes a
    keyword: 0 quoted against 671 bare across `star`, `none`, `random`,
    `random_non_colonizable`, `ideal_planet_class` and the rest. A quoted
    keyword parses cleanly and then fails to resolve, so the body is simply
    never created and the log says one line.
    See .docs/decisions/27-quoted-class-keyword.md.
    """
    pool = declared_classes()
    return bool(pool) and val not in pool


def star_count(sc_key: str) -> int | None:
    """How many stars a star class supplies to `class = star` planets."""
    for root in (VANILLA, BUILD):
        d = root / "common/star_classes"
        if not d.is_dir():
            continue
        for f in d.rglob("*.txt"):
            text = strip_comments(f.read_text(encoding="utf-8-sig", errors="replace"))
            m = re.search(rf"^{re.escape(sc_key)}\s*=\s*\{{", text, re.M)
            if not m:
                continue
            depth, j = 0, m.end() - 1
            for n, ch in enumerate(text[j:], j):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return len(re.findall(r"^\s*planet\s*=", text[j:n + 1], re.M))
    return None


def check_references(text: str) -> list[str]:
    """Everything in the generated file that must resolve against the merged
    tree, and does not.

    This exists because the remap tables were applied as `MAP.get(val, val)` —
    an STNH name with no mapping was written through *unchanged*, naming
    something STG does not vendor (STNH's common/ is not harvested; we take its
    art). The engine does not survive it: it hard-crashes initialising
    CSystemInitializerDataBase, with nothing in error.log.

    Four families, because each round of fixes revealed the next:
    planet/star classes, asteroid belt types, the star *count* — a
    `class = star` planet beyond what the system's star class supplies has no
    star to draw from, and vanilla never does it in 40 files — and the
    *quoting* of a class keyword, which decides whether it resolves at all.
    See .docs/decisions/26-home-system-classes.md and
    .docs/decisions/27-quoted-class-keyword.md.
    """
    pc = declared("planet_classes", "pc_")
    sc = declared("star_classes", "sc_")
    belts = declared("asteroid_belts")
    if not pc or not sc or not belts:
        return []                      # no reference tree to check against

    bad = []
    # Quoted values must name a declared class; a keyword quoted here parses and
    # then silently resolves to nothing, so the body is never created.
    for name in sorted(set(re.findall(r'\bclass\s*=\s*"([^"]+)"', text))):
        pool = sc if name.startswith("sc_") else pc
        if name in CLASS_BUILTINS or is_class_keyword(name):
            bad.append(f"class keyword '{name}' is quoted; it must be bare")
        elif name not in pool:
            bad.append(f"class '{name}'")
    for name in sorted(set(re.findall(r"asteroid_belt\s*=\s*\{\s*type\s*=\s*(\w+)", text))):
        if name not in belts:
            bad.append(f"asteroid belt type '{name}'")

    # Star count, per initializer.
    for m in re.finditer(r'^([a-z_0-9]+)\s*=\s*\{', text, re.M):
        depth, j = 0, m.end() - 1
        body = ""
        for n, ch in enumerate(text[j:], j):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    body = text[j:n + 1]
                    break
        cm = re.search(r'class\s*=\s*"(sc_[a-z0-9_]+)"', body)
        if not cm:
            continue
        have = star_count(cm.group(1))
        if have is None:
            continue
        want, stack = 0, []
        # Uppercase keys push too. `NOT = {` is a block like any other, and a
        # walker that popped on its `}` without pushing on its `{` unbalanced
        # the stack from the first AI-empire guard onwards — see
        # `ai_empire_block`.
        for t in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{|(\})|class\s*=\s*"?star"?\b', body):
            if t.group(1) is not None:
                stack.append(t.group(1))
            elif t.group(2) is not None:
                if stack:
                    stack.pop()
            elif stack and stack[-1] in ("planet", "moon"):
                want += 1
        if want > have:
            bad.append(f"{m.group(1)}: star class {cm.group(1)} supplies "
                       f"{have} star(s) but {want} `class = star` planet(s) "
                       f"need one (add a SYSTEM_STAR_CLASS override)")
    return bad


def convert_body(body: str, indent: str) -> list[str]:
    """A planet/moon block reduced to geometry, with classes remapped."""
    lines = []
    for key in PLANET_KEEP:
        val = scalar(body, key)
        if val is None:
            continue
        if key == "class":
            val = PLANET_CLASS.get(val, val)
            # A keyword must be bare or it never resolves; a name may be quoted.
            lines.append(f"{indent}{key} = {val}" if is_class_keyword(val)
                         else f'{indent}{key} = "{val}"')
        elif key == "name":
            lines.append(f'{indent}{key} = "{val}"')
        else:
            lines.append(f"{indent}{key} = {val}")
    return lines


def scalars(body: str, key: str) -> list[str]:
    """Every top-level `key = value` in `body`, in order — `ethic` and `trait`
    are repeated keys and `scalar` only ever returns the first."""
    flat = body
    for _ in range(8):
        nxt = re.sub(r"\{[^{}]*\}", " ", flat)
        if nxt == flat:
            break
        flat = nxt
    return re.findall(rf'\b{key}\s*=\s*"([^"]*)"', flat)


def ai_empire_block(stg_key: str, emp: dict, indent: str) -> str:
    """The `init_effect` that creates this empire's AI copy on its own capital.

    THIS IS THE MECHANISM A TREK GALAXY ACTUALLY RUNS ON, and it is neither the
    prescripted lottery nor anything to do with `CUSTOM_EMPIRE_SPAWN_CHANCE`.
    `prescripted_countries/` is the roster the PLAYER picks from; an AI Trek
    empire is *created* by its home system's initializer, which a static galaxy
    scenario puts on the map. Vanilla does exactly this for the United Nations
    of Earth in `com_sol_system`, and STNH does it 43 times.
    .docs/decisions/92-create-country-initializers.md.

    THE GUARD IS THE WHOLE DIFFERENCE BETWEEN ONE KLINGON EMPIRE AND TWO. When
    the player picks this empire, their country already carries the design key
    as a country flag — `src/common/prescripted_flags/stg_empire_flags.txt`,
    vanilla's `empire_human_2` pattern — so `any_country = { has_country_flag =
    <key> }` is already true and nothing is created. When nobody is playing it,
    nothing carries the flag and the AI copy is made here.

    Playable countries exist before the initializers run, which is what makes
    that guard answerable: vanilla's own `com_sol_system` decides its
    `usage_odds` by asking `any_playable_country = { … has_country_flag =
    human_2 … }` during galaxy generation.

    THE BODY IS VANILLA'S RECIPE, not STNH's. `create_country` then
    `create_colony`, deposits, blockers, start buildings and pops, leaders and
    `game_start.9` / `game_start.33` — the exact sequence `com_sol_system` uses
    for npc_UNoE, whose comment ("needs delay for system ownership to settle")
    is also the reason no `create_starbase` appears here: `create_colony`
    establishes the system.

    ONE LINE IS BORROWED FROM STNH RATHER THAN DERIVED FROM VANILLA and is
    labelled here because of it: `ideal_planet_class` inside `traits`. Vanilla
    gives a created species its habitability through a `trait_pc_*_preference`
    trait and STG's prescripted empires carry none — they declare
    `planet_class` instead, which `create_species` has no field for. STNH
    writes `ideal_planet_class` in 42 initializer files on this same 4.4.6, so
    the AI copy's preference matches its own homeworld the way the player's
    copy does. If a live run shows AI empires with the wrong habitability, this
    is the line that did not take.
    """
    body = emp["body"]
    sp = (sub_blocks(body, "species") or [""])[0]
    flag = (sub_blocks(body, "empire_flag") or [""])[0]
    icon = (sub_blocks(flag, "icon") or [""])[0]
    bg = (sub_blocks(flag, "background") or [""])[0]
    colors = (sub_blocks(flag, "colors") or [""])[0]

    civics = re.findall(r'"([^"]+)"', (sub_blocks(body, "civics") or [""])[0])
    ethics = scalars(body, "ethic")
    traits = scalars(sp, "trait")
    species_class = scalar(sp, "class") or ""
    tgt = stg_key.removeprefix("stg_")

    def ln(depth: int, text: str) -> str:
        return f"{indent}{'	' * depth}{text}"

    out = [ln(0, "init_effect = {"),
           ln(1, f"# The AI copy of {stg_key}, created only when no country is"),
           ln(1, "# already playing it. See ai_empire_block in the generator."),
           ln(1, "if = {"),
           ln(2, "limit = { NOT = { any_country = { has_country_flag = "
                 f"{stg_key} }} }} }}"),
           ln(2, "create_species = {"),
           ln(3, f'name = "{scalar(sp, "name")}"'),
           ln(3, f'plural = "{scalar(sp, "plural")}"'),
           ln(3, f'adjective = "{scalar(sp, "adjective")}"'),
           # Bare, as vanilla writes `class = EXD` and `class = MOL`. Quoting is
           # cosmetic on a species class -- but `check_references` reads every
           # quoted `class =` in this file as a PLANET class, so a quoted one
           # here would be reported as an undeclared planet class.
           ln(3, f"class = {species_class}"),
           ln(3, f'portrait = "{scalar(sp, "portrait")}"'),
           ln(3, "homeworld = THIS"),
           ln(3, f'namelist = "{scalar(sp, "name_list")}"'),
           ln(3, "traits = {")]
    out += [ln(4, f'trait = "{t}"') for t in traits]
    out += [ln(4, f'ideal_planet_class = "{emp["planet_class"]}"'),
            ln(3, "}"),
            ln(3, f"effect = {{ save_event_target_as = {tgt}_species }}"),
            ln(2, "}"),
            ln(2, "create_country = {"),
            ln(3, f'name = "{scalar(body, "name")}"'),
            ln(3, f'adjective = "{scalar(body, "adjective")}"'),
            ln(3, "type = default"),
            ln(3, f'authority = "{scalar(body, "authority")}"'),
            ln(3, "civics = { "
                  + " ".join(f'civic = "{c}"' for c in civics) + " }"),
            ln(3, "ethos = { "
                  + " ".join(f'ethic = "{e}"' for e in ethics) + " }"),
            ln(3, f'origin = "{scalar(body, "origin")}"'),
            ln(3, f"species = event_target:{tgt}_species"),
            ln(3, f'name_list = "{scalar(sp, "name_list")}"'),
            ln(3, f'ship_prefix = "{scalar(body, "ship_prefix")}"'),
            ln(3, "flag = {"),
            ln(4, f'icon = {{ category = "{scalar(icon, "category")}" '
                  f'file = "{scalar(icon, "file")}" }}'),
            ln(4, f'background = {{ category = "{scalar(bg, "category")}" '
                  f'file = "{scalar(bg, "file")}" }}'),
            ln(4, "colors = { "
                  + " ".join(f'"{c}"' for c in re.findall(r'"([^"]+)"', colors))
                  + " }"),
            ln(3, "}"),
            ln(3, "effect = {"),
            ln(4, f"save_event_target_as = {tgt}_country"),
            ln(4, f"set_graphical_culture = {scalar(body, 'graphical_culture')}"),
            ln(4, "set_city_graphical_culture = "
                  f"{scalar(body, 'city_graphical_culture')}"),
            ln(4, f"set_country_flag = {stg_key}"),
            ln(3, "}"),
            ln(2, "}"),
            ln(2, f"create_colony = {{ owner = event_target:{tgt}_country }}"),
            ln(2, "generate_start_deposits_and_blockers = yes"),
            ln(2, "clear_blockers = yes"),
            ln(2, "colony = {"),
            ln(3, "generate_start_buildings_and_districts = yes"),
            ln(3, "generate_start_pops = yes"),
            ln(2, "}"),
            ln(2, f"event_target:{tgt}_country = {{"),
            ln(3, "create_starting_leaders = yes"),
            ln(3, "country_event = { id = game_start.9 }"),
            # The delay is vanilla's, with vanilla's reason: system ownership
            # has to settle before game_start.33 reads it.
            ln(3, "country_event = { id = game_start.33 days = 1 }"),
            ln(2, "}"),
            ln(1, "}"),
            ln(0, "}")]
    return "\n".join(out)


def convert(stg_key: str, stnh_key: str, body: str, emp: dict,
            loc: dict[str, str]) -> str:
    sys_name = loc.get(emp["system_key"] or "", None)
    stnh_star = scalar(body, "class") or "sc_g"
    star = SYSTEM_STAR_CLASS.get(stg_key) or STAR_CLASS.get(stnh_star, stnh_star)

    out = [f"# {stg_key} — from STNH's {stnh_key}. Geometry theirs, mechanics vanilla's.",
           f"stg_{stg_key.removeprefix('stg_')}_home = {{}}".replace("{}", "{")]
    out.append(f'\tname = "{emp["system_key"]}"' if emp["system_key"]
               else f'\tname = "{sys_name or stnh_key}"')
    out.append(f'\tclass = "{star}"')
    out.append("\tusage = custom_empire")
    out.append("\tflags = { empire_home_system stg_home_system }")
    out.append("\tinit_effect = { generate_home_system_resources = yes }")
    out.append("")

    for belt in sub_blocks(body, "asteroid_belt"):
        t = scalar(belt, "type") or "rocky_asteroid_belt"
        t = ASTEROID_BELT.get(t, t)
        r = scalar(belt, "radius") or "100"
        out.append(f"\tasteroid_belt = {{ type = {t} radius = {r} }}")

    # The capital is not always a `planet`. Andoria is a MOON of the gas giant
    # Onlith, which is canon and which STNH models faithfully; so is Alrond.
    # A converter that only looked at planet blocks dropped both empires.
    started = False

    def emit(block: str, keyword: str, indent: str) -> None:
        nonlocal started
        is_start = (scalar(block, "starting_planet") == "yes") and not started
        out.append(f"{indent}{keyword} = {{")
        out.extend(ln for ln in convert_body(block, indent + "\t")
                   if not ln.strip().startswith("starting_planet"))
        if is_start:
            started = True
            out.append(f"{indent}\tstarting_planet = yes")
            out.append(f"{indent}\tdeposit_blockers = none")
            out.append(f"{indent}\tmodifiers = none")
            out.append(f"{indent}\tinit_effect = {{ prevent_anomaly = yes }}")
            # The effect that actually establishes the empire on this planet:
            # capital, pops, districts, and the home-system starbase that makes
            # the empire the system's owner. Without it the geometry spawns and
            # the empire does not own its own home system. Every vanilla
            # `usage = custom_empire` initializer carries it except
            # sol_system_initializer; deneb_system is our exact case -- a
            # prescripted empire on fixed geometry -- and it pairs this with
            # `starting_planet = yes` in a SECOND init_effect block, which is
            # why this is not merged into the one above.
            # See .docs/decisions/26-home-system-classes.md.
            out.append(f"{indent}\tinit_effect = "
                       f"{{ generate_empire_home_planet = yes }}")
            out.append(ai_empire_block(stg_key, emp, indent + "\t"))
        for mn in sub_blocks(block, "moon"):
            emit(mn, "moon", indent + "\t")
        out.append(f"{indent}}}")

    for pl in planets_flattened(body):
        emit(pl, "planet", "\t")

    out.append("}")
    text = "\n".join(out)

    # STNH names the primary star of the Andorian system "Andoria" -- and the
    # capital is Andoria too, the moon of Onlith, which is canon. Ours would
    # then show the same name twice on one map, because the empire's own
    # `planet_name` renames the capital and nothing renames the star. Vanilla's
    # convention settles it: Sol's star is called Sol, so a star that collides
    # with the capital takes the system's name instead.
    #
    # TWO THINGS WERE WRONG WITH DOING THAT BY SUBSTITUTION.
    #
    # A star is not always spelled `pc_<x>_star`. The lookahead named that form
    # only, and the commonest star this generator emits is the bare `star`
    # keyword -- CLASS_BUILTINS, filled by the engine from the system's class.
    # So the rule fired for Andoria, whose star carries an explicit pc_ class,
    # and silently missed Qo'noS, Cait, Romulus and Haakon.
    #
    # And substituting the system key only moves the collision when the system
    # and the capital are NAMED DIFFERENTLY. 23 STG empires render the same
    # string for both -- Bajor the system and Bajor the planet, which is Trek's
    # own convention and not a defect -- so pointing the star at the system key
    # renders the identical word and a player still reads "Qo'noS" twice.
    #
    # Vanilla settles it by omission rather than by choosing a name: 12 of the
    # 16 star bodies in its `usage = custom_empire` initializers carry NO name
    # at all, and the engine names the star from its system. The four it does
    # name are Sol, Deneb and the two stars of the Titawin binary. So drop the
    # colliding name and take vanilla's default; inventing a name for the
    # Klingon sun would be content, and this generator does not author content.
    capital = loc.get(emp["planet_key"] or "", None)
    if capital:
        text = re.sub(
            rf'[ \t]*\bname\s*=\s*"{re.escape(capital)}"\n'
            rf'(?=[^{{}}]*?class\s*=\s*(?:star\b|"?pc_[a-z]*_star))',
            "", text, count=1)

    for dup, replacements in SOURCE_NAME_FIXES.get(stg_key, {}).items():
        seen = 0

        def renumber(m: re.Match, _r=replacements) -> str:
            nonlocal seen
            new = _r[seen] if seen < len(_r) else m.group(2)
            seen += 1
            return f'{m.group(1)}"{new}"'

        text = re.sub(rf'(\bname\s*=\s*)"({re.escape(dup)})"', renumber, text)
    return text, started


def main() -> int:
    loc = load_loc()
    empires = load_empires()
    stnh = load_stnh()
    by_name = {}
    for k, b in stnh.items():
        n = scalar(b, "name")
        if n:
            by_name.setdefault(n, k)

    chunks, placed, unplaced, nostart = [], {}, [], []
    for stg_key, emp in sorted(empires.items()):
        if stg_key in SKIP:
            placed[stg_key] = SKIP[stg_key]
            continue
        if stg_key in AUTHORED:
            key = f"stg_{stg_key.removeprefix('stg_')}_home"
            cap = (CAPITAL.replace("@PLANET@", emp["planet_key"] or "")
                          .replace("@CLASS@", emp["planet_class"] or "pc_continental")
                          .replace("@AI_EMPIRE@",
                                   ai_empire_block(stg_key, emp, "\t\t")))
            body = AUTHORED[stg_key].replace("\t@CAPITAL@", cap)
            chunks.append(
                f"# {stg_key} — authored: STNH's own home system is procedural.\n"
                f"{key} = {{\n{body}"
                f"\tusage = custom_empire\n"
                f"\tflags = {{ empire_home_system stg_home_system }}\n"
                f"\tinit_effect = {{ generate_home_system_resources = yes }}\n"
                f"}}")
            placed[stg_key] = key
            continue
        sys_name = loc.get(emp["system_key"] or "", "")
        cand = ALIASES.get(stg_key) or by_name.get(sys_name)
        if not cand:
            base = stg_key.removeprefix("stg_").removeprefix("minor_")
            for tok in base.split("_"):
                for stem in (tok, tok.rstrip("s"), tok + "n", tok + "an", tok + "ian"):
                    for suf in ("_homeworld", "_initializer", "_homeworld_01"):
                        if stem + suf in stnh:
                            cand = stem + suf
                            break
                    if cand:
                        break
                if cand:
                    break
        if not cand:
            unplaced.append((stg_key, sys_name))
            continue
        text, started = convert(stg_key, cand, stnh[cand], emp, loc)
        if not started:
            nostart.append((stg_key, cand))
            continue
        chunks.append(text)
        placed[stg_key] = f"stg_{stg_key.removeprefix('stg_')}_home"

    header = f'''\
# GENERATED by tools/gen_home_systems.py — do not hand-edit; regenerate.
#
# A real home system for every STG prescripted empire that has one, converted
# from STNH's own (decision 19's pattern: their identity, vanilla's mechanics).
# STNH's init_effect scripting is dropped wholesale — it sets STNH country
# flags and event targets we do not vendor — and its Trek planet and star
# classes are mapped onto vanilla's. Every class emitted here is checked to
# resolve before this file is written: an unmapped one crashes the game at
# startup and logs nothing (.docs/decisions/26-home-system-classes.md).
# See .docs/decisions/25-real-home-systems.md.
#
# The Federation is not here: it uses vanilla's own sol_system_initializer,
# which Real Space rescales, and which is already the real solar system. That
# also means the Federation has no AI copy — the block below is what creates one
# and there is nowhere to put it (.docs/decisions/93-static-galaxy-scenario.md).
#
# EACH CAPITAL CARRIES A GUARDED create_country. It creates this empire's AI
# copy, and only when no country already carries the empire's own design key as
# a country flag — which the player's copy does, from
# common/prescripted_flags/. That is the mechanism a Trek galaxy runs on; the
# prescripted pool is the player's roster and places nobody
# (.docs/decisions/92-create-country-initializers.md).
#
# {len(chunks)} systems generated, {len(unplaced)} empires left on generated systems.

'''
    body = header + "\n\n".join(chunks) + "\n"

    # Refuse to write a file that names a class nothing declares. The engine
    # does not survive one: it crashes initialising CSystemInitializerDataBase,
    # before error.log gets a line.
    if bad := check_references(body):
        print("ERROR: generated initializers reference things the merged tree "
              "does not declare:", file=sys.stderr)
        for name in bad:
            print(f"    {name}", file=sys.stderr)
        print("\nEach needs an entry in PLANET_CLASS, STAR_CLASS, ASTEROID_BELT "
              "or SYSTEM_STAR_CLASS. Nothing written.", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(body, encoding="utf-8")

    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"  {len(chunks)} initializers generated")
    print(f"  {len(placed)} empires placed, {len(unplaced)} without an STNH system")
    if nostart:
        print(f"  {len(nostart)} skipped: STNH block has no starting_planet")
        for k, c in nostart:
            print(f"      {k:52} {c}")
    if unplaced:
        print("  no STNH home system found for:")
        for k, n in unplaced:
            print(f"      {k:52} {n}")

    # The wiring half is a report, not an edit: prescripted_countries/ is
    # hand-written src/, so the initializer lines are added there deliberately.
    (REPO / ".vendor-cache").mkdir(exist_ok=True)
    (REPO / ".vendor-cache/home_systems_map.txt").write_text(
        "\n".join(f"{k}\t{v}" for k, v in sorted(placed.items())) + "\n",
        encoding="utf-8")
    print(f"  map for wiring: .vendor-cache/home_systems_map.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
