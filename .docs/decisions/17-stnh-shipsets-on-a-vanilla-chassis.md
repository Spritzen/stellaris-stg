# 17 — STNH shipsets on a vanilla chassis

**Date:** 2026-08-03
**Status:** applied, then **superseded in part by
[decision 18](18-walshicus-shipsets-replace-stnh-hulls.md)** — nine of the
fourteen cultures moved off this generator onto Walshicus' vanilla-chassis art,
so **the Assignments table below is no longer current for FED, VUL, KDF, ROM,
CAR, FER, THO, DOM or BRG.** What survives unchanged: the measurement that
defined the problem, the load-order rule, and the "two things deliberately not
done".
**Supersedes** the second half of plan.md §6's Phase 3 paragraph, which assumed
pointing `graphical_culture` at an STNH art directory was most of the work.

**The `locator` blocks this decision generates took two more rounds to get
right, and the intermediate readings were both wrong.** An `.asset` declaration
*does* satisfy the engine, and a `position` on it *does* place the gun
([decision 28](28-weapon-locator-positions.md)) — but neither holds in an entity
that also says `clone`, which discards everything declared beside it
([decision 30](30-clone-discards-sibling-locators.md)). `gen_shipsets.py` emits
them, with positions read off the donor mesh's bounding box, and copies the
donor body out rather than cloning wherever it needs to add one.

## The measurement that changed the job

plan.md §6 reads: *"the placeholder `graphical_culture` on all five species
classes and prescripted empires: vanilla shipsets today, the vendored STNH ones
after."* That reads as a rename. It is not, and the reason is measurable.

A Stellaris graphical culture is a **name prefix**, not a directory: the engine
resolves ship art by looking up `<graphical_culture>_<entity>`, where `<entity>`
comes from the ship size and its section templates. So a culture is complete only
if the art declares the names vanilla asks for.

Surveying all 106 vendored ship directories for the entity names vanilla's
reference culture (`mammalian_01`) declares:

