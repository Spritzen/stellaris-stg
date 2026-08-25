# The long Vulcan run — what to cover

> **What** — an ordered checklist for a long Confederacy of Vulcan playthrough:
> what to do, what to look at, what "right" looks like, and what this empire
> cannot reach.
> **Open when** — before launching this run, and again before reporting back.
> **Then** — [Live runs](../guides/live-runs.md) · [What the last run left open](../planning/ufp-run-remediation.md) · [Open questions](../planning/open-questions.md) · [The Federation run before it](ufp-long-campaign.md)

Written 2026-08-11, for the first run against the build that carries
[decision 81](../decisions/81-random-names-are-loc-keys.md) and
[decision 82](../decisions/82-hull-section-attach-points.md). **Nothing either of
those fixed has been seen in game**, and this run is what grades them.

**Write observations inline, under the item they answer**, in a fenced block
opening with `#OBSERVATIONS` — the convention
[the Federation plan](ufp-long-campaign.md) uses. An observation under the wrong
item is worth much less than one under the right item, because the item carries
the expectation it should be read against.

---

## Before launch

- [done] **Run the loop and confirm it is clean.** `make vendor && make validate &&
      make docs`. The mod folder is a symlink, so the rebuild is live the moment
      it finishes.
- [done] **Copy the old `error.log` aside first.** The game truncates every file in
      `/paradox/stellaris/logs/` at startup, so launching destroys the 2026-08-10
      baseline this run has to be compared against:
      `cp /paradox/stellaris/logs/error.log /paradox/stellaris/logs/error.log.2026-08-10`
- [done] **Restart the launcher**, enable *Star Trek Galaxies* in the playset,
      launch.
- [] **Note the wall-clock start and end.** The last analysis leaned on the
      session window to separate init errors from in-play ones, and that
      separation changes the conclusion completely
      ([live-runs.md](../guides/live-runs.md)).
```markdown
#RUNTIMES
- 2026-08-22 14:05 - Launched Stellaris from Paradox launcher.
- 2026-08-22 14:35 - Started a new game.
```
- [ ] **Do not relaunch after you stop.** The log is per-session; a second launch
      wipes the run you just played.

## Galaxy settings, because they decide what this run can measure

- [X] **Force-spawn two or three Trek empires from the designer's own toggle.**
      This is the highest-value single setting on the page. The last run met 22
      empires and **none of them was Trek**; three hypotheses were eliminated by
      measurement and what is left cannot be answered from the container. If the
      forced ones appear, the content is fine and pool weighting is the whole
      story. **If a force-spawned one fails to appear, that is a real defect and
      a much sharper one to chase.**
      [ufp-run-remediation.md](../planning/ufp-run-remediation.md), item 4.
```markdown
#OBSERVATIONS
- Forced spawn is only an option for player made empires
```
- [X] **Pick neighbours you want graded.** Klingon, Romulan and Cardassian are
      the sets with the most art behind them; a forced Klingon neighbour gets you
      a third shipset in the same run for free.
```markdown
#OBSERVATIONS
- This was never something you can set
```
- **Large galaxy, 600–1000 stars, 20+ AI empires.** This is a survey-led run
      again, and every question below is downstream of how many bodies get
      surveyed.
```markdown
#OBSERVATIONS
- Galaxy Size 600, AI Empires 18, No Adv. AI Starts, 1 Fallen Empire
```
- **Ironman off.** You will want to reload, re-open a screen and look twice.
- **Three or more science ships from the start**, kept fed and kept moving.
      Half of this checklist is unreachable otherwise.

---

## In the empire designer, before you press start

Ten minutes here settles more eyes-only questions than the next two hours will.

- **T'Pau's clothes.** Her row names `portrait = stg_vul_ruler`,
      `texture = 0`, `clothes = 0` on a dedicated one-texture selector pointing
      at `civ_vulcan_female_clothes_02.dds`, which is present on disk. She should
      be in a **Vulcan civilian robe** — not a Starfleet uniform, not a random
      garment. The 29 malformed texture paths that muddied this question last
      time are fixed, so **this is now a clean test of
      [decision 69](../decisions/69-ruler-clothes-dedicated-selectors.md)**: if
      she is still wrong, the dedicated selector is not being reached at all and
      the portrait clone is the thing to doubt, not an index.
