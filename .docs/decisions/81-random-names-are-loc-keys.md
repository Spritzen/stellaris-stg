# 81 — A quoted random name is a localisation key, and STG shipped 330 with no key

**Status:** decided, 2026-08-10
**Falsifies** [decision 52](52-trek-star-names.md) in one part — its `token()`
rule stands, its "these are literals" reasoning does not.
**Follows** [decision 61](61-music-player-track-names.md), which is the same
failure in the music database.

## The report

From the 2026-08-10 Federation run, off the galaxy map:

> *"Most nebula names contain an underscore instead of a space. e.g.
> Arachnid_Nebula and Class_9_Nebula"* — and, separately, *"System name:
> Kullat_Nunu"*.

## The mechanism

An entry in `common/random_names/` is written one of two ways, and the quoting
is what distinguishes them:

```
Altair                                  # unquoted: a literal, drawn as itself
"Epsilon_Eridani"                       # quoted: a KEY, looked up
Epsilon_Eridani:0 "Epsilon Eridani"     # localisation/english/random_names/
```

A key with no entry is **drawn verbatim**, and nothing is logged. That is
[decision 61](61-music-player-track-names.md)'s finding — *a name that resolves
to itself still resolves* — in a third database, after the music player and the
shipset dropdown.

## Why decision 52 got it backwards

`tools/gen_star_names.py`'s `token()` said, in its own docstring:

> Apostrophes are ordinary and unquoted (Spoo'a, Gor'kaner, T'u) — the opposite
> of the common/name_lists/ rule, because these are literals and not loc keys
> (**nothing in vanilla's localisation defines Amgathorra**).

Every clause of that is true. The inference is not. Amgathorra is **unquoted**,
and the measurement was taken over the unquoted names — which are indeed
literals with no keys — then applied to the quoted ones, which are the other
kind. The two subsets were never separated, so the evidence never touched the
claim it was supporting.

**Measured 2026-08-10 against vanilla 4.4**, splitting them properly:

| | quoted entries | of those, localised |
|---|---|---|
| `star_names` | 55 | **55** |
| `nebula_names` | 55 | **55** |

Not a majority — **all of them, with no exception in either pool.** Re-measure
by taking the quoted entries out of
`/stellaris/common/random_names/base/00_random_names.txt` and looking each up in
`/stellaris/localisation/english/random_names/`.

STG shipped **330 quoted entries and zero keys**, so every multiword Trek system
and nebula in a generated galaxy drew its own key.

## What changed

`tools/gen_star_names.py` now writes a second file,
`src/localisation/english/stg_random_names_l_english.yml` — **328 keys**, one for
every quoted entry the regenerated pool holds, underscore reversed to the spaced
form STNH placed on the map, so the value is a reversal rather than a guess.
Unquoted single-word entries are untouched: they are literals, and that half of
decision 52 was right.

**The tool was also not idempotent, and this found it.** It subtracts names
already in the merged pool by reading `stg-build/`, which `make vendor` has
filled with its own previous output — so the second run subtracted its own 580
names and wrote a pool a third the size. It now skips its own file by name. The
same trap is documented in `tools/fix_ship_locators.py`; this is its second
instance, and the pattern is worth recognising: **a generator that reads the
built tree must exclude what it wrote there.**

Re-running with that fixed also dropped 22 names the tool's own rules exclude —
Aldebaran, Betelgeuse, Sirius and 19 more that STG's name lists already own
([decision 25](25-real-home-systems.md)) — a backlog from the tree
growing since the last run, not a new call.

## What it does not settle

Whether the **display values** are right, one by one. `Class_9_Nebula` becomes
"Class 9 Nebula" and `82_G._Eridani` becomes "82 G. Eridani", which are correct;
328 of them have not been read individually, and no check can ask whether a
name reads well. That is the next run's eyes.
