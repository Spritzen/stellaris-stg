# What is actually open

> **What** — the questions still live, split by what would settle them: a live
> run, somebody's eyes, or a decision nobody has made yet.
> **Open when** — asking what to do next, or after the user reports a live run
> and you need to know what to look for.
> **Then** — [Live runs](../guides/live-runs.md) · [Status](status.md) · [Phases](phases.md)

Every question the plan originally marked `[OPEN]` is decided, and the
keep-or-drop calls on source mods are closed. The *rule* that closed them is what
carries forward, not the verdicts: **error count is a cost to pay down, not a
reason to drop a mod; sources go on content grounds only**
([decision 12](../decisions/12-fix-source-errors-dont-drop.md)).

---

## Needs a live run to settle — and all of it is eyes-only

**A reference that resolves produces no log record.** `make validate` clean is not
evidence for anything in this section — the standing lesson of decisions
[08](../decisions/08-stnh-art-shadows-vanilla.md) and
[42](../decisions/42-event-picture-geometry.md).

> **Read [ufp-run-remediation.md](ufp-run-remediation.md) and
> [analysis 2026-08-16](../analysis/2026-08-16.md) before working any item
> below.** Between them, the Federation run of 2026-08-10
> ([its plan](../runs/ufp-long-campaign.md)) and the Vulcan run of 2026-08-22
> ([its plan](../runs/vulcan-long-campaign.md)) answered most of this section, and
> several items now have a confirmed cause on disk rather than an eyes-only
> question — so the thing to do next is *grade a fix*, not re-diagnose.
>
> **Both runs ended before the long half of their plan.** The dig sites, the
> anomalies, the story events and every hull above corvette are **unreached
> twice** — unmeasured, not negative, and the reason a third run's first job is
> length rather than breadth. [The 2026-08-15
> audit](../analysis/2026-08-15.md), finding 1;
> [analysis 2026-08-16](../analysis/2026-08-16.md), "What this run could not
> reach".
>
> **The three questions the Vulcan run opened are all closed** as of 2026-08-22
> ([decision 84](../decisions/84-shipset-descs-and-home-system-names.md)) and
> none of them needed a live run or a content call. Two were mechanical and both
> were **larger than the analysis recorded** — 30 shipset description keys wrong
> rather than 7, and seven duplicate body names from three separate generator
> bugs rather than one paste. The third, the six cultures with no city art, was
> **not a defect at all**: `fallback` is the mechanism and vanilla's own header
> says so. See "Confirmed on disk" below.

### The shipsets' weapons

Whether the Walshicus shipsets draw their weapons — 17 of the 22 playable
empires fly one — and whether the pruned event pictures took anything visible
with them.

Then the weapon-mount re-derivation
([60](../decisions/60-mounts-share-existing-points.md),
[67](../decisions/67-source-art-hardpoint-names.md)) across all 27 shipsets — the
thing to look for is a mount that no longer breaks the pattern of the ones beside
it, and, on the 66% still placed from the bounding box, whether any of them reads
as badly as the corvette's third gun did.

> **Three shipsets graded, all on the corvette: Klingon and Cardassian
> 2026-08-08, Vulcan 2026-08-22.** The user reports the mounts on the
> Bortas-class, the Hideki-class — all three of the latter — and the Vulcan
> corvette as well placed. Three of 27, and the corvette is the hull class the
> original defect was found on, so these are the strongest single checks
> available rather than a sample of the rest. **24 shipsets still ungraded.**

> **The corvette was the only hull that could have graded well.** The
> 2026-08-10 run reported the Federation destroyer's stern mounts as plainly
> wrong, and the log gave the reason: **132 hulls across all 22 Trek shipsets were
> missing the section attach points their `ship_size` names**, so those sections
> never attached and their guns were placed against nothing. A corvette needs only
> `part1` and so was never affected — which is why three corvette gradings in a
> row looked like evidence about the shipsets.
>
> **Fixed the same day** — 230 attach points over 100 files
> ([82](../decisions/82-hull-section-attach-points.md)) — and **nothing about it
> is confirmed in game after two runs.** The 2026-08-22 run flew corvettes and
> science ships only, so the eight `has no attach point` records that fired on
> 2026-08-10 are **unmeasured, not confirmed gone**. Grading the mounts above
> corvette is now a live question rather than an unanswerable one, and it is the
> single most valuable unmeasured thing in the project.
> [ufp-run-remediation.md](ufp-run-remediation.md), item 1. The check that now
> guards the repair is [83](../decisions/83-widen-attach-points-and-two-new-checks.md);
> a clean check only says the locators exist.

