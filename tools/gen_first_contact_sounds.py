#!/usr/bin/env python3
"""Rewrite src/common/inline_scripts/first_contact_event_sounds.txt.

WHAT THE FILE IS. Vanilla's `first_contact_event_sounds` is an inline script
that every first-contact event splices in whole, and it is a list of
`show_sound` blocks each gated on the contact's `is_species_class`. It knows
vanilla's thirteen classes and nothing else. STG declares 129 of its own, so
NO BLOCK PASSES for a Trek empire and the engine says so, once per contact:

    event.cpp:896  Failed to pick an event sound from among the available
                   options for event first_contact.355 (defaulting to first
                   on list)

Ten records in the 2026-08-28 UFP run -- every first contact in it -- and the
sound you get is whichever block happens to be first, which is the AQUATIC one.

WHY THIS IS GENERATED AND NOT WRITTEN BY HAND. The mapping has to be TOTAL:
every declared species class in exactly one block. A class left out is not a
compile error, it is one more silently wrong sound and one more log record, and
the next class somebody adds would reopen the defect without touching this file.
So the table below is checked against `src/common/species_classes/` in both
directions and the tool dies on either mismatch, and `make gen-check` asks every
run whether the committed output is still what today's inputs produce.

WHY NOT A TRIGGERLESS CATCH-ALL, which would be four lines instead of 129.
Vanilla has the form -- `events/unrest_events.txt:192` is a `show_sound` block
with a sound and no trigger -- but the engine's own message says it picks "from
among the available options", i.e. it filters by trigger and then chooses. A
block that always passes is therefore always in the running and would take
contacts away from the specific ones rather than backstopping them. Every class
is named instead, and the blocks stay mutually exclusive the way vanilla's are.

VANILLA'S OWN THIRTEEN BLOCKS ARE COPIED THROUGH, read from /stellaris at
generation time rather than restated here: this file replaces vanilla's by path,
so anything not carried forward is silently dropped for vanilla species too
(decision 07's failure mode). `make gen-check` turns a game patch that re-cuts
them into a diff instead of a silence.

    python3 tools/gen_first_contact_sounds.py [--dry-run]

See .docs/decisions/101-first-contact-sounds-are-species-class-gated.md
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GAME = Path(os.environ.get("STELLARIS_GAME_DIR", "/stellaris"))
CLASSES = REPO / "src" / "common" / "species_classes" / "stg_species_classes.txt"
VANILLA = GAME / "common" / "inline_scripts" / "first_contact_event_sounds.txt"
OUT = REPO / "src" / "common" / "inline_scripts" / "first_contact_event_sounds.txt"

# ── the mapping, which is a content call and not a lookup ─────────────────────
#
# Thirteen sounds, 129 classes, and Star Trek is a humanoid franchise: the
# honest shape is a short list of species with a louder non-humanoid reading
# and a long tail that is simply humanoid. Each entry below carries the reason,
# because "why is the Kobali a necroid" is the question this table exists to
# answer and it is not recoverable from the key.
#
# `fungoid` is deliberately unused: nothing in the roster reads as fungal, and
# assigning one to reach thirteen for thirteen would be worse than leaving it.
# `avian` very nearly was — the Aurelians are the franchise's birds and STG has
# no class for them, only clothes art. The Kinshaya carry it instead, on the
# wings.
MAPPING: dict[str, list[tuple[str, str]]] = {
    "machine": [
        ("BRG",  "Borg -- drones, and the class is machine-intelligence only"),
        ("HOLO", "photonic lifeforms; the class is built on vanilla's ROBOT"),
        ("CRA",  "Cravic -- Automated Personnel Units, robots outright"),
        ("PRA",  "Pralor -- the other half of the same war, same robots"),
        ("BYN",  "Bynars, bonded to their computer from birth"),
    ],
    "lithoid": [
        ("THO",  "Tholians -- crystalline, and the class carries LITHOID"),
        ("BRIK", "Brikar -- rock-bodied"),
    ],
    "necroid": [
        ("KOB",  "Kobali, who reproduce by reanimating other species' dead"),
        ("VID",  "Vidiians -- the Phage, and organ harvesting"),
        ("MED",  "Medusans -- non-corporeal, and unbearable to look at"),
    ],
    "toxoid": [
        ("MAL",  "Malon -- theta-radiation haulers, toxic by trade"),
    ],
    "reptilian": [
        ("CAR",  "Cardassians"),
        ("GOR",  "Gorn"),
        ("TRO",  "T'Rogorans, Gorn-adjacent"),
        ("SEL",  "Selay -- serpentine"),
        ("SAU",  "Saurians"),
        ("VOT",  "Voth -- descended from Earth's hadrosaurs"),
        ("XIN",  "Xindi -- six sub-species, and the Reptilians are the face of them"),
        ("HAZ",  "Hazari -- the species class file calls them tuatara"),
        ("TZE",  "Tzenkethi"),
    ],
    "arthropoid": [
        ("UND",  "Undine -- Species 8472, tripedal and not remotely humanoid"),
        ("HUR",  "Hur'Q -- insectoid"),
    ],
    "mammalian": [
        ("CAI",  "Caitians -- felinoid"),
        ("KZI",  "Kzinti -- felinoid"),
        ("LYR",  "Lyrans -- felinoid"),
        ("LYRI", "Lyridians -- the diaspora of the same"),
        ("ANTI", "Anticans -- canine"),
    ],
    "aquatic": [
        ("ANT",  "Antedeans -- piscine"),
        ("MON",  "Moneans, who live in a water world and nothing else"),
    ],
    "molluscoid": [
        ("DOM",  "Founders -- liquid-state, and BIOLOGICAL is only vanilla's nearest archetype"),
    ],
    "plantoid": [
        ("SHE",  "Sheliak -- chlorophyll-based, and contemptuous of carbon units"),
    ],
    "avian": [
        ("KIN",  "Kinshaya -- winged, and the only wings in the roster"),
    ],
}
HUMANOID = "humanoid"      # the tail: every class the table above does not name


def die(msg: str) -> None:
    print(f"gen_first_contact_sounds: {msg}", file=sys.stderr)
    raise SystemExit(1)


def declared() -> list[str]:
    """The species classes src/ declares, in file order."""
    text = CLASSES.read_text(encoding="utf-8")
    return [m.group(1) for m in re.finditer(r"^([A-Z][A-Z_0-9]*)\s*=\s*\{", text, re.M)]


def vanilla_blocks() -> str:
    """Vanilla's own thirteen, verbatim, trailing whitespace normalised."""
    text = VANILLA.read_text(encoding="utf-8")
    if "show_sound" not in text:
        die(f"{VANILLA} carries no show_sound block -- vanilla has changed shape")
    return text.replace("\r\n", "\n").strip("\n")


