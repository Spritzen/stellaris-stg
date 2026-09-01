# What `make validate` checks

> **What** — a catalogue of every check in `tools/validate.py`, grouped by the
> kind of question it asks, with the live failure each was written for.
> **Open when** — a check fires and you need to know what it means, or you are
> about to add one and want to know what is already covered.
> **Then** — [How to write a check](check-design.md) · [Acks](acks.md) · [The clutter closure](clutter.md)

`make validate` asks six kinds of question. The grouping matters more than the
list: **most new findings are a known question asked of a new database**, and
knowing which family you are in tells you how to calibrate.

> **Why the cross-reference families exist at all.** On 2026-08-01 this script
> reported `ok — 0 warnings` against a build throwing **~8,780 errors**. Structure
> was fine; nothing was checking that one file's *names* resolved against
> another's. **Do not add a check that only reads `src/` when the question is
> about the merge.**

---

## A. Structure — is the file well-formed?

| Check | Asks |
|---|---|
| `check_localisation` | UTF-8 BOM present, every key has a `:0` version, loc syntax parses |
| `check_script` | brace balance across `.txt` / `.gui` / `.gfx` |
| `check_vendored` | no hand-edit to a generated file, by checksum |
| `check_src_shadowing` | every `src/` file shadowing a vanilla or source path carries a header saying what it overrides and why |
| `check_descriptor` | `descriptor.mod` has not drifted from what the build declares |
| `check_manifest_parses` | `vendor.yml` is valid YAML and declares the sources `.source/` holds |
| `check_sources` | every declared source is snapshotted |
| `check_selector_texture_paths` | every quoted texture path in `gfx/portraits/asset_selectors/` ends in `.dds` — the **syntax half** of the malformed-path question |

The BOM rule asks vanilla **per folder** rather than asserting one answer:
`common/name_lists/` is BOMed 76 times out of 76 and every other database zero.

`check_selector_texture_paths` is here rather than in family B because it asks
nothing about resolution. A path with no extension is malformed whatever is on
disk, and appending `.dds` cannot be the wrong answer — so it landed on its own,
ahead of the harder *and resolves* half, which is now
`check_selector_texture_files` in family B. **That half's "196 findings, each
needing a content call" was a measurement error**: the population was 117 rows,
76 of them repaired with no call to make and the remaining 41 under one policy,
and **the tree is now at zero**
([80](../decisions/80-selector-textures-that-resolve.md)). Vanilla writes **7,845** such paths and every one ends `.dds`; no other
extension appears in that position at all, so the floor is 0 and there is no
scope. The engine falls back silently on a miss, which is why 10 rows survived
two live runs: the log records only the rows somebody actually drew.
Opened by the 2026-08-10 Federation run and widened by the 2026-08-22 Vulcan
run; [78](../decisions/78-widen-attach-points-and-two-new-checks.md) is where
both landed.

---

## B. Names that must resolve against the merged tree

The largest family. Each asks: *this file names something — does anything
declare it?*

