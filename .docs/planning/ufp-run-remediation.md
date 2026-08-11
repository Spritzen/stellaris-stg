# Remediating the 2026-08-10 Federation run

> **What** — every defect the long Federation run turned up, each traced to a
> root cause on disk, with the fix, the mechanism it goes through, and the check
> that would have caught it.
> **Open when** — picking up work off that run, or before re-opening any question
> its observations touch.
> **Then** — [The run plan](../runs/ufp-long-campaign.md) · [Open questions](open-questions.md) · [Status](status.md) · [Live runs](../guides/live-runs.md)

The observations are in [the run plan itself](../runs/ufp-long-campaign.md),
written inline under the checklist items they answer. This file is the other
half: what each one *is*, and what closing it costs.

**Tiers are ordered by evidence, not by severity.** Tier 1 had a root cause
confirmed against disk and a mechanical fix; Tier 2 was a real defect still
owing one investigation; Tier 3 might not have been a defect at all and needed
measuring first.

## Where every item stands, 2026-08-10

| | Item | |
|---|---|---|
| 1 | Hull section attach points | **Fixed** — 230 points, 22 shipsets ([82](../decisions/82-hull-section-attach-points.md)) |
| 2 | Malformed portrait paths | **Fixed** — 29 patched; **196 dangling textures found beside them, left** |
| 3 | Star and nebula names unlocalised | **Fixed** — 328 keys, one per quoted entry ([81](../decisions/81-random-names-are-loc-keys.md)) |
| 4 | No Trek empires met | **Narrowed, open** — three causes eliminated; needs a force-spawn on the next run |
| 5 | Planetary Diversity event scope | **Fixed** — 6 patches; ~98 of the log's 174 post-init records |
| 6 | ~70 music tracks | **Not a defect** — 55 declarations, 27 rotation; the run plan's "22" was stale |
| 7 | Shipset dropdown lists species | **Not a defect** — vanilla has no shipset name key either; the *descriptions* are missing |
| 8 | City art 25% small in the designer | **Not the art** — every file is at canvas; UI Overhaul's rect is the suspect |

**Five of the eight are closed, three of those by measurement rather than by a
change.** What is genuinely still open is item 4, item 2's 196, and item 8's
rect — plus everything in Tier 4, which only a live run can reach.

`make vendor`, `make validate` and `make docs` are clean throughout.

---

## What the log said

`/paradox/stellaris/logs/error.log`, read 2026-08-10 against the run of the same
day (session 12:21:32 → 23:19:51, ~11 hours):

| | 2026-08-10 | Baseline 2026-08-08 |
|---|---|---|
| Records / size | **2,251 / 228 KB** | 1,261 / 187 KB |
| Startup window | 49.4 s (`time.log`) | 49.3 s |
| Records **after** startup | **174** | 1 |

Against the ~1 MB a clean vanilla run produces, the volume is fine. The 174
post-init records are the whole of the log's value, and they fall into three
groups — 98 Planetary Diversity event-scope errors, 19 missing portrait
textures, 8 missing ship attach points — with the remaining 49 spread one-apiece
across vanilla text and script warnings.

**The jump from 1 post-init record to 174 is a change of run, not of build.**
The 2026-08-08 baseline was a short session; this one played eleven hours and
opened the screens. Re-measure with:

```bash
grep -cE '^\[[0-9:]{8}\]' /paradox/stellaris/logs/error.log
```

---

## Tier 1 — root cause confirmed, fix is mechanical

**All three landed 2026-08-10**, as [decision 82](../decisions/82-hull-section-attach-points.md)
(item 1), `vendor.yml` patches (item 2) and
[decision 81](../decisions/81-random-names-are-loc-keys.md) (item 3). `make
vendor`, `make validate` and `make docs` all report **0 errors, 0 warnings**
against the build of 2026-08-10 (22,406 files). **None of the three is
confirmed in game** — every one of them is an eyes-only property once the
references resolve, and the next run is what grades them. Each item below keeps
its diagnosis and gains a **What landed** note.

### 1. Every non-corvette Trek hull is missing its section attach points

**Seen:** *"UFP Destroyers; stern mounts don't match the modal at all."*

**Logged:** eight records, e.g.

```
starfleet_tng_destroyer_entity   has no attach point named part2
starfleet_tng_cruiser_entity     has no attach point named part2, part3
starfleet_tng_battleship_entity  has no attach point named part2, part3
starfleet_tng_titan_entity       has no attach point named part2, part3
starfleet_tng_colossus_entity    has no attach point named frame_ship
```

