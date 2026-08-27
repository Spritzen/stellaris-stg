# 05 — The two `interface/*.gui` merges are unnecessary

**Decided:** 2026-08-01, during Phase 0.
**Supersedes:** plan.md §4, which listed four files as needing a hand-written merge.

Two of the four are `interface/planet_view.gui` and `interface/game_setup/setup.gui`.
Neither needs a merge. UI Overhaul Dynamic wins both outright, on harvest order,
and writing the merges the plan called for would have made the mod worse.

## `interface/game_setup/setup.gui` — YAGEM vs UIOD

YAGEM's entire delta is two lines in `ai_empires_container`: `height` 153 → 612
and `max_slots_vertical` 3 → 12. It is solving one problem — vanilla's AI-empire
grid is too short once YAGEM's larger galaxies allow more empires.

UIOD solves the same problem structurally. Its container is
`size = { width = 570 height = -10 }` (fill the parent) with
`verticalScrollbar = "right_vertical_slider_thick"` and `smooth_scrolling = yes`,
and `max_slots_vertical` is **commented out** — no vertical cap at all, scroll
for as many as exist.

Transplanting YAGEM's literal values onto that would replace a fill-height
scrolling container with a fixed 612px one and re-impose a 12-row cap that UIOD
deliberately removed. Strictly worse, in service of a delta that no longer has
anything to fix.

## `interface/planet_view.gui` — PD - Planet View vs UIOD

PD's delta is 37 lines, self-annotated `#V<original>`, and almost all of it is
one systematic change: stretch vanilla's 680-high planet view to 832 and push
every dependent offset down by 152px, so PD's extra planet information fits.

UIOD's planet view is already `1220 × 940`, with `1000` and `1040` variants at
higher resolutions, built on its own variables (`@sidebar_list_height = 870`,
`@district_rows = 12`). It is **taller than the 832 PD was expanding to**, and
it is a different layout — PD's absolute pixel offsets are keyed to vanilla's
line-for-line structure and have no counterpart in UIOD's file.

The four non-layout lines in PD's delta settle it. PD's copy is **stale against
Stellaris 4.4**: it references `GFX_arkship_header_default` and the loc key
`ARKSHIP_BUTTON`, and *neither exists in 4.4* — vanilla has
`GFX_arkship_planetview_header_civilian` and `ARKSHIP_CONTROLS_BUTTON`. PD's
file predates a vanilla rename. Applying its delta would introduce a missing
sprite reference and a tooltip showing a raw key.

## Consequence

`src/` contains two merged files, not four:

- `src/common/planet_classes/00_planet_classes.txt`
- `src/common/traits/04_species_traits.txt`

Both `.gui` files are left to the vendored UIOD copies. If a future Stellaris
patch changes them, the thing to re-check is whether UIOD still covers what the
submods were compensating for — not whether to resurrect these merges.

## The general lesson

The plan sized these merges from *line counts* — a 74-line delta against an
8,963-line one reads like a small transplant onto a big base. Line count says
nothing about whether the base already solved the problem. Both deltas were
compensating for vanilla limitations that UIOD removes at the root, and in both
cases the smaller mod was the more out-of-date one. Diff the intent, not the
lines, before merging a UI file.
