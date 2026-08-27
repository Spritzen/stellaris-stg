# The static galaxy plan — how STG actually gets a Trek galaxy

> **What** — the plan to place Trek empires by static galaxy scenario and
> `create_country` initializers, modelled on STNH, and to make STG's own
> scenarios the only ones the player can pick.
> **Open when** — working on why the galaxy is not Trek, or before touching
> `map/`, `prescripted_countries/` or `CUSTOM_EMPIRE_SPAWN_CHANCE` again.
> **Then** — [Decision 92](../decisions/92-create-country-initializers.md) · [Decision 91](../decisions/91-static-galaxy-is-the-mechanism.md) · [Open questions](open-questions.md) · [Status](status.md)

Six galaxies have contained no Trek AI empire. Three fixes went into the
prescripted-empire pool and none moved the number, and the 2026-08-26 save
proved the pool itself is correct: all 99 designs loaded, `spawn_enabled = yes`
on every one, one prescripted country in the galaxy —
[decision 90](../decisions/90-design-database-is-not-the-cause.md).

**The pool was never the mechanism.** `prescripted_countries/` is what the
*player* picks from. AI Trek empires are placed by a **static galaxy scenario**
that puts a named system at a named position, whose **solar system initializer
`create_country`s the empire on the spot** —
[decision 92](../decisions/92-create-country-initializers.md). That is what STNH
does 43 times, and what vanilla itself does for the United Nations of Earth in
`com_sol_system`. It touches none of `spawn_enabled`,
`CUSTOM_EMPIRE_SPAWN_CHANCE`, `playable` or `randomized`.

**Nothing below invalidates the 99 prescripted empires.** They stay exactly as
they are and remain the player's roster. This plan adds a second, parallel path
for the AI copies.

---

## The four pieces

| # | Piece | Where it lives | Modelled on |
|---|---|---|---|
| 1 | **Static galaxy scenarios** — systems, positions, hyperlanes | `src/map/setup_scenarios/stg_*.txt` | STNH's 22 maps; vanilla's `static_galaxy_example.txt` |
| 2 | **`create_country` initializers** — the empire itself | `src/common/solar_system_initializers/` | vanilla `com_sol_system`; STNH's 43 |
| 3 | **Lock the picker** — only STG scenarios selectable | empty override files (below) | STNH ships vanilla's five as 0-byte files |
| 4 | **A `make validate` check** — the map is a closed graph and every initializer it names exists | `tools/validate.py` | [check design](../validation/check-design.md) |

---

## 1. The scenarios

A `static_galaxy_scenario` is a header of galaxy parameters, then one
`system = { … }` line per star, then one `add_hyperlane = { … }` line per lane.

```
system = { id = "372" name = "Qo'nos" position = { x = -189 y = 164 }
           initializer = stg_klingon_empire_home
           spawn_weight = { base = 0 modifier = { add = 100000 has_country_flag = klingon_empire } } }
add_hyperlane = { from = "372" to = "373" }
```

**Every STNH map sets `random_hyperlanes = no`** — all 22 of them — but only
**one of the 22 defines a single lane**: `09 botf`, with 468 systems and **892**
`add_hyperlane` lines. The other 21, every canon map among them, pair
`random_hyperlanes = no` with `num_hyperlanes = { min = 0 max = 0 }` and **zero**
`add_hyperlane` (measured 2026-08-27; re-measure with
`grep -c add_hyperlane <map>`). **So the lane graph is not the cost driver — the
systems are.** What 21 maps do instead is worth settling before piece 1 starts,
because "no random lanes and no defined lanes" is a combination this project has
not yet seen run.

| STNH map | systems | weighted | note |
|---|---|---|---|
| `09 botf` | 468 | 99 | **smallest canon map** — the scale to aim at first |
| `04 tiny_alpha_beta` | 558 | 118 | |
| `03 alpha_beta_quadrant` | 869 | 123 | |
| `01 default_galaxy_map` | 1,436 | 151 | |
| `17 new_lore_galaxy_map` | 3,757 | 150 | the ceiling, not the target |

`spawn_weight = { base = 0 … }` means **no empire lands in that system except the
one the modifier matches** — that is what pins Qo'noS to the Klingons. Vanilla
documents a second form, `spawn_design = <design>`, which names a prescripted
design outright and *"will ignore spawn_weight"*; it is the simpler binding where
it works, and STG's design keys (`stg_klingon_empire`) are ready-made for it.
**Which of the two STG uses is the first thing to settle**, because piece 2
depends on it.

## 2. The initializers do the real work

STNH's Qo'noS initializer creates the Klingon Empire outright:

