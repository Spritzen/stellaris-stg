# 92 — Six localisation keys are declared twice by files we wrote, and the Breen home system was asking for the wrong one of two real names

**Status:** decided, 2026-08-28 — **the finding is fixed and the check holds it
at zero.** No content call, no live run.
**Follows** [decision 91](91-src-contests-its-own-name-lists.md), which is the
same hole one directory over, and was found by asking where else its shape
could hide.
**Corrects** [decision 23](23-real-home-systems.md)'s generator for the fourth
time, after the three [decision 79](79-shipset-descs-and-home-system-names.md)
found.

## Where this came from

Decision 91 ended on a sentence rather than on a fix: `check_key_conflicts`
gates on two *sources*, so `src/` contesting itself is invisible to it, and
`check_src_key_contention` was written to close that for `src/common/`.

**The obvious next question is whether `src/common/` is the only place `src/`
can contest itself, and it is not.** `src/localisation/` has the identical
shape and was covered by neither check:

- `check_key_conflicts` walks `stg-build/common/` only, so it never sees a
  `.yml` at all;
- `check_localisation` reads each file **alone** — BOM, language tag, entry
  syntax — so it has no idea another file of ours already spelled the key.

## The finding

`src/localisation/` ships **18 files declaring 23,624 keys**. Six are declared
by two files of ours, and **one of the six disagrees with itself**:

| key | `stg_home_systems_l_english.yml` | `stg_names_l_english.yml` |
|---|---|---|
| **`STG_N_Portas`** | **"Portas V"** | **"Portas"** |
| `STG_N_BolarusIII` | "Bolarus III" | "Bolarus III" |
| `STG_N_BolarusVII` | "Bolarus VII" | "Bolarus VII" |
| `STG_N_Clarus` | "Clarus" | "Clarus" |
| `STG_N_Dozaria` | "Dozaria" | "Dozaria" |
| `STG_N_YridiaIV` | "Yridia IV" | "Yridia IV" |

The five twins cost only their own lines. **The sixth is a defect the player can
see**, and the shape of it is worth more than the fix.

### Both readings of Portas are real, and the initializer asked for the wrong one

`src/common/name_lists/stg_breen.txt` already carries **two separate keys**,
because the Breen use the name in two places:

```
colonizer = { STG_N_NewBreen STG_N_Portas  STG_N_Dozaria … }   # a ship: "Portas"
planet_names = { … STG_N_PortasV STG_N_Dozaria … }             # a world: "Portas V"
```

`tools/gen_home_systems.py`'s authored Breen block placed the frozen third body
as `name = "STG_N_Portas"` — the **ship's** key — and then
`stg_home_systems_l_english.yml` redeclared that key as `"Portas V"` to get the
name it actually wanted. So one of the two rendered wrong and **filename sort
decided which**: `stg_home_systems_…` sorts before `stg_names_…`, so on the
usual last-wins reading the name file wins, the Breen home system's third planet
draws as **"Portas"**, and the redeclaration is dead weight. Had the other file
won, every Breen colony ship would have launched named **"Portas V"**.

**Neither outcome is what anybody wrote.** The key that means what the
initializer wanted already existed, three lines away in a file the same
generator reads.

## The fix

One key, in the generator, because the file is generated:

```diff
-\tplanet = { name = "STG_N_Portas"  class = "pc_frozen" … }
+\tplanet = { name = "STG_N_PortasV" class = "pc_frozen" … }
```

and all six declarations removed from `stg_home_systems_l_english.yml`, whose
header now carries the rule: **a name already in `stg_names_l_english.yml` is
not repeated here.** That file is the one flat `STG_N_` namespace by design —
its own header says so — and the home-systems file exists for the keys that
namespace has no reason to hold.

**One thing checked before making it, and it is why the fix is only the key.**
"Portas V" is now both a home-system body and a token in the Breen colony pool.
That is not a new problem and not worth singling out: **16 home-system body
names across 11 empires are already offered by their own empire's colony pool**
— Remus, Praxis, T'Khut, Jeraddo, Hobus among them. Whether a Breen colony
called Praxis is wrong is a real question, but it is a *content* question about
all 16, not about this one, and `check_colony_name_collisions` deliberately asks
only about **capitals**. Left as it is.

## The check

`check_src_loc_key_contention`, new in `tools/validate.py`. Three reports: a key
declared by two files of ours whose values **differ**, a key declared twice with
the **same** value, and a key repeated **inside one file**.

**A same-value duplicate is reported on purpose.** It costs nothing at runtime,
and that is exactly the state the disagreeing one hid in — five harmless twins
are the reason nobody ever looked at the sixth.

**The floor is the strongest in the file.** Vanilla declares **148,053 keys
across 231 english files, contests none of them, and repeats no key inside a
file.** Nothing here is a judgement about how much duplication is normal: the
answer is none.

**The scope is `src/`, and it is a calibration result**
([rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter)).
Build-wide, **16** keys are declared twice by two files of one source — the same
number decision 91 met, and split the same way:

| | keys | values differ | verdict |
|---|---|---|---|
| **Real Space 4.0** | 10 | 0 | `realspace_l_english.yml` against `realspace_replace_l_english.yml` — a base/replace pair, every value identical. Its own design, and [decision 11](11-fix-source-errors-dont-drop.md) forbids second-guessing it |
| **`src/`** | 6 | 1 | ours, and the subject of this decision |

A further **41 keys are contested across sources**, of which **8 differ** — and
all 8 are Planetary Diversity overriding itself through its own extensions
(`!_ow_l_english.yml`, `planetarydiversity_aw_*`). That is the "extension wins"
family case [decision 27](27-merge-semantics-per-directory.md) settles, and it
is `check_key_conflicts`' question rather than this one's. **`check_key_conflicts`
cannot currently ask it either, because it walks `common/` only** — recorded
here, not fixed here: widening it needs the family acks in `vendor.yml` extended
to localisation, and PD's 8 are the only differing case in the tree.

**The language gate is derived from vanilla at run time**
([rule 4](../validation/check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand)):
a language folder is asked about only if vanilla contests nothing in its own
copy of it. A game patch that ships a duplicate silently stops us asking about
that language, which is the right direction to fail.

**Calibrated by reverting the repair.** With `STG_N_Portas` put back, and
`STG_N_Dozaria` doubled inside one file, all three reports fire and name the
files, the key and both values.

## The thing worth carrying forward

**Decision 91's lesson has a second half.** 91 said a check that gates on the
wrong noun reports a number while seeing nothing. This says: **when you fix
that, ask where else the same gate is wrong.** `src/` contests itself in
`common/` and in `localisation/`; one check was written for the first and the
second was sitting a directory away, holding a defect for as long as the home
systems have existed.

And a smaller one, which is [decision 79](79-shipset-descs-and-home-system-names.md)'s
lesson again: **`gen_home_systems.py` has now been wrong four times about body
names, and every time the wrongness was invisible in the file it writes.** A
generated file reads as authoritative. It is only as good as the check pointed
at it.
