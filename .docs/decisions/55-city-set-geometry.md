# 55 — STNH's city layers are a 560×280 canvas in an 800×400 planet view

**Status:** decided, 2026-08-08
**The same defect as** [decision 40](40-event-picture-geometry.md), one
directory over, found the same way — by a live run reporting that a picture was
the wrong size while `make validate` said `ok`.

## The report

*"Infrastructure screen; the city structure art looks too low, it might be a
scaling issue — it was that way on all planets, backdrop art looks correct as in
the planetary art behind the building art."*

## The measurement

`gfx/portraits/city_sets/` holds two families and vanilla is exact about both:

| | vanilla | built tree, before |
|---|---|---|
| `*_room.dds` | 91 of 91 at **952×340** | 316 of 324 at 952×340 |
| `*_city_l0N.dds` | 266 of 266 at **800×400** | 97 at 560×280, 44 at 800×400, a long tail |

**153 files shadow a vanilla path at the wrong dimensions, and all 153 are
STNH's.** 560×280 is exactly 70% of 800×400, and it is the canvas STNH's own
`interface/` was cut for — which STG never vendors, because plan.md §3 takes
STNH's art and not its script.

That STNH honours the *room* canvas and not the *city* one is the calibration:
this is not a mod that ignores canvases, it is a mod whose planet view is a
different size from the one we ship.

**The backdrop was right the whole time for a reason worth keeping.**
`gfx/portraits/environments/*_sky.dds` is one of the 121 contested paths
`additive_only` makes STNH lose to Planetary Diversity, UIOD and Real Space
(plan.md §3). Only the half of the planet view that nobody else claims was ever
wrong — so the user's "backdrop correct, buildings wrong" is the harvest rule
drawing the line, not a coincidence.

## Why the layers cannot simply be stretched

A city layer is composited by **exact pixel position**. Vanilla's own content
sits at a different offset in every layer of a set:

```
humanoid_01_city_l01   content 136×54  at +360+205   on 800×400
humanoid_01_city_l03   content 547×144 at  +84+205
humanoid_01_city_l04   content 635×328 at +165+72
humanoid_01_city_l06   content 800×328 at   +0+72
```

So the canvas is load-bearing, and 41 of STNH's files are that canvas
**top-trimmed** — 560×224, 560×266, 561×234 — every one of them with its content
ending flush at the bottom edge. Nothing is trimmed off the bottom, and the
width stays 560.

## Decision

Re-cut them with `resample_to_vanilla:`, which already existed for decision 40,
plus a second fit mode:

```yaml
resample_to_vanilla:
  - "gfx/event_pictures/*.dds"
  - glob: "gfx/portraits/city_sets/*.dds"
    fit: canvas
```

`fit: crop` (the default, and what the event pictures have always had) crops to
fill at centre gravity. `fit: canvas` pads the file back onto the source mod's
own canvas first — **bottom-aligned**, transparent fill — and only then scales
to vanilla's dimensions. On this corpus that is lossless in geometry: 59 files
are already the full 560×280 and scale 10:7 exactly, 41 get their trimmed rows
back before scaling, 36 are fully transparent blanks, and 17 are odd sizes that
take the same rule.

**Crop-to-fill would have been wrong here**, and visibly: a 560×224 layer
scaled to fill 800×400 is scaled to 1000×400 and then cut back, losing 20% of
the width of every trimmed layer.

The canvas is **derived, not written down** — the modal dimensions of the files
that pattern matched, taken from the source itself, exactly as the target is
read off vanilla. Both halves survive a resync and a game patch.

Result: 157 shadowed city textures, **0 mismatched**, and the content's relative
position is preserved to the pixel (`humanoid_01_city_l01` had its content at
190/560 = 0.339 of the width and flush to the bottom; it now sits at 271/800 =
0.339, flush to the bottom).

## What this does NOT fix

STNH's own Trek city prefixes — `klingon`, `vulcan_01`, `cardassian_01`,
`borg_01`, `tholian_01`, `undine_01` — shadow no vanilla path, so
`resample_to_vanilla` has nothing to read a target off and leaves them alone.
Their art-bearing layers (`l04`–`l06`) are on the same 560×280 canvas and their
`l01`–`l03` are fully transparent blanks at odd sizes, so the six empires named
by [decision 47](47-flags-city-sets.md) should still show cities at 70%. Fixing
them means asserting 800×400 rather than reading it, which is the one thing
decision 40 refused to do — so it waits for a live run to confirm the symptom
survives on exactly those six and nowhere else.

## How this class of defect gets caught next time

`check_shadowed_texture_geometry` gained `gfx/portraits/city_sets` as its second
directory, with its own calibration written beside it: **153 findings against 0
vanilla false positives, 0 after the re-cut.** The scope is still a constant
with a ratio next to it, because over the whole tree the same rule reports 865
findings and almost all of them are deliberate reskins.
