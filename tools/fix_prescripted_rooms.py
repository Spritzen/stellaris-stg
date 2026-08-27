#!/usr/bin/env python3
"""One-shot: rewrite `room =` in src/prescripted_countries/stg_*.txt from the
assignment STNH's own prescripted files make.

STG's 101 empires were converted from STNH's, but their `room =`
values were not: 99 of 101 carried a vanilla `personality_*` room, and the 20
empires STNH gives a Trek room lost it. Same class of defect as decision 45 --
a converted field that no longer says what the source says, reported by nothing
because a room that resolves to the wrong picture still resolves.

Run from the repo root. Idempotent. Reads .source/, never the built tree.
"""
import re
import sys
from pathlib import Path

STNH = Path(".source/688086068/prescripted_countries")
OURS = Path("src/prescripted_countries")

# STG key -> STNH key, for the empires a CamelCase-to-snake_case fold does not
# match. Renames STG made deliberately: the founder species' own state (Vulcan
# High Command -> Confederacy of Vulcan) or the era (UnitedEarth -> UFP).
ALIASES = {
    "stg_united_federation_of_planets": "tngUnitedFederationofPlanets",
    "stg_confederacy_of_vulcan": "VulcanHighCommand",
    "stg_dominion": "TheDominion",
    "stg_bolian_union": "BolianLeague",
    "stg_trill_symbiosis": "TrillRepublic",
    "stg_caitian_empire": "CaitianUnion",
    "stg_xindi_empire": "XindiCouncil",
    "stg_suliban_empire": "SulibanCabal",
    "stg_yridian_empire": "YridianLeague",
    "stg_krenim_empire": "KrenimImperium",
    "stg_malon_empire": "MalonSanctity",
    "stg_vidiian_empire": "VidiianSodality",
    "stg_terran_empire": "tngTerranEmpire",
}

# Where STG keeps its own answer instead of STNH's, and why. These are the only
# three; everything else is the source's value verbatim.
OVERRIDES = {
    # STNH's prescripted file says personality_ruthless_capitalists_room, but its
    # own room_selector maps the `trill_symbiosis_commission` country to
    # trillsym_room, and STG's empire is the Symbiosis rather than the Republic.
    "stg_trill_symbiosis": "trillsym_room",
    # STNH says personality_hive_mind_room and ships no Tholian room. THO is
    # LITHOID in STG (crystalline, .docs/planning/phases.md Phase 2), and lithoid_room is
    # vanilla's answer for that archetype.
    "stg_tholian_assembly": "lithoid_room",
    # STNH says borg_room for the Collective and STG had machine_room -- keep
    # the Trek art. Listed here because it is the one row where STG was WRONG
    # and the source right, so a future reader does not read it as a divergence.
    "stg_borg_collective": "borg_room",
}


def blocks(text):
    """(key, start, end) for every depth-0 `key = { ... }`."""
    for m in re.finditer(r"^(\w+) = \{", text, re.M):
        i, depth = m.end(), 1
        while depth and i < len(text):
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        yield m.group(1), m.end(), i - 1


def fold(camel):
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", camel)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", s)
    return s.lower()


def source_rooms():
    if not STNH.is_dir():
        sys.exit(f"fix_prescripted_rooms: {STNH} missing -- make sources-sync ID=688086068")
    out = {}
    for f in sorted(STNH.glob("STH_*.txt")):
        t = f.read_text(errors="replace")
        for key, a, b in blocks(t):
            m = re.search(r'room = "([^"]+)"', t[a:b])
            if m:
                out[key] = m.group(1)
                out[fold(key)] = m.group(1)
    return out


def main():
    src = source_rooms()
    rows, missing = [], []
    for f in sorted(OURS.glob("stg_*.txt")):
        t = f.read_text(encoding="utf-8")
        edits = []
        for key, a, b in blocks(t):
            m = re.search(r'(\n\troom = ")([^"]+)(")', t[a:b])
            if not m:
                continue
            want = OVERRIDES.get(key)
            how = "STG"
            if want is None:
                stnh = ALIASES.get(key) or key.replace("stg_minor_", "").replace("stg_", "")
                want = src.get(stnh) or src.get(fold(stnh))
                how = "STNH"
            if want is None:
                missing.append((f.name, key, m.group(2)))
                continue
            rows.append((key, m.group(2), want, how))
            if want != m.group(2):
                edits.append((a + m.start(2), a + m.end(2), want))
        for start, end, want in sorted(edits, reverse=True):
            t = t[:start] + want + t[end:]
        if edits:
            f.write_text(t, encoding="utf-8")
            print(f"  {f}: {len(edits)} room(s) rewritten")

    changed = [r for r in rows if r[1] != r[2]]
    print(f"\n{len(rows)} empire(s) matched, {len(changed)} changed, {len(missing)} unmatched")
    for key, was, now, how in changed:
        print(f"  {key:46} {was:44} -> {now:36} [{how}]")
    for name, key, was in missing:
        print(f"  UNMATCHED  {key:46} keeps {was}  ({name})")


if __name__ == "__main__":
    main()
