# 38 — Real Space drops ten Sol-neighbour initializers Planetary Diversity still calls

**Status:** decided, 2026-08-07

## The report

The 2026-08-07 15:41 run threw four `prescripted_systems.cpp` errors:

```
Invalid initializer "sol_neighbor_t1".                      pd_habitat_start.txt:314
Invalid initializer "sol_neighbor_t1_no_guaranteed_colony".  pd_habitat_start.txt:324
Invalid initializer "sol_neighbor_t2".                       !vanilla_sol_initializers_ow.txt:111
Invalid initializer "sol_neighbor_t2".                       !vanilla_sol_initializers_ow.txt:240
```

Both referencing files are Planetary Diversity's. Neither declares the keys.

## What actually happened

`common/solar_system_initializers/sol_initializers.txt` is vendored from **Real
Space 4.0**, and it shadows vanilla's path. Both files declare exactly 22
depth-0 keys, which is why nothing noticed: Real Space **adds** twelve real-star
systems (`alpha_centauri_mediumsector`, `bernards_star_mediumsector`,
`sirius_mediumsector`, `procyon_mediumsector` and variants) and **drops** twelve
of vanilla's generic `sol_neighbor_t*` ones. Equal counts, disjoint contents.

That is Real Space working as designed — replacing invented neighbours with real
astronomy is the entire mod. The defect is not the replacement; it is that
**Planetary Diversity was written against vanilla's key names** and still calls
three of them. Two of the twelve PD re-declares itself in
`!vanilla_sol_initializers_ow.txt`; ten are declared nowhere in the built tree.

This is a cross-source break, not a source bug: each mod is correct alone.

## The fix

`src/common/solar_system_initializers/stg_restore_sol_neighbors.txt` restores all
ten missing keys with vanilla's bodies verbatim.

**Additive, not a shadow.** Real Space's file declares none of these ten, so
nothing contests it and its real-star systems are untouched. The restored
systems only ever generate where something references them, and the only
references are PD's three.

Vanilla's bodies use `@distance`, `@base_moon_distance` and `@jumps`, declared
at the top of vanilla's *own* `sol_initializers.txt` — a file we no longer ship.
They are **substituted as literals** (50, 10, 3) rather than redeclared:
`@base_moon_distance` is set to three different values by different files in
this one directory (7, 10, 5), so inheriting it would be non-deterministic, and
redeclaring it would add to the `Variable name ... is already taken` noise the
directory already produces. Decision 31 is the neighbouring hazard.

Vanilla's `sol_neighbor_t1` is named `NAME_Barnards_Star` and Real Space ships
its own `bernards_star_mediumsector`. Both can now generate, in different
galaxies from different callers. That is cosmetic overlap, not a collision.

## The check that should have caught it, and why it did not

`check_vanilla_regression` examines `.txt` files only from `additive_only`
sources and from sources whose descriptor declares a version older than the
target. Its stated premise: *"a live 4.x gameplay mod overriding a vanilla
database is what mods ARE."* Real Space 4.0 is a current 4.x mod, so its file
was never examined — the check reported 141 files and could not see this one.

The premise is right about **intent** and wrong about **consequence**. A live
mod may replace a vanilla database on purpose and still strand a *third* mod
that references the old keys. Intent is not the discriminator; whether anything
still references the dropped key is.

Measured before widening, per the calibration rule in CLAUDE.md. Dropping the
source-scope for `.txt` and checking every vendored file that shadows a vanilla
path yields **31 dropped keys across 11 files**, of which 8 files are already
acked. The three unacked:

| File | Source | Dropped | Verdict |
|---|---|---|---|
| `solar_system_initializers/sol_initializers.txt` | Real Space 4.0 | 12 | **real** — this defect |
| `solar_system_initializers/special_system_initializers.txt` | Real Space 4.0 | 1 (`trappist_initializer`) | false positive — **moved** to `solsector_large_systems.txt` |
| `traits/01_species_traits_habitability.txt` | Planetary Diversity | 9 (`trait_pc_*_preference`) | false positive — **moved** to `04_species_traits_habitability_cold.txt` |

Both false positives are the same shape: a mod moving its own declarations
between files. `check_vanilla_regression` already has the rescue for that — the
`elsewhere` map — but applied it only to `.asset`/`.gfx`, where the same problem
had been found before. Extending that rescue to `.txt` removes both, and the
widened check stands at **1 finding, 0 false positives**.

So the scope change is two lines, and the rescue it depends on already existed.

**`src/` is exempt from the widening, and only from the `.txt` widening.** STG
is a total conversion: emptying vanilla's prescripted empires out of
`src/common/prescripted_countries/` is the point. Widening without that gate
reported 63 such keys across 19 files, all deliberate. `src/` already has two
checks of its own — `check_src_shadowing` requires every shadow be annotated,
and `check_src_source_regression` ([decision 34](34-src-shadows-drop-source-declarations.md))
catches `src/` dropping what a *source* declares.

## Calibrated by reverting the fix

Required, because the first attempt at this check **could not fail**. Removing
only the built copy of `stg_restore_sol_neighbors.txt` still reported 0 findings:
the check's pre-existing `src/` rescue found the same file in `src/` and
subtracted the keys again. A check that reports 0 for both the broken and the
fixed tree has a number to show for itself and no ability to earn it — the
`check_duplicate_entities` failure of 2026-08-07 in a different costume.

With **both** copies removed the widened check reports the defect, and with
either in place it is silent:

| Tree | Findings |
|---|---|
| fix in place | 0 |
| fix reverted (built **and** `src/` copies removed) | **1** — names Real Space 4.0 and all 10 keys |
| restored | 0 |
