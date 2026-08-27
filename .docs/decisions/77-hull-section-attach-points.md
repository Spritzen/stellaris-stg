# 77 — Every Trek hull above corvette borrows a corvette's frame, and its sections hang on points a corvette does not have

**Status:** decided, 2026-08-10
**Follows** [decision 33](33-station-section-attach-points.md), which is the
same defect one entity family over and whose check was scoped to stop exactly
where this begins.
**Follows** [decision 57](57-mounts-share-existing-points.md) — a mount is no
use on a section that never attaches.

## The report

From the 2026-08-10 Federation run:

> *"UFP Destroyers; stern mounts don't match the modal at all. It's possible the
> first mount position is artistically correct, which makes me think a
> horizontal mirror of this position would also be correct… deep dive on this as
> this could reveal/resolve issues across all ships."*

The instinct that it generalises was right, and by more than the report assumed.

## The eight records

```
pdx_entity.cpp:1217  starfleet_tng_destroyer_entity   has no attach point named part2
pdx_entity.cpp:1217  starfleet_tng_cruiser_entity     has no attach point named part2
pdx_entity.cpp:1217  starfleet_tng_cruiser_entity     has no attach point named part3
pdx_entity.cpp:1217  starfleet_tng_battleship_entity  has no attach point named part2, part3
pdx_entity.cpp:1217  starfleet_tng_titan_entity       has no attach point named part2, part3
pdx_entity.cpp:1217  starfleet_tng_colossus_entity    has no attach point named frame_ship
```

**Word for word decision 33's message**, which named two Walshicus *station*
entities in the run of 2026-08-07.

## The mechanism

A hull entity's mesh supplies the attach points its size's `section_slots` hang
sections on: `part1`+`part2` for a destroyer, `part1`+`part2`+`part3` for
cruiser, battleship and titan, `frame_ship` for a colossus. Every Trek hull
above corvette instead declares

```
pdxmesh = "molluscoid_01_corvette_frame_mesh"
```

— **a corvette's frame.** A corvette's whole requirement is `part1`, so the
borrowed frame answers for that and has no `part3` and no `frame_ship` at all.
The sections hung on those never attach, and their guns are placed against
nothing.

Where the point does exist it is still a *corvette's*: `part1` and `part2` sit
~3 units of z apart on that frame, which is a corvette's length, on hulls scaled
at 6. Since STNH puts the **entire ship** in the bow section
(`starfleet_tng_destroyer_bow_L1_entity` → the Steamrunner mesh) and makes every
other section an `empty_mesh` carrying only gun locators in whole-hull
coordinates, that spacing throws the stern guns off the model. Both halves
produce the same symptom, which is why the report saw one defect.

Re-measure: `grep -rc 'pdxmesh = "molluscoid_01_corvette_frame_mesh"'
stg-build/gfx/models/ships/`.

## What changed

`tools/fix_ship_locators.py` gained a hull pass — `hull_entities()` — declaring
each slot **past the first** onto `part1`'s own position, so every section
attaches where the bow does and the gun coordinates land on the hull they were
drawn for. 230 attach points over 100 files, all 22 Trek shipsets plus 12 more
culture directories.

Three scoping decisions, each of which changed the output:

- **`part1` is never written.** It is the one point a corvette frame always
  has, and declaring it anyway would have moved the bow section of 293 entities
  that render correctly today — including the corvette, the one hull three runs
  have graded as right.
- **Only hulls on a borrowed frame.** An entity whose mesh is its own culture's
  art has a rig built for it.
- **Never a file `vendor.yml` patches.** An `src/` override replaces the
  vendored copy and would silently discard the patch; the build refuses it
  outright. 28 files are reported and left, all of them decision 33's own
  station patches.

## Two parsers were wrong about comments, and this found them

STNH's art comments out whole `state = { … }` blocks and leaves the opener
behind, so `bajoran_01_standard_ships.asset` is **+2 braces on a raw count and
balanced on a real one**. The game reads it fine. Two things here did not:

- `fix_ship_locators.py` matched entity blocks on raw text, so its insertion
  points in that file were in the wrong entity. It now masks comments to spaces
  before scanning, preserving offsets.
- `validate.py`'s brace checker counted braces inside comments. It only ever saw
  the file once the tool made it an `src/` override — the vendored copy is not
  checked — so it reported 2 unclosed braces in a file that has none.

**A checker that is wrong about the language will be believed**, and this one
was only caught because it fired on a file that was known-good.

## What this does not fix, and what to do next

**The check that would have caught this exists and was deliberately narrowed.**
`check_section_attach_points` asks precisely this question, and decision 33
scoped it to the station family because at full scope vanilla contributes 41
findings of its own against the mods' 147. Widening it is the durable guard and
is its own piece of work, named as such in the check's own docstring: establish
first whether those 41 are vanilla quirks or a mesh lookup resolving wrongly.
With this change in place, the mod half of that ratio is what should now be
zero, which is the measurement that makes widening tractable.

**Nothing here is confirmed in game.** Section placement is an eyes-only
property; `make validate` clean says the locators exist, not that the ships look
right. The report's other question — whether the destroyer's `small_gun_02` at
`{ -4.384 0.407 7.189 }` should mirror `small_gun_01` at `{ 4.384 0.407 2.054 }`
in z as well as x — is **only answerable after this lands**, because today those
guns are attached to nothing.