### The ruler clothes

The plainest form this question has ever taken: **the president in a Starfleet
formal robe, the Vulcan councillor in her white robe, the Terran empress in the ENT
mirror coat** — each empire in exactly the garment its `game_setup` row names, with
no index between the two.

If any one of them is still wrong, the one-texture selector is not being reached at
all and the portrait clone is the thing to doubt, not a number.
[Decision 69](../decisions/69-ruler-clothes-dedicated-selectors.md), which
falsified [68](../decisions/68-ruler-clothes-index-restored.md).

> **Answered for Vulcan, 2026-08-22: T'Pau draws in a Vulcan civilian robe.**
> The dedicated one-texture selector is reached, which is the clean test
> [decision 69](../decisions/69-ruler-clothes-dedicated-selectors.md) was waiting
> for. **The president and the Terran empress are still ungraded** — different
> empires, different selectors, and a Vulcan run says nothing about either.
>
> **The malformed paths behind the 2026-08-10 "president is still wrong" report
> are now all gone.** 29 rows were patched that day in the *male* master
> selector; the **female** master was never touched and still held eleven, which
> the Vulcan run logged three of. All eleven landed 2026-08-22 and
> `check_selector_texture_paths` holds the tree at zero
> ([83](../decisions/83-widen-attach-points-and-two-new-checks.md)).
>
> **One caveat keeps this from being fully clean**: the same sweep found **196
> selector rows pointing at textures that exist in no source mod at all**, each
> of them a silent fallback and each needing a content call. If a ruler is still
> wrong, check whether its garment is one of the 196 before doubting the selector
> again. [ufp-run-remediation.md](ufp-run-remediation.md), item 2.
>
> **And the clothes-slider wrap is arithmetic, not a defect.** The designer's
> slider runs to 499; the male pool is 495 wide and the female 472, so
> 496–499 address nothing — exactly the range the 2026-08-10 run named.
> **Prediction the next run can falsify in a minute: on a female portrait the
> wrap begins at ~472, on a male at ~496.**
> [Analysis 2026-08-16](../analysis/2026-08-16.md).

### The 2026-08-08 warning triage

Six `vendor.yml` renames changed which declaration the engine is left with, and a
rename that works produces no log record. The 2026-08-10 run graded one half —
**nebula sizing on the galaxy map is correct**. What is still unseen: whether
habitats draw as vanilla's orbital ring rather than a Suliban helix.
[Decision 53](../decisions/53-duplicate-entity-triage.md).

### Music

**Closed 2026-08-10, by measurement rather than by a change.** The anthem is in
rotation ([55](../decisions/55-federation-anthem.md)) and the track names are all
distinct ([61](../decisions/61-music-player-track-names.md)). Nothing in the tree
needed fixing; the *expectation* did.

> **The two figures count different things, and a run plan must carry both.** The
> player lists **55 declarations**; the rotation is **27 playlist entries**,
> reproducing [decision 65](../decisions/65-music-rotation-dedupe.md) exactly. A
> run reporting "approx. 70 tracks" is eyeballing the 55.
> [ufp-run-remediation.md](ufp-run-remediation.md), item 6.

What is still ungraded by ear: whether the four chosen main-theme titles sit
right beside the eighteen derived ones.

### Ship registries and their class names

Whether the Trek registries read right on the right hulls, and whether the class
names fold by the same tonnage table without leaking across empires.
[Decisions 59](../decisions/59-ship-name-pools.md),
[72](../decisions/72-ship-class-names.md),
[73](../decisions/73-class-name-thematic-fill.md). Five things to watch, in
descending order of how obviously they would be wrong:

