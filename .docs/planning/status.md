# Where things stand

> **What** — the current state of the build: phase completion, the `error.log`
> baseline, and what the last live runs established.
> **Open when** — starting a session, or before quoting any number about the
> build.
> **Then** — [Open questions](open-questions.md) · [Phases](phases.md) · [Live runs](../guides/live-runs.md)

*Last updated 2026-08-28, against the build of that date and the Klingon run of
2026-08-27. The build figures below are unchanged by the 28th's work — one
`vendor.yml` patch, one loc key, four new checks, a fifth widened, three deleted
name lists and 17 deleted colony-name tokens move the file count by three and
nothing else. **No live run has a write-up any more** — the run plans and analyses were
retired on 2026-08-27 ([89](../decisions/89-retired-run-write-ups.md)), and what
each run established now lives in the decision it produced and in the baseline
table below. Every number here has a date because
every number here goes stale — [style guide §6](../style-guide.md).*

| | |
|---|---|
| **Phase 0** — vendoring pipeline | **complete** |
| **Phase 1** — playable Federation | **complete**, run in-game repeatedly |
| **Phase 2** — the rest of the galaxy | **complete**. 99 prescripted empires (22 majors/quadrant/frontier, 77 minors; all playable, and all in the pool the generator draws from since the `playable = stg_never` gate was removed — **and the 2026-08-26 save proves all 99 reach the design database — and that no galaxy has yet drawn one**, see [decision 83](../decisions/83-design-database-is-not-the-cause.md); the mechanism a Trek galaxy actually needs is a static map plus `create_country` initializers — [decision 85](../decisions/85-create-country-initializers.md) — and **both ship and have now been run once**: 95 systems, 21 empires, 36 `create_country` blocks and the `prescripted_flags` join between them, [decision 86](../decisions/86-static-galaxy-scenario.md), graded by the 2026-08-27 Klingon run [87](../decisions/87-static-map-lanes-are-generated.md)) over 99 distinct species classes, 89 name lists, 36 generated home systems plus vanilla's Sol. `src/` declares **129** classes in all — the extra 30 are the STNH selector stubs of [decision 30](../decisions/30-declare-stub-species-classes.md) |
| **Phase 3** — art and identity | **complete 2026-08-08**. Clothing triggers, shipsets, weapon mounts, flags, rooms, city sets, loading screens, `paragon_backgrounds.txt`, the shipsets' 39 extra flags |
| **Phase 4** — polish | **started 2026-08-08**. Music, the ship registries and their class names, then the three slices [decision 70](../decisions/70-trek-anomalies.md) scoped: **21 Trek anomalies** ([70](../decisions/70-trek-anomalies.md)), **6 dig sites** ([71](../decisions/71-trek-archaeology.md)) and **21 story events** ([72](../decisions/72-trek-story-events.md)), all 2026-08-09. All three are shipped; what remains in the phase has no scope written for it |
| **Phase 5** — the clutter pass | **complete 2026-08-07** (pipeline work, taken out of order) |

## The build, as it stands

**Read every figure below off the build rather than off this page** —
`.vendor-manifest.json` and the `make validate` summary line carry the live
ones.

