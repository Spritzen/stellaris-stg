# 24 — STNH identifiers in generated home systems

*Originally "STNH planet and star classes". Retitled after the first fix did
not stop the crash: the defect was never specifically about classes.*


*Decided 2026-08-03. Follows directly from
[decision 23](23-real-home-systems.md), which introduced
`tools/gen_home_systems.py` and the file this is about. Also the reason
`check_initializer_classes` exists in `tools/validate.py`.*

## The symptom

Stellaris **crashed during startup** and never reached the menu.

The container-side evidence was unusually thin, and the shape of it is the
lesson:

| Log | What it said |
|---|---|
| `time.log` | **empty** — startup never completed |
| `game.log` | three lines, stopping after `2113 defines loaded` |
| `setup.log` | ends at `Initializing Database: CSystemInitializerDataBase` |
| `error.log` | 166 KB, and **nothing about the crash** |

`dlc_load.json` recorded `enabled_mods: ["mod/star_trek_galaxies.mod"]`, so this
was STG and not a vanilla run (the check decision 14 exists for).

`error.log`'s last line was an unrelated `common/pop_jobs/` duplicate-key
notice. **The crashing database logs nothing at all**, because it dies while
resolving names rather than while parsing — there is no parse error to report.
`setup.log`'s trailing `Initializing Database:` line is the only pointer to the
culprit, and it names it exactly.

## The cause

`common/solar_system_initializers/stg_home_systems.txt` — generated hours
earlier by decision 23's new tool — named **nine classes that nothing in the
merged tree declares**:

| Referenced | Kind | Now maps to |
|---|---|---|
| `pc_d_class_solitanian` | planet | `pc_barren` |
| `pc_k_class_adaptable` | planet | `pc_barren` |
| `pc_k_class_transjovian` | planet | `pc_barren` |
| `pc_o_class_sulfur` | planet | `pc_barren` |
| `pc_e_class` | planet | `pc_toxic` |
| `pc_voth_city_ship` | planet | `pc_continental` |
| `pc_hunters_lodge` | planet | `pc_continental` |
| `sc_binary_gk` | star | `sc_binary_g_k` |
| `sc_trinary_gff` | star | `sc_trinary_a_f_g` |

All nine are STNH's own, defined in
`.source/688086068/common/planet_classes/00_planet_classes.txt` and
`…/star_classes/STH_star_classes.txt`. **STG does not vendor STNH's `common/`**
— we take its art, not its script — so in the merged tree they resolve to
nothing.

The generator was supposed to prevent exactly this. Its header says STNH's
"Trek planet classes are mapped onto vanilla's", and it carried two remap
tables to do it. But both were applied as:

```python
val = PLANET_CLASS.get(val, val)      # tools/gen_home_systems.py
```

**An unmapped class was written through unchanged.** The tables held the
thirteen STNH classes someone had noticed; the other nine passed straight into
the build wearing STNH's names. A hand-kept allowlist with a silent fallback is
the failure mode, not the missing entries — the entries will always be
incomplete.

## The mappings, and the rule behind them

The rule is decision 23's own: *habitability is what matters*. Every one of the
seven planet classes is checked against STNH's own definition.

Five are `colonizable = no` in STNH too, so they become `pc_barren` — the
vanilla uninhabitable rock — except `pc_e_class`, where STNH's own
`icon = GFX_planet_type_toxic` picks out `pc_toxic` among the uninhabitable
classes. This also keeps `pc_k_class_adaptable` consistent with the
`pc_k_luna_class` / `pc_k_ares_class` entries already in the table.

Two are `colonizable = yes`: `pc_voth_city_ship` and `pc_hunters_lodge`, both
`is_artificial_planet = yes` orbital habitats, and both are their empire's
capital (`starting_planet = yes`). They map to `pc_continental` rather than
`pc_habitat` because `stg_minor_voth_theocracy` and
`stg_minor_hirogen_hunters` each already declare `planet_class = "pc_continental"`,
and the prescripted empire overrides the initializer's class anyway — so this
makes the two agree, which is the rule the hand-written systems in the
generator already follow.