| | corvette | destroyer | cruiser | battleship | civilian | stations |
|---|---:|---:|---:|---:|---:|---:|
| `mammalian_01` (vanilla) | 4/4 | 6/6 | 10/10 | 18/18 | 7/7 | 8/8 |
| **every STNH Trek culture** | **1/4** | **0/6** | **0/10** | **0/18** | 6/7 | 0–8/8 |
| `generic_06` (STNH's own vanilla-shaped set) | 3/4 | 6/6 | 10/10 | 11/18 | 7/7 | 4/8 |

STNH is a total conversion: it deleted vanilla's ship sizes and wrote its own
ladder — `corvette`, `strike`, `saber`, `steamrunner`, `assault_cruiser`,
`adv_cruiser`, `exploration_cruiser`, `sovereign`, `super_battleship` — every one
of them a **single-slot** hull (`part1` only) with three whole-ship section
variants named `coreA`, `coreB`, `coreC`. Vanilla's destroyer has two section
slots and its cruiser, battleship and titan have three.

So `graphical_culture = federation` on its own buys Trek civilian ships and
**mammalian\_01 warships**, because `fallback` silently supplies every name the
culture is missing. The gap is invisible to `make validate` and would have been
invisible in `error.log` too — a fallback that resolves is not an error.

*Two ways this could have been got wrong and was not.* An early count said
`generic_08` was a complete vanilla-shaped set; its vanilla entities are all
**commented out**, and a `name = "…"` regex that does not strip `#` reads them as
declarations. And `federation/` looked like it might carry multi-section hulls —
89 of its meshes contain a `partN` string — but per-mesh, every one is `part1`
alone; only `federation_fleet_museum.mesh`, a static prop, has more.

## What was built

`tools/gen_shipsets.py`, which emits 982 entity declarations into **one** file,
`src/gfx/models/ships/zz_stg_shipsets.asset`. Three mechanisms, all of them
vanilla vocabulary rather than invention:

- **`clone`** — vanilla's own ship assets clone entities across directories
  (`starbase_marauder_entity` clones `station_generic_01_entity`). Each vanilla
  hull name clones the STNH hull chosen for that size.
- **`locator = { name = "partN" … }`** — vanilla declares attach points in
  script 500+ times, `part2` 28 times and `part3` 46. The cloned destroyer,
  cruiser, battleship and titan frames get the slots their STNH meshes lack.
- **`stg_empty_section_entity`** — a no-mesh section, modelled on vanilla's
  `empty_section_entity`, which ten of its section-template files use.

Every cloned section also carries the gun mount points its vanilla templates name
and its STNH mesh lacks — the first list read from `common/section_templates/`,
the second by scanning the `.mesh` binary. 989 attach points, and only the
missing ones, so a real mount is never overridden with `{ 0 0 0 }`.

The mapping, by displacement along STNH's ladder:

| vanilla size | STNH hull | sections |
|---|---|---|
| corvette | `corvette` | the one slot takes `coreA/B/C` |
| destroyer | `saber` | bow takes the cores, stern is empty |
| cruiser | `adv_cruiser` | bow takes the cores, mid and stern empty |
| battleship | `sovereign` | bow takes the cores, mid and stern empty |
| titan, juggernaut | `super_battleship`, else `sovereign` scaled 1.5×/2.0× | as above |

Preference lists, not fixed assignments — the Bajorans have no `saber` and get
their `corvette` hull for the destroyer; Cardassians, Breen, Dominion and Borg
have a `super_battleship` and get a titan that is not just a bigger battleship.

**Choosing a bow section therefore swaps the whole Trek hull**, because an STNH
`coreA` is a complete ship rather than a nose. That is a consequence of the art,
not a design preference, and it reads well: three variants per class per empire.

### Why the mid and stern slots are empty rather than borrowed

The alternative is letting them fall back, which bolts a mammalian_01 stern onto
a Trek hull. Empty sections keep vanilla's ship designer intact — the slots, the
component templates, the weapon counts and the AI's auto-designs are all
untouched — and cost only the section geometry, which STNH never drew.

The gun attach points matter and nearly did not happen. Vanilla's
`empty_section_entity` declares `root` alone, and vanilla only ever pairs it with
section templates whose `locatorname = "root"`. The standard cruiser and
battleship templates name `large_gun_01`, `strike_craft_locator_02` and twelve
others, so an unmodified clone would have had every mid- and stern-mounted turret
fail to attach. The generator therefore gives **every** cloned section the mounts
its own templates name and its mesh lacks — both lists read, one from
`common/section_templates/` and one from the `.mesh` binary, so they follow the
game rather than a memory of it. The first version derived the list for the empty
sections only and left the bow sections and the titan short, which is 308 of the
2026-08-11 run's records.

### Stations and civilian craft are borrowed, not faked

Eight of the fourteen cultures declare two or fewer of vanilla's eight station
hulls, and Ferengi space had no colony ship, constructor or transport at all.
Falling back would have put vanilla starbases over Trek space — the most visible
object in the game after the ships themselves. Each culture instead names donor
cultures: Federation members borrow Starfleet designs, which is canon; the
Klingons borrow from `klingon_houses`, the Romulans from `reman_01`, the Dominion
from `karemma_01`, the Borg from `borg_02`; everyone falls through a shared tail
of STNH's generic sets. `sponsored_colonizer` and `guided_sapience_colonizer`,
which no STNH culture ships, clone the culture's own colony ship.

**Result: all fourteen cultures now score 4/4, 6/6, 10/10, 18/18, 7/7, 8/8 —
parity with vanilla's reference culture.** Two names still fall back for every
culture, `construction_window` and `military_station_section_hangar`, because no
STNH directory declares either.

## Load order — the part that cost a live run

**`clone` resolves against entities the engine has already loaded**, and it walks
`gfx/models/ships/` as a single alphabetical sequence with files and directories
interleaved. The first version of this pass put each culture's declarations in a
file beside the art it cloned, which is the obvious place and is wrong: 537
records, and the **Vulcan and Tholian shipsets did not render at all**, because
`vulcan_01` and `tholian_01` are the only two Trek directories whose names sort
after `stg`. Eleven cultures worked by luck of the alphabet. Cross-culture
station borrows failed the same way in whichever direction the alphabet ran.

Hence one file named `zz_stg_shipsets.asset`: `zz_` sorts after `zahl_01`, the
last directory in that tree, so every clone target is loaded before the file is
read. **Do not split it up.** Four independent slices of that run's log
establish the ordering rule.

`make validate`'s `check_asset_load_order` enforces it, confirmed to fire
against a deliberately reintroduced version of the defect before being trusted.
Its *other* half — whether a section entity carries the locators its templates
name — was rebuilt twice more; decision 30 is the current story.

## Assignments

| Class | Empire | Art directory |
|---|---|---|
| FED | United Federation of Planets | `federation` |
| VUL | Confederacy of Vulcan | `vulcan_01` |
| KDF | Klingon Empire | `klingon` |
| ROM | Romulan Star Empire | `romulan` |
| CAR | Cardassian Union | `cardassian_01` |
| FER | Ferengi Alliance | `ferengi_01` |
| BAJ | Bajoran Republic | `bajoran_01` |
| TRI | Trill Symbiosis | `federation_32` |
| ADR | Andorian Empire | `andorian_01` |
| BOL | Bolian Union | `bolian_01` |
| BRE | Breen Confederacy | `breen_01` |
| THO | Tholian Assembly | `tholian_01` |
| DOM | The Dominion | `dominion_01` |
| BRG | Borg Collective | `borg_01` |

**Trill is the one compromise: STNH ships no Trill art.** `federation_32` is a
Federation variant set, which suits a member world; it is also what the Trill
would fly.

Set on both the species class and the prescripted empire.
`city_graphical_culture` is left on its vanilla value throughout — STG does not
vendor STNH's city art, and inventing a mapping would only mislabel it.

## Two things deliberately not done

**No `common/ship_sets/` override.** plan.md §6 pointed at STNH's trick of
neutering vanilla's biological/mechanical split with `always = yes/no`. STNH
needs it; STG does not. Vanilla's `mechanical` set is
`NOT = { uses_ship_category = bio_ship }`, and no STG culture is a bio-ship
culture — not even the Tholians (LITHOID) or the Borg (MACHINE), since
`bio_ship` is Biogenesis' category. All fourteen land in `mechanical` unaided,
so shadowing a vanilla file would buy nothing and cost an override to maintain.

**No shipset display-name loc key.** Vanilla defines `<culture>_shipset_desc`
and nothing else per culture — there is no `humanoid_01:` key anywhere in its
localisation. Fourteen `_shipset_desc` keys are written in
`src/localisation/english/stg_shipsets_l_english.yml`; what the browser shows as
the *name* is an in-game observation still to be collected, not a guess to
encode.

## Verified, and how

- `make validate`: **ok — 6 warnings**, the same six pre-existing
  `common/random_names/` ones. No new finding.
- **982 entity names declared, 0 of them already declared anywhere in the built
  tree.** A name declared twice is one `pdx_entity` duplicate record per call
  site — the largest group in every live run to date is exactly that class.
- **Every `clone` target resolves, and resolves EARLY ENOUGH** — checked by
  walking the tree in the engine's order, not by asking whether the name exists
  anywhere. That distinction is the whole of the repair above.
- **No section entity we declare is missing a locator its templates mount on**,
  resolved through the clone chain into vendored and vanilla meshes.
- Brace balance.
- Per-culture parity re-measured **after** `make vendor`, against the built tree
  rather than against `src/`, because the question is about the merge.

## What the log cannot tell us

The same warning as [decision 16](16-phase-3-clothing-triggers.md): the failure
modes here are mostly silent. A fallback that resolves is not an error, a turret
attached at the hull origin is not an error, and a titan at 1.5× a battleship is
not an error. **Expect this change to cost close to zero error records, and do
not read that as confirmation.** The checklist below is the instrument.

### Prediction for the next live run

Superseded by a later run, which predicted a 1,692 load window with all three
new classes at zero.

**The prediction this section originally made is worth leaving on the record as
a lesson.** It identified all three failure modes correctly and put every one of
them in the *play* window, on the reasoning that ship art is drawn rather than
parsed. Two fired, both at **load**, because the engine resolves `clone` and
validates section locators while reading the tree. The number it committed to —
1,692 — was met exactly by the pre-existing groups, so the arithmetic was right
and the scope was wrong, and only the group-by-group reconciliation showed it.

### What only the user's eyes can grade

0. **Do the Vulcan and Tholian shipsets render at all?** They were invisible in
   the 2026-08-11 run and are the reason it was repaired.
1. Do Federation ships read as Starfleet at every size — corvette, destroyer,
   cruiser, battleship — or does one class still look like stock Stellaris?
   A vanilla-looking hull means a name this pass missed.
2. Do the three bow sections in the ship designer swap the whole hull, and are
   all three actually distinct models?
3. Are mid- and stern-mounted turrets visible, and are they somewhere sane
   rather than floating at the hull's centre?
4. Are the titan and juggernaut visibly larger than the battleship? For FED,
   VUL, KDF, ROM, FER, BAJ, TRI, ADR, BOL and THO they are the same hull scaled;
   CAR, BRE, DOM and BRG get a genuinely different one.
5. Are starbases and mining/research stations Trek? Ten of the fourteen cultures
   are flying borrowed ones — check the Bolians and the Tholians especially,
   they borrow the most.
6. Does the shipset browser in the empire designer show a readable **name** for
   each culture, or a raw key like `federation`? Vanilla defines no name key and
   this pass invented none.
7. Trill: `federation_32` is a compromise. Does it read as "a Federation member"
   or as "the Federation, again"?
