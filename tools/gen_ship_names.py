#!/usr/bin/env python3
"""Rewrite the `ship_names` pools in src/common/name_lists/ from STNH's.

Phase 4. Reported from the 2026-08-08 live run: the ship name pools per class
did not come across from STNH. They did not -- STG's 92 lists were hand-written
from scratch, 6,093 tokens in total, a median of 62 per list against vanilla's
own median of 116. STNH ships 38,707, and they are the real Starfleet, Klingon
and Romulan registries.

WHY THEY COULD NOT BE COPIED, which is the whole problem this file solves.
STNH replaced vanilla's ship sizes with its own single-slot hull ladder, so its
pools are keyed by HULL: `fed_heavy_cruiser_nebula` (96 names),
`fed_heavy_escort_defiant` (91), `kdf_battlecruiser_vorcha` (119). STG flies a
vanilla chassis (decision 17), so none of those keys exists here and every one
of them would be read as a pool the engine never asks for. They have to be
FOLDED onto vanilla's corvette / destroyer / cruiser / battleship / titan by
tonnage, which is a judgement, so the table is written out below and every one
of STNH's 206 distinct keys must match a rule or this script stops.

Reads .source/, never the built tree -- the same rule as the other one-shots.

    python3 tools/gen_ship_names.py [--dry-run]

See .docs/decisions/56-ship-name-pools.md
"""
from __future__ import annotations

import argparse
import re
import unicodedata
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STNH = REPO / ".source" / "688086068"
LISTS = REPO / "src" / "common" / "name_lists"
LOC_OUT = REPO / "src" / "localisation" / "english" / "stg_ship_names_l_english.yml"
LOC_EXISTING = REPO / "src" / "localisation" / "english" / "stg_names_l_english.yml"


def die(msg: str) -> None:
    print(f"error {msg}", file=sys.stderr)
    raise SystemExit(1)