| Check | Asks | Written for |
|---|---|---|
| `check_dangling_identifiers` | scripted triggers, traits and species classes the vendored art names | 34 STNH species classes falling through to the clothes selector's `default` — [30](../decisions/30-declare-stub-species-classes.md) |
| `check_dangling_shaders` | shader effects a mesh names | Real Space's gas giant rings drawing with no material — [32](../decisions/32-src-shadows-drop-source-declarations.md) |
| `check_dangling_art_references` | meshes and particles a vendored `.asset` names | |
| `check_selector_texture_files` | that a quoted asset-selector texture path resolves against the built tree **or vanilla** — the *resolves* half of the malformed-path question | 117 rows naming art that is in neither — carried as 196 until vanilla was put back in the resolution set — [80](../decisions/80-selector-textures-that-resolve.md) |
| `check_gfx_file_refs` | bare texture filenames a vendored `.gfx` names, and whether the file is on disk | 190 textures named by kept `.gfx` files, none in the tree — [22](../decisions/22-group-c-texture-references.md) |
| `check_texture_basenames` | a `meshsettings` texture — a **bare** filename — resolved by basename against everything loaded, vanilla included | the sibling above skips bare filenames, which left `texture_diffuse = "foo.dds"` unasked in any form: 139 `Failed to find texture` records, **not one** of them in the built tree, against a clean `make validate` |
| `check_asset_variables` | `@variable` an art file references that neither it nor `common/scripted_variables/` declares | loads as `Malformed token` and drops the value — [29](../decisions/29-asset-local-variables.md) |
| `check_initializer_classes` | planet classes, star classes and asteroid belt types a solar system initializer names | a startup crash that logs **nothing at all** — [24](../decisions/24-home-system-classes.md) |
| `check_attach_targets` | entities named by `attach = { "slot" = "X" }` | vanilla leaves 0 of its 5,672 such references unresolved — [35](../decisions/35-attach-edges-into-pruned-art.md) |
| `check_room_references` | the room or city set a prescripted empire names, backed by a real `*_room.dds` / `*_city_l01.dds`; and the `common/graphical_culture/` entry behind a city set | the one database addressed by a **bare name with no path and no declaration** — [46](../decisions/46-room-selector-merge.md), [59](../decisions/59-city-set-cultures-undeclared.md) |
| `check_graphical_culture_art` | an **offerable** graphical culture that reaches city art — its own `<key>_city_l01.dds`, or one its `fallback` chain arrives at | the reverse of `check_room_references` question 6, and the check that **falsified the finding it was written for**: 24 of vanilla's 52 declared cultures ship no city art of their own, so "declared implies art" is not the rule; follow the fallback and vanilla is 0 of 22 and STG 0 of 41 — [79](../decisions/79-shipset-descs-and-home-system-names.md) |
| `check_shipset_descriptions` | a graphical culture a prescripted empire **flies** with no `<culture>_shipset_desc`, and a description key naming a culture nothing declares | 30 of 30 wrong in one direction or the other: 7 keys written against the **city-set** culture names and 23 flown cultures with none, so every Walshicus set drew a raw key. Vanilla is **0 of 19** flown and **0 of 20** keys, while keying only 20 of its 52 declared — flown is the population, declared the bound — [79](../decisions/79-shipset-descs-and-home-system-names.md) |
| `check_home_system_body_names` | two bodies in one `usage = custom_empire` initializer carrying the same name | one reported duplicate turned out to be **seven, in six systems, from three causes** — a `sub_blocks` that matched at every depth, a de-collision rule blind to the bare `star` keyword, and STNH naming both moons of S'latas alike. Scope is a calibration: vanilla fails this **62 times in 357** overall and **0 times in 9** home systems — [79](../decisions/79-shipset-descs-and-home-system-names.md) |
| `check_prescripted_initializers` | home-system initializers a prescripted empire names | [23](../decisions/23-real-home-systems.md) |
| `check_static_galaxy` | a static galaxy scenario's six joins: every `initializer` and `spawn_design` resolves; every country flag a `spawn_weight` tests is reachable, from `set_country_flag` **or** from `common/prescripted_flags/`; no two systems share an id or a position; hyperlane endpoints are declared and the graph is connected, and a static map declaring **no** lanes is an error; every `flag = empire_X` on a prescripted empire resolves to an entry carrying that empire's own key; and — since 2026-08-29 — **a system reserved for an `stg_` empire names an initializer that actually creates it**, `set_country_flag = <flag>` with `inline_script` includes expanded | every one of them fails silently, and STNH's 22 maps report **4,265** against their own tree — 4,256 systems naming one of 38 initializers nothing declares — while vanilla and Ariphaos are **0**. A static map with **no** lanes is an error, not a valid shape — it used to be waved through on the grounds that 21 of STNH's 22 define none, and that is how a 95-system galaxy holding one hyperlane reported clean every time; those 21 build their network in a start-of-game script STG does not vendor ([87](../decisions/87-static-map-lanes-are-generated.md)). A scenario leaving `random_hyperlanes` on stays exempt. One condition is scoped to `stg_*` keys because *"the flag is the design key"* is our convention and vanilla answers it 21 times in 51 without a defect — [86](../decisions/86-static-galaxy-scenario.md). **The sixth question is the one the other five could not ask.** They all ask whether a join RESOLVES, and the Federation's Sol resolved perfectly while creating nobody: the map pinned STG's headline empire to system `0` and no AI Federation existed in any galaxy where the player picked somebody else. Population **21**, floor **0**, and calibrated on **three** controls rather than on its own defect — removing the fragment, misspelling the Klingon flag, truncating the Romulan one. The Klingon control is why the condition is a `\b`-terminated regex and not `in`: `stg_klingon_empire` is a prefix of `stg_klingon_empire_TYPO`, so the first draft called a misspelt flag a match and reported clean. Bodies are read **`BUILD` first** because Real Space shadows vanilla's `sol_initializers.txt` at the same path — vanilla's copy creates nobody either, so reading it would report the defect for the wrong reason and keep reporting it after the fix — [107](../decisions/107-the-ai-federation.md) |
| `check_galaxy_size_references` | a `galaxy_size = <name>` naming a setup scenario nothing in `map/setup_scenarios/` declares, resolved with our copy of a path **shadowing** vanilla's rather than sorting against it | `galaxy_size` is a trigger that resolves a `setup_scenario` **by its name**, which is what [88](../decisions/88-lock-the-galaxy-picker.md) said nothing did — so withdrawing a scenario by occupying its path and declaring nothing dangles every reference to it, silently. Vanilla's floor **0 of 113**, necessarily, since it declares all five sizes it references; the merged tree is **113 of 113** and all five are acked under `galaxy_size_ack` as the picker lock's price. The cost is behavioural: each five-way size ladder collapses to its base, `ai_habitat_cap` to **0**. The control is emptying the ack, which reports all 113 and names the same ladder the engine did — [98](../decisions/98-withdrawn-scenarios-are-referenced-by-name.md) |
| `check_prescripted_portraits` | portrait sets and groups an empire names | |
| `check_name_lists` | name-list tokens with no loc key | every name token is a loc key — 603 of them, not the 218 first scored |
| `check_species_class_loc` | species classes missing the loc family the engine derives from the class key, **or carrying it under an `STG_` prefix it never looks up** | a raw three-letter key on screen, nothing in `error.log` — [19](../decisions/19-species-class-localisation.md) |
| `check_music_declarations` | a music track no `music = { }` names, a declaration naming no file, **and a playlist entry with no loc key** | the Federation anthem unheard through every run — [52](../decisions/52-federation-anthem.md); 16 of the playlist's 22 entries listed as `newhorizonssong1`, as measured in 2026-08-08's [58](../decisions/58-music-player-track-names.md) — **both halves of that figure have since moved**, and the rotation is now 27 entries with every one keyed ([62](../decisions/62-music-rotation-dedupe.md)) |
| `check_anomalies` | the four files an anomaly needs to agree on: the outcome event a category names, the sprite its picture names, and the six loc keys behind the log entry, the popup and the buttons — **and whether a positive `spawn_chance` or a script that names it can ever put the category in front of a player** | an anomaly is complete or it is a blank popup, and neither state dangles — [70](../decisions/70-trek-anomalies.md); `spawn_chance` defaults to `base = 0`, so 49 of vanilla's 327 have none and 3 are reachable by nothing at all — [74](../decisions/74-reachability-checks.md) |
| `check_archaeology` | the five files a dig site needs to agree on: the stage events and rune icons it names, its picture, the modifier its finale awards, the loc behind all of it — **whether `stages = N` matches the `stage` blocks beside it**, and **whether a positive `weight` or a script that names it can ever place the site** | a hand-written integer that nothing enforces and that makes the dig unfinishable when it is wrong; vanilla is 0 for 123 — [71](../decisions/71-trek-archaeology.md). And decision 71's own headline claim, which had no check behind it: 74 of vanilla's 123 sites carry no positive weight and **0** are reachable by nothing at all — [74](../decisions/74-reachability-checks.md) |
| `check_story_events` | the four files a story event needs to agree on: the event a hook names, its picture, its loc — **and whether the on_action KEY itself is one the engine declares or a `fire_on_action` reaches** | a hook nothing fires is a file that parses, art that loads and content that never once runs; decision 71's `weight = 0` in a seventh database — [72](../decisions/72-trek-story-events.md) |

