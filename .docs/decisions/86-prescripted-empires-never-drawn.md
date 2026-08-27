# 86 — The Trek empires were never drawn: vanilla gives the prescripted pool a 5% chance per AI slot

**Status:** decided, 2026-08-24
**Closes** [ufp-run-remediation.md](../planning/ufp-run-remediation.md) item 4,
open since 2026-08-10 with three hypotheses eliminated and no cause.
**Follows** [decision 14](14-remove-vanilla-prescripted-empires.md) and
[decision 19](19-stnh-minor-powers-as-ai-empires.md), which between them are
what makes the fix safe.
**Corrected in part by** [decision 88](88-playable-gates-the-design-database.md),
2026-08-25. The lever below is right and is kept. Two things said about it are
not: the pool it draws from held **21** empires, not 101 — `playable = stg_never`
keeps the other 79 out of the engine's design database entirely — and the claim
under *What the save proves* that all 101 appear in the save's `design={…}`
catalogue is wrong; both saves carry exactly 22 `design={` blocks. The
Federation's unfired `spawn_enabled = always`, left open below, was the shared
`sol_system_initializer` after all, and the reasoning that dismissed it
("neither of the pair spawned, where a collision should have cost only the
loser") assumed a failure mode the engine does not have.
**Falsified as a closure by the 2026-08-25 evening run**, the second galaxy at
100% and the first with decision 88's fix in it: still zero Trek empires in 18,
with every empire met. The lever remains correct and remains in the tree; it was
never the cause. Item 4 is reopened — [open-questions.md](../planning/open-questions.md),
"Whether the prescripted pool can ever be drawn from" (that section's title as of
2026-08-26; the galaxy half of it moved to
[static-galaxy-plan.md](../planning/static-galaxy-plan.md)).

## The report

From the 2026-08-24 Vulcan run: *"No other star trek empires were met in the
galaxy and yet all 18 empires were met in game."*

The same thing the Federation run said on 2026-08-10 (*"22 Empires met and no
trek empires"*) and the short Vulcan run implied on 2026-08-22. **Three runs,
three galaxies, zero Trek AI empires between them.**

## The cause, and it was never in the empires

`common/defines/00_defines.txt:972`:

```
CUSTOM_EMPIRE_SPAWN_CHANCE = 50   # Chance that an empire will be created from an
                                  # existing template instead of randomly
                                  # generated (10 = 1% chance)
```

**The scale is `10 = 1%`, so vanilla ships 5%.** Every AI slot rolls
independently: a 5% chance it is filled from the prescripted pool, a 95% chance
the galaxy generator invents an empire instead.

| Run | AI empires | P(no prescripted empire) |
|---|---|---|
| 2026-08-10 | 20 | 0.95²⁰ = **36%** |
| 2026-08-24 | 18 | 0.95¹⁸ = **40%** |

At 18 slots the *expected* number of Trek empires is 0.9. Drawing zero is not a
defect, it is the second most likely outcome. Three galaxies in a row is
unremarkable at these odds.

**No STG empire was ever rejected.** That is the part worth stating plainly,
because three sessions were spent looking for a rejection.
`check_prescripted_empires` passes on all 101 against vanilla's own `opposites`,
`allowed_ethics` and archetype budgets; the initializers resolve; the portraits
resolve. They were eligible the whole time and simply almost never rolled.

## What the save proves

`confederacyofvulcan_1053035964/2200.07.02.sav`, the galaxy the 2026-08-22 run
left behind, settles it without needing the engine's cooperation. The save's
`initializer={…}` block lists every home system the generator actually placed:

```
"stg_confederacy_of_vulcan_home"      ← the played empire
"distantstars_init_06"
"megacorp_interstellar_assembly_init_01"
…
```

**Exactly one STG home initializer in the whole galaxy, and it is the player's.**
All 101 empires appear once each elsewhere in the file, inside the `design={…}`
catalogue every save carries — present as templates, absent as countries.

## Why `spawn_enabled` was the wrong lever to reach for

`spawn_enabled = always` is real and it does work; the community's
*Always Spawn Premade Empires* mod is nothing but that token applied to vanilla's
53. But it is a **per-empire** guarantee, and STG has 101 empires and a galaxy
with 18 AI slots. Forcing the pool is not something `always` can express.

It also cannot be reached from the UI. The run reported *"Forced spawn is only an
option for player made empires"*, and that is correct and by design: the empire
designer's force-spawn toggle belongs to empires the player built. A prescripted
empire's only equivalent is the script token.

**The one `always` in the tree did not fire either.** The Federation carries it
and did not appear in the 2026-08-22 galaxy despite the player being Vulcan.
That is a real anomaly, it is **not** what this decision fixes, and it now has
somewhere to go — see *What this does not settle*.

## Decision

`src/common/defines/stg_defines.txt`:

```
NGameplay = {
	CUSTOM_EMPIRE_SPAWN_CHANCE = 1000
}
```

**1000 is 100%: every AI slot draws from the prescripted pool.**

For an ordinary mod that would be a bad value, because it would crowd out
vanilla's randomly generated empires in favour of a handful of presets. For STG
it is the only value that matches what the mod already is, and only because two
earlier decisions did the work first:

- **[Decision 14](14-remove-vanilla-prescripted-empires.md)** removed all 52
  vanilla prescripted empires. The pool holds nothing but Trek — there is no
  Blorg Commonality left for a slot to draw.
- **[Decision 19](19-stnh-minor-powers-as-ai-empires.md)** put STNH's 79 minor
  powers in as AI-only empires (`playable = stg_never`). That is a pool deep
  enough to fill a large galaxy without repeating an empire.

So the galaxy is asked to use a 101-empire all-Trek pool, and 18 AI slots become
18 Trek empires. **This is the setting a total conversion wants, and STG has been
one since decision 14 without ever telling the galaxy generator.**

`FALLEN_CUSTOM_EMPIRE_SPAWN_CHANCE` is deliberately left at vanilla's 50. STG
ships no prescripted fallen empire, so raising it would only make the generator
look harder for something that is not there.

## What this does not settle

**Why the Federation's `spawn_enabled = always` did not fire.** At 100% the
question stops mattering for whether Trek empires appear — every slot is Trek
now regardless — but it is still an unexplained token, and the same live-run
evidence that closed this decision left it open. Two readings survive:

- the shared `sol_system_initializer`. The Federation and the mirror Terran
  Empire both name it and it is `max_instances = 1`
  ([decision 25](25-real-home-systems.md) took that path knowing it was
  untested). Against this reading: **neither** of the pair spawned, where a
  collision should have cost only the loser.
- the long-standing engine bug the community reports against force-spawn, where
  one or two forced empires are quietly replaced by randomly generated ones.

Both are cheap to distinguish now: at 100% the next galaxy should hold ~18 Trek
empires, and whether the Federation is among them is one glance at the contacts
list. [Open questions](../planning/open-questions.md) carries it.

## How this class of defect gets caught next time

It does not, and that is worth being honest about rather than inventing a check.

**No check could have found this.** Every name resolved, every empire validated,
`error.log` was silent — the galaxy generator rolled a die and lost, which is
not a defect from any static point of view. It is the purest case yet of the
rule [live-runs.md](../guides/live-runs.md) already states: a screen nobody
opened is a check that never ran, and here the screen was the galaxy itself.

What *did* find it was reading a **define** rather than the content, after three
sessions of reading the content. **When every instance of a population is
individually valid and the population is still absent, stop auditing the
instances and go and read the rule that samples them.**