```
create_country = {
    name = "NAME_klingon_empire"
    type = default
    authority = auth_kdf_high_council
    civics = { … }  ethos = { … }  origin = "origin_klingon"
    species = event_target:klingonSpecies
    flag = { … }    ship_prefix = "IKS"
    effect = { set_graphical_culture = klingon  set_country_flag = klingon_empire  … }
}
```

`set_country_flag = klingon_empire` is the other half of the map's
`spawn_weight` — the flag exists because the initializer set it.

**STG already owns most of the inputs.** Each of the 36 home-system initializers
([25](../decisions/25-real-home-systems.md)) has a matching prescripted empire
carrying the exact name, adjective, ethics, civics, authority, government, flag,
ship prefix, graphical culture and species. **A `create_country` block is a
mechanical transcription of a `prescripted_countries/` entry**, which means it
should be *generated*, not hand-written — the same generator discipline as the
eleven existing ones, and `make gen-check` proves it stays a fixpoint.

## 3. Locking the picker — the answer is an empty file

**STNH ships vanilla's five setup scenarios as 0-byte files:**

```
.source/688086068/map/setup_scenarios/{tiny,small,medium,large,huge}.txt   →  0 bytes each
```

A same-named empty file overrides vanilla's and the scenario simply does not
exist, so `tiny`/`small`/`medium`/`large`/`huge` vanish from the galaxy-shape
picker. **That is the seamless experience, and it is proven in a shipping mod.**

STG's picker currently offers **fourteen** entries, none of them ours:

| source | entries |
|---|---|
| vanilla's five, overridden with **Ariphaos Galaxies**' content | `tiny` `small` `medium` `large` `huge` |
| Ariphaos's own additions | `Nano` `Massive` `Enormous` `Gargantuan` `Titanic` `Colossal - 3k/4k/5k/6k` |

To leave only STG's scenarios, both groups have to go: the five through empty
`src/map/setup_scenarios/` files (`src/` wins over vendored), the nine through a
`vendor.yml` exclude.

> **This is a content call, and it should be made deliberately rather than as a
> side effect.** Removing all nine Ariphaos scenarios removes most of what that
> source is *for*. That is a judgement about STG's galaxy, not an error count, so
> [invariant 4](../guides/working-rules.md) is satisfied either way — but
> [decision 12](../decisions/12-fix-source-errors-dont-drop.md) still says say so
> out loud. **Open:** keep Ariphaos's sizes as extra *static* maps at larger star
> counts, or drop them.

`priority` orders the list and the lowest-priority scenario is not automatically
the default; `default = yes` is. Exactly one STG scenario should carry it.

## 4. The check

A static map is a graph and a graph can be validated, which makes this cheap to
keep honest — [check design](../validation/check-design.md):

- every `initializer` a scenario names exists in
  `common/solar_system_initializers/`, and every `spawn_design` names a real
  prescripted design;
- every `add_hyperlane` endpoint is a declared system `id`, and **where a
  scenario defines lanes at all, the graph is connected** — an unreachable
  component is a galaxy the player cannot cross and produces no log record at
  all. 21 of STNH's 22 maps define none, so "no lanes" is a valid shape and must
  not be reported as a disconnected graph;
- no two systems share an `id` or a position;
- every `has_country_flag` a `spawn_weight` tests is `set_country_flag`-ed by
  some initializer, which is the join that silently fails.

The vanilla floor to calibrate against is vanilla's own five scenarios plus
STNH's 22 in `.source/`
([rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter)).

---

## Order of work

1. **Settle `spawn_weight` + country flag versus `spawn_design`.** One question,
   and pieces 1 and 2 both hang off it.
2. **One scenario, small, end to end** — ~100 systems, the 22 majors, quadrant
   and frontier powers on their real home systems. Follow the 21 maps that define
   no lanes before hand-cutting any; the one live run proves the mechanism, and
   whether lanes are needed at all is part of what it proves.
3. **The generator** for the `create_country` initializers, off
   `prescripted_countries/`.
4. **The check**, calibrated against vanilla and STNH.
5. **Scale to a full map**, then lock the picker (piece 3) once at least one STG
   scenario is playable — *not before, or there is nothing to select*.

## What this closes, and what it does not

**Closes:** the six-galaxy question, if it works — it is the only mechanism yet
found that vanilla and a shipping Trek conversion both use.

**Does not close:** whether the prescripted *pool* can ever be drawn from. That
question stays open in [open-questions.md](open-questions.md) with `randomized`
as its live suspect, because the 99 remain the player's roster and a player
picking the Klingons still needs them correct. This plan makes it stop mattering
for the galaxy.

**Do not raise or lower `CUSTOM_EMPIRE_SPAWN_CHANCE` again.** STNH leaves it at
vanilla's 50 and has a Trek galaxy
([91](../decisions/91-static-galaxy-is-the-mechanism.md)).