def block(sound: str, entries: list[tuple[str, str]]) -> str:
    out = ["\tshow_sound = {",
           f"\t\tsound = event_first_contact_{sound}",
           "\t\ttrigger = {",
           "\t\t\tcontact_country? = {",
           "\t\t\t\tOR = {"]
    width = max(len(k) for k, _ in entries)
    for key, why in entries:
        line = f"\t\t\t\t\tis_species_class = {key}"
        if why:
            line = f"\t\t\t\t\tis_species_class = {key:<{width}}\t# {why}"
        out.append(line)
    out += ["\t\t\t\t}", "\t\t\t}", "\t\t}", "\t}"]
    return "\n".join(out)


def render() -> str:
    keys = declared()
    seen = set(keys)
    if len(keys) != len(seen):
        die("src/common/species_classes/ declares a class twice")

    mapped: dict[str, str] = {}
    for sound, entries in MAPPING.items():
        for key, _ in entries:
            if key in mapped:
                die(f"{key} is mapped twice: {mapped[key]} and {sound}")
            if key not in seen:
                die(f"{key} is mapped to {sound} but no species class declares it")
            mapped[key] = sound

    tail = [k for k in keys if k not in mapped]
    if not tail:
        die("nothing left for the humanoid block -- the table cannot be right")

    head = [
        "# first_contact_event_sounds -- OVERRIDES vanilla's file of the same",
        "# path, which is the only way to reach it: the inline script is spliced",
        "# into vanilla's own first-contact events and we shadow none of those.",
        "#",
        "# WHY. Vanilla's list gates every sound on `is_species_class` against its",
        "# own thirteen classes. STG declares 129 of its own and matches none, so",
        "# no block passes and the engine falls back to the first entry on the",
        "# list -- `event.cpp:896`, ten times in the 2026-08-28 UFP run, once per",
        "# first contact, every one of them playing the AQUATIC sting.",
        "#",
        "# Vanilla's thirteen blocks are carried through unchanged and come first:",
        "# this file replaces vanilla's, so a block not copied here is dropped for",
        "# vanilla species too (decision 07's failure mode).",
        "#",
        "# GENERATED by tools/gen_first_contact_sounds.py -- do not hand-edit. The",
        f"# mapping is total by construction: all {len(keys)} classes, each in exactly",
        "# one block, and the tool dies rather than emit a partial one. `make",
        "# gen-check` asks every run whether this is still what the inputs produce.",
        "# .docs/decisions/101-first-contact-sounds-are-species-class-gated.md",
        "",
        "# ── vanilla's thirteen ────────────────────────────────────────────────",
    ]
    body = [vanilla_blocks(), "",
            "# ── STG's, by the nearest reading of the species ──────────────────────"]
    for sound in MAPPING:
        body.append(block(sound, MAPPING[sound]))
    body.append(block(HUMANOID, [(k, "") for k in tail]))
    return "\n".join(head + body) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    text = render()
    if a.dry_run:
        old = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
        print(f"{OUT.relative_to(REPO)}: "
              f"{'unchanged' if old == text else 'WOULD CHANGE'} "
              f"({len(text.splitlines())} lines)")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"  wrote {OUT.relative_to(REPO)}  ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
