# 40 — Event pictures are re-cut to vanilla's dimensions at harvest

**Status:** decided, 2026-08-07

## The report

After the 2026-08-07 live run: *"an event popup had a backing image that was
scaled way bigger than the display panel."*

## Nothing was wrong with the UI overhaul

UIOD's `interface/eventwindow.gui` is internally consistent and it is the file in
the tree. It draws the picture at `scale = 1.5`:

| | |
|---|---|
| Vanilla event picture | 450 × 150 |
| × UIOD's `scale = 1.5` | **675 × 225** |
| UIOD's frame art (`gfx/ui_overhaul_qhd/eventwindow/event_frame.dds`) | **693 × 239** |

675 × 225 inside 693 × 239 is the design. The overhaul was working; it was being
handed the wrong art.

## What was actually wrong

**STNH replaces 569 of vanilla's 639 event picture paths with 620 × 264 art.**
`additive_only` only protects paths an earlier *source* claimed — it has never
protected vanilla, exactly as `vendor.yml` says above the STNH entry and as
[decision 07](07-stnh-art-shadows-vanilla.md) established. So:

| | |
|---|---|
| STNH event picture | 620 × 264 |
| × UIOD's `scale = 1.5` | **930 × 396** |
| against UIOD's frame | 693 × 239 |

34% too wide, 66% too tall. That is the popup.

Two of the 569 are far worse. `satellite_in_orbit.dds` and `space_debris.dds`
are replaced by **9315 × 264** animation strips — 15 frames of 621. Vanilla's
`interface/eventpictures.gfx` declares those sprites with no `noOfFrames`, so
the engine draws the whole strip: ~13,970 px across at scale 1.5.

A third consequence has nothing to do with the window at all. Vanilla pins **220
of these sprites to hardcoded `upper_left` / `lower_right` rects** in 450 × 150
space (`GFX_evt_satellite_in_orbit_zoom_1` and friends). Every one of them was
reading the wrong region of a re-dimensioned texture.

## Why nothing caught it

**Every name resolved.** The file existed, the sprite that declared it resolved,
the window that drew it resolved. `make validate` reported `ok — 23 warnings`
against the broken build, and so did the run before it. The whole cross-reference
family asks whether a reference *resolves*; not one of them asks whether the
thing it resolves to is still the **shape** the referrer was cut for.

`error.log` could not have shown it either. The engine loads a 620 × 264 texture
and draws it exactly as told. There is no defect from its point of view — 1,268
lines, all but one inside the init window, nothing about event pictures.

## The decision

**Re-cut at harvest, rather than drop the art or refit the window.**

`vendor.yml` gains `resample_to_vanilla:` on the STNH entry, and `tools/vendor.py`
re-cuts a matching file whenever vanilla ships one at the same path with
different dimensions. Three properties matter:

- **The target is read off vanilla, never written down.** It survives a game
  patch that re-cuts vanilla's own art, and it costs nothing for the 11 files
  that already match — those are copied byte-for-byte.
- **Centre crop to fill, verified against the art rather than assumed.** STNH's
  620 × 264 pictures are the same scenes vanilla ships at 450 × 150, re-rendered
  taller; a centre crop back to 3:1 recovers vanilla's framing almost exactly.
  Scaling to fit would letterbox inside UIOD's frame.
- **Written uncompressed.** That is vanilla's own format for most of these paths,
  it avoids a second lossy pass over the ~1/3 of STNH's that already ship DXT,
  and it sidesteps DXT's 4 × 4 blocks at widths like 450 that they do not divide.

Animation strips are frozen at frame 0. The frame width is the **divisor of the
strip width nearest the source's own modal still width**, derived from the corpus
rather than asserted: guessing it from the aspect ratio picks 828 for the
20-frame strips (3.13∶1 is a plausible picture) and silently bleeds frame 1 into
the crop. Both extractions were checked by eye before the rule was kept.

### Alternatives rejected

- **Drop STNH's event pictures.** One line, and UIOD would render correctly — but
  it trades away the Trek art, which is the point of the mod.
- **Refit `eventwindow.gui` in `src/`.** The frame, shadow and stripes are fixed
  693 × 239 art, so fitting 620 × 264 means either letterboxing with visible gaps
  or hiding the chrome the way STNH's own `eventwindow.gui` does — it pushes all
  three to `x = -9990`. That discards the overhaul, and it fixes neither the 220
  crop rects nor the two strips.
- **Generate into `src/`,** as `tools/gen_shipsets.py` and the other generators
  do. Those emit text. 569 uncompressed DDS is ~154 MB into a tracked directory
  currently holding 3.7 MB. The build tree is gitignored and rebuildable; this
  belongs there.

## Cost

~5 s on `make vendor` (569 ImageMagick invocations inside the existing thread
pool, on a 35 s build). No cache: not worth the second thing to reason about.

## The check

`check_shadowed_texture_geometry` in `tools/validate.py`, scoped to
`gfx/event_pictures`.

**The scope is a calibration result.** Over the whole tree the same rule reports
**865 findings and almost all of them are by design**:

| Directory | Findings | What they are |
|---|---|---|
| `gfx/loadingscreens` | 20 / 20 | deliberate 2× HD upscale |
| `gfx/models` | 4 | UV-mapped, resolution-independent |
| `gfx/interface` | 99 | 92 are UIOD resizing vanilla UI art **while shipping the `.gui` that lays it out** — a reskin, not a defect |
| `gfx/portraits` | 173 | STNH planet and city art, drawn scaled to the panel |
| `gfx/event_pictures` | **569** | **all real** |

`gfx/event_pictures` is the one directory where the dimensions are load-bearing
and *not* owned by whoever swaps the art. 569 true findings against 0 vanilla
false positives; 0 after the re-cut. Widening it means making that case for
another directory, which is why the scope is a constant with the ratio next to
it — the same reasoning as `check_section_attach_points` (CLAUDE.md, and
[decision 33](33-station-section-attach-points.md)).

**A check that has never failed is worse than an absent one**, so this one was
calibrated on both sides: the pre-fix files were copied back over the tree and it
named both `acquire_asset.dds` (620 × 264) and `space_debris.dds` (9315 × 264)
before the build was restored.

One rule was tried and thrown away. *"A sprite's crop rect must lie inside its
texture"* sounds like the sharper check and has a clean vanilla baseline — 0
against itself. It scores **0 against the broken build too**: a 450 × 150 rect
sits comfortably *inside* a 620 × 264 texture. Wrong region, not out of bounds.
It could not have failed, so it was not kept.

## Still open, deliberately not touched

- **834 STNH event pictures render nowhere.** They are unique to STNH (no vanilla
  path), and the file that declares them, `interface/STH_event_pictures.gfx`,
  lives in STNH's `interface/` — which the harvest never takes, by design. They
  are inert bytes in the tree and the raw material for a Phase 3 that wants Trek
  art on Trek events. Untouched here: they are not what broke, and harvesting
  that one `.gfx` would drag STNH's 3.12-era `interface/` question open with it.
- **153 files under `gfx/portraits/city_sets`** change dimensions the same way,
  some to 21 × 17 from vanilla's 800 × 400. Drawn scaled to the planet panel
  rather than at native size, so the failure mode is different and possibly
  nothing. Not measured against a live run; worth a look when someone is next in
  the planet view.
