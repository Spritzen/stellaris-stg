#!/usr/bin/env python3
"""Rewrite the `ship_class_names` pools in src/common/name_lists/ from STNH's.

Phase 4, and the other half of decision 56. That decision folded STNH's ship
REGISTRIES onto vanilla's ship sizes and left the CLASS name -- the "Nebula" in
"Nebula -- Interceptor" -- open, because the obvious source did not work: STNH's
`TECH_UNLOCK_*_TITLE` strings carry real class names under a key scheme that
matches no pool key, 0 of 192 by direct lookup. It recorded a fuzzy join off the
hull key's own suffix as the next step.

THE FUZZY JOIN IS NOT NEEDED, AND THAT IS THE FINDING. STNH's name lists carry
their own `ship_class_names` block, keyed by the same hull vocabulary as
`ship_names` and holding one loc token per hull:

    fed_heavy_cruiser_nebula = { HUMAN_CLASS_Nebula }     -> "Nebula"
    kdf_battlecruiser_vorcha = { KLINGON_CLASS_Vorcha }   -> "Vor'cha"

57 of STNH's 169 lists have one, and between them they declare 165 of the 177
Trek hull keys any registry uses. The 12 left are swarm hulls and vanilla's own
starbase tiers -- `starbase_citadel`, `starbase_outpost` -- which name a station
tier rather than a class. So the suffix never has to be guessed at, and the
spellings a suffix loses (`t_pol` is T'Pol, `kiri_kin_tha` is Kiri-kin-tha,
`ktinga` is K't'inga) are simply read off the value. A join was built first and
deleted: across the 90 STNH lists STG maps to it had 594 candidates and every
one was SHARED HULL VOCABULARY rather than a class -- see SPELLINGS below.

Reads .source/, never the built tree -- the same rule as the other one-shots.
The tonnage table, the STNH-list mapping and the key alphabet all come from
gen_ship_names.py rather than being restated: one tonnage judgement, in one
place, or the two halves of a ship's name drift apart.

    python3 tools/gen_ship_class_names.py [--dry-run]

See .docs/decisions/67-ship-class-names.md
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from collections import Counter
from pathlib import Path

from gen_ship_names import (
    LISTS, LOC_EXISTING, ORDER, REPO, STNH, TOKEN_RE, TONNAGE,
    block, close_of, die, read, stg_key, stg_sources, stnh_loc,
)

LOC_OUT = REPO / "src" / "localisation" / "english" / "stg_ship_class_names_l_english.yml"
LOC_SHIPS = REPO / "src" / "localisation" / "english" / "stg_ship_names_l_english.yml"

# ── the four lists decision 56 takes NO registries from ───────────────────────
#
# It leaves `bolian`, `breen`, `bajoran` and `andorian` on their hand-written
# pools because those STNH lists key their registries by FEDERATION hulls --
# taking them would put Starfleet registries in a Bajoran fleet. That is right
# for `ship_names` and WRONG HERE, and inheriting it cost real content: three of
# the four declare class names of their own for the SHARED hulls, and they are
# the genuine article -- Bajor's Perikian, Ornathia and Denorios, the Breen's
# Plesh Brek and Sarr Thenn, Andoria's Kumari, Charal and Khyzon.
#
# So the registries stay excluded and the class names come across, filtered.
CLASS_ONLY = {
    "andorian": ["Andorian"],
    "bajoran": ["Bajoran"],
    "bolian": ["Bolian"],          # declares no ship_class_names; here for the record
    "breen": ["Breen"],
}

# What the filter has to catch. A shared hull is named for its tier
# (`saber`, `adv_cruiser`, `military_station_small`); an empire's own hull names
# the empire somewhere in the key, and NOT ALWAYS AS THE PREFIX -- Andorian.txt
# declares `military_defense_fed_2 = { ANDORIAN_CLASS_Danube }`, which is a
# Federation runabout wearing an Andorian key. Matching on the prefix alone
# would have let three Starfleet classes into the Andorian Empire.
EMPIRE_TOKENS = {"fed", "kdf", "rom", "dom", "car", "cardassian", "klingon",
                 "borg", "undine", "xindi", "nor", "civ"}


def shape(s: str) -> str:
    """A string reduced to what two spellings of one class have in common:
    casefolded, accents dropped, letters and digits only. `B'Rel` and `B'rel`
    are one shape; so are `Kiri-kin-tha` and `KiriKinTha`."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def usable(value: str | None) -> bool:
    """Decision 45's rule, as gen_ship_names applies it: a value that is still a
    loc key, or that carries markup or a substitution, is not a name."""
    if not value or not value.strip():
        return False
    return not (re.fullmatch(r"[A-Z][A-Z0-9_]{3,}", value)
                or "§" in value or "$" in value or "[" in value)