`check_texture_basenames` matches on the **stem**, not the filename: the engine
resolves the extension itself and vanilla relies on it — its own
`_other_meshes.gfx` asks for `.tga` files it ships only as `.dds`. That is all
five of vanilla's `.tga` references, so an extension-sensitive check would report
vanilla itself ([rule 4](check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand)).

### The written form can be part of the name

`class = "star"` is **not** `class = star`. `star` is an engine keyword, and
quoted it stops being one, so the body is never created. Three separate checks
made the quotes optional in a regex and were blind to 23 missing stars across 20
home systems while reporting clean. [Decision 25](../decisions/25-quoted-class-keyword.md).

The converse is a separate trap that looks identical in a regex: STNH writes
`is_species_class = "HOLO"` quoted, and three checks reading that field with a
bare-only `(\w+)` were blind to it.
[Decision 30](../decisions/30-declare-stub-species-classes.md).

**Ask whether a field's written form changes its meaning before normalising it.**

---

## C. Two sources, one key

Harvest order does not reach this case: both files ship, and the engine picks by
**filename sort within the directory** — first for the fourteen FIOS
directories, last for everything else.
[Decision 27](../decisions/27-merge-semantics-per-directory.md).

| Check | Asks | Note |
|---|---|---|
| `check_key_conflicts` | any `common/` database key claimed by two mod families, or redefined smaller than vanilla's | names the file that **wins** |
| `check_defines_conflicts` | `common/defines/` keys set by two sources **to different values**; length-coupled arrays that disagree; an array coupled to an engine-internal one **no script can set** | matching the scriptable pair is necessary and not sufficient — saying `ok` on that basis hid a live error for five days, [41](../decisions/41-planet-scale-system-length.md) |
| `check_loc_key_conflicts` | a **localisation** key two sources declare with values that **disagree** | the fourth quadrant of the contested-key hole, and the one nothing could reach: `check_key_conflicts` asks its question of `key = { … }` blocks and **a localisation file has no blocks**, so widening it was never a matter of adding a directory. `error.log` records a key that is *missing* and nothing at all about one two files declare — both resolve, the engine keeps one, and that is [45](../decisions/45-minor-power-names-truncated.md)'s 78-of-79 `of Earth` defect exactly. Raw population **41 contested keys of 27,742, 8 of them differing**, and all 8 are Planetary Diversity overriding its own placeholders through its own extensions — `Placeholder Origin - DO NOT USE` losing to `Megaflora Tree of Life` — every one resolving to the extension under filename sort, which is [27](../decisions/27-merge-semantics-per-directory.md)'s "extension wins". So `vendor.yml`'s `key_conflict_families` empties this check as it empties its sibling, and the parser is now `_key_conflict_families()` shared by both rather than copied. **LIOS always** — localisation has no FIOS directory, so the winner is the last filename in sort order with none of the sibling's directory table behind it. A same-value duplicate is **not** reported here although [92](../decisions/92-src-contests-its-own-loc-keys.md) reports one in `src/`: a duplicate of ours is a file to delete, a source's is not ours to tidy ([11](../decisions/11-fix-source-errors-dont-drop.md)). Floors vanilla **148,053 keys in 231 files contesting none** and the merged tree **0 across families**; four controls, and the first injection picked two sources of one family, was correctly filtered, and read as *the check cannot fire* — **a control that does not know what the check filters is not a control** — [109](../decisions/109-two-sources-one-loc-key.md) |
| `check_order_sensitive_databases` | an order-sensitive database fed by more than one source | [53](../decisions/53-starbase-modules-order.md) |
| `check_duplicate_entities` | one entity name declared by two files with **bodies that differ** | vanilla names 8,409 entities and never repeats one — [31](../decisions/31-duplicate-entity-declarations.md), triaged in [50](../decisions/50-duplicate-entity-triage.md) |
| `check_duplicate_textures` | one texture **basename** carried by two folders with different content | a `.mesh` names its textures by bare filename *inside the binary*, so the engine keeps one globally: vanilla repeats 1 basename in 7,711, the built tree repeated 142 — [44](../decisions/44-coalition-of-hope-takes-vul.md), [51](../decisions/51-federation-texture-collisions.md) |

