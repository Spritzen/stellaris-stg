# 27 — a quoted `class` keyword is a different keyword

*Decided 2026-08-03. The fourth round on the file
[decision 25](25-real-home-systems.md) introduced and
[decision 26](26-home-system-classes.md) has fixed three times.*

## The symptom

Play started as the Klingon Empire. Qo'noS had **no star**, and the empire did
not own its own home system.

Decision 26's round three had predicted the ownership half and fixed it —
`generate_empire_home_planet = yes` is present on all 37 capitals in the build
that ran. It was not enough, because the two symptoms turned out to be one
defect and it was not the one round three addressed.

## The evidence

`error.log`, one line, inside the play window rather than the init window
(startup completed at 49.7 s; these are at +12 s):

```
[22:54:24][prescripted_systems.cpp:411]: invalid planet class or random_list [star]
```

and then, in order, everything downstream of it:

| Line | What it means |
|---|---|
| `Invalid context switch [system_star] from Qo'noS [galactic_object]`, `01_start_of_game_effects.txt:16` | `generate_home_system_resources` cannot reach the star, so the home system loses its `d_energy_5` starting deposit |
| `set_location: Unable to resolve 'prev.capital_scope.star'`, `game_start.txt:1167` | the starting **science ship** is not created |
| `set_location: Unable to resolve 'prev.capital_star'`, `game_start.txt:1321` | the starting **construction ship** is not created |
| `set_location: Unable to resolve 'prev.capital_star'`, `game_start.txt:1491` | the starting **corvettes** are not created |

The ownership symptom has no line of its own and could not have one: vanilla's
own idiom for the home starbase is `prev.capital_star.starbase`
(`game_start.txt:1474`) — the starbase is anchored **to the star**. No star, no
starbase; no starbase, no owner. `random_owned_starbase`, which `game_start.txt`
uses three times to fit out that starbase, is a silent no-op over an empty set.

That the file attribution on the `system_star` line names
`00_nomad_custom_initializers.txt` is a red herring: the scope is
`Qo'noS [galactic_object]`, which is unambiguous. Trust the scope, not the
file:line, when a scripted effect is invoked from many places.

## The cause

`common/solar_system_initializers/stg_home_systems.txt` wrote

```
class = "star"
```

where every other file in the merged tree writes

```
class = star
```

`star` is not a class name. It is an engine keyword meaning *fill this body in
from the system's own star class*. Quoted, it stops being that keyword and
becomes a name to look up — and no `common/planet_classes/` entry is called
`star`, so the lookup fails, the body is never created, and the system spawns
one planet short. The one planet it was short of was the star.

### The rule, derived rather than assumed

Quoting is not free-form in this position, and it is not uniformly required
either. Asked of vanilla's own 44 initializer files:

| Value | Quoted | Bare |
|---|---:|---:|
| `star` | 0 | 341 |
| `random_non_colonizable` | 0 | 280 |
| `ideal_planet_class` | 0 | 23 |
| `random` | 0 | 16 |
| `random_colonizable` | 0 | 7 |
| `none` | 0 | 3 |
| `random_asteroid` | 0 | 1 |
| `random_non_ideal` | 0 | 1 |
| **any `pc_*` class name** | **891** | 750 |
| **any `rl_*` randomizer list** | **quoted** | — |

> **A keyword is written bare, always. A name may be written either way.**

So the defect is not "an unquoted thing got quoted" in general — it is specific
to the keyword vocabulary, and the vocabulary is discovered by asking vanilla
which values it *never* quotes, not by listing them.

STNH, whose geometry this file is converted from, writes `class = star` bare
762 times. The quoting was introduced entirely by our generator:
`convert_body()` emitted `f'{indent}{key} = "{val}"'` unconditionally, which is
correct for the `pc_*` names that are most of its output and wrong for the one
keyword among them.

## The sweep

**20 of 37 generated home systems, 23 star bodies.** The log named one because
one system was instantiated — the empire that was played. This is CLAUDE.md's
"the log is a sample of that class, not a census", and it is the whole reason
the sweep was worth doing: the ratio of evidence to defect was 1:23.

