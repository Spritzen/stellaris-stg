# The long Federation run — what to cover

> **What** — an ordered checklist for a long United Federation of Planets
> playthrough: what to do, what to look at, what to write down, and what to
> ignore.
> **Open when** — before launching this run, and again before reporting back.
> **Then** — [What the run found, and the fix for each](../planning/ufp-run-remediation.md) · [Live runs](../guides/live-runs.md) · [Open questions](../planning/open-questions.md) · [Status](../planning/status.md)
>
> **This run happened, 2026-08-10.** Its observations are inline below, under the
> items they answer. A run plan is spent when its run is over
> ([runs/README.md](README.md)) — read it for what was looked at, and
> [the remediation plan](../planning/ufp-run-remediation.md) for what to do
> about it.

## Before you launch

- [Y] **Run the loop and confirm it is clean.** `make vendor && make validate` —
      the mod folder is a symlink, so a rebuild is live the moment it finishes.
- [Y] **Copy the old `error.log` aside first.** The game truncates every file in
      `/paradox/stellaris/logs/` at startup, so launching destroys the 2026-08-08
      baseline that the next analysis has to reconcile against:
      `cp /paradox/stellaris/logs/error.log /paradox/stellaris/logs/error.log.2026-08-08`
- [Y] **Restart the launcher**, enable *Star Trek Galaxies* in the playset,
      launch.
- [Y] **Do not relaunch after you stop.** The log is per-session; a second launch
      wipes the run you just played.

## Galaxy settings, because they decide what this run can measure

- [Y] **Large galaxy, 600–1000 stars.** This is a survey-led run; every question
      worth answering is downstream of how many bodies get surveyed.
- [Y] **More AI empires rather than fewer.** All 101 prescripted empires are in
      the AI pool, and the ones you meet are the ones that get graded.
- [Y] **Ironman off.** You will want to reload, re-open a screen, and look twice.
- [Y] **Run three or more science ships from the start** and keep them fed. Half
      of this checklist is unreachable otherwise.
```markdown
#OBSERVATIONS 
- Set for 20 AI empires
```
## In the empire designer, before you press start

Five minutes here answers three open questions that no log record will ever
carry.

- [N] **The president's clothes.** His row names `portrait = stg_fed_ruler`,
      `texture = 0`, `clothes = 0` on a dedicated one-texture selector. He should
      be in the **Starfleet formal robe** — not an ENT jumpsuit, not a random
      garment. If he is wrong, the selector is not being reached at all and the
      portrait clone is the thing to doubt, not the index
      ([69](../decisions/69-ruler-clothes-dedicated-selectors.md)).
```markdown
#OBSERVATIONS 
- no its not what is expected; also I can't tell what clothing number it's pointed to as the ruler appearance isn't set, i.e. its set to 1 and if i increment and then decrement back to 1 it shows the default, so the image isn't showing the same as the settings
```
```markdown
#OBSERVATIONS 
- On the clothing slider 486-499, 495, 496, 498,  is showing the same as index 1, possibly more I've not checked all
```
- [Y] **The room behind him** is `earth_room`, STNH's own assignment — a Trek
      room, not a vanilla personality room
      ([48](../decisions/48-room-selector-merge.md)).
```markdown
#OBSERVATIONS 
- yes the room behind is appropriately star trek and fitting for UFP
```
- [Y] **Skim the room dropdown.** It should still be "realistically over 300"
      entries with the four hidden empires present
      ([62](../decisions/62-city-set-cultures-undeclared.md)).
```markdown
#OBSERVATIONS 
- looks correct
```
- [Y] **The flag draws** — `Federation1.dds` from the `trek` category, blue on
      light blue ([49](../decisions/49-flags-city-sets.md)).
```markdown
#OBSERVATIONS 
- looks correct
```
- [N] **The ship-appearance dropdown lists Starfleet TNG Era** alongside the other
      26 shipsets, with no blank or duplicated row.
```markdown
#OBSERVATIONS 
- something is not right in the menu it is listing species and not shipset names, it seems functional enough to play through and the shipset it's defaulted to does look correctly TNG era ships
```
```markdown
#OBSERVATIONS 
- many cities are incorrectly resampled on the empire designer - city & rooms selection screen, alot of them look approx 25% to small, but surely this can be measured correctly
```

## The first hour — survey, because that is the point of this run

**Open the situation log and leave it open.** Anomalies, dig sites and story
events all report there, and it is the one screen that turns this run into
evidence.

### Trek anomalies

STG adds 21 categories to a merged pool of ~348, so **most anomalies you meet
will still be vanilla's** — a run with few Trek ones is not a defect. Write down
the ones you do see, by name and level; that observed sample against the 21 is
worth more than any impression.

