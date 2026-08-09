# 32 — Declare the 34 selector-named species classes; retire the ack

**Status:** decided, 2026-08-07
**Reverses** the acking rationale recorded in `vendor.yml` above
`dangling_identifier_ack`. **Extends**
[decision 10](10-species-class-keys-unprefixed.md),
[20](20-minor-power-species-class-keys.md) and
[21](21-species-class-localisation.md).

## The report

The 2026-08-07 live run threw **439 `parser_deferred_database_objects.cpp:84`
records, 21.8% of `error.log`** — the largest defect class in the file that was
ours:

```
Failed to deferred read key reference AEN from database
  file: gfx/portraits/asset_selectors/humanoid_master_female_clothes_01.txt line: 16
```

34 distinct keys, 220 references from the male master clothes selector, 212 from
the female, 2 from the Klingon selector. Every one is an `is_species_class`
value in vendored STNH clothing art gating a wardrobe branch on a class STG did
not declare.

**33 of the 34 were in `dangling_identifier_ack`.** `make validate` reported
`ok — 12 warning(s)` throughout, and had done for every run since the list was
written.

## Why they were acked, and why that was wrong

The recorded reasoning: these are Phase 2 peoples, "declaring empty classes now
would create species that appear nowhere and have to be rewritten in Phase 2",
and the cost was scored as "confined to load time and shrinking by one species
per Phase 2 addition."

Two parts of that do not survive the run:

**The cost is not confined to load time.** A species whose class does not
resolve falls through to the selector's `default`, which is human civilian
clothing — the same defect `check_portrait_clothes_selectors` reports by name
for KRI, VALT and TNG. The ack was silencing a load-time symptom of a
gameplay-visible failure.

**An ack on a whole class of finding cannot shrink by one.** Nothing decrements
it; the list sat unchanged while the errors recurred every run. This is exactly
what `CLAUDE.md` says an ack does — "an ack entry stays silent forever" — and
the reason it recommends a content comparison instead. Here neither applies: the
finding was real and the fix was cheap.

## Decision

**All 34 are declared.** 30 as new stubs in
`src/common/species_classes/stg_species_classes.txt`, each with the 27-key loc
family decision 21 requires. `dangling_identifier_ack` is now `[]` — kept, empty,
so the next reader finds the note rather than wondering why there is no ack.

**Four were not new classes but misspellings of our own** — decision 20 applied
a second time, and the reason to check every near miss before adding a key:

| STG had | STNH's selectors want | Species |
|---|---|---|
| `DELT` | `DEL` | Deltan |
| `ELAU` | `ELA` | El-Aurian |
| `MONE` | `MON` | Monean |
| `PARA` | `PAR` | Paradan |

Renaming those four also cleared two standing
`check_portrait_clothes_selectors` warnings (MONE, PARA) — the class and the
clothing were always the same people under two spellings.

**Four lookalikes were left alone, because they are different peoples.** This is
the trap: a shared prefix is not evidence of a shared species.

| Selector key | Is not | Because |
|---|---|---|
| `BREK` Brekkian | `BRE` Breen | unrelated; Breen is a major power |
| `KOBL` Kobliad | `KOB` Kobali | selector gates *axanari* art on KOBL |
| `KREE` Kreetassan | `KRE` Krenim | unrelated |
| `KRESS` Kressari | `KRE` Krenim | unrelated |

The previous session had already reasoned this out for ORN (Ornaran, not Orion)
and KOBL in the ack's own comment, and was right; the error was acking them
rather than declaring them.

**`graphical_culture = generic_01` on all 30, and it is inert.** No empire
declares these classes, so nothing resolves ship art through them. A kin culture
is deliberately not guessed — that would assert a relationship the sources do
not state.

**`HOLO` is `archetype = ROBOT`**, modelled on vanilla's own ROBOT class.
Photonic lifeforms are not `BIOLOGICAL` with `trait_organic`, and STNH's own
archetypes live in a `common/species_archetypes/` STG does not vendor, so naming
one drops the class silently.

## The tooling gap that let one through

`HOLO` was the one key of the 34 that **no ack covered, and nothing reported.**
STNH writes it `is_species_class = "HOLO"` — quoted — and three separate checks
read that field with a bare-only `(\w+)`. All three were blind to it.

This is [decision 27](27-quoted-class-keyword.md)'s lesson from the other side.
There, `class = "star"` vs `class = star` changes the *meaning* and normalising
the quotes away deleted the defect. Here the quoting is cosmetic, the engine
attempts the lookup either way, and refusing to read one of the two forms
deleted the *reference*. The two cases look identical in a regex and are
opposite in what they demand:

> **Ask whether a field's written form changes its meaning before deciding
> whether to normalise it.** If it does, keep the form and check it. If it does
> not, accept every form the sources use.

`_SPECIES_CLASS_REF` in `tools/validate.py` now accepts both, and all three call
sites share it. Calibrated by removing `HOLO` from `src/` and the build: found
with the fix (2 references, matching the log exactly), missed without it.