**The mechanism.** A ship is assembled by attaching each section at the locator
its `ship_size` names. Vanilla asks for `part1`+`part2` on a destroyer and
`part1`+`part2`+`part3` on cruiser, battleship and titan
(`/stellaris/common/ship_sizes/00_ship_sizes.txt`, lines 308 and 397); a colossus
asks for `frame_ship` (`/stellaris/common/ship_sizes/01_colossi.txt:15`).
Every STG hull entity above corvette instead carries
`pdxmesh = "molluscoid_01_corvette_frame_mesh"` — **a corvette's frame, borrowed
for hulls a corvette's rig was never built for.** A corvette needs `part1` and
nothing else, so the frame answers for `part1`, has no `part3` and no
`frame_ship` at all, and the sections whose locator is missing never attach.
Their guns are then placed against nothing.

**One part of this is observed rather than derived.** The frame's own `.mesh`
does name `part1_locator` and `part2_locator`, so the destroyer's missing `part2`
is not a missing name in the file — an attach point can also come from the
animated rig, which is not readable from the container (vanilla's titan and
colossus frames name no part locators in their mesh files either, and work).
**The log is the evidence for `part2`; the mesh contents are the evidence for
`part3` and `frame_ship`.** The fix below is the same either way, which is why
this is worth doing without resolving it.

The corvette is unaffected because it only ever needs `part1`, which is why that
checklist item came back `[Y]` while the destroyer did not.

