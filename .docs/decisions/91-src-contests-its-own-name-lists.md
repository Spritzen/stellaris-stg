# 91 — Three name lists are declared twice by files we wrote, and the key-conflict check could never have seen it

**Status:** decided, 2026-08-28 — the check and the finding are settled.
**The content call this left open was made the same day and is
[decision 93](93-power-lists-win-the-contested-keys.md)**: the hand-written power
list wins all three, and the converted duplicates are deleted. The text below
stands as it was written, including the sentence saying the call is open.
**Follows** [decision 27](27-merge-semantics-per-directory.md), whose per-directory
merge table this uses and, in one entry, corrects.
**Corrects** the premise that `common/name_lists` is a database where the file is
the unit — see "The key is the identifier" below.
**One figure below is corrected by**
[decision 96](96-section-slots-survive-a-replacement.md): the vanilla floor for
`common/name_lists` is **80 keys in 76 files**, not 78 — the check's own
`^key = {` regex could not see `LITH1.txt` and `LITH2.txt`, which indent
`LITHOID1` and `LITHOID2`. The verdict is unchanged in both directions: still 0
contested, still the same fourteen databases asked. The text below stands as it
was written.

## The finding

`src/common/name_lists/` ships **92 files declaring 89 distinct keys**. Three keys
are declared twice, by two files we wrote ourselves:

| key | hand-written power list | STNH-converted minor list | wins under LIOS |
|---|---|---|---|
| `STG_CAITIAN` | `stg_caitian.txt` — 107 tokens, all five core class tiers | `stg_minor_caitian.txt` — 94 tokens, **no `titan`** | `stg_minor_caitian.txt` |
| `STG_KLINGON` | `stg_klingon.txt` — 701 tokens | `stg_minor_klingon.txt` — 690 tokens | `stg_minor_klingon.txt` |
| `STG_VULCAN` | `stg_vulcan.txt` — 2,507 tokens | `stg_minor_vulcan.txt` — 2,460 tokens | `stg_vulcan.txt` |

**One of each pair never reaches the game**, and which one is decided by filename
sort rather than by anybody's intent — which is why the answer is not even
consistent across the three: the minor list wins twice and the power list once.

**Two of the three are major powers** — the Klingon Empire and the Confederacy of
Vulcan, of the five in `stg_major_powers.txt`. The third, the Caitian Union, is a
frontier power. These are the most-played empires in the mod.

The overlap is heavy but not total: Caitian shares 47 tokens with 60 and 47
unique to either side, Klingon 647 shared with 54 and 43, Vulcan 2,443 shared
with 64 and 17. So this is not one list saved twice — each side carries names the
other does not.

**Nothing else is contested.** The sweep is the whole of `src/common/`: 772
identifiers over 16 databases, and these three are the only ones claimed twice.

## Why no check could see it

`check_key_conflicts` has asked the right question about the wrong population
since it was written. Its gate is

```python
multi = len({s for s in mods.values()}) > 1 and len(mods) > 1
```

— **two distinct *sources***. Every file in `src/` carries the same source, so a
key `src/` contests with itself can never satisfy it. The check was examining
`common/name_lists`, counting it in its 506 files, and structurally incapable of
reporting these three. That is
[rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)
in the same shape it has taken twice before: **a check that cannot fail is worse
than an absent one, because it reports a number.**

## The key is the identifier, whatever `WHOLE_TEXT_DIRS` says

`common/name_lists` sits in `WHOLE_TEXT_DIRS` in `tools/validate.py` — the table
of databases where "a FILE is the unit and no key-level merge happens: the id is
the filename". **Vanilla falsifies that in its own tree.**

- **19 of vanilla's 76 name-list files declare a key that is not their filename.**
  `AQU1.txt` declares `AQUATIC1`; `Graygoo.txt` declares `graygoo`;
  `LITH3.txt` declares `LITHOID3`.
- **`28_biogenesis.txt` declares two keys**, `default` and `bio_ship`.

A prescripted country writes `name_list = "STG_KLINGON"` and the engine resolves
**the key**. So two files claiming one key contest it however they are named, and
the filename is not the id.

**The table is left as written.** `check_key_conflicts` is calibrated against it
and editing it would move that check's behaviour for a reason that belongs to a
different check. The correction is recorded here instead, and the new check does
not consult it.

## The check

`check_src_key_contention`, new in `tools/validate.py`: **two files we wrote
declaring one identifier, in a database vanilla never contests.**

**Its scope is `src/`, and that is a calibration result**
([rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter)).
Build-wide, exactly **16** keys are contested by two files of a single source.
**13 belong to source mods and are their own design** — Planetary Diversity's
`zzz_`-prefixed decision overrides, and `common/inline_scripts/` fragments, where
the depth-0 key is a chunk of script rather than a name. Second-guessing those is
what [decision 11](11-fix-source-errors-dont-drop.md) forbids. The remaining 3
are ours, and `src/` is the one source whose every file we chose.

**Its database gate is read out of vanilla at run time**
([rule 4](../validation/check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand)),
not hand-listed: a database is asked about only if vanilla contests no identifier
in it. Over the 16 databases `src/` writes into, vanilla's count is **0 in
fourteen** — `common/name_lists` among them, **0 across 78 keys in 76 files** —
and non-zero in exactly two, `common/static_modifiers` (7) and `common/traits`
(1), which are therefore not asked. A game patch that makes vanilla start
contesting a database silently stops us asking about it, which is the right
direction for this one to fail.

**`make validate` now reports 3 warnings rather than 0**, and that is the check
working. It is the first time the tree has not been clean since the warning
triage of 2026-08-07, and it stays that way until the content call below is made.

## What is open: which of each pair to keep

**This is a content call and it is not made here.** Both files in each pair are
ours, so the choice is not "confirm the merge" — it is one list to keep and one
to fold in or drop, and the two options cost differently:

- **Keep the power list, drop the converted one.** The hand-written files are the
  ones decisions [56](56-ship-name-pools.md), [67](67-ship-class-names.md) and
  [68](68-class-name-thematic-fill.md) built the tonnage ladder into, and
  `stg_caitian.txt`'s header says its names are "constructed to a consistent
  feline phonology" — a deliberate voice. Cost: the 47/43/17 tokens unique to the
  converted side. **The Kzinti Empire also names `STG_CAITIAN`** and would simply
  resolve to the surviving file, so nothing breaks.
- **Fold the unique tokens in, then drop.** Loses no names, but
  `stg_minor_caitian.txt` is STNH's Kilrathi vocabulary — Dralthi, Salthi,
  Gratha, Jalthi — beside a hand-built feline phonology, and mixing them is
  precisely the judgement the first option's author was making.

**The recommendation is the first**, with the second reserved for the Klingon and
Vulcan pairs, where both sides are the same vocabulary and the overlap is 87% and
97%. It is not applied without a decision from the maintainer.

## The thing worth carrying forward

**A measurement taken off one of two contested files is a measurement of nothing
in particular**, and one is already in the record: [open
questions](../planning/open-questions.md) states that "21 of the 22 majors,
quadrant and frontier powers now carry all five core tiers — the gap is Caitian,
which has no `titan` block". Measured against `stg_caitian.txt` all 22 carry five;
measured against `stg_minor_caitian.txt` one does not. **Both readings are in the
tree, and until this is resolved neither is the answer.**
