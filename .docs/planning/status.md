# Where things stand

> **What** — the current state of the build: phase completion, the `error.log`
> baseline, and what the last live runs established.
> **Open when** — starting a session, or before quoting any number about the
> build.
> **Then** — [Open questions](open-questions.md) · [Phases](phases.md) · [Live runs](../guides/live-runs.md)

*Last updated against the build of 2026-08-22 and the run of 2026-08-22
([analysis 2026-08-16](../analysis/2026-08-16.md)). Every number here has a date
because every number here goes stale — [style guide §6](../style-guide.md).*

| | |
|---|---|
| **Phase 0** — vendoring pipeline | **complete** |
| **Phase 1** — playable Federation | **complete**, run in-game repeatedly |
| **Phase 2** — the rest of the galaxy | **complete**. 101 prescripted empires (22 playable, 79 AI-only minors) over 100 distinct species classes, 92 name lists, 37 real home systems. `src/` declares **131** classes in all — the extra 31 are the STNH selector stubs of [decision 32](../decisions/32-declare-stub-species-classes.md) |
| **Phase 3** — art and identity | **complete 2026-08-08**. Clothing triggers, shipsets, weapon mounts, flags, rooms, city sets, loading screens, `paragon_backgrounds.txt`, the shipsets' 39 extra flags |
| **Phase 4** — polish | **started 2026-08-08**. Music, the ship registries and their class names, then the three slices [decision 75](../decisions/75-trek-anomalies.md) scoped: **21 Trek anomalies** ([75](../decisions/75-trek-anomalies.md)), **6 dig sites** ([76](../decisions/76-trek-archaeology.md)) and **21 story events** ([77](../decisions/77-trek-story-events.md)), all 2026-08-09. All three are shipped; what remains in the phase has no scope written for it |
| **Phase 5** — the clutter pass | **complete 2026-08-07** (pipeline work, taken out of order) |

## The build, as it stands

**Read every figure below off the build rather than off this page** —
`.vendor-manifest.json` and the `make validate` summary line carry the live
ones.

