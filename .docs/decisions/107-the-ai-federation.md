# 107 — The Federation had no AI copy because Sol belongs to Real Space, and an `inline_script` reaches into a source's initializer without reproducing it

**Status:** decided, 2026-08-29
**Closes** [decision 86](86-static-galaxy-scenario.md)'s first open content call
— *"the one empire in the map whose AI copy does not exist, and it is the most
visible one… the first thing to fix after the mechanism is graded"* — which
[decision 106](106-sealed-system-is-vanilla-content.md) graded the same day.
**Follows** [decision 85](85-create-country-initializers.md), which established
that an AI Trek empire is created by its home system's initializer, and
[decision 101](101-first-contact-sounds-are-species-class-gated.md), which is
where `common/inline_scripts/` first became a file of ours.
**Adds a sixth question** to `check_static_galaxy`, which had asked whether
every join on the map *resolves* and never whether the seat it reserves is ever
*filled*.

## The defect

The static galaxy map reserves system `0` — Sol — for the Federation:

```
system = { id = "0" … initializer = sol_system_initializer
           spawn_weight = { base = 0 modifier = {
               add = 100000 has_country_flag = stg_united_federation_of_planets } } }
```

Every one of the other 20 empires on that map is reserved the same way **and
created by its own initializer**, through the guarded `create_country` that
[decision 85](85-create-country-initializers.md) found and
[decision 86](86-static-galaxy-scenario.md) generated 36 times into
`src/common/solar_system_initializers/stg_home_systems.txt`. The Federation's
was the one seat with nobody behind it: when the player picked anybody else,
Sol generated, Earth generated, and **the United Federation of Planets did not
exist in the galaxy at all**.

**Every static check said the map was fine, and every one of them was right.**
`sol_system_initializer` resolves. `stg_united_federation_of_planets` is
declared in `common/prescripted_flags/`. The position is unique, the id is
unique, the lanes reach it. Five questions about whether a join *resolves*
cannot see a join that resolves to a file which creates nobody — see "The check"
below.

## Why it had been left open

Sol is **not ours**. `common/solar_system_initializers/sol_initializers.txt` is
Real Space 4.0's, shadowing vanilla's file of the same name, and it is Real
Space's copy the engine loads. The other 36 AI copies live in an `src/` file
because the systems they sit in are ours; there is no `src/` file that can add
a line to a block another mod declares.

[Decision 86](86-static-galaxy-scenario.md) named two ways out and preferred the
second:

| candidate | what it costs |
|---|---|
| a `patches:` entry carrying the whole `create_country` | ~55 lines of empire identity hand-written into `vendor.yml`, where nothing joins it back to the Federation's prescripted entry |
| an STG-owned Sol generated from Real Space's geometry, Federation repointed | [decision 23](23-real-home-systems.md)'s *"pointing at it beats reproducing it"*, plus Earth's `continental_planet_earth_entity`, the `planet_earth`/`luna` flags and both asteroid belts, all of which a conversion drops |

## What shipped is a third option, and it costs neither

**`inline_script`.** The engine's own include: a preprocessor step that pastes a
named file's text at the point of reference, before anything is parsed. Vanilla
uses it in `common/solar_system_initializers/` nine times over —
`distant_stars_initializers.txt:150` is the short string form this uses.

| piece | where | how |
|---|---|---|
| the AI copy | `src/common/inline_scripts/stg_federation_ai_empire.txt` | **generated** — `tools/gen_home_systems.py`'s `INLINE_AI`, through the same `ai_empire_block` the other 36 use |
| the include | one line into Real Space's Earth, at planet level after its own `init_effect` | a `patches:` entry in `vendor.yml` |
| the guard | `NOT = { any_country = { has_country_flag = stg_united_federation_of_planets } }` | unchanged from the other 36 |

Real Space keeps Sol — geometry, entity, flags, belts and all — and the block
is **read out of the Federation's own `prescripted_countries/` entry on every
build**, so it cannot drift from the empire it copies the way the first
candidate's hand-written copy would. The patch adds one line and changes nothing
Real Space wrote.

**`generate_empire_home_planet = yes` is deliberately not added.**
`sol_system_initializer` is the single vanilla `usage = custom_empire`
initializer that omits it, and it is acked as such in `home_planet_generation_ack`.
Vanilla's own `com_sol_system` creates the United Nations of Earth on that same
Sol with `create_country` → `create_colony` → deposits → blockers → start
buildings and pops → leaders → `game_start.9`/`.33` and **no**
`generate_empire_home_planet` either. That sequence is exactly what
`ai_empire_block` emits, so the AI copy is self-sufficient and the player's Sol
is untouched.

