# 28 — `clone` discards every locator declared beside it

**Date:** 2026-08-07
**Status:** accepted
**Extends:** [26 — Weapon locators](26-weapon-locator-positions.md), whose repair
was correct about *what* to declare and wrong about *where* it could be declared.

## The report

The 2026-08-07 live run threw **1,383** records against the nine cultures
`zz_stg_shipsets.asset` declares:

| source | records |
|---|---|
| `ship_design_templates.cpp:405` — section template × entity missing a locator | 877 |
| `section.cpp:311` — section entity missing a required locator | 506 |

The 506 is the *same number decision 26 measured before its repair*. The repair
moved `make validate`'s tracked count 676 → 0 and moved the engine's count not
at all.

## What is actually true

`clone` is a whole-entity copy applied **after** the block is read. Anything else
in that block is discarded, locators included. The entity ends up with exactly
the donor's mounts and none of the ones written beside the `clone`.

Three measurements, all against the merged tree and that run's log:

- Of the 173 entities the engine named, **173 were `clone`-plus-`locator` blocks
  and 0 came from anywhere else.**
- For all 173, the locators reported missing were **exactly** the ones declared
  beside the `clone`.
- Vanilla never writes the two together: **0 of 8,429** entity declarations,
  against 210 that clone and 2,160 that declare locators.

Decision 26 remains right that an `.asset` declaration satisfies the engine —
vanilla places 59 section entities' gun mounts that way and none is reported.
The qualifier it was missing is *in an entity that does not also say `clone`*.

## Consequence

**Where a generated entity needs a mount its donor lacks, copy the donor's
declaration out instead of cloning it.** `Emitter.expand` in
`tools/gen_shipsets.py` does this: 256 donors reproduced verbatim under the new
name, plus the placed mounts. It is behaviour-preserving — `clone` would have
produced that same body — and it costs 180 KB in one file, against vanilla's
largest ship `.asset` at 754 KB. The 392 entities that need no extra locators
still clone, which is both smaller and clearer about intent.

`clone` itself is not the problem and decision 16's load-order rule still binds:
the donor must sort earlier, which is why the file is named to sort last.

Two things fell out of doing it:

- **Reading only the mesh binary to decide what a donor already carries was
  wrong in both directions.** It claimed 79 sections were short of mounts their
  donor's `.asset` declares perfectly well, and it counted a donor declaration
  at `{ 0 0 0 }` as a mount when that is decision 26's silent defect. `has_mounts`
  now asks both, and treats *placed* rather than *present* as the question.
- **STNH writes half its locators over four lines and vanilla writes them on
  one.** A line-oriented regex sees only one form; it duplicated 29 mounts before
  `_locator_spans` became a brace-matched scanner.

Three cases remain where a donor declares a required mount at the origin over a
position its mesh bakes — decision 26's unresolved SHADOWED class. They are
unchanged by this and are not made worse: `clone` inherited the same declaration.

## What this says about the checks

`make validate` reported `0` for exactly this, and **could not have reported
anything else**: it read the locators out of the same block as the `clone` and
credited them. Its subject was 252 dead declarations.

That is the third time the rule at the top of CLAUDE.md has paid out — *a check
that cannot fail is worse than an absent one, because it reports a number* — and
the first time the check had been calibrated and still went blind, because the
calibration ran before the repair that invalidated it. **A check calibrated
against one shape of the data is not calibrated against the shape the repair
leaves behind.** Recalibrate on the far side of the fix, not only the near side.

`check_asset_load_order` now raises a hard error on `clone` beside `locator`
rather than silently counting it, and `locs` is empty for a cloning entity so the
placement half cannot be fooled either. Calibrated by probe: the error fires,
and the tree is otherwise clean of the pattern — 0 occurrences across vanilla and
all 48 vendored sources.