- **A Nebula-class name on a corvette.** The tonnage table is a judgement and
  this is how it fails. The class half is the easier of the two to catch by eye:
  *Nebula – Interceptor* is one glance.
- **Whether the Klingon and Romulan lists read as their own.** The fuzzy join
  that would have put Saber, Steamrunner and Sovereign in the Klingon fleet was
  deleted before it shipped; this is a check that nothing else does the same.
- **Whether the invented English sits beside the canon names.** Decision 73
  filled the empty tiers from vanilla's own second idiom (NEC4's vices, AQU1's
  water), so what to look for is `Stormwall` next to `Bolarus` and `Escrow` next
  to `Jaglom Shrek` — and whether the Xindi species names read as classes or
  just as species labels. **21 of 22 playable empires now carry all five core
  tiers**, against 13 — **the gap is Caitian, which has no `titan` block**
  (`src/common/name_lists/stg_minor_caitian.txt`, measured 2026-08-22), so a
  Caitian titan draws from `generic` and that is the one empire where a
  tonnage-mismatched class name is expected rather than a defect.
- **Whether the Defiant showing at two tonnages** — destroyer and cruiser, which
  is STNH's own modelling — reads as wrong or as fine.
- **Whether any list draws a class name plainly belonging to another tonnage**,
  which would mean a `generic` token escaped demotion.

> Two things left standing on purpose. **Malon's inherited pools name a type, not
> a class** — STNH declares `Waste Extraction Cruiser`, which will read as *"Waste
> Extraction Cruiser – Interceptor"*; it is a source's content, so it is flagged
> rather than cut. And **the 46 AI-only minors stay generic-only**, where
> `generic` is drawn 100% of the time and thin is not broken.

### The Trek anomalies

**21 categories, 27 outcome events, 24 pictures, 123 loc keys and ~3,500 words**,
none of which any check can grade
([decision 75](../decisions/75-trek-anomalies.md)). Three separate questions, and
they fail differently:

- **Does the writing sound like Star Trek, or like a different mod?** The
  register is a survey officer's report, which is vanilla's own — so what to
  watch for is a description that reads as a *plot summary* of an episode rather
  than as something a science officer wrote.
- **Does the picture match the text under it?** All 24 were looked at before
  they were chosen, and two rejected on tone. **Nine of the 24 are frames
  extracted from a 9315×264 animation strip**, and a wrong frame is the failure
  mode there.
- **Do the levels and rewards feel right?** An anomaly level gates which
  scientist can crack it and how often the roll fails. The mapping is a
  judgement, but there is a number to hold it against
  ([78](../decisions/78-phase-4-count-corrections.md)):

  | level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | mean |
  |---|---|---|---|---|---|---|---|---|
  | STG, 21 categories | 2 | 2 | 5 | 3 | 6 | 3 | 0 | **3.86** |
  | vanilla base game, 40 | 12 | 14 | 6 | 4 | 3 | 0 | 1 | **2.4** |

  Vanilla puts 65% of its base-game categories at level 1–2 and 10% at level 5+;
  STG puts 19% and **43%**. The merged pool still leans vanilla (348 categories),
  so the galaxy is not harder — but **the Trek half is the slow, failure-prone
  half**, which is the half the player is meant to notice, and early-game
  scientists will bounce off it.

> **And the framing question underneath all three.**
> [Decision 74](../decisions/74-event-picture-families.md) centre-crops these
> pictures from 620×264 to 450×150, losing 21 px top and bottom. For the 569
> that shadow a vanilla path that crop was verified against the vanilla scene
> they replace; **the anomalies' 24 shadow nothing, so there is no control** —
> twelve were looked at and read correctly, which is a sample. A subject cropped
> at the chin is what it would look like. The archaeology's 27 and the story
> events' 21 were each looked at in the exact crop before being chosen
> ([76](../decisions/76-trek-archaeology.md),
> [77](../decisions/77-trek-story-events.md)), **so if a framing problem shows
> up, the anomalies' 24 are where to look first.**

