# 20 — Eight minor powers take STNH's species-class key, not a near miss

**Status:** decided, 2026-08-03
**Supersedes nothing.** Extends [decision 10](10-species-class-keys-unprefixed.md)
from *"do not prefix these keys"* to *"do not respell them either."*

## The report

After a live run the user reported that the species class looked wrong for some
empires. `error.log` said nothing about it — this is a silence-failure class, as
CLAUDE.md warns for anything that fails by falling back rather than by being
refused.

## What was actually wrong

A prescripted empire's portraits carry a `clothes_selector`. For most Trek
peoples STNH points that at `humanoid_master_male_clothes_01` /
`humanoid_master_female_clothes_01`, which pick the clothing texture by
`is_species_class = …` and end with

```
default = "gfx/models/portraits/human_civilian/civ_human_male_clothes_01.dds"
```

STG declared its 79 minor powers with keys of its own invention. Eight of them
are peoples the master selectors already gate on, under a *slightly different
spelling*:

| Empire | STG's key | STNH's key | art folder the selector gates |
|---|---|---|---|
| `stg_minor_benzarian_commonwealth` | `BENZ` | `BEN`  | `benzite` |
| `stg_minor_denobulan_unity`        | `DENO` | `DEN`  | `denobulan` |
| `stg_minor_hydran_kingdom`         | `HYD`  | `HYDR` | `hydran` |
| `stg_minor_kessok_heliolatry`      | `KESS` | `KES`  | `kessok` |
| `stg_minor_nygean_sector_authority`| `NYGE` | `NYG`  | `nygean` |
| `stg_minor_tellarian_technocracy`  | `TELL` | `TEL`  | `tellarite civilian` |
| `stg_minor_turei_commonwealth`     | `TURE` | `TUR`  | `turei` |
| `stg_minor_vau_nakat_order`        | `VAUN` | `VAU`  | `vau_nakat` |

A near miss is not a partial match. The selector never names `BENZ`, so a
Benzite fell through to `default` and wore **human civilian clothes** — with the
Benzite head and body still rendering above them. That is what "the species
class was wrong" looked like on screen.

The same eight keys were sitting in `vendor.yml`'s `dangling_identifier_ack`
under the heading *"species classes for Trek peoples STG does not ship yet"*.
STG had been shipping all eight since the minor-power harvest
([decision 19](19-stnh-minor-powers-as-ai-empires.md)); nobody reconciled the
two lists. Three of the entries were even annotated `# Benzite`, `# Denobulan`,
`# Tellarite`.

## Decision

The eight keys are renamed to STNH's spelling, in
`src/common/species_classes/stg_species_classes.txt` and
`src/prescripted_countries/stg_z_minor_powers.txt`, and removed from
`dangling_identifier_ack`. Nothing else in `src/` referenced them.

Decision 10's reasoning applies unchanged: **the art names the key, so the art
chooses the key.** The only new part is that this binds the exact string, and a
key that is merely *close* buys nothing at all — there is no partial credit in
`is_species_class`.

## What was deliberately not renamed

`ORN` and `KOBL` stay acked. They read as Orion and Kobali, and STG ships both
peoples (`ORI`, `KOB`) — but the master selectors gate **haakonian** art on
`ORN` and **axanari** art on `KOBL`. Renaming to match the name would dress
Orions and Kobali in another species' clothes: worse than the fallback, and
harder to spot.

Nine further empires reach the master selector with a class it does not name.
Four are correct as they stand and are acked in `vendor.yml` under
`portrait_clothes_ack`: `TER` and `CON` wear human art and `DELT` and `ELAU`
generic `human_02` art, so the selector's human-civilian `default` is already
the right answer and a class would change nothing.

The other five stay un-acked and are reported every run, because each is a
missing-content finding rather than a settled exception:

- `MONE` (Monean) and `PARA` (Paradan) have their own art folders and no
  clothing entry anywhere in the selectors. Phase 2.
- `KRI` (Krios) is on `kriosian` art, which STNH gates on **two** classes,
  `MIZ` and `XAH`. Renaming needs someone to decide which, so it is not a
  mechanical fix.
- `VALT` (Valtese, on Trill art) and `TNG` (Coalition of Hope, on Vulcan art)
  *could* be pointed at `TRI` and `VUL`, but that makes them literally Trill and
  Vulcan for every other class-gated rule in the build — a content decision,
  left open.

## Predicted cost change

The eight classes are referenced by the master selectors 110 times in the
2026-08-03 log (`TEL` 22, `DEN` 18, `NYG` 18, `VAU` 16, `BEN` 13, `HYDR` 8,
`TUR` 8, `KES` 7), all as
`parser_deferred_database_objects.cpp:84 Failed to deferred read key reference`.
Declaring them resolves every one. The load window should go **3,292 → 3,182**,
with the whole change inside group B/B′ (549 → 439).

**The clothing itself is a silence failure and the log cannot confirm it.**
Zero records is consistent with the selectors working and with them still
returning the default. Only the user's eyes in game settle that — look at a
Tellarite or Benzite leader portrait and check they are not in a human civilian
jacket.

## How this class of defect gets caught next time

`make validate` already checks that a prescripted empire's class has a
`common/portrait_sets/` entry, but skips empires that are `playable = stg_never`
— correct for the designer, and exactly why all 79 minor powers were invisible
to it. The missing check is a different question, and does not care about
playability: *for each prescripted empire, resolve its portrait group to the
`clothes_selector` its members use; if that selector gates on `is_species_class`
and never names the empire's class, the species wears the selector's
`default`.* That is `check_portrait_clothes_selectors`, added with this change.

Calibrated the way `check_prescripted_empires` was: reverting the eight renames
makes it report exactly seventeen findings — the nine above plus those eight,
and nothing else. No false positives, no misses.