```markdown
#OBSERVATIONS
- Confirmed she is in a civilian robe
```
- **Then walk the clothes slider a long way** — 1, 20, 100, 300, 480, 499 —
      and say whether high indices redraw as index 1. **The selector rows
      pointing at textures no source mod ships are gone** — 196 when this plan
      was written, 117 when it was measured, 0 since 2026-08-24
      ([85](../decisions/85-selector-textures-that-resolve.md)) — so a wrap seen
      now is the slider arithmetic and nothing else.
      [ufp-run-remediation.md](../planning/ufp-run-remediation.md), item 2.
```markdown
#OBSERVATIONS
- I'm not scrolling through all these. I got to 286 with no duplicates before getting RSI.
```
- **The room behind her** is `vulcan_room` — a Trek room, not a vanilla
      personality room ([48](../decisions/48-room-selector-merge.md)).
```markdown
#OBSERVATIONS
- Confirmed background is vulcan
```
- **The flag draws**: `Vulcan.dds` from the `trek` category on the `circle`
      background, burgundy on desert yellow
      ([49](../decisions/49-flags-city-sets.md)).
```markdown
#OBSERVATIONS
- Confirmed flag is correct
```
- **The city preview, and this is the one to be precise about.** The art is
      **not** the suspect — every city layer in the tree sits at vanilla's
      800×400 canvas and every room at 952×340 (build of 2026-08-10). The suspect
      is **UI Overhaul Dynamic's rect**: it replaces `customize_species.gui`
      wholesale, and art cut for vanilla's canvas is being drawn into somebody
      else's frame. So the question is not "does it look small" but **"does it
      look small *here* and correct on the planet screen later"** — because one
      file cannot satisfy two rects, and which of the two is wrong decides the
      fix. [ufp-run-remediation.md](../planning/ufp-run-remediation.md), item 8.
```markdown
#OBSERVATIONS
- All pictures look correct except the following list where the city picture is scaled to small: Bajoran, Trill, Andoran, Bolian, Breen, Hologram, Xepolite, Zakdorn, Monean, Medusan.
```
- **The ship-appearance list showing species names is not a defect** —
      vanilla has no shipset name key either, so do not report it again. **What
      to look at is the description panel beside it.** Fourteen
      `_shipset_desc` strings were written; the Vulcan empire flies the
      `vulcan` culture and the description is keyed `vulcan_01`, which is a
      **city-only** culture. Expect the panel to be **empty** for Vulcan, and say
      so either way — that is a one-glance answer to whether the key name is
      wrong.
```markdown
#OBSERVATIONS
- Vulcan Description box shows vulcan_shipset_desc instead of the actual description.
```
---

## The first hours — survey, because that is the point of this run

**Open the situation log and leave it open.** Anomalies, dig sites and story
events all report there, and it is the one screen that turns this run into
evidence.

### 40 Eridani, before you leave it

- **Walk the home system once and read every body's name.** It should be
      **40 Eridani**, capital **Vulcan** (a desert world), with T'Khut,
      T'Rukhemai, Delta Vega, Keid, Ket-Cheleb, Kerkhov and 40 Eridani B and C
      around it — thirteen bodies in a trinary
      ([25](../decisions/25-real-home-systems.md)). **A name showing as a raw key
      or with underscores in it is the finding**, and it is the same family as
      the star-name defect below, one database over.
```markdown
#OBSERVATIONS
- Confirmed it is **40 Eridani**, capital **Vulcan** (a desert world), with T'Khut, T'Rukhemai, Delta Vega, Keid, Ket-Cheleb, Kerkhov and 40 Eridani B and C around it.
- System is a binary star systems
```
- **The ship prefix reads `VSS`.**
```markdown
#OBSERVATIONS
- Confirmed VSS prefixes
```
### The star and nebula names

- **One pass over the galaxy map, reading names.** 328 localisation keys
      landed on 2026-08-10 for names that had none, so `Arachnid_Nebula`,
      `Class_9_Nebula` and `Kullat_Nunu` should now read as **Arachnid Nebula**,
      **Class 9 Nebula** and **Kullat Nunu**. **Any remaining underscore is a
      missed key**; a name that reads badly in plain English is a different
      finding and also worth writing down — **328 display values are unread and
      no check can grade one**
      ([81](../decisions/81-random-names-are-loc-keys.md)).
