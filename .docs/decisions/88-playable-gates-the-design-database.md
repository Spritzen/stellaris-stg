# 88 — `playable` gates the engine's design database, not the picker, so 79 of the 101 empires could never spawn

**Status:** decided, 2026-08-25
**Falsifies** [decision 19](19-stnh-minor-powers-as-ai-empires.md)'s mechanism —
its 79 AI-only empires were never AI-anything — and the "101 empires deep"
premise [decision 86](86-prescripted-empires-never-drawn.md) rested its value on.
**Follows** [decision 86](86-prescripted-empires-never-drawn.md), whose
`CUSTOM_EMPIRE_SPAWN_CHANCE = 1000` is kept and is now the second half of a
working fix rather than the whole of a fix that could not work.
**Closes** [open-questions.md](../planning/open-questions.md)'s standing question
of why the Federation's `spawn_enabled = always` never fired.

## The report

From the 2026-08-25 Vulcan run, the first played with
`CUSTOM_EMPIRE_SPAWN_CHANCE = 1000`: *"No star trek empires were met again and I
met every empire."*

**Four runs, four galaxies, zero Trek AI empires.** Decision 86 raised the pool's
draw rate from 5% to 100% and the galaxy did not change, which is the shape of a
finding: at 100% the die is no longer the variable.

## What the saves prove

Two saves on disk carry a `design={…}` catalogue — the engine's own record of
every empire design it loaded.

```
save games/unitedfederationofplanets_898554066/2200.01.01.sav  → 22 design blocks
save games/confederacyofvulcan_1053035964/2200.07.02.sav       → 22 design blocks
```

**Twenty-two, not 101.** Extracting every design key and comparing it against the
source tree gives an exact match, both ways:

| | count |
|---|---|
| empires in `prescripted_countries/stg_*.txt` | 101 |
| carrying `playable = stg_never` | 79 |
| **not** carrying it | **22** |
| **designs the engine loaded** | **22** |

Zero of the 79 present; zero of the 22 missing. The set the engine loaded *is*
the set whose `playable` trigger passes.

**So `playable` does not hide an empire from the picker. It keeps the empire out
of the design database, and the galaxy generator draws AI empires from that same
database.** An empire that fails `playable` cannot be picked *and* cannot spawn.

Decision 86 stated the opposite — *"All 101 empires appear once each … inside the
`design={…}` catalogue"* — from the same file. That reading counted every
appearance of an empire's key rather than the `design={` blocks, and 79 of the
101 appear in a save for other reasons.

## There is no AI-only prescripted empire

Decision 19 built 79 minor powers on `playable = stg_never` + `spawn_enabled =
yes`, reading those as "hidden from the player, available to the AI". The engine
has no such state. Vanilla never claims otherwise: its two `playable =
empire_design_never` empires (`humans1`, `humans2`) are **also**
`spawn_enabled = no`. They are dead stubs kept for key compatibility, not
AI-only empires, and vanilla ships no example of the combination STG invented.

**An empire is in the picker and in the pool, or it is in neither.** That is the
whole of the rule.

## What else was wrong, found by removing the gate

The gate was load-bearing for the checks too: three of them skipped
`playable = stg_never` empires as unreachable. Removing it put all 79 in front of
rules they had never been measured against, and both findings are real.

**78 empires had no `common/portrait_sets/` entry for their species class.** The
designer has no portrait to offer and answers by hiding the empire — *'Must
select a portrait'*. So removing the `playable` gate alone would have moved all
79 from one exclusion to another, and the galaxy would have looked identical.
`src/common/portrait_sets/stg_portrait_sets.txt` gains 78 blocks, one per class,
each naming the portrait group the empire's own `species` block already names.
It is 78 and not 79 because `stg_minor_tng_coalition_hope` is Vulcan and takes
VUL deliberately ([decision 46](46-coalition-of-hope-takes-vul.md)).

**Twelve species classes reached the empire designer wearing human civilian
clothes.** Exactly the defect [decision 22](22-empire-designer-clothes.md) fixed
for six classes in August, unchanged in cause: the two `humanoid_master_*`
selectors gate every scope but `game_setup`, and `game_setup` is the only scope
the designer reads. The same two `vendor.yml` patches gain twelve rows each side,
every one of them the art that class's own `species` scope already names.

