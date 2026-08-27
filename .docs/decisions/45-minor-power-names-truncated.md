# 45 — 78 of 79 minor-power names shipped truncated, and 16 loc keys shipped as text

**Status:** decided, 2026-08-08. Repaired: 100 values across
`src/localisation/english/stg_minor_powers_l_english.yml`, and
`check_prescripted_loc` added so it cannot recur silently.
**Found by** the 2026-08-07 clothes-selector work
([decision 44](44-coalition-of-hope-takes-vul.md)), which needed the Coalition
of Hope's loc for an unrelated reason and found it read `"of Hope (2300s)"`.

## The report

`STG_EMPIRE_minor_confederation_earth:0 "of Earth"`. Not a typo — the same
damage sits on 78 of the 79 minor powers, and the survivors show the mechanism:

| source | shipped |
|---|---|
| `NAME_Confederation_of_Earth` "Confederation of Earth" | `of Earth` |
| `NAME_elaurian_auditorium` "El-Aurian Auditorium" | `-Aurian Auditorium` |
| `NAME_trogoran_empire` "T'Rogoran Empire" | `'Rogoran Empire` |
| `NAME_hurq_stagnancy` "Hur'Q Stagnancy" | `'Q Stagnancy` |
| `EMPIRE_DESIGN_KinshayaHolyOrder` "Holy Order of the Kinshaya" | `Order of the Kinshaya` |
| `EMPIRE_DESIGN_CravicImperative` "Cravic Imperative" | `CravicImperative` |

Whatever generated the file dropped the leading token **without handling the
separator**, so `El-Aurian` lost `El` and kept the hyphen, `Hur'Q` lost `Hur`
and kept the apostrophe. Most names came out as a bare government noun —
`Sovereignty`, `Commonwealth`, `Houses`, `Hegemony` — which reads like a
deliberate short form and is why it survived every review to date. It did not
survive being compared against the source.

Separately, **16 values were the loc key itself**, drawn on screen verbatim:
`STG_species_adjective_minor_tng_coalition_hope:0
"PRESCRIPTED_species_adjective_VulcanHighCommand"`.

**Nothing logs any of this.** Loc that resolves to the wrong string still
resolves; `make validate` was clean through every run on record, because no
check had ever compared STG's converted loc against the thing it was converted
from. This is decision 19's failure class — a silence failure in loc — one layer
further out.

## Getting the right answer was harder than it looks, and two attempts were wrong

**The mapping is exact.** All 79 `stg_minor_<slug>` keys match an STNH
prescripted empire by CamelCase — `acamarian_sovereignty` → `AcamarianSovereignty`
— 79/79, no fuzzy matching anywhere.

Two bugs in the repair pass, both worth recording because both produced
*confident wrong answers* rather than failures:

- **A block-wide `^\s*name\s*=` regex is not the empire's name.**
  `CravicImperative` has no top-level `name`, so the regex found
  `species.name = "Cravic"` and the repair would have renamed the empire from
  `CravicImperative` to `Cravic` — replacing one wrong name with another, and
  looking plausible on the diff. Fixed by parsing the block and reading depth 1
  only. This is decision 31's lesson exactly: finding a name is not the same
  problem as finding *the right* name.
- **Not every literal that matches a loc key is a loc key.** Resolving each
  field by "is this token in the source loc?" turned the ship prefixes `SKR`,
  `TLS` and `VAU` into **"Humanoid"** and `VS` into `vs`, because those are also
  species-class loc keys. Only a loc-key-*shaped* token
  (`PRESCRIPTED_|NAME_|EMPIRE_DESIGN_`) is treated as a key now. The converse of
  decision 30's trap: there, refusing to read a quoted form deleted a real
  reference; here, reading a bare form created a false one.

Both were caught by reading the diff rather than trusting the count. A pass that
reported "103 repairs" was wrong in 7 of them.

## What was repaired, and what was deliberately not

100 values, in three classes:

| class | n | rule |
|---|---|---|
| truncated empire name | 78 | ours is a proper substring of the source's, or the source's minus spaces |
| value is a raw loc key | 16 | matches `^(PRESCRIPTED\|NAME\|EMPIRE_DESIGN)_\w+$` |
| species field built from the broken empire name | 6 | ours == the broken name (± `s`) **and** the real species word differs |

Every one of the 78 is a **clean truncation** — checked, 0 exceptions. That is
the evidence the repair is a restoration and not a rewrite: if the generator had
been paraphrasing rather than truncating, some of the 78 would not be substrings.

**Six values were left alone**, and the boundary matters more than the count:

```
STG_adjective_minor_cravic_imperative        'Cravic'    (STNH: 'Cravics')
STG_species_plural_minor_kessok_heliolatry   'Kessoks'   (STNH: 'Kessok')
STG_species_plural_minor_kzinti_empire       'Kzintis'   (STNH: 'Kzinti')
STG_species_plural_minor_oschean_hunters     'Oscheans'  (STNH: 'Oschean')
STG_species_adjective_minor_oschean_hunters  'Oschean'   (STNH: 'Oscheani')
STG_species_plural_minor_undine_vanguard     'Undines'   (STNH: 'Undine')
```

These are **not damage**. STNH's plural genuinely differs from ours and ours is
ordinary English; three of them were nearly repaired anyway because the broken
empire name happened to equal the species word, so `Kessoks` looked like
"the broken name plus s". The rule was tightened to require that the real
species word *differ* from the broken name, which is what separates a derived
field from a coincidence. **The repair's job was to undo breakage, not to
impose the source's taste** — and a repair that quietly does the second is
indistinguishable from the first on a diff.

## The check

`check_prescripted_loc` asks both questions against `.source/`, resolving STNH's
workshop id out of `vendor.yml` rather than hardcoding it.

Truncation is asked as *"is ours a proper substring of the source's?"* rather
than by re-deriving the name. Deliberately narrow: it cannot fire on a name STG
shortened on purpose unless the shortening is also a substring, and it is silent
on the six taste differences above — a check that reported those would be
reporting a preference, and would have been acked into uselessness within a
week.

**Calibrated in both directions**, per decision 28 — and this is the part
decision 41 got wrong by measuring something both hypotheses predicted:

- On the repaired file: **0 findings.**
- With five of the shipped defects re-introduced verbatim — one of each shape:
  bare noun (`Sovereignty`), lost-separator hyphen (`-Aurian Auditorium`), lost
  separator apostrophe (`'Q Stagnancy`), leading preposition (`of Earth`), and a
  raw key — **5 findings, one per defect, no false positives.**

The second half is the one that matters. The check was written against a file
that had already been repaired, so "0 findings" on its own is exactly what a
check that cannot fire also reports — the `check_vanilla_regression` failure in
decision 31's second paragraph. Re-breaking the file is the only thing that
distinguishes them.

## What this does not cover

Only `stg_minor_powers`. `stg_frontier_powers.txt`, `stg_major_powers.txt` and
`stg_quadrant_powers.txt` were converted from the same source by the same hand
and have **not** been swept — their names read plausibly, which is precisely
what these 78 did. The check is scoped to the file whose damage was measured
rather than widened on the assumption the others are the same shape; widening it
is a piece of work with its own calibration, not a one-line constant change.
That is decision 44's scope rule, applied to the file where someone will
reasonably want to widen it.
