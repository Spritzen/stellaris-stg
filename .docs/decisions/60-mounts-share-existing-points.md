# 60 — A missing mount shares a point the artist drew

**Status:** decided, 2026-08-08
**Narrows** [decision 28](28-weapon-locator-positions.md), which gave every
unplaced mount a position spread through the mesh's bounding box. That was right
where the mesh said nothing and wrong wherever it had already answered.

## The report

From the 2026-08-08 live run, on a Starfleet TNG corvette: *"the first 2 mounts
seemed good placement, the 3rd is plausibly in place and so it's possibly not a
bug but worth double checking."*

It was not a bug and it was not the artist's either. Read out of
`starfleet_tng_corvette.mesh`:

```
small_gun_01   (0.000,  1.407, -6.376)   baked by the artist
small_gun_02   (0.000,  0.933, -6.229)   baked by the artist
small_gun_03   (2.480,  0.586, -1.805)   decision 28's bounding-box spread
```

Both of the artist's mounts are on the **centreline at the bow** — the forward
phaser strip, which is what a Trek ship's guns look like. Decision 28's third
one is starboard and amidships, inside the hull and entirely plausible, and
visibly not part of the pattern. The user spotted it by eye with no log record
anywhere, which is the same class of finding as decisions 42 and 48.

## Decision

**Where a mount has no position of its own, give it one that somebody drew.**
Three tiers, in order, in `tools/fix_ship_locators.py`:

1. **The section's own placed mounts.** Round-robin over them, sorted, so two
   missing mounts over two anchors land on different points rather than
   stacking. The corvette's `small_gun_03` now sits exactly on `small_gun_01`.
2. **Any other hardpoint the same mesh bakes** — a torpedo tube, a medium gun —
   when the section itself has nothing placed. The vocabulary of what counts as
   a hardpoint is **derived from vanilla**: the union of every `locatorname` its
   `common/section_templates/` name, 201 of them, so `target_locator_01` is
   excluded because it is an aim point that no template mounts anything on.
3. **The bounding-box spread**, unchanged, and only where the mesh bakes no
   hardpoint at all.

**Exact co-location, not a nudge.** A nudged position is a guessed position,
which is the thing this replaces. Two turrets on one point is a cosmetic cost;
a turret somewhere nobody drew is the defect.

**The tiers do not mix.** Doubling up on the section's own mounts beats
borrowing another template's, so tier 1 is used alone whenever it is non-empty.

## The sweep

Re-derived across all 27 shipsets — the whole population, per decision 28's own
rule that the defect is in the art and each empire reaches a different set of it.
**157 `src/` overrides, 1,626 mounts placed, 125 added, 54 bare declarations
dropped, 0 unplaceable.**

| Where the position comes from | mounts | |
|---|---|---|
| the section's own placed mounts | 165 | 9% |
| another hardpoint on the same mesh | 434 | 25% |
| the bounding-box spread | 1,152 | 66% |

**599 of 1,751 now sit on a point the artist drew, against 0 before.** Two
thirds still do not, and that is the art rather than the rule: most of these
sections bake no locator at all, which is the defect decision 28 was written
for in the first place.

Checked afterwards: **0 of 1,755 placed mounts fall outside the bounding box of
the mesh they were taken from.** (A first pass reported 10, all of them
comparing an artist's own baked position against `section_bbox`'s *largest*
candidate mesh rather than the one that owns the locator — the check was
approximate, the placements were not.)

## Two things this turned up that were not the subject

- **`strip_generated_header` was anchored on a sentence.** It cut the generated
  header at `# See .docs/decisions/28-...md.\n\n`, so the moment the header
  gained a second decision link it would have matched nothing and stacked a
  fresh header onto all 157 overrides on the next run. It now cuts at the first
  blank line, which is a landmark the wording cannot move.
- **`provenance()` read the wrong table.** It took the first row in
  `.docs/provenance.md` mentioning the shipset directory, and `## Patched files`
  — three columns, `| File | Source | Why |` — sits above `## Every file`, which
  is the two-column one it wants. Once [decision 35](35-station-section-attach-points.md)
  added 66 station patches, every Walshicus set's `src/` header was written with
  a patch rationale where the mod name belongs. It had read as correct for as
  long as no patch touched those directories.

**A re-derivation is not a re-run.** `make vendor` copies `src/` into the built
tree, and this tool reads the built tree — so running it again after a vendor
finds every mount already placed and writes *nothing*, which is indistinguishable
in the output from having no work to do. The generated overrides have to be
deleted and the tree re-vendored first. The procedure is in the module docstring,
because it cost a confusing pass to notice.