# ── the tonnage table ────────────────────────────────────────────────────────
#
# STNH hull vocabulary -> the vanilla `ship_names` key that hull's registry
# belongs in. Matched as a substring of the pool key, longest rule first, so
# `fed_adv_heavy_cruiser_inquiry` takes the `adv_heavy_cruiser` rule rather
# than the `heavy_cruiser` one.
#
# The tiers are STNH's own, read off its ship_sizes: a bird-of-prey and a
# frigate are what a corvette is for, a light cruiser is a destroyer, a heavy
# cruiser or battlecruiser is a cruiser, an exploration or advanced cruiser is
# a battleship, and the one-off flagships are titans. Vanilla's own key names
# (generic, science, constructor, colonizer, transport, the stations) STNH uses
# unchanged, so they pass through.
#
# `civ_raven` is STNH's civilian runabout and `*_shuttle_*` its smallest hull;
# both are corvette-sized. `military_defense_*` are STNH's defence platforms,
# which vanilla splits by starbase tier -- they go to the small station pool,
# the only one every vanilla name list defines.
TONNAGE: list[tuple[str, str]] = [
    # ── pass-through: STNH already uses vanilla's key ──
    ("generic", "generic"),
    ("science", "science"),
    ("constructor", "constructor"),
    ("construction_ship", "constructor"),
    ("colonizer", "colonizer"),
    ("colony_ship", "colonizer"),
    ("sponsored_colonizer", "sponsored_colonizer"),
    ("transport", "transport"),
    ("research_station", "research_station"),
    ("observation_station", "observation_station"),
    ("mining_station", "mining_station"),
    ("military_station_small", "military_station_small"),
    ("military_station_medium", "military_station_medium"),
    ("military_station_large", "military_station_large"),
    ("ion_cannon", "ion_cannon"),
    ("colossus", "colossus"),
    ("juggernaut", "juggernaut"),
    ("titan", "titan"),
    ("corvette", "corvette"),
    ("destroyer", "destroyer"),
    ("battleship", "battleship"),

    # ── stations and defences ──
    ("military_defense", "military_station_small"),
    ("orbital_cannon", "ion_cannon"),
    ("deep_space_starbase", "military_station_large"),
    ("starbase", "military_station_large"),
    ("nor_starbase", "military_station_large"),
    ("naval_museum", "military_station_small"),

    # ── titan: the one-off flagships ──
    ("hero_ship", "titan"),
    ("flagship", "titan"),
    ("mobile_throne", "titan"),
    ("mobile_carrier", "titan"),
    ("sword", "titan"),
    ("queen", "titan"),
    ("dreadnought", "titan"),

    # ── battleship: the capital cruisers ──
    ("adv_heavy_cruiser", "battleship"),
    ("advanced_cruiser", "battleship"),
    ("exploration_cruiser", "battleship"),
    ("command_cruiser", "battleship"),
    ("super_battleship", "battleship"),
    ("adv_cruiser", "battleship"),
    ("starbird", "battleship"),
    ("warship", "battleship"),

    # ── cruiser ──
    ("heavy_cruiser", "cruiser"),
    ("heavy_escort", "cruiser"),
    ("battlecruiser", "cruiser"),
    ("warbird", "cruiser"),
    ("carrier", "cruiser"),
    ("mmv", "cruiser"),
    ("sovereign", "cruiser"),
    ("cruiser", "cruiser"),

    # ── destroyer ──
    ("light_cruiser", "destroyer"),
    ("explorer", "destroyer"),
    ("steamrunner", "destroyer"),
    ("saber", "destroyer"),
    ("escort", "destroyer"),
    ("raptor", "destroyer"),

    # ── corvette ──
    ("frigate", "corvette"),
    ("gunboat", "corvette"),
    ("bop", "corvette"),
    ("raider", "corvette"),
    ("interceptor", "corvette"),
    ("scout", "corvette"),
    ("runabout", "corvette"),
    ("shuttle", "corvette"),
    ("attack_wing", "corvette"),
    ("attack_ship", "corvette"),
    ("strike_ship", "corvette"),
    ("strike", "corvette"),
    ("stealth", "corvette"),
    ("civ_", "corvette"),
    ("small_ship", "corvette"),
    ("large_ship", "cruiser"),

    # ── the hulls only ship_class_names names ──
    #
    # `ship_class_names` is keyed by the same hull vocabulary but reaches 19
    # hulls no registry pool does -- the Borg, the Undine, the fallen empires,
    # the Xindi planet killer, Annorax. They are placed by VANILLA'S OWN
    # fleet_slot_size ladder (corvette 1, destroyer 2, cruiser 3, battleship 4,
    # titan 8, juggernaut and colossus 32) read against STNH's value for each
    # hull, which is the comment on every line. Nothing here is a guess about
    # what a cube "feels like".
    ("borg_probe", "corvette"),                             # fleet 1
    ("borg_unimatrix_defense", "military_station_small"),   # fleet 2, a station
    ("cardassian_cannon", "military_station_small"),        # fleet 2, a station
    ("borg_pyramid", "battleship"),                         # fleet 4
    ("borg_sphere", "battleship"),                          # fleet 4
    ("fallen_attack", "battleship"),                        # fleet 4
    ("fallen_interdictor", "battleship"),                   # fleet 4
    ("undine_01_bio_ship", "battleship"),                   # fleet 4
    ("borg_diamond", "titan"),                              # fleet 8
    ("fallen_assault", "titan"),                            # fleet 8
    ("cardassian_01_weapons_platform", "titan"),            # fleet 16
    ("undine_01_bio_infester", "titan"),                    # fleet 16
    ("xindi_planet_killer", "titan"),                       # fleet 16
    ("borg_cube", "juggernaut"),                            # fleet 32
    ("borg_tactical", "juggernaut"),                        # fleet 32
    ("super_cube", "juggernaut"),                           # fleet 32
    ("time_ship_annorax", "juggernaut"),                    # fleet 32
    ("undine_01_bio_behemoth", "juggernaut"),               # fleet 32
    ("undine_01_bio_vanquisher", "juggernaut"),             # fleet 32
]
TONNAGE.sort(key=lambda r: -len(r[0]))

# ── which STNH list feeds which STG list ─────────────────────────────────────
#
# Almost all of it is the file stem: stg_klingon -> Klingon, stg_minor_pakled
# -> Pakled. These are the ones where it is not, and each is a content call
# rather than a spelling one.
EXPLICIT = {
    "federation": ["Human", "HUMAN2"],   # the UFP is human-led; both registries
    "terran": ["Terran"],                # the mirror Terran Empire, ENT era
    "dominion": ["Founder", "JemHadar", "Vorta"],
    "minor_confederation": ["Confederation"],
    "minor_mam1": ["MAM1"], "minor_mam2": ["MAM2"], "minor_mam3": ["MAM3"],
    "minor_klingon": ["Klingon_Houses", "Klingon"],
    "minor_vulcan": ["Vulcan"],
    "trill": ["Trill", "Trill_Symbiont"],
    # No STNH list of its own; these fly Federation or Klingon registries in
    # STNH's own map, and taking a neighbour's list would put another power's
    # ship names in their fleet. Left on STG's hand-written pools.
    "bolian": [], "breen": [], "bajoran": [], "andorian": [],
}

# ── script ───────────────────────────────────────────────────────────────────

