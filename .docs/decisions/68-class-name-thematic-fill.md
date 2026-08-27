# 68 — A class-name pool is one semantic field, and vanilla is the model for filling one

**Status:** decided, 2026-08-09
**Follows** [decision 67](67-ship-class-names.md), which harvested everything STNH
declares and left the rest measured.

## What was left

Decision 67 took every class name STNH has and stopped there, on the grounds
that a list with no size pools has no defect — `generic` is drawn 100% of the
time when nothing competes with it. That is true and it is not the same as
saying the pools are good. After that harvest, **five playable empires had no
tonnage at all** (Bolian, Tholian, Trill, Vidiian, Yridian), **eight had no
`titan`**, Xindi had one class name outside generic and Borg had no destroyer or
cruiser tier. Romulan had no destroyer.

## Vanilla is the model, and it has exactly two idioms

Reading all 13 vanilla lists that carry the block — the rule the project applies
to script, applied to content:

| | |
|---|---|
| **Invented species-language words** | HUM1 `Il-Koth, Daskall, Mongath, Sipii` · LITH3 `Kroshhk, Na'phonn, Naawr'hekh` · AVI1 `V'Taka, K'Mirom, S'Porak` |
| **One semantic field in plain English** | NEC4 vices `Abasement, Anxiety, Avarice, Bane` · HIVE2 robustness `Athletic, Brawny, Bulky, Durable` · AQU1 water `Abyss, Crest, Current, Ebb` · X_MACHINE_AGE1 cyber `Enigma, Ether, Nexus, Valence` |

Two things worth carrying:

- **Vanilla never splits `ship_class_names` by tonnage.** All 13 use `generic`
  only, 17–40 names, median 22. STG splits because its empires are Trek navies
  where the class *is* the tonnage — but the pool sizes vanilla thinks are right
  are the yardstick, and STG is under them.
- **The second idiom is invented English, and that is licensed.** `Abasement`
  is not a Necroid word somebody found; it is a writer choosing a register and
  filling it. STG's Phase 1 pools already work this way — the Yridian pool is
  `Ledger, Broker, Confidence, Ransom`, the Vidiian one `Phage, Sustainer,
  Harvest, Transplant`. **Extending an existing register is not inventing
  lore.**

## Decision

**99 hand-authored class names across 15 lists, +3 placements for Romulan;
820 → 1,864 tokens; 69 new keys in `stg_names_l_english.yml`**, which is where
hand-written names live. They are ordinary `src/` content, so
`gen_ship_class_names.py`'s union rule preserves them — confirmed by re-running
it to `+0`.

Each empire's field was checked against Memory Alpha or Memory Beta first, and
graded by tonnage: small and fast at corvette, heavy or ceremonial at titan.

| Empire | Field, and what grounds it |
|---|---|
| Bolian | Bolarus IX is stormy and oceanic with three continents under the Quorum of Bole — an oceanic register in AQU1's idiom. `Bole, Spindrift, Shoal` → `Threefold, World Council` |
| Tholian | Silicon-based, crystalline, mineral carapace. Extends the tree's own `Lattice, Prism, Facet`. `Shard, Sliver, Chert` → `Corundum, Weaver, Adamant` |
| Trill | Leran Manev on Manev Bay under Bes Manev, the Tenara cliffs, the Caves of Mak'ala, initiates and Guardians, the zhian'tara. `Initiate, Manev` → `Bes Manev, Zhian'tara` |
| Vidiian | Two thousand years of the Phage and the *honatta* who harvest against it. Surgical register. `Lancet, Scalpel, Suture` → `Sodality, Convalescence` |
| Yridian | Information merchants; Jaglom Shrek sold Worf his father's fate. `Courier, Cipher, Errand` → `Contraband, Clearinghouse, Trove` |
| Xindi | **The one place canon supplied the tonnage itself.** The six species of Xindus graded by the ships canon gives each — Insectoid fast and aggressive, Reptilian the warship, Primate and Arboreal lightly armed, Aquatic largest and slowest. `Avian` is a memorial; they were extinct by the 2150s |
| Borg | Geometry and collective anatomy, continuing the cube/sphere/pyramid series. Canon puts the scout ship between probe and sphere, so `Scout` moved to destroyer; `Tetrahedron, Vinculum, Dodecahedron` |
| The eight titans | Andorian `Shran, Kuthar` · Bajoran `Shakaar, Kohn-Ma` (resistance cells, as `Ornathia` already is) · Breen `Permafrost, Absolute Zero` · Caitian `Pridemaster, Sabertooth` · Ferengi `Divine Treasury, Grand Exchange` · Krenim `Continuum, Paradox` (temporal science, as `Annorax` is) · Malon `Behemoth, Theta` · Suliban `Cell Omega, Grand Helix` |

**Romulan needed no new names.** `Talon`, `Shrike` and `Whitewind` were already
in its `generic` pool and are light warbirds, so they were placed at destroyer —
and decision 67's demotion rule took them out of generic on its own. Where a
list already holds the right name in the wrong place, moving it beats writing
one.

**21 of 22 playable empires now have all five core tiers**, against 13 before.

## What was deliberately not done

- **The 46 AI-only minor lists stay generic-only.** Filling them means ~1,000
  names at a quality that would not survive being read, for empires that never
  appear in the picker and whose `generic` is drawn 100% of the time anyway.
  Decision 67's finding stands for them: thin is not broken.
- **Several tiers are thin — 1 or 2 names.** Breen, Caitian, Ferengi, Krenim,
  Malon, Suliban, Bajoran and Andorian sit well under vanilla's median of 22.
  The 50/50 draw against a 9-name `generic` softens it to roughly 11 per hull,
  which is why this was left rather than padded.
- **Malon's inherited pools name a TYPE, not a class.** STNH declares
  `Waste Extraction Cruiser`, `Waste Extraction Battleship` and four more, which
  will read as *"Waste Extraction Cruiser – Interceptor"*. They are STNH's own
  content and dropping a source's content to taste is not a call this file
  makes ([decision 11](11-fix-source-errors-dont-drop.md)); the titan fill sits
  alongside them. **Flagged for the next live run.**

## What this does not settle

The same thing decision 67 could not: **whether any of it reads right, which
needs eyes.** Two new things to look at — whether the invented-English registers
sit beside the canon names without sounding like a different mod (`Stormwall`
next to `Bolarus`, `Escrow` next to `Jaglom Shrek`), and whether the Xindi
species names read as class names at all or just as species labels.