```markdown
#OBSERVATIONS
- Confirmed observable names in the galaxy view appear with no underscores.
```
### The Trek anomalies — the largest ungraded surface in the project

**21 categories, 27 outcome events, 24 pictures and ~3,500 words, and nothing in
the container can grade any of it** ([75](../decisions/75-trek-anomalies.md)).
The last run graded four *story* events and no anomalies, so this is close to
untouched.

- [ ] **Write down every Trek anomaly you meet, by name and level.** STG adds 21
      categories to a merged pool of ~348, so **most anomalies will still be
      vanilla's** — a run with few Trek ones is not a defect. The observed sample
      is worth more than any impression.
- [ ] **Does the picture match the text, and is it framed right?** This is the
      highest-value look in the whole run. These 24 pictures are the only ones in
      the project whose 620×264 → 450×150 centre-crop has **no vanilla control
      behind it** ([74](../decisions/74-event-picture-families.md)). **A subject
      cropped at the chin is what the failure looks like.**
- [ ] **Nine of the 24 are frames pulled from an animation strip**, and the
      failure there is a picture that is technically fine but shows the **wrong
      moment**.
- [ ] **Does the writing sound like Star Trek, or like a different mod?** The
      register is a survey officer's report, which is vanilla's own. Watch for a
      description that reads as a **plot summary of an episode** rather than as
      something a science officer wrote.
- [ ] **Do the levels feel like a wall?** STG puts 43% of its categories at level
      5+ against vanilla's base-game 10%, and 19% at level 1–2 against vanilla's
      65% ([78](../decisions/78-phase-4-count-corrections.md)). The galaxy is not
      harder overall, but **the Trek half is the slow, failure-prone half** and
      that is the half you are meant to notice. **A materialist empire with early
      research bonuses is the fairest possible test of it** — say whether your
      scientists still bounce off.
- [ ] **Nine of the 21 are `max_once` or `max_once_global`** — the ones naming a
      specific object (Tox Uthat, the Iconian gateway, the planet-killer remnant,
      the Omega signature, the deep-space probe). **Seeing one of those twice in
      a galaxy is a real finding.**

---

## The long game — what only hours can reach

### The Trek dig sites — the hole in the record

This is the item the run is being lengthened for. It went **unreached** last
time, which is unmeasured, not negative.

- [ ] **Do they turn up at all?** Sites are placed by vanilla's `ancrel.9999` on
      `on_survey_planet` — a 5-in-405 roll per surveyed body, then chosen by
      weight. **55 of the 131 site types in the merged pool carry a positive
      weight and six of those are STG's** (measured 2026-08-09), so roughly one
      in nine random placements should be Trek before planet class is taken into
      account. **Zero over a few dozen surveys means nothing; zero over a whole
      large-galaxy game is the signal**, and then the weights are what to doubt,
      not the content ([76](../decisions/76-trek-archaeology.md)).
- [ ] **Survey the ugly worlds, not just the good ones.** The weights are keyed
      on planet class: barren and nuked (Hall of the Blade), desert and arid (Ark
      in the Sand, Desert Sanctuary), frozen and toxic (Sealed Mechanism), nuked
      and arid (Hebitian Vaults), any habitable world (Lost Colony). **A
      pacifist, unhurried empire is well placed to survey everything rather than
      the good half**, which is precisely what the last run could not do.
- [ ] **Excavate at least one to the finale.** A four- or five-stage dig spans a
      scientist's career, and **the failure mode is a middle stage that reads as
      filler** between the hook and the payoff.
- [ ] **Do the finale choices feel like choices?** Five of the six end on two
      options with different modifiers — take the blade or seal the hall, return
      the ark or keep reading it, wake the mechanism or backfill the shaft. If
      one side is obviously correct every time, it is not a choice, it is a tax.
- [ ] **Note whether more than one of the six ever shows** in a single galaxy.

### The Trek story events

