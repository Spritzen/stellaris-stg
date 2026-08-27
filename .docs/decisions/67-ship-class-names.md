# 67 — STNH declares its own class names, so decision 56's fuzzy join was never needed

**Status:** decided, 2026-08-09
**Follows / closes the open half of** [decision 56](56-ship-name-pools.md).
**Uses** [decision 45](45-minor-power-names-truncated.md)'s rule on the way in.

## What was open

Decision 56 folded STNH's ship *registries* onto vanilla's ship sizes and left
`ship_class_names` — the "Nebula" in *Nebula – Interceptor* — explicitly open. It
had looked for a source and reported the search as failed:

> STNH's hull-class **key suffixes** are the right source
> (`fed_heavy_cruiser_nebula` → Nebula), but the suffix alone loses the
> spelling — `fed_light_cruiser_t_pol` is `T'Pol`. […] its `TECH_UNLOCK_*_TITLE`
> strings carry the real class names under a key scheme that does not match the
> pool keys — 0 of 192 by direct lookup. **A fuzzy join is the next step.**

STG shipped ten hand-written class names per list, all under `generic`.

## The finding

**STNH's name lists carry a `ship_class_names` block of their own**, keyed by the
same hull vocabulary as `ship_names` and holding one loc token per hull:

```
fed_heavy_cruiser_nebula = { HUMAN_CLASS_Nebula }     -> "Nebula"
kdf_battlecruiser_vorcha = { KLINGON_CLASS_Vorcha }   -> "Vor'cha"
fed_light_cruiser_t_pol  = { ANDORIAN_CLASS_Tpol }    -> "T'Pol"
```

57 of STNH's 169 lists have one, and between them they declare **165 of the 177
Trek hull keys** any registry uses. The 12 left over are swarm hulls and
vanilla's own starbase tiers (`starbase_citadel`, `starbase_outpost`) — a station
tier, not a class. Decision 56 searched the localisation and never looked at the
name lists it was already parsing.

So the answer is a **direct harvest folded by decision 56's own tonnage table**,
and the spellings the suffix loses are read off the value rather than guessed.

### The join was built first, and deleting it is the result

A suffix-shape join was implemented and measured before being removed, because
the negative result is the useful part. Two things it established:

- Indexed against **any** short localisation value it resolved 176 of 187 hull
  keys — and wrongly: `fed_light_cruiser_curry_type` took `Type` off an
  army-view label, `military_defense_fed_1` took `1`. Restricted to STNH's own
  `*_CLASS_*` namespace it resolved 152 with 3 ambiguities, all of them case.
- Run for real it contributed **nothing**. Across the 90 STNH lists STG maps to
  it had 594 candidates and **every one was shared hull vocabulary rather than a
  class**: STNH's cross-empire hulls are literally named `saber`, `sovereign`
  and `steamrunner`, so deriving from `Klingon.txt`'s `saber = { … }` put
  **Saber, Steamrunner and Sovereign in the Klingon fleet**. Every list that
  flies a shared hull declares its own name for it — `Andorian.txt` says
  `saber = { ANDORIAN_CLASS_Charal }` — and a list that declares nothing
  correctly gets nothing and falls back to `ship_names`, which is what vanilla's
  `README_NAME_LISTS.txt` documents.

## Decision

`tools/gen_ship_class_names.py`, a one-shot in the shape of `gen_ship_names.py`,
importing its tonnage table, list mapping and key alphabet rather than restating
them — **one tonnage judgement in one place, or the two halves of a ship's name
drift apart**. Reads `.source/688086068/`, never the built tree.

**92 lists rewritten, 820 → 1,766 `ship_class_names` tokens, 286 new class keys**
in `src/localisation/english/stg_ship_class_names_l_english.yml`, from 1,176 STNH
declarations. Vanilla, for scale, gives the block to 13 lists at a median of 22.

Three things inside it are the ones worth knowing.

- **`generic` is drawn at ANY tonnage, so a class with a size must leave it.**
  Vanilla's own README: *"If both generic and size-specific names exist, 50%
  chance of using either list."* STG's ten hand-written names all sat in
  `generic`, so once the harvest gave Nebula a `cruiser` pool the name would
  **still** land on a corvette half the time — the exact defect this file exists
  to fix, surviving its own repair. A generic token some size pool now claims is
  demoted out of generic; one no size claims stays, because generic is the only
  place it can be drawn from. **76 demoted, 266 left.**
- **The demotion matches by SHAPE, not by token**, and that is not fussiness.
  STG hand-wrote `STG_N_DDeridex`; STNH declares `D'deridex`. `stg_key` keeps
  case, so an exact match leaves the Romulan warbird in `generic` *and* in
  `battleship` and the 50/50 comes straight back under a capital letter.
