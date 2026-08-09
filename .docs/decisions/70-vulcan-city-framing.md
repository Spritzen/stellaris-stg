# 70 — The Vulcan city is not cropped by us; the art is composed that way

**Status:** decided, 2026-08-08 — **reviewed and left alone.** No change made.
Follows [decision 58](58-city-set-geometry.md),
[63](63-city-set-family-targets.md) and
[66](66-city-set-canvas-overflow.md), the three passes that did change it.

## The report

From the Vulcan Confederacy run: *"Planet view on the capital. Buildings look
off, was the original image cut to scale? they should have been resampled to
the correct size, I say this because the right side of the image looks cut
off."*

A fair reading of the picture, and the right question to ask of a pipeline that
has now re-cut this art three times. The answer is that the horizontal axis is
the one axis nothing in the chain touches.

## Measured, end to end

**The pipeline never crops horizontally.** `fit: canvas` pads width and only
ever *grows* it (`cw = max(canvas_w, file_w)`); vulcan_01's layers are 248–560
wide against a 560 canvas, so the scale to 800 is a clean 10:7 with nothing cut.

**UIOD's frame does not crop it either.** `interface/planet_view.gui` draws
`GFX_portrait_planet` at `scale = 1.112` into a window of
`@portrait_window_width = 890` — and 800 × 1.112 = 889.6. The art is scaled to
fill the frame width **exactly**. (Vanilla's own planet view is the same idea
with different numbers: an 850×240 window with `clipping = yes` over the same
800×400 art, so both builds show a horizontal band and neither trims the sides.)

**What we do cut is the top, and it is empty sky.** vulcan_01 is the tallest
set in the tree — `l06` is 560×367 against the family's 560×280 canvas, the
overflow decision 66 chose to crop rather than squash. Rendering the full
560×367 stack beside the shipped 800×400 shows the removed 87 rows are sky and
nothing else. The framing is unchanged.

**So the sliced building is STNH's.** `vulcan_01_city_l06.dds` spans its 560-px
canvas with content touching both the left and right edges; the amphitheatre at
the right is cut in the source file. We cannot un-cut it.

## Two things the same look established, both worth keeping

- **64 of the 88 width-trimmed city layers are fully transparent.** `-gravity
  south` centres a trimmed layer horizontally, which would be wrong for any
  layer whose true x-offset was lost to the trim — and that was the live worry,
  since a city layer carries no declaration anywhere and its offset is baked
  into the texture. It does not bite: the small layers (`21×17`, `16×8`, `5×40`)
  are trims of *empty* images, and vulcan_01's `l04`/`l05`/`l06` are full
  560-wide files with transparent margins, so no real content is ever recentred.
  The 24 narrow layers that do carry content are all in prefixes no STG empire
  names. **If an empire is ever moved onto one of those prefixes, re-open this.**
- **Layer count is right.** Vanilla ships 6 `*_city_l0N` layers per prefix (26 of
  29 prefixes; 3 ship 5), and every STG prefix ships 6. An earlier reading of
  this as "short against 11" was the check comparing against a number vanilla
  does not use.

## What is left, and why it is not a defect

vulcan_01's buildings read larger relative to the frame than
`humanoid_01`'s or `klingon`'s. That is composition, not geometry: STNH drew
Vulcan as a close view down a canyon where it drew the others as skylines.
Changing it means letterboxing the set — scaling 560×367 into 800×400 to fit
rather than to fill, leaving transparent bands at the sides where every other
city set reaches the edge. That trades a framing preference for a visible seam,
so it is not taken.

## The rule worth carrying

**Establish which axis a symptom is on before believing the axis it names.**
"Cut off on the right" is a horizontal complaint about a picture whose only
lossy step is vertical. Three passes had already been made over this art on the
assumption that the reported symptom located the defect; here the report was
accurate about what it looked like and the geometry had to be measured
separately — pipeline, then GUI frame, then source file — to say which of the
three owned it. None of them was the one named.
