# Decisions — index

> **What** — every resolved decision, grouped by subject, one line each.
> Count them with `ls .docs/decisions/[0-9]*.md | wc -l`; `make docs` checks the
> set against this index.
> **Open when** — before reopening a settled question, or when a citation names a
> decision by number and you need to know what it says.
> **Then** — [Style guide §7](../style-guide.md#7-decision-files-have-a-fixed-head) for the file format · [Documentation map](../README.md)

**Read the decision before reopening its question.** Each file records what was
decided, why, and what it cost — usually a live run. Several were falsified by a
later run and kept anyway, because the pair is worth more than either alone.

> **Renumbered 2026-08-27.** Seven decisions that had been wholly superseded or
> falsified were removed, and the remaining 88 renumbered to run 01–88 with no
> gaps. Every citation in `.docs/`, `tools/`, `src/` and `vendor.yml` was
> rewritten to match, and every reference to a removed decision was replaced by a
> statement of what it had said, so no note lost its meaning. **Numbers used
> before that date do not map onto this index** — read a stale citation by its
> slug, not its number. The seven removed: no source-mod archive (superseded by
> [08](08-source-snapshot.md)); STNH's minor powers as AI-only empires; Trek star
> names from STNH's maps; `clothes = N` as a file-order index (superseded by
> [65](65-ruler-clothes-dedicated-selectors.md)); the Vulcan city needing no
> reframe (falsified by [81](81-city-horizon-band.md)); the prescripted pool's 5%
> spawn chance; and `playable` gating the design database.

