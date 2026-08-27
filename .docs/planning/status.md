# Where things stand

> **What** — the current state of the build: phase completion, the `error.log`
> baseline, and what the last live runs established.
> **Open when** — starting a session, or before quoting any number about the
> build.
> **Then** — [Open questions](open-questions.md) · [Phases](phases.md) · [Live runs](../guides/live-runs.md)

*Last updated against the build of 2026-08-26 and the run of the same day; the
last run with a written analysis is 2026-08-22
([analysis 2026-08-16](../analysis/2026-08-16.md)). Every number here has a date
because every number here goes stale — [style guide §6](../style-guide.md).*

| | |
|---|---|
| **Phase 0** — vendoring pipeline | **complete** |
| **Phase 1** — playable Federation | **complete**, run in-game repeatedly |
| **Phase 2** — the rest of the galaxy | **complete**. 99 prescripted empires (22 majors/quadrant/frontier, 77 minors; all playable, and all in the pool the generator draws from since [decision 88](../decisions/88-playable-gates-the-design-database.md) — **and the 2026-08-26 save proves all 99 reach the design database — and that no galaxy has yet drawn one**, see [decision 90](../decisions/90-design-database-is-not-the-cause.md); the mechanism a Trek galaxy actually needs is a static map plus `create_country` initializers, neither of which STG ships — [decision 92](../decisions/92-create-country-initializers.md), planned in [static-galaxy-plan.md](static-galaxy-plan.md)) over 99 distinct species classes, 92 name lists, 36 generated home systems plus vanilla's Sol. `src/` declares **129** classes in all — the extra 30 are the STNH selector stubs of [decision 32](../decisions/32-declare-stub-species-classes.md) |
| **Phase 3** — art and identity | **complete 2026-08-08**. Clothing triggers, shipsets, weapon mounts, flags, rooms, city sets, loading screens, `paragon_backgrounds.txt`, the shipsets' 39 extra flags |
| **Phase 4** — polish | **started 2026-08-08**. Music, the ship registries and their class names, then the three slices [decision 75](../decisions/75-trek-anomalies.md) scoped: **21 Trek anomalies** ([75](../decisions/75-trek-anomalies.md)), **6 dig sites** ([76](../decisions/76-trek-archaeology.md)) and **21 story events** ([77](../decisions/77-trek-story-events.md)), all 2026-08-09. All three are shipped; what remains in the phase has no scope written for it |
| **Phase 5** — the clutter pass | **complete 2026-08-07** (pipeline work, taken out of order) |

## The build, as it stands

**Read every figure below off the build rather than off this page** —
`.vendor-manifest.json` and the `make validate` summary line carry the live
ones.

| | Build of 2026-08-27 |
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

**The current baseline is the 2026-08-26 Vulcan run**, the first since
2026-08-22 to leave a save on disk — which is what made
[decision 90](../decisions/90-design-database-is-not-the-cause.md) possible. The
2026-08-10 Federation run beside it is still the deepest: ~11 hours, and the only
log so far that carried real defects rather than eyes-only findings.

| | **2026-08-26** Vulcan | 2026-08-25 pm Vulcan | 2026-08-25 am Vulcan | 2026-08-24 Vulcan | 2026-08-22 Vulcan | 2026-08-10 Federation | 2026-08-08 |
|---|---|---|---|---|---|---|---|
| Records / size | **1,315 / 195 KB** | 1,280 / 191 KB | 1,335 / 190 KB | 1,315 / 208 KB | 1,264 / 187 KB | 2,251 / 228 KB | 1,261 / 187 KB |
| Startup window | 48.3 s | 45.1 s | 48.5 s | 46.8 s | 55.4 s | 49.4 s | 49.3 s |
| Records **after** startup | **55** | 13 | 19 | 55 | 4 | 174 | 1 |
| Play window | **~2 h 45 m** | ~1 h | ~2.5 h | ~7 h | ~26 min | ~11 h | short |

**Read the post-init column, never the total.** 187–208 KB is the init-window
floor of this build and it has not moved in seven runs; against the ~1 MB a clean
vanilla run produces the volume is fine either way. **The 1 → 174 → 4 → 55 → 19
→ 13 → 55 swing is a change of run, not of build**: the short sessions opened few
screens.

**Five of 2026-08-26's 55 post-init records name STG files, and all five are now
fixed** — `select_empire_design_view.cpp:714`, five minor powers hidden from the
empire designer by two vanilla gates STG had no check for. Both rules were swept
across all 99 empires and found exactly those five;
`check_prescripted_empires` now carries all three
([decision 90](../decisions/90-design-database-is-not-the-cause.md)). The other
50 are the familiar vanilla mix, plus the `ariphaos_precursor_cosmic.txt` record
below, which recurred.

