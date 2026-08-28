# 79 — Thirty shipset descriptions were keyed to the wrong database, six home systems named a body twice, and one finding falsified itself

**Status:** decided, 2026-08-22
**Follows** [decision 78](78-widen-attach-points-and-two-new-checks.md), whose
"read the docs against the tree" sweep this continues — three of the four items
below came from the same place and none from a live run.
**Follows** [decision 59](59-city-set-cultures-undeclared.md), whose mechanism
analysis 2026-08-16 read forwards, and which turns
out not to run in that direction.
**Follows** [decision 23](23-real-home-systems.md), whose generator carried two
bugs nothing had ever asked about.

## Where these came from

Analysis 2026-08-16 left three items marked
*confirmed on disk, waiting on a content call* — its findings 2, 3 and 4. This
records what happened when each was actually worked. **Two were real and larger
than recorded; the third was not a defect at all.**

The pattern worth carrying: **each of the three had been measured once, and each
measurement had stopped one question short of the mechanism.** Finding 3 counted
the dead keys without asking what the live population was. Finding 4 found one
duplicate name without asking whether the generator that wrote it could write
more. Finding 2 found missing art without reading the line in vanilla's own file
header that says what happens when art is missing.

---

## 1. The shipset descriptions were keyed against the wrong culture database

**All thirty were wrong, in one direction or the other.**

STG wrote 14 `<culture>_shipset_desc` keys. Seven named a **city-set** culture
rather than a **shipset** one — `vulcan_01` where the Vulcans fly `vulcan`,
`federation` where the Federation flies `starfleet_tng`, and likewise
`borg_01`, `cardassian_01`, `dominion_01`, `ferengi_01`, `tholian_01`. Three of
those seven name a culture that **is not declared anywhere at all**. Meanwhile
**23 cultures that a prescripted empire actually flies had no key**, so the
browser drew the raw string for every Walshicus set in the mod.

The prose was written and good. It was filed against the wrong index.

**The repair is a rename for the seven and sixteen new descriptions**, and the
new prose is **grounded in the art rather than in lore**: the hull diffuse
textures under `stg-build/gfx/models/ships/<culture>/` were read before any line
was written, which is why `generic_06` is described as pale and cyan-veined (its
three flyers are aquatic species and its texture is exactly that) and `malon` as
ochre under hazard striping. A `generic_NN` set is flown by many unrelated
minors and so names no species; a set named for a civilisation names it, which
is the convention the Klingon and Romulan lines already used.

**The calibration is the cleanest this project has measured.** Vanilla declares
**52** graphical cultures and writes only **20** description keys, so *"every
declared culture is described"* is not the rule and a check asking it would
report vanilla in 32 places. But:

| direction | vanilla | STG before | STG after |
|---|---|---|---|
| a culture a prescripted empire **flies**, with no key | **0 of 19** | 23 of 30 | **0 of 30** |
| a key naming a culture **nothing declares** | **0 of 20** | 3 of 14 | **0 of 30** |

Both floors are exactly 0, so `check_shipset_descriptions` needs no scope
([rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter)).
**Flown is the population; declared is the sanity bound.**

> **One correction to how this was reported.** The run plan predicted an *empty*
> panel and the run saw the key text. That is not a second defect: **Stellaris
> renders an unresolved localisation key as the raw key**, so "the box shows
> `vulcan_shipset_desc`" is the normal signature of a missing key. The
> expectation was wrong, not the observation.

## 2. One duplicate body name was three bugs in six systems

Analysis 2026-08-16 finding 4 recorded two bodies in
40 Eridani both named "Kerkhov's Moon" and called it *"small, certain, one
edit"*. Swept across all 37 generated home systems it is **seven duplicates in
six systems**, from **three unrelated causes**, and none of them is an edit to
the file — `stg_home_systems.txt` is generated, and its header says so.

**Cause A — `sub_blocks` did not do what its docstring said.** It promised
"immediate children" and its `finditer` scanned the whole body, returning matches
at every nesting depth. STNH writes Kerkhov as a `planet` **nested inside** the
star 40 Eridani C, so Kerkhov's moon was returned as a moon of the *star* as well
as of its own parent, and both were emitted. Fixed with a depth guard, plus an
explicit `planets_flattened()` so the nested planet is still promoted to system
level — that promotion was always intended, it just used to be a side effect of
the bug.

**Cause B — a star is not always spelled `pc_<x>_star`.** The rule that stops a
star sharing the capital's name matched that spelling only, and the generator's
commonest star is the **bare `star` keyword** filled in by the engine. So the
rule fired for Andoria and silently missed **Qo'noS, Cait, Romulus and Haakon**,
each of which drew its capital's name twice on one map.

