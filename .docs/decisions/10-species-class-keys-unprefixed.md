# Decision 10 — the five species classes take STNH's bare keys, not `STG_`

**Resolved 2026-08-02.** Amends the `stg_` prefix rule in `CLAUDE.md`.
Prerequisite for Phase 3; evidence in
the 08-01 analysis §4a.

## What was decided

`STG_FED`, `STG_VUL`, `STG_KDF`, `STG_ROM`, `STG_CAR` are renamed to **`FED`,
`VUL`, `KDF`, `ROM`, `CAR`** — STNH's own key names — in
`src/common/species_classes/stg_species_classes.txt` and everywhere they are
referenced (`stg_portrait_sets.txt`, `stg_major_powers.txt`, and the species
class loc key families in `stg_species_l_english.yml`).

The *file* stays `stg_`-prefixed. Only the keys change.

## Why

The vendored STNH clothing selectors under `gfx/portraits/asset_selectors/`
choose a portrait's outfit with `is_species_class = <KEY>`, and those keys are
STNH's bare ones. The live run measured **660 `Failed to deferred read key
reference` errors across 49 distinct undefined class keys** — every Trek uniform
selector in the tree failing its gate before any trigger is evaluated.

This is not a cosmetic naming question. It defeats the mod's purpose: with
`STG_*` classes, no Trek species can ever match a Trek clothing selector, so
every leader falls through to the default texture. Phase 3 could give all 139
stubbed triggers perfect bodies and the uniforms would still not appear, because
the species-class gate fails first.

## Why not the alternatives

**Keep `STG_*` and edit the selectors.** 500+ vendored files, and it violates
plan.md §2 rule 1 (never hand-edit a vendored file). Expressing it as
`vendor.yml` patches would mean 500+ declared patches that break on every STNH
update.

**Keep `STG_*` and add bare aliases.** Stellaris has no species-class aliasing.
Declaring both means two classes per species in the empire designer.

**Vendor STNH's `common/species_classes/`.** Rejected for the same reason
decision 08 rejected vendoring its triggers: it declares `archetype = HUMANOID`
from STNH's `common/species_archetypes/`, pulling in the total-conversion script
we exist not to ship. It would also bring 257 classes when we need five.

## The precedent this follows

Already stated in the header of
`src/common/scripted_triggers/stg_stnh_art_triggers.txt`:

> *"Deliberate exception to the stg_ prefix rule is NOT needed here: these are
> STNH's key names, which the vendored art references verbatim, so they cannot
> be renamed."*

The same argument, applied to the same body of vendored art. Decision 08 made it
for triggers and simply did not notice it also applied to classes, traits and
shader effects — see plan.md §3, "STNH's art is wired to STNH's namespace".

## The collision risk, stated honestly

Bare `FED` / `VUL` / `KDF` / `ROM` / `CAR` are exactly the keys another Trek mod
would claim, and Stellaris merges every mod into one namespace. That risk is
real and it is accepted, because **STG is standalone and permanently the only
mod in its playset** (plan.md §1). Verified against the two things that could
collide today: no vanilla species class and no vanilla localisation key uses any
of the five.

## The rule this generalises to

> **Keys that vendored art references verbatim are not ours to prefix.** Where
> STG's own script must meet vendored STNH art at a shared key — species
> classes, leader traits, scripted triggers, shader effects — the key takes
> STNH's name. Everything else keeps `stg_`.

Recorded in `CLAUDE.md` alongside the prefix rule.
