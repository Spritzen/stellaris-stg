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

Reads .source/, never the built tree -- the same rule as the other one-shots.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "src" / "common" / "random_names" / "base" / "stg_star_names.txt"

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
    opposite of the common/name_lists/ rule, because these are literals and not
    loc keys (nothing in vanilla's localisation defines Amgathorra).
    """
    n = " ".join(name.split())
    if " " in n:
        return '"' + n.replace(" ", "_") + '"'
    return n


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
    built = set()
    base = REPO / "stg-build" / "common" / "random_names" / "base"
    for f in sorted(base.glob("*.txt")):
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
        "# Entries are LITERALS, not localisation keys — vanilla defines loc",
        "# for none of its own 1,763. Multiword names take vanilla's quoted",
        "# underscore form; apostrophes are ordinary here, unlike name lists.",
        "# See .docs/decisions/52-trek-star-names.md.",
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
    print(f"{OUT.relative_to(REPO)}: {len(stars)} star name(s), "
          f"{len(nebulae)} nebula name(s) "
          f"(from {len(trek)} placed, minus {len(trek & built)} already "
          f"pooled and {len(trek & owned)} STG owns)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