def pools_of(name: str, key: str) -> dict[str, list[str]]:
    """One STNH list's `ship_names` or `ship_class_names`: hull key -> tokens."""
    f = STNH / "common" / "name_lists" / f"{name}.txt"
    if not f.is_file():
        die(f"{f} missing -- run `make sources-sync ID=688086068`")
    s = read(f)
    span = block(s, key)
    if span is None:
        return {}
    body = s[span[0]:span[1]]
    out: dict[str, list[str]] = {}
    for m in re.finditer(r"(?m)^[ \t]*(\w+)[ \t]*=[ \t]*\{", body):
        pre = body[:m.start()]
        if pre.count("{") != pre.count("}"):
            continue
        end = close_of(body, m.end()) - 1
        out.setdefault(m.group(1), []).extend(
            re.findall(r"[A-Za-z_][\w.'-]*", body[m.end():end]))
    return out


def tonnage_of(hull: str, where: str) -> str:
    want = next((v for k, v in TONNAGE if k in hull), None)
    if want is None:
        die(f"{where}: no tonnage rule for ship_class_names key {hull!r}. "
            f"Add one to TONNAGE in tools/gen_ship_names.py -- a key with no "
            f"rule is a whole class list silently dropped.")
    return want


def spellings(loc: dict[str, str]) -> dict[str, str]:
    """shape -> the one spelling STNH uses for it, over its `*_CLASS_*` keys.

    THIS IS ALL THAT SURVIVES OF THE FUZZY JOIN, and it points inward rather
    than outward: it does not invent a class name for a hull, it makes STNH
    agree with itself. `KLINGON_CLASS_BRel` is "B'Rel" and `KLINGON_CLASS_Brel`
    is "B'rel" -- one class, two capitalisations, and stg_key keeps case, so
    untouched they are two loc keys and two entries in the same fleet's pools.

    The disagreements are tiny and entirely case: B'Rel/B'rel, Jej'ha/JejHa',
    Defiant/`Defiant `. Broken by how often STNH writes each spelling, then
    alphabetically, so the answer never depends on file order.
    """
    counts: dict[str, Counter] = {}
    for k, v in loc.items():
        if "_CLASS_" not in k:
            continue
        v = v.strip()
        if not usable(v) or len(v) > 40:
            continue
        counts.setdefault(shape(v), Counter())[v] += 1
    return {sh: max(sorted(c), key=lambda v: (c[v], v))
            for sh, c in counts.items() if sh}


