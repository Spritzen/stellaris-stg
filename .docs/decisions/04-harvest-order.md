# 04 — Harvest order corrections

**Decided:** 2026-08-01

Established the harvest order in plan.md §3 against measured evidence rather than
inference: every file in all 29 harvest sources enumerated (19,106 distinct
paths, 550 contested), cross-checked against the mod authors' stated load orders.
Three things changed.

> **The counts below are the 2026-08-01 mount, when the harvest was 29 sources.**
> It has moved several times since. For current figures read
> `.vendor-manifest.json` (plan.md §4 explains how); the *order* and the
> reasoning are what this file is for.

## The Universal Resource Patch moves from first to last

Its README states the requirement verbatim — *"Load order: Absolute bottom, below
all mods, including UI mods."*

**Why it matters here specifically:** URP's `topbar_other_resource_groups.txt` is
1,271 lines against vanilla's 41 and is a strict superset of every contender. It
already carries Planetary Diversity's resources *and* an explicitly annotated
STNH block (`sr_latinum`, `sr_dilithium`, `sr_ketracel_white`, `sr_crew`, …). At
position 1 it was being overwritten by PD - Unique Worlds' 42-line version,
silently costing STG Trek resource display in the topbar — content we want and
would otherwise have rebuilt by hand.

**Consequence:** deletes a conflict rather than solving it. The old §4 row for
this file said "small, additive; merge both". No merge is needed.

## STNH art becomes additive-only

Vendored last unconditionally, STNH won 137 paths against gameplay mods we kept
on purpose: 121 planet-view backdrops under `gfx/portraits/environments/`, 10
vanilla-named planet event pictures, and 6 files under `gfx/models/ships/` that
are a vanilla shipset entity definition and shared VFX textures.

**The rule:** take STNH's art paths, but skip any path an earlier source already
claims.

**Why it is free:** none of STG's Trek identity is contested. All 104 STNH ship
directories (`federation`, `klingon`, `romulan`, `cardassian`, `borg`, …), every
species portrait, every room, and everything under `flags/`, `music/` and
`sound/` are uniquely STNH's. The only contested `gfx/portraits/` files are under
`environments/` — planet backdrops, not species art.

## The conflict register was incomplete

Seven rows listed; sixteen non-`gfx/` conflicts exist, plus 534 under `gfx/`.
Added nine rows — most importantly
`common/scripted_variables/00_realspace_scripted_variables.txt` (Real Space vs
System Scale), which drives every Real Space scale value and had no recorded
decision.

Measuring the merges also reclassified them. Three of the four "hard" merges are
small: `setup.gui` is a 4-line delta onto UIOD, `planet_view.gui` a 74-line one.
Only `00_planet_classes.txt` is genuinely hard, and it is harder than recorded —
Real Space *removes* ~300 vanilla lines, so it is not a clean additive merge.

## Two smaller calls

- **Whiter Stars loses `b_star.dds` / `t_star.dds` to Real Space** via an explicit
  exclude. Real Space owns star classes; a 16-file mod declaring
  `supported_version="3.*"` overriding it was an accident of tier placement.
  Recorded as an exclude rather than a reorder, so Whiter Stars stays in the
  graphics tier where it reads correctly.
- **`desktop.ini`, `*.psd` and `Thumbs.db` are excluded from vendoring** — 12
  junk files shipped by the PD family, two of them contested.

**Also noted:** the vendor tool must normalise line endings before diffing or
checksumming. Several sources ship CRLF, which makes a naive diff report 16,964
changed lines on a file whose real delta is 74, and would make `make validate`'s
hand-edit detection fire on every rerun.

**Not applicable — don't chase it.** Searching for prior art on the
`00_planet_classes.txt` collision surfaces a "PD-RS compatibility patch"
(workshop 2053888865, mirrored on Skymods). It targets **Real Space: New
Frontiers**, a different mod from the Real Space 4.0 (937289339) we harvest, so
it does not apply. `00_planet_classes.txt` is hand-merge work in Phase 0.

**Revisit if:** a source mod updates on Steam and its file set changes. The
contested-path measurement behind this decision is a snapshot of the mount as of
2026-08-01; `make provenance` plus a re-run of the enumeration is the way to
check whether any of it has moved.