### The Trek archaeology

**6 dig sites, 27 stage events, 27 pictures, 117 loc keys and ~3,800 words**
([decision 76](../decisions/76-trek-archaeology.md)). The writing and picture
questions above apply here unchanged. Three that are specific to a dig:

- **Do they turn up at all?** This is the one question a live run answers
  cheaply and nothing else answers. The sites spawn through `ancrel.9999` on
  `on_survey_planet`, at vanilla's own 5-in-405 roll, weighted on planet class —
  so the test is whether a dig site appears in the situation log over a few dozen
  surveys, and whether more than one of the six ever shows in one galaxy. If
  **none** appears, the weights are the thing to doubt, not the content.
- **Does a five-stage dig hold up over the hours it takes?** An anomaly is one
  popup; a site is four or five, spread across a scientist's career. The failure
  mode is a middle stage that reads as filler between the hook and the payoff.
- **Do the finale choices feel like choices?** Five of the six end on two options
  with different modifiers — take the blade or seal the hall, return the ark or
  keep reading it, wake the mechanism or backfill the shaft. If one side is
  obviously correct every time, it is not a choice, it is a tax.

### The Trek story events

**21 events, 21 pictures, 84 loc keys and ~4,000 words**
([decision 77](../decisions/77-trek-story-events.md)). The writing and picture
questions above apply here unchanged. Four that are specific to a story event:

- **Do they fire at all, and at the right rate?** The pool is calibrated against
  vanilla's own 18.6% per five-year pulse, and `stg_recent_story` blanks the
  pulse after a hit, so the long-run figure is ~17% for the Federation and ~13%
  for an ungated empire — roughly one story event per decade per empire
  ([78](../decisions/78-phase-4-count-corrections.md) has the three tiers). If
  **none** appears in a long game the thing to doubt is the hook, not the
  weights: a custom on_action reached only by `fire_on_action` is exactly the
  arrangement `check_story_events` was written to police, and a check that has
  never failed in the live game is not yet evidence
  ([check design rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)).
- **Does the right empire get the right story?** Twelve are gated on species
  class. A Klingon empire seeing the Federation Council, or a Federation empire
  seeing none of its own two in a whole game, are the two ways the gate is
  wrong, and they fail in opposite directions.

  > **And a third way, which is not a broken gate and would not read as one:
  > eleven of the 22 playable empires are outside the gate entirely** — BOL, BRE,
  > THO, CAI, XIN, SUL, YRI, KRE, MAL, VID and the mirror **TER**, plus all 79
  > AI minors. They see only the eight open events. **A Malon player reporting "I
  > never see my own story" is reporting the content, not the gate**, so ask
  > which empire before doubting the trigger. Left open as a content gap;
  > growing the pool is cheap, because `random_events` fires exactly one winner
  > ([78](../decisions/78-phase-4-count-corrections.md)).
- **Does a five-year flavour popup read as texture or as interruption?** This is
  the one question the anomalies and dig sites do not raise, because those are
  answers to something the player did. A story event arrives unbidden. If it
  reads as a tax on the pause key the weights are too high, and `1200 = 0` is
  the one number to move.
- **Does the register hold at country scope?** The dig sites are a survey
  officer's report; these are a service dispatch, written from inside an
  institution. The failure mode is a description that reads as a narrator
  summarising an episode instead of a civil servant writing a minute.

### Answered by the runs of 2026-08-08

Kept as one line each, because the *shape* of the answer is what transfers; the
finding itself is in the decision.

- Rooms and hidden empires — all four hidden empires are back and the designer's
  room list is *"realistically over 300"*
  ([48](../decisions/48-room-selector-merge.md),
  [62](../decisions/62-city-set-cultures-undeclared.md)).
- Star names **append** rather than replace, confirmed by the three-way mix on
  the galaxy map — the property, not the total, is what carries: STG's 806 names
  add to Real Space's and YAGEM's 5,702 rather than displacing them
  ([52](../decisions/52-trek-star-names.md), correcting
  [44](../decisions/44-random-names-pools-append.md)).
