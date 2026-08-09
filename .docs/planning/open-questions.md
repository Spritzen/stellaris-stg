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

### The shipsets' weapons

Whether the nine Walshicus shipsets draw their weapons, and whether the pruned
event pictures took anything visible with them.

Then the weapon-mount re-derivation
([60](../decisions/60-mounts-share-existing-points.md),
[67](../decisions/67-source-art-hardpoint-names.md)) across all 27 shipsets — the
thing to look for is a mount that no longer breaks the pattern of the ones beside
it, and, on the 66% still placed from the bounding box, whether any of them reads
as badly as the corvette's third gun did.

> **Two shipsets graded, both on the corvette: Klingon and Cardassian, 2026-08-08.**
> The user reports the mounts on the Bortas-class and then on the Hideki-class —
> all three of the latter — well placed. Two of 27, and the corvette is the hull
> class the original defect was found on, so these are the strongest single checks
> available rather than a sample of the rest. **25 shipsets still ungraded.**

### The ruler clothes

The plainest form this question has ever taken: **the president in a Starfleet
formal robe, the Vulcan councillor in her white robe, the Terran empress in the ENT
mirror coat** — each empire in exactly the garment its `game_setup` row names, with
no index between the two.

If any one of them is still wrong, the one-texture selector is not being reached at
all and the portrait clone is the thing to doubt, not a number.
[Decision 69](../decisions/69-ruler-clothes-dedicated-selectors.md), which
falsified [68](../decisions/68-ruler-clothes-index-restored.md).

### The 2026-08-08 warning triage

Six `vendor.yml` renames changed which declaration the engine is left with, and a
rename that works produces no log record. Worth a look: whether habitats draw as
vanilla's orbital ring rather than a Suliban helix, and whether Real Space's nebula
globules and debris fields look the size the systems around them are built at.
[Decision 53](../decisions/53-duplicate-entity-triage.md).

### Music

The Federation anthem is in the ambient rotation and takes one hearing to confirm
([55](../decisions/55-federation-anthem.md)). Then the 22 track names now that they
have titles ([61](../decisions/61-music-player-track-names.md)) — what to listen
for is whether the four chosen main-theme titles sit right beside the eighteen
derived ones. And whether the rotation reads as 27 distinct recordings
([65](../decisions/65-music-rotation-dedupe.md)).

### Ship registries and their class names

Whether the Trek registries read right on the right hulls.
[Decision 59](../decisions/59-ship-name-pools.md)'s tonnage table is a judgement,
and **a Nebula-class name turning up on a corvette is the way it would be wrong.**

The class half now folds by the same table
([72](../decisions/72-ship-class-names.md)), so that sentence covers both and the
class name is the easier of the two to catch by eye — *Nebula – Interceptor* is
one glance. Three things new to that pass: whether the **Klingon and Romulan
lists read as their own** (the join that would have leaked Federation classes
into them was deleted before it shipped, so this is a check that nothing else
does the same); whether the **Defiant showing at two tonnages** — destroyer and
cruiser, which is STNH's own modelling — reads as wrong or as fine; and whether
any list still draws a class name that plainly belongs to another tonnage, which
would mean a `generic` token escaped demotion.

> **The empty tiers are filled by hand, and what needs eyes is the writing.**
> [Decision 73](../decisions/73-class-name-thematic-fill.md) gave the five
> tonnage-less empires a graded set, filled eight missing titans and placed
> Romulan's destroyers from names it already had — **21 of 22 playable empires
> now carry all five core tiers**, against 13. The registers are vanilla's own
> second idiom (NEC4's vices, AQU1's water), so what to look for is whether the
> invented English sits beside the canon names without sounding like a different
> mod: **`Stormwall` next to `Bolarus`, `Escrow` next to `Jaglom Shrek`**, and
> whether the Xindi species names read as classes or just as species labels.
>
> Two things left standing on purpose. **Malon's inherited pools name a type,
> not a class** — STNH declares `Waste Extraction Cruiser`, which will read as
> *"Waste Extraction Cruiser – Interceptor"*; it is a source's content, so it is
> flagged rather than cut. And **the 46 AI-only minors stay generic-only**,
> where `generic` is drawn 100% of the time and thin is not broken.

### The Trek anomalies

New on 2026-08-09 and the largest eyes-only surface the project has ever added
at once: **21 categories, 27 outcome events, 123 loc keys and ~3,500 words of
prose**, none of which any check can grade
([decision 75](../decisions/75-trek-anomalies.md)).

Three separate questions, and they fail differently:

- **Does the writing sound like Star Trek, or like a different mod?** The same
  test [decision 73](../decisions/73-class-name-thematic-fill.md) set for the
  class names, over four hundred words instead of one. The register is a
  survey officer's report, which is vanilla's own register — so what to watch
  for is a description that reads as a *plot summary* of an episode rather than
  as something a science officer wrote.
- **Does the picture match the text under it?** 24 STNH pictures, all looked at
  before they were chosen, and two rejected on tone — `mugato_world.dds` is
  animated in a cartoon style and `romulan_minefield.dds` does not depict a
  minefield. **Nine of the 24 are frames extracted from a 9315×264 animation
  strip**, and a wrong frame is the failure mode there.
- **Do the levels and rewards feel right?** An anomaly level gates which
  scientist can crack it. 21 categories span levels 1–6 and the mapping is a
  judgement, not a measurement.