The two star classes must keep their **star count**, because the initializer's
own `class = "star"` planets are filled from the system class: Denobula
declares three, Garid two. `sc_binary_gk` is exactly vanilla's `sc_binary_g_k`
(G + K) with an underscore dropped. STNH's `sc_trinary_gff` is G + F + F and
vanilla has no `g_f_f`, so `sc_trinary_a_f_g` — it keeps the G that STNH
declares as the system's own class, plus one of the two F stars.

## The second crash, and the mistake that caused it

**Fixing the nine classes did not stop the crash.** The next run died at exactly
the same line — `Initializing Database: CSystemInitializerDataBase`, empty
`time.log`, an `error.log` byte-identical in size to the previous run's.

Two more defects were in the same generated file, and both are the *same bug* as
the nine:

**`icy_asteroid_belt_dispersed`**, used four times in
`stg_minor_confederation_earth_home`. STNH's `STH_asteroid_belts.txt` adds it to
vanilla's six types; we do not vendor STNH's `common/`. The generator emitted it
via `scalar(belt, "type") or "rocky_asteroid_belt"` — **another silent
pass-through**, in a function fifty lines from the two that had just been fixed.

**The Romulan star count.** `stg_romulan_star_empire_home` declared `sc_m` — one
M star — and placed *two* `class = "star"` planets: Romulus, and **Hobus**, the
star that destroys Romulus in the 2009 film, which STNH models faithfully with
`flags = { secondaryStar }`. A `class = "star"` planet is filled from the star
class's list, so the second had nothing to draw from. Now overridden to
`sc_binary_m_m` via `SYSTEM_STAR_CLASS`, keeping both STNH's star type and Hobus.

### What the mistake actually was

The first pass fixed **the instances the evidence named** — nine dangling
classes — and then built two checks that looked for dangling *classes*. The rule
was never about classes. It is:

> **Any STNH identifier the generator does not explicitly map is written
> through unchanged, into a tree that does not vendor STNH's `common/`.**

Classes were simply where it was first noticed. CLAUDE.md already says this —
*derive the rule and sweep the tree, never repair only the instances the log
named* — and the first pass did not do it. The sweep that should have happened
immediately takes one query: enumerate **every identifier-valued key** in the
generated file and check each against the merged tree. There are only six
(`class`, `type`, `usage`, `deposit_blockers`, `modifiers`, `name`), and it
finds the belt type at once.

That sweep has now been run tree-wide and is clean: no unresolvable belt types
in any of the 44 initializer files, no initializer key declared in two files,
and all 32 classes our file names resolve.

## What was changed

**`tools/gen_home_systems.py`** — `PLANET_CLASS` and `STAR_CLASS` gained the
nine mappings; `ASTEROID_BELT` and `SYSTEM_STAR_CLASS` are new. The guard is now
`check_references()` and covers all three families — classes, belt types, and
star count — refusing to write the file and naming what failed. Calibrated
against the crashing build: it reports both round-two defects.

**`tools/validate.py`** — `check_initializer_classes()` asks the same questions
of the *merged tree* rather than of `src/`, so it covers every source mod's
initializers. Classes and belt types are errors; star count is a warning,
because Real Space breaks it three times and the game demonstrably loads.

## Two calibration passes on the class check, both worth recording

The check was wrong twice before it was right, and both errors are general.

**`class` is heavily overloaded in these files.** A flat regex over
`solar_system_initializers/` produced **51 false positives against 14 true
findings**: `create_species = { class = random_non_machine }` is a species
class, `create_leader = { class = scientist }` a leader class,
`ideal_design_class` a ship design. Only two positions name a planet or star
class — the initializer's own level, and directly inside a `planet`/`moon`
block — so the extractor is block-aware and tests the innermost block key
(`moon` nests inside `planet`, so depth alone is wrong).

**Vanilla documents its vocabulary by commenting it out.** `class = none` and
`class = random_asteroid` are legal engine keywords that vanilla's live
initializers never use; they appear only in
`solar_system_initializers/example.txt`, commented, alongside `random`,
`random_colonizable` and the rest. Stripping comments before deriving the
allowlist hid them and cost two more false positives. `example.txt` is
therefore read **raw**, every other file stripped. This is CLAUDE.md's
`isBajoranReligiousLeader` lesson again: read what is *written*, not only what
is live.