def known_keys() -> dict[str, str]:
    """Every STG_N_ key already spelled, across BOTH the hand-written names and
    decision 56's harvest. One flat namespace, so a class name that is also a
    ship name is one key -- and the existing spelling is the deliberate one."""
    out: dict[str, str] = {}
    for p in (LOC_EXISTING, LOC_SHIPS):
        if not p.is_file():
            continue
        for line in read(p).split("\n"):
            m = re.match(r'\s*(STG_N_[^\s:]+):\d*\s+"(.*)"\s*$', line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def render(pools: dict[str, list[str]]) -> str:
    lost = [k for k in pools if k not in ORDER]
    if lost:
        die(f"ship_class_names key(s) {lost} are not in ORDER and would be dropped")
    out = []
    for key in ORDER:
        toks = pools.get(key)
        if not toks:
            continue
        out.append(f"\t\t{key} = {{\n")
        line: list[str] = []
        for t in toks:
            line.append(t)
            if len(line) == 6:
                out.append("\t\t\t" + " ".join(line) + "\n")
                line = []
        if line:
            out.append("\t\t\t" + " ".join(line) + "\n")
        out.append("\t\t}\n\n")
    return "".join(out).rstrip("\n") + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    loc = stnh_loc()
    canon = spellings(loc)
    have = known_keys()
    new_loc: dict[str, str] = {}
    stats: Counter = Counter()

    for f in sorted(LISTS.glob("stg_*.txt")):
        stem = f.stem[len("stg_"):]
        srcs = stg_sources(stem)
        if not srcs and stem not in CLASS_ONLY:
            stats["no STNH source"] += 1
            continue

        harvested: dict[str, list[str]] = {}
        for s, shared_only in [(x, False) for x in srcs] + \
                              [(x, True) for x in CLASS_ONLY.get(stem, [])]:
            for hull, toks in pools_of(s, "ship_class_names").items():
                if shared_only and set(hull.split("_")) & EMPIRE_TOKENS:
                    stats["another empire's hull, skipped"] += 1
                    continue
                want = tonnage_of(hull, f"{s}.txt")
                for t in toks:
                    v = loc.get(t)
                    if not usable(v):
                        stats["STNH token with no usable value"] += 1
                        continue
                    harvested.setdefault(want, []).append(
                        canon.get(shape(v.strip()), v.strip()))
                    stats["harvested"] += 1

        text = read(f)
        span = block(text, "ship_class_names")
        if span is None:
            die(f"{f.name} has no ship_class_names block")
        current = text[span[0]:span[1]]

        # STG's hand-written class names stay -- the same UNION rule decision 56
        # sets for the registries -- and stay first in their pool.
        pools: dict[str, list[str]] = {}
        for m in re.finditer(r"(?m)^[ \t]*(\w+)[ \t]*=[ \t]*\{", current):
            pre = current[:m.start()]
            if pre.count("{") != pre.count("}"):
                continue
            end = close_of(current, m.end()) - 1
            raw = current[m.end():end].split()
            keep = [t for t in raw if TOKEN_RE.match(t)]
            stats["unusable token(s) dropped"] += len(raw) - len(keep)
            pools[m.group(1)] = keep

        added = 0
        for key, values in harvested.items():
            seen = set(pools.get(key, []))
            for value in values:
                k = stg_key(value)
                prior = have.get(k, new_loc.get(k))
                if prior is not None and prior != value:
                    stats["kept the existing spelling"] += 1
                elif k not in have:
                    new_loc[k] = value
                if k not in seen:
                    seen.add(k)
                    pools.setdefault(key, []).append(k)
                    added += 1

        # A NAME IN `generic` IS DRAWN AT ANY TONNAGE. Vanilla's own
        # README_NAME_LISTS.txt: "If both generic and size-specific names exist,
        # 50% chance of using either list." So a class name that now HAS a size
        # would still land on a corvette half the time if it also stayed in
        # generic -- which is the defect this file exists to fix. A generic
        # token some size pool now claims is DEMOTED out of generic; one no size
        # claims stays, because generic is the only place it can be drawn from.
        #
        # Matched BY SHAPE, not by token, because the two halves spell a class
        # differently often enough to matter: STG wrote `STG_N_DDeridex` by hand
        # and STNH declares `D'deridex`, so an exact match leaves the Romulan
        # warbird in generic AND in battleship and the defect survives its own
        # fix. Same rule that makes one class one key above.
        sized = {shape(t) for k, v in pools.items() if k != "generic" for t in v}
        if sized and pools.get("generic"):
            before = len(pools["generic"])
            pools["generic"] = [t for t in pools["generic"] if shape(t) not in sized]
            stats["demoted"] += before - len(pools["generic"])
            stats["stayed generic"] += len(pools["generic"])
            if not pools["generic"]:
                del pools["generic"]

        stats["lists rewritten"] += 1
        stats["class names added"] += added
        text = text[:span[0]] + "\n" + render(pools) + "\t" + text[span[1]:]
        if not args.dry_run:
            f.write_text(text, encoding="utf-8-sig")

    if not args.dry_run and new_loc:
        head = (
            "l_english:\n"
            " # Star Trek Galaxies -- ship CLASS names harvested from STNH.\n"
            " #\n"
            " # GENERATED by tools/gen_ship_class_names.py, alongside the\n"
            " # ship_class_names pools in src/common/name_lists/. Same flat\n"
            " # STG_N_ namespace as stg_names_l_english.yml (hand-written) and\n"
            " # stg_ship_names_l_english.yml (the registries); a name already\n"
            " # spelled in either is not repeated here.\n"
            " #\n"
            " # See .docs/decisions/67-ship-class-names.md\n")
        LOC_OUT.write_text(
            head + "".join(f' {k}:0 "{new_loc[k]}"\n' for k in sorted(new_loc)),
            encoding="utf-8-sig")

    print(f"  {LISTS.relative_to(REPO)}/  {stats['lists rewritten']} list(s) "
          f"rewritten, {stats['no STNH source']} left on their own pools")
    print(f"  {LOC_OUT.relative_to(REPO)}  {len(new_loc)} new class key(s)")
    print(f"    +{stats['class names added']} class token(s) across the pools, "
          f"from {stats['harvested']} STNH declaration(s)")
    print(f"    {stats['demoted']} generic token(s) demoted to a size, "
          f"{stats['stayed generic']} left in generic")
    if stats["STNH token with no usable value"]:
        print(f"    {stats['STNH token with no usable value']} STNH token(s) "
              f"skipped for having no usable english value")
    if stats["kept the existing spelling"]:
        print(f"    {stats['kept the existing spelling']} kept an existing "
              f"STG spelling")


if __name__ == "__main__":
    main()