> **And the framing question underneath all three.**
> [Decision 74](../decisions/74-event-picture-families.md) centre-crops these
> pictures from 620×264 to 450×150, losing 21 px top and bottom. For the 569
> that shadow a vanilla path that crop was verified against the vanilla scene
> they replace; these 24 shadow nothing, so **there is no control** — twelve
> were looked at and read correctly, which is a sample. A subject cropped at
> the chin is what it would look like. **The archaeology adds 27 more on the
> same terms**, and those 27 were each looked at in the exact crop before being
> chosen ([76](../decisions/76-trek-archaeology.md)) — so if a framing problem
> shows up, the anomalies' 24 are where to look first.

### The Trek archaeology

New on 2026-08-09 and the same shape one database over: **6 dig sites, 27 stage
events, 27 pictures, 117 loc keys and ~3,800 words**, none of which any check can
grade ([decision 76](../decisions/76-trek-archaeology.md)). The writing and
picture questions above apply here unchanged. Three that are specific to a dig:

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

New on 2026-08-09 and the last of the three
[decision 75](../decisions/75-trek-anomalies.md) scoped: **21 events, 21
pictures, 84 loc keys and ~4,000 words**, none of which any check can grade
([decision 77](../decisions/77-trek-story-events.md)). The writing and picture
questions above apply here unchanged. Four that are specific to a story event:

- **Do they fire at all, and at the right rate?** The pool is calibrated at 21%
  per five-year pulse against vanilla's own 18.6%, which works out at roughly
  one story event per decade per empire. If **none** appears in a long game the
  thing to doubt is the hook, not the weights — a custom on_action reached only
  by `fire_on_action` is exactly the arrangement `check_story_events` was
  written to police, and a check that has never failed in the live game is not
  yet evidence ([check design rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)).
- **Does the right empire get the right story?** Twelve are gated on species
  class. A Klingon empire seeing the Federation Council, or a Federation empire
  seeing none of its own two in a whole game, are the two ways the gate is
  wrong, and they fail in opposite directions.
- **Does a five-year flavour popup read as texture or as interruption?** This is
  the one question the anomalies and dig sites do not raise, because those are
  answers to something the player did. A story event arrives unbidden. If it
  reads as a tax on the pause key the weights are too high, and `1200 = 0` is
  the one number to move.
- **Does the register hold at country scope?** The dig sites are a survey
  officer's report; these are a service dispatch, written from inside an
  institution. The failure mode is a description that reads as a narrator
  summarising an episode instead of a civil servant writing a minute.

### Answered, kept here for the shape of the answer

- **Rooms and hidden empires — confirmed on the Cardassian run of 2026-08-08.**
  All four hidden empires are back in the empire list, and the designer's room list
  is *"realistically over 300"* against the 19 of
  [decision 48](../decisions/48-room-selector-merge.md).
- **Five of the six city sets were declared nowhere** — the Klingon run of
  2026-08-08 found it: the designer hid Vulcan, Cardassia, the Tholians and the
  Borg outright with `EMPIRE_DESIGN_INVALID_GFX_CULTURE`. The art was complete and
  the `room_selector` was right — only the `common/graphical_culture/` entry was
  missing, which nothing dangles on. Klingon was the one that worked, because its
  city name is also its *shipset* culture name and that is declared. Sweeping the
  rule found a fifth, `stg_minor_undine_vanguard`, which is AI-only and so can
  never appear in any log.
  [Decision 62](../decisions/62-city-set-cultures-undeclared.md).
- **Star names append rather than replace — settled 2026-08-08.**
  [Decision 44](../decisions/44-random-names-pools-append.md) had inferred it from
  two mods' file layouts and labelled itself as inference; the Cardassian run
  reports the galaxy map carrying *"a mix — Trek names, real stars, and catalogue
  designations (HD/HIP numbers)"*, which is exactly the three-way mix that
  distinguishes append from replace. The effective pool is **6,531**, not the 1,584
  decision 44 recorded. [Decision 52](../decisions/52-trek-star-names.md).
- **The city framing.** Answered and needed no change
  ([70](../decisions/70-vulcan-city-framing.md)).

---

## Log-level leftovers

*With their share of the 2026-08-07 run's 1,308 records.*

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
- **704 report-tier orphans** from the clutter closure (build of 2026-08-09;
  [decision 45](../decisions/45-clutter-pass.md) recorded 706, and `make
  validate` prints the live figure). At vanilla's own 4.9%
  leftover rate in `gfx/models`, a finding there is indistinguishable from
  Paradox's. Widening the prune scope means moving a tier in `tools/clutter.py`
  **with a new ratio written beside it**. [The clutter closure](../validation/clutter.md).
- **`descriptor.mod` declares `"Total Conversion"`, `"Species"`, `"Events"`,
  `"Graphics"`.** Accurate for a vendored merge, and cosmetic since STG is never
  published. Leave it.
- **The prescripted-power sweep is done and clean.** `stg_minor_powers` shipped
  with 78 of its 79 empire names truncated and 16 loc values that were the loc key
  itself; all 100 are repaired
  ([47](../decisions/47-minor-power-names-truncated.md)). The other three files —
  `stg_frontier_powers.txt`, `stg_major_powers.txt`, `stg_quadrant_powers.txt` —
  were swept and are clean: **0 leaked loc keys, 0 truncations** across all 22
  empires, against all 111 STNH empires.

  > The premise behind worrying about them was wrong in a specific way worth
  > keeping: **those three were hand-authored and only the minors were generated**,
  > and truncation is a *generator* failure. "Same hand" describes who chose the
  > content, not what produced the file, and only the second matters for this
  > defect class. [Decision 51](../decisions/51-prescripted-loc-scope.md).