The pulse fires — the last run proved that much, and it was the worst case
[decision 79](../decisions/79-reachability-checks.md) was written against.
**Vulcan sits in the middle tier**: one gated event of its own against the
Federation's two, so its headline rate is **17.8% per five-year pulse**, and
`stg_recent_story` blanks the pulse after a hit, which takes the long-run figure
to roughly **15%** — about three per century
([78](../decisions/78-phase-4-count-corrections.md)).

- [ ] **Watch for Vulcan's own event by name: *The Road to Gol*.** Its pool is
      that one plus the eight open to everybody.
- [ ] **Seeing a Federation, Klingon or Romulan institution event is the gate
      failing** — *The Academy Class*, *A Session of the Council*, *The Floor of
      the Great Hall*, *The Continuing Committee*. That is the direction nobody
      has tested yet: the last run played the empire holding *two* of the gated
      events, so it could not distinguish a gate that works from a gate that
      leaks.
- [ ] **Note the open ones you see too** — *A Fault in the Pattern Buffer*, *The
      Cartography Office*, *The Convoy*, *The Long Round* and the rest. Four were
      graded correct on picture and register last run; the rest are unread.
- [ ] **First contact fires its own**, *The First Words*, on a separate hook.
      Note whether it appears when you meet your first empire — and note anything
      odd in the sound, because `first_contact.5` and `first_contact.380` both
      logged *Failed to pick an event sound* last time.
- [ ] **Texture or interruption?** A story event arrives unbidden, unlike an
      anomaly or a dig. If it reads as a tax on the pause key the weights are too
      high, and `1200 = 0` is the one number to move
      ([77](../decisions/77-trek-story-events.md)).

### The Vulcan hulls — the fix that has never been seen

**230 attach points over 100 files landed 2026-08-10, across all 22 Trek
shipsets, and not one of them is confirmed in game**
([82](../decisions/82-hull-section-attach-points.md)). Before that fix, every
non-corvette hull's stern sections attached to nothing and their guns were placed
against nothing — which is why the Federation destroyer's mounts read as plainly
wrong.

- **The corvette first, as a control.** Three separate runs have graded a
      corvette as correct, because a corvette only ever needed `part1` and so was
      never affected. If the Vulcan corvette looks wrong, something new broke.
```markdown
#OBSERVATIONS
- Confirmed corvette and gun mounts look correct
```
- [ ] **Then destroyer, cruiser, battleship, titan as you unlock them** — and
      **look at the stern specifically**, since that is where the missing
      sections were. What you are asking is whether the guns now sit **on the
      hull** rather than floating beside it or stacked at the origin.
- [ ] **Then the pattern question, which is the harder one.** 66% of mounts
      across the 27 shipsets are still placed from the bounding box
      ([67](../decisions/67-source-art-hardpoint-names.md)); the thing to look
      for is a mount that **breaks the pattern of the ones beside it**, not a
      mount you dislike.
- [ ] **Do the weapons draw at all**, and did the pruned event pictures take
      anything visible with them?
- [ ] **If you forced a Klingon or Cardassian neighbour, look at one of their
      capital ships in combat.** Their corvettes were graded well on 2026-08-08;
      above corvette they are as unseen as everything else.

### Ship registries and class names — and Vulcan is the sharpest test we have

Read [decision 72](../decisions/72-ship-class-names.md) and
[73](../decisions/73-class-name-thematic-fill.md) before grading this, because
part of what looks wrong here is a deliberate call.

- [ ] **A class name plainly belonging to another tonnage is the clean defect.**
      *Nebula – Interceptor* is one glance and means a `generic` token escaped
      demotion.
- [ ] **Read the Vulcan class names and say whether they read as Vulcan.**
      The corvette tier opens Karatek, Sharien, Vras, D'Mir; the destroyer tier
      T'Pau, Surak; the cruiser tier Sh'Ran, D'Kyr — and then **each tier
      continues into Starfleet classes**: Constitution, Sovereign, Defiant,
      Prometheus on the cruiser, Excelsior, Ambassador, Galaxy on the battleship.
      That is defensible for a Federation founder member and it is what
      [decision 73](../decisions/73-class-name-thematic-fill.md) chose. **Say
      whether it reads as a member world's fleet or as somebody else's fleet with
      a Vulcan name on the front.**
