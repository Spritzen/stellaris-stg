# 18 — Walshicus' shipsets replace STNH's hulls for nine of fourteen cultures

**Date:** 2026-08-03
**Status:** accepted
**Supersedes, in part:** [17 — STNH shipsets on a vanilla chassis](17-stnh-shipsets-on-a-vanilla-chassis.md)

## The problem decision 17 was solving, and why it could not be solved

STNH replaced vanilla's ship sizes with its own single-slot ladder, so no Trek
culture in its art declares a destroyer, cruiser or battleship entity under
vanilla's names. Decision 17 closed that gap by generating vanilla-shaped
entities on top of STNH's hulls — `clone` of an STNH hull for the frame, `clone`
of its `coreA/B/C` for the bow section, and a no-mesh `stg_empty_section_entity`
for the mid and stern slots STNH has no art for.

Two live runs measured what that costs:

| | 2026-08-02 | 2026-08-03 |
|---|---:|---:|
| `assetfactory.cpp:1019` — clone parent not loaded yet | 537 | **0** |
| `ship_design_templates.cpp:405` — template locator missing | 308 | 1,362 |
| `section.cpp:311` — section entity locator missing | 228 | 790 |

The clone half was fixed and stayed fixed. **The locator half cannot be fixed
the way decision 17 assumed.** All 268 entities reporting a missing locator
declare that exact locator in `zz_stg_shipsets.asset`, and the engine ignores it:

```
zz_stg_shipsets.asset  name = "federation_battleship_bow_XL1_entity"
                       clone = "federation_sovereign_coreA_entity"
                       locator = { name = "xl_gun_01" position = { 0 0 0 } }

error.log  [section.cpp:311]: ship section entity "federation_battleship_bow_XL1_entity"
                              is missing required locator "xl_gun_01"
```

Vanilla has 264 entities that use `clone`. **None of them declares its own
`locator`.** The combination is unattested in the reference tree, and 989
generated attach points bought nothing. 630 of the 790 records are sections
cloning the mesh-less empty section, where there is no geometry to mount on at
all — a `position = { 0 0 0 }` locator would put a turret at the hull origin
even if the engine honoured it.

So two of every Trek warship's three sections were fictional by construction.
That is not a bug in the generator; it is the cost of putting one-piece hulls on
a three-slot chassis.

## What changed

Walshicus published 22 standalone Trek shipsets (the *Star Trek: New
Civilisations* family), each one culture, each **built on vanilla's chassis
natively**: `common/graphical_culture/<culture>.txt` with `fallback =
mammalian_01`, and `gfx/models/ships/<culture>/` laid out by vanilla ship size,
declaring 124 entities including **all 44 of vanilla's section entities** under
vanilla's own names.

Checked against the engine's own requirement — the locators
`common/section_templates/` mount components on, resolved through the clone
chain and the `.mesh` binaries:

```
22 shipsets × 44 section entities declared × 0 missing locators
```

The only hits were 5 on `<culture>_titan_entity`, and **vanilla's own
`mammalian_01_titan_entity` fails identically**: its mesh carries `part1` and no
guns, because a titan's mounts live on its bow/mid/stern parts, not its frame.
That is vanilla parity, not a gap.

## The decision

**Nine cultures move to Walshicus' sets. Five stay on STNH through the
generator, because no set exists for them.**