- The Vulcan city framing needed no change
  ([70](../decisions/70-vulcan-city-framing.md)).

---

## Confirmed on disk — all three worked, and one was not a defect

*[Decision 84](../decisions/84-shipset-descs-and-home-system-names.md), 2026-08-22.
This section held three items each described as needing somebody to decide what
the right answer was. **None of them did.** Two were mechanical once measured
properly and both turned out larger than recorded; the third dissolved on
reading vanilla's own file header. The section is kept, rather than deleted,
because the pattern is the lesson: **each had been measured once, and each
measurement stopped one question short of the mechanism.***

- **The shipset descriptions — fixed, and it was 30 of 30 rather than 7.**
  Seven keys named a *city-set* culture instead of a *shipset* one and 23 flown
  cultures had no key at all, so every Walshicus set — the Federation's own
  `starfleet_tng` and the Vulcans' `vulcan` included — drew a raw key. Seven
  renames plus sixteen new descriptions, the new prose grounded in the hull
  textures rather than in lore. `check_shipset_descriptions` now asks both
  directions; vanilla's floor is **0 and 0**, while vanilla keys only 20 of its
  52 declared cultures — **flown is the population, declared is the bound.**
- **The 40 Eridani duplicate — fixed, and it was three bugs in six systems.**
  Recorded as *"small, certain, one edit"*; swept across all 37 generated home
  systems it was **seven duplicate names from three unrelated causes** — a
  `sub_blocks` that matched at every nesting depth, a star/capital de-collision
  rule blind to the bare `star` keyword, and STNH naming both moons of S'latas
  alike. All three fixed in `tools/gen_home_systems.py`, because the file is
  generated. `check_home_system_body_names` guards it: vanilla fails the
  question **62 times in 357** initializers overall and **0 times in 9** home
  systems, which is where the scope comes from.
- **The six cultures with no city art — NOT A DEFECT, and no call was needed.**
  Vanilla's own `00_graphical_culture.txt` says in its header that `fallback`
  lets the game use another culture's asset when one is missing, and all six
  declare `fallback = mammalian_01`. **24 of vanilla's own 52 declared cultures
  ship no city art either** — 46%, so the premise could never have been the
  rule. `check_graphical_culture_art` asks the invariant that does have a floor
  — an offerable culture reaches art, its own or its fallback's — and vanilla is
  0 of 22 with STG 0 of 41. The orphan `generic_01`–`generic_06` art is
  `check_unreferenced`'s question and [decision 45](../decisions/45-clutter-pass.md)'s
  standing policy, not a defect.

> **What generalises, and it has now happened twice.** [Decision
> 83](../decisions/83-widen-attach-points-and-two-new-checks.md) struck
> [analysis 2026-08-16](../analysis/2026-08-16.md) finding 5 for the same
> reason this strikes finding 2: **both were measurements taken without reading
> the thing that had already measured them** — a helper in `tools/validate.py`
> in one case, three lines of vanilla's own file header in the other. Before
> writing a check for a finding, read vanilla's header and the check next door.

**What genuinely still needs eyes** out of all this: whether the sixteen new
shipset descriptions read as Trek, and whether the four stars whose colliding
names were dropped now draw with their system's name the way vanilla's twelve
unnamed ones do.

## Log-level leftovers

*Init-window groups that are third-party or reviewed, listed with their share of
the 2026-08-07 run's 1,308 records — the run that triaged them.
[Analysis 2026-08-16](../analysis/2026-08-16.md) has the current per-group
breakdown of the init window, which has not changed shape since.*

- **ASB's projectile reimplementations — 213 records, the largest class left.**
  `alt_*` and `ap_*` in `gfx/projectiles/` redeclare vanilla names and the engine
  keeps one. **Still open: which one renders.**
