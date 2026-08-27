# Phases

> **What** — what each phase built, what it taught, and what it left behind.
> Each phase ends in something playable.
> **Open when** — picking up work, or wondering whether something has been done
> before and why it looks the way it does.
> **Then** — [Status](status.md) · [Open questions](open-questions.md) · [Scope](scope.md)

| Phase | State |
|---|---|
| [0 — the vendoring pipeline](#phase-0--the-vendoring-pipeline) | complete |
| [1 — playable Federation](#phase-1--playable-federation) | complete |
| [2 — the rest of the galaxy](#phase-2--the-rest-of-the-galaxy) | complete |
| [3 — art and identity](#phase-3--art-and-identity) | complete 2026-08-08 |
| [4 — polish](#phase-4--polish) | started 2026-08-08 |
| [5 — the clutter pass](#phase-5--the-clutter-pass) | complete 2026-08-07 |
| [6 — the static galaxy](#phase-6--the-static-galaxy) | **planned 2026-08-26**, not started |

---

## Phase 0 — The vendoring pipeline

**COMPLETE.**

`tools/vendor.py` + `vendor.yml` with zip unpacking and per-mod include/exclude
globs; `make vendor` / `provenance` / `clean-vendor`; and the `validate.py` checks
that checksum vendored files and flag an unannotated `src/` shadow. Two merges
landed in `src/`; the other two proved unnecessary
([decision 06](../decisions/06-gui-merges-unnecessary.md)).

---

## Phase 1 — Playable Federation

**COMPLETE.**

The vertical slice, establishing every pattern the other species copy. All five
majors landed together rather than the Federation alone — they share one file each
and the marginal cost after the first was small: species classes (`FED`, `VUL`,
`KDF`, `ROM`, `CAR`, deliberately unprefixed), portrait sets wired to the STNH
portrait groups, name lists, prescripted empires, and localisation.

**Two things from this phase are permanent gotchas rather than history:**

- **Every name token is a localisation key.** Stellaris has no literal mode: it
  looks a name token up as a key, always, and logs `Failed to localize` when it
  misses. This was first scored as 218 character names; it is **603 tokens**,
  because ship, ship-class and planet names work identically. Trek names with
  apostrophes therefore *must* be keys — no vanilla name list contains a bare
  apostrophe.
- **`sequential_name = "%O% Fleet"` is not a format.** Vanilla writes a loc key
  whose *value* contains `$ORD$` (`HUMAN1_FLEET:0 "$ORD$ Fleet"`); `%O%` appears
  nowhere in vanilla.

`check_name_lists` enforces both, so neither can come back silently.

**Vanilla's 52 prescripted empires are removed** — 19 comment-only shadow files,
so the picker and AI spawning offer Trek and nothing else. `default.txt` is
deliberately kept: it is the custom-empire template, not a playable empire.
[Decision 14](../decisions/14-remove-vanilla-prescripted-empires.md).

---

## Phase 2 — The rest of the galaxy

**COMPLETE.** 99 prescripted empires — 22 majors/quadrant/frontier powers and
77 minors, all playable and all in the pool the galaxy generator draws from
since [decision 88](../decisions/88-playable-gates-the-design-database.md) — over 99
distinct species classes. 92 name lists, 36 generated home systems plus vanilla's
Sol. `src/common/species_classes/stg_species_classes.txt` declares **129** classes —
the other 30 are the STNH selector stubs of
[decision 32](../decisions/32-declare-stub-species-classes.md), which are not
empires.

### The 22 majors, quadrant and frontier powers

The five majors, then nine more (Ferengi, Bajoran, Trill, Andorian, Bolian, Breen,
Tholian, Dominion, Borg), then eight frontier powers the Walshicus art made
possible (Caitian, Xindi, Suliban, Yridian, Krenim, Malon, Vidiian, NX-era Terran
Empire).

**Every authority/government/civic/ethic tuple is copied whole from a vanilla
prescripted empire rather than assembled**, because the game does not report an
invalid one — it refuses to start. The rules are in
[prescripted empire rules](../reference/prescripted-empire-rules.md).

Three are not BIOLOGICAL, for reasons recorded in the header of
`src/common/species_classes/stg_species_classes.txt`: **THO** is LITHOID
(crystalline; STNH's `CRYSTALLINE` archetype is not vendored), **BRG** is MACHINE,
**DOM** stays BIOLOGICAL because vanilla has nothing closer to a liquid-state life
form. The Borg are `auth_machine_intelligence` + `civic_machine_assimilator` — a
**machine** intelligence, not a hive mind; the assimilator civic only exists on the
machine side.

### 77 minor powers

Converted rather than authored: their identity is STNH's (names, species,
homeworlds, rulers, heraldry, 70 name lists totalling 6,302 loc keys), their
mechanics are vanilla's, because all 110 of STNH's use at least one STNH-only
origin, trait, civic or room and not one validates against 4.4 as written.
[Decision 19](../decisions/19-stnh-minor-powers-as-ai-empires.md).

They were built as **AI-only**, on `playable = stg_never` + `spawn_enabled =
yes`. There is no such state: `playable` gates the engine's design database, the
galaxy generator draws from that database, and so the gate kept them out of both
the picker and the galaxy for four live runs.
[Decision 88](../decisions/88-playable-gates-the-design-database.md) removed it —
all 99 empires are playable, and all 99 are in the pool the galaxy generator draws from — **though six galaxies running have drawn none of them**, and the 2026-08-26 save proved the pool itself is correct
([90](../decisions/90-design-database-is-not-the-cause.md)). The pool was never
the mechanism: AI empires are created by their home system's initializer, which a
static galaxy scenario places — [92](../decisions/92-create-country-initializers.md),
planned in [static-galaxy-plan.md](static-galaxy-plan.md).

### Species-class localisation

All 129 declared classes carry vanilla's 27-key family, derived off the class key
rather than prefixed `STG_` — which the engine never looks up.
[Decision 21](../decisions/21-species-class-localisation.md).

### Home systems

36 initializers plus vanilla's Sol, wired into **37** empires — all 22 majors,
quadrant and frontier powers, and 15 minors. The
Federation is on vanilla's own real Sol. The mirror Terran Empire used to
*share* that key — recorded here as meaning "a galaxy never holds both", which
was the wrong way round: two prescripted empires naming one starting system is a
documented engine failure that logs nothing and **costs both of them**. It has
its own authored mirror Sol since 2026-08-25.
[Decision 25](../decisions/25-real-home-systems.md),
[88](../decisions/88-playable-gates-the-design-database.md).

> **This file crashed the game at startup three separate times, and the pattern is
> the lesson.** First: eleven STNH identifiers the generator's remap tables passed
> through unchanged, into a tree that does not vendor STNH's `common/`
> ([26](../decisions/26-home-system-classes.md)). Second: the same class again,
> because the first fix repaired only the instances the evidence named. Third: the
> generator quoted the `class = star` **keyword**, which stops it resolving —
> **20 of the 37 systems spawned with no star**, and with no star there is no home
> starbase and no `capital_star` for the starting fleets. One log line for the one
> system that was played, 23 star bodies actually broken, and all three checks over
> the file were blind because they normalised the quotes away before comparing
> ([27](../decisions/27-quoted-class-keyword.md)).

**62 minors are still on generated systems**, because their STNH originals
are procedural and resolve against random lists in the `common/` we do not vendor.

### Trek names for systems and stars

Written 2026-08-08: 829 star names and 80 nebula names in
`src/common/random_names/base/stg_star_names.txt`, taking the pool from 5,702 to
**6,531** and nebulae from 71 to 151. Pools append
([44](../decisions/44-random-names-pools-append.md)), so none of Real Space's or
YAGEM's names are displaced. *(806 star names as of 2026-08-10 — re-running the
generator for [decision 81](../decisions/81-random-names-are-loc-keys.md) dropped
a backlog the tool's own rules exclude. Count the entries in the file, not this
line.)*

> **The source is STNH's `map/setup_scenarios/`, not its `star_names` pool, and
> the difference is the whole finding.** STNH's 5,992-entry pool looks like the
> obvious harvest and is the wrong one: its `### FICTIONAL ###` section is 796 of
> **vanilla's own** names relabelled, and the 5,156 it genuinely adds are filler —
> trees, scientists, surnames, `Enchilada`. The Trek content is in the ten
> hand-built maps, 1,444 systems placed by name. 183 were dropped because STG
> already owns them as a home system or capital (`Khitomer`, `Betazed`, `Risa`,
> `Rura Penthe`), which is decision 25's confusion arriving from the other
> direction. [Decision 52](../decisions/52-trek-star-names.md), which also corrects
> decision 44's pool arithmetic — short by 3.6×, because it missed YAGEM's two
> files feeding the same key.

### Random Trek empires — deferred, and the premise has since failed

Every STG species class is `randomized = no` on purpose — a random AI empire
rolling up as Klingons with random ethics and vanilla names reads as a bug.
This was deferred on the grounds that *"the minors already populate the galaxy,
so this is about variety now, not emptiness"*.

**That premise is false and has been for every run.** Six galaxies have been
generated with no Trek AI empire in any of them, and the 2026-08-26 save measured
it directly: every one of the 18 AI empires was a vanilla species class on a
vanilla name list. Emptiness, not a variety problem.
STNH's own answer to this is worth knowing: it sets `randomized = no` on all its
named Trek classes exactly as we do, and adds two classes of its own,
`RANDOMTREK` and `PRE_RANDOMTREK`, with `randomized = yes` so that randomly
generated empires still come out Trek-shaped. **That is a second, independent
route to a Trek galaxy and it does not depend on the prescripted pool being
drawn at all.**

**Since 2026-08-26 it may not be independent after all.** Vanilla is 32 of 33
spawn-eligible prescripted empires on a *randomizable* species class and STG is
0 of 99, which makes `randomized` a candidate for the prescripted question
itself rather than only a route around it —
[decision 90](../decisions/90-design-database-is-not-the-cause.md) has the
cross-tab and what argues against it. Either way the work is the same shape and
the cost is the same: **vanilla ships a `common/species_names/` entry for every
class it randomizes and STG ships none for its 99**, so this was never the one
line it looks like. Phase 4 at the earliest.

---

## Phase 3 — Art and identity

**COMPLETE (2026-08-08).**

Wire the vendored art to our species and empires. The bytes arrive with the
vendoring; this phase is the *script* that points our content at them.

### Clothing

STNH's 140 harvested art triggers were all defined in one pass and the era,
identity, role and stratum ones given real bodies
([16](../decisions/16-phase-3-clothing-triggers.md)), so the Starfleet, Klingon,
Romulan and Cardassian uniforms already in the tree became reachable. The file
now declares 141, 24 of them with a body —
[stnh-art.md](../architecture/stnh-art.md#stnhs-art-is-wired-to-stnhs-namespace--in-four-ways).

> **The empire designer was still dressing five species as humans, and it is a
> *scope* decision 16 never looked at.** `game_setup` is the only scope the picker
> reads, and STNH's two master selectors leave it a bare human-civilian default —
> right for the per-species selectors every other Trek people has, wrong for one
> shared by 44 classes. [Decision 22](../decisions/22-empire-designer-clothes.md).
>
> **Read that in the opposite direction and it is decision 64.** Getting
> `game_setup` right says nothing about the five scopes the *game* reads, and the
> Terran Empire was gated in the designer and in **none** of them — its ten
> ENT-era mirror uniforms want `uses_mirror_starfleet_uniform` /
> `uses_terran_uniform_ruler` / `enterprise_era`, all three on decision 16's INERT
> list, so every Terran leader wore a generic uniform. Turning an era on **per
> empire** rather than globally is the mechanism; *"exactly one era may be true"*
> constrains what one leader sees, not the whole mod. The sweep also found **four
> rows in the female master selector missing the species gate the male file has**,
> so every ungated non-Federation female operations commander wore Vulcan clothes.
> Five more classes still fall through, four of them on minors and unloggable.
> [Decision 64](../decisions/64-terran-empire-mirror-uniforms.md).
>
> **The starting ruler was wrong for a second, independent reason.** Every
> prescripted `ruler = { }` pinned `texture = 1 clothes = 1` — indices, not flags,
> copied from the first empire file into all 101. `texture = 1` is off the end of
> the list on **74** of them.
> [Decision 23](../decisions/23-prescripted-ruler-appearance.md).

### Shipsets

A graphical culture is a *name prefix*, not a directory: the engine resolves art as
`<culture>_<entity>`, and every STNH Trek culture declares one of vanilla's four
military hull entities and **none** of its 40 section entities, because STNH
replaced vanilla's ship sizes with its own single-slot ladder.
`graphical_culture = federation` alone therefore buys Trek civilian ships and
mammalian_01 warships, silently, via `fallback`.

Nine of the then-fourteen cultures moved to Walshicus' sets, which declare all 44
section entities natively; five (BAJ, TRI, ADR, BOL, BRE) have no such set and
stay on entities generated by `tools/gen_shipsets.py`.
[Decision 18](../decisions/18-walshicus-shipsets-replace-stnh-hulls.md),
superseding [17](../decisions/17-stnh-shipsets-on-a-vanilla-chassis.md) in part.
`common/ship_sets/` needed no override. **The eight frontier powers added later
in Phase 2 all name a Walshicus set too, so the standing figure is 17 of 22**;
the five above are still the only generated ones.

### Weapon mounts — four passes, and both halves had to be true

Trek ship art mostly does not bake gun locators into the `.mesh`; it declares them
in the `.asset`, either with no `position` or at `{ 0 0 0 }`, leaving every gun at
the model origin. An `.asset` declaration *does* satisfy the engine — but **only in
an entity that does not also say `clone`**, which discards everything declared
beside it.

[Decision 28](../decisions/28-weapon-locator-positions.md) gave the mounts real
positions read off each mesh's bounding box;
[decision 30](../decisions/30-clone-discards-sibling-locators.md) moved the
generated ones out of `clone` blocks. **The baseline is now 0, so any movement is a
finding.** Starbases, orbital rings and defence platforms are deliberately excluded
— no hull to spread guns along, so placing them would be inventing.

> **The bounding-box spread was itself a guess wherever the artist had already
> answered**, which is the 2026-08-08 pass and
> [decision 60](../decisions/60-mounts-share-existing-points.md). The Starfleet TNG
> corvette bakes two mounts on the centreline at the bow and the spread put the
> third starboard and amidships — plausible, inside the hull, and visibly not the
> artist's; a live run caught it by eye with no log record anywhere. A missing
> mount now SHARES a point somebody drew: the section's own placed mounts first,
> then any other hardpoint the same mesh bakes, and only then the bounding box.
> Re-derived across all 27 shipsets: 157 overrides, 1,626 mounts placed, and **599
> of 1,751 positions now sit on a point the artist drew, against 0 before**. The
> remaining 1,152 are meshes that bake no locator at all, which is the original
> defect rather than a shortfall of the rule.

> **"What does the game mount on" is not "where did the artist draw a gun", and one
> derived set was answering both.** Vanilla's 201 `locatorname`s never say
> `torpedo`, `point_gun` or `extra_large_gun` — the Trek art's own words for a
> tube, a point-defence mount and a spinal gun — so 164 meshes baking
> `point_gun_01` and 189 baking `torpedo_01` were invisible as anchors, and the
> Terran NX corvette stacked all three of its guns on one of the two points its
> mesh carries. Split in two, with the borrowed stems labelled as borrowed and a
> second sweep over all 1,182 meshes adding the `.001` exporter suffix, the
> `_l`/`_r`/`_X` side suffix and two more stems — **157 names recognised against
> 94, 263 positions moved across 71 section entities, and no mount changed tier.**
> The cost was spread, never correctness. It was missed because every number
> decision 60 reported counts what the rule *did*, so a rule blind to a whole kind
> of point moves none of them; the tool now prints the names it does **not**
> recognise. [Decision 67](../decisions/67-source-art-hardpoint-names.md).

> **Section ATTACH POINTS are a fourth pass and a different database.** The above
> reads `common/section_templates/` and asks whether a *section* carries the mounts
> its template fires from. `common/ship_sizes/` also declares `section_slots`,
> naming `part1`..`partN` on the *hull* — and all 22 Walshicus shipsets bake none
> of them into their station meshes and declare only `root`, so the sections have
> nowhere to attach at all. Fixed by 66 `vendor.yml` patches.
> [Decision 35](../decisions/35-station-section-attach-points.md).

### Flags, early

The 22 majors, quadrant and frontier powers fly vendored STNH heraldry from
`flags/trek/`, done
alongside Phase 2 because the files were already there.

### The STNH ship-model prune

Forced rather than chosen: STNH and Walshicus both ship a `klingon` and a `romulan`
directory, so harvesting STNH's tree whole meant the newer art winning the `.gfx`
declaring a mesh while STNH's `.asset` using it survived. **43 directories of 104.**
Read `vendor.yml`'s list rather than this sentence — it grew twice after the prune.

> **That prune bit back three times, and all three bites are the same shape.** Five
> directories restored after a run measured 1,640 records from 15 `.mesh` files
> that kept art still declared; 190 more were textures named as bare filenames by
> `.gfx` files we kept, none of which were in the tree at all
> ([24](../decisions/24-group-c-texture-references.md)); then `attach` edges
> nothing was following ([37](../decisions/37-attach-edges-into-pruned-art.md)).
> **"Declared" is not "present":** an include list converges on whatever question
> the checks ask, and it asked about mesh *names*, then mesh *files*, and never
> about textures. One file type further down each time. All closed, each by a check
> that can now fail — and Phase 5 is the systematic answer.

### Rooms

Closed 2026-08-08 and the largest of the four.
`gfx/portraits/asset_selectors/room_textures.txt` in the tree was **STNH's 3.12
copy at vanilla's path**: 23 of vanilla's 42 designer rooms and 35 of its 55
`ruler` rules simply absent, and all 29 Trek rooms it names gated on country flags
STG never sets. Of 327 room textures the designer offered **19**.

STG now ships one merged selector — vanilla verbatim + 47 Trek rooms keyed on
species class + Diverse Rooms' 297, whose own second `room_selector` is excluded
because two files claiming one selector name is decided by nothing on disk. The 101
empires' `room =` values, which had been replaced wholesale by vanilla personality
rooms, are restored from STNH's own assignment: **95 of 101 changed.**
[Decision 48](../decisions/48-room-selector-merge.md).

> **Nothing could have reported it, and that is the transferable part.** A room is
> the only art in the game addressed by a BARE NAME with no path and no declaration
> — so nothing dangles, and twenty-odd cross-reference checks were structurally
> blind to the whole database at once. `check_vanilla_regression` read the file and
> passed it, because `room_selector` was still declared. Decision 33's rule one
> level deeper: here the identity is the entries INSIDE the block.

### City sets

Mostly already true and nobody had checked: STNH re-cuts `humanoid_01`,
`mammalian_01`, `reptilian_01` and thirteen more at *vanilla's own paths*, so every
empire left on a vanilla prefix has drawn Trek cities since the first harvest. The
six STNH ships under its own name — `borg_01`, `cardassian_01`, `klingon`,
`tholian_01`, `undine_01`, `vulcan_01` — are now named by the six empires they were
cut for. [Decision 49](../decisions/49-flags-city-sets.md).

### Loading screens

Needed no work, established by measurement: STNH replaces all 20 of vanilla's and
adds six, nothing in either tree declares one, and `tools/clutter.py` already
records `gfx/loadingscreens/*` as a root because the engine picks by directory. 26
Trek screens have been live since the first harvest.

### The shipsets' 39 extra flags

Harvested additively. `additive_only` now takes a list of path prefixes as well as
`yes`, because the shipsets must beat STNH on `gfx/`
([18](../decisions/18-walshicus-shipsets-replace-stnh-hulls.md)) and must **not**
beat it on `flags/` — where 12 of their 14 colliding files are a *different size*,
256×256 against STNH's 128×128. The 39 arrive, STNH's 541 are untouched, and the
Malon stop flying the Talaxian flag.

**The 22 minor powers on `neutral.dds` are a separate problem the 39 do not
solve** — swept against all 155 Trek flags, exactly one (`hur'q.dds`, missed on the
apostrophe) has art. The other 21 take a distinct vanilla icon each, which is what
STNH itself does for four of them. [Decision 49](../decisions/49-flags-city-sets.md).

### `paragon_backgrounds.txt`

STNH's copy stays excluded — 31 of its 32 triggers are declared now, but four of
those are on decision 16's INERT list, so it would reach nothing while dropping
vanilla's four legendary rows. STG declares its own instead: 28 rows on species
class plus `src/interface/stg_paragon_backgrounds.gfx`, because a background name
resolves to a *sprite* and STNH declares its sprites in `interface/`, which we
never take.

23 of the 52 textures reached, and they came back out of `.source/` by themselves
as predicted — the prune count fell from 990 to 967 with no edit to `vendor.yml`.
[Decision 50](../decisions/50-paragon-backgrounds.md).

### Outstanding from this phase

Whether the Walshicus sets actually *draw* their weapons is something only the
user's eyes can grade — a locator that resolves produces no log record. The same is
true of every room, city set and leader background wired above.
[Open questions](open-questions.md).

---

## Phase 4 — Polish

**STARTED 2026-08-08.**

Trek-flavoured events, anomalies and archaeology. Revisit hand-placed home systems
if Trek-named random ones turn out not to be enough. This is where the mod stops
being a reskin and starts having a voice — and it is also infinite, so it comes
after everything with a definition of done.

**All three things [decision 75](../decisions/75-trek-anomalies.md) scoped are
now shipped** — anomalies ([75](../decisions/75-trek-anomalies.md)), archaeology
([76](../decisions/76-trek-archaeology.md)) and story events
([77](../decisions/77-trek-story-events.md)), 2026-08-09. What remains in the
phase has no scope written for it yet.

**One thing is already queued behind it: integrating More Events Mod**, which is
subscribed for that purpose and deliberately untouched until the content above
has been through a live run —
[decision 80](../decisions/80-mem-integration-deferred.md).

### Done: music

[Decision 55](../decisions/55-federation-anthem.md).
`music/Anthem_of_the_United_Federation_of_Planets.ogg` now plays. `music/` has
**two** halves, an `.asset` mapping a name to a file and a `.txt` putting that name
in the playlist, and the anthem had neither — the only one of the tree's 17 tracks
nothing declared. `src/music/stg_music.{asset,txt}` declare it at vanilla's own
default volume, and `check_music_declarations` now asks both directions against a
vanilla floor of 30 tracks, 30 declarations, 0 dangling. The main menu needed
nothing: STNH already repoints `maintheme` at its own theme.

> **`music/` has a THIRD half, and it is what the player reads.**
> [Decision 61](../decisions/61-music-player-track-names.md): the player shows the
> declaration NAME looked up as a loc key, and a name with no key is drawn verbatim
> while logging nothing — *a name that resolves to itself still resolves*. **16 of
> 22 entries listed as `newhorizonssong1`, `maintheme7` and our own
> `stg_ufp_anthem`.** Titles harvested from STNH's localisation, then from the
> `.ogg`'s own Vorbis TITLE tag where STNH names nothing. `maintheme` had been
> showing vanilla's "Creation and Beyond" over STNH's theme since the first
> harvest.

> **And a FOURTH question none of the three asks: which declared tracks are in the
> rotation, and are any of them the same recording.**
> [Decision 65](../decisions/65-music-rotation-dedupe.md). The rotation is **27
> entries / 27 distinct recordings**, down from 32/27: `maintheme` and STNH's
> `maintheme1`–`maintheme10`/`12` are **twelve declaration names for one file**,
> six of which carried a playlist entry, so the theme held 19% of the rotation.
> Decision 61 had found six of the twelve and kept them at the user's direction;
> that is now reversed and five comment-only `src/music/*.txt` remove the aliases
> from the playlist while leaving the declarations, which are what keep the `.ogg`
> reachable. **Nothing on disk produces the ~86 the user counted** — 55 is the
> merged declaration count, 47 the audio-file count.
>
> Left open: STNH's `songs.txt` shadows vanilla's and **comments out all 17 vanilla
> tracks**, which is why 27 rather than 44. Restoring them is a taste call in the
> opposite direction to the one that was asked for.

### Done: the ship registries

[Decision 59](../decisions/59-ship-name-pools.md). STG's 92 name lists were
hand-written in Phase 1 and never revisited — 6,093 tokens, a median of 62 per list
against vanilla's 116, so the Federation had five cruiser names and then repeated.
STNH has 38,707, keyed by its own hull ladder (`fed_heavy_cruiser_nebula`, 96
names) which a vanilla chassis cannot ask for.

`tools/gen_ship_names.py` folds them onto vanilla's ship sizes by an explicit
tonnage table — an unmapped key stops the build — and re-emits the values as
`STG_N_` keys. **88 lists, 6,093 → 32,805 tokens, 9,951 new name keys.**
> **The other half is done, and the answer was that the question was wrong.**
> [Decision 72](../decisions/72-ship-class-names.md): STNH's name lists carry
> their own `ship_class_names` block, one loc token per hull, declaring **165 of
> the 177 Trek hull keys** — so the fuzzy join decision 59 called for was never
> needed, and it was built, measured and deleted. It contributed nothing but
> would have put **Saber, Steamrunner and Sovereign in the Klingon fleet**,
> because STNH's cross-empire hulls are literally named that.
> `tools/gen_ship_class_names.py` imports 59's tonnage table rather than
> restating it. **92 lists, 820 → 1,766 tokens, 286 new class keys.**
>
> It also reverses 59's exclusion of `bolian`, `breen`, `bajoran` and `andorian`
> **for class names only** — right for registries, wrong here, and three of the
> four declare their own. Searching Memory Alpha and then Memory Beta for the
> five of those empires still without a size split returned **nothing worth
> taking**: canon names no classes for Tholian, Vidiian, Trill or Yridian ships,
> and what STG hand-wrote in Phase 1 is already the better material.

### Done: the class names STNH does not have

[Decision 73](../decisions/73-class-name-thematic-fill.md), and the model is
vanilla. Its 13 class-name lists use exactly two idioms — invented
species-language words (HUM1's `Il-Koth`, LITH3's `Kroshhk`) or **one semantic
field in plain English** (NEC4's vices, HIVE2's robustness, AQU1's water) — and
the second is what STG's Phase 1 pools already are, so extending a register is
not inventing lore. **99 hand-authored names across 15 lists, 820 → 1,864
tokens, and 21 of those 22 now carry all five core tiers** against 13.

> **Vanilla never splits this block by tonnage at all** — all 13 lists are
> `generic` only, 17–40 names, median 22. STG splits because a Trek class *is*
> its tonnage, but vanilla's pool sizes are the yardstick and STG is still under
> them. Left thin rather than padded.
>
> The subtlety worth carrying: **`generic` is drawn at any tonnage** — vanilla's
> README puts it at 50/50 against the size-specific list — so STG's ten
> hand-written names had to be *demoted out of* generic once a size claimed
> them, or Nebula would still land on a corvette half the time. Matched by
> shape, because STG wrote `DDeridex` and STNH writes `D'deridex`.

### Done: the Trek anomalies, and the scope call behind them

[Decision 75](../decisions/75-trek-anomalies.md), 2026-08-09. This section used
to say the phase's remaining work had no external definition of done and had to
be **scoped deliberately before starting**; that is the call, made: **anomalies
first, archaeology and story events after.** An anomaly is the smallest complete
unit of voice the game has — a category, an outcome, a picture and four hundred
words — and vanilla's base game ships **40** categories, which is a yardstick
where archaeology has none.

**21 categories, 27 outcome events, 24 Trek pictures over 48 sprites, 123 loc
keys, ~3,500 words.** Half of vanilla's base-game count, thin rather than padded
— [decision 73](../decisions/73-class-name-thematic-fill.md)'s call about pool
sizes, applied to a different database. Every trigger, reward tier, deposit,
modifier and guard is copied from a vanilla file that was opened, including the
`clear_deposits` guard vanilla puts before every research deposit, without which
the research station is unbuildable and the reward unreachable. No `specimen`,
no DLC-gated branch: STG is standalone.

> **The art had to be unlocked first, and that is the larger finding.**
> [Decision 74](../decisions/74-event-picture-families.md). STNH ships ~1,430
> event pictures and the closure pruned **805** of them every build, exactly as
> [decision 42](../decisions/42-event-picture-geometry.md) predicted it would
> until somebody wanted Trek art on Trek events. Declaring one is two lines;
> declaring one also puts 620×264 art in a window cut for 450×150, which is
> decision 42's own defect in decision 42's own directory. `target: family` was
> the lever, and both the build and the check had refused it here in the same
> words — *"580 of its 639 are 450×150 and the other 59 are a genuine second
> size"*. **True of the directory, false of both families in it:** the 59 are
> the `origins/` subdirectory, 59 of 59 at 220×115, and the top level is 580 of
> 580. Split, each is 100% uniform against a 90% floor. 722 → **1,661** files
> re-cut, `make vendor` 35 s → 75 s, and the 24 pictures the first `.gfx` named
> came back out of `.source/` by themselves — prune 959 → **935**, with no edit
> to `vendor.yml`.

`check_anomalies` ties the four halves together and **failed on its first run
against real content**: the Iconian Gateway category and both its events shipped
with no localisation at all — one authoring slip, invisible to every other check
and to `error.log`.

### Done: the archaeology, and the field that decides whether it is ever seen

[Decision 76](../decisions/76-trek-archaeology.md), 2026-08-09, and it did copy
what the anomalies established — the picture pipeline, the loc shape, the
five-files-must-agree check. **6 dig sites, 27 stage events, 27 Trek pictures
over 54 sprites, 9 finale modifiers, 117 loc keys, ~3,800 words.** Six against
vanilla's base-game ten, thin rather than padded, on the same call
[73](../decisions/73-class-name-thematic-fill.md) made about pool sizes.

> **`weight` is the whole question, and six of vanilla's ten decline it.** A
> site type's `weight` block is read by exactly one thing —
> `create_archaeological_site = random`, whose only caller in the game is
> `ancrel.9999` on `on_survey_planet`, and whose trigger asks nothing about DLC.
> Vanilla's other six base-game sites carry `weight = 0` and are placed by a
> story chain that knows where it wants them. **STG writes no story chain**, so a
> `weight = 0` site here is complete, correct, validating clean and unreachable
> — [decision 62](../decisions/62-city-set-cultures-undeclared.md)'s defect
> class, one database over. All six carry real weights keyed on planet class.

> **Eleven pictures were rejected on what the crop showed**, not on the filename:
> four TAS-animated frames, three close-ups of a named character's face, two
> near-featureless gradients and two too dark to read at 450×150. Three of the
> eleven were named after exactly the subject a site wanted. And **four first
> choices were already spent on an anomaly** — `theChase`,
> `undergroundTunnels`, `stone_of_gol`, `ancientCapsule1` — so the sites took
> the siblings. One picture, one subject.

`check_archaeology` asks ten questions vanilla scores 0 on across its 123 site
types and 475 stage events — one of them, **`stages = N` against the `stage`
blocks beside it**, has no counterpart in `check_anomalies` and is the one most
worth having — plus one at a floor of 1 and an eleventh scoped the way
[51](../decisions/51-prescripted-loc-scope.md) established.

**And a twelfth as of [decision 79](../decisions/79-reachability-checks.md):
`weight` itself**, which is the field this section calls the whole question and
which no check asked until the [2026-08-15 audit](../analysis/2026-08-15.md)
went looking. A site with no positive weight that nothing in script names can
never be placed; vanilla's floor for that pair is 0 of 123, so it is asked of the
whole tree. `check_anomalies` gained the same question over `spawn_chance`.

### Done: the story events, and the merge question the design refuses to ask

[Decision 77](../decisions/77-trek-story-events.md), 2026-08-09, and it
completes the scope [decision 75](../decisions/75-trek-anomalies.md) set.
**3 hooks, 21 story events + a 2-event pulse gatekeeper, 21 Trek pictures over
42 sprites, 84 loc keys, ~4,000 words.** Twelve belong to one people and are
gated on species class — the Academy and the Council, the road to Gol, a
challenge on the floor of the Great Hall, the Continuing Committee, a Cardassian
tribunal, an amendment to the Rules of Acquisition, the Celestial Temple, a Borg
efficiency deviation, a Founder's visit, the Symbiosis Commission, the Ushaan.
Eight are open to every empire and are the life of a starfaring service. The
twenty-first hangs on first contact.

> **The design's one real decision is what it declines to do.** Vanilla's
> `on_five_year_random_pulse_country` is the slot the base game reserves for
> exactly this and is very nearly empty on a standalone host — of its 435 points
> of content, all but one entry is DLC. `events = { }` lists demonstrably merge
> across files; **whether a second file's `random_events` merges or REPLACES is
> a question nothing on disk answers**, and being wrong the replacing way
> deletes vanilla's own `1900 = 0` and fires a story event nearly every pulse
> for the rest of the game. `stg_on_five_year_story_pulse` is our own on_action
> key, reached by one line in an `events` list — the merge behaviour that is
> proven — so we own every weight including the one for "nothing happens".
> Calibrated at **21% against vanilla's own 18.6%**, and because
> `random_events` fires exactly one winner, growing the pool later cannot make
> the player see more popups, only different ones.

`check_story_events` asks four questions and **the first has no counterpart in
either sibling: is the on_action KEY itself one the engine will ever fire?** A
hook whose key is wrong parses, its events exist, its art loads, and nothing
under it ever runs — decision 76's `weight = 0` in a seventh database. Vanilla
scores 0 across the built tree's 58 hooks once empty stubs are excluded, and
**17 in its own `00_on_actions.txt`**.

> **Its first run found a defect in the two checks beside it rather than in the
> content.** 26 hooks in Real Space, Planetary Diversity, Ariphaos and System
> Scale were reported as firing events nobody declares, and every one of those
> events was in the tree, declared as a bare **`event = { }`** — legal, written
> by vanilla in forty-odd of its own files, and not matched by
> `kind.endswith("_event")`. All three checks now share `_is_event_block`.
> **Missing the bare form does not make an event dangle; it makes a check
> believe one does**, which is worse, because the next move is to repair content
> that was never broken. Neither sibling's floor moved.

> **Three pictures were rejected for a reason none of the earlier passes had**:
> `engineering_bay`, `cargoship_caravan` and `galactic_market` are STNH shipping
> **vanilla's own art under vanilla's own name** — Stellaris concept art, in a
> Trek directory, with a Trek-sounding filename. 580 of STNH's 1,350 event
> picture names also exist in `/stellaris/gfx/event_pictures`; only the other
> 770 are art STNH added. Eight more were rejected on what the 450×150 crop
> showed, on [75](../decisions/75-trek-anomalies.md)'s standard.

---

## Phase 5 — The clutter pass

**COMPLETE (2026-08-07).** Pipeline work rather than content, taken out of order
because it changes what every later phase inherits.

23,555 files / 15.0 GB → **22,309 / 14.1 GB**: 964 removed by the closure, 323 by
explicit excludes.

The mechanism, its calibration and the four non-obvious things about it are in
[the clutter closure](../validation/clutter.md); the decision is
[45](../decisions/45-clutter-pass.md).

---

## Phase 6 — The static galaxy

**PLANNED 2026-08-26. Not started.** The full plan is
[static-galaxy-plan.md](static-galaxy-plan.md); this is what the phase is and why
it exists.

Six galaxies contained no Trek AI empire. Three fixes went into the prescripted
pool — [86](../decisions/86-prescripted-empires-never-drawn.md)'s spawn chance,
[88](../decisions/88-playable-gates-the-design-database.md)'s `playable` gate,
[90](../decisions/90-design-database-is-not-the-cause.md)'s five hidden designs —
and the 2026-08-26 save proved the pool is *correct* and still never drawn.

**The pool was never the mechanism.** `prescripted_countries/` is the player's
roster. AI empires in a total conversion are **created by their home system's
initializer**, which a **`static_galaxy_scenario`** places on the map. Vanilla
does it for the United Nations of Earth in `com_sol_system`; STNH does it 40
times — [decision 92](../decisions/92-create-country-initializers.md).

Four pieces: the scenarios, the `create_country` initializers (generated off
`prescripted_countries/`, not hand-written), locking the picker to STG's own
scenarios by shipping vanilla's five as empty files, and a `make validate` check
that the map is a connected graph naming things that exist.

**The lanes looked cheaper than they were, and this paragraph is the reason
why** — corrected by [94](../decisions/94-static-map-lanes-are-generated.md).
All 22 STNH maps set `random_hyperlanes = no`, and only **one of the 22 defines
any lanes** — the BotF map, 468 systems and 892 `add_hyperlane` lines. That much
is measured and holds. What does not hold is the conclusion: the other 21 do not
go without a lane graph, they **build one in script** at game start
(`every_system = { connect_neighbour_stars = yes }`, in `events/STH_start.txt`).
STG vendored the header and not the script, and shipped a galaxy with one
hyperlane in 98 systems. STG now generates its lanes into the file, as BotF
does, and `make validate` rejects a lane-less static map. The cost driver is
still the systems; the lanes were never free.
What STG already owns is the identity half — 36 real home systems
([25](../decisions/25-real-home-systems.md)), 99 empires whose `create_country`
blocks are a mechanical transcription of entries that already exist, and the
1,444 Trek systems already harvested by name
([52](../decisions/52-trek-star-names.md)).

**Ends in something playable**, like every phase here: one small scenario, the 22
majors on their real home systems, proven in a live run before anything scales.
