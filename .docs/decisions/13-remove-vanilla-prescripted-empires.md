# 13 — Remove vanilla's prescripted empires; pin `supported_version` exactly

**Date:** 2026-08-02
**Status:** decided
**Supersedes:** nothing. Extends plan.md §1 (Trek-named systems, no hand-placed
homeworlds) to the empire picker.

---

## 1. What was decided

**Every vanilla prescripted empire is removed.** 52 of them, across 19 files,
shadowed by comment-only files in `src/prescripted_countries/`.

**`prescripted_countries/default.txt` is deliberately NOT shadowed.** It is not a
playable empire — it is the `default = yes` template the empire creator starts a
custom empire from. Removing it breaks custom empire creation, which is the one
path a player actually uses.

**`src/descriptor.mod` declares `supported_version="4.4.6"`**, not `"4.4.*"`, so
a game patch is announced rather than absorbed.

## 2. Why remove them

STG is a total conversion. The United Nations of Earth, the Blorg Commonality and
the Tzynn Empire are not Trek, and they arrive in two places that matter:

1. the empire-select list, alongside the five major powers in
   `src/prescripted_countries/stg_major_powers.txt`;
2. AI empire spawning, where a galaxy asked for 15 empires will happily seat the
   Scyldari Confederacy next to the Federation.

This is a **content** ground, which is the only kind
[decision 11](11-fix-source-errors-dont-drop.md) accepts. It is not an error-count
argument: the 52 empires threw nothing in the 2026-08-02 13:35 run.

## 3. Why comment-only shadows rather than any other mechanism

A file at a vanilla path replaces vanilla's entirely (CLAUDE.md, *Overwrite vs.
append*). That is normally the hazard — it is how
[decision 07](07-stnh-art-shadows-vanilla.md) happened — and here it is exactly
the tool wanted: total replacement of a file whose whole content we mean to drop.

**Prior art, and it is STNH's.** STNH ships its own copies of all these vanilla
filenames, and they are comment-only — 6 bytes, 14 bytes, 62 bytes. One of them
says so outright: `### Keep file empty to override vanilla entries`. A 3.12-era
total conversion reached the same answer.

**We write our own rather than vendoring STNH's**, for three reasons:

- STNH's set is 3.12-era. It has no `82_infernals_prescripted_empires.txt`, no
  `84_biogenesis_…`, no `85_grand_archive_…` — the packs 4.4 added since. Those
  three files' 5 empires would have survived.
- Vendoring the folder would also bring STNH's six `STH_*.txt` files, ~2,000
  lines of Trek empires. That is a Phase 3 content decision about whose
  Federation we ship, and it is not this one.
- STNH's `default.txt` is a 3.12 copy that drops `trait = "trait_organic"` and
  `ship_size = "civilian_arkship_tier_1"`. Shadowing vanilla's with it is
  decision 07's failure mode, in the one file §1 says to keep.

So `prescripted_countries` stays out of STNH's `include:` list in `vendor.yml`,
and the 19 shadows are ours.

## 4. What was checked before removing them

Prescripted empires are presets, not script targets — but that was verified, not
assumed:

| Suspicion | Finding |
|---|---|
| `resistance` referenced by `events/machine_age_situation_events_2.txt` | a loc key, `custom_tooltip = "synth.300.a.resistance.tt"` |
| `broken_shackles` referenced by `events/first_contact_events.txt` | a loc key, `text = first_contact.4000.desc.broken_shackles` |
| `knights` referenced by three `common/` files | the Knights of the Toxic God origin's jobs and buildings, not the empire key |
| `is_human_prescripted_empire` scripted trigger | reads `has_country_flag = human_1/2/3`. With the empires gone the flags are never set and the trigger is simply always false — which is the desired result |

No vanilla file resolves a prescripted empire **by key**.

## 5. The version pin, and the check that could not have caught a patch

`supported_version="4.4.6"` makes the launcher flag STG when the game moves. That
is the user-visible half. The half that matters day to day is in `make validate`.

`check_descriptor` compared `declared.split(".")[0]` — the **major** — against
`launcher-settings.json`'s `modsCompatibilityVersion`, which is `4.4`, a
compatibility *bucket* that does not carry a patch level at all. With `4.4.*`
declared, nothing short of Stellaris 5 could have made it fire. It was reporting
a comparison it was structurally incapable of failing — the exact hazard CLAUDE.md
names about `check_vanilla_regression`.

It now compares component-by-component against `rawVersion` (`v4.4.6`), the exact
installed build, honouring `*` so a deliberate `4.4.*` still works. Verified by
running it against a descriptor declaring a version the installed game does not
have, and watching it warn.

**Why a patch matters enough to want the alarm:** the harvest contains files that
shadow vanilla paths from four different mods. A Stellaris patch that adds
entities, particles or flag colours to one of those paths silently un-declares
them in our build, with no error at load. That is decision 07, and it is
discovered by re-reading the sources after a patch — which first requires
knowing a patch happened.

## 6. Cost

If a later phase wants a vanilla empire back as a Trek analogue, the shadow file
is comment-only and vanilla's original is at
`/stellaris/prescripted_countries/<same name>` — restoring one is a copy of one
block. Nothing is destroyed.
