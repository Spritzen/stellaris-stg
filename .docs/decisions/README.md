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

---

## Writing a new one

Next free number, `NN-slug.md`, the head format in
[style guide §7](../style-guide.md#7-decision-files-have-a-fixed-head), then:

1. add a row to this index in the right section;
2. update [planning/status.md](../planning/status.md) and
   [planning/open-questions.md](../planning/open-questions.md) if it closes
   something they list;
3. run `make docs`.