- **Does the picture match the text under it, and is it framed right?** This
      is the highest-value look in the whole run. The anomalies' 24 pictures are
      the only ones in the project whose 620×264 → 450×150 centre-crop has **no
      vanilla control behind it** — the archaeology's 27 and the story events' 21
      were each checked in the exact crop before being chosen
      ([74](../decisions/74-event-picture-families.md)). **A subject cropped at
      the chin is what the failure looks like.**
- **Nine of the 24 are frames pulled from a 9315×264 animation strip**, and a
      wrong frame is the specific failure mode there — a picture that is
      technically fine but shows the wrong moment.
- **Does the writing sound like Star Trek, or like a different mod?** The
      register is a survey officer's report, which is vanilla's own. What to
      watch for is a description that reads as a **plot summary of an episode**
      rather than as something a science officer wrote.
- **Do the levels feel like a wall?** STG puts 43% of its categories at level
      5+ against vanilla's base-game 10%, and 19% at level 1–2 against vanilla's
      65% ([78](../decisions/78-phase-4-count-corrections.md)). The galaxy is not
      harder overall, but **the Trek half is the slow, failure-prone half** and
      that is the half you are meant to notice. Say whether early scientists
      bounce off it.
- **Nine of the 21 are `max_once` or `max_once_global`** — the ones naming a
      specific object (Tox Uthat, the Iconian gateway, the planet-killer remnant,
      the Omega signature, the deep-space probe). Seeing one twice in a galaxy
      would be a real finding.
```markdown
#OBSERVATIONS
- "Program Complete"; Trek event. Picture looks correctly fitted and is appropriate to the event. Flavour text is appropriate and fits with the gameplay. Rewards - 274 unity or 250 engineering research. Took unity.
- "The Academy Class"; Trek event. Picture looks correctly fitted and is appropriate to the event. Flavour text is appropriate and fits with the gameplay. Rewards - 330 society research  or 330 physics research. Took society.
- "The Graveyard"; Trek event. Picture looks correctly fitted and is appropriate to the event. Flavour text is appropriate and fits with the gameplay. Rewards - +3 engineering to planet
- "The Long Round"; Trek event. Picture looks correctly fitted and is appropriate to the event. Flavour text is appropriate and fits with the gameplay. Rewards - 2073 society research or 1449 unity +200 leader xp.
```
### Trek dig sites

- **Do they turn up at all?** This is the question a live run answers cheaply
      and nothing else answers. Sites are placed by vanilla's `ancrel.9999` on
      `on_survey_planet`, a 5-in-405 roll per surveyed body, then chosen by
      weight. **55 of the 131 site types in the merged pool carry a positive
      weight, and six of those 55 are STG's** (measured 2026-08-09 against
      `stg-build/` plus vanilla — re-measure by grepping
      `common/archaeological_site_types/` in both trees for a `weight` block with
      a positive `add`/`base`), so roughly one in nine random placements should
      be a Trek one before planet class is taken into account. Zero over a few dozen
      surveys means nothing; **zero over a whole large-galaxy game is the
      signal**, and then the weights are the thing to doubt, not the content
      ([76](../decisions/76-trek-archaeology.md)).
- **Survey the ugly worlds, not just the good ones.** The weights are keyed
      on planet class: barren and nuked (Hall of the Blade), desert and arid (Ark
      in the Sand, Desert Sanctuary), frozen and toxic (Sealed Mechanism), nuked
      and arid (Hebitian Vaults), any habitable world (Lost Colony).
- **Excavate at least one to the finale.** A four- or five-stage dig spans a
      scientist's career, and **the failure mode is a middle stage that reads as
      filler** between the hook and the payoff.
- **Do the finale choices feel like choices?** Five of the six end on two
      options with different modifiers — take the blade or seal the hall, return
      the ark or keep reading it, wake the mechanism or backfill the shaft. If one
      side is obviously correct every time, it is not a choice, it is a tax.
- **Note whether more than one of the six ever shows** in a single galaxy.
```markdown
#OBSERVATIONS
- None observed, only a portion of the map was revealed.
```
## The long game — what only hours can reach

### Story events

The pool fires on a five-year pulse and `stg_recent_story` blanks the next pulse
after a hit, so the Federation's long-run rate is **~17% per pulse** — about five
events across 150 in-game years, drawn from the ten in its pulse pool — its own
two, plus the eight open to everybody. A first-contact event hangs off its own
hook and is not part of that ten.

- **Do they fire at all?** Ten pulses is fifty years and about an 85% chance
      of at least one. **If you reach 2250 having seen none, stop and say so** —
      that is the single highest-value negative result available on this run, and
      it points straight at `stg_on_five_year_story_pulse`, a custom on_action
      reached only by `fire_on_action`
      ([79](../decisions/79-reachability-checks.md)).
