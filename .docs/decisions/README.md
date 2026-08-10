# Decisions — index

> **What** — all 80 resolved decisions, grouped by subject, one line each.
> **Open when** — before reopening a settled question, or when a citation names a
> decision by number and you need to know what it says.
> **Then** — [Style guide §7](../style-guide.md#7-decision-files-have-a-fixed-head) for the file format · [Documentation map](../README.md)

**Read the decision before reopening its question.** Each file records what was
decided, why, and what it cost — usually a live run. Several were falsified by a
later run and kept anyway, because the pair is worth more than either alone.

**These files do not move.** The number is the address, and several hundred
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
| [05](05-harvest-order.md) | Harvest order corrections |
| [11](11-drop-cinematic-camera-and-ambient-soundtracks.md) | Drop Cinematic Camera, Kammarheit and Apocryphos — *Cinematic Camera restored by [43](43-planet-scale-system-length.md)* |
| [12](12-fix-source-errors-dont-drop.md) | **Fix a source mod's errors; never drop the mod to silence them** |
| [80](80-mem-integration-deferred.md) | More Events Mod is in scope and waits — it writes the databases Phase 4 just wrote by hand, and eyes cannot attribute what they cannot separate |

## The pipeline

| | |
|---|---|
| [04](04-no-source-archive.md) | No source-mod archive — *superseded by [09](09-source-snapshot.md)* |
| [09](09-source-snapshot.md) | The build reads `.source/`, not `/workshop` |
| [13](13-build-dir-and-symlink-deploy.md) | The mod tree moves to `stg-build/`, and the deploy is a symlink |
| [29](29-merge-semantics-per-directory.md) | Which file wins is a property of the **directory** — the FIOS/LIOS table |
| [45](45-clutter-pass.md) | Unreferenced content goes by default, and the closure decides |

## Deployment and runtime

| | |
|---|---|
| [07](07-launcher-local-mod-registration.md) | The launcher does not scan `mod/` — registry, playset and files are three systems |
| [15](15-native-linux-runtime.md) | Compatibility mode off: native Linux build, and the user-data folder moved back |

## Merges, shadows and duplicates

| | |
|---|---|
| [06](06-gui-merges-unnecessary.md) | The two `interface/*.gui` merges are unnecessary |
| [08](08-stnh-art-shadows-vanilla.md) | STNH's art shadows vanilla, and its art **is** script |
| [24](24-group-c-texture-references.md) | Group C is a texture problem, and the include list could not see it |
| [33](33-duplicate-entity-declarations.md) | One entity name declared twice silently decides which art renders |
| [34](34-src-shadows-drop-source-declarations.md) | An `src/` override shadows the *sources* too, not just vanilla |
| [37](37-attach-edges-into-pruned-art.md) | `attach` edges into pruned STNH art — kept, not integrated |
| [38](38-real-space-drops-sol-neighbours.md) | Real Space drops ten Sol-neighbour initializers PD still calls |
| [39](39-sbx-citadel-slot-renumbering.md) | SBX renumbers vanilla's citadel gun slots and vanilla's own design breaks |
| [46](46-coalition-of-hope-takes-vul.md) | Three findings from the 08-07 fourth run, and the two checks they bought |
| [53](53-duplicate-entity-triage.md) | The 13 duplicate entity declarations, triaged — and the suppression that swallowed a real one |
| [54](54-federation-texture-collisions.md) | The `federation/` vs `starfleet_tng/` texture pairs are the same artwork |
| [56](56-starbase-modules-order.md) | `common/starbase_modules` fed by two sources: looked at, acked |

## Empires, species and names

| | |
|---|---|
| [10](10-species-class-keys-unprefixed.md) | The five species classes take STNH's bare keys, not `STG_` |
| [14](14-remove-vanilla-prescripted-empires.md) | Remove vanilla's prescripted empires; pin `supported_version` exactly |
| [19](19-stnh-minor-powers-as-ai-empires.md) | STNH's remaining prescripted empires, as AI-only minor powers |
| [20](20-minor-power-species-class-keys.md) | Eight minor powers take STNH's species-class key, not a near miss |
| [21](21-species-class-localisation.md) | Species class loc keys hang off the class key, **unprefixed** |
| [23](23-prescripted-ruler-appearance.md) | Prescripted rulers pin no appearance index |
| [25](25-real-home-systems.md) | Real home systems, and why the original plan was wrong about them |
| [26](26-home-system-classes.md) | STNH identifiers in generated home systems — a crash that logs nothing |
| [41](41-civic-granted-species-traits.md) | Six Trek empires took a civic without the trait it grants |
| [44](44-random-names-pools-append.md) | `common/random_names/` pools append — *arithmetic corrected by [52](52-trek-star-names.md)* |
| [47](47-minor-power-names-truncated.md) | 78 of 79 minor-power names shipped truncated, 16 loc keys shipped as text |
| [51](51-prescripted-loc-scope.md) | The other three prescripted-power files are clean; the check keeps two scopes |
| [52](52-trek-star-names.md) | Trek star names come from STNH's **maps**, not its `star_names` pool |
| [81](81-random-names-are-loc-keys.md) | A quoted random name is a localisation key, and STG shipped 330 with no key — *falsifies [52](52-trek-star-names.md) in part* |
| [59](59-ship-name-pools.md) | STNH's ship registries, folded onto vanilla's ship sizes |
| [72](72-ship-class-names.md) | STNH declares its own class names, so 59's fuzzy join was never needed |
| [73](73-class-name-thematic-fill.md) | A class-name pool is one semantic field, and vanilla is the model for filling one |

## Ship art and weapon mounts

| | |
|---|---|
| [17](17-stnh-shipsets-on-a-vanilla-chassis.md) | STNH shipsets on a vanilla chassis — *narrowed by [18](18-walshicus-shipsets-replace-stnh-hulls.md)* |
| [18](18-walshicus-shipsets-replace-stnh-hulls.md) | Walshicus' shipsets replace STNH's hulls for nine of fourteen cultures |
| [28](28-weapon-locator-positions.md) | Weapon locators: `.asset` declarations do count, and they need positions |
| [30](30-clone-discards-sibling-locators.md) | `clone` discards every locator declared beside it |
| [31](31-asset-local-variables.md) | `@variables` in art files are file-local, and copying an entity leaves them behind |
| [35](35-station-section-attach-points.md) | Walshicus' station hulls carry no section attach points |
| [60](60-mounts-share-existing-points.md) | A missing mount shares a point the artist drew |
| [82](82-hull-section-attach-points.md) | Every Trek hull above corvette borrows a corvette's frame, and its sections hang on points a corvette does not have — *[35](35-station-section-attach-points.md) one entity family over* |
| [67](67-source-art-hardpoint-names.md) | The artist's vocabulary is not the game's |

## Portraits, clothes, rooms, city sets and flags

| | |
|---|---|
| [16](16-phase-3-clothing-triggers.md) | Real bodies for the 140 STNH clothing triggers |
| [22](22-empire-designer-clothes.md) | `game_setup` is a scope, and a shared selector has to gate it too |
| [32](32-declare-stub-species-classes.md) | Declare the 34 selector-named species classes; retire the ack |
| [42](42-event-picture-geometry.md) | Event pictures are re-cut to vanilla's dimensions at harvest |
| [48](48-room-selector-merge.md) | One `room_selector`, written by us — a database nothing could dangle on |
| [49](49-flags-city-sets.md) | The shipsets' 39 extra flags, 22 empires on a grey placeholder, the Trek city sets |
| [50](50-paragon-backgrounds.md) | Paragon leader backgrounds: declare our own rather than un-exclude STNH's |
| [57](57-prescripted-rulers-unpin-clothes.md) | A prescripted ruler pins no clothes index at all |
| [58](58-city-set-geometry.md) | STNH's city layers are a 560×280 canvas in an 800×400 planet view |
| [62](62-city-set-cultures-undeclared.md) | Five city sets with complete art and no declaration — the designer hid the empires |
| [63](63-city-set-family-targets.md) | Read the resample target off vanilla's **family**, not only the file |
| [64](64-terran-empire-mirror-uniforms.md) | The Terran Empire's mirror uniforms, and four female rows with no species gate |
| [66](66-city-set-canvas-overflow.md) | A file taller than the canvas was scaled by two different factors |
| [68](68-ruler-clothes-index-restored.md) | An absent `clothes` is index 0 — **falsified by [69](69-ruler-clothes-dedicated-selectors.md)**, kept for the diagnosis |
| [69](69-ruler-clothes-dedicated-selectors.md) | A shared master selector cannot be indexed; give the ruler its own |
| [70](70-vulcan-city-framing.md) | The Vulcan city is not cropped by us; the art is composed that way |
| [74](74-event-picture-families.md) | `gfx/event_pictures` is two families, and reading it as one left 865 pictures unasked |

## Content — events, anomalies and archaeology

| | |
|---|---|
| [75](75-trek-anomalies.md) | Phase 4 starts with anomalies, because they are the one part of "a voice" with a yardstick |
| [76](76-trek-archaeology.md) | Trek archaeology, and the one field in the format that decides whether any of it is ever seen |
| [77](77-trek-story-events.md) | Trek story events, and the merge question the design refuses to ask |
| [78](78-phase-4-count-corrections.md) | Four numbers in Phase 4 were wrong, and the worst was another database's right number — *corrects [75](75-trek-anomalies.md) and [77](77-trek-story-events.md) in part* |

## Audio

| | |
|---|---|
| [55](55-federation-anthem.md) | The Federation anthem plays, and a check that a track is reachable |
| [61](61-music-player-track-names.md) | The music player draws the declaration name, and 16 had no key |
| [65](65-music-rotation-dedupe.md) | The rotation is 27 tracks, not 86, and six of them were one recording |

## Checks, calibration, and things reviewed then left

| | |
|---|---|
| [27](27-quoted-class-keyword.md) | A quoted `class` keyword is a different keyword — 23 missing stars, 3 blind checks |
| [36](36-oversized-real-space-systems.md) | Real Space's oversized systems: leave them, they are its own warning |
| [40](40-live-run-2026-08-07-repairs.md) | The 2026-08-07 15:41 run's small defects, and what each one cost |
| [43](43-planet-scale-system-length.md) | `PLANET_SCALE_SYSTEM` is measured against an array no script can set |
| [71](71-doc-inventory-checks.md) | A doc citation can resolve perfectly and still describe a repo that moved |
| [79](79-reachability-checks.md) | A site with no `weight` and a category with no `spawn_chance` are complete, clean and unreachable — and the second half of the question is what makes the check worth having |

---

## Writing a new one

Next free number, `NN-slug.md`, the head format in
[style guide §7](../style-guide.md#7-decision-files-have-a-fixed-head), then:

1. add a row to this index in the right section;
2. update [planning/status.md](../planning/status.md) and
   [planning/open-questions.md](../planning/open-questions.md) if it closes
   something they list;
3. run `make docs`.
