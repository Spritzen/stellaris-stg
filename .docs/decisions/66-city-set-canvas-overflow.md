# 66 — A file taller than the canvas was scaled by two different factors

**Status:** decided, 2026-08-08
**The third and last door into** [decision 58](58-city-set-geometry.md)'s
symptom. 58 fixed the files smaller than STNH's canvas,
[63](63-city-set-family-targets.md) fixed the ones shadowing no vanilla path,
and this one fixes the ones **larger** than the canvas — which neither of them
looked at, because a file that already fills the canvas reads as the case with
nothing to do.

## The report

From the live Terran Empire run: *"Checked Terran planet view and the buildings
looked low."* Terran flies `city_graphical_culture = "humanoid_01"`, and
humanoid_01 turned out to be re-cut exactly right — so the report did not name
this defect. Sweeping the rule behind it did, on a different empire.

## The measurement

`fit: canvas` padded the file onto the source's own canvas and then hard-resized
to the target:

```python
cw, ch = max(canvas[0], dims[0]), max(canvas[1], dims[1])   # only ever grows
... "-extent", f"{cw}x{ch}", "-resize", f"{tw}x{th}!"
```

`max()` was written to protect a file bigger than the canvas from being cropped.
It does — and in doing so it hands `-resize !` a box whose aspect ratio is no
longer the canvas's, so x and y are scaled by different factors. **Ten files
overflow the 560×280 canvas vertically**, and the whole set belongs to three
prefixes:

| file | source | vertical squash |
|---|---|---|
| `vulcan_01_city_l06` | 560×367 | **×0.763** |
| `vulcan_01_city_l05` | 559×352 | **×0.795** |
| `vulcan_01_city_l04` | 560×300 | ×0.933 |
| `generic_05_city_l04` (+`_devastated`) | 560×307 | ×0.912 |
| `toxoid_01_city_l04` (+`_devastated`) | 560×307 | ×0.912 |
| `borg_01_city_l06` | 560×283 | ×0.989 |
| `generic_03_city_l01_devastated` | 560×283 | ×0.989 |
| `mammalian_01_city_l01_devastated` | 560×283 | ×0.989 |

`vulcan_01` is a **playable empire's** set — the Vulcan High Command names it —
and l04–l06 are the layers a developed capital actually draws. Its buildings
were flattened to three quarters of their height, which is the *same symptom
sentence* decisions 58 and 63 were reported with: buildings low and small,
backdrop behind them correct.

## Decision

Derive the pre-resize height from the canvas rather than from the file:

```python
cw = max(canvas[0], dims[0])
ch = round(canvas[1] * cw / canvas[0])
```

The box now always carries the canvas's aspect ratio, so `-resize !` is always a
uniform scale. Width still only ever grows: a crop there would cut art out of
the middle of the frame, where a crop in height cuts it off the top edge.

**Cropping the top is what the source mod itself draws.** The content in these
files is bottom-flush and the canvas is 560×280; anything above row 280
overflows STNH's own planet-view frame and is not visible in STNH either.
`vulcan_01_city_l06` loses 87 of its 367 rows, all of them sky and clifftop
above the frame.

The one file that looks like an overflow and is not is `solarpunk_01_city_l06`
at 1536×768 — a higher-resolution copy of the same 2:1 canvas, not art that
overflows it. The new arithmetic handles it without a special case: `cw = 1536`
gives `ch = 768`, so nothing is cropped and the scale stays uniform. That is the
test that says the rule is about the *aspect*, not about the size.

Result: 299 city layers at 800×400 as before, 0 of them scaled anisotropically,
where 10 were. `make validate` clean, 0 warnings.

## How this class of defect gets caught next time

**It cannot recur, and that is better than a check.**
`check_shadowed_texture_geometry` was structurally blind here and would have
stayed blind: it compares the *output* dimensions against vanilla's, and the
output was 800×400 the whole time — correct size, wrong picture. The defect
lived entirely inside the re-cut.

Adding a check that re-derived the plan and compared aspect ratios would be a
check that can no longer fail, since `ch` is now computed *from* `canvas[0]` and
`canvas[1]`. CLAUDE.md's rule — *a check that cannot fail is worse than an
absent one, because it reports a number* — says to remove the failure mode by
construction and say so, rather than to ship the number.

## The rule worth carrying

**A guard against one error can create its opposite.** `max()` was there
deliberately, with a comment saying so: *"a file already at or past the canvas
is left alone — `-extent` only ever grows here, never crops."* Losing pixels was
the risk being guarded against, and the guard traded it for a silent change of
aspect ratio, which loses no pixels and ruins the picture anyway. The comment
was accurate about what the code did and never asked what the code did *next*.

Second, and this is why the sweep happened at all: **the empire a report names
is a sample, not the population.** Terran's set was correct; the report was
still worth a sweep of every set in the directory, and the sweep is what found
Vulcan. That is `check_prescripted_empires`' lesson —
*derive the rule and sweep the tree* — applied to a report with no log record
behind it at all.
