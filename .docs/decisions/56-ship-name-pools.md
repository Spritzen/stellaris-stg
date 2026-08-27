# 56 — STNH's ship registries, folded onto vanilla's ship sizes

**Status:** decided, 2026-08-08
**Phase 4.** The user's suspicion from the live run was exactly right: *"I
suspect that the name pools for each class might not have come across from
STNH."* They had not.

## The measurement

| | lists | `ship_names` tokens | median per list |
|---|---|---|---|
| STG, before | 92 | 6,093 | 62 |
| vanilla | 71 | — | 116 |
| STNH | 150 | 38,707 | 46 |

STG's pools were hand-written from scratch in Phase 1 and never revisited: five
or six names per class per empire, so the Federation fielded five cruisers named
Constellation, Galaxy, Nebula, Ambassador and Akira and then started repeating.

## Why they could not be copied

STNH replaced vanilla's ship sizes with its own single-slot hull ladder, so its
pools are keyed by **hull**, not by class:

```
fed_heavy_cruiser_nebula     96 names
fed_heavy_escort_defiant     91
fed_explorer_new_orleans    118
kdf_battlecruiser_vorcha    119
rom_sword_scimitar           43
```

STG flies a vanilla chassis ([decision 17](17-walshicus-shipsets-replace-stnh-hulls.md)),
so not one of those keys exists here. Copied verbatim they would be 206 pools
the engine never asks for — present, parsed, and silently unused. They have to
be **folded** onto `corvette` / `destroyer` / `cruiser` / `battleship` / `titan`
by tonnage, and that is a judgement rather than a lookup.

The second half is localisation. STNH's tokens are its own loc keys
(`HUMAN_SHIP_Nebula`), and STG does not vendor STNH's `localisation/` — so the
*values* have to be harvested too and re-emitted in STG's flat `STG_N_`
namespace. Every name token is a loc key (plan.md §6, Phase 1); a token with no
key draws as itself.

## Decision

`tools/gen_ship_names.py`, a one-shot in the shape of `gen_star_names.py`:
reads `.source/688086068/`, never the built tree; rewrites the `ship_names`
block of each `src/common/name_lists/stg_*.txt`; writes
`src/localisation/english/stg_ship_names_l_english.yml`.

**88 of 92 lists rewritten, 9,951 new name keys, 6,093 → 32,805 tokens**
(median 62 → 85; the Federation 59 → 5,978).

Four decisions inside it are the ones worth knowing:

- **The tonnage table is written out, and an unmapped key is a build error.**
  All 206 of STNH's distinct pool keys must match a rule or the script stops
  naming the key — because a key with no rule is a whole registry dropped in
  silence, which is the failure mode this file exists to prevent. Rules match as
  substrings, longest first, so `fed_adv_heavy_cruiser_inquiry` takes
  `adv_heavy_cruiser` and not `heavy_cruiser`.
- **The pools are a UNION, not a replacement.** STG's hand-written names stay,
  so Enterprise, Voyager and Defiant survive a harvest that does not happen to
  contain them, and they stay first in the list.
- **The key alphabet is the engine's, and it is narrower than the names.** A
  name-list token is `[A-Za-z][A-Za-z_0-9-]*` — vanilla's own alphabet, which is
  what `check_name_lists` reads. STNH's registries carry `Hammarskjöld`,
  `Auñón-Chancellor` and `Temba, at rest`; a key spelling any of those verbatim
  **ends the token early**, so `STG_N_Hammarskjöld` becomes `STG_N_Hammarskj`
  plus a stray `ld`, and both draw as themselves. Keys are NFKD-folded to ASCII
  and stripped to that alphabet; the *value* keeps every character. This was not
  theoretical — the first run shipped it and `check_name_lists` caught 62
  errors across 5 files.
- **Where a key already exists, STG's spelling wins.** One flat namespace means
  `Bok'Nor` (STG) and `Bok Nor` (STNH) are one key. STG's is the deliberate
  one — `stg_names_l_english.yml`'s header records that whole family as
  apostrophes recovered from tokens that spelled a space and an apostrophe
  identically — so a collision keeps the existing value and is counted, not
  silent.

Decision 45's rule is enforced on the way in: a harvested value that is still a
loc key, or that carries `§` markup or a `$` substitution, is not a name and is
skipped. 29 STNH tokens were dropped that way.

## The four lists left alone

`bolian`, `breen`, `bajoran` and `andorian` have no STNH name list of their own.
Taking a neighbour's would put Federation or Klingon registries in their fleets,
which is worse than a thin pool, so they keep their hand-written names.

## Still open — `ship_class_names`

The other half of the user's question, and the one the class name in
"Nebula – Interceptor" comes from. STG ships ten hand-written class names per
list under `generic`; STNH's hull-class **key suffixes** are the right source
(`fed_heavy_cruiser_nebula` → Nebula, `fed_heavy_escort_defiant` → Defiant), but
the suffix alone loses the spelling — `fed_light_cruiser_t_pol` is `T'Pol` and
`fed_explorer_kiri_kin_tha` is `Kiri-kin-tha`. STNH's ship-size loc is no help
(`fed_heavy_cruiser_nebula:0 "Heavy Cruiser V"`), and its `TECH_UNLOCK_*_TITLE`
strings carry the real class names (`"K't'inga Battlecruiser"`) under a key
scheme that does not match the pool keys — 0 of 192 by direct lookup. A fuzzy
join is the next step and it is a separate piece of work.
