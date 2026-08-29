# 109 — The fourth quadrant of the contested-key hole was localisation between two sources, and the family filter is the whole check

**Status:** decided, 2026-08-29
**Closes** the item [decision 92](92-src-contests-its-own-loc-keys.md) opened and
did not fix — *"`check_key_conflicts` cannot see a contested localisation key …
worth doing when something else touches that check; not worth doing alone"* —
carried on [open-questions.md](../planning/open-questions.md) since 2026-08-28.
**Completes** the quadrant map begun by
[91](91-src-contests-its-own-name-lists.md),
[92](92-src-contests-its-own-loc-keys.md) and
[94](94-src-contests-its-own-identities.md).
**Refactors** `check_key_conflicts`: the `key_conflict_families` parser is now
`_key_conflict_families()` and both checks call it.

## The hole, stated as a grid

Two questions — *who is contesting*, and *what kind of file* — make four
quadrants. Three had checks; the fourth had never been asked.

| | `common/` blocks | `localisation/` keys |
|---|---|---|
| two files of **ours** | `check_src_key_contention` ([91](91-src-contests-its-own-name-lists.md)) | `check_src_loc_key_contention` ([92](92-src-contests-its-own-loc-keys.md)) |
| two **sources** | `check_key_conflicts` | **nothing** |

`check_key_conflicts` walks `stg-build/common/` and asks its question of
`key = { … }` blocks. **A localisation file has no blocks**, so widening it was
never a matter of adding a directory — the scanner has nothing to scan. That is
the same reason 91 and 92 are two checks rather than one, and the new one is
`check_loc_key_conflicts`, a sibling rather than a parameter.

## Why the question is worth asking at all

**`error.log` records a localisation key that is missing. It records nothing
about a key two files declare**, because both resolve — the engine keeps one and
renders it. That is [decision 45](45-minor-power-names-truncated.md) exactly:
78 of 79 minor powers shipped reading `of Earth` and no log ever said so,
because **loc that resolves to the wrong string still resolves**. With 49
vendored sources and no load order left at runtime, one mod overwriting
another's string is a silent change of content.

## The measurement, and the finding is the filter

Read raw, the merged tree contests **41 keys across sources, and 8 of them
disagree**. All 8 are Planetary Diversity overriding its own placeholders
through its own extensions:

| key | loses | wins |
|---|---|---|
| `origin_pd_aw_tree_of_life` | `Placeholder Origin - DO NOT USE` (PD) | `Megaflora Tree of Life` (PD - Ascension Worlds) |
| `d_pd_confluence_spire_building` | `Placeholder` (PD - Ascension Worlds) | `Confluence Spire` (PD - More Arcologies) |
| `d_pd_confluence_spire_building_desc` | `You should not see this, please report if you do` | the real description |
| `pd_aw_necro_planet` | `Placeholder for OW` (PD) | `Necropolis` (PD - Ascension Worlds) |
| `pd_pelagic_planet_desc`, `pd_wasteland_planet_desc`, `pd_aw_wasteland_planet_desc` | — | the extension's, or its `$…$` indirection |

**Every one resolves to the extension under filename sort**, checked by hand for
each: `planetarydiversity_ascension_worlds_` sorts before
`planetarydiversity_aw_`, `!_ow_` before `planetarydiversity_more_arcologies_`.
This is the *"extension wins, record don't merge"* case
[decision 27](27-merge-semantics-per-directory.md) settles and
[the conflict register](../architecture/conflict-register.md) enumerates — the
same shape that accounts for 75 of `check_key_conflicts`' 88 raw findings.

**So the same `key_conflict_families:` declaration in `vendor.yml` that empties
that check empties this one, and it is read from the same place** — which is
why the parser was extracted rather than copied. Two copies drift, and a family
that quietly stops applying to one of two checks is precisely the silence the
list exists to prevent.

## The check

`check_loc_key_conflicts`, in [validate.py](../../tools/validate.py). A key
declared by **two different sources with values that disagree**, outside a
declared family.

- **Same value, two sources: not reported.** Unlike its `src/` sibling, which
  reports a same-value twin deliberately ([92](92-src-contests-its-own-loc-keys.md):
  *"five harmless twins are why nobody looked at the sixth"*). The reasoning does
  not carry across: a duplicate of **ours** is a file to delete, and a duplicate
  between two **sources** is not ours to delete at all — [decision 11](11-fix-source-errors-dont-drop.md)
  says fix a source's errors, not tidy its design.
- **LIOS, always.** Localisation has no FIOS directory: the engine reads every
  `.yml` and the last filename in sort order wins, so the winner is
  `sorted(files)[-1]` with none of `check_key_conflicts`' directory table
  behind it.
- **The language gate is derived from vanilla at run time**
  ([rule 4](../validation/check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand)),
  the same way as `check_src_loc_key_contention`. It also pays for itself
  immediately: the built tree carries a `localisation/replace/` and a nested
  `localisation/localisation/`, and the gate excludes both for free because
  vanilla ships neither.

**Population 27,742 keys. Floors: vanilla 148,053 keys in 231 english files
contesting none ([92](92-src-contests-its-own-loc-keys.md)), the merged tree 41
contested and 0 across families.**

## Calibration — four controls, and one of them is the interesting one

| state | findings |
|---|---|
| as shipped | **0** |
| **the family filter removed** | **8** — and they are the PD placeholders above, by name |
| a key injected into two sources of **different** families, values differing | **1**, naming both files, both sources and the winner |
| the same injection with **identical** values | **0** |

**The first injection was wrong and reported clean.** It picked the two sources
with the most localisation files, which turned out to be *Planetary Diversity*
and *PD - Ascension Worlds* — the same family — so the filter correctly ate it
and the control looked like a failure of the check. The fix was to choose the
pair by asking `_key_conflict_families()` which sources are **not** related, and
it landed on PD - Ascension Worlds against Real Space 4.0. **A control that
does not know what the check filters is not a control**, and this one would have
passed as "the check cannot fire" if it had not been re-derived.

## What this does not settle

**Nothing is broken today, and that is a measurement rather than a promise.**
The check ships holding a surface at zero, which is what
`check_key_conflicts` does in `common/` and what
[decision 104](104-script-documentation-is-a-version-exact-oracle.md) declined
to do for modifiers — the difference is that this one *can* fire: the population
is 41 live cross-source claims, one `sources-sync` away from a ninth that is not
a placeholder.

**The non-English languages are unasked in practice.** The gate admits any
language vanilla ships and does not self-contest, but the built tree only
carries `english` after the harvest, so the count is one language's. If a source
is ever vendored with its `l_german` intact, the check covers it with no change.