- **One class is one key.** The same shape index harmonises STNH with itself:
  `KLINGON_CLASS_BRel` is "B'Rel" and `KLINGON_CLASS_Brel` is "B'rel" — one
  class, two capitalisations, two loc keys, two entries in one fleet's pools.
  Ties break on how often STNH writes each spelling, then alphabetically, so the
  answer never depends on file order. Where STG has already spelled a key, STG's
  spelling wins and is counted, not silent — 2 did.

### The tonnage table grew by 19, and vanilla placed them

`ship_class_names` reaches 19 hulls no registry pool names — the Borg, the
Undine, the fallen empires, the Xindi planet killer, Annorax. They are placed by
**vanilla's own `fleet_slot_size` ladder** (corvette 1, destroyer 2, cruiser 3,
battleship 4, titan 8, juggernaut and colossus 32) read against STNH's value for
each hull, and the value is the comment on every line of the table. `borg_probe`
is 1 and a corvette; `borg_cube`, `super_cube` and `time_ship_annorax` are 32 and
juggernauts. Nothing there is a guess about what a cube feels like. An unmapped
key still stops the build, for decision 56's reason: a key with no rule is a
whole class list dropped in silence.

## Decision 56's exclusion is right for registries and wrong for classes

It leaves `bolian`, `breen`, `bajoran` and `andorian` on hand-written pools
because those STNH lists key their *registries* by Federation hulls, and taking
them would put Starfleet names in a Bajoran fleet. The first cut of this file
inherited that through `stg_sources()` and it cost real content: **three of the
four declare class names of their own for the SHARED hulls**, and they are the
genuine article — Bajor's Perikian, Ornathia, Shabren and Denorios, the Breen's
Plesh Brek and Sarr Thenn, Andoria's Kumari, Charal and Khyzon.

So `CLASS_ONLY` takes the class names while the registries stay excluded, and
the filter is the same lesson as the deleted join in a second costume: **an
empire's own hull does not always say so in the prefix.** `Andorian.txt`
declares `military_defense_fed_2 = { ANDORIAN_CLASS_Danube }` — a Federation
runabout wearing an Andorian key — so matching on the prefix alone would have
walked three Starfleet classes into the Andorian Empire. Rejecting any key with
an empire token in *any* position catches it. **+29 class names; Andorian,
Bajoran and Breen stop being tonnage-agnostic.**

## Where the outside sources run out, and why that is the answer

The gap after the harvest is **five playable empires with no size split at all** —
Bolian, Tholian, Trill, Vidiian, Yridian — plus Xindi at one, and eight lists
with no `titan`. Memory Alpha and Memory Beta were searched for those, in that
order, and **essentially nothing was taken**. The reason is structural rather
than a failure of searching:

- **Canon names no classes for any of them.** These were one-off guest vessels,
  so the wiki has only descriptive types — *Vidiian warship*, *Tholian vessel*,
  *Yridian starship*. A type is not a class name, and "Vidiian warship" in the
  class slot reads worse than what is already there.
- **What STG hand-wrote in Phase 1 is already canon-grounded and better.** The
  Vidiian pool is Dereth, Motura, Sulan, Danara and Honatta — named Vidiians —
  before it reaches its thematic Phage and Harvest. Tholian opens on Loskene and
  Nezhek. Bolian is Bolarus, Bolias, Sappora. Memory Beta's one Bolian offering,
  the Bolarus class, **was already in the pool**.
- **Xindi is the one case canon could have filled and should not.** It supplies
  six species-typed ships — Insectoid, Reptilian, Aquatic, Primate, Arboreal —
  which would fold by tonnage cleanly and then read as *"Insectoid – Interceptor"*
  against the existing *"Dolim – Interceptor"*. Rejected on how it reads.

**A list with no size pools has no defect to fix.** `generic` is drawn 100% of
the time when nothing competes with it, so these five produce a sensible class
name for every hull; they are thin, not broken. The only thing they lack is
tonnage, and no source outside the tree can supply it without inventing.

## What this does not settle

**Whether the classes read right on the right hulls, which only a live run can
say.** The tonnage table is a judgement — decision 56 says so about the
registries and it is no less true here. The way it would be wrong is the same
shape: *a Nebula-class name turning up on a corvette*, now visible in the class
half as well as the name half.

Two things to look at that are new here:

- The **Defiant appears at two tonnages** in the Federation list, from
  `fed_escort_ship_defiant` (destroyer) and `fed_heavy_escort_defiant` (cruiser),
  and the **D7 the same way** for the Klingons (cruiser, and titan via
  `kdf_hero_ship_d7`). Both are STNH modelling one class at two tiers, kept
  rather than reconciled, because picking one would be inventing.
- `UNDINE_CLASS_infestabami` resolves to **`infestabami`** — lowercase, and
  plainly sloppy rather than a name. It is STNH's spelling, it is not a loc key
  so decision 45's rule does not catch it, and the Undine are AI-only, so no log
  will ever mention it. Left as STNH wrote it.
