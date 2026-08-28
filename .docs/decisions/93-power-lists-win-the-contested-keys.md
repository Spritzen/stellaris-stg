# 93 — The hand-written power list wins all three contested name-list keys, and the converted duplicates are deleted

**Status:** decided, 2026-08-28 — the content call
[decision 91](91-src-contests-its-own-name-lists.md) left open, made by the
maintainer and applied. **`make validate` is back to 0 warnings.**
**Completes** [decision 91](91-src-contests-its-own-name-lists.md), whose finding
and check are unchanged by this.
**Corrects a measurement in** [decision 68](68-class-name-thematic-fill.md)'s
tier coverage, recorded below.

## The call

`STG_CAITIAN`, `STG_KLINGON` and `STG_VULCAN` were each declared by two files we
wrote — a hand-written power list and an STNH-converted minor list — so one of
each pair never reached the game and **filename sort decided which**, giving a
different answer for Caitian and Klingon than for Vulcan.

**Keep the power list; drop the converted duplicate.** Decision 91's first
option, taken for all three rather than split. Deleted:

```
src/common/name_lists/stg_minor_caitian.txt
src/common/name_lists/stg_minor_klingon.txt
src/common/name_lists/stg_minor_vulcan.txt
```

`src/common/name_lists/` now ships **89 files declaring 89 keys** — one file,
one key, and the first time that has been true.

## Why the power list, and why not the fold

The hand-written files are the ones decisions [56](56-ship-name-pools.md),
[67](67-ship-class-names.md) and [68](68-class-name-thematic-fill.md) built the
**tonnage ladder** into. The converted files' own headers say what they are:
STNH's tokens, re-bucketed for vanilla's ladder because "STNH's file buckets by
its own (saber, sovereign, steamrunner) and those keys mean nothing here". Both
sides are honest work; only one side is the side three decisions were written
against.

**The fold was available and was not taken**, which cost the 47 Caitian, 43
Klingon and 17 Vulcan tokens unique to the converted side. For Klingon and Vulcan
that is a small loss out of a shared vocabulary — the two sides overlap 87% and
97%. For **Caitian it is the whole point**: `stg_caitian.txt`'s header says its
names are "constructed to a consistent feline phonology", and
`stg_minor_caitian.txt` is STNH's *Kilrathi* vocabulary — Dralthi, Salthi,
Gratha, Jalthi. Folding those together would have undone a deliberate voice to
save 47 tokens.

**Nothing references a deleted file.** Every consumer names the *key*: two
prescripted powers (`stg_major_powers.txt`, `stg_frontier_powers.txt`), the
Kzinti Empire in `stg_z_minor_powers.txt`, and six `namelist`/`name_list`
lines in `stg_home_systems.txt`. All six now resolve to the surviving file, which
is the file the majors were always meant to get.

## What it cost, measured rather than assumed

**Five localisation keys, and not the ~107 the token counts suggest.**
`gen_ship_names.py` and `gen_ship_class_names.py` rewrite the `ship_names` and
`ship_class_names` pools of whatever name lists exist and emit the loc for them,
so re-running both after the deletion is what says how much was really only in
the converted files:

| file | keys lost |
|---|---|
| `stg_ship_class_names_l_english.yml` | 4 |
| `stg_ship_names_l_english.yml` | 1 (`STG_N_WahsHiqus`, "Wah'sHiqus") |

The rest of the "unique" tokens were unique to that *file* and not to the
tree — they are still spelled once in `stg_names_l_english.yml`, the one flat
`STG_N_` namespace, and other lists still draw them. **The token-count diff
overstated the loss by a factor of twenty**, and the only reason we know is
that the generators were re-run instead of the counts being trusted.

## The measurement this settles

[Open questions](../planning/open-questions.md) has carried, since 2026-08-22,
*"21 of the 22 majors, quadrant and frontier powers now carry all five core
tiers — the gap is Caitian, which has no `titan` block"*. Decision 91 put that
back in doubt, because it was measured against `stg_minor_caitian.txt` while
`stg_caitian.txt` carries all five.

**With the minor file gone there is only one reading left, and it is the good
one: all 22 carry all five core tiers.** The Caitian titan exception is
withdrawn — a Caitian titan now draws a Caitian class name, not a `generic` one,
and there is no longer an empire where a tonnage-mismatched class name is
expected rather than a defect.

## The thing worth carrying forward

**A contested key does not only hide a name — it hides a measurement, and the
measurement outlives the defect.** The Caitian `titan` gap was written down,
cited, and used to excuse an expected in-game oddity for six days, and it was
never true of the file anybody intended to ship. Decision 91 caught it because
the check named *both* files; nothing else in the project would have.
