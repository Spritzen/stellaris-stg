# 85 — AI Trek empires are created by their home system's initializer, not drawn from the prescripted pool

**Status:** decided, 2026-08-26
**Follows** [decision 84](84-static-galaxy-is-the-mechanism.md), which found the
static map and stopped one step short of what the map is *for*.
**Supersedes the direction of** the two earlier fixes — raising
`CUSTOM_EMPIRE_SPAWN_CHANCE` to 1000, and removing the `playable = stg_never`
gate from the 79 minor powers. Both are correct about what they fixed, and both
were tuning a mechanism that does not place AI empires in a total conversion.
**Plan:** [static-galaxy-plan.md](../planning/static-galaxy-plan.md).

## The finding

STNH's Qo'noS system initializer does not *select* the Klingon Empire. It
**creates** it:

```
.source/688086068/common/solar_system_initializers/Beta_Empire_Systems/STH_klingon_initialisers.txt:56
    create_country = {
        name = "NAME_klingon_empire"
        type = default
        authority = auth_kdf_high_council
        origin = "origin_klingon"
        species = event_target:klingonSpecies
        effect = { set_graphical_culture = klingon  set_country_flag = klingon_empire  … }
    }
```

STNH does this **43 times** with `type = default`, across 40 initializer files —
a real, expanding, diplomatic empire, not an enclave. The static galaxy
scenario's job is only to put that system on the map at that position; the
initializer does the rest.

**This is a vanilla pattern, not an STNH invention.** 22 vanilla initializer
files call `create_country`, and vanilla's own `com_sol_system` uses
`type = default` to place the **United Nations of Earth** as an AI neighbour on
the Commonwealth of Man start (`sol_initializers.txt:970`). Vanilla's other uses
are enclaves, factions, marauders, fallen empires and guardians.

## Why this explains six empty galaxies

`prescripted_countries/` is the **player's** roster. `spawn_enabled`,
`CUSTOM_EMPIRE_SPAWN_CHANCE` and the design database govern a lottery that
sprinkles the occasional preset into an otherwise random galaxy — vanilla's own
words, *"a small random chance of being spawned instead of a randomly-generated
AI empire"*. **A total conversion does not fill a galaxy that way, and STG has
been trying to for three fixes.**

It also explains the two things that never fit:

- **STNH leaves `CUSTOM_EMPIRE_SPAWN_CHANCE` at vanilla's 50** and has a Trek
  galaxy. It does not use the lottery.
- **STNH's random maps show the same symptom STG has.** No static map means no
  Trek home systems placed, which means no initializer runs, which means no
  `create_country`. The mod's own discussions report exactly that.

The 2026-08-26 save is consistent to the letter: 99 designs loaded, zero drawn,
and **one** STG initializer placed in the whole galaxy — the player's own.

## Locking the picker: an empty file overrides a vanilla scenario

STNH ships vanilla's `tiny`, `small`, `medium`, `large` and `huge` setup
scenarios as **0-byte files**. A same-named empty file overrides vanilla's and
the scenario ceases to exist, so only the mod's own maps appear in the
galaxy-shape picker. That is the mechanism for the seamless experience, proven in
a shipping mod, and it costs one empty file per vanilla scenario.

STG's picker currently offers fourteen entries and **none of them are STG's**:
vanilla's five, overridden with Ariphaos Galaxies' content, plus Ariphaos's nine
size variants. Removing the nine is a **content call about Ariphaos**, not an
error count, and [decision 11](11-fix-source-errors-dont-drop.md) requires it be
made out loud. Left open in the plan.

## What is not decided here

**Which binding pins an empire to its system** — STNH's
`spawn_weight = { base = 0 modifier = { add = 100000 has_country_flag = X } }`
paired with a `set_country_flag` in the initializer, or vanilla's documented
`spawn_design = <design>`, which names a prescripted design outright and
*"will ignore spawn_weight"*. The plan makes this the first question because
everything else hangs off it.

**Whether the prescripted pool can ever be drawn from** stays open —
`randomized` remains its live suspect
([83](83-design-database-is-not-the-cause.md),
[84](84-static-galaxy-is-the-mechanism.md)). The 99 stay as they are and stay
the player's roster. This decision makes that question stop gating the galaxy.

## Cost, honestly

Every one of STNH's 22 maps sets `random_hyperlanes = no`, but **only one of
them defines any lanes**: the BotF map, 468 systems and **892** `add_hyperlane`
lines. The other 21 — every canon map among them — carry zero, alongside
`num_hyperlanes = { min = 0 max = 0 }`. So a hand-cut lane graph is one map's
choice rather than the price of a static galaxy, and the systems are the cost
driver. This is still a phase, not a patch. What STG already owns is the
identity half — 36 real home systems ([23](23-real-home-systems.md)), 99
empires whose `create_country` blocks are a mechanical transcription of their
`prescripted_countries/` entries, and 1,444 Trek systems already harvested by
name from STNH's maps.
