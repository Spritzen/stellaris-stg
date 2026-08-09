# 28 — Weapon locators: `.asset` declarations do count, and they need positions

**Date:** 2026-08-03
**Status:** accepted, with one qualifier added by
[decision 30](30-clone-discards-sibling-locators.md)
**Supersedes:** the claim in `tools/gen_shipsets.py`'s `Emitter` docstring that
`.asset` locator declarations "do nothing".

> **Read decision 30 with this.** A declaration satisfies the engine only in an
> entity that does not also say `clone`, and the repair below put 252 of them
> beside one. The "676 → 0" under *What was fixed* is a false signal: the engine
> was still at 506 four days later.

## The report

A live run of the Klingon start: all three weapon mounts on the starting ships
fired from the centre of the hull rather than from the guns.

## What is actually true

Vanilla bakes weapon locators into the `.mesh` binary with real coordinates. The
locator chunk of `mammalian_01_corvette_M1S1.mesh` carries

```
medium_gun_01 (-0.037, 1.006, -1.355)
small_gun_01  ( 0.000, 1.014,  1.123)
```

Most of the Trek ship art does not. `bajoran_01/frigate/bajoran_corvette.mesh`
ends with an **empty** locator chunk — eight bytes, no entries. The art declares
its guns in the `.asset` instead, and declares them either at an explicit
`position = { 0 0 0 }` or with a `rotation` and no `position` at all. Either way
the gun ends up at the model origin, which is the middle of the ship.

## The claim this reverses

`gen_shipsets.py` used to emit a `locator` block for every mount point a donor
hull was short of — 989 of them — and that emission was removed on the reasoning
that mount points are read off mesh geometry and an `.asset` declaration is
ignored. The 2026-08-03 run disproves it. Classifying every
(section template × culture) pair against the merged tree and intersecting with
the run's own log:

| class | meaning | pairs | engine logged |
|---|---|---|---|
| MISSING | declared nowhere — not in `.asset`, not baked | 857 | **506** |
| NOPOS | declared in `.asset`, no usable position, not baked | 2780 | **0** |
| SHADOWED | bare `.asset` declaration over a baked position | 200 | **0** |

Every one of the engine's 506 `section.cpp:311` records falls inside MISSING, and
not one of the 2,780 NOPOS cases is logged. **An `.asset` declaration satisfies
the engine's existence check.** Had declarations been ignored, all 2,780 would
have been reported.

The earlier reading confused two things: a declaration silences the *error*, but
a declaration *without a position* still leaves the gun at the origin. Removing
the declarations therefore traded a silent visual defect for a logged one and
fixed nothing.

## That a declared position places the gun

Vanilla does this itself, once —
`arthropoid_01_battleship_bow_XL1_entity` declares

```
locator = { name = "xl_gun_01" position = { 0 0 -14.5 } }
```

for a locator its mesh does not bake. A 14.5-unit offset down the hull axis is
not a value anyone writes for an ignored field.

## Consequence

Declaring a locator is necessary but not sufficient. Three rules:

1. **If the mesh bakes it, do not redeclare it bare.** A bare redeclaration is at
   best redundant and at worst resets the position. Deleting it is safe under
   either reading.
2. **If the mesh does not bake it, declare it with a real position.**
3. **Derive the position from geometry, never invent it.** The `.mesh` binary
   carries an axis-aligned bounding box as the `min`/`max` properties; guns are
   placed within it. `gen_shipsets.py` reads that box rather than hard-coding
   offsets, so the placement follows the art if the art changes.

## What was fixed

1. **The sections `gen_shipsets.py` generates**, which are ours: 676 mounts, now
   placed from the donor hull's bounding box. `make validate`'s tracked count
   for these went 676 → 0.
2. **The vendored shipsets**, via `tools/fix_ship_locators.py --all`: 156 `src/`
   overrides across 22 shipsets, 1,626 mounts placed and 54 bare declarations
   dropped in favour of a position the mesh already baked.

Every shipset is covered rather than whichever one is being flown — each STG
empire reaches a different part of this art.

`src/` overrides and not `vendor.yml` patches, because a patch is literal
find-and-replace and these files repeat the same bare line for a dozen entities
that each need a different position. The cost is the one CLAUDE.md names: an
upstream fix to this art is now masked. Each override says so in its header, and
rerunning the tool after `make vendor` regenerates them from the current source.

## Scope still open

**Starbases, orbital rings and defence platforms are deliberately excluded.**
Their sections are `empty_mesh` like the warship ones, but they bolt onto a
modular station with no hull to spread guns along — a citadel section wants
`medium_gun_01`..`013` and no bounding box says where those go. Placing them
from geometry would be inventing, which rule 3 above forbids. They are reported
by `make validate` and left alone.

**A different defect wears the same clothes.** 250 warship mounts still resolve
nowhere after this work, concentrated in `generic_06` (124), `xindi` (26),
`dominion` (20), `cardassian` (14), `borg` (12) and `ferengi` (6). These are not
mispositioned locators — the *section entity* does not exist in that shipset at
all, so there is no `.asset` block to correct. `generic_06` is the clear case:
`gen_shipsets.py` reports `NO HULL` for its cruiser, battleship, titan and
juggernaut, so those sizes fall back to another culture's art entirely. That is
decision 17/18 territory, not this one.

## Not settled

Whether a bare `.asset` declaration *overrides* a position the mesh already
bakes, or is ignored in favour of it, could not be established from the
container. The repair is safe either way: where the mesh bakes the mount, the
bare declaration is deleted, which is a no-op under the second reading and a fix
under the first.
