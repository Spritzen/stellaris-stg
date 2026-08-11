# Conflict register — who wins a contested path, and why

> **What** — the paths two or more sources claim, how each was settled, and the
> explicit excludes.
> **Open when** — a file in the build came from a mod you did not expect, or you
> are adding a source that ships a path something else already does.
> **Then** — [Harvest order](harvest-order.md) · [decision 29](../decisions/29-merge-semantics-per-directory.md) · [Key-conflict checks](../validation/checks.md#c-two-sources-one-key)

**`make vendor` reports 947 overwrite events — plus 220 paths skipped by the
additive-only rule and 888 files removed by the prune closure** (build of
2026-08-10). Read them out of `.vendor-manifest.json` rather than recounting by
hand; they move whenever a source is dropped or an `include:` widens, and this
section has been stale five times for exactly that reason:

```bash
python3 - <<'EOF'
import json, collections
m = json.load(open('.vendor-manifest.json'))
ow = m['overwrites']
print(len(ow), 'overwrites,', len(m['skipped']), 'skipped,', len(m['pruned']), 'pruned')
for o in ow:
    if not o['path'].startswith('gfx/'):
        print(' ', o['path'], '|', o['from'], '->', o['to'])
print(collections.Counter((o['from'], o['to'])
      for o in ow if o['path'].startswith('gfx/')).most_common(10))
EOF
```

They are overwrite *events*, not contested paths: a path three sources claim
scores twice.

> **This register enumerates contested PATHS, and two sources can also contest a
> KEY under different filenames.** Harvest order does not reach that case at all:
> both files ship, and the engine picks by **filename sort within the directory**
> — first for the fourteen FIOS directories, last for everything else.
>
> `check_key_conflicts` and `check_defines_conflicts` cover it, comparing
> *content* so that two sources setting one key identically are not reported.
> **`renames:` in `vendor.yml` is the only lever that changes who wins**, where
> the nearest thing used to be an `src/` copy of the whole losing file altered in
> nothing but its name.
>
> [Decision 29](../decisions/29-merge-semantics-per-directory.md) has the FIOS
> table, what was rejected from it, and why it is the one allowlist here not
> measured against `/stellaris`.

---

## Needs a real merge — write the file in `src/`

Deltas measured against vanilla with line endings normalised.

| File | Contenders (delta from vanilla) | Approach |
|---|---|---|
| `common/planet_classes/00_planet_classes.txt` | Real Space **323 lines**, PD **113** | **Done.** Load-bearing for habitability. Real Space's ~300 removed lines are 11 star classes it *moves* to `realspace_planet_classes.txt`, not deletions. Exactly one block, `pc_continental`, is touched by both, and their edits do not overlap. |
| `common/traits/04_species_traits.txt` | PD **37**, PD - Ascension Worlds **65** | **Done.** Of the 3 blocks both touch, 2 are byte-identical. Base is Ascension plus PD's `trait_plantoid_bloomed`. |
| `gfx/particles/realspace_generic_particles.gfx`, `gfx/models/planets/rs_star_meshes.gfx` | Real Space vs **STNH's fork of the same two filenames** | **Done, and it is the case `additive_only` creates.** STNH forked Real Space's files and added entries; Real Space wins the path and STNH's additions are skipped — while the STNH file that *uses* them is vendored and calls for them 62 times. Resolved by two `src/` files that **declare rather than shadow**. |

> **Prefer declaring to shadowing.** The third row and the four
> `src/**/stg_restored_vanilla_entities.asset` files take a *new* filename and add
> only the missing declarations. The vendored file still wins its own path, we own
> nothing we did not write, and a source update cannot silently revert us. Reach
> for a same-path merge only when the file genuinely has to be one file, as the
> two `common/` rows do.

**Method — three-way diff against vanilla.** Each mod's delta is usually small and
disjoint; the merged file is vanilla plus both deltas. Record the reasoning in a
header comment on the merged file.

```bash
diff <(tr -d '\r' < /stellaris/common/planet_classes/00_planet_classes.txt) \
     <(tr -d '\r' < /workshop/819148835/common/planet_classes/00_planet_classes.txt)
```

---

## Settled by harvest order — record, don't merge

| File | Contenders | Winner and why |
|---|---|---|
| `common/scripted_variables/00_realspace_scripted_variables.txt` | Real Space, RS - System Scale | **System Scale.** It rescales every value the file defines (`@star_standard_scale` 20→70, `@planet_standard_scale` 11→24). Real Space's copy would undo the submod entirely. |
| `common/megastructures/06_matter_decompressor.txt` | Real Space, RS - System Scale | System Scale — it exists to rescale these. |
| `gfx/models/planets/_planetary_entities.asset` | Real Space, RS - System Scale, PD - More Arcologies | Last wins (More Arcologies). The two RS copies differ only by scale and More Arcologies is downstream of both. |
| `common/inline_scripts/traits/pd_nuked_effects.txt`, `radiotrophic_effects.txt` | PD, PD - Ascension Worlds | Extension wins. |
| `interface/resource_groups/topbar_other_resource_groups.txt` | Universal Resource Patch, PD - Unique Worlds | **URP, outright.** Its 1,271-line file is a strict superset of PD's 42-line one. Works *only* because URP loads last — [harvest order](harvest-order.md#why-the-universal-resource-patch-is-last-not-first). |
| `interface/planet_view.gui` | PD - Planet View, UIOD | **UIOD, outright.** PD's delta is a uniform +152px stretch of vanilla's 680-high layout; UIOD's rewrite is already 1220×940 with scaled variants and its own layout variables. PD's copy is also **stale against 4.4** — it references `GFX_arkship_header_default` and `ARKSHIP_BUTTON`, neither of which exists. |
| `interface/game_setup/setup.gui` | YAGEM, UIOD | **UIOD, outright.** YAGEM raises `ai_empires_container` to `height = 612` / `max_slots_vertical = 12`; UIOD reaches the same end better with a scrollable container and `max_slots_vertical` commented out. Applying YAGEM's values would re-impose the cap UIOD deliberately removed. |
| `interface/main_alerts.gui`, `resource_groups/ui_overhaul_*`, `ui_overhaul_qhd-gfx/*.gfx` | UIOD, UIOD - Extended Topbar | Submod wins. |

*(Two `interface/*.gui` files this section once listed as needing merges do not —
UIOD's rewrite subsumes both deltas and transplanting them would have introduced
bugs. [Decision 06](../decisions/06-gui-merges-unnecessary.md).)*

The `gfx/` overwrites are all last-wins within a family and need no individual
decisions — the large groups are UIOD → Dark UI (189), the 172 ship-asset
overrides written into `src/` by `tools/fix_ship_locators.py` (151 from the
Walshicus sets, 21 from STNH — decisions
[28](../decisions/28-weapon-locator-positions.md) and
[82](../decisions/82-hull-section-attach-points.md)), Starfleet TNG → Terran NX
(49), PD → Vanilla Replacements (45), PD → Ascension Worlds (41).

> **One family is worth knowing about**: the 22 Walshicus shipsets overwrite each
> other on shared texture and effect filenames, because they are one author's
> family sharing a `stnc_shipset_shared/` vocabulary. Last-wins is correct and no
> decision is needed; the visible cost is the 143 duplicate-texture records in
> every live run, where that library meets STNH's `shared_assets/`
> ([46](../decisions/46-coalition-of-hope-takes-vul.md),
> [54](../decisions/54-federation-texture-collisions.md)).

---

## Explicit excludes

| Source | Exclude | Why |
|---|---|---|
| Whiter Stars | `gfx/map/star_classes/b_star.dds`, `t_star.dds` | Real Space owns star classes and ships art for all of them. Whiter Stars is a 16-file mod declaring `supported_version="3.*"`; letting it override Real Space's star art is an accident of tier placement, not a decision. Its other 14 files are kept. |
| All sources | `desktop.ini`, `*.psd`, `Thumbs.db`, `*.bak`, `*.wip`, `*.wavorig`, `*.pdn`, `*.dcm` | Editor and Explorer by-products naming no Stellaris format at all. Vanilla ships 99 `.editordata`, 6 `.bak` and 2 `.ods` itself, which makes it a category rather than a complaint about one mod. [Decision 45](../decisions/45-clutter-pass.md), phase 1. |
| All sources | nine non-English `localisation/` trees | 235 files, plus 38 loose per-language files. Not unreachable — deliberate upstream content STG has no use for, on the same taste grounds as [decision 11](../decisions/11-drop-cinematic-camera-and-ambient-soundtracks.md). Decision 45, phase 3. |
| UIOD - Dark UI | `gfx/speeddial/**`, `gfx/tiny_outliner/**` | Re-skins for two mods not in the harvest — the only two directories in the tree with **zero** reachable siblings. Same class as the five URP topbar-compat files [decision 12](../decisions/12-fix-source-errors-dont-drop.md) excluded. |
| PD, PD - Unique Worlds | the two `*placehold*` civics/origins files | Each stubs a key that a submod **in the harvest** defines for real, with a body of `potential = { always = no }`. It loses on filename sort today and would win outright in a FIOS directory. |
| Real Space 4.0 | `localisation/replace/patrons_list.yml` | Two Patreon credit keys read by nothing, naming real people. |
| STNH | `gfx/models/ships/borg_01/test_diff` | A 128×128 DDS with no extension, so no loader can open it by any name. |
| Diverse Rooms | `gfx/portraits/asset_selectors/dr_room_textures.txt` | A SECOND file claiming `room_selector`, which STNH's copy of vanilla's file also claims — decided by nothing on disk, and under the reading where DR wins, its 277 unconditional `ruler` rows put every empire in a cave. Its 297 designer rows are merged into `src/`'s single selector instead. [Decision 48](../decisions/48-room-selector-merge.md). |

Beyond these, **`make vendor` removes unreferenced files itself** — 888 of them
on the build of 2026-08-10,
re-derived on every build by the reachability closure rather than listed here,
because an 813-line exclude list is correct the day it is written and silently
wrong after the next `make sources-sync`. See [the clutter closure](../validation/clutter.md).

> **The consequence to know about: `vendor.yml` alone no longer describes the
> output.** The manifest plus the closure do, and
> [`.docs/provenance.md`](../provenance.md) lists every removal.