> **Both conflict checks compare *content*, not just names.** Two sources
> claiming one key with bodies that differ only in whitespace, or setting one
> define to the same value, are not in conflict and are not reported.
> **Prefer that to an ack** — an ack stays silent forever; a content comparison
> starts firing again by itself the day the two bodies diverge. Two
> `defines_conflict_ack` entries were deleted on those grounds rather than kept.

`renames:` in `vendor.yml` is the **only** lever that changes who wins.

---

## D. A shadow that drops declarations

A file at a path something else also ships replaces it whole — including the
declarations it happened not to copy.

| Check | Asks |
|---|---|
| `check_vanilla_regression` | vendored art **or script** that shadows a vanilla path while dropping declarations vanilla still references |
| `check_src_source_regression` | an `src/` override that drops declarations the **source** it shadows makes |

`check_vanilla_regression` scopes to **every** source since 2026-08-07, not just
the stale and additive-only ones: a current mod may replace a vanilla database on
purpose and still strand a **third** mod that calls the old keys
([36](../decisions/36-real-space-drops-sol-neighbours.md)). `flags/colors.txt`
cost 47 of vanilla's 72 flag colours this way
([07](../decisions/07-stnh-art-shadows-vanilla.md)).

`check_src_source_regression` exists because `src/` beats the sources too, not
only vanilla: `src/gfx/FX/pdxmesh.shader` was written as "vanilla 4.4 plus STNH's
five effects" and dropped all 41 Real Space appends to the same path
([32](../decisions/32-src-shadows-drop-source-declarations.md)).

