# 81 — Vulcan's skyline filled 325 of 400 rows against a family median of 289, and the fix is a resample, not a crop

**Status:** decided, 2026-08-24
**Falsifies** the 2026-08-08 review of this art, which measured it three ways
and left it alone.
**Supersedes** [decision 63](63-city-set-canvas-overflow.md)'s treatment of the
overflow: the crop it chose is what produced the symptom.

## The report

From the 2026-08-24 Vulcan run: *"Vulcan city screen — the city picture is
scaled incorrectly, this must be addressed."*

The third time this art has been reported and the first time it has been fixed.
The same complaint was reviewed on 2026-08-08: that pass measured the pipeline, the GUI frame and the source file, found no
crop on the axis the report named, and concluded the composition was STNH's and
not ours. **That reasoning was sound and its conclusion was wrong**, because all
three measurements were of the horizontal axis and of the canvas — and the
defect is vertical and in the content.

## The measurement that had not been made

A planet view's apparent scale is set by its **horizon layer** (`*_city_l06`):
how many of the canvas's 400 rows the skyline fills. Measured across the merged
tree, non-opaque layers only:

| | content rows | top edge |
|---|---|---|
| `humanoid_01` | 291 | +109 |
| `klingon` | 289 | +111 |
| `tholian_01` | 288 | +112 |
| `borg_01` | 286 | +114 |
| **merged-tree median** | **289** | |
| `undine_01` | 311 | +89 |
| `molluscoid_01` | 314 | +86 |
| `aquatic_01` | 316 | +84 |
| **`vulcan_01`** | **325** | **+75** |
| `nemesis_01` | 328 | +72 |
| `pd_federation_builders_01` | 331 | +69 |

**It is not merely large, it is clipped.** UIOD's `interface/planet_view.gui`
draws `GFX_portrait_planet` at `scale = 1.112` at `y = -120` into a window
276 rows tall, which shows source rows **108 to 356** of the 400. A skyline
whose top edge is at +109 meets the top of that window exactly; vulcan_01's is
at +75, so its top 33 rows were cut off by the frame. That is the reported
symptom, and it sits on the axis that review ruled out.

## Why no `fit:` mode could reach it

The obvious repair — pad to the source's own 560×367 frame instead of cropping
to the 560×280 family canvas — does not work, and the reason is worth keeping.

**STNH composed vulcan_01 with a different content-to-frame ratio than the
family has.** Its source horizon is 560×367 with content filling 227 rows —
**62%** of the frame, where the sets it sits beside fill **72%**. So:

| treatment | content rows in 800×400 | |
|---|---|---|
| pad to 560×367, scale (`fit: canvas` as written) | 247 | too short — the "flat and low" look [decision 63](63-city-set-canvas-overflow.md) removed |
| crop to 560×280, scale (`fit: canvas` as shipped) | 325 | too tall — this report |
| **family band** | **289** | |

**No choice of canvas lands in the band, because the ratio itself differs.**
`fit: crop` and `fit: canvas` both preserve the source's content-to-canvas
ratio; the thing that is wrong here *is* that ratio. Only rescaling the content
reaches it, so the target has to be read off the **content box** rather than off
the canvas — which is a third kind of rule, not a third `fit:` value.

## Decision

A new `normalize_city_scale:` rule in `vendor.yml`, running over the **merged
tree** after every source, `src/`, patch and rename has landed:

```yaml
normalize_city_scale:
  glob: "gfx/portraits/city_sets/*_city_l0*.dds"
  horizon: "_city_l06"
  tolerance: 0.10
```

For any set whose horizon exceeds the median by more than the tolerance, every
layer of that set is scaled on the **vertical axis only** by `median / actual`
and padded back onto its own 800×400 canvas **bottom-aligned**.

**Nothing is cropped.** Every pixel of the source survives; the transparent rows
added at the top are sky the environment backdrop draws anyway. The full 800-px
width is kept, so the horizon still reaches both edges — the transparent side
bands that letterboxing would leave are the seam the 2026-08-08 review
refused, and refusing it was right.

The cost is a **10.5% vertical compression** of Vulcan's buildings, and it is
the whole cost. It is taken deliberately: the alternative that preserves aspect
exactly is the side-band seam, and the alternative that preserves the source
ratio is a skyline the window cuts the top off.

### The median is measured against the merged tree, not vanilla

This looks like a mistake and is not. **Vanilla's own `humanoid_01` horizon is
328 rows at +72** — indistinguishable from vulcan_01's 325, and it would have
made vulcan_01 look perfectly in family. But the built tree's `humanoid_01` is
**STNH's**, at 291, because STNH shadows the vanilla path
([decision 07](07-stnh-art-shadows-vanilla.md)). Every Trek set sits beside
STNH's art, never beside Paradox's. **The band a player actually sees is the one
to measure against**, and reading this target off vanilla — the reflex every
other rule in `resample_to_vanilla:` correctly follows — would have found
nothing wrong.

### Calibration

Median 289, ceiling 318. Three sets are above it and were re-scaled: `vulcan_01`
(325 → 289), `nemesis_01` (328 → 289), `pd_federation_builders_01` (331 → 289).
The nearest thing to a false positive is `aquatic_01` at 316, an ordinary
vanilla set in ordinary use, and it clears with 2 rows to spare; `molluscoid_01`
(314) and `undine_01` (311) are both named by STG empires and both read fine in
the run.

**The rule sweeps the directory rather than the ten sets an STG empire names
today**, because a city set becomes offerable the moment a
`city_graphical_culture` points at it — scoping the fix to current users would
leave the same defect waiting behind the next empire that adopts one
([live-runs.md](../guides/live-runs.md#a-screen-nobody-opened-is-a-check-that-never-ran)).

Layers whose content fills the entire canvas are skipped **by kind, not by
name**: they are opaque backdrop art rather than a skyline and have no band to
sit inside. `cardassian_01` is one of them.

## The result

```
vulcan_01_city_l06   800x290 at +0+110     (humanoid_01: 800x291 at +0+109)
vulcan_01_city_l04   385x191 at +104+209   (humanoid_01: 398x190 at +105+210)
vulcan_01_city_l05   331x192 at +344+208
```

**`l04` landing on 191 rows against humanoid_01's 190 is the independent check.**
The factor was derived from `l06` alone and applied blind to the rest of the set;
that `l04` then matches the family to within one row says the whole set was
uniformly oversized by one factor, which is exactly what a frame-ratio mismatch
predicts and what a composition difference would not.

## What this does not fix

**None of STNH's six Trek city sets ships `_devastated` layers.** Every vanilla
set has five (`humanoid_01`, `avian_01`, `reptilian_01`, `molluscoid_01`, …);
`vulcan_01`, `klingon`, `cardassian_01`, `borg_01`, `tholian_01` and `undine_01`
have none. The engine composites these by naming convention with no `.gfx` or
`.gui` declaration anywhere, so nothing in the tree references them and no check
can ask for them — and no run has yet devastated a Trek homeworld to find out
whether the engine falls back or draws nothing.

That is the one element UIOD genuinely does not cover, and it is a **content**
gap rather than a wiring one: city sets have no interface-side hook at all, so
there is nothing to declare for a new set. UIOD's only contribution is the window
geometry, which is global and which the re-scaled art now matches.
[Open questions](../planning/open-questions.md) carries it.
