# 75 — Phase 4 starts with anomalies, because they are the one part of "a voice" with a yardstick

**Status:** decided, 2026-08-09
**Follows:** [74](74-event-picture-families.md)

## The problem this had to solve first

[Phases](../planning/phases.md#phase-4--polish) says Phase 4's remaining work is
"Trek-flavoured events, anomalies and archaeology", and then says the thing that
makes it hard:

> it is the first work in the project with no external definition of done — the
> sources supply no events to harvest and no check can say when a mod has a
> voice. **Scope it deliberately before starting.**

Both halves are true. `stg-build/common/anomalies/` held **0** files and
`common/archaeological_site_types/` held one, from Planetary Diversity; the
harvest takes no `events/` from STNH by design
([architecture/stnh-art.md](../architecture/stnh-art.md)), so there is nothing
to fold, remap or measure against a source the way
[decision 59](59-ship-name-pools.md) and [72](72-ship-class-names.md) could.

## The scope, and why this slice

**Anomalies first, archaeology and story events after.** Three reasons, in the
order they mattered:

1. **Anomalies have a yardstick and archaeology does not.** Vanilla's base game
   ships **40** anomaly categories in
   `common/anomalies/00_anomaly_categories.txt` (327 across all its files, most
   of them DLC and precursor chains). "How many, and how long is a description"
   is a question vanilla answers, which is the same move
   [decision 73](73-class-name-thematic-fill.md) made with class-name pool
   sizes.
2. **An anomaly is the smallest complete unit of voice the game has.** A
   category, an outcome, a picture and four hundred words. It is finishable, and
   twenty of them are twenty times finishable — where an archaeology chain is
   one long thing that is either done or not.
3. **It is purely additive on a vanilla chassis**, which is the design test in
   [scope.md](../planning/scope.md): categories merge by key, so vanilla's 327
   are untouched and these sit beside them. A Stellaris player who has never
   watched Star Trek gets the game they know, with different things in it.

**The art decided the order too.** STNH's 805 pruned event pictures are the
richest unspent asset in the tree, and anomalies are what spends them —
[decision 74](74-event-picture-families.md) is the enabling work, and it had to
be done first or every picture here would have rendered 930×396 in a 693×239
frame.

## What shipped

| | |
|---|---|
| `src/common/anomalies/stg_anomaly_categories.txt` | **21 categories** |
| `src/events/stg_anomaly_events.txt` | **27 outcome events**, one namespace, no chains |
| `src/interface/stg_event_pictures.gfx` | **48 sprites over 24 STNH pictures** |
| `src/localisation/english/stg_anomalies_l_english.yml` | **123 keys, ~3,500 words** |

21 against vanilla's base-game 40 — half, deliberately, and thin rather than
padded, which is the call [decision 73](73-class-name-thematic-fill.md) made
about pool sizes for the same reason.

**Every trigger, reward tier, deposit, modifier and guard is copied from a
vanilla file that was opened**, not remembered: the categories from
`00_anomaly_categories.txt`, the events from `anomaly_events_1.txt`. Including
the guard that is easy to leave out —

```
if = { limit = { NOT = { has_deposit_for = shipclass_research_station } } clear_deposits = yes }
```

— which vanilla puts before every research deposit it adds, because without it
the planet keeps a deposit that makes the research station unbuildable and the
reward is unreachable.

**No `specimen = `, no DLC-gated effect, no `has_ancrel`-style branch.** STG is
standalone and has to behave the same whatever the host owns.

## The two things a reader will want to argue with

**Two pictures were rejected on tone, not availability.** `mugato_world.dds` is
animated in a modern cartoon style and would have sat beside twenty live-action
stills; `romulan_minefield.dds` does not depict a minefield. Both were dropped
after looking at them rather than after reading the filename, which is the only
way that call can be made.

**Seven of the 21 are `max_once` or `max_once_global`.** A Trek anomaly that
names a specific thing — an Iconian gateway, the Omega particle, a neutronium
fragment — reads as broken if the galaxy has four of them. The ones that name a
*kind* of thing (debris fields, derelicts, cliff dwellings) are unrestricted,
which is vanilla's own split.

## The check

`check_anomalies` in `tools/validate.py`. An anomaly is **four files that have
to agree**, and none of them dangles when they do not — a category with no
outcome event resolves to a blank popup, and a missing loc key draws the raw key
on screen. That is [decision 47](47-minor-power-names-truncated.md)'s silence in
a fifth database.

**Vanilla is the calibration and it is nearly perfect**, over its 327 categories
and the 310 `ship_event`s in `events/anomaly_events_*.txt`:

| Question | Vanilla findings |
|---|---|
| category's picture is declared | 0 |
| category name / description loc key | 0 / 0 |
| event title / description / option loc key | 0 |
| event picture is declared | 0 |
| **category names an event that exists** | **1** — `UBUME_BABY_CAT` points at `anomaly.6791`, which Paradox does not ship |

So all six are asked of every anomaly in the built tree. **A seventh question
has a scope**, because its floor is nothing like zero: *"an anomaly event no
category names"* scores **114 of vanilla's 310**, since vanilla chains events
off each other. Over `stg_anomaly_events.txt` the shape is different by
construction — every event there is a category outcome and there are no chains —
so the question is exact there and meaningless anywhere else.
[Check design rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter),
and the same two-scope shape as [decision 51](51-prescripted-loc-scope.md).

**It failed on its first run against real content**, which is the calibration
that counts: the Iconian Gateway category and both its events shipped with no
localisation at all — 8 errors, one authoring slip, invisible to every other
check and to `error.log`. Then deliberately, against a broken tree: a dangling
event id, an undeclared sprite and two orphaned events, all four reported.

## What only eyes can grade

Whether the writing sounds like Star Trek and not like a different mod, whether
the pictures match the text they sit under, and whether the rewards feel right
for the anomaly levels. None of that produces a log record.
[Open questions](../planning/open-questions.md).
