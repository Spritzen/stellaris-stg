# 100 — Starbase Extended sizes every tier's slot table off the largest tier, and the smaller ones name attach points no mesh carries

**Status:** decided, 2026-08-28
**Follows** [decision 33](33-station-section-attach-points.md) and
[decision 77](77-hull-section-attach-points.md), the same defect in the station
and hull families. This is the third, and the first where the art is vanilla's
and unedited — what is ours is the table.
**Follows** [decision 37](37-sbx-citadel-slot-renumbering.md), the same mod, the
same shape and the same lever: patch SBX's table, never vanilla's content.

## The report

From the 2026-08-28 UFP run, at 21:38:18 — during play, an hour into the
session:

```
pdx_entity.cpp:1217  mammalian_01_starbase_starport_entity has no attach point named part4
pdx_entity.cpp:1217  mammalian_01_starbase_starport_entity has no attach point named part5
pdx_entity.cpp:1217  mammalian_01_starbase_starport_entity has no attach point named part6
pdx_entity.cpp:1217  mammalian_01_starbase_starport_entity has no attach point named part7
```

**Word for word decision 77's message, and decision 33's before it.** The
2026-08-27 run carried zero of these; `make validate` was clean; the 230 attach
points decision 77 wrote were all still in place. This is a different family.

## The mechanism

A starbase size's `section_slots` hangs each module on a named locator, and the
locator has to exist in the mesh the entity's `pdxmesh` resolves to. Vanilla
sizes its tables to its own art:

| size | vanilla names |
|---|---|
| `starbase_starport` | `part1` `part2` `part3` |
| `starbase_starhold` | `part1` … `part5` |
| `starbase_starfortress`, `starbase_citadel` | `part1` … `part7` |
| `orbital_ring_tier_1` | `part1` `part2` `part3` |
| `orbital_ring_tier_2` | `part1` … `part4` |
| `orbital_ring_tier_3` | `part1` … `part5` |

Starbase Extended 3.0 gives the **whole family one table**. Its starport,
starhold, starfortress and citadel blocks are byte-identical — one 36-slot table
reaching `part7`, sized for the citadel — and its three orbital ring tiers share
another, reaching `part5`, sized for tier 3. On the top tier of each family the
art answers and nothing is wrong. On the tiers below it, every slot past
vanilla's own limit hangs on a locator that is not in the mesh: **the section
never attaches, the module never renders, and the only trace is one
`pdx_entity` record per point, per entity, the first time somebody looks at
one.**

## The sweep, which is 72 entities and not one

The log named a single starport, because a starport is what the run happened to
draw. Sweeping the rule instead of the instance — vanilla's table for a size
against the merged one, then every graphical culture's entity against the
points the merged table names:

| size | missing | entities |
|---|---|---|
| `starbase_starport` | `part4` `part5` `part6` `part7` | 16 |
| `starbase_starhold` | `part6` `part7` | 16 |
| `orbital_ring_tier_1` | `part4` `part5` | 20 |
| `orbital_ring_tier_2` | `part5` | 20 |

**72 entities, and 40 of them are declared by vanilla alone** — every culture's
orbital ring, art SBX never touches. That is why no check saw this and why the
log is the weaker evidence: a screen nobody opened is a check that never ran,
and forty of these could not have been reported by any run at all until someone
built a ring.

## The fix

Four `vendor.yml` patches, one per affected size, remapping every over-reaching
slot onto a point vanilla's own table for that size names:

| size | remap |
|---|---|
| `starbase_starport` | `part4`,`part6` → `part2`; `part5`,`part7` → `part3` |
| `starbase_starhold` | `part6` → `part4`; `part7` → `part5` |
| `orbital_ring_tier_1` | `part4` → `part2`; `part5` → `part3` |
| `orbital_ring_tier_2` | `part5` → `part4` |

Slot count, module capacity and every other field are untouched: an SBX starport
still carries six modules, they now attach.

**Repointed, not authored**, which is decision 37's argument reused. Adding the
points to the art is not available: they are baked into the mesh, not declared
in the `.asset`, so a declared locator could only sit at the model origin —
[decision 26](26-weapon-locator-positions.md)'s failure by another route, on 72
entities, 40 of them vanilla's. Reusing an existing point is **SBX's own idiom**
and not a compromise this patch introduces: in the table as shipped, `part5`
already carries eight of the 36 slots and `part7` seven.

**The tiers that work are left alone.** starfortress, citadel and ring tier 3
name nothing vanilla does not, and collapsing them onto `part2`/`part3` would
bunch six modules onto two hardpoints on the tiers that render correctly today.
That is the whole reason this is four anchored patches rather than one
replacement of a table that appears four times in one file — each `from` carries
the size's own `combat_size_multiplier` line, which is all that distinguishes
the identical blocks, and each asserts `count: 1`.

## The guard, and why it is a new check rather than a wider old one

`check_section_attach_points` asks exactly this question one level down — does
the ENTITY carry the point — and could not have caught it twice over: the
starbase family is outside both of its scopes, and it skips entities vanilla
alone declares, which is 40 of the 72. Neither is a bug in it. Its subject is
art we vendor, and here the art is innocent.

`check_slot_table_widening` asks the question one level **up**, where the defect
actually is: **a vendored `section_slots` may not name an attach point vanilla's
own table for the same size does not.** Vanilla's table is the only guarantee
anybody has of what every culture's mesh holds, because vanilla ships art for
all of them and never names a point its art lacks. It reads two text files, no
meshes, and its whole population is six sizes — the four above, plus SBX's
genuinely new `starbase_stronghold` and `starbase_headquarters`, which have no
vanilla table to be compared against and are exempt. Baseline 0, ack list
`slot_table_widening_ack`, empty.

## A precedence bug this found on the way

`check_section_attach_points` read `common/ship_sizes/` **BUILD first, then
vanilla**, and assigned unconditionally — so for a size declared in both trees
under different filenames, vanilla's table landed last and won. The engine
resolves it the other way: vanilla loads first and the mod's file replaces the
size whole, which is how `sbx_3_0_starbases.txt` takes `starbase_starport` off
`00_starbases.txt` without shadowing it by path. **19 sizes are declared that
way.** It was latent rather than load-bearing — `ion_cannon` is the only one of
the 19 inside the check's station scope and vanilla and SBX agree on it — but
the check was reading a table the game never uses. Both checks now share
`_slot_tables()`, which reads in engine order.

## What this does not fix

**Nothing here is confirmed in game.** Module placement is eyes-only:
`make validate` clean says the locator now exists, not that six modules on two
hardpoints look right on a starport. That is the standing caveat of
[decision 07](07-stnh-art-shadows-vanilla.md) and decision 77 both, and it is
listed in [open questions](../planning/open-questions.md).

**One starbase-family entity is still short of a point and it is ours.**
`federation_32_starbase_fe_outpost_entity`, in STNH's own
`federation_32_starbase_entities.asset`, carries no `part1`, which vanilla's
`starbase_fe_outpost` table names — so a fallen empire flying that culture gets
no core section. It is one entity, the detector is a byte search of a mesh blob
that decision 77 already records as capable of a false negative on an animated
rig, and it is outside `check_slot_table_widening`'s subject. **Left, and named
here rather than swept in silently**: widening the entity check to the starbase
family is the work that would settle it.
