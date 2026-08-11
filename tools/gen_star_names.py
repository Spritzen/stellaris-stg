#!/usr/bin/env python3
"""Generate src/common/random_names/base/stg_star_names.txt from STNH's maps.

Phase 2's last unwritten item: Trek names for the systems a normally generated
galaxy fills in around our 37 hand-placed home systems (.docs/planning/phases.md, Phase 2).

SOURCE: STNH's `map/setup_scenarios/*.txt`, not its `common/random_names/`.
STNH's star_names pool looks like the obvious source and is the wrong one --
its "FICTIONAL" block is 796 of VANILLA's own names plus 40, and the 5,156 it
adds under "EXTRA" are filler (Enchilada, Arugala, Bruscetta, tree and surname
lists) that would read as a bug in a Trek galaxy. The hand-built maps are where
the Trek content is: 1,444 distinct system names placed by name.
See .docs/decisions/52-trek-star-names.md.

CONTENT comes from .source/, never from the built tree. stg-build/ IS read, for
one question only -- which names the merged pool already holds, so this file
appends rather than repeats -- and that read has to skip this tool's own output
or it subtracts itself. See the comment on `built` in main().
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "src" / "common" / "random_names" / "base" / "stg_star_names.txt"
LOC_OUT = (REPO / "src" / "localisation" / "english"
           / "stg_random_names_l_english.yml")

# Nebulae are a different pool. Vanilla's nebula_names is written in exactly
# these forms ("Yinarim_Nebula", "Temestra_Badlands", "Tyjanock_Expanse"), so
# routing on the trailing word follows vanilla rather than inventing a rule.
NEBULA_TAIL = ("Nebula", "Expanse", "Badlands", "Cluster", "Drift", "Patch",
               "Rift", "Void")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace")


def pool(text: str, key: str) -> list[str]:
    """Entries of a depth-0 `key = { ... }` block, comments dropped."""
    out: list[str] = []
    idx = 0
    while True:
        i = text.find(key + " = {", idx)
        if i < 0:
            return out
        if i > 0 and text[i - 1] not in "\n﻿":   # depth-0 only
            idx = i + 1
            continue
        b = text.index("{", i)
        d = 0
        for j in range(b, len(text)):
            if text[j] == "{":
                d += 1
            elif text[j] == "}":
                d -= 1
                if d == 0:
                    break
        out += [x.strip().strip('"') for x in text[b + 1:j].split("\n")
                if x.strip() and not x.strip().startswith("#")]
        idx = j


def stnh_root() -> Path:
    mtext = read(REPO / "vendor.yml")
    m = re.search(r'^\s*-\s*id:\s*"?(\d+)"?\s*\n\s*name:\s*'
                  r'"Star Trek: New Horizons"', mtext, re.M)
    if not m:
        sys.exit("vendor.yml does not declare Star Trek: New Horizons")
    m2 = re.search(r"^\s*source_root:\s*(\S+)\s*$", mtext, re.M)
    root = Path(m2.group(1).strip("\"'")) if m2 else Path(".source")
    if not root.is_absolute():
        root = REPO / root
    return root / m.group(1)


def token(name: str) -> str:
    """Vanilla's own written form, measured rather than assumed.

    Vanilla's star_names holds 1,763 entries: 0 contain a space, and the 55
    multiword ones are QUOTED WITH UNDERSCORES ("Epsilon_Eridani", "Tau_Ceti").
    Apostrophes are ordinary and unquoted (Spoo'a, Gor'kaner, T'u) -- the
    opposite of the common/name_lists/ rule.

    A QUOTED ENTRY IS A LOCALISATION KEY, and this docstring used to say the
    opposite. The measurement behind "these are literals" was taken over the
    UNQUOTED names -- nothing defines Amgathorra, which is true -- and then
    applied to the quoted ones, which is where it fails: all 55 quoted
    star_names and all 55 quoted nebula_names are defined in vanilla's
    localisation/english/random_names/, without a single exception. STG shipped
    330 quoted entries and no keys, so the 2026-08-10 Federation run read
    `Arachnid_Nebula` and `Kullat_Nunu` off the galaxy map. Hence loc_lines().
    See .docs/decisions/52-trek-star-names.md and its falsification.
    """
    n = " ".join(name.split())
    if " " in n:
        return '"' + key_of(n) + '"'
    return n


# A localisation key is [A-Za-z0-9_.] and nothing else. Vanilla proves it from
# both ends: 0 of its English keys contain an apostrophe, and 0 of the 238
# quoted random names do either -- it never has to make this choice because it
# has no multiword name with one. STG has 19 (Barnard's_Star, Tyken's_Rift,
# Sagittarius A*).
_KEY_STRIP = re.compile(r"[^A-Za-z0-9_.]")


def key_of(name: str) -> str:
    """The loc key for a multiword name: spaces to underscores, rest stripped.

    STG's name lists already answer this -- `STG_N_Mak_ala:0 "Mak'ala"` -- and
    the rule is the same one: the KEY is sanitised, the VALUE keeps the
    apostrophe. The value is what the galaxy map draws, so nothing is lost.
    """
    return _KEY_STRIP.sub("", " ".join(name.split()).replace(" ", "_"))


def loc_lines(names: list[str]) -> list[str]:
    """`Key:0 "Display Name"` for every entry token() will quote.

    Only the quoted ones need a key: an unquoted single-word entry is drawn as
    itself and vanilla defines none of those. The display value is the name as
    STNH placed it on the map, which is the spaced form the underscored key was
    built from -- so this is a reversal, not a guess.
    """
    out, seen = [], {}
    for n in names:
        n = " ".join(n.split())
        if " " not in n:
            continue
        k = key_of(n)
        # Sanitising can collide two distinct names onto one key
        # (`Kapteyn'_Star` and `Kapteyn's_Star` both give `Kapteyn_Star`).
        # First wins, and the loser is reported rather than written twice --
        # a duplicate key is the engine's own last-one-wins, silently.
        if k in seen:
            print(f"  note: {n!r} shares key {k} with {seen[k]!r}; "
                  f"one display name will win")
            continue
        seen[k] = n
        out.append(f'  {k}:0 "{n}"')
    return out


def main() -> int:
    stnh = stnh_root()
    scen = stnh / "map" / "setup_scenarios"
    if not scen.is_dir():
        sys.exit(f"no such directory: {scen}")

    trek: set[str] = set()
    for f in sorted(scen.glob("*.txt")):
        for m in re.finditer(r'\bname\s*=\s*"([^"]+)"', read(f)):
            v = " ".join(m.group(1).split())
            if v and not v.startswith("STH_galaxy"):
                trek.add(v)

    # Everything already in the merged pool, so we append rather than repeat.
    # OUR OWN OUTPUT IS NOT "already pooled". `make vendor` copies src/ into
    # the build, so a second run reads this file back and subtracts every name
    # it contributed last time -- 909 entries became 329 exactly once, which is
    # how this was found. Skip by name, so the tool is idempotent.
    built = set()
    base = REPO / "stg-build" / "common" / "random_names" / "base"
    for f in sorted(base.glob("*.txt")):
        if f.name == OUT.name:
            continue
        t = read(f)
        built |= set(pool(t, "star_names")) | set(pool(t, "nebula_names"))

    # Every name STG already owns: home systems, capitals, name-list pools.
    # A random system called Bajor while the Bajoran Republic is at Bajor is
    # the class of bug decision 25 was written about.
    owned: set[str] = set()
    for f in sorted((REPO / "src" / "localisation" / "english").glob("*.yml")):
        owned |= {v for _, v in re.findall(r'^\s*(STG_\w+):0\s*"([^"]*)"',
                                           read(f), re.M)}
    for f in sorted((REPO / "src" / "common" / "name_lists").glob("*.txt")):
        t = read(f)
        for key in ("planet_names", "system_names"):
            owned |= set(pool(t, key))

    fresh = sorted(trek - built - owned)
    # Two names can sanitise onto one token ("Sagittarius A" and
    # "Sagittarius A*"), and writing both would enter the same pool entry
    # twice -- harmless to the game, but it doubles that name's draw weight
    # and gives the key two display values. First wins.
    tokens: set[str] = set()
    deduped = []
    for n in fresh:
        t = token(n)
        if t in tokens:
            continue
        tokens.add(t)
        deduped.append(n)
    fresh = deduped
    stars = [n for n in fresh if not n.rsplit(" ", 1)[-1] in NEBULA_TAIL]
    nebulae = [n for n in fresh if n.rsplit(" ", 1)[-1] in NEBULA_TAIL]

    body = [
        "# Star Trek Galaxies — Trek system names for a generated galaxy.",
        "#",
        "# Harvested from STNH's hand-built map/setup_scenarios by",
        "# tools/gen_star_names.py. These pools APPEND rather than replace",
        "# (decision 44), so this file adds to the 5,702 names Real Space and",
        "# YAGEM already contribute and replaces none of them.",
        "#",
        "# A QUOTED entry is a localisation KEY — all 110 of vanilla's own are",
        "# defined in localisation/english/random_names/. Multiword names take",
        "# vanilla's quoted underscore form and get a key in",
        "# src/localisation/english/stg_random_names_l_english.yml, written by",
        "# the same tool. Unquoted single-word entries are literals and need",
        "# none; apostrophes are ordinary here, unlike name lists.",
        "# See .docs/decisions/52-trek-star-names.md and its falsification.",
        "",
        "star_names = {",
    ]
    body += ["\t" + token(n) for n in stars]
    body += ["}", ""]
    if nebulae:
        body += ["nebula_names = {"]
        body += ["\t" + token(n) for n in nebulae]
        body += ["}", ""]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")

    keys = loc_lines(stars) + loc_lines(nebulae)
    LOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig: vanilla BOMs every localisation file and `make validate`
    # enforces it.
    LOC_OUT.write_text("\n".join([
        "l_english:",
        " # Display names for the quoted entries in",
        " # common/random_names/base/stg_star_names.txt, which are KEYS and not",
        " # literals — see that file's header. Without these the galaxy map",
        " # draws the key, underscores and all.",
        " #",
        " # GENERATED by tools/gen_star_names.py -- rerun it, do not hand-edit.",
        *keys,
        "",
    ]), encoding="utf-8-sig")

    print(f"{LOC_OUT.relative_to(REPO)}: {len(keys)} key(s)")
    print(f"{OUT.relative_to(REPO)}: {len(stars)} star name(s), "
          f"{len(nebulae)} nebula name(s) "
          f"(from {len(trek)} placed, minus {len(trek & built)} already "
          f"pooled and {len(trek & owned)} STG owns)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
