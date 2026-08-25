# 89 — The Republic of Hope and the Klingon-Cardassian Alliance are gone: two 2300s empires holding a second 40 Eridani and a second Qo'noS

**Status:** decided, 2026-08-25
**Closes** [decision 46](46-coalition-of-hope-takes-vul.md)'s subject — the
empire that took `VUL` no longer exists.
**Follows** [decision 88](88-playable-gates-the-design-database.md), which put
all 99 in the AI pool and so made every duplicate home system a galaxy that
holds the same world twice.

## The call

The user asked for both empires to be removed. This file records what "removed"
had to reach, because two prescripted empires are never only two blocks in one
file.

## Why they were the two worth removing

Both are alternate-timeline entries — the localisation named them
`Republic of Hope (2300s)` and `Klingon-Cardassian Alliance (2300s)` — and
`tools/gen_home_systems.py` had matched both to a home system another empire
already held:

| empire | STNH source system | also held by |
|---|---|---|
| `stg_minor_tng_coalition_hope` | `vulcan_homeworld` | `stg_confederacy_of_vulcan` — 40 Eridani |
| `stg_minor_tng_klingon_cardassian_alliance` | `klingon_homeworld` | `stg_klingon_empire` — Qo'noS |

Not the *same* initializer key, so nothing collided the way the Federation and
the mirror Terran Empire collided on `sol_system_initializer` — these were two
separate copies of the same place, each with its own key. Under the gate
decision 88 removed, neither could ever load and it cost nothing. Without the
gate, a galaxy could hold two 40 Eridanis, and vanilla's own
`AI_EMPIRE_PREVIEW_TOOLTIP_INCOMPATIBLE_SYSTEM` shows the engine has no opinion
about that case at all: it warns only about a shared key.

## What "removed" reached

Nine things, and only the first was the empire:

1. **The two blocks** in `src/prescripted_countries/stg_z_minor_powers.txt` —
   79 minors becomes **77**, 101 empires becomes **99**.
2. **Their two home systems**, by regenerating rather than editing:
   `tools/gen_home_systems.py` reads `src/prescripted_countries/`, so dropping
   the empires drops `stg_minor_tng_coalition_hope_home` and
   `stg_minor_tng_klingon_cardassian_alliance_home`. 38 generated systems
   becomes **36**.
3. **Species class `TNGK`**, declared for the Alliance and named by nothing
   else — not by a clothes selector, not by another empire.
4. **Species class `TNG`**, which is the part that would have been missed. Its
   own comment records it as claimed by no empire since decision 46 moved the
   Coalition of Hope onto `VUL`; it was kept alive only because the empire
   existed. With the empire gone it is dead in both directions. 131 classes
   becomes **129**.
5. **The `TNGK` portrait set.** The minors section is now 77 blocks for 77
   empires with 77 distinct classes — the "78 blocks below, not 79" note that
   existed *because* the Coalition of Hope shared `VUL` is deleted, not
   renumbered.
6. **18 empire localisation keys** and **54 species localisation keys** (27
   each for `TNG` and `TNGK`, the family [decision 21](21-species-class-localisation.md)
   requires).
7. **The counts in the comments that state them** — six in
   `stg_z_minor_powers.txt`, one in `stg_major_powers.txt` (`95 of the 101` is
   now `92 of the 99`; the seven that pin `clothes = 0` are unchanged), one in
   `stg_species_classes.txt`, four in `stg_portrait_sets.txt`.
8. **A stub count that was already wrong.** `stg_species_classes.txt` said
   `31 of the 131 are selector stubs`. There were 30 stubs below the divider
   before this change and 30 after — the 31st was `TNG`, which sat above the
   divider as a real class no empire claimed. It now reads `30 of the 129`, and
   the sentence is true for the first time.
9. **Six documents** that state the counts as current fact: `status.md`,
   `phases.md`, `glossary.md`, both run plans, `stnh-art.md`. Decisions and
   analyses keep their numbers — those record what was measured on a date.

## What was deliberately left

**The flag art.** `flags/trek/coalition_of_hope.dds` and `Mirror2.dds` stay
vendored. They are STNH heraldry in the `trek` category that
[decision 49](49-flags-city-sets.md) put in front of the player, and a flag
nobody's empire names is still a flag a player can pick. `make clutter` agrees:
nothing unreferenced inside the prune scope.

**The `starfleet_tng` shipset**, which both empires flew and which the
Federation and four others still do.

## What this does not do

**It does not change how many Trek empires reach the galaxy.** That question is
open and this removal is orthogonal to it — see
[open-questions.md](../planning/open-questions.md), "Whether the galaxy is Trek
now". 99 empires that cannot be drawn are no better than 101.

`make vendor` / `validate` / `docs` / `clutter` / `gen-check` all clean;
`validate` reports 99 prescripted empires, 129 species classes, 36 home systems,
0 warnings.