## The Real Space findings, which are not ours

Two sets, both acked in `vendor.yml` under `initializer_class_ack`:

`realspace_special_system_initializers.txt` names `red_giant`,
`blue_supergiant`, `yellow_supergiant`, `yellow_stars` and `blue_stars`, none
declared anywhere — including in Real Space's own source, whose randomizer
lists are all `rl_`-prefixed (`rl_blue_stars`, `rl_red_giant_stars`), so these
read as the prefix dropped by hand. The same file also places two
`class = "star"` planets against one-star classes in `rs_special_init_17`,
`_19` and `_21`.

Both predate the crash and the mod loaded with them for two days, **so neither
an unresolvable star class nor a surplus star is reliably fatal on its own**.
That is worth knowing and it is why the ack exists rather than a fix: nothing in
STG depends on those systems, and the cost is a wrong star class in three Real
Space special systems.

It also means the causal claim here is narrower than it looks. What is
established: the crash is in this database, nothing else in it changed that day,
this file contained eleven references the merged tree cannot resolve, and all
eleven are gone. Which one the engine actually died on is not determinable from
the container.

## Third round: it loaded, and the empire did not own its home system

With the eleven references fixed the game started — 49.6 s, `time.log`
populated. Play then reported starting as the Klingon Empire **without owning
the Qo'noS system**.

`error.log` says nothing about it, and could not: this is a gameplay outcome,
not a load failure. All 37 generated capitals carried

```
starting_planet = yes
init_effect = { prevent_anomaly = yes }
```

and nothing else. `starting_planet = yes` says *which* body is the capital.
**`generate_empire_home_planet = yes` is what puts the empire on it** — capital
building, pops, districts, and the home-system starbase that makes the empire
the system's owner. Without it the geometry spawns and the empire is never
established on it.

The rule is vanilla's own, and it is nearly universal: of vanilla's nine
`usage = custom_empire` initializers, **eight run the effect**.

| Pattern | Initializers |
|---|---|
| `home_planet = yes` + effect | the six `custom_starting_init_*`, `titawin_init` |
| `starting_planet = yes` + effect | `deneb_system` |
| `starting_planet = yes`, no effect | `sol_system_initializer` — **the only one** |

`deneb_system` is our case exactly: a prescripted empire on fixed geometry whose
capital is one specific body. It pairs `starting_planet = yes` with the effect
in a **second** `init_effect` block, which is why the generator emits two rather
than merging them.

Sol is left as a special case rather than treated as licence: five vanilla
empires use it and start correctly, and vanilla's scripted content references it
by name throughout. It and Real Space's two rescaled solsector copies are acked
under `home_planet_generation_ack`; the Federation and the mirror Terran Empire
point at it and so ride on vanilla's own arrangement.

`check_home_planet_generation` in `tools/validate.py` now enforces this.
Calibrated against the broken build: **40 findings — all 37 generated systems,
plus the three acked Sol variants, and nothing else.**

### Why this one was invisible to everything built so far

The two checks from rounds one and two ask whether a *name resolves*. This
defect has no unresolved name: every identifier was valid, the file loaded, and
the database initialised. It is a **missing** statement, not a wrong one — and
no log records an absence. Only playing the empire showed it.

That is the same lesson as CLAUDE.md's "a screen nobody opened is a check that
never ran", one level further out: the game starting is not evidence the content
works. Three rounds here produced three defects, and each was found by a
different instrument — `setup.log`'s last line, a tree-wide reference sweep, and
a player noticing.

## Status

Rounds one and two are **confirmed**: the game loads, in 49.6 s, with
`time.log` populated.

Round three — home-planet generation — is **not confirmed**. `make vendor` and
`make validate` are clean (0 errors, the same 12 pre-existing warnings as
before any of this), and all 37 capitals now carry the effect, but whether the
Klingon Empire owns Qo'noS is for the next live run to report.