**The number is the address**, and several hundred
citations in `tools/`, `src/` and `vendor.yml` point at
`.docs/decisions/NN-slug.md` — count them with the one-liner in
[style guide §3](../style-guide.md#3-folders-are-categories-and-every-folder-has-a-readme),
which is also where the rule lives: category is in this index, not in the path.

> **Decisions written before 2026-08-08 cite `plan.md §N` and `CLAUDE.md`.** Both
> were split on that date. Their **bodies are left exactly as written** — a
> decision records what was true when it was made, and rewriting one to match a
> later filesystem is how a record stops being one. Read those citations through
> this table:
>
> | Old citation | Now |
> |---|---|
> | `plan.md §1` | [planning/scope.md](../planning/scope.md) |
> | `plan.md §2` | [architecture/vendored-merge.md](../architecture/vendored-merge.md) |
> | `plan.md §3` | [architecture/harvest-order.md](../architecture/harvest-order.md) and [stnh-art.md](../architecture/stnh-art.md) |
> | `plan.md §4` | [architecture/conflict-register.md](../architecture/conflict-register.md) |
> | `plan.md §5` | [reference/repo-layout.md](../reference/repo-layout.md) |
> | `plan.md §6` | [planning/phases.md](../planning/phases.md) |
> | `plan.md §7` | [guides/working-rules.md](../guides/working-rules.md) |
> | `plan.md §8` | [planning/open-questions.md](../planning/open-questions.md) |
> | `plan.md`, "where things stand" | [planning/status.md](../planning/status.md) |
> | `CLAUDE.md`, a rule about checks | [validation/check-design.md](../validation/check-design.md) |
> | `CLAUDE.md`, a rule about acks | [validation/acks.md](../validation/acks.md) |
> | `CLAUDE.md`, the prefix / comment rules | [guides/writing-script.md](../guides/writing-script.md) |
> | `CLAUDE.md`, the `error.log` procedure | [guides/live-runs.md](../guides/live-runs.md) |
>
> Citations in **live** code — `tools/`, `src/`, `vendor.yml` — were rewritten to
> the new paths, because those are pointers a reader follows now rather than a
> record of what was believed then.

---

## Project shape and scope

| | |
|---|---|
| [01](01-standalone-vendored-mod.md) | Standalone, self-contained mod — no load order to lean on |
| [02](02-drop-ariphaos.md) | Drop the Ariphaos Unofficial Patch — 4.2.4 against our 4.4 |
| [03](03-content-scope.md) | Content scope: era, art, empires, map |
| [04](04-harvest-order.md) | Harvest order corrections |
| [10](10-drop-cinematic-camera-and-ambient-soundtracks.md) | Drop Cinematic Camera, Kammarheit and Apocryphos — *Cinematic Camera restored by [41](41-planet-scale-system-length.md)* |
| [11](11-fix-source-errors-dont-drop.md) | **Fix a source mod's errors; never drop the mod to silence them** |
| [75](75-mem-integration-deferred.md) | More Events Mod is in scope and waits — it writes the databases Phase 4 just wrote by hand, and eyes cannot attribute what they cannot separate |

## The pipeline

| | |
|---|---|
| [08](08-source-snapshot.md) | The build reads `.source/`, not `/workshop` |
| [12](12-build-dir-and-symlink-deploy.md) | The mod tree moves to `stg-build/`, and the deploy is a symlink |
| [27](27-merge-semantics-per-directory.md) | Which file wins is a property of the **directory** — the FIOS/LIOS table |
| [43](43-clutter-pass.md) | Unreferenced content goes by default, and the closure decides |

## Deployment and runtime

| | |
|---|---|
| [06](06-launcher-local-mod-registration.md) | The launcher does not scan `mod/` — registry, playset and files are three systems |
| [14](14-native-linux-runtime.md) | Compatibility mode off: native Linux build, and the user-data folder moved back |

## Merges, shadows and duplicates

| | |
|---|---|
| [05](05-gui-merges-unnecessary.md) | The two `interface/*.gui` merges are unnecessary |
| [07](07-stnh-art-shadows-vanilla.md) | STNH's art shadows vanilla, and its art **is** script |
| [22](22-group-c-texture-references.md) | Group C is a texture problem, and the include list could not see it |
| [31](31-duplicate-entity-declarations.md) | One entity name declared twice silently decides which art renders |
| [32](32-src-shadows-drop-source-declarations.md) | An `src/` override shadows the *sources* too, not just vanilla |
| [35](35-attach-edges-into-pruned-art.md) | `attach` edges into pruned STNH art — kept, not integrated |
| [36](36-real-space-drops-sol-neighbours.md) | Real Space drops ten Sol-neighbour initializers PD still calls |
| [37](37-sbx-citadel-slot-renumbering.md) | SBX renumbers vanilla's citadel gun slots and vanilla's own design breaks |
| [44](44-coalition-of-hope-takes-vul.md) | Three findings from the 08-07 fourth run, and the two checks they bought |
| [50](50-duplicate-entity-triage.md) | The 13 duplicate entity declarations, triaged — and the suppression that swallowed a real one |
| [51](51-federation-texture-collisions.md) | The `federation/` vs `starfleet_tng/` texture pairs are the same artwork |
| [53](53-starbase-modules-order.md) | `common/starbase_modules` fed by two sources: looked at, acked |

## Empires, species and names

| | |
|---|---|
| [09](09-species-class-keys-unprefixed.md) | The five species classes take STNH's bare keys, not `STG_` |
| [13](13-remove-vanilla-prescripted-empires.md) | Remove vanilla's prescripted empires; pin `supported_version` exactly |
| [18](18-minor-power-species-class-keys.md) | Eight minor powers take STNH's species-class key, not a near miss |
| [19](19-species-class-localisation.md) | Species class loc keys hang off the class key, **unprefixed** |
| [21](21-prescripted-ruler-appearance.md) | Prescripted rulers pin no appearance index |
| [23](23-real-home-systems.md) | Real home systems, and why the original plan was wrong about them |
| [24](24-home-system-classes.md) | STNH identifiers in generated home systems — a crash that logs nothing |
| [39](39-civic-granted-species-traits.md) | Six Trek empires took a civic without the trait it grants |
| [42](42-random-names-pools-append.md) | `common/random_names/` pools append — *arithmetic corrected 2026-08-08 by the Trek star-name harvest, which found YAGEM's two missing files* |
| [45](45-minor-power-names-truncated.md) | 78 of 79 minor-power names shipped truncated, 16 loc keys shipped as text |
| [49](49-prescripted-loc-scope.md) | The other three prescripted-power files are clean; the check keeps two scopes |
| [56](56-ship-name-pools.md) | STNH's ship registries, folded onto vanilla's ship sizes |
| [67](67-ship-class-names.md) | STNH declares its own class names, so 56's fuzzy join was never needed |
| [68](68-class-name-thematic-fill.md) | A class-name pool is one semantic field, and vanilla is the model for filling one |
| [76](76-random-names-are-loc-keys.md) | A quoted random name is a localisation key, and STG shipped 330 with no key — *falsifies the star-name harvest's "these are literals" reasoning; its `token()` rule stands* |
| [82](82-remove-mirror-timeline-duplicates.md) | The Republic of Hope and the Klingon-Cardassian Alliance are removed: two 2300s empires holding a second 40 Eridani and a second Qo'noS — *closes [44](44-coalition-of-hope-takes-vul.md)'s subject* |
| [83](83-design-database-is-not-the-cause.md) | The 99 designs *are* loaded and still nothing draws them, five empires were hidden by two vanilla gates, and the initializer theory cannot explain 62 of them — *confirms that removing the `playable = stg_never` gate worked, closes the database half of the question, corrects [external-sources.md](../reference/external-sources.md) on `randomized`* |
| [84](84-static-galaxy-is-the-mechanism.md) | STNH gets its Trek galaxy from static maps, not from the spawn lottery, and STG ships no map at all — *corrects [83](83-design-database-is-not-the-cause.md)'s STNH reading, reframes `CUSTOM_EMPIRE_SPAWN_CHANCE` as the wrong mechanism* |
| [85](85-create-country-initializers.md) | AI Trek empires are created by their home system's initializer, not drawn from the prescripted pool — *supersedes the direction of both earlier fixes — the spawn-chance define and the `playable` gate; plan in [static-galaxy-plan.md](../planning/static-galaxy-plan.md)* |
| [86](86-static-galaxy-scenario.md) | The country flag is what joins a static map to an empire, and `prescripted_flags` is the half nobody had written — *completes [85](85-create-country-initializers.md); ships the map, the AI copies and `check_static_galaxy`; leaves the picker lock and the AI Federation open* |
| [87](87-static-map-lanes-are-generated.md) | STNH builds its lane network in script, not in the map, and copying the empty map shipped a galaxy with one hyperlane in it — *answers [86](86-static-galaxy-scenario.md)'s question 2 and confirms [84](84-static-galaxy-is-the-mechanism.md), [85](85-create-country-initializers.md) and [86](86-static-galaxy-scenario.md) from a live save; inverts `check_static_galaxy`* |
| [88](88-lock-the-galaxy-picker.md) | The picker offers one galaxy, and withdrawing a scenario means occupying its path and declaring nothing — *completes [static-galaxy-plan.md](../planning/static-galaxy-plan.md)'s piece 3; excludes twelve YAGEM maps, masks vanilla's five, and makes STG's map the default* |

## Ship art and weapon mounts

| | |
|---|---|
| [16](16-stnh-shipsets-on-a-vanilla-chassis.md) | STNH shipsets on a vanilla chassis — *narrowed by [17](17-walshicus-shipsets-replace-stnh-hulls.md)* |
| [17](17-walshicus-shipsets-replace-stnh-hulls.md) | Walshicus' shipsets replace STNH's hulls for nine of fourteen cultures |
| [26](26-weapon-locator-positions.md) | Weapon locators: `.asset` declarations do count, and they need positions |
| [28](28-clone-discards-sibling-locators.md) | `clone` discards every locator declared beside it |
| [29](29-asset-local-variables.md) | `@variables` in art files are file-local, and copying an entity leaves them behind |
| [33](33-station-section-attach-points.md) | Walshicus' station hulls carry no section attach points |
| [57](57-mounts-share-existing-points.md) | A missing mount shares a point the artist drew |
| [64](64-source-art-hardpoint-names.md) | The artist's vocabulary is not the game's |
| [77](77-hull-section-attach-points.md) | Every Trek hull above corvette borrows a corvette's frame, and its sections hang on points a corvette does not have — *[33](33-station-section-attach-points.md) one entity family over* |

## Portraits, clothes, rooms, city sets and flags

| | |
|---|---|
| [15](15-phase-3-clothing-triggers.md) | Real bodies for the 140 STNH clothing triggers |
| [20](20-empire-designer-clothes.md) | `game_setup` is a scope, and a shared selector has to gate it too |
| [30](30-declare-stub-species-classes.md) | Declare the 34 selector-named species classes; retire the ack |
| [40](40-event-picture-geometry.md) | Event pictures are re-cut to vanilla's dimensions at harvest |
| [46](46-room-selector-merge.md) | One `room_selector`, written by us — a database nothing could dangle on |
| [47](47-flags-city-sets.md) | The shipsets' 39 extra flags, 22 empires on a grey placeholder, the Trek city sets |
| [48](48-paragon-backgrounds.md) | Paragon leader backgrounds: declare our own rather than un-exclude STNH's |
| [54](54-prescripted-rulers-unpin-clothes.md) | A prescripted ruler pins no clothes index at all |
| [55](55-city-set-geometry.md) | STNH's city layers are a 560×280 canvas in an 800×400 planet view |
| [59](59-city-set-cultures-undeclared.md) | Five city sets with complete art and no declaration — the designer hid the empires |
| [60](60-city-set-family-targets.md) | Read the resample target off vanilla's **family**, not only the file |
| [61](61-terran-empire-mirror-uniforms.md) | The Terran Empire's mirror uniforms, and four female rows with no species gate |
| [63](63-city-set-canvas-overflow.md) | A file taller than the canvas was scaled by two different factors |
| [65](65-ruler-clothes-dedicated-selectors.md) | A shared master selector cannot be indexed; give the ruler its own — *supersedes the file-order index model a live run falsified at all six positions* |
| [69](69-event-picture-families.md) | `gfx/event_pictures` is two families, and reading it as one left 865 pictures unasked |

## Content — events, anomalies and archaeology

| | |
|---|---|
| [70](70-trek-anomalies.md) | Phase 4 starts with anomalies, because they are the one part of "a voice" with a yardstick |
| [71](71-trek-archaeology.md) | Trek archaeology, and the one field in the format that decides whether any of it is ever seen |
| [72](72-trek-story-events.md) | Trek story events, and the merge question the design refuses to ask |
| [73](73-phase-4-count-corrections.md) | Four numbers in Phase 4 were wrong, and the worst was another database's right number — *corrects [70](70-trek-anomalies.md) and [72](72-trek-story-events.md) in part* |
| [90](90-add-anomaly-target-scope.md) | `add_anomaly` runs on a planet nobody owns, so `target = owner` resolves to nothing — *fixes the one post-init record naming a shipped file since 2026-08-10, in a `vendor.yml` patch per [11](11-fix-source-errors-dont-drop.md); adds `check_anomaly_targets`, vanilla floor 0 of 29* |

## Audio

| | |
|---|---|
| [52](52-federation-anthem.md) | The Federation anthem plays, and a check that a track is reachable |
| [58](58-music-player-track-names.md) | The music player draws the declaration name, and 16 had no key |
| [62](62-music-rotation-dedupe.md) | The rotation is 27 tracks, not 86, and six of them were one recording |

## Checks, calibration, and things reviewed then left

| | |
|---|---|
| [25](25-quoted-class-keyword.md) | A quoted `class` keyword is a different keyword — 23 missing stars, 3 blind checks |
| [34](34-oversized-real-space-systems.md) | Real Space's oversized systems: leave them, they are its own warning |
| [38](38-live-run-2026-08-07-repairs.md) | The 2026-08-07 15:41 run's small defects, and what each one cost |
| [41](41-planet-scale-system-length.md) | `PLANET_SCALE_SYSTEM` is measured against an array no script can set |
| [66](66-doc-inventory-checks.md) | A doc citation can resolve perfectly and still describe a repo that moved |
| [74](74-reachability-checks.md) | A site with no `weight` and a category with no `spawn_chance` are complete, clean and unreachable — and the second half of the question is what makes the check worth having |
| [78](78-widen-attach-points-and-two-new-checks.md) | A stale ratio was guarding the hull family, the female selector was never swept, and no generator was ever a checked fixpoint — *widens [33](33-station-section-attach-points.md), guards [77](77-hull-section-attach-points.md)* |
| [79](79-shipset-descs-and-home-system-names.md) | Thirty shipset descriptions were keyed to the wrong database, six home systems named a body twice, and one finding falsified itself — *continues [78](78-widen-attach-points-and-two-new-checks.md), corrects [23](23-real-home-systems.md)'s generator, closes [59](59-city-set-cultures-undeclared.md) in the reverse direction* |
| [80](80-selector-textures-that-resolve.md) | The 196 was 117, two thirds of it was never a content call, and the thirteen that were took one policy rather than thirteen decisions — *completes [78](78-widen-attach-points-and-two-new-checks.md)'s second half* |
| [81](81-city-horizon-band.md) | Vulcan's skyline filled 325 of 400 rows against a family median of 289, and the fix is a resample, not a crop — *falsifies the 2026-08-08 review that left this art alone, supersedes [63](63-city-set-canvas-overflow.md)'s crop* |
| [89](89-retired-run-write-ups.md) | The five live-run write-ups are retired, and a retired document leaves a provenance label behind, not a link — *removes 2,408 lines and rewrites the 51 references they left, including 7 from live code; adds `check_link_labels` to `make docs`* |
| [97](97-bare-decision-numbers.md) | A third of every decision citation carries no path and no link, and three of them named the wrong decision — *the form `check_code_citations` and `check_link_labels` both miss: **519** bare numbers, all of which resolved and three of which pointed at the wrong decision after the 2026-08-27 renumbering. Adds `check_bare_decision_numbers` (floor **0 of 519**, and it reads wrapped lines because that is how one hid); records the `git blame` audit for the semantic half a check cannot do — completes [89](89-retired-run-write-ups.md)'s sweep* |
| [91](91-src-contests-its-own-name-lists.md) | Three name lists are declared twice by files we wrote, and the key-conflict check could never have seen it — *`check_key_conflicts` gates on two **sources**, so `src/` contesting itself is invisible to it; adds `check_src_key_contention`, vanilla floor 0 of **80** in `common/name_lists` (published as 78; corrected by [96](96-section-slots-survive-a-replacement.md)); corrects [27](27-merge-semantics-per-directory.md) on whether a name list's id is its filename; **which of each pair to keep is open***  |
| [92](92-src-contests-its-own-loc-keys.md) | Six localisation keys are declared twice by files we wrote, and the Breen home system was asking for the wrong one of two real names — *the same hole as [91](91-src-contests-its-own-name-lists.md) one directory over, which neither `check_key_conflicts` nor `check_localisation` could reach; adds `check_src_loc_key_contention`, vanilla floor **0 across 148,053 keys in 231 files**; corrects [23](23-real-home-systems.md)'s generator a fourth time* |
| [93](93-power-lists-win-the-contested-keys.md) | The hand-written power list wins all three contested name-list keys, and the converted duplicates are deleted — *completes [91](91-src-contests-its-own-name-lists.md)'s open content call; `src/common/name_lists/` is now 89 files declaring 89 keys, `make validate` is back to 0 warnings, and the Caitian `titan` gap [68](68-class-name-thematic-fill.md) recorded was never true of the file we ship* |
| [94](94-src-contests-its-own-identities.md) | The third quadrant of the contention hole is `src/` outside `common/` and `localisation/`, and it was clean — *asks [91](91-src-contests-its-own-name-lists.md)'s question a third time, in the 11 directories neither it, [92](92-src-contests-its-own-loc-keys.md) nor `check_duplicate_entities` could reach; adds `check_src_identity_contention`, vanilla floor **0 across 11,857 identities**, ours **0 of 193**. **No defect found** — the value is that the shape is now covered everywhere it can occur, and the check reports 6 on the built tree to prove it can fail* |
| [95](95-colony-pools-drop-home-system-bodies.md) | A colony pool must not offer a name its own empire's home system already carries, and 17 tokens did — *makes the content call the 2026-08-28 open-questions item left open, and corrects its count from 16 over 11 empires to **17 over 12**; the extra one is the Terran Empire's Mars, invisible to a key-wise comparison because Sol's body is vanilla's `NAME_Mars` and the pool offers `STG_N_Mars`. Widens `check_colony_name_collisions` to a third flavour — floors: vanilla **0 of 8** comparable empires, STNH **0 of 10** including four on a 32-body Sol with a 160-name pool. Two drafts of the check under-reported and only the calibration caught them* |
| [96](96-section-slots-survive-a-replacement.md) | A section replacement must keep every slot vanilla's own designs mount on, and the 23 duplicate-section records say nothing about whether it did — *generalises [37](37-sbx-citadel-slot-renumbering.md) from the one instance a live log named into the swept rule; triages the 23 `ship_design_templates.cpp:216` records no document had named. Adds `check_section_slot_references`, asked of the **merge** because vanilla owns all 412 designs and SBX owns the only section file we ship — floors **0 and 0** over 6,882 component references, and the control is decision 37 reverted, which recovers the same four slots the live log named. On the way: `_top_level_blocks` anchored its key at **column 0**, which lost six `ship_section_template` declarations vanilla indents and made [91](91-src-contests-its-own-name-lists.md)'s `common/name_lists` floor **80 keys, not 78*** |
| [98](98-withdrawn-scenarios-are-referenced-by-name.md) | A withdrawn setup scenario is still referenced by name, and the picker lock dangled 113 of vanilla's own triggers — *corrects [88](88-lock-the-galaxy-picker.md)'s one load-bearing sentence: the setup screen enumerates the directory, but `galaxy_size` is a **trigger that resolves a `setup_scenario` by name**. **353 records in the 2026-08-28 Klingon run against 0 in every log before the lock**, and the cost is behavioural — every five-way galaxy-size ladder in vanilla script collapses to its base, `ai_habitat_cap` to **0**. **The lock stands**: the call is made with the price measured rather than assumed. Adds `check_galaxy_size_references` (vanilla floor **0 of 113**, all 113 vanilla's own) and `galaxy_size_ack`, which the one-commit reversal empties* |
| [99](99-starbase-modules-name-sections-too.md) | A starbase module names a section template too, and two of SBX's name one that exists nowhere — *widens [96](96-section-slots-survive-a-replacement.md) into the reference direction it did not walk: a module writes a bare `section = "KEY"`, not a `section = { template = … }` block, and nothing had asked whether those resolve. Two `ship_design_templates.cpp:480` records in every log on disk, named by no document. **SBX's own defect, not a harvest loss** — grepping all of `.source/` finds the keys only in the referencing file. Repointed in `vendor.yml` at the one ring section no module claims; floors vanilla **0 of 96**, merged **0 of 123**, reverted **2**. The art is a guess and is eyes-only* |
| [100](100-starbase-slot-tables-outrun-the-art.md) | Starbase Extended sizes every tier's slot table off the largest tier, and the smaller ones name attach points no mesh carries — *the third family of [33](33-station-section-attach-points.md) and [77](77-hull-section-attach-points.md), and the first where the art is vanilla's and innocent. Four `pdx_entity.cpp:1217` records in the 2026-08-28 UFP run named one starport; the swept rule is **72 entities** — 16 starports, 16 starholds, 40 orbital rings — and **40 of them are declared by vanilla alone**, which the entity check skips by design. Four `vendor.yml` patches remap every over-reaching slot onto a point vanilla's own table names, decision [37](37-sbx-citadel-slot-renumbering.md)'s lever and SBX's own idiom. Adds `check_slot_table_widening`, which asks the question one level up and needs no mesh — population **six sizes**, floor **0**, reverted **4**. Found a precedence bug on the way: the old check read BUILD before vanilla and so read a table the game never uses for **19** sizes* |
| [101](101-first-contact-sounds-are-species-class-gated.md) | Every first contact in the game plays the aquatic sting, because vanilla picks the sound off a species class list STG replaced wholesale — *the same shape as [09](09-species-class-keys-unprefixed.md) and [19](19-species-class-localisation.md): the engine derives something from the class key and 129 unprefixed keys get nothing. Vanilla's `first_contact_event_sounds` gates thirteen sounds on `is_species_class` against its own thirteen classes; STG matches none, so the engine takes the first entry on the list and it is the AQUATIC one. **Ten records in the 2026-08-28 UFP run — every first contact in it.** Overridden by a generated `src/` file carrying vanilla's thirteen unchanged plus eleven of ours; the mapping is a made content call, **total across all 129 by construction**, and `tools/gen_first_contact_sounds.py` is the fourteenth generator. No triggerless catch-all: the engine picks *among* the options that pass, so one would compete rather than backstop* |
| [102](102-syntax-checking-stopped-at-src.md) | The brace checker only ever read `src/`, so nothing had asked whether the tree the game loads parses at all — *asked by the user after the UFP run: could a missing close have stopped the window firing? **We did not know.** `check_script` walked 340 files of ours; the build's parseable surface is **3,934** and was unchecked, and a missing brace makes the parser swallow the rest of the file with no log record. Swept: build **0 unbalanced**, vanilla **3**, none of them vendored — so the hypothesis was wrong AND the check that should have said so did not exist. A second class with it: `@variables` in `common/`, where a first cut treated `@` as file-local and reported **592 vanilla files**, measuring the model rather than the tree; the rule is `scripted_variables/` globally plus file-local, and 24 of vanilla's remaining 25 are `$PARAM$` concatenations. Floors **1 vanilla, 1 ours** — Sensor Expansion reaching for a companion mod's variable six times, patched out rather than given an invented number* |
| [103](103-setup-log-is-a-load-manifest.md) | `setup.log` is a load manifest, its one four-figure error class is the engine asking for loc no version of the game ships, and its trait dump is an external control we did not have — *11,922 lines nobody had opened, from the same run. 13 of 15 classes are dumps. The **1,605** `Missing ship size Localization Key` records are **321 ship sizes × exactly 5 suffixes**, 1,500 of them on sizes only vanilla declares — and vanilla defines the family for **no** size, its own `corvette_build_speed_mult` included. Closed: 0% ours, not a defect, and the 10 mod-only keys are left rather than made the only ones in the game. The **607** `Made X into opposite of Y` records are the engine's COMPUTED opposites graph, and against `check_prescripted_empires`' file-derived one they agree **607/607, zero either side** — the first external oracle any check here has had, where the calibration was previously only reverting our own repairs. Corrects 102's count of 1,375* |
| [104](104-script-documentation-is-a-version-exact-oracle.md) | The engine writes a version-exact, merge-aware script reference on every launch, and its modifier list is not the allowlist it looks like — *the user asked what `logs/script_documentation/` is. Five files the engine regenerates at the end of every load **from the merged database**: 1,056 effects, 1,087 triggers, 99 scope links, 47,510 modifier names, and the `[Scope.Property]` vocabulary — 568 modifier lines derived from our own `sr_acean`/`sr_eludium`, 757 job families including vendored `pd_` ones, against `Pegasus v4.4.6`. Already load-bearing: [98](98-withdrawn-scenarios-are-referenced-by-name.md) rests on it. `check_modifier_names` was built and **not shipped**: read as an allowlist the dump scores **125 unknown names in 12,464 vanilla references**, and **117 of the 125 have vanilla loc keys** — real modifiers it omits, the whole `<category>_jobs_bonus_workforce_mult` family among them. Widened to dump ∪ vanilla loc keys the floor is **vanilla 0, `src/` 0 of 96, build 0 of 2,167** — no defect to catch, so no check, because one that cannot fail reports a number. Not snapshotted: 4.7 MB, regenerated per launch, and `.source/` is gitignored* |
| [105](105-ten-log-files-nothing-had-named.md) | Ten of the nineteen log files had never been named by any document, and the one the guide called empty had been carrying content for a day — *live-runs.md said `debug.log` was "empty in every run so far"; it held **10,663 bytes** from the same 2026-08-28 run three decisions were written from. Six rows for a directory of **nineteen log files**, and **ten of them had never been named by any document or tool** — `script_documentation/` among them, only its `triggers.log` ever cited. `debug.log` triaged: 72 records, 71 `Category already set to X, overriding`, **64 of them from vanilla's own `specimens.txt` — 0% ours**, the same verdict [103](103-setup-log-is-a-load-manifest.md) reached by the same method. The eight empties' writers established by string search over the **unstripped** game binary: four verified writers (`dump_event_data`, `script_profiler` ×2, `libPDXSDK.so` — which is why `pdxsdk.log` alone is mode 0644) and four verified absences. Adds `tools/logs.py` and `make logs`, which fails when an EMPTY file gains bytes or an unnamed file appears — control **2 errors on an injected pair, 19 files and 0 warnings on the real directory** — and `check_log_inventory`, which holds the tool's table and the page to each other so the row cannot rot again* |

---

## Writing a new one

Next free number, `NN-slug.md`, the head format in
[style guide §7](../style-guide.md#7-decision-files-have-a-fixed-head), then:

1. add a row to this index in the right section;
2. update [planning/status.md](../planning/status.md) and
   [planning/open-questions.md](../planning/open-questions.md) if it closes
   something they list;
3. run `make docs`.