| Species class | was (STNH) | now |
|---|---|---|
| FED | `federation` | `starfleet_tng` |
| VUL | `vulcan_01` | `vulcan` |
| KDF | `klingon` | `klingon` (Walshicus') |
| ROM | `romulan` | `romulan` (Walshicus') |
| CAR | `cardassian_01` | `cardassian` |
| FER | `ferengi_01` | `ferengi` |
| THO | `tholian_01` | `tholian` |
| DOM | `dominion_01` | `dominion` |
| BRG | `borg_01` | `borg` |
| BAJ, TRI, ADR, BOL, BRE | `bajoran_01`, `federation_32`, `andorian_01`, `bolian_01`, `breen_01` | unchanged — STNH, generated |

`tools/gen_shipsets.py` is not retired; it is narrowed from fourteen cultures to
five. Output drops from 982 entities to 380.

Thirteen further cultures arrive with no species class yet — Terran NX, Caitian,
Yridian, Tuterian, Xindi, Talarian, Malon, Betazoid, Suliban, Krenim, Elachi,
Lukari, Vidiian. They cost nothing unused, and are the obvious raw material for
the Phase 2 species work. **Eight of the thirteen became playable empires the
same day** (Caitian, Xindi, Suliban, Yridian, Krenim, Malon, Vidiian, Terran NX
— plan.md §6, Phase 2); the other five are still unused art.

### What is taken from each set, and what is not

Only `gfx` and `common/graphical_culture`. The omissions are all deliberate:

- **`interface/`** — every set ships a 3,391-line `interface/credits.txt` that
  shadows vanilla's 10,945-line one. Decision 08's failure mode exactly.
- **`common/species_classes/`** — each declares its own (`STARFLEET_TNG`,
  `KLINGON`, …). STG owns that namespace; the binding is one
  `graphical_culture =` line in `src/`, per [decision 10](10-species-class-keys-unprefixed.md).
- **`flags/`** — all 22 write `flags/trek/`, where 43 of their 82 files collide
  with STNH's 425. STNH stays the flag source. **Open item:** the 39 they add
  that STNH lacks have not been looked at.
- **`localisation/`** — carries only the species-class name we don't take and
  `FLAG_CATEGORY_trek`, which STNH already provides.

Root-level files (`descriptor.mod`, `credits.txt`, `layout.txt`) are never
vendored anyway, per vendor.yml's standing rule.

### STNH's ship tree: pruned, then partly restored

This is the other half of the change, and it was **not** optional. STNH has
directories named `klingon` and `romulan`; so does Walshicus. Same path, so the
newer art wins the `.gfx` that *declares* a mesh while STNH's `.asset` that
*uses* it survives — 7 dangling references to `romulan_research_station_mesh`,
caught by `make validate` on the first build of the new tier.

The include list is the five cultures we still generate for, plus the
directories `gen_shipsets.py`'s own output says it borrows stations and civilian
craft from, plus the shared directories that `make validate` named one rebuild
at a time. Each exclude and each acked mesh name is recorded in `vendor.yml`
where it applies.

**Do not take a file count off this page.** The first prune took STNH's ship
tree to 13 directories; it has grown twice since, each time because a check
asked about one file type further down (below, and
[decision 24](24-group-c-texture-references.md)). `vendor.yml` is the list and
`.vendor-manifest.json` is the count.

Two cross-culture aggregators had to be excluded by name rather than pruned by
directory, because each one references art from *every* STNH culture and so
drags the whole 104-directory tree back in behind it:
`starbases/sth_starbase_entities.asset` (one starbase set per culture) and
`other/empire_select/empire_select_dummy.asset` (the empire-selection preview).

## Prediction for the next live run

Measured per culture out of the 2026-08-03 log, so this is arithmetic on
observed data rather than an estimate:

| class | 2026-08-03 | predicted |
|---|---:|---:|
| `assetfactory.cpp:1019` | 0 | **0** |
| `section.cpp:311` | 790 | **282** |
| `ship_design_templates.cpp:405` | 1,362 | **489** |
| shipset total | 2,152 | **771** |

The 282 and 489 are the exact counts the five kept cultures contributed to that
run — `bajoran_01` 58/101 and 56/97 for each of the other four. They are
expected to survive unchanged, because nothing about how those five are
generated has changed. **If they move, the generator's donor changes moved them,
and that is the finding.**

The 1,692-record floor is **not** predicted. 22 sources were added and 3,987
STNH files removed, and neither side's effect on it has been measured. Derive it
from a complete `uniq -c` over the new log rather than assuming it held.

## RESOLVED 2026-08-12 — both open items below

The 2026-08-12 live run settled both, and
the 08-12 analysis
carries the measurements. In summary:

- **The prediction in the table above was exact.** The five kept cultures came in
  at `bajoran_01` 58 and 56 for each of the other four = **282**, to the record.
  The run measured 506 because [decision 19](19-stnh-minor-powers-as-ai-empires.md)
  added four `generic_*` donor directories as cultures afterwards (+224). Nothing
  moved.
- **The locator check was rewritten and calibrated**: 0 false negatives against
  the engine's 506, reported as a tracked count of 676 rather than as errors.
  Both that rewrite and the 99-non-erroring-entity puzzle it left behind were
  settled later by
  [decision 30](30-clone-discards-sibling-locators.md) — `clone` discards every
  locator declared beside it, so the check was crediting 252 dead declarations
  and the rewrite was still a check that could not fail. Read 30 for the rule
  and [28](28-weapon-locator-positions.md) for the repair.
- **A third, larger defect this decision introduced** was found by the same run:
  pruning STNH's ship tree left 15 `.mesh` files declared by art we kept and
  absent from the build, costing **1,640 records**. `make validate` gained
  `check_gfx_file_refs`; the five directories are back in the `include:` list.
  A second, smaller instance of the same defect — bare texture filenames — was
  closed by [decision 24](24-group-c-texture-references.md), which found the
  same include list had never named `shared_assets/` at all.

The section below is kept as written, for the reasoning.

## What only the user's eyes can grade

1. **Do the nine new shipsets render, and do weapons draw on them?** The whole
   case for the swap is that they carry real mount points. `error.log` cannot
   confirm a turret appearing — a locator that resolves produces no record.
2. **Do the five STNH cultures still look right?** Their donor pool shrank when
   nine cultures left the harvest; the generator re-picked stations and civilian
   craft from what remains.
3. Everything in [decision 17's list](17-stnh-shipsets-on-a-vanilla-chassis.md)
   that is not about ship art is unchanged.
