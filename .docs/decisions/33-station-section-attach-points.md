# 33 — Walshicus' station hulls carry no section attach points

**Decided 2026-08-07**, from the live run of that morning.

## What happened

Two records, late in the run, after loading finished:

```
pdx_entity.cpp:1217  starfleet_tng_military_station_small_entity has no attach point named part1
pdx_entity.cpp:1217  starfleet_tng_military_station_small_entity has no attach point named part2
```

Vanilla's `military_station_small` ship size declares
`section_slots = { "west" = { locator = "part1" } "east" = { locator = "part2" } }`.
Vanilla's own station art bakes `part1`/`part2` into the `.mesh`. Walshicus'
stations bake nothing and their `.asset` declares only `root`, so the sections
have nowhere to attach.

## This is a different question from decision 26, and the names hide that

Both end in the word "locator" and they are not the same thing:

| | reads | asks about | failure |
|---|---|---|---|
| decision 26 / `check_asset_load_order` | `common/section_templates/` | gun mounts on a **section** entity | gun fires from the model origin |
| this one | `common/ship_sizes/` `section_slots` | attach points on a **hull** entity | the section never attaches at all |

Decision 26 deliberately excluded starbases and defence platforms from the
*weapon position* work — "no hull to spread guns along, so placing them would be
inventing." That carve-out still stands and is why the attach points added here
sit at `{ 0 0 0 }`: it is the convention every gun locator in these same files
already uses, and spreading them would be the inventing decision 26 declined.
The fix makes the attachment **resolve**; it does not pretend to place anything.

## Decision

Sixty-six `vendor.yml` patches — 22 shipsets × 3 entities
(`military_station_small` needs `part1`–`part2`, `military_station_large`
`part1`–`part8`, `ion_cannon` `part1`) — inserting the locators after the entity's
`name` line. A patch rather than an `src/` override because the change is three
lines in someone else's file and we have no wish to own 22 of them; `count: 1`
on every replacement means a source update that moves the anchor stops the build
instead of silently dropping the fix. None of the 66 entities uses `clone`, so
the declarations are honoured (decision 28).

`tools/validate.py` gains `check_section_attach_points`.

## The log named 2 of 66

One culture's small station, because that is the only starbase a three-minute run
drew. The other 65 are the same defect in art nobody looked at yet — the same
shape as the nine AI-only prescripted empires that could never produce a record.
Sweeping the rule rather than repairing the instances is what found them.

## Scope is calibration, not convenience

Over the station family — `military_station_*` and `ion_cannon` — vanilla
contributes **1** finding in ~350 entities against 66 from the vendored
shipsets. Over all 317 ship sizes with `section_slots` the ratio collapses to
**41 vanilla against 147 mod**, which is not a signal anyone can act on. Hence
`_STATION_SIZE`. Widening it means first establishing whether those 41 are
vanilla quirks or a mesh lookup this check resolves wrongly — it is a piece of
work, not a constant to edit.

## And the first cut of the check was confidently wrong

`pdxmesh = "X_mesh"` is a **declaration name, not a filename**. The real file is
named by `file = "….mesh"` in a `.gfx`, and a first pass that globbed for
`<name>.mesh` found nothing anywhere — so every entity looked like it was missing
every attach point, and it reported **1,279 findings, most of them vanilla's**.
A check that flags vanilla en masse is measuring itself, not the tree.
