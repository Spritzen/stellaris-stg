# 60 — Read the resample target off vanilla's FAMILY, not only the file

**Status:** decided, 2026-08-08
**Closes the half** [decision 55](55-city-set-geometry.md) named and could not
reach. Found by the live Cardassian Union run it asked for.

## The report

*"Cardassia Prime's cities; buildings look small and sunk low, with the backdrop
behind them correct. That's the 30% canvas bug."*

Exactly the symptom decision 55 predicted would survive, on exactly the empire
it predicted it would survive on.

## Why 58 could not reach it

`resample_to_vanilla:` reads its target off **the vanilla file being shadowed**,
and that is deliberate: it must keep working across a game patch that re-cuts
vanilla art. But it means the question has no answer when there is no such file:

```python
vanilla = GAME_DIR / rel
if not vanilla.is_file():
    continue                    # ← 113 files left at STNH's own size
```

STNH's six own Trek city prefixes — `klingon`, `vulcan_01`, `cardassian_01`,
`borg_01`, `tholian_01`, `undine_01` — shadow no vanilla path, because vanilla
has no Cardassians. They are named by six of our empires
([decision 47](47-flags-city-sets.md)), they were on the 560×280 canvas, and
`make validate` reported `ok` throughout because
`check_shadowed_texture_geometry` asks the same question the harvest does and
was blind in the same place.

## Decision

**A second way to get a target: the modal dimensions of vanilla's own files
matching the same pattern.** Still derived from vanilla, never asserted — which
is the property [decision 40](40-event-picture-geometry.md) refused to give up
and the reason 58 stopped rather than writing `800x400` into the manifest.

```yaml
- glob: "gfx/portraits/city_sets/*_city_l*.dds"
  fit: canvas
  target: family
- glob: "gfx/portraits/city_sets/*_room.dds"
  fit: crop
  target: family
```

Three things this needed that are not obvious:

- **`target: family` is opt-in per rule, not global.** Vanilla is 266/271
  uniform on city layers and 91/91 on rooms; it is 580/639 on event pictures,
  whose other 59 are a genuine second size. Applying the family rule globally
  re-cut **1,344** event pictures on the first attempt — a silent widening far
  past decision 40's calibrated scope. A widening should read as the piece of
  work it is (CLAUDE.md's rule for `check_section_attach_points`), so it is
  declared where someone will see it.

- **One directory, two families, two fit modes — so two rules.** The old glob
  was `city_sets/*.dds`, which was fine while the target came per-file and is
  not fine now: the modal over both families is 800×400 and would have padded
  every room onto a city canvas. A city layer is one of six composited by exact
  pixel position (`fit: canvas`); a room is one full-bleed backdrop whose aspect
  ratio is load-bearing and whose offsets are not (`fit: crop`) — the difference
  that `fit:` exists to express.

- **The canvas and the strip width are per pattern too.** `still_width` decides
  whether a wide file is an animation strip; shared across the directory it
  hands the heuristic a 620 px event-picture width while it looks at a 952 px
  room, and 952 has a divisor at 476 that passes every test the heuristic
  applies. A room would have been re-cut to its own left half.

**A size vanilla itself uses in that family is left alone.** Vanilla ships
`ai_01_city_l01..l05` at **4×4** — its own way of saying "this layer is empty" —
so 4×4 is vocabulary in this directory rather than a defect, and Planetary
Diversity's `pd_tree_of_life_01` uses the same idiom for the same purpose.
Derived from vanilla's own usage, per CLAUDE.md's rule for allowlists.

## Result

| | before | after |
|---|---|---|
| `*_city_l*.dds` | 197 at 800×400, 102 across 33 other sizes | **299 at 800×400** + 6 vanilla-idiom 4×4 |
| `*_room.dds` | 316 at 952×340, 11 others (to 1026×403) | **327 at 952×340** |

STNH files re-cut per build: 722 → **835**.

## How this class of defect gets caught next time

`check_shadowed_texture_geometry` gained the same second question, over the same
two families, with `_GEOMETRY_FAMILIES` named beside `_GEOMETRY_DIRS` so the
check and the manifest can be read against each other. It now examines 1,212
files rather than 737.

**Calibrated by running the rule over `.source/`'s un-recut art: 113 family
findings before, 0 after** — and its shadowed-path half independently
reproduces decision 55's 153, which is what says the harness is measuring the
right thing. 0 vanilla false positives by construction: both the target and the
allowed sizes are read out of vanilla.

## The rule worth carrying

**"Vanilla ships nothing here" is not the same as "nothing to check against."**
A file can shadow no path and still be drawn into a frame vanilla sized, if it
belongs to a family vanilla is uniform about. Decision 40's rule — derive, never
assert — was read as *derive from the file*, and the file is only the narrowest
of several things you can derive from. The wider question was available the
whole time and nobody asked it, which is decision 43's lesson arriving in a
directory that has now taught it twice.
