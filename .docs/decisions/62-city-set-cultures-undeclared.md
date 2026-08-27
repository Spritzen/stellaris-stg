# 62 — Five city sets with complete art and no declaration: the designer hid the empires

**Resolved 2026-08-08**, from the Klingon live run of the same day.
**Corrected in part by [decision 88](88-playable-gates-the-design-database.md),
2026-08-25:** the reasoning below rests on `stg_minor_undine_vanguard` being
`playable = stg_never` and therefore beyond the empire designer's reach. That
gate is gone from all 79 minor powers, so the empire *does* reach the designer
now and a log **can** name it. The defect the sweep found, and the fix, are
unaffected.

## The report

`error.log` was 187 KB / 1,267 lines, startup 50.0 s (15:05:07–15:05:57).
**1,261 of those lines fall inside the startup window.** Six do not, and four of
them are one finding:

```
[15:06:00][select_empire_design_view.cpp:714]: Hiding invalid prescripted empire design 'stg_confederacy_of_vulcan':
[15:06:00][select_empire_design_view.cpp:719]:     City & Room:
    EMPIRE_DESIGN_INVALID_GFX_CULTURE
[15:06:00][select_empire_design_view.cpp:714]: Hiding invalid prescripted empire design 'stg_cardassian_union':
[15:06:00][select_empire_design_view.cpp:714]: Hiding invalid prescripted empire design 'stg_tholian_assembly':
[15:06:00][select_empire_design_view.cpp:714]: Hiding invalid prescripted empire design 'stg_borg_collective':
```

The engine prints the reason once and the following three empires bare, which is
worth noting only so the next reader does not conclude the other three failed for
a different reason.

The sixth line is `planet.cpp:2058`, the acked standing cost of
[decision 43](43-planet-scale-system-length.md) — one line, post-init,
non-recurring, exactly the shape that decision closes on. Not a new finding.

## What was wrong

`common/graphical_culture/` is **one database holding two kinds of thing**:
shipset cultures and city-set-only cultures. Vanilla declares `humanoid_01`,
`lithoid_01`, `avian_01` there beside `mammalian_01` — the values that appear in
`city_graphical_culture`, not just the ones that appear in `graphical_culture`.

Five STNH city sets ship **complete art** — six layers each in
`gfx/portraits/city_sets/`, `<name>_city_l01.dds` through `l06` — under keys that
**no entry in that database declared**, in the built tree or in vanilla:

| empire | `city_graphical_culture` | art | declared | in the picker |
|---|---|---|---|---|
| `stg_confederacy_of_vulcan` | `vulcan_01` | 6 layers | **no** | hidden |
| `stg_cardassian_union` | `cardassian_01` | 6 layers | **no** | hidden |
| `stg_tholian_assembly` | `tholian_01` | 6 layers | **no** | hidden |
| `stg_borg_collective` | `borg_01` | 6 layers | **no** | hidden |
| `stg_minor_undine_vanguard` | `undine_01` | 6 layers | **no** | *never reaches it* |

The shipset side was fine throughout: `vulcan`, `cardassian`, `tholian`, `borg`
are each declared by their own vendored `*_graphical_culture.txt`. So was the
room side — [decision 48](48-room-selector-merge.md)'s `room_selector` offers
`vulcan_room`, `cardassian_room`, `lithoid_room` and `borg_room`, and all four
textures exist. **Only the city culture declaration was missing**, and the
designer's "City & Room" tab validates all three together, which is why the
message names a tab that was two-thirds correct.

## Why nothing caught it, and the rule that generalises

`check_room_references` already asked whether a `city_graphical_culture` has a
`<name>_city_l01.dds` behind it — question 5, calibrated at 0 of vanilla's 4.
**All five passed it.** The art is there. The art was never the problem.

This is [decision 34](34-src-shadows-drop-source-declarations.md)'s rule in a new
database: *"declared somewhere" is not "declared where the engine looks"* —
inverted, because here the thing that resolved was the **file** and the thing
that was missing was the **declaration**. A city set needs both, and the check
that asked for one read as though it had asked for both. Nothing dangles: the
bare name finds its `.dds` exactly as vanilla's comment promises, so the load
path is silent and the refusal happens later, in a screen, at empire-design time.

**And the log is a sample, not a census** — CLAUDE.md's rule, earned again.
Sweeping the *rule* rather than repairing the four the log named turned up a
fifth, `stg_minor_undine_vanguard`, which is `playable = stg_never`. An AI-only
empire never reaches the empire designer, so `select_empire_design_view.cpp`
never validates it and **no log will ever name it.** It had the same defect the
whole time.

## The fix

`src/common/graphical_culture/stg_city_set_cultures.txt` declares all five.
It is a new file, not a shadow: the keys exist nowhere else, so the merge is
purely additive and no FIOS/LIOS question arises.

The shape is vanilla's own for a city-only culture (`solarpunk_01`,
`industrial_01` in `00_graphical_culture.txt`) and the vendored
`pd_city_set_cultures.txt`'s: a `fallback` plus `ship_selection_weight = { base
= 0 }`, which keeps a culture that exists only to dress planets out of ship
selection entirely. `fallback = mammalian_01` for the same reason
`stg_graphical_culture.txt` uses it —
[decision 17](17-stnh-shipsets-on-a-vanilla-chassis.md).

Keys are unprefixed, exception 2 of CLAUDE.md's prefix rule: the engine finds a
city set as `<key>_city_l01.dds`, so the key is the vendored art's to choose.
[Decision 10](10-species-class-keys-unprefixed.md).

**It is not in `stg_graphical_culture.txt`** because that file is generated by
`tools/gen_shipsets.py`. The generator writes exactly that one path and does not
own the directory, so a sibling file is safe.

## The check

`check_room_references` gains question 6: a `city_graphical_culture` that no
`common/graphical_culture/` entry declares. It is deliberately **separate from
question 5** rather than folded into it — the two failures are independent, and
one file's worth of art passing the first is precisely what hid the second.

`_declared_graphical_cultures()` models shadowing rather than unioning the two
trees: a build file replaces the vanilla file of the same **name**, so vanilla's
declarations survive only from files the build does not replace. The build ships
neither of vanilla's two filenames today. Modelling it anyway is what keeps the
check correct the day it does.

Calibration, both directions:

- **Vanilla floor:** 0 undeclared of 53 `city_graphical_culture` references
  across vanilla's own prescripted countries. No false-positive pressure.
- **By reverting:** run against the pre-fix build it reports exactly the 5, and
  nothing else in the tree. After `make vendor` it reports 0 and `make validate`
  is `ok — 0 warning(s)`.

Reported as a `warn`, alongside the other four questions in that check.

## Not confirmed in game

Container-side evidence only. The declarations are in the built tree and the
tree validates; **whether the four empires now appear in the picker needs a live
run**, and the fifth cannot be confirmed from any log at all — it is AI-only, so
the only evidence available will be seeing an Undine world's cities render as
Undine rather than falling through to `mammalian_01`.