| | Build of 2026-08-28 |
|---|---|
| Files / size | **22,394 / 14.3 GiB** ([the per-tier split](../architecture/vendored-merge.md#size)) — three fewer than the 27th, the three name lists [93](../decisions/93-power-lists-win-the-contested-keys.md) deleted |
| Re-cut at harvest / pruned | 1,661 / **888** |
| Overwrites / additive skips | 952 / 220 |
| `make vendor` | 68 s |
| `make validate` | **0 warnings, 0 errors**, over **51 checks** — four more than yesterday. It warned 3 for part of 2026-08-28, on the contested name-list keys [decision 91](../decisions/91-src-contests-its-own-name-lists.md) found, and [decision 93](../decisions/93-power-lists-win-the-contested-keys.md) closed them the same day |
| `make docs` | **0 warnings, 0 errors** |
| `make gen-check` | **13 of 13 generators are fixpoints** |

**The prune has fallen 935 → 909 → 888 across three passes with no edit to
`vendor.yml`**, and that is the property worth knowing rather than the number:
the 27 pictures [decision 71](../decisions/71-trek-archaeology.md)'s dig sites
declare and the 21 [decision 72](../decisions/72-trek-story-events.md)'s story
events declare came back out of `.source/` by themselves, exactly as the
anomalies' 24 did. Declaring art un-prunes it; nothing has to be excluded.

`make validate` gained `check_anomalies`, `check_archaeology` and
`check_story_events` over Phase 4 and `make docs` gained a second family of
question — whether the documented inventory still matches the repo, not only
whether its citations resolve ([66](../decisions/66-doc-inventory-checks.md)).

**2026-08-22 added six, all from reading the docs rather than a live run.**
First three ([78](../decisions/78-widen-attach-points-and-two-new-checks.md)):
`check_section_attach_points` gained a **second scope** covering every hull
flying a borrowed frame, which is what finally guards
[decision 77](../decisions/77-hull-section-attach-points.md)'s 230 attach points;
`check_selector_texture_paths` is new and found ten malformed portrait paths that
two live runs had sampled three of; and **`make gen-check`** is a new target
asking whether each of the generators still reproduces `src/` exactly.
All of them do — eleven then, thirteen since
[decision 86](../decisions/86-static-galaxy-scenario.md) added
`gen_empire_flags.py` and `gen_static_galaxy.py`.

**Then three more, from working the three items the Vulcan run left marked
*waiting on a content call*** ([79](../decisions/79-shipset-descs-and-home-system-names.md)) —
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

**2026-08-28 added a forty-eighth, from the one queue item in the `error.log`
baseline rather than from the docs**: `check_anomaly_targets`, which asks whether
an `add_anomaly`'s `target` names a scope or a property of the planet it is
standing on ([90](../decisions/90-add-anomaly-target-scope.md)). Vanilla's floor
is **0 of 29**, and its allowlist is read out of vanilla at run time rather than
written into the check, so it survives a game patch
([rule 4](../validation/check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand)).
Its scope is the interesting part and it is a calibration result: a bare
`target = owner` is ordinary on other effects — **vanilla writes 8 of them**, over
3,067 `target =` sites in 124 effect kinds — and only `add_anomaly` guarantees the
unowned scope that makes one wrong.

**And a forty-ninth the same day, which found something nothing had been able to
see** ([91](../decisions/91-src-contests-its-own-name-lists.md)):
`check_src_key_contention` asks whether **two files we wrote** declare one
identifier. `check_key_conflicts` gates on two *sources*, so a key `src/`
contests with itself could never satisfy it — it was counting `common/name_lists`
among its 506 files the whole time. **Three keys were contested, and two are
major powers**: `STG_KLINGON`, `STG_VULCAN` and `STG_CAITIAN` are each declared
by a hand-written power list and an STNH-converted minor list, so one of each
pair never reaches the game and **filename sort decides which** — inconsistently,
the minor list winning twice and the power list once. Vanilla's floor in
`common/name_lists` is **0 across 78 keys in 76 files**.

**This is why `make validate` warned for part of the day**, and it was the check
working. **The content call was made the same day and the tree is clean again**
([93](../decisions/93-power-lists-win-the-contested-keys.md)): the hand-written
power list wins all three, the three converted duplicates are deleted, and
`src/common/name_lists/` is now **89 files declaring 89 keys** — one file, one
key, for the first time. The cost was measured rather than assumed by re-running
the two generators that emit name-list loc: **five keys**, not the ~107 the token
counts implied, because the rest were unique to the *file* and not to the tree.

It also settles a figure that was in the record wrongly. *"The gap is Caitian,
which has no `titan` block"* was measured against `stg_minor_caitian.txt`, the
file nobody intended to ship; the surviving one carries all five tiers, so **all
22 majors, quadrant and frontier powers carry all five** and the Caitian titan
exception is withdrawn. **A contested key hides a measurement as well as a name,
and the measurement outlives the defect.**

**And a fiftieth, from asking where else the forty-ninth's hole could be**
([92](../decisions/92-src-contests-its-own-loc-keys.md)).
`check_src_key_contention` closed `src/` contesting itself in `common/`;
`src/localisation/` has the identical shape and **neither existing check could
reach it** — `check_key_conflicts` walks `common/` only, and
`check_localisation` reads each file alone. `check_src_loc_key_contention` found
**six keys declared by two files of ours, and one of the six disagreed with
itself**: the Breen home system's third body asked for `STG_N_Portas` — the key
that means **"Portas"**, a colonizer ship — while `stg_home_systems_l_english.yml`
redeclared that same key as **"Portas V"**. So either the planet drew as *Portas*
or every Breen colony ship launched as *Portas V*, and **filename sort decided
which**. The name that was wanted already existed as its own key, `STG_N_PortasV`,
three lines away in a file the same generator reads.

**Fixed in `tools/gen_home_systems.py` and regenerated** — which makes four body-name
bugs that generator has now had, after the three
[79](../decisions/79-shipset-descs-and-home-system-names.md) found — and all six
duplicate declarations are gone. **Vanilla's floor is the strongest in the
file: 0 across 148,053 keys in 231 english files**, with no key repeated inside a
file either. The scope is again a calibration result: build-wide 16 keys are
declared twice by one source, **10 of them Real Space's own base/replace pair
with every value identical**, and 6 ours.

**And a fifty-first, from asking the same question a third time — which is the
one that came back empty** ([94](../decisions/94-src-contests-its-own-identities.md)).
The two checks above walk one directory each, `src/common/` and
`src/localisation/`, and `check_duplicate_entities` walks `*.asset` only. That
left **384 declarations of ours across 11 directories** — `events/`,
`prescripted_countries/`, `interface/`, `gfx/`, `map/` — where nothing had ever
put the question. `check_src_identity_contention` asks it, and **`src/` contests
nothing: 0 findings across 193 identities against vanilla's 11,857.**

**The zero is the result, and the third asking is what makes it one.** 91 found a
defect, 92 asked again and found another, 94 asks again and finds none — which is
what turns *"we fixed two instances"* into *"the shape is covered everywhere it
can occur"*, for the price of a session rather than a live run.

**And a widening rather than a fifty-second, which is where the day's last
defect was** ([95](../decisions/95-colony-pools-drop-home-system-bodies.md)).
`check_colony_name_collisions` asked whether a colony pool offers some empire's
**capital**; it now also asks whether it offers any other **body of its own
empire's home system** — a Klingon colony called Praxis while the real Praxis
orbits Qo'noS. **17 tokens across 12 empires were dropped from `planet_names`,
and every `ship_names` copy was left alone**, because that is where STNH puts
them and STG already did that half.

**The floor is what unblocked it, and it was not vanilla's nine home systems.**
STNH answers the same question **0 times** across the ten of its empires that
have both a real home system and a real pool — **four of them on a 32-body Sol
with a 160-name pool** — and vanilla is **0 of 8** comparable. STG was 12 of 37.

**The count in the record was wrong and the check found the missing one.** This
had been logged as 16 names over 11 empires; it is **17 over 12**. The extra is
the Terran Empire's **Mars** — its home system is Sol, so the body carries
vanilla's `NAME_Mars` while the pool offers our `STG_N_Mars`, one name under two
keys, invisible to a key-wise comparison. **Two drafts of the widened check
missed it too, and both failed by under-reporting**: the first resolved
localisation from the build alone (11 empires), the second added vanilla with
`rglob("*.yml")` and let **Portuguese** win the key, resolving Mars to *Marte*
and unmaking a finding it had reported a moment before (10). `*l_english.yml`
fixes it. **A clean `make validate` would have read as success both times** —
only reverting the repair caught either, which is
[rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)
paying for itself twice in one check.

**What the check cost was getting identity right, not contention**
([rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)),
and it was wrong three times first, confidently each time. In `events/` the
identity is the `id` inside a depth-0 event block, not the block key and not
every `id =` — counting those conflates **declaring** an event with **firing**
one and reports 33 vanilla collisions that are all references. In a `.gfx` it is
the `name` of each direct child of the container, read at that child's own depth
and in both written forms: an anchored `^\s*name = …$` found **0** of
`stg_paragon_backgrounds.gfx`'s 28 sprites, because that file writes each on one
line. **Five of the 11 directories exclude themselves** because vanilla contests
them — `interface` on per-charset fonts, `music` on `song`,
`map/setup_scenarios` on `setup_scenario` — and none of that is hand-listed.

**A zero finding is worth only as much as the proof the check can fail.** This
one reports **6** when pointed at the built tree — PD's `zzz_` override, a
base/`_fix` pair, three PD particles, UIOD's defines split, all of them a source
overriding itself — and 2 on an injected duplicate.

---

## The static galaxy — run once, and the mechanism works

**2026-08-27.** The mechanism [decision 85](../decisions/85-create-country-initializers.md)
identified is now in the tree, in four parts and one correction —
[decision 86](../decisions/86-static-galaxy-scenario.md):

| | |
|---|---|
| `src/map/setup_scenarios/stg_alpha_beta_quadrant.txt` | **95 systems, 21 empires, 162 hyperlanes**, every coordinate harvested from STNH's default galaxy map and scaled. The lanes are generated from those same positions — shipping without them, as 21 of STNH's 22 maps appear to, cost the 2026-08-27 run ([87](../decisions/87-static-map-lanes-are-generated.md)) |
| `src/common/solar_system_initializers/stg_home_systems.txt` | **36 `create_country` blocks**, one per home system, each guarded so the player's own empire is never duplicated |
| `src/common/prescripted_flags/stg_empire_flags.txt` | **99 country flags** — the join the plan did not have. It is what gives the *player's* copy of an empire the flag the map weights on |
| `check_static_galaxy` | five questions; vanilla floor **0**, STNH's own maps **4,265** |

**A Klingon run on 2026-08-27 graded it, and three of decision 86's four
questions came back good** ([87](../decisions/87-static-map-lanes-are-generated.md)):
the scenario appears in the picker and renders its name; **20 AI Trek empires
were created, one each**; exactly **one** Klingon Empire existed while playing
the Klingons, so the `prescripted_flags` guard fired; and no randomly generated
empire appeared. **Decisions 84, 85 and 86 are confirmed by a live save.**

**Question 2 failed and is now fixed.** The galaxy generated with **one**
hyperlane in 98 systems, because `random_hyperlanes = no` builds nothing and
STG had not vendored the start-of-game script STNH builds its network with.
The lanes are generated into the file now, and `check_static_galaxy` rejects a
lane-less static map — it used to wave one through, which is why `make validate`
reported clean over the defect. **Still unrun with lanes**, and that is the next
test.

**The picker is locked** ([88](../decisions/88-lock-the-galaxy-picker.md)):
YAGEM's twelve maps are excluded, vanilla's five are masked by files in `src/`
that declare nothing, and *The Known Galaxy* carries `default = yes`. **Exactly
one scenario declaration now reaches the engine** — so there is nothing to
select, and no random galaxy to fall back to. That also makes the map a single
point of failure, reversible in one commit.

**Two empires are deliberately absent from the map**: the Terran Empire, whose
Sol and Earth collide with the Federation's, and an AI Federation, because Sol
is Real Space's file and STG does not own it. Both are content calls in
decision 86.


## The `error.log` baseline

**The current baseline is the 2026-08-27 Klingon run**, the first against the
static galaxy — and the second in a row to be settled by the **save** rather than
by the log ([87](../decisions/87-static-map-lanes-are-generated.md)). The
2026-08-10 Federation run at the far end is still the deepest: ~11 hours, and the
only log so far that carried real defects rather than eyes-only findings.

| | **2026-08-27** Klingon | 2026-08-26 Vulcan | 2026-08-25 pm Vulcan | 2026-08-25 am Vulcan | 2026-08-24 Vulcan | 2026-08-22 Vulcan | 2026-08-10 Federation | 2026-08-08 |
|---|---|---|---|---|---|---|---|---|
| Records / size | **1,267 / 187 KB** | 1,315 / 195 KB | 1,280 / 191 KB | 1,335 / 190 KB | 1,315 / 208 KB | 1,264 / 187 KB | 2,251 / 228 KB | 1,261 / 187 KB |
| Startup window | 47.1 s | 48.3 s | 45.1 s | 48.5 s | 46.8 s | 55.4 s | 49.4 s | 49.3 s |
| Records **after** startup | **4** | 55 | 13 | 19 | 55 | 4 | 174 | 1 |
| Play window | not recorded | ~2 h 45 m | ~1 h | ~2.5 h | ~7 h | ~26 min | ~11 h | short |

**Read the post-init column, never the total.** 187–208 KB is the init-window
floor of this build and it has not moved in eight runs; against the ~1 MB a clean
vanilla run produces the volume is fine either way. **The 1 → 174 → 4 → 55 → 19
→ 13 → 55 → 4 swing is a change of run, not of build**: the short sessions opened
few screens.

**The 2026-08-27 run's four post-init records name no STG file** — three
`spawn_system` failures out of Planetary Diversity's `events/pd_unique.txt` and
one `PLANET_SCALE_SYSTEM` size mismatch (acked,
[41](../decisions/41-planet-scale-system-length.md)). All three `spawn_system`
records were **consequences of the lane defect**, not evidence of it: the log
named the symptom, and a galaxy with no hyperlanes produces no record at all
([87](../decisions/87-static-map-lanes-are-generated.md)).

**Five of 2026-08-26's 55 post-init records name STG files, and all five are now
fixed** — `select_empire_design_view.cpp:714`, five minor powers hidden from the
empire designer by two vanilla gates STG had no check for. Both rules were swept
across all 99 empires and found exactly those five;
`check_prescripted_empires` now carries all three
([decision 83](../decisions/83-design-database-is-not-the-cause.md)). The other
50 are the familiar vanilla mix, plus the `ariphaos_precursor_cosmic.txt` record
below, which recurred.

The 2026-08-25 evening run's **13 post-init records were eight distinct kinds**
over roughly an hour of play: `PLANET_SCALE_SYSTEM` (acked,
[41](../decisions/41-planet-scale-system-length.md)), three `add_intel` and two
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
[invariant 4](../guides/working-rules.md) applied — patched in `vendor.yml`, the
source kept. *(Not the dropped Ariphaos Unofficial Patch — same author, different
mod. [Decision 02](../decisions/02-drop-ariphaos.md).)*

**Fixed 2026-08-28** ([decision 90](../decisions/90-add-anomaly-target-scope.md)),
and it was worse than "one occurrence in an hour" made it sound. `cstorms.200` is
a `ship_event` whose `from` is the planet just surveyed, and its own trigger
requires that planet to be **uncolonised** — so `target = owner` asks an unowned
body for its owner and the adAkkaria anomaly was **never added on any planet the
event ever fired for**. The anomaly is the whole payload of the event. The tell
was eight lines up in the same file: the sibling event `cstorms.100` still
carried vanilla's `prev.owner`. The patch restores vanilla's own `root.owner`.

`check_anomaly_targets` now holds it there — **vanilla's floor is 0 of 29**, and
the check is calibrated by reverting the repair, at which point it names the same
file and the same line 127 the engine did. It is scoped to `add_anomaly` alone
because a bare `target = owner` is ordinary elsewhere: vanilla writes 8 of them
over 3,067 `target =` sites. **Not confirmed in game** — grading it means
surveying the adAkkaria system's barren bodies.

**None of 2026-08-24's 55 post-init records names an STG file either** — they are
vanilla's own event and trigger scripts plus Planetary Diversity's domed-base
decision, over seven hours of play. That is a volume reading only: **no analysis
was written for this run** ([those are written on request](../analysis/README.md)),
so the run's own observations were folded into the empire-spawn investigation
and recorded nowhere else.

**Two 2026-08-10 fixes are now confirmed in game by silence** — the 98-record
Planetary Diversity cluster and the 19 missing-localisation records are both
**0** in the 2026-08-22 run, and it exercised the thing that produced each. That
is the first time a live run has closed a defect in this project by measurement
rather than by inspection. What the Federation run of 2026-08-10 found, and what
each finding cost, is in decisions
[76](../decisions/76-random-names-are-loc-keys.md) through
[80](../decisions/80-selector-textures-that-resolve.md).

**What still has no in-game evidence at all.** Of the six runs since
2026-08-10, one ended early, four were played without a run plan and written up
only in the empire-spawn investigation that ends in
[decision 83](../decisions/83-design-database-is-not-the-cause.md), and the
sixth — 2026-08-27, Klingon — was a static-galaxy grading run that ended on a
galaxy with one hyperlane in it
([87](../decisions/87-static-map-lanes-are-generated.md)). None of them reported
on any of these:

- **Every hull above corvette.** [Decision 77](../decisions/77-hull-section-attach-points.md)'s
  230 attach points are the single most valuable unmeasured thing in the project.
- **The dig sites, the anomalies and the story events** — unreached in all six
  runs since 2026-08-10
  ([71](../decisions/71-trek-archaeology.md), [70](../decisions/70-trek-anomalies.md),
  [72](../decisions/72-trek-story-events.md)).
- **Habitats** ([50](../decisions/50-duplicate-entity-triage.md)), the ship class
  names and registries ([67](../decisions/67-ship-class-names.md)), and the music
  by ear.

**What the Vulcan run opened is closed** — its findings 2–4, all worked
2026-08-22 without a live run or a content call
([79](../decisions/79-shipset-descs-and-home-system-names.md)). **Two were
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
([13](../decisions/13-remove-vanilla-prescripted-empires.md)) and deep enough to
fill a galaxy — the 77 minor powers. **It was never the
cause**: three further galaxies at 100% drew zero even with the
`playable = stg_never` gate gone, and the
2026-08-26 save proved the pool itself is correct
([83](../decisions/83-design-database-is-not-the-cause.md)). The mechanism a
Trek galaxy actually needs is a static map plus `create_country` initializers —
[85](../decisions/85-create-country-initializers.md) — and it shipped and ran
on 2026-08-27, putting **20 AI Trek empires** in the galaxy on its first try:
[86](../decisions/86-static-galaxy-scenario.md),
[87](../decisions/87-static-map-lanes-are-generated.md),
[static-galaxy-plan.md](static-galaxy-plan.md). **Do not treat this paragraph as
the live record**; [open questions](open-questions.md) is. **The Federation's
`spawn_enabled = always` still did not fire** and is still its own open
question. **The selector rows pointing at art no source mod
ships are closed**: 117 rather than the 196 recorded, two thirds of them a
misspelled directory or a substitute the tree named itself, the rest repointed
under one policy, and the tree held at zero by a new check
([80](../decisions/80-selector-textures-that-resolve.md)).

The game has been the **native Linux build** since 2026-08-02
([decision 14](../decisions/14-native-linux-runtime.md)) — content unaffected,
deployment re-confirmed on it, startup and gfx counts **not comparable across that
boundary**.

Analyses are written only on request, one file per live run
([`../analysis/`](../analysis/README.md)), and **none is standing**: the two that
existed were retired on 2026-08-27 once every finding in them had landed in a
decision. A run named by a date in this file is named by the date it was
**played**.

---

## The four runs of 2026-08-08 — what still carries

Four runs in one day (Klingon, Cardassian, Terran, Vulcan), ~1,300 records each
bar the Klingon's 2,020. **Every finding across all four was eyes-only** and each
one is stated in full in its own decision — [20](../decisions/20-empire-designer-clothes.md),
[46](../decisions/46-room-selector-merge.md),
[54](../decisions/54-prescripted-rulers-unpin-clothes.md)–[56](../decisions/56-ship-name-pools.md),
[59](../decisions/59-city-set-cultures-undeclared.md)–[64](../decisions/64-source-art-hardpoint-names.md),
[65](../decisions/65-ruler-clothes-dedicated-selectors.md) — and the Vulcan
city framing they reviewed and left was **falsified 2026-08-24** by
[81](../decisions/81-city-horizon-band.md). **Three things
outlive the runs themselves:**

**Eyes-only is now the standard shape.** `make validate` was clean throughout,
and the 590-record room-selector `weight` defect visible in the Klingon count is
the last one a log has carried.

**The one falsification worth carrying forward.** The Vulcan run killed the
`clothes = N` index model outright — all six
rulers it pinned an index for wore a garment the model does not predict, so
`clothes = N` on a *shared* master selector is not an enumeration, and nothing in
the container can say what it is. The seven affected rulers took STNH's own
convention instead: a dedicated **one-texture** selector and `clothes = 0`
([65](../decisions/65-ruler-clothes-dedicated-selectors.md)). **The 2026-08-22
run vindicated that** — T'Pau draws in a Vulcan civilian robe, so the dedicated
selector is reached and the falsification is confirmed rather than merely
inferred.

**The 17 warnings standing on 2026-08-07 were triaged to 0, and two of them were
real defects** — five nebula and debris entities rendering at a third of System
Scale's size, and every empire's habitats at risk of drawing as a Suliban helix.
Decisions [50](../decisions/50-duplicate-entity-triage.md),
[51](../decisions/51-federation-texture-collisions.md),
[53](../decisions/53-starbase-modules-order.md). **The 2026-08-10 run graded the
nebula half and it is correct; the habitats have still not been seen after two
runs since.**