- **Watch for the Federation's own two by name**: *The Academy Class* and
      *A Session of the Council*. Seeing neither across a long game is the gate
      failing in one direction; seeing another empire's — the Klingon Great Hall,
      the Romulan Continuing Committee — is it failing in the other.
- **Note the eight open ones you see too** — *A Fault in the Pattern Buffer*,
      *The Cartography Office*, *The Convoy* and the rest. Eleven of the 22
      playable empires see only these, so their quality carries more weight than
      their count.
- **First contact fires its own**: *The First Words*, on a separate hook. Note
      whether it appears when you meet your first empire.
- **Texture or interruption?** A story event arrives unbidden, unlike an
      anomaly or a dig. If it reads as a tax on the pause key the weights are too
      high, and `1200 = 0` is the one number to move.
- **Does the register hold?** These are service dispatches written from
      inside an institution. The failure mode is a description that reads as a
      **narrator summarising an episode** instead of a civil servant writing a
      minute.

### The Starfleet TNG shipset

- [Y] **Look at a corvette close up, early.** Its two forward phasers sit on the
      centreline at the bow, where the artist drew them; the third mount now sits
      **exactly on top of the first** rather than starboard-amidships where the
      bounding-box spread put it. Two turrets on one point is the intended cost —
      what would be wrong is a gun somewhere nobody drew
      ([60](../decisions/60-mounts-share-existing-points.md)).
- [?] **Then every hull as you unlock it** — destroyer, cruiser, battleship,
      titan. 66% of mounts across the 27 shipsets are still placed from the
      bounding box ([67](../decisions/67-source-art-hardpoint-names.md)); the
      thing to look for is a mount that **breaks the pattern of the ones beside
      it**.
- [N] **Do the weapons draw at all**, and did the pruned event pictures take
      anything visible with them?

### Ship names and class names

- [?] **A Nebula-class name on a corvette is how the tonnage table fails**, and
      the class half is the easier of the two to catch: *Nebula – Interceptor* is
      one glance. The Federation corvette tier should read Oberth, Nova,
      Peregrine, Danube; the cruiser tier Constitution, Sovereign, Nebula, Akira;
      the battleship tier Galaxy, Excelsior, Ambassador, Odyssey
      ([72](../decisions/72-ship-class-names.md)).
- [?] **Does the invented English sit beside the canon names** without announcing
      itself ([73](../decisions/73-class-name-thematic-fill.md))?
- [?] **The Defiant appears at two tonnages** — destroyer and cruiser — which is
      STNH's own modelling. Say whether that reads as wrong or as fine.
- [?] **A class name plainly belonging to another tonnage** means a `generic`
      token escaped demotion. Worth one report if you see it.
```markdown
#OBSERVATIONS
- UFP Destroyers; stern mounts don't match the modal at all. It's possible the first mount position is artistically correct, which makes me think a horizontal mirror of this position would also be correct but first check for missed artistic mounts - deep dive on this as this could reveal/resolve issues across all ships.
```
### Music

- [Y] **The Federation anthem is in the ambient rotation** and takes one hearing
      to confirm ([55](../decisions/55-federation-anthem.md)).
- [N] **Open the music player and read the 22 track names.** What to listen for
      is whether the four chosen main-theme titles sit right beside the eighteen
      derived ones ([61](../decisions/61-music-player-track-names.md)).
```markdown
#OBSERVATIONS 
- Track list has approx. 70 tracks in it
```
- [?] **Does the rotation read as 27 distinct recordings**, or does something
      repeat ([65](../decisions/65-music-rotation-dedupe.md))?
```markdown
#OBSERVATIONS 
- All the names of tracks are unique from what I can tell and going by an eyeballing of duplicate track lengths this looks to confirm no duplicates, still hard to eyeball.
```

### Galaxy Map
```markdown
#OBSERVATIONS
- Most nebula names contain an underscore instead of a space. e.g. Arachnid_Nebula and Class_9_Nebula
- System name: Kullat_Nunu
- Nebula size on galaxy map looks correct
- 22 Empires met and no trek empires; can we make sure somehow that our empires are in a game. I know if you create an empire there is a selector to do that.
```

### Final Play Run Notes
```markdown
#OBSERVATIONS
- It's worth pointing out that I observed all of the standard UI gameplay windows and was actively looking for oddities, I pointed out inconsitancies, issues and errors. If there were oddities that were missed they were likely not glaring, or it didn't happen in this play run.
- On the Planetry screen the city view was hard to say one way or another if it was correct or not, meaning it didn't look bad or out of place. It's not a confirmation that its correct. May be worth looking at the window sizes from UI Overhaul mod and then just resampling all artwork, that we use, to fit. It's also worth double checking we haven't polluted our banks of images; have we correctly identified which pictures are for the city screen and which pictures go in the empire designer screen for selectors - as an example.
- Newly elected president gained the correct clothes.
```