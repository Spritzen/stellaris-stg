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

The BOM rule asks vanilla **per folder** rather than asserting one answer:
`common/name_lists/` is BOMed 76 times out of 76 and every other database zero.

---

## B. Names that must resolve against the merged tree

The largest family. Each asks: *this file names something — does anything
declare it?*

| Check | Asks | Written for |
|---|---|---|
| `check_dangling_identifiers` | scripted triggers, traits and species classes the vendored art names | 34 STNH species classes falling through to the clothes selector's `default` — [32](../decisions/32-declare-stub-species-classes.md) |
| `check_dangling_shaders` | shader effects a mesh names | Real Space's gas giant rings drawing with no material — [34](../decisions/34-src-shadows-drop-source-declarations.md) |
| `check_dangling_art_references` | meshes and particles a vendored `.asset` names | |
| `check_gfx_file_refs` | bare texture filenames a vendored `.gfx` names, and whether the file is on disk | 190 textures named by kept `.gfx` files, none in the tree — [24](../decisions/24-group-c-texture-references.md) |
| `check_texture_basenames` | a `meshsettings` texture — a **bare** filename — resolved by basename against everything loaded, vanilla included | the sibling above skips bare filenames, which left `texture_diffuse = "foo.dds"` unasked in any form: 139 `Failed to find texture` records, **not one** of them in the built tree, against a clean `make validate` |
| `check_asset_variables` | `@variable` an art file references that neither it nor `common/scripted_variables/` declares | loads as `Malformed token` and drops the value — [31](../decisions/31-asset-local-variables.md) |
| `check_initializer_classes` | planet classes, star classes and asteroid belt types a solar system initializer names | a startup crash that logs **nothing at all** — [26](../decisions/26-home-system-classes.md) |
| `check_attach_targets` | entities named by `attach = { "slot" = "X" }` | vanilla leaves 0 of its 5,672 such references unresolved — [37](../decisions/37-attach-edges-into-pruned-art.md) |
| `check_room_references` | the room or city set a prescripted empire names, backed by a real `*_room.dds` / `*_city_l01.dds`; and the `common/graphical_culture/` entry behind a city set | the one database addressed by a **bare name with no path and no declaration** — [48](../decisions/48-room-selector-merge.md), [62](../decisions/62-city-set-cultures-undeclared.md) |
| `check_prescripted_initializers` | home-system initializers a prescripted empire names | [25](../decisions/25-real-home-systems.md) |
| `check_prescripted_portraits` | portrait sets and groups an empire names | |
| `check_name_lists` | name-list tokens with no loc key | every name token is a loc key — 603 of them, not the 218 first scored |
| `check_species_class_loc` | species classes missing the loc family the engine derives from the class key, **or carrying it under an `STG_` prefix it never looks up** | a raw three-letter key on screen, nothing in `error.log` — [21](../decisions/21-species-class-localisation.md) |
| `check_music_declarations` | a music track no `music = { }` names, a declaration naming no file, **and a playlist entry with no loc key** | the Federation anthem unheard through every run — [55](../decisions/55-federation-anthem.md); 16 of 22 tracks listed as `newhorizonssong1` — [61](../decisions/61-music-player-track-names.md) |

`check_texture_basenames` matches on the **stem**, not the filename: the engine
resolves the extension itself and vanilla relies on it — its own
`_other_meshes.gfx` asks for `.tga` files it ships only as `.dds`. That is all
five of vanilla's `.tga` references, so an extension-sensitive check would report
vanilla itself ([rule 4](check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand)).

### The written form can be part of the name

`class = "star"` is **not** `class = star`. `star` is an engine keyword, and
quoted it stops being one, so the body is never created. Three separate checks
made the quotes optional in a regex and were blind to 23 missing stars across 20
home systems while reporting clean. [Decision 27](../decisions/27-quoted-class-keyword.md).

The converse is a separate trap that looks identical in a regex: STNH writes
`is_species_class = "HOLO"` quoted, and three checks reading that field with a
bare-only `(\w+)` were blind to it.
[Decision 32](../decisions/32-declare-stub-species-classes.md).

**Ask whether a field's written form changes its meaning before normalising it.**

---

## C. Two sources, one key

Harvest order does not reach this case: both files ship, and the engine picks by
**filename sort within the directory** — first for the fourteen FIOS
directories, last for everything else.
[Decision 29](../decisions/29-merge-semantics-per-directory.md).

| Check | Asks | Note |
|---|---|---|
| `check_key_conflicts` | any `common/` database key claimed by two mod families, or redefined smaller than vanilla's | names the file that **wins** |
| `check_defines_conflicts` | `common/defines/` keys set by two sources **to different values**; length-coupled arrays that disagree; an array coupled to an engine-internal one **no script can set** | matching the scriptable pair is necessary and not sufficient — saying `ok` on that basis hid a live error for five days, [43](../decisions/43-planet-scale-system-length.md) |
| `check_order_sensitive_databases` | an order-sensitive database fed by more than one source | [56](../decisions/56-starbase-modules-order.md) |
| `check_duplicate_entities` | one entity name declared by two files with **bodies that differ** | vanilla names 8,409 entities and never repeats one — [33](../decisions/33-duplicate-entity-declarations.md), triaged in [53](../decisions/53-duplicate-entity-triage.md) |
| `check_duplicate_textures` | one texture **basename** carried by two folders with different content | a `.mesh` names its textures by bare filename *inside the binary*, so the engine keeps one globally: vanilla repeats 1 basename in 7,711, the built tree repeated 142 — [46](../decisions/46-coalition-of-hope-takes-vul.md), [54](../decisions/54-federation-texture-collisions.md) |

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
([38](../decisions/38-real-space-drops-sol-neighbours.md)). `flags/colors.txt`
cost 47 of vanilla's 72 flag colours this way
([08](../decisions/08-stnh-art-shadows-vanilla.md)).

`check_src_source_regression` exists because `src/` beats the sources too, not
only vanilla: `src/gfx/FX/pdxmesh.shader` was written as "vanilla 4.4 plus STNH's
five effects" and dropped all 41 Real Space appends to the same path
([34](../decisions/34-src-shadows-drop-source-declarations.md)).

---

## E. It resolves, and it is still wrong

The subtlest family. Nothing dangles; the defect is in the *value*, the
*geometry* or the *position*.

| Check | Asks | Written for |
|---|---|---|
| `check_shadowed_texture_geometry` | vendored art that shadows a vanilla **texture** path at different pixel dimensions — and art that shadows *no* vanilla path but breaks the family vanilla is uniform about | STNH's 620×264 event pictures drawn at 930×396 inside UIOD's 693×239 frame through two live runs of `ok` — [42](../decisions/42-event-picture-geometry.md); city layers on a canvas exactly 70% of vanilla's, drawing every planet's buildings low and small — [58](../decisions/58-city-set-geometry.md), [63](../decisions/63-city-set-family-targets.md), [66](../decisions/66-city-set-canvas-overflow.md) |
| `check_prescripted_loc` | prescripted loc converted from a source that no longer says what the source says: a value that is still a loc **key**, or a name **truncated** to a substring | 78 of 79 minor powers shipped as `of Earth`, `-Aurian Auditorium`, `'Q Stagnancy` — nothing in `error.log` ever, because **loc that resolves to the wrong string still resolves** — [47](../decisions/47-minor-power-names-truncated.md). Two scopes on purpose: [51](../decisions/51-prescripted-loc-scope.md) |
| `check_prescripted_empires` | traits, ethics or portraits that break a rule vanilla's own databases declare; a civic **granting** a species trait no species block carries | reported once per trait name, so six broken empires read as three log lines — [41](../decisions/41-civic-granted-species-traits.md). See [prescripted empire rules](../reference/prescripted-empire-rules.md) |
| `check_prescripted_appearance` | ruler `texture` / `clothes` indices that are off the end of the list | `texture = 1` was off the end on **74** of 101 — [23](../decisions/23-prescripted-ruler-appearance.md), [57](../decisions/57-prescripted-rulers-unpin-clothes.md), [69](../decisions/69-ruler-clothes-dedicated-selectors.md) |
| `check_portrait_clothes_selectors` | selector rows with no species gate, and the scopes the game actually reads | four female master-selector rows with no gate put every ungated non-Federation female commander in Vulcan clothes — [64](../decisions/64-terran-empire-mirror-uniforms.md), [22](../decisions/22-empire-designer-clothes.md) |
| `check_asset_load_order` | a `locator` declared beside a `clone`, and `clone` resolution order | `clone` resolves against entities **already loaded**, walking `gfx/models/ships/` as one alphabetical sequence — "declared somewhere" said yes 982 times while the Vulcan and Tholian shipsets did not render at all — [30](../decisions/30-clone-discards-sibling-locators.md) |
| `check_section_attach_points` | a hull entity missing the `part1`..`partN` attach points its ship size's `section_slots` names | all 22 Walshicus shipsets declared only `root`, so station sections had nowhere to attach — [35](../decisions/35-station-section-attach-points.md) |
| weapon-mount positions (in `check_asset_load_order`) | a weapon mount with no position anywhere | it fires from the middle of the ship — [28](../decisions/28-weapon-locator-positions.md), [60](../decisions/60-mounts-share-existing-points.md), [67](../decisions/67-source-art-hardpoint-names.md) |
| `check_colony_name_collisions` | a name list whose colony and capital pools collide | |
| `check_home_planet_generation` | a home planet that will not generate as the empire declares it | |

---

## F. The dual — a file nothing references

`check_unreferenced` asks the **reverse** of every question above: not *does this
name resolve*, but *does anything name this file?*

813 STNH event pictures no `spriteType` declares sat in the tree because nothing
had ever asked that direction. [Decision 45](../decisions/45-clutter-pass.md),
and [the clutter closure](clutter.md) for how it decides and why its scope is
narrow.

**This is the one check that deletes**, which changes everything about how it is
calibrated — see [check design, rule 1](check-design.md#1-a-check-that-deletes-is-not-a-check-that-reports).
