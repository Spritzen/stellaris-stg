# 80 — More Events Mod is in scope and waits, because it writes the databases Phase 4 just wrote by hand

**Status:** decided, 2026-08-09
**Follows:** [12](12-fix-source-errors-dont-drop.md),
[75](75-trek-anomalies.md), [76](76-trek-archaeology.md),
[77](77-trek-story-events.md)

## What was decided

**More Events Mod (`727000451`) and the compatch that ships with it
(`2993881965`) are subscribed on purpose, for an integration pass that has not
started.** Neither is snapshotted into `.source/` and neither is in `vendor.yml`.
The pass begins once the content already in the tree has been through a live run
and graded; snapshot them then.

This is a **sequencing** call. It is not a
[decision 12](12-fix-source-errors-dont-drop.md) content call, and no case has
been made against MEM.

## Why it waits, rather than why it was declined

MEM is 2.3 GB declaring `v4.4.*` — 917 `common/`, 160 `events/`, 1,810
localisation and 1,870 `gfx/` files. It writes anomalies, archaeological sites
and country events: **the same three databases decisions
[75](75-trek-anomalies.md), [76](76-trek-archaeology.md) and
[77](77-trek-story-events.md) have just filled by hand**, all three of them
landing on 2026-08-09 and **none of them yet seen by the game**
([status.md](../planning/status.md)'s baseline predates all four).

Harvest MEM first and every finding in the next `error.log` — and every judgement
in front of the screen — becomes a question of whose content it belongs to. The
21 Trek anomalies, 6 dig sites and 21 story events are graded by eye or not at
all ([open questions](../planning/open-questions.md)), and eyes cannot attribute
what they cannot separate. Their yardsticks are stated against *vanilla's* pools
— 40 base-game anomaly categories, 10 base-game site types, an 18.6% pulse — and
MEM moves every one of those denominators.

So the order is: **grade what is here, then take MEM.** The cost of waiting is a
delay. The cost of not waiting is that Phase 4's whole eyes-only surface stops
being measurable, which is not recoverable by re-reading a log.

## The compatch's name is wrong, and that is the trap worth recording

Its descriptor reads *"Real Space System Scale/Planetary Shields Compatch 2.0"*
and declares `supported_version="3.11.2"`, which reads as a patch for a mod STG
does not subscribe to and would be dismissed on sight. **All 19 of its files are
`mem_*`**: it rescales MEM's planetary-shield ambient objects and planet entities
for **Real Space – System Scale**, which STG harvests at position 2
([harvest order](../architecture/harvest-order.md)).

It therefore belongs to MEM, comes into scope the moment MEM does, and is
exactly the kind of art-versus-scale bridge System Scale's own submods are.
Its stale `supported_version` is the usual author-declared caution flag and says
nothing about whether it works — [subscribed mods](../planning/subscribed-mods.md#declared-support-below-our-44-target).

## What this decision does not settle

Nothing about *how* MEM is integrated: which paths are taken, whether its events
are re-gated the way STNH's clothing triggers were
([16](16-phase-3-clothing-triggers.md)), whether generic Stellaris flavour sits
beside Trek flavour at all, or where it lands in harvest order. Those are the
integration pass, and they are open. **Only the timing is closed.**
