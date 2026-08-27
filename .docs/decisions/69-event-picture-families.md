# 69 — `gfx/event_pictures` is two families, and reading it as one left 865 pictures unasked

**Status:** decided, 2026-08-09
**Follows:** [40](40-event-picture-geometry.md), [55](55-city-set-geometry.md), [60](60-city-set-family-targets.md)

## Why this came up

Phase 4 wants Trek art on Trek events, and the art is already in `.source/`:
STNH ships about 1,430 event pictures and the clutter closure pruned **805** of
them from every build, because STNH declares them in
`interface/STH_event_pictures.gfx` and the harvest never takes STNH's
`interface/` ([decision 40](40-event-picture-geometry.md) predicted exactly
this, and called them "the raw material for a Phase 3 that wants Trek art on
Trek events").

Declaring one is a two-line `.gfx` entry. Declaring one **also puts a 620×264
texture into a window cut for 450×150**, which is decision 40's defect, in
decision 40's own directory, waiting behind the first sprite anybody writes.

## The measurement that was wrong, and how

`resample_to_vanilla:` had `gfx/event_pictures/*.dds` with the default
`target: path`: re-cut a file only where **vanilla ships one at the same path**.
That covers the 569 STNH pictures that shadow vanilla and is structurally blind
to the 865 that shadow nothing — every picture a Trek event would want.

`target: family` is the lever [decision 60](60-city-set-family-targets.md) built
for exactly this, and both the build and the check had already refused it here,
in the same words:

> `gfx/event_pictures` is deliberately absent — 580 of its 639 are 450×150 and
> the other 59 are a genuine second size, so it has no single family answer.

**That sentence is true of the directory and false of both families in it.**
The 59 are not scattered stragglers. They are `gfx/event_pictures/origins/`,
vanilla's origin pictures, **59 of 59 at 220×115**, and the top level is **580
of 580 at 450×150**. One glob measured across both reads 90.8% uniform — a hair
over the 0.90 floor, and one game patch from silently falling under it. Split,
each family is 100%.

Re-measure either with:

```bash
find /stellaris/gfx/event_pictures -maxdepth 1 -name '*.dds' \
  -exec identify -format '%wx%h\n' {} + | sort | uniq -c
find /stellaris/gfx/event_pictures/origins -name '*.dds' \
  -exec identify -format '%wx%h\n' {} + | sort | uniq -c
```

## The decision

**Two rules, ordered, both `target: family`.**

```yaml
- glob: "gfx/event_pictures/origins/*.dds"
  target: family
- glob: "gfx/event_pictures/*.dds"
  target: family
```

**Order is load-bearing and it is not obvious.** `fnmatch`'s `*` spans `/`, so
the broad glob matches `origins/` too; the narrower rule has to come first or it
never sees a file.

That ordering only helps if the *family measurement* obeys it too, so
`vanilla_families()` in `tools/vendor.py` now attributes each vanilla file to
**the first rule whose glob matches it** — the same first-match rule
`resample_plan()` already applied to the source's files. Before, the two halves
disagreed about what a family was: the broad glob's histogram silently included
the origin pictures. `tools/validate.py` mirrors it, with the families as globs
relative to the directory rather than bare basenames, so the same two-family
split is expressible in both places.

## What it cost and what it bought

| | |
|---|---|
| Files re-cut at harvest | 722 → **1,661** |
| `make vendor` | 75 s, from ~35 s |
| Prune count | 959 → **935** — the 24 pictures the first `.gfx` named came back by themselves, with no edit to `vendor.yml` |
| `make validate` | 0 errors, 0 warnings, before and after |

**The build re-cuts ~800 pictures it then prunes**, which is the honest cost of
the simple rule: the resample plan runs at harvest and the closure runs after
the merge. It is about seven seconds and it means a picture is correctly sized
the moment somebody declares it, rather than the build after.

Nine of the ~30 STNH-unique pictures that were *already* in the tree — kept by
the closure because a star name matched their basename — were **9315×264
animation strips**. They render nowhere, because nothing declares them, so this
was latent rather than live; they are all 450×150 now, frozen at frame 0 by the
strip rule decision 40 already had.

## The check

`check_shadowed_texture_geometry` gains `gfx/event_pictures` in
`_GEOMETRY_FAMILIES`, as `("origins/*.dds", "*.dds")`.

**Calibrated on both sides, and on both families separately**, because a
two-family split has a failure mode a one-family one does not — each family
accepting the other's size:

| Probe | Result |
|---|---|
| A 620×264 file at a path vanilla does not ship | **reported** against 450×150 |
| A 220×115 file in `origins/` | silent — that is that family's own size |
| A 450×150 file in `origins/` | **reported** against 220×115 |
| The build as it stands | 0 findings over 1,287 examined |

The frame-0 extractions were checked by eye before the rule was kept, as
decision 40's were: twelve strips rendered to PNG and looked at. All twelve are
legible stills of the scene the filename names.

## What this does not settle

**Whether STNH's pictures are framed for a 3∶1 crop.** Decision 40 verified that
for the 569 that shadow a vanilla path, by comparing them against the vanilla
scene they replace. The 865 that shadow nothing have no such control — a centre
crop of 620×264 to 450×150 loses 21 px top and bottom, and nothing on disk says
whether the artist put anything there. Twelve looked right. That is a sample,
and it is eyes-only, so it belongs in
[open questions](../planning/open-questions.md).