## The anchor is sixteen lines, and that is the finding underneath the fix

`sol_initializers.txt` carries **seven Earths** — `sol_system_initializer`,
`com_sol_system`, `ai_sol_system`, `lost_colony_sol_system`,
`toxic_knights_sol_start`, `sol_system_fear_of_the_dark_system`,
`mindwarden_sol_system_init` — and their planet blocks are byte-identical down
to `entity = "continental_planet_earth_entity"`. Measured, not assumed:

| candidate anchor | occurrences |
|---|---|
| `flags = { planet_earth }` | 6 |
| `save_global_event_target_as = sol_system_earth` | 9 |
| `entity = "continental_planet_earth_entity"` | 7 |
| Earth's whole planet head, `name` through `init_effect` | not unique |
| **Earth's `init_effect` close through Luna and the planet after her** | **1** |

Uniqueness only arrives at Luna. `count: 1` is what makes that safe rather than
lucky: [`vendor.py`](../../tools/vendor.py) dies when the occurrence count is
anything but the declared one, so if Real Space ever edits any of those sixteen
lines the build stops instead of the patch landing on somebody else's Earth.

**The general lesson: in a file that repeats a well-known block, the shortest
unique anchor is not near the thing you are editing.** Six of the seven Earths
here are variants of the same scene, and every line a reader would reach for
first is one of the duplicated ones.

## The check

`check_static_galaxy` gains a sixth question: **a system reserved for an `stg_`
empire must name an initializer that actually creates it** —
`set_country_flag = <flag>` somewhere in that initializer's body, read with
`inline_script` includes expanded (`_expand_inline_scripts`, new). The block
form `inline_script = { script = X … }` is deliberately not followed: it takes
parameters, so pasting its text unbound would be a different file from the one
the engine assembles.

**Population 21, floor 0, and it is calibrated on three separate controls**
rather than on the one defect it was written for:

| state | findings |
|---|---|
| as shipped | **0** |
| the fragment removed — the state before this decision | **1**, naming system `0`, `sol_system_initializer` and the Federation |
| `set_country_flag = stg_klingon_empire` misspelt | **1**, naming system `2` |
| `set_country_flag = stg_romulan_star_empire` truncated | **1**, naming system `3` |

**The Klingon control found a bug in the first draft of the check.** It was
written as `f"set_country_flag = {cf}" not in body` — a substring test — and
`stg_klingon_empire` is a prefix of `stg_klingon_empire_TYPO`, so the misspelt
flag matched and the control reported clean. The condition is a `\b`-terminated
regex now. **The only reason it was caught is that the calibration broke an
empire the fix had not touched**; a control that only reproduces the original
defect would have passed a check that could not see a typo, which is
[check design rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)
arriving from a direction it does not name.

**Scope is `stg_` flags, for the reason the fifth question already carries:**
*"the country flag is the design key"* is our convention and vanilla's roster
does not share it.

**And one line of the check is a merge question, not a script question.** The
initializer bodies are collected **`BUILD` first**, with `setdefault`, because
Real Space shadows vanilla's `sol_initializers.txt` at the same path — reading
vanilla's copy would have asked the sixth question of a file nobody runs, and
answered it with vanilla's `sol_system_initializer`, which creates nobody
either. It would have reported the defect for the wrong reason and gone on
reporting it after the fix.

## What this does not settle

**It is not graded.** `make validate`, `make gen-check`, `make clutter` and
`make docs` are all clean, and a reference that resolves produces no log record
— the standing lesson of [decision 07](07-stnh-art-shadows-vanilla.md). What a
run answers, in one glance at the contacts list: **is there an AI Federation in
the galaxy, and is there exactly one?** Two would mean the guard did not see the
player's flag; that is the failure mode, and it is the same one
[decision 86](86-static-galaxy-scenario.md) built `common/prescripted_flags/` to
prevent for the other 36.

**The Terran Empire stays out of the map**, unchanged from
[decision 86](86-static-galaxy-scenario.md). Its home system is Sol and its
capital Earth, and it belongs to a mirror scenario when there is one. Note that
it does have its own initializer, `stg_terran_empire_home` — what it lacks is a
seat on the prime-universe map, which is a different question and still a
deliberate one.
