# 95 — A colony pool must not offer a name its own empire's home system already carries, and 17 tokens did

**Status:** decided, 2026-08-28 — the content call
[open-questions](../planning/open-questions.md) recorded on 2026-08-28 and
deliberately left unmade, measured against two floors, put to the maintainer and
applied.
**Completes** the *"Sixteen home-system bodies are also offered as colony
names"* item, and **corrects its count**: it is **seventeen names across twelve
empires**, not sixteen across eleven.
**Widens** `check_colony_name_collisions`, added by
[decision 23](23-real-home-systems.md).
**Third instance of** the lesson in
[decision 79](79-shipset-descs-and-home-system-names.md) — a measurement taken
without reading the check next door.

## The call

**Drop the seventeen tokens from `planet_names`, and leave every `ship_names`
copy alone.**

| empire | dropped from its `planet_names` |
|---|---|
| Klingon | Praxis |
| Romulan | Remus, Hobus |
| Vulcan | T'Khut, Delta Vega |
| Bolian | Bolarus III, Bolarus VII |
| Breen | Dozaria, Portas V |
| Bajoran | Andros, Jeraddo |
| Ferengi | Clarus |
| Trill | Mak'ala |
| Cardassian | Hutet |
| Xindi | Azati Prime |
| Yridian | Yridia IV |
| Terran | Mars |

Twelve files in `src/common/name_lists/`, one occurrence each, all inside
`planet_names > generic > names`. These files are **hand-authored** —
`gen_ship_names.py` and `gen_ship_class_names.py` rewrite `ship_names` and
`ship_class_names` in the same files and neither touches `planet_names`, and
`gen_star_names.py` only *reads* the pool — so the edit belongs in `src/` and all
13 generators are still fixpoints after it.

## Why it is a defect and not flavour

The item said the widened check "needs its own vanilla floor first" and that
"vanilla's nine home systems are the only calibration set available and they are
few". **There is a second set and it is the right one**: STNH, whose home
systems STG's are harvested from.

| tree | empires on a `usage = custom_empire` initializer | bodies | pool tokens | collide |
|---|---|---|---|---|
| vanilla | 10 | 158 | 776 | **0** |
| STNH, its own tree | 111 | 607 | 1,161 | **1** |
| STG, before this | 37 | 308 | 809 | **12** |

**STNH's 111 is soft and its 1 is a joke** — *"Pakled Planet"* — because most
STNH name lists ship an empty `planet_names`. Restricting all three to empires
that had the chance, **≥3 bodies and ≥20 pool names**: vanilla **0 of 8**, STNH
**0 of 10**, STG **3 of 14**.

**The controls are direct rather than statistical.** Four of STNH's ten sit on a
**32-body Sol with a 160-name pool** — `UnitedEarth`, `ConfederationEarth`,
`tngUnitedFederationofPlanets`, `tngTerranEmpire` — and none collides once.
Vanilla's United Nations of Earth is the same control at 18 × 59: `HUMAN1`'s
pool contains **no** Sol body at all.

**And the convention is legible, not merely observed.** STNH's `Terran.txt` puts
Mercury, Venus, Mars, Jupiter, Saturn, Luna, Titan and Europa in **`ship_names`**
— Starfleet's own naming convention — and the only Mars anywhere in its
`planet_names` is `TERRAN_PLANET_NewMars`. **A home-system body becomes a ship
name; a colony is a new place, or `New` the old one.** STG already did that half:
`stg_terran.txt` carries `STG_N_Mars` in five `ship_names` tiers. Only the pool
leaked, which is why the fix is a deletion and not a rewrite.

## The seventeenth name, and why one measurement could not see it

Eleven of the twelve empires collide key-for-key: `STG_N_Praxis` is in the pool
and `"Praxis"` is in the system. **The Terran Empire does not.** Its home system
is Sol, so the body carries **vanilla's** `NAME_Mars` while the pool offers
**our** `STG_N_Mars`. Two keys, one displayed name, and a comparison over keys
reports nothing.

`check_colony_name_collisions` had said so in its own docstring since decision
23 — *"the collision is between their VALUES: STG_N_Vulcan and
STG_planet_name_vulcan are different keys that both render Vulcan"* — and
resolves both sides through localisation before comparing. The measurement that
produced the sixteen did not. That is the **third** time a finding here has
stopped one question short of a mechanism already written down next door, after
the two [decision 79](79-shipset-descs-and-home-system-names.md) records.

## What the check cost, and it was not the contention

The third flavour is fifteen lines. **Two drafts of it were wrong, and the
calibration is the only reason either was caught** — both failed by
*under*-reporting, which a clean `make validate` would have reported as success
([check design rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)).

**Draft one resolved localisation from the build only** and found 11 empires,
not 12. Vanilla's `NAME_Mars` is not in `stg-build/localisation/`, so the Terran
body stayed an unresolved key — the check missed the exact case it had been
written for, in a second layer of the same blindness.

**Draft two added vanilla and found 10.** `(root/"localisation").rglob("*.yml")`
takes **every language** vanilla ships, and with `setdefault` keeping the first
file walked, Portuguese won: Mars resolved to *"Marte"*, Praxis to
*"Práxis&!name"*. Adding a whole language pack **unmade** a finding the check
had been reporting a moment earlier. The glob is `*l_english.yml` now. The build
is english-only, so this changes nothing for the two older flavours — but the
same latent trap was sitting in them.

**Proof it can fail:** reverting the repair in `src/` and rebuilding, the check
reports **12 errors naming all 17 names**, the Terran Mars among them, and
`make validate` is back to 0 with the repair in place.

`_initializer_body_names` is now a shared helper, used by this check and by
`check_home_system_body_names`, which asks whether two of those bodies collide
with **each other**. They read the same bodies the same way and had no business
doing it twice.

## What this does not do

**It does not touch the sixteen `ship_names` occurrences**, which are correct and
are the convention.

**It does not widen the scope past `usage = custom_empire`.** An empire whose
initializer the engine will not give it has no home system to collide with, and
vanilla's own initializers fail the *neighbouring* question 62 times in 357 for
reasons that are deliberate ([79](79-shipset-descs-and-home-system-names.md)).

**Pools shrank by one or two names each** — Bolian 19 → 17, Vulcan 20 → 18 — and
were not topped back up. Nothing measures a pool's depth, and the alternative on
the table, STNH's `New<name>` form, was declined: it reads badly on the numbered
bodies (*"New Bolarus III"*).