## Two empires cannot share one starting system

Independent of `playable`, and the answer to the question decision 86 left open.

The Federation and the mirror Terran Empire both named `sol_system_initializer`.
`tools/gen_home_systems.py` recorded that as a benign race — *"the empire that
loses the race falls back to a generated home system … confirm against a live
run"* — and the live runs falsified it: **neither** spawned, in any galaxy, the
Federation not even on `spawn_enabled = always`. Paradox's own bug report
([2.2.7, still open](https://forum.paradoxplaza.com/forum/threads/stellaris-2-2-7-b1a8-forced-custom-empire-do-not-spawn-if-starting-solar-system-is-duplicated.1165395/))
describes it exactly: two force-spawned empires sharing a starting solar system,
only one spawns, no error and no notification.

The Terran Empire gets its own authored mirror Sol. It cannot copy vanilla's,
because `sol_system_initializer` carries `sol`, `sol_system`, `planet_earth` and
`planet_mars` — flags vanilla events address by name, so a second system holding
them would give the galaxy two Earths. Geometry crosses, flags do not.

## `max_instances` does not belong on a home system

All 37 generated home systems carried `max_instances = 1`. Vanilla's own data
says that is a category error — it is a scatter-pool cap, not a home-system
property:

| `usage` | initializers | with `max_instances` |
|---|---|---|
| `misc_system_init` | 194 | 135 |
| `custom_empire` | 9 | **0** |
| `empire_init` | 6 | **0** |
| `origin` | 14 | **0** |
| `fallen_empire_init` | 7 | **0** |
| `nomad_init` | 7 | **0** |

**Zero across all 43 empire-facing initializers, vanilla's own Sol included.**
Removed from the generator's two emission sites. Whether it was contributing is
untested and the point is that it is off-pattern in a place where vanilla is
unanimous, which is the standing reason to match vanilla rather than reason
about the engine.

The wider pattern is worth recording even though STG does not follow it: of
vanilla's 35 AI-spawnable prescripted empires, **30 name no `initializer` at
all**, and the community's standing advice for an empire that must spawn is to
give it a random start. STG names one for all 39 of its empires that have a home
system. That is deliberate — decision 25 bought real home systems with play
evidence — and it is now the only remaining off-pattern thing about the pool.

## Decision

1. **`playable = stg_never` is removed from all 79 minor powers**, and the
   trigger it named is deleted — nothing else used it. The empire picker goes
   from 22 entries to 101; `src/prescripted_countries/stg_minor_powers.txt` is
   renamed `stg_z_minor_powers.txt` so the majors, quadrant and frontier powers
   sort above them, the way vanilla's `00_top_countries.txt` puts humans first.
2. **78 portrait sets are added**, without which (1) changes nothing.
3. **Twelve `game_setup` rows per selector**, so those species are not drawn as
   humans in a picker they have just become visible in.
4. **The Terran Empire takes its own mirror Sol**, and `max_instances` comes off
   every generated home system.
5. **`CUSTOM_EMPIRE_SPAWN_CHANCE` stays at 1000.** Decision 86's lever was right
   and its premise was wrong: the pool it draws from is 100 empires now, and was
   21 when that decision valued it at 101.

## How this class of defect gets caught next time

Decision 86 said no check could have found it and that was true of the die-roll.
It is not true here, and the mechanism is worth naming: **the gate that hid the
empires also hid them from the checks that would have found the rest.** Three
checks carried `playable = stg_never` as a skip. They were correct to — an
unreachable empire genuinely cannot fail a designer rule — which is what makes
the pattern dangerous: a *correct* skip on a *wrong* premise is invisible from
both ends. Removing one token turned 0 findings into 90.

**A skip condition is an assumption the checks stop testing.** When a population
is excluded from a rule, the exclusion is the thing to re-derive first, before
auditing anything the rule still covers.

And the rule that actually found it, which decision 86 stated and then did not
apply to itself: **when every instance of a population is individually valid and
the population is still absent, go and read the rule that samples them.** The
first sampling rule was the define. The second was `playable`, and it was one
`grep` and one save away the whole time.