> **And fixing it by substitution would not have worked.** Pointing the star at
> the system's own loc key only helps when the system and the capital are named
> differently — and **23 STG empires render the same string for both** (Bajor the
> system, Bajor the planet), which is Trek's convention and not a defect. The
> substitution would have rendered the identical word and left the check passing
> over a defect a player can still see.
>
> **Vanilla settles it by omission.** **12 of the 16** star bodies in its
> `usage = custom_empire` initializers carry **no name at all** and the engine
> names the star from its system; the four it does name are Sol, Deneb and the
> two stars of the Titawin binary. So the colliding name is **dropped**, not
> replaced. Inventing a name for the Klingon sun would be content, and this
> generator does not author content.

**Cause C — STNH's own file.** Both moons of the gas giant S'latas are named
"S'latas a", where the rest of their Romulan system suffixes properly.
[Decision 11](11-fix-source-errors-dont-drop.md) says fix a source's errors, and
their own convention says the fix: the second becomes "S'latas b". It is recorded
in a `SOURCE_NAME_FIXES` table beside `ALIASES`, deliberately small.

**`check_home_system_body_names` scope is `usage = custom_empire`, and that is a
calibration result.** Asked of every vanilla initializer the question fails **62
times in 357** — 17%, because vanilla repeats a name deliberately for identical
decorative objects (four `NAME_Ring_Section`s, three `NAME_Mining_Corps`). Asked
of the nine initializers a prescripted empire actually starts in, vanilla's count
is **0**. A home system is hand-authored and every body in it is meant to be a
place.

> **A measurement error worth recording.** The first version of this check
> counted the initializer's own top-level `name` as a body and reported **Sol
> against itself** — vanilla names the system `NAME_Sol` and its primary star
> `NAME_Sol`, which is the convention the whole de-collision rule is built on.
> Compare bodies with bodies.

## 3. Finding 2 was not a defect — the fallback is the mechanism

Analysis 2026-08-16 finding 2 read six declared
cultures with no `<key>_city_l01.dds` as six styles the empire designer offers
with nothing to draw, and asked for a content call: point them at one of the
orphan city sets, or accept a blank planet surface. **Neither is needed, and the
answer is in the first three lines of vanilla's own file.**

> `# Setting fallback will allow the game to try and use another culture if the
> asset is missing`
> — `/stellaris/common/graphical_culture/00_graphical_culture.txt`

Every one of the six declares `fallback = mammalian_01`, and `mammalian_01`
ships city art.

**The numbers that make that more than an assertion:**

| population | vanilla | STG |
|---|---|---|
| declared cultures | 52 | 41 |
| …with no city art of their own | **24 (46%)** | 27 |
| …offerable (no `randomized = { always = no }`) | 22 | 41 |
| offerable, no art, **no fallback chain that reaches any** | **0** | **0** |

**46% is why "declared implies art" cannot be the rule** — vanilla would be
broken in 24 places. Narrowing to the cultures actually offered leaves two
vanilla cases, `mindwarden_01` and `nemesis_01`, and both declare a fallback.
Follow the chain and both counts are 0.

`check_graphical_culture_art` asks the invariant that does have a floor: **an
offerable culture must reach city art, its own or its fallback's.** STG passes it
today at a *stricter* population than vanilla's, because STG declares no
`randomized = { always = no }` at all, so all 41 of its cultures are in scope
against vanilla's 22.

**The second half of finding 2 — `generic_01`–`generic_06`, art no
`city_graphical_culture` names — is orphan art, not a defect.** That is
`check_unreferenced`'s question, `gfx/portraits/city_sets` is already one of its
closure roots, and the standing policy on report-tier orphans is
[decision 43](43-clutter-pass.md).

> **What generalises.** This is the second finding in two analyses to dissolve on
> contact with a measurement that already existed — finding 5 was struck by
> [decision 78](78-widen-attach-points-and-two-new-checks.md) for the same
> reason. **Both were measurements taken without reading the thing that had
> already measured them.** Before writing a check for a finding, read vanilla's
> own file header and the check next door.

---

## What this cost, and what it leaves

`make vendor`, `make validate`, `make docs` and `make gen-check` are clean:
**0 warnings, 0 errors**, 11 of 11 generators still fixpoints.

**All three new checks were made to fail before they were believed**
([check-design rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)):
a renamed key, a removed `fallback` and a pasted body name each produced exactly
the intended warning and nothing else.

**Still not settled, and still needing eyes rather than a container:** whether
the sixteen new descriptions read as Trek, and whether the four stars whose names
were dropped now draw with their system's name as vanilla's twelve do. Both are
[open questions](../planning/open-questions.md) items, not this decision's.