**It is 132 hulls across all 22 Trek shipsets, not the five the log named** —
22 each of destroyer, cruiser, battleship, titan, colossus and juggernaut. The
log named `starfleet_tng` only because that is the set the run flew. Deriving the
rule rather than repairing the instances is
[live-runs.md](../guides/live-runs.md#a-screen-nobody-opened-is-a-check-that-never-ran)'s
standing requirement. Re-measure with:

```bash
grep -rc 'pdxmesh = "molluscoid_01_corvette_frame_mesh"' stg-build/gfx/models/ships/
```

**The obvious fix is the wrong one.** Retargeting each hull to a vanilla frame
mesh of the matching tonnage would supply the locators — and spread the sections
apart, because a vanilla frame's `part1`/`part2`/`part3` are metres apart, tuned
to vanilla art. STNH does not build ships that way. Its **bow** section carries
the entire ship mesh (`starfleet_tng_destroyer_bow_L1_entity` →
`starfleet_tng_destroyer_c_mesh`, the Steamrunner) and its **stern** sections are
`pdxmesh = "empty_mesh"` — invisible carriers that exist only to hold guns, whose
locators are already authored in whole-hull coordinates. They are *meant* to sit
at the hull origin.

**The fix:** declare the section-slot locators explicitly on the hull entity at
`position = { 0 0 0 }`. Every section then attaches at the hull origin, which is
the coordinate space its guns were drawn in, and the borrowed rig stops being
consulted for a question it cannot answer. This is vanilla's own mechanism —
282 bare `part1` and 25 bare `part2` declarations sit in
`/stellaris/gfx/models/ships/*/*.asset` for exactly this reason.

**Scoped to hulls flying a borrowed frame.** An entity whose `pdxmesh` is its own
culture's art is left alone: it has a rig built for it, and the corvette — the
one hull three separate runs have graded as correct — is in that group.

**The mechanism:** these `.asset` files are already `src/` overrides owned by
`tools/fix_ship_locators.py` (see its header for why `src/` and not a
`vendor.yml` patch). This is a new rule in that tool, not a hand edit — 132
entities, and [invariant 2](../../CLAUDE.md) forbids touching the vendored copy.

**The check already exists, and it was scoped away from this.**
`check_section_attach_points` in `tools/validate.py` asks exactly this question —
does the hull carry the attach points its size's `section_slots` name — and
[decision 35](../decisions/35-station-section-attach-points.md) narrowed it to
the **station** family on calibration grounds: over all 317 sizes with
`section_slots`, vanilla itself produces 41 findings against the mods' 147, a
ratio nobody can act on.

So this is **decision 35's defect recurring one database over**. That decision
came from the same `pdx_entity.cpp:1217` message in a live run, swept the rule
across all 22 shipsets' stations, and stopped at the station boundary — where
the calibration stopped. The hulls were never covered, and no run had flown one
above corvette until this one.

**Widening the check is the durable fix and its own piece of work**, named as
such in the check's own docstring: establish first whether vanilla's 41 are real
quirks or a mesh lookup this resolves wrongly. With the tool change above in
place, the mod side of that ratio is what should now be 0 — which is the
measurement that makes widening viable, and the reason to take it next rather
than later.

**Still needs eyes afterwards.** Section placement is a visual property; a clean
log only says the locators exist now.

> **What landed** — `hull_entities()` in `tools/fix_ship_locators.py`, writing
> **230 attach points over 100 files**, every one onto `part1`'s own position
> rather than the origin, so the bow does not move. The rule's output for
> `starfleet_tng` reproduces the log's eight records exactly, which is the
> strongest correspondence available without launching the game. Two parsers
> that counted braces inside comments were fixed on the way — one in this tool,
> one in `validate.py`.
> [Decision 82](../decisions/82-hull-section-attach-points.md).

### 2. STNH's master clothes selector names textures that cannot load

**Seen:** *"no its not what is expected … the image isn't showing the same as the
settings"*, and *"486-499, 495, 496, 498, is showing the same as index 1"*.

**Logged:** 19 `Could not find texture` records, of which the diagnostic ones are

```
gfx/models/portraits/human_civilian/human_president_male_1 … _7   ← no extension
gfx/models/portraits/human_civilian/human_terran_ruler_male_1.dds.dds
```

**The mechanism.** All nine target files exist on disk. The defect is purely in
the reference:
`stg-build/gfx/portraits/asset_selectors/humanoid_master_male_clothes_01.txt:2766`
onward names seven presidents with **no `.dds` at all**, and line 2835 onward
names the Terran ruler textures with a **doubled** `.dds.dds`. Both come
unchanged from the source mod (`.source/688086068/`). A texture that fails to
load falls back, which is exactly "the image isn't showing the same as the
settings" and exactly why high slider indices redraw as index 1.

**This does not reopen [decision 69](../decisions/69-ruler-clothes-dedicated-selectors.md).**
The Federation ruler takes `stg_fed_ruler_clothes`, a dedicated one-texture
selector pointing at `federation_president_male_1.dds`, and that file is present
and logged no error. Whether the dedicated selector is *reached* remains
unproven — the run says the garment is wrong, and nothing on disk contradicts
decision 69 yet. **Fix the selector first and look again**; a fallback happening
anywhere in the chain is enough to explain a wrong garment.

**The mechanism:** `patches:` entries in `vendor.yml`. Unlike the locator work
these are literal, unambiguous find-and-replace on a distinctive string, which is
what a patch is for.

**The check:** every quoted texture path in `gfx/portraits/asset_selectors/`
ends in `.dds` and resolves against the merged tree. That sweep also picks up the
`kriosian`, `starfleet_all_good_things_mirror_mirror`,
`starfleet_next_generation_02_mirror` and `starfleet_next generation 02` (a space
in the directory name) misses in the same log.

> **What landed** — 29 replacements over the two master selectors: seven
> president rows given the `.dds` they were missing, and 22 Terran ruler rows
> losing a doubled one. Both files now hold **zero** malformed paths.
>
> **The sweep found a much larger population, and it is a different defect.**
> **196 texture paths in `gfx/portraits/asset_selectors/` resolve to no file in
> the merged tree** — including the `kriosian`, `all_good_things_mirror_mirror`
> and `starfleet next generation` misses the log named. Unlike the 29, these are
> not malformed: the paths are well-formed and **the art is in no source mod at
> all**, so this is neither our harvest nor our prune. Every one is a silent
> fallback in the empire designer.
>
> Left deliberately: fixing one means either deleting the row — changing which
> garment a species wears — or supplying art, and that is a content call per
> row, not a sweep. **Measure first**, with the loop that produced the 196:
> walk every quoted `gfx/models/portraits/…` in that directory and test it
> against `stg-build/`. Worth its own scoped piece of work, and a check once the
> shape of the answer is known.

### 3. 330 star and nebula names ship without a single localisation key

**Seen:** *"Most nebula names contain an underscore instead of a space. e.g.
Arachnid_Nebula and Class_9_Nebula"*, *"System name: Kullat_Nunu"*.

**Logged:** nothing, and that is the point — this is
[decision 61](../decisions/61-music-player-track-names.md)'s
*a name that resolves to itself still resolves*, in a third database.

**The mechanism.** A quoted entry in `random_names` is a **localisation key**,
not a display string. Vanilla writes both halves:

```
common/random_names/base/00_random_names.txt      "Epsilon_Eridani"
localisation/english/random_names/…_l_english.yml  Epsilon_Eridani:0 "Epsilon Eridani"
```

[src/common/random_names/base/stg_star_names.txt](../../src/common/random_names/base/stg_star_names.txt)
held **330 quoted entries and STG shipped zero keys for any of them**, so every
one drew its own key. Unquoted entries (`Badlands`) are literals and are fine.

**The fix:** generate `src/localisation/english/random_names/`, underscore →
space, reviewed by hand where that is not the right answer.

**The check:** every quoted `random_names` entry has a localisation key. This
is the third database to need the same question asked, after the music player
([61](../decisions/61-music-player-track-names.md)) and the shipset dropdown
below — which argues for one check over the pattern rather than three checks over
three files.

> **What landed** — `tools/gen_star_names.py` now writes
> `src/localisation/english/stg_random_names_l_english.yml`, **328 keys** against
> the regenerated pool's 328 quoted entries — closed in both directions, no
> orphans. `Arachnid_Nebula`, `Class_9_Nebula` and `Kullat_Nunu` — the three the
> run named by hand — are all keyed.
>
> **The generator was not idempotent, and this found it.** It subtracts names
> already pooled by reading `stg-build/`, which `make vendor` fills with its own
> previous output, so a second run subtracted its own 580 names and wrote a pool
> a third the size. Fixed by skipping its own file. Re-running also dropped 22
> names the tool's own rules exclude — Aldebaran, Betelgeuse, Sirius and 19 more
> that STG's name lists already own — a backlog from the tree growing since the
> generator last ran, not a new call.
>
> The **display values** are unread, 328 of them. No check can ask whether a
> name reads well. [Decision 81](../decisions/81-random-names-are-loc-keys.md).

---

## Tier 2 — a real defect, owing one investigation

**Item 5 landed 2026-08-10. Item 4 is narrowed but not closed** — three
hypotheses eliminated by measurement, and what is left is a galaxy-setup
question no container-side change can settle.

### 4. 22 empires met, none of them Trek

**Seen:** *"22 Empires met and no trek empires; can we make sure somehow that our
empires are in a game."* The run was set to 20 AI empires.

Every STG prescripted empire carries `spawn_enabled = yes`, which makes it
*eligible*, not present — and vanilla 4.4 uses only `yes` and `no`, so there is
no stronger token to reach for. Guaranteed presence comes from the per-empire
force-spawn toggle in the empire designer, which is a **run-plan instruction**,
not a repo change.

But zero out of 22 is enough to test the other hypothesis first, and it is the
one with a precedent: the engine **drops an invalid prescripted empire silently**
rather than refusing it, and a sweep of that rule once turned up nine more
([live-runs.md](../guides/live-runs.md#a-screen-nobody-opened-is-a-check-that-never-ran)).
Sweep all 101 for validity against 4.4's ethic/authority/civic rules before
concluding this is only a settings question.

*(The `ValidateGovernment: ethic_fanatic_egalitarian` block at 17:49 is **not**
evidence here — it is a randomly generated `origin_necrophage` empire, checked
and excluded.)*

> **Three hypotheses eliminated, 2026-08-10.** None of them is why.
>
> | Hypothesis | Measurement | Verdict |
> |---|---|---|
> | Silently dropped on an invalid trait, ethic or civic | `check_prescripted_empires` asks exactly this against vanilla's own `opposites`, `allowed_ethics`, archetype budgets and portrait sets, and passes on all 101 | **Ruled out** |
> | Excluded because their home systems are hand-placed | 23 of vanilla's own 33 spawn-eligible empires also carry an `initializer`, and those spawn as AI routinely | **Ruled out** |
> | Not marked spawnable | 100 of 101 are `spawn_enabled = yes`; the 101st is the Federation | **Ruled out** |
>
> **One anomaly, and it is not the cause.** The Federation alone carries
> `spawn_enabled = always`, a value vanilla uses nowhere in its 53 — it is only
> `yes` or `no` there. It is also the empire the run *played*, so its spawning
> says nothing either way. Worth normalising to `yes` or establishing that
> `always` parses, but it cannot explain 100 empires that did not appear.
>
> **What is left is the galaxy-setup question**, and it is not answerable from
> the container: whether the generator drew from the prescripted pool at all for
> those 20 AI slots. The next run settles it cheaply and definitively — **force-
> spawn two or three Trek empires from the designer's own toggle**. If they
> appear and nothing else Trek does, the content is fine and the pool weighting
> is the whole story; if a force-spawned one *fails to appear*, that is a real
> defect and a much sharper one to chase. This belongs in the next run plan as
> an instruction, not in the repo as a change.

### 5. Planetary Diversity's infester events fire into the wrong scope

98 records, the largest post-init group by far:
`pdplanetaryinfesters.100/110/120` and their `pdaw` twins declare `scope = planet`
but are fired from a ship scope by
`stg-build/common/on_actions/pd_on_actions.txt` and its `pd_aw_` twin.
Vendored, therefore ours to fix and never a reason to drop the mod
([decision 12](../decisions/12-fix-source-errors-dont-drop.md)).

**Vanilla settles the type without ambiguity.** `on_building_complete` is
documented `# This = Colony` in `00_on_actions.txt`, and **every** vanilla event
hooked on it or on `on_building_upgraded` is a `carrier_event` — `tutorial.14`,
`akx.10000`, `plant.101`, `cyber.201`. A `planet_event` there is rejected
outright, which is the message.

The bodies confirm it independently: all six wrap their work in
`planet = { … }`, a transition that is redundant from a planet root and
necessary from a carrier one. **They were written for the type they should have
been declared as.**

> **What landed** — six `vendor.yml` patches, `planet_event` → `carrier_event`,
> three in Planetary Diversity's file and three in PD - Ascension Worlds'.
> Verified in the rebuilt tree. This should take the post-init log from 174
> records to about 76 on its own.

---

## Tier 3 — measure before treating it as a defect

**All three measured 2026-08-10, and none of them is a defect.** Two were the
run plan expecting the wrong number, and the third is a real question that the
measurement moved somewhere else entirely. Nothing in the tree changed for any
of them; what changed is what we know.

### 6. The music player lists ~70 tracks

**Seen:** *"Track list has approx. 70 tracks in it"*, against the 22 the
checklist expected and the 27 distinct recordings
[decision 65](../decisions/65-music-rotation-dedupe.md) measured.

Both of those figures count **STG's own** rotation. The player lists everything
loaded, and base vanilla ships only 7 `music/*.asset` files — the rest arrive
from the DLC folders, which decision 65's replacement model never counted.
Re-measure across `/stellaris/dlc/*/music/` before touching anything. If ~70 is
correct, the stale document is the defect and decision 65 is what gets fixed.

The same run reports the names are all distinct and the lengths show no
duplicates, which is the half of decision 65 that still holds.

> **Measured — the two decisions count different things, and both are right.**
> The DLC theory was wrong: the game ships **no** music outside `/stellaris/music`
> (0 `.ogg` under `/stellaris/dlc`, 30 in the base folder). The real split is
> between a **declaration** and a **playlist entry**:
>
> | | at runtime | |
> |---|---|---|
> | `music = { … }` declarations | 45 STG + 10 vanilla = **55** | what the player lists ([61](../decisions/61-music-player-track-names.md)) |
> | `song = { … }` playlist entries | 17 STG + 10 vanilla = **27** | the rotation ([65](../decisions/65-music-rotation-dedupe.md)) |
>
> Decision 65's 27 reproduces **exactly**. The run's "approx. 70" is an eyeball
> count of the 55 declarations, and `setup.log` corroborates the order of
> magnitude directly: `musicmanager.cpp` reports **162 songs loaded** across the
> whole session, a running total that counts every declaration in every context.
>
> **The stale number is the run plan's "22"** — decision 61's playlist count from
> before 65 remeasured it. Neither the tree nor decision 65 needs anything. A
> future run plan should say *55 names in the player, 27 in the rotation*.

### 7. The ship-appearance dropdown lists species, not shipset names

**Seen:** *"it is listing species and not shipset names … the shipset it's
defaulted to does look correctly TNG era ships."*

> **Measured — this is vanilla's own behaviour, not a defect.** There is no
> `<culture>_shipset` name key in vanilla either: across all of
> `localisation/english/`, the only shipset keys that exist are **20
> `_shipset_desc`** entries and no names at all. Vanilla's list reads
> "Mammalian", "Avian", "Reptilian" because its shipsets are named after the
> species classes they belong to — so a list of species names *is* the vanilla
> presentation, and STG's 50 graphical cultures inherit it. My Tier 3 framing of
> this as decision 61's family was wrong: there is no missing key, because there
> is no key.
>
> **What is genuinely absent is the description.** 0 of STG's 50 cultures have a
> `_shipset_desc` against vanilla's 20 for its own, which is why the panel beside
> the list is empty. That is content to write, not a bug to fix, and it is the
> only actionable thing here.

### 8. City art is undersized in the designer

**Seen:** *"many cities are incorrectly resampled … alot of them look approx 25%
to small, but surely this can be measured correctly"*, and on the planet screen,
*"hard to say one way or another if it was correct."*

> **Measured — the art is not the problem, and that narrows this a lot.** Every
> city layer in the built tree is now at vanilla's canvas and every room file at
> vanilla's: **299 layers at 800×400** and **327 rooms at 952×340**, with no tail
> at all. Decisions [58](../decisions/58-city-set-geometry.md),
> [63](../decisions/63-city-set-family-targets.md) and
> [66](../decisions/66-city-set-canvas-overflow.md) between them fixed 153 files
> and the check behind them holds. **A file cut to the right canvas cannot be
> 25% small because of its dimensions.**
>
> **So the rect is the suspect, and the run's own instinct was right.** The
> empire designer is not vanilla's screen: `interface/customize_species.gui`
> comes from **UI Overhaul Dynamic** and replaces vanilla's wholesale — 734 diff
> lines, not an edit. Art cut for vanilla's canvas is being drawn into UI
> Overhaul's rect. That is decision 58's exact mechanism — art cut for one canvas
> shown in another — one screen over.
>
> **The trap, and why this is not a resample.** The same file serves the planet
> view *and* the designer preview. Resampling it to fit UI Overhaul's rect would
> break the planet view, which the same run graded as fine. **One file cannot
> satisfy two rects**, so the fix is UI Overhaul's rect or the designer's scaling
> — not the art. Establish the rect from that `.gui` before touching a single
> `.dds`.

**On the picture-bank question the run asked** — *"have we correctly identified
which pictures are for the city screen and which go in the empire designer
selectors"* — the banks are clean. Every file in `gfx/portraits/city_sets/`
carries a `_city_l0N` or `_room` suffix and sits at that family's canvas, with
**one exception**: `future_starfleet.dds`, at 955×341, three pixels off the room
canvas, carrying neither suffix and **referenced by nothing in the tree**. An
orphan rather than a defect, and worth deleting rather than fixing.

---

## Tier 4 — carried to the next run

| | |
|---|---|
| Trek dig sites | **Unreached** — only part of the map was surveyed, so this is unmeasured, not negative ([76](../decisions/76-trek-archaeology.md)) |
| Story events | Four seen, all four correct on picture, framing and register. The pulse fires; [decision 79](../decisions/79-reachability-checks.md)'s worst case did not happen |
| The remaining hulls | Everything above destroyer, once item 1 lands |
| Event sound | `first_contact.5` and `first_contact.380` both logged `Failed to pick an event sound`. Small, real, cheap |
| Force-spawn a Trek empire | Item 4's remaining half, and the cheapest decisive test on this list |
| The music numbers | **55** names in the player, **27** in the rotation — not 22. Carry the right figures into the next plan |
| Stern mount symmetry | On the destroyer, `small_gun_01` sits at `{ 4.384 0.407 2.054 }` and `small_gun_02` at `{ -4.384 0.407 7.189 }` — mirrored in x but not in z. The run's own guess, that a horizontal mirror of the first is the right answer, is a live hypothesis; 66% of mounts are still bounding-box placements ([67](../decisions/67-source-art-hardpoint-names.md)) and this looks like one beside an artist's. **Only worth judging after item 1**, since today those guns are attached to nothing |

---

## What the run confirmed

Recorded so no future session re-opens them: the room behind the ruler is a Trek
room and the dropdown still runs past 300 entries
([48](../decisions/48-room-selector-merge.md),
[62](../decisions/62-city-set-cultures-undeclared.md)); the flag draws
([49](../decisions/49-flags-city-sets.md)); the corvette's mounts are right
([60](../decisions/60-mounts-share-existing-points.md)); the Federation anthem is
in rotation ([55](../decisions/55-federation-anthem.md)); nebula sizing on the
galaxy map is correct; a newly elected president wore the correct clothes; and
all four story events read as Trek, with pictures correctly fitted
([74](../decisions/74-event-picture-families.md),
[77](../decisions/77-trek-story-events.md)).

**The run also states what it could not see** — *"if there were oddities that
were missed they were likely not glaring"* — which is the honest form and should
be read as coverage, not as a pass.