---

## E. It resolves, and it is still wrong

The subtlest family. Nothing dangles; the defect is in the *value*, the
*geometry* or the *position*.

| Check | Asks | Written for |
|---|---|---|
| `check_shadowed_texture_geometry` | vendored art that shadows a vanilla **texture** path at different pixel dimensions — and art that shadows *no* vanilla path but breaks the family vanilla is uniform about | STNH's 620×264 event pictures drawn at 930×396 inside UIOD's 693×239 frame through two live runs of `ok` — [40](../decisions/40-event-picture-geometry.md); city layers on a canvas exactly 70% of vanilla's, drawing every planet's buildings low and small — [55](../decisions/55-city-set-geometry.md), [60](../decisions/60-city-set-family-targets.md), [63](../decisions/63-city-set-canvas-overflow.md); and `gfx/event_pictures` read as one 90.8%-uniform family when it is two 100% ones, which left the 865 pictures that shadow nothing unasked — [69](../decisions/69-event-picture-families.md) |
| `check_prescripted_loc` | prescripted loc converted from a source that no longer says what the source says: a value that is still a loc **key**, or a name **truncated** to a substring | 78 of 79 minor powers shipped as `of Earth`, `-Aurian Auditorium`, `'Q Stagnancy` — nothing in `error.log` ever, because **loc that resolves to the wrong string still resolves** — [45](../decisions/45-minor-power-names-truncated.md). Two scopes on purpose: [49](../decisions/49-prescripted-loc-scope.md) |
| `check_prescripted_empires` | traits, ethics or portraits that break a rule vanilla's own databases declare; a civic **granting** a species trait no species block carries; and, since 2026-08-26, three rules about whether a civic or trait is *available at all* — a civic `playable` only when a DLC is **absent**, a civic whose `possible` gates `species_class` to a positive vanilla list, and a trait vanilla declares `species_possible_add = { always = no }` | reported once per trait name, so six broken empires read as three log lines — [39](../decisions/39-civic-granted-species-traits.md). The three availability rules come from five empires hidden from the designer, two of which printed **no reason at all**; sweeping each rule found exactly those five — [83](../decisions/83-design-database-is-not-the-cause.md). See [prescripted empire rules](../reference/prescripted-empire-rules.md) |
| `check_prescripted_appearance` | ruler `texture` / `clothes` indices that are off the end of the list | `texture = 1` was off the end on **74** of 101 — [21](../decisions/21-prescripted-ruler-appearance.md), [54](../decisions/54-prescripted-rulers-unpin-clothes.md), [65](../decisions/65-ruler-clothes-dedicated-selectors.md) |
| `check_portrait_clothes_selectors` | selector rows with no species gate, and the scopes the game actually reads | four female master-selector rows with no gate put every ungated non-Federation female commander in Vulcan clothes — [61](../decisions/61-terran-empire-mirror-uniforms.md), [20](../decisions/20-empire-designer-clothes.md) |
| `check_asset_load_order` | a `locator` declared beside a `clone`, and `clone` resolution order | `clone` resolves against entities **already loaded**, walking `gfx/models/ships/` as one alphabetical sequence — "declared somewhere" said yes 982 times while the Vulcan and Tholian shipsets did not render at all — [28](../decisions/28-clone-discards-sibling-locators.md) |
| `check_section_attach_points` | a hull entity missing the `part1`..`partN` attach points its ship size's `section_slots` names — **two scopes**: the station family, and (since 2026-08-22) every other size, gated on the frame being *borrowed* | all 22 Walshicus shipsets declared only `root`, so station sections had nowhere to attach — [33](../decisions/33-station-section-attach-points.md). The same defect on the *warship* hulls is [77](../decisions/77-hull-section-attach-points.md), fixed in `tools/fix_ship_locators.py` and **now guarded** by the second scope — [78](../decisions/78-widen-attach-points-and-two-new-checks.md) |
| `check_build_script_syntax` | every script file in **stg-build/** balances its braces and closes its strings — the same scanner `check_script` has always run over `src/`, pointed at the other tree | nothing had ever asked. `check_script` walks 340 files of ours; the build's parseable surface is **3,934** of the 22,395 files the tree held that day, the rest being art, and it was entirely unchecked — and it is the half that matters more, being 49 mods merged, patched, resampled and pruned. **A missing brace does not fail loudly**: the parser swallows the rest of the file, so everything below it is silently absent with no log record. Floor **0 of 3,934**, measured; vanilla fails its own parser **3** times and the build ships none of the three, which is why this reports rather than errors — [102](../decisions/102-syntax-checking-stopped-at-src.md) |
| `check_script_variables` | a `common/` file reading an `@variable` neither it nor `common/scripted_variables/` declares | the class ASB and SBX both shipped, only ever found by reading a log. An unresolved `@` does not keep its name — **the field gets nothing** — which is `vendor.yml`'s `nsc_starbases` patch exactly: two `@` names, and the two ship sizes that file exists to declare came up with no build-block radius and no formation priority. **Scope is both halves and a first cut got it wrong**: treating `@` as file-local (which that patch's own note says) reported **592 vanilla files**, 29% of `common/`, measuring the model rather than the tree; `scripted_variables/` is global *on top of* file-local, which drops vanilla to 25. **24 of those 25 are `@name$PARAM$` inline-script concatenations**, not references — check-design rule 8 again, the written form is part of the name — and a `$` after the match is the tell. Vanilla's true floor **1**, ours **1** before the patch and 0 after — [102](../decisions/102-syntax-checking-stopped-at-src.md) |
| `check_slot_table_widening` | a **vendored ship size** whose `section_slots` names an attach point vanilla's own table for the same size does not | the cause-side of `check_section_attach_points` and it needs no mesh: vanilla's table is the only guarantee of what every culture's art carries, because vanilla ships art for all of them and never names a point its art lacks. Starbase Extended gives the starport, starhold, starfortress and citadel **one** 36-slot table and all three orbital ring tiers another, each sized for the largest member — so `starbase_starport` reached `part7` against art that stops at `part3`, and **72 entities** across every graphical culture lost their modules. The entity check could not have caught it twice over: the starbase family is outside both its scopes, and **40 of the 72 are declared by vanilla alone**, which it skips by design — the art is innocent here and the table was ours. Population **six sizes**, floor **0**, reverting the four `vendor.yml` patches reports **4**; SBX's genuinely new `starbase_stronghold` and `starbase_headquarters` have no vanilla table to compare against and are exempt rather than acked — [100](../decisions/100-starbase-slot-tables-outrun-the-art.md) |
| weapon-mount positions (in `check_asset_load_order`) | a weapon mount with no position anywhere | it fires from the middle of the ship — [26](../decisions/26-weapon-locator-positions.md), [57](../decisions/57-mounts-share-existing-points.md), [64](../decisions/64-source-art-hardpoint-names.md) |
| `check_colony_name_collisions` | a `planet_names` pool offering a name some empire's **capital** uses, its **own** capital, or — since 2026-08-28 — any other **body of its own empire's home system** | the first two are [23](../decisions/23-real-home-systems.md). The third is [95](../decisions/95-colony-pools-drop-home-system-bodies.md): a Klingon colony called Praxis while the real Praxis orbits Qo'noS. Scope is `usage = custom_empire`, joined through `prescripted_countries`, and it is a calibration result — vanilla **0 of 8** comparable empires (its UNE is 18 Sol bodies against `HUMAN1`'s 59-name pool with **no** overlap), STNH **0 of 10**, four of which sit on a 32-body Sol with a 160-name pool. STNH shows the convention as well as the floor: home-system bodies go in `ship_names`, and its only Mars in a colony pool is `TERRAN_PLANET_NewMars`. **Resolution is through localisation on both sides and over `*l_english.yml` alone** — the build-only map missed the Terran Mars (Sol's body is vanilla's `NAME_Mars`, the pool offers `STG_N_Mars`) and a `*.yml` map let Portuguese win the key and resolve it to *Marte*. Both drafts under-reported; only reverting the repair caught them, at which point it names all 17 |
| `check_anomaly_targets` | an `add_anomaly` whose `target` names a property of the planet it is standing on rather than a scope — the allowlist read out of vanilla at run time | `add_anomaly` runs on a body nobody has claimed, so `target = owner` resolves to nothing and the anomaly is silently not added. Scoped to this one effect on purpose: a bare `target = owner` is ordinary elsewhere and **vanilla writes 8 of them**, over 3,067 `target =` sites in 124 effect kinds — it is `add_anomaly` alone that guarantees an unowned scope, and vanilla's own 29 are 14 `root`, 8 `solar_system`, 6 `prev`, 1 `prevprev` and no bare property. Vanilla's floor **0 of 29**; calibrated by reverting the repair, and it names the same line the engine did — [90](../decisions/90-add-anomaly-target-scope.md) |
| `check_section_slot_references` | a ship design mounting on a **slot name** the section template that wins the key no longer offers; a design naming a section nothing declares; and — since 2026-08-28 — a **starbase module** naming one, which is the same database reached from a directory the check did not walk | the swept rule behind [37](../decisions/37-sbx-citadel-slot-renumbering.md), whose four `ship_growth_stage.cpp` records were one instance from one screen somebody opened. Asked of the **merge**, FIOS in both databases: vanilla owns all 412 designs, SBX owns the only `common/section_templates` file the build ships, and the defect is what the two make together. Vanilla's floor **0 and 0** over 6,882 component references and the merged tree matches it; the control is decision 37's patch reverted, which reports exactly the four `MEDIUM_GUN_010..013` the live log named, and an injected slot-less replacement reports 16. **The module direction is a separate floor and a separate control**: vanilla **0 of 96** bare `section = "KEY"` references, the merged tree **0 of 123** once patched, and reverting the patch recovers the two `ship_design_templates.cpp:480` records — `SHIELD_` and `ARMOR_ORBITAL_RING_SECTION` — that sat in every log on disk unnamed ([99](../decisions/99-starbase-modules-name-sections-too.md)). **Reads both written forms of a slot** — named `component_slot` mounts and the utility banks a `large_utility_slots = 6` count expands to — because 14 of those 16 are utility slots — [96](../decisions/96-section-slots-survive-a-replacement.md) |
| `check_src_key_contention` | two files **we** wrote declaring one identifier, in a database vanilla never contests — the database gate read out of vanilla at run time | `check_key_conflicts` gates on two **sources**, so a key `src/` contests with itself can never satisfy it: it was counting `common/name_lists` among its 506 files and structurally unable to report the three keys in it. Scope is a calibration result — build-wide **16** keys are contested by one source, **13** of them a source mod's own design (PD's `zzz_` overrides, `inline_scripts` fragments) and 3 ours. Vanilla's floor in `common/name_lists` is **0 across 80 keys in 76 files** (published as 78 until [96](../decisions/96-section-slots-survive-a-replacement.md) fixed a column-0 anchor that could not see the two indented lithoid lists), and 0 in 14 of the 16 databases `src/` writes into — [91](../decisions/91-src-contests-its-own-name-lists.md) |
| `check_src_loc_key_contention` | two localisation files **we** wrote declaring one key, or one file declaring it twice — the language gate read out of vanilla at run time | the same hole as `check_src_key_contention` one directory over, and neither existing check could reach it: `check_key_conflicts` walks `common/` only, and `check_localisation` reads each file alone. **Six keys were contested and one disagreed with itself** — the Breen home system's third body asked for `STG_N_Portas` "Portas" (a colonizer ship) while the home-systems loc file redeclared that key as "Portas V", so one of the two rendered wrong and filename sort decided which. A same-value duplicate is reported too, because five harmless twins are why nobody looked at the sixth. Vanilla's floor is **0 across 148,053 keys in 231 english files**, and 0 keys repeated inside a file; build-wide the 16 one-source duplicates are 10 Real Space's own base/replace pair (0 differing) and our 6 — [92](../decisions/92-src-contests-its-own-loc-keys.md) |
| `check_src_identity_contention` | two files **we** wrote declaring one identity, or one file declaring it twice, anywhere in `src/` **outside** `common/` and `localisation/` — the database gate read out of vanilla at run time | the third and last quadrant of the hole [91](../decisions/91-src-contests-its-own-name-lists.md) and [92](../decisions/92-src-contests-its-own-loc-keys.md) opened: the two sibling checks walk one directory each, and `check_duplicate_entities` walks `*.asset` only, so **384 declarations of ours across 11 directories** had never been asked. **Identity is not the block key in two of the three forms** — in `events/` it is the `id` inside a depth-0 `*_event` block (counting every `id =` conflates declaring an event with firing one, and reports 33 vanilla collisions that are all references); in a `.gfx` it is the `name` of each direct child of the container, read at that child's own depth and in **both** written forms (an anchored regex found 0 of `stg_paragon_backgrounds.gfx`'s 28 one-line sprites). Five databases pass the gate and five exclude themselves because vanilla contests them — `interface` on per-charset fonts, `music` on `song`, `map/setup_scenarios` on `setup_scenario`. Vanilla's floor **0 across 11,857 identities**; ours **0 of 193**. Calibrated twice: the same code reports **6** on the built tree, all a source overriding itself, and 2 on an injected duplicate — [94](../decisions/94-src-contests-its-own-identities.md) |
| `check_home_planet_generation` | a home planet that will not generate as the empire declares it | |

---

## F. The dual — a file nothing references

`check_unreferenced` asks the **reverse** of every question above: not *does this
name resolve*, but *does anything name this file?*

813 STNH event pictures no `spriteType` declares sat in the tree because nothing
had ever asked that direction. [Decision 43](../decisions/43-clutter-pass.md),
and [the clutter closure](clutter.md) for how it decides and why its scope is
narrow.

**This is the one check that deletes**, which changes everything about how it is
calibrated — see [check design, rule 1](check-design.md#1-a-check-that-deletes-is-not-a-check-that-reports).