The 2026-08-25 evening run's **13 post-init records were eight distinct kinds**
over roughly an hour of play: `PLANET_SCALE_SYSTEM` (acked,
[43](../decisions/43-planet-scale-system-length.md)), three `add_intel` and two
`add_trust` script errors in vanilla's own `nemesis_operations_events_1.txt` and
`shroud_events.txt`, one `Invalid context switch [FROM]` in vanilla's
`00_admiral_traits.txt`, three `Failed to pick an event sound` on `first_contact`
events, one colony building-placement failure, and one missing sound effect.

**One of them names a file we ship**, and it is the first post-init record to do
so since 2026-08-10:

```
[18:14:33] eventscope.cpp:3383  add_anomaly: Unable to resolve country from 'owner'
                                (country scope) at events/!!!!!!ariphaos_precursor_cosmic.txt line: 127
```

Vendored from **Assorted Precursor Adjustments** (harvest position 13), so
[invariant 4](../guides/working-rules.md) applies — fix it in a `vendor.yml`
patch, do not drop the source. One occurrence in an hour; a queue item, not a
regression. *(Not the dropped Ariphaos Unofficial Patch — same author, different
mod. [Decision 02](../decisions/02-drop-ariphaos.md).)*

**None of 2026-08-24's 55 post-init records names an STG file either** — they are
vanilla's own event and trigger scripts plus Planetary Diversity's domed-base
decision, over seven hours of play. That is a volume reading only: **no analysis
was written for this run** ([those are written on request](../analysis/README.md)),
so the run's own observations live in
[decision 86](../decisions/86-prescripted-empires-never-drawn.md) and nowhere
else.

**Two 2026-08-10 fixes are now confirmed in game by silence** — the 98-record
Planetary Diversity cluster and the 19 missing-localisation records are both
**0**, and the run exercised the thing that produced each. That is the first time
a live run has closed a defect in this project by measurement rather than by
inspection. The whole reading is
[analysis 2026-08-16](../analysis/2026-08-16.md); the Federation run's own
findings and what each cost are in
[ufp-run-remediation.md](ufp-run-remediation.md).

**What still has no in-game evidence at all.** Of the five runs since
2026-08-10, one ended early and the other four were played without a run plan
and written up only in [decision 86](../decisions/86-prescripted-empires-never-drawn.md),
[decision 88](../decisions/88-playable-gates-the-design-database.md) and
[decision 90](../decisions/90-design-database-is-not-the-cause.md), so none
of them reported on any of these:

- **Every hull above corvette.** [Decision 82](../decisions/82-hull-section-attach-points.md)'s
  230 attach points are the single most valuable unmeasured thing in the project.
- **The dig sites, the anomalies and the story events** — unreached in all five
  runs since 2026-08-10
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
names. **Closed 2026-08-24 and reopened twice since: why no Trek empire appeared in 22,
or in 18.** The closure said `CUSTOM_EMPIRE_SPAWN_CHANCE` is 50 on a `10 = 1%`
scale — a **5% chance per AI slot** — so a few galaxies with none was the
ordinary outcome rather than a defect. The lever was real and is still in the
tree at 1000 (100%), safe only because the pool is all-Trek
([14](../decisions/14-remove-vanilla-prescripted-empires.md)) and deep enough to
fill a galaxy ([19](../decisions/19-stnh-minor-powers-as-ai-empires.md))
([86](../decisions/86-prescripted-empires-never-drawn.md)). **It was never the
cause**: three further galaxies at 100% drew zero
([88](../decisions/88-playable-gates-the-design-database.md)), and the
2026-08-26 save proved the pool itself is correct
([90](../decisions/90-design-database-is-not-the-cause.md)). The mechanism a
Trek galaxy actually needs is a static map plus `create_country` initializers —
[92](../decisions/92-create-country-initializers.md),
[static-galaxy-plan.md](static-galaxy-plan.md). **Do not treat this paragraph as
the live record**; [open questions](open-questions.md) is. **The Federation's
`spawn_enabled = always` still did not fire** and is still its own open
question. **The selector rows pointing at art no source mod
ships are closed**: 117 rather than the 196 recorded, two thirds of them a
misspelled directory or a substitute the tree named itself, the rest repointed
under one policy, and the tree held at zero by a new check
([85](../decisions/85-selector-textures-that-resolve.md)).

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
[70](../decisions/70-vulcan-city-framing.md) — **the last of these falsified
2026-08-24** by [87](../decisions/87-city-horizon-band.md). **Three things
outlive the runs themselves:**

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