def stg_key(name: str) -> str:
    """A name -> its STG_N_ key, in the convention stg_names_l_english.yml sets:
    spaces, apostrophes and full stops removed, hyphens kept.

    AND ASCII-FOLDED, which the hand-written names never needed. A key is a
    TOKEN in the name list, and the engine's token alphabet is the one vanilla
    writes: `[A-Za-z][A-Za-z_0-9-]*`. STNH's registries carry Hammarskjöld,
    Auñón-Chancellor and `Temba, at rest`, and a key spelling any of those
    verbatim ends the token early -- STG_N_Hammarskj, then `ld` as a second
    token, both of which resolve to nothing and draw as themselves. The value
    keeps every character; only the key is folded.
    """
    folded = unicodedata.normalize("NFKD", name)
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    folded = re.sub(r"[^A-Za-z0-9-]", "", folded)
    return "STG_N_" + folded


def read(p: Path) -> str:
    return p.read_text("utf-8-sig", errors="replace").replace("\r\n", "\n")


def close_of(s: str, i: int) -> int:
    """Index just past the `}` closing the block whose `{` was at i-1."""
    d = 1
    while d:
        if s[i] == "{":
            d += 1
        elif s[i] == "}":
            d -= 1
        i += 1
    return i


def block(s: str, key: str, depth_any: bool = True):
    """(start, end) of the body of `key = { ... }`, or None."""
    m = re.search(r"(?m)^[ \t]*" + re.escape(key) + r"[ \t]*=[ \t]*\{", s)
    if not m:
        return None
    end = close_of(s, m.end())
    return m.end(), end - 1


def stnh_pools(name: str) -> dict[str, list[str]]:
    """STNH's `ship_names` for one list: vanilla key -> its loc keys."""
    f = STNH / "common" / "name_lists" / f"{name}.txt"
    if not f.is_file():
        die(f"{f} missing -- run `make sources-sync ID=688086068`")
    s = read(f)
    span = block(s, "ship_names")
    if span is None:
        return {}
    body = s[span[0]:span[1]]
    out: dict[str, list[str]] = {}
    for m in re.finditer(r"(?m)^[ \t]*(\w+)[ \t]*=[ \t]*\{", body):
        pre = body[:m.start()]
        if pre.count("{") != pre.count("}"):
            continue
        end = close_of(body, m.end()) - 1
        toks = re.findall(r"[A-Za-z_][\w.'-]*", body[m.end():end])
        key = m.group(1)
        want = next((v for k, v in TONNAGE if k in key), None)
        if want is None:
            die(f"{name}.txt: no tonnage rule for ship_names key {key!r}. "
                f"Add one to TONNAGE in tools/gen_ship_names.py -- a key with "
                f"no rule is a whole registry silently dropped.")
        out.setdefault(want, []).extend(toks)
    return out


def stnh_loc() -> dict[str, str]:
    """STNH's english localisation, key -> value."""
    d = STNH / "localisation" / "english"
    if not d.is_dir():
        die(f"{d} missing -- run `make sources-sync ID=688086068`")
    out: dict[str, str] = {}
    for f in sorted(d.glob("*.yml")):
        for line in read(f).split("\n"):
            m = re.match(r'\s*([A-Za-z_][\w.\'-]*):\d*\s+"(.*)"\s*$', line)
            if m:
                out.setdefault(m.group(1), m.group(2))
    if len(out) < 10000:
        die(f"only parsed {len(out)} STNH loc keys -- the files changed shape")
    return out


def existing_loc() -> dict[str, str]:
    """The HAND-WRITTEN names only. LOC_OUT is regenerated from scratch every
    run, so reading it back would make a bad key from a previous run immortal:
    it would be in `have`, so it would never be rewritten, and it would still
    be a token in the pool."""
    out: dict[str, str] = {}
    if LOC_EXISTING.is_file():
        for line in read(LOC_EXISTING).split("\n"):
            m = re.match(r'\s*(STG_N_[^\s:]+):\d*\s+"(.*)"\s*$', line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


# The engine's name-list token alphabet, as vanilla writes it. A pool token
# outside it is not a name the game can look up, so it is dropped rather than
# carried forward -- which is also how a bad key from an earlier run of this
# script gets swept out instead of surviving in the union below.
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z_0-9\-]*\Z")


def stg_sources(stem: str) -> list[str]:
    """Which STNH list(s) feed this STG one."""
    if stem in EXPLICIT:
        return EXPLICIT[stem]
    bare = stem[len("minor_"):] if stem.startswith("minor_") else stem
    for cand in (bare.capitalize(), bare.upper(), bare):
        if (STNH / "common" / "name_lists" / f"{cand}.txt").is_file():
            return [cand]
    return []


ORDER = ["generic", "corvette", "destroyer", "cruiser", "battleship", "titan",
         "juggernaut", "colossus", "science", "colonizer", "sponsored_colonizer",
         "constructor", "transport", "ion_cannon", "research_station",
         "observation_station", "mining_station", "military_station_small",
         "military_station_medium", "military_station_large"]


