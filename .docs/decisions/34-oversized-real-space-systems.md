# 34 — Real Space's oversized systems: leave them, they are its own warning

**Decided 2026-08-07**, from the live run of that morning. **No change made** —
this records why, so the next session does not spend the afternoon again.

## What happened

One record, in play:

```
galactic_object.cpp:2731  System Mintaka with initializer mintaka_system is too big.
                          Make sure the outer radius is smaller than 900.
```

## What it is

`CELESTIAL_WARNING_COORDINATE_VALUE` is the threshold, and every party to the
merge has an opinion about it:

| | value |
|---|---|
| vanilla `00_defines.txt` | 600 |
| Real Space `realspace_defines.txt` | **900** (what our tree has) |
| STNH `sth_defines.txt` | 2000 (not vendored — STNH's `common/` is not taken) |

The comment Real Space kept from vanilla says it plainly: *"System size at which
you get errors for the system being too big (500 is the normal values, as
graphics can glitch with bigger values)."*

So Real Space raised the threshold to 900 **because it builds big systems**, and
its own largest systems still exceed the number it chose for itself. `mintaka_system`
is Real Space's, vendored unmodified — it is the only source shipping
`solsector_large_systems.txt`, so no merge decision touched it.

## It is not a merge artefact, and that was worth checking

The obvious suspect was Real Space – System Scale, which rescales Real Space.
It does not apply here: its only relevant change is `@base_moon_distance`
**10 → 6**, which makes these systems *smaller*. Standalone Real Space would
trip this warning harder than our tree does.

## Mintaka is not special either — the log named the system that got generated

Summing top-level `orbit_distance` and `change_orbit` across Real Space's 198
initializers:

| reach | initializer |
|---|---|
| 950 | `jabbah_system` |
| 795 | `algorab_system` (+ its small/medium sector variants) |
| **738** | **`mintaka_system`** ← the one this galaxy happened to roll |
| 690 | `almach_system` |
| … | median 470 |

## Decision

**Change nothing.** Not the geometry, not the threshold.

- Editing Real Space's orbits means picking numbers, and there is no number to
  derive — mintaka is fifth-largest, so any cut deep enough to matter is a
  redesign of the mod's own systems.
- Raising `CELESTIAL_WARNING_COORDINATE_VALUE` silences a diagnostic its author
  deliberately set, and the author's own comment warns that graphics glitch at
  large values. Silencing the warning would not fix the thing the warning is
  about.
- The cost is bounded and known: one `error.log` line per oversized system that
  actually generates, in play, from a source-owned threshold. The 2026-08-07 run
  generated its galaxy and played to first contact with this warning present.

## What is ours, and it is clean

STG's own 27 home-system initializers (decisions 23–25) top out at **515**,
comfortably inside Real Space's 900 and inside vanilla's 600. Nothing we
generate is near the limit — which is the half of this question that would have
been worth acting on, and is not.
