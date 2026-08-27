# 83 — The 99 designs *are* loaded and still nothing draws them, five empires were hidden by two vanilla gates, and the initializer theory cannot explain 62 of them

**Status:** decided, 2026-08-26
**Follows** the removal of the `playable = stg_never` gate, whose fix is
confirmed working by the save below: the design database now holds all 99.
**Falsifies** the remaining half of [open-questions.md](../planning/open-questions.md)'s
standing either/or — "either they were still not in the design database … or the
cause is something else again." It is something else again.
**Narrows** the "unique home system" hypothesis
([open-questions.md](../planning/open-questions.md), "What vanilla does"): it
cannot be the whole cause, because 62 of the 99 carry no `initializer` at all and
were not drawn either.
**Corrects** [external-sources.md](../reference/external-sources.md)'s dismissal
of the `randomized` claim, which answered a question about `common/portrait_sets/`
and left the one about `common/species_classes/` unasked.
**Corrected in part by [decision 84](84-static-galaxy-is-the-mechanism.md)**, the
same day: the section below reads STNH as evidence *against* the `randomized`
hypothesis, and that was wrong — STNH's Trek galaxy comes from static maps, so
its prescripted pool was never under test. The vanilla cross-tab below stands;
the STNH row against it does not.

## The run

The 2026-08-26 Vulcan run — **the sixth galaxy in a row with no Trek AI empire**,
and the first since 2026-08-22 to leave a save on disk. `ironman` is off and
`settings.txt` no longer carries the flag, so the evidence channel
[live-runs.md](../guides/live-runs.md#the-save-is-better-evidence-than-the-log-when-there-is-one)
asked for is open. That ask is what made this decision possible; everything below
is read out of `gamestate`, not inferred.

`save games/confederacyofvulcan5_1438312515/2258.06.04.sav`, ~2 h 45 m of play.

## What the save settles

**The design database is not the cause.** The `design={…}` catalogue holds
**99 blocks**, every one of them STG's, `spawn_enabled=yes` preserved on each:

```bash
grep -cP '^\tdesign=$' gamestate      # 99
```

*(The blocks are nested inside `galaxy={…}` and the brace sits on the following
line, so the earlier `grep 'design={'` finds zero in a 4.4.6 save. Match the
key, not the brace.)*

**Nothing drew from it.** Of 77 `country={…}` entries, exactly one carries a
prescripted name key — `STG_EMPIRE_vulcan`, the player. Every one of the 18 AI
empires is `%ADJECTIVE%` or `%ADJ%`.

**The galaxy is vanilla to the species.** Every empire species in `species_db` is
a vanilla class on a vanilla name list — `REP`/`REP2`, `MAM`/`MAM4`, `PLANT`,
`NECROID2`, `LITHOID3`. `VUL` and `STG_VULCAN` appear once each, for the player.
No STG class, name list or portrait reached an AI empire by any route.

**Of the 36 STG home-system initializers, one was placed** —
`stg_confederacy_of_vulcan_home`, the player's. The other 35 were never reached.

## Why the initializer theory cannot be the whole cause

Counting the designs by what they ask for:

| designs | `initializer` |
|---|---|
| 62 | `""` — none, so the generator places them anywhere |
| 36 | a named `stg_*_home` |
| 1 | `sol_system_initializer` (the Federation) |

The 62 were free of the objection the vanilla cross-tab raises and **were not
drawn either**. Whatever excludes them is not about home systems. The hypothesis
survives only as a *second* filter, and stripping the `initializer` lines would
still cost [decision 23](23-real-home-systems.md) for a fix that demonstrably
cannot reach 62 of 99 — so the standing "do not strip them" holds.

## What the log did name: five empires, two vanilla gates, both swept

`select_empire_design_view.cpp:714` hid five designs. Two printed a reason; three
printed only their name. Both rules were derived and swept across all 99, and
each found **exactly** the empires the log named and nothing more — the
[sweep-the-rule](../guides/live-runs.md#a-screen-nobody-opened-is-a-check-that-never-ran)
discipline coming out even for once.

**1. A civic that is only available *without* a DLC.** `civic_corporate_dominion`
is `playable = { NOT = { host_has_dlc = "Megacorp" } }` — vanilla's stand-in for
the MegaCorp civic, unavailable to anyone who owns MegaCorp. Four empires took
it: `stg_minor_morali_states`, `stg_minor_talaxian_empire`,
`stg_minor_valtese_senate`, `stg_minor_yaderan_republic`.

**This was not a copy-paste slip.** All four lift the tuple whole from vanilla's
own `iferyx` — `auth_oligarchic` + `gov_trade_league` +
`civic_corporate_dominion` + `civic_shadow_council`, ethics egalitarian /
spiritualist / pacifist — exactly as
[stg_z_minor_powers.txt](../../src/prescripted_countries/stg_z_minor_powers.txt)'s
header says every tuple is built. `iferyx` is hidden on a full install too. **The
rule "lift a vanilla tuple whole" is sound and insufficient: the tuple also has
to survive the DLC set STG requires.** And `gov_trade_league` names the civic in
its own `possible`, so the government had to move with it.

Repaired to `civic_merchant_guilds` + `civic_shadow_council` on
`gov_theocratic_oligarchy` — trade identity kept, ethics and authority untouched,
`gov_theocratic_oligarchy` asking only `is_oligarchic_authority` and
`is_spiritualist`, which all four already are.

**2. A civic and a trait gated to vanilla species classes.**
`stg_minor_brunali_empire` carried `civic_tankbound`, whose `possible` gates
`species_class` to `{ AQUATIC INF NECROID TOX }` — no STG class can ever satisfy
it — and `trait_tankbound`, which vanilla declares
`species_possible_add = { always = no }`: a civic's `modification` block grants
it and a species block can never carry it directly. Repaired to
`civic_agrarian_idyll`, which asks only for pacifist and matches the
`trait_agrarian` the Brunali already carry.

All three rules are now in `check_prescripted_empires`
([the catalogue](../validation/checks.md)), read out of vanilla's own databases
rather than hardcoded. Calibration: reverting the five repairs makes the check
report **six findings over those five empires and nothing else** — Brunali's
civic and trait are two defects, not one.

**None of this explains the empty galaxy.** Five hidden empires out of 99 cannot
produce zero out of 18, and the four `iferyx` copies were hidden in the *designer*
while the other 94 were not. It is a real defect fixed on its own merits.

## The candidate this leaves, and what is against it

Every STG species class carries `randomized = no`
([decision 30](30-declare-stub-species-classes.md)'s file header, on the grounds
that these classes appear only as prescripted empires). Cross-tabulating
vanilla's own `prescripted_countries/` against each empire's species class:

| | class is randomizable (`yes`, default, or a trigger) | `randomized = no` |
|---|---|---|
| `spawn_enabled = yes` | **32** | **1** |
| `spawn_enabled = no` | 17 | 1 |

The single exception is `mindwardens`, on `MINDWARDEN`
(`randomized = { always = no }`). **STG is 0 of 99 on the randomizable side.** The
save agrees from the other end: the `randomized = no` classes present in the
galaxy — `ROBOT`, the ten `PRE_*`, `SHROUDWALKER`, `SALVAGER`,
`MINDWARDEN_ENCLAVE` — appear only as pops, pre-FTLs and enclaves, never as an
AI empire.

**Two things are against it and both are real.** Vanilla's `mindwardens` is a
counterexample, and **STNH ships the same combination 94 times**: every one of its
110 Trek empires uses a `randomized = no` class and 94 are `spawn_enabled = yes`.
That STNH also ships `RANDOMTREK`/`PRE_RANDOMTREK` at `randomized = yes` so that
randomly generated empires still come out Trek-shaped is suggestive of a mod that
hit this wall and went around it — but it is not proof, and STNH's galaxies have
never been measured here.

**And the fix is not one line.** Vanilla ships a `common/species_names/` entry for
every class it randomizes; STG ships **none** for its 99. Flipping `randomized`
without them would ship a combination vanilla never ships, which is the mistake
pattern this project keeps paying for. It is a two-part change and the second part
is 99 name pools.

## What to do next, in order

**1. One glance at the AI empire preview before pressing start.** Unchanged from
[open-questions.md](../planning/open-questions.md), and now the *only* cheap
discriminator left: 18 *Random AI Empire* slots means the generator never
consults the pool; Trek empires listed there means it does and placement fails.
The database question it was half-aimed at is closed, so this glance now answers
the whole of what is left.

**2. Keep leaving saves on disk.** Two questions that took four runs each were
settled from a save in minutes, and so was this one.