| | Build of 2026-08-22 |
|---|---|
| Files / size | **22,406 / 14.3 GiB** ([the per-tier split](../architecture/vendored-merge.md#size)) |
| Re-cut at harvest / pruned | 1,661 / **888** |
| Overwrites / additive skips | 947 / 220 |
| `make vendor` | 69 s |
| `make validate` | **0 warnings, 0 errors** |
| `make docs` | **0 warnings, 0 errors** |
| `make gen-check` | **11 of 11 generators are fixpoints** |

**The prune has fallen 935 → 909 → 888 across three passes with no edit to
`vendor.yml`**, and that is the property worth knowing rather than the number:
the 27 pictures [decision 76](../decisions/76-trek-archaeology.md)'s dig sites
declare and the 21 [decision 77](../decisions/77-trek-story-events.md)'s story
events declare came back out of `.source/` by themselves, exactly as the
anomalies' 24 did. Declaring art un-prunes it; nothing has to be excluded.

`make validate` gained `check_anomalies`, `check_archaeology` and
`check_story_events` over Phase 4 and `make docs` gained a second family of
question — whether the documented inventory still matches the repo, not only
whether its citations resolve ([71](../decisions/71-doc-inventory-checks.md)).

**2026-08-22 added six, all from reading the docs rather than a live run.**
First three ([83](../decisions/83-widen-attach-points-and-two-new-checks.md)):
`check_section_attach_points` gained a **second scope** covering every hull
flying a borrowed frame, which is what finally guards
[decision 82](../decisions/82-hull-section-attach-points.md)'s 230 attach points;
`check_selector_texture_paths` is new and found ten malformed portrait paths that
two live runs had sampled three of; and **`make gen-check`** is a new target
asking whether each of the eleven generators still reproduces `src/` exactly.
All eleven do.

**Then three more, from working the three items the Vulcan run left marked
*waiting on a content call*** ([84](../decisions/84-shipset-descs-and-home-system-names.md)) —
**none of which turned out to need a call**: `check_shipset_descriptions`
(vanilla floor **0 and 0**; STG was 30 of 30 wrong in one direction or the
other), `check_home_system_body_names` (vanilla **0 of 9** home systems against
**62 of 357** initializers overall, which is where the scope comes from) and
`check_graphical_culture_art`, which **falsified the finding it was written
for** — 24 of vanilla's own 52 declared cultures ship no city art either, and
`fallback` is what resolves it.
What each asks, and the vanilla floor each is calibrated against, is in
[the check catalogue](../validation/checks.md); the floors themselves are
constants in `tools/validate.py` with the ratio written beside them
([rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter)).

---

## The `error.log` baseline

**The current baseline is the 2026-08-22 Vulcan run** — a 26-minute session, and
the cleanest log this project has recorded. The 2026-08-10 Federation run beside
it is the deep one: ~11 hours, and the only log so far that carried real defects
rather than eyes-only findings.

| | **2026-08-22** Vulcan | 2026-08-10 Federation | 2026-08-08 |
|---|---|---|---|
| Records / size | **1,264 / 187 KB** | 2,251 / 228 KB | 1,261 / 187 KB |
| Startup window | 55.4 s | 49.4 s | 49.3 s |
| Records **after** startup | **4** | 174 | 1 |
| Play window | ~26 min | ~11 h | short |

**Read the post-init column, never the total.** ~187 KB is the init-window floor
of this build and it has not moved in three runs; against the ~1 MB a clean
vanilla run produces the volume is fine either way. **The 1 → 174 → 4 swing is a
change of run, not of build**: the short sessions opened few screens.

**Two 2026-08-10 fixes are now confirmed in game by silence** — the 98-record
Planetary Diversity cluster and the 19 missing-localisation records are both
**0**, and the run exercised the thing that produced each. That is the first time
a live run has closed a defect in this project by measurement rather than by
inspection. The whole reading is
[analysis 2026-08-16](../analysis/2026-08-16.md); the Federation run's own
findings and what each cost are in
[ufp-run-remediation.md](ufp-run-remediation.md).

**What still has no in-game evidence at all**, after two runs that both ended
early:

- **Every hull above corvette.** [Decision 82](../decisions/82-hull-section-attach-points.md)'s
  230 attach points are the single most valuable unmeasured thing in the project.
- **The dig sites, the anomalies and the story events** — unreached twice
  ([76](../decisions/76-trek-archaeology.md), [75](../decisions/75-trek-anomalies.md),
  [77](../decisions/77-trek-story-events.md)).
- **Habitats** ([53](../decisions/53-duplicate-entity-triage.md)), the ship class
  names and registries ([72](../decisions/72-ship-class-names.md)), and the music
  by ear.

**What the Vulcan run opened is closed** — its findings 2–4, all worked
2026-08-22 without a live run or a content call
([84](../decisions/84-shipset-descs-and-home-system-names.md)). **Two were
bigger than the analysis recorded and one was not a defect**: the shipset
descriptions were 30 of 30 wrong rather than 7 (seven renames, sixteen new
descriptions written against the hull art); the 40 Eridani duplicate was seven
duplicate names in six systems from three separate `gen_home_systems.py` bugs
rather than one paste; and the six cultures with no city art all declare a
`fallback` that reaches art, which is the mechanism vanilla's own file header
names. Still open from 2026-08-10: why no Trek empire appeared in 22 — which
now has a one-glance answer waiting, since the Federation alone carries
`spawn_enabled = always` — and the 196 selector rows pointing at art no source
mod ships.

The game has been the **native Linux build** since 2026-08-02
([decision 15](../decisions/15-native-linux-runtime.md)) — content unaffected,
deployment re-confirmed on it, startup and gfx counts **not comparable across that
boundary**.

Analyses are written only on request, one file per live run
([`../analysis/`](../analysis/README.md)). **Filenames there are sequence slots,
not dates**: `2026-08-16` is the run of 2026-08-22.

---

## The four runs of 2026-08-08 — what still carries

Four runs in one day (Klingon, Cardassian, Terran, Vulcan), ~1,300 records each
bar the Klingon's 2,020. **Every finding across all four was eyes-only** and each
one is stated in full in its own decision — [22](../decisions/22-empire-designer-clothes.md),
[48](../decisions/48-room-selector-merge.md), [52](../decisions/52-trek-star-names.md),
[57](../decisions/57-prescripted-rulers-unpin-clothes.md)–[59](../decisions/59-ship-name-pools.md),
[62](../decisions/62-city-set-cultures-undeclared.md)–[68](../decisions/68-ruler-clothes-index-restored.md),
[70](../decisions/70-vulcan-city-framing.md). **Three things outlive the runs
themselves:**

**Eyes-only is now the standard shape.** `make validate` was clean throughout,
and the 590-record room-selector `weight` defect visible in the Klingon count is
the last one a log has carried.

**The one falsification worth carrying forward.** The Vulcan run killed
[decision 68](../decisions/68-ruler-clothes-index-restored.md) outright — all six
rulers it pinned an index for wore a garment the model does not predict, so
`clothes = N` on a *shared* master selector is not an enumeration, and nothing in
the container can say what it is. The seven affected rulers took STNH's own
convention instead: a dedicated **one-texture** selector and `clothes = 0`
([69](../decisions/69-ruler-clothes-dedicated-selectors.md)). **The 2026-08-22
run vindicated that** — T'Pau draws in a Vulcan civilian robe, so the dedicated
selector is reached and the falsification is confirmed rather than merely
inferred.

**The 17 warnings standing on 2026-08-07 were triaged to 0, and two of them were
real defects** — five nebula and debris entities rendering at a third of System
Scale's size, and every empire's habitats at risk of drawing as a Suliban helix.
Decisions [53](../decisions/53-duplicate-entity-triage.md),
[54](../decisions/54-federation-texture-collisions.md),
[56](../decisions/56-starbase-modules-order.md). **The 2026-08-10 run graded the
nebula half and it is correct; the habitats have still not been seen after two
runs since.**