- [ ] **The titan class names are Enterprise-A through Enterprise-E**, which are
      registries in canon, not classes. **Look at what a Vulcan titan is actually
      called on screen** and report the exact string. This is the sharpest
      single check on this list because it is unambiguous either way.
- [ ] **Then the registries, which are a separate pool.** The Vulcan corvette
      registry pool runs past 600 names and its tail is not Vulcan at all —
      Eisenhower, Reagan, Zulu, Aztec, Tomahawk. **Say whether a VSS Eisenhower
      ever rolls**, because that is the one thing that decides whether the tail
      is harmless depth or a visible defect
      ([59](../decisions/59-ship-name-pools.md),
      [`src/common/name_lists/stg_vulcan.txt`](../../src/common/name_lists/stg_vulcan.txt)).

### The planet screen, the habitats, and the rest of the UI

- [ ] **The capital's city view, once it has grown.** `vulcan_01` is the tallest
      city set in the tree and the one already reviewed and left alone
      ([70](../decisions/70-vulcan-city-framing.md),
      [66](../decisions/66-city-set-canvas-overflow.md)). **The right-hand
      amphitheatre being cut is STNH's own art and is not a defect** — do not
      report it again. What is worth reporting is a **new** difference between
      this screen and the designer preview.
```markdown
#OBSERVATIONS
- The city picture looks scaled completely wrong.
```
- [ ] **Build a habitat and look at it.** Six `vendor.yml` renames changed which
      entity declaration the engine keeps, and **a rename that works produces no
      log record**. The nebula half of that question was graded correct last run;
      **whether habitats draw as vanilla's orbital ring rather than a Suliban
      helix has never been seen** ([53](../decisions/53-duplicate-entity-triage.md)).
- [ ] **Open every standard UI window once** — fleet manager, species, leaders,
      diplomacy, technology, situation log, the outliner — and say whether
      anything is clipped, empty or drawn at the wrong scale. The last run did
      exactly this and it is what turned up the designer's city scaling.

### Music

- [ ] **The count is 55 names in the player and 27 in the rotation.** Not 22, and
      not 70 — those two figures count a **declaration** and a **playlist entry**
      respectively, and both are correct ([61](../decisions/61-music-player-track-names.md),
      [65](../decisions/65-music-rotation-dedupe.md)). **Do not re-report a count
      unless it is neither of those.**
- [ ] **The Federation anthem is in the ambient rotation for a Vulcan empire
      too**, since the rotation is global rather than per-empire
      ([55](../decisions/55-federation-anthem.md)). Confirming that is a
      one-hearing answer to a question nobody has asked yet.
- [ ] **Read the track names once** and say whether the four chosen main-theme
      titles sit right beside the eighteen derived ones. This is the half of the
      music question still ungraded by ear.

---

## What this run cannot reach — do not spend hours on it

Knowing this in advance is the cheapest thing on the page.

- **The Terran mirror uniforms and the Federation president's robe.** Different
  empires, different selectors. A Vulcan run says nothing about either.
- **The 79 minor powers' ship names.** They are `generic`-only on purpose,
  where thin is not broken.
- **The Malon pools naming a type rather than a class** — *Waste Extraction
  Cruiser – Interceptor* is a source's own content, already flagged, and not
  yours to find again.
- **Real Space's oversized systems, `PLANET_SCALE_SYSTEM`, and the 703
  report-tier clutter orphans.** All three are reviewed and deliberately left
  ([open-questions.md](../planning/open-questions.md)).
- **More Events Mod.** Subscribed, deferred on purpose, and nothing about it is
  in this build.

---

## When you stop

- [ ] **Stop the game and do not relaunch.**
- [ ] **Say the wall-clock window**, so the analysis can separate init errors
      from in-play ones.
- [ ] **Report back and let the container read `error.log` before drawing any
      conclusion** — that is standard practice and it is cheap
      ([live-runs.md](../guides/live-runs.md)).
- [ ] **Say what you did not open.** *"If there were oddities that were missed
      they were likely not glaring"* is the honest form of that, and it should be
      read as coverage rather than as a pass — **a screen nobody opened is a
      check that never ran**
      ([live-runs.md](../guides/live-runs.md#a-screen-nobody-opened-is-a-check-that-never-ran)).