| | Systems |
|---|---|
| **Broken** — `class = "star"` | Bajoran Republic, Caitian Empire, Cardassian Union, **Klingon Empire**, Romulan Star Empire (2 stars), Suliban Empire, Xindi Empire, and the minors Acamarian, Betazoid, Cheronite, Denobulan (3 stars), Haakonian, Hirogen, Hur'q, Kinshaya, Kobali, Kraylor, Lyran, Rigellian, TNG Klingon-Cardassian Alliance |
| **Unaffected** — concrete `pc_*_star` | the 17 others, including Andorian, Bolian, Borg, Breen, Vulcan, Dominion, Ferengi, Tholian, Trill |

The 17 that survived did so by accident of provenance rather than by design:
they are the systems the generator authors by hand, plus the converted ones
where STNH happened to name a concrete star class (or where `pc_invisible_star`
maps to `pc_g_star`). A quoted `"pc_g_star"` is a quoted *name*, which is legal.

The Federation and the mirror Terran Empire ride on vanilla's
`sol_system_initializer` and were never affected.

No other file in the merged tree — vanilla, Real Space, Planetary Diversity,
44 files in all — quotes a class keyword anywhere.

## Why nothing caught it

Three instruments existed over exactly this file and all three were blind, each
for its own reason. This is the part worth keeping.

**`check_initializer_classes` in `tools/validate.py`** — written in round one
*for this file*, for this class of defect. Its extractor,
`_initializer_class_refs`, matched `class\s*=\s*"?([A-Za-z][A-Za-z0-9_]*)"?`:
the quotes are optional and **discarded**. `"star"` and `star` are the same
token to it. The check asked "does this name resolve?", the name resolved, and
the check was structurally incapable of asking the only question that mattered.

**`check_references` in `tools/gen_home_systems.py`** — the generator's own
refuse-to-write guard, also from round one. Same blindness, arrived at from the
other side: it read quoted values with `class\s*=\s*"([^"]+)"` and passed
anything in `CLASS_BUILTINS`, a set that exists precisely to say *`star` is
fine*. It was correct that `star` is fine and wrong that `"star"` is `star`.

**The star-count check**, from round two, matched `class\s*=\s*"star"` — the
quoted form only. It was counting the broken spelling and would have gone blind
the moment the spelling was fixed. It had never fired.

The common failure is one sentence:

> **Every check treated quoting as insignificant whitespace. In this position
> it is semantic.**

CLAUDE.md's rule is *establish when a reference resolves, not just whether it
does*. The rule under it, which this cost a live run to learn, is that a
reference has a **written form** as well as a name, and normalising the form
away before comparing can delete the defect. `_strip_comments` was the earlier
instance of the same mistake, in decision 26's own calibration notes.

## What was changed

**`tools/gen_home_systems.py`**

- `declared_classes()` and `is_class_keyword()` are new: a `class` value that no
  `planet_classes/` or `star_classes/` file declares is a keyword, not a name.
- `convert_body()` emits keywords bare and names quoted.
- `check_references()` gained a fourth family — a quoted keyword is refused, not
  merely allowed through — and the star-count matcher now accepts both forms so
  it cannot go blind on a corrected file again.

**`tools/validate.py`**

- `_initializer_class_tokens()` replaces `_initializer_class_refs()` as the
  primitive and returns `(name, quoted)` pairs; `_initializer_class_refs()`
  remains as a wrapper for the questions that genuinely do not care.
- `check_initializer_classes()` derives `bare_only` — the names vanilla writes
  bare and *never* quotes — and errors on a quoted use of one.

### The calibration pass, which was needed

The first version of the check used "not a declared class ⇒ must be bare". It
reported **14 false positives against the 1 true finding**: the `rl_*`
randomizer lists (`rl_habitable_normal`, `rl_unhabitable_planets`, …) are
declared nowhere on disk — the engine holds them internally — and vanilla
quotes them everywhere.

Deriving the answer per name from vanilla's own usage instead of from a
property of the name gives **1 finding and 0 false positives** over all 44
files. It is the same rule as the BOM check asking vanilla per folder, and the
shader allowlist asking vanilla what it never declares: *ask, don't assert*.

## Status

`make vendor` and `make validate` are clean — 0 errors and the same 12
pre-existing warnings as before the change. All 23 star bodies across the 20
systems now read `class = star`.

**Not confirmed in game.** Whether the Klingon Empire spawns with a star, owns
Qo'noS, and starts with its science ship, constructor and corvettes is for the
next live run to report. The four consequences are each independently visible,
so the run either confirms all of them or narrows the cause usefully.