- **SBX — 67 records**, naming techs from an older Stellaris, plus the only in-play
  findings in that run. SBX also renumbers vanilla's citadel gun slots, breaking
  vanilla's own design ([39](../decisions/39-sbx-citadel-slot-renumbering.md)). Its
  `advanced_military_program` — the one `potential` block in either its file or
  vanilla's that switched to `solar_system` unguarded — is patched as of 2026-08-07
  ([46](../decisions/46-coalition-of-hope-takes-vul.md)).
- **143 duplicate textures** where STNH's `shared_assets/` meets Walshicus'
  `stnc_shipset_shared/` — [the conflict register](../architecture/conflict-register.md)
  explains why last-wins is correct here. Now watched by
  `check_duplicate_textures` and acked by directory, so the reviewed library stays
  silent and a *new* collision reports.
- **`legend` — 2 records**, inside vendored Klingon art at
  `gfx/portraits/asset_selectors/klingon/klingon_male_clothes_combined.txt:42,48`.
- The small defects of that run and what each cost are in
  [decision 40](../decisions/40-live-run-2026-08-07-repairs.md).

---

## Reviewed and deliberately left alone — do not reopen without new evidence

- **Real Space's oversized systems.** `System Mintaka … is too big` is Real Space's
  own initializer against Real Space's own raised threshold, five of its 198
  systems exceed it, and System Scale makes them *smaller*. Changing either the
  geometry or the threshold would be inventing or silencing. STG's own home systems
  top out at 515 and are clear.
  [Decision 36](../decisions/36-oversized-real-space-systems.md).
- **`PLANET_SCALE_SYSTEM` keeps its 8 entries.** The engine measures it against
  `ZOOM_STEPS_SYSTEM`, an array no script can set, and the visual test found
  13-against-8 rendering correctly.
  [Decision 43](../decisions/43-planet-scale-system-length.md).
- **703 report-tier orphans** from the clutter closure (build of 2026-08-10;
  [decision 45](../decisions/45-clutter-pass.md) recorded 706, and `make
  validate` prints the live figure). At vanilla's own 4.9%
  leftover rate in `gfx/models`, a finding there is indistinguishable from
  Paradox's. Widening the prune scope means moving a tier in `tools/clutter.py`
  **with a new ratio written beside it**. [The clutter closure](../validation/clutter.md).
- **`descriptor.mod` declares `"Total Conversion"`, `"Species"`, `"Events"`,
  `"Graphics"`.** Accurate for a vendored merge, and cosmetic since STG is never
  published. Leave it.
- **Nine `Failed to find entity … for attachment` records every run** — five
  Romulan bird-of-prey sections, three Klingon cores, one named `_test_`. Triaged
  in [decision 37](../decisions/37-attach-edges-into-pruned-art.md): STNH art
  whose consumers live in a `common/` STG does not vendor, with a twelve-line
  rationale under `attach_target_ack` in `vendor.yml`. Stable across three runs
  and costing nothing at runtime. **The shape worth keeping: the ack silences
  `check_attach_targets`, not the engine** — nine records a run is its standing
  price — **and it is scoped by *file***, so a genuinely new unresolved attach in
  those four files would also go unreported.
- **The prescripted-power sweep is done and clean.** `stg_minor_powers` shipped
  with 78 of its 79 empire names truncated and 16 loc values that were the loc key
  itself; all 100 are repaired
  ([47](../decisions/47-minor-power-names-truncated.md)). The other three files
  were swept and are clean: **0 leaked loc keys, 0 truncations** across all 22
  empires.

  > The premise behind worrying about them was wrong in a specific way worth
  > keeping: **those three were hand-authored and only the minors were generated**,
  > and truncation is a *generator* failure. "Same hand" describes who chose the
  > content, not what produced the file, and only the second matters for this
  > defect class. [Decision 51](../decisions/51-prescripted-loc-scope.md).

---

## Queued, and deliberately not started

**More Events Mod and its compatch are subscribed for a later integration pass**
— in scope, waiting on this page's eyes-only surface being graded first.
**Only the timing is closed**; which paths are taken and how MEM's events sit
beside Trek ones are the pass itself and are open.
[Decision 80](../decisions/80-mem-integration-deferred.md).