def render(pools: dict[str, list[str]]) -> str:
    # ORDER decides what is written, so a key missing from it is a pool that
    # would vanish without a word -- the failure mode this whole file exists
    # to make impossible.
    lost = [k for k in pools if k not in ORDER]
    if lost:
        die(f"ship_names key(s) {lost} are not in ORDER and would be dropped")
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
    have = existing_loc()
    new_loc: dict[str, str] = {}
    stats = Counter()
    unmapped: Counter = Counter()

    for f in sorted(LISTS.glob("stg_*.txt")):
        stem = f.stem[len("stg_"):]
        srcs = stg_sources(stem)
        if not srcs:
            stats["no STNH source"] += 1
            continue

        harvested: dict[str, list[str]] = {}
        for s in srcs:
            for key, toks in stnh_pools(s).items():
                harvested.setdefault(key, []).extend(toks)

        text = read(f)
        span = block(text, "ship_names")
        if span is None:
            die(f"{f.name} has no ship_names block")
        current = text[span[0]:span[1]]

        # STG's own hand-written names stay: the pools are a UNION, so
        # Enterprise, Voyager and Defiant survive a harvest that does not
        # happen to contain them.
        pools: dict[str, list[str]] = {}
        for m in re.finditer(r"(?m)^[ \t]*(\w+)[ \t]*=[ \t]*\{", current):
            pre = current[:m.start()]
            if pre.count("{") != pre.count("}"):
                continue
            end = close_of(current, m.end()) - 1
            keep, drop = [], 0
            for t in current[m.end():end].split():
                if TOKEN_RE.match(t):
                    keep.append(t)
                else:
                    drop += 1
            stats["unusable token(s) dropped"] += drop
            pools[m.group(1)] = keep

        added = 0
        for key, toks in harvested.items():
            seen = set(pools.get(key, []))
            for t in toks:
                value = loc.get(t)
                if value is None or not value.strip():
                    unmapped[t] += 1
                    continue
                # Decision 45's rule: a value that is still a loc key, or that
                # carries markup, is not a name and must never be shipped.
                if re.fullmatch(r"[A-Z][A-Z0-9_]{3,}", value) or "§" in value \
                        or "$" in value or "[" in value:
                    unmapped[t] += 1
                    continue
                k = stg_key(value)
                # ONE FLAT NAMESPACE, so a key already spelled keeps its
                # spelling. STG writes Bok'Nor where STNH writes Bok Nor, and
                # both reduce to STG_N_BokNor; STG's is the deliberate one --
                # stg_names_l_english.yml's header records that whole family as
                # apostrophes recovered from tokens that spelled a space and an
                # apostrophe identically. Counted, not silent.
                prior = have.get(k, new_loc.get(k))
                if prior is not None and prior != value:
                    stats["kept STG's spelling"] += 1
                elif k not in have:
                    new_loc[k] = value
                if k not in seen:
                    seen.add(k)
                    pools.setdefault(key, []).append(k)
                    added += 1

        stats["lists rewritten"] += 1
        stats["names added"] += added
        body = "\n" + render(pools) + "\t"
        text = text[:span[0]] + body + text[span[1]:]
        if not args.dry_run:
            f.write_text(text, encoding="utf-8-sig")

    if not args.dry_run and new_loc:
        head = (
            "l_english:\n"
            " # Star Trek Galaxies -- ship registry names harvested from STNH.\n"
            " #\n"
            " # GENERATED by tools/gen_ship_names.py, alongside the ship_names\n"
            " # pools in src/common/name_lists/. Same flat STG_N_ namespace as\n"
            " # stg_names_l_english.yml, which holds the hand-written names; a\n"
            " # name already spelled there is not repeated here.\n"
            " #\n"
            " # See .docs/decisions/56-ship-name-pools.md\n")
        lines = [head]
        for k in sorted(new_loc):
            lines.append(f' {k}:0 "{new_loc[k]}"\n')
        LOC_OUT.write_text("".join(lines), encoding="utf-8-sig")

    print(f"  {LISTS.relative_to(REPO)}/  {stats['lists rewritten']} list(s) "
          f"rewritten, {stats['no STNH source']} left on their own pools")
    print(f"  {LOC_OUT.relative_to(REPO)}  {len(new_loc)} new name key(s)")
    print(f"    +{stats['names added']} name token(s) across the pools")
    if unmapped:
        print(f"    {len(unmapped)} STNH token(s) skipped for having no usable "
              f"english value (e.g. {', '.join(list(unmapped)[:4])})")


if __name__ == "__main__":
    main()
