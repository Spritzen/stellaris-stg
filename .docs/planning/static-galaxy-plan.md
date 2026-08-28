# The static galaxy plan — how STG actually gets a Trek galaxy

> **What** — the plan to place Trek empires by static galaxy scenario and
> `create_country` initializers, modelled on STNH, and to make STG's own
> scenarios the only ones the player can pick.
> **Open when** — working on why the galaxy is not Trek, or before touching
> `map/`, `prescripted_countries/` or `CUSTOM_EMPIRE_SPAWN_CHANCE` again.
> **Then** — [Decision 86](../decisions/86-static-galaxy-scenario.md) · [Decision 85](../decisions/85-create-country-initializers.md) · [Decision 84](../decisions/84-static-galaxy-is-the-mechanism.md) · [Open questions](open-questions.md) · [Status](status.md)

> ## Where this plan stands, 2026-08-27
>
> **All four pieces are built, and a live run has graded them** —
> [86](../decisions/86-static-galaxy-scenario.md),
> [87](../decisions/87-static-map-lanes-are-generated.md),
> [88](../decisions/88-lock-the-galaxy-picker.md). The 2026-08-27 Klingon save
> holds **20 AI Trek empires, one each, and no randomly generated empire**: the
> mechanism works. **One question failed and is fixed but unrun** — the map
> shipped with no lanes and generated a galaxy with one hyperlane in it, so the
> 162 generated lanes are what the next run grades. `make validate` clean and
> `make gen-check` 13 of 13 were **not** evidence about the galaxy: both were
> clean throughout all six empty ones, and clean over the lane defect too.
>
> | | |
> |---|---|
> | the binding | **`spawn_weight` + country flag.** STNH uses `spawn_design` zero times in 22 maps; it routes back through the draw that already failed six times |
> | the map | `src/map/setup_scenarios/stg_alpha_beta_quadrant.txt` — 95 systems, 21 empires, **162 generated hyperlanes**, every coordinate harvested from STNH's default galaxy map |
> | the AI copies | 36 `create_country` blocks, generated into `stg_home_systems.txt` |
> | **the piece this plan did not have** | the **country flag join**. `common/prescripted_flags/` is what gives the *player's* copy of an empire the flag the map weights on and the initializer guards on. STG shipped none. §2 below said the flag "exists because the initializer set it" — that is true only of the AI copy |
> | the check | `check_static_galaxy`, five questions, vanilla floor 0 |
> | still open | **an AI Federation** (Sol is Real Space's file) and the **Terran Empire**, whose Sol collides with the Federation's. Piece 3, the picker lock, is done — [88](../decisions/88-lock-the-galaxy-picker.md) |

Six galaxies have contained no Trek AI empire. Three fixes went into the
prescripted-empire pool and none moved the number, and the 2026-08-26 save
proved the pool itself is correct: all 99 designs loaded, `spawn_enabled = yes`
on every one, one prescripted country in the galaxy —
[decision 83](../decisions/83-design-database-is-not-the-cause.md).

**The pool was never the mechanism.** `prescripted_countries/` is what the
*player* picks from. AI Trek empires are placed by a **static galaxy scenario**
that puts a named system at a named position, whose **solar system initializer
`create_country`s the empire on the spot** —
[decision 85](../decisions/85-create-country-initializers.md). That is what STNH
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
| 3 | ~~**Lock the picker**~~ — **done 2026-08-27**, [88](../decisions/88-lock-the-galaxy-picker.md) | override files in `src/` + a `vendor.yml` exclude | STNH ships vanilla's five as 0-byte files |
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
`add_hyperlane` lines. The other 21, every canon map among them, carry **zero**
`add_hyperlane` (re-measure with `grep -c add_hyperlane <map>`). **So the lane
graph is not the cost driver — the systems are.**

> **RESOLVED 2026-08-27 by a live run, and the paragraph above is why it took
> one — [decision 87](../decisions/87-static-map-lanes-are-generated.md).**
> "The lane graph is not the cost driver" is true and was never the question.
> The question was what those 21 maps pair the empty lane list *with*, and the
> answer is not a parameter: **it is a script.** STNH's `events/STH_start.txt`
> runs `every_system = { connect_neighbour_stars = yes }` at game start, which
> walks `every_neighbor_system_euclidean` adding a lane to each neighbour. STG
> vendors neither that effect nor that event. Copying the header without it
> shipped a 95-system galaxy containing **one** hyperlane, and no log said so.
>
> **STG now generates its lanes into the file**, BotF's road — see
> `tools/gen_static_galaxy.py` and [87](../decisions/87-static-map-lanes-are-generated.md).
> `check_static_galaxy` treats a lane-less
> static map as an error, so this cannot ship twice.
>
> The `num_hyperlanes` re-measurement below stands and is unaffected: they do
> *not* all set `{ min = 0 max = 0 }`. Re-measured 2026-08-27: **10 do**
> (01, 02, 10, 12, 17, 18, 19, 20, 22, 23), **six** set `{ min = 5 max = 5 }`,
> **four** carry no `num_hyperlanes` line at all, and `04 tiny_alpha_beta` sets
> `{ min = 0.5 max = 1.0 }`. STG's scenario keeps 04's. With
> `random_hyperlanes = no` the key is inert either way — it is the density the
> setup screen offers for *random* generation — so it was left untouched rather
> than tuned, to keep the lanes the only variable the next run has to grade.

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
design outright and *"will ignore spawn_weight"*.

> **Settled 2026-08-27: `spawn_weight` + country flag**
> ([86](../decisions/86-static-galaxy-scenario.md)). STNH uses `spawn_design`
> **zero** times across all 22 maps, and it is the form that needs the design
> database to hand out a prescripted design — the draw six galaxies have
> already shown does not fill a galaxy. `spawn_weight` needs only a country
> flag, and the initializer that creates the empire sets that flag itself.

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

> **That is only true of the AI copy, and the missing half was the whole risk.**
> When the *player* picks the Klingons there is no initializer to set the flag,
> so the guard could not tell them from nobody playing the empire and would
> create a second Klingon Empire on Qo'noS. **`common/prescripted_flags/` is
> where the player's copy gets it** — vanilla's `humans2` carries
> `flag = empire_human_2`, whose entry sets `human_2` at country creation, and
> `com_sol_system` reads exactly that during galaxy generation. STG shipped no
> such file and no `flag =` line on any of its 99 empires until
> [decision 86](../decisions/86-static-galaxy-scenario.md).

**STG already owns most of the inputs.** Each of the 36 home-system initializers
([23](../decisions/23-real-home-systems.md)) has a matching prescripted empire
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

**Done 2026-08-27** — [decision 88](../decisions/88-lock-the-galaxy-picker.md),
which confirms the reasoning below and adds the part it did not have: the two
groups need *different* levers, because excluding a vanilla-named path does not
remove it, it hands it back to vanilla. STG's picker offered **fourteen**
entries, none of them ours:

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
> [decision 11](../decisions/11-fix-source-errors-dont-drop.md) still says say so
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
- every `add_hyperlane` endpoint is a declared system `id`, and **the graph is
  connected** — an unreachable component is a galaxy the player cannot cross and
  produces no log record at all. **A static map that declares no lanes is an
  error**, not a valid shape: this bullet said the opposite, and that is how a
  95-system galaxy with one hyperlane in it passed `make validate` every time
  ([87](../decisions/87-static-map-lanes-are-generated.md)). The 21 STNH maps
  that declare none build their network in a start-of-game script STG does not
  vendor. A scenario leaving `random_hyperlanes` on is exempt;
- no two systems share an `id` or a position;
- every `has_country_flag` a `spawn_weight` tests is `set_country_flag`-ed by
  some initializer, which is the join that silently fails.

The vanilla floor to calibrate against is vanilla's own five scenarios plus
STNH's 22 in `.source/`
([rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter)).

---

## Order of work

1. ~~**Settle `spawn_weight` + country flag versus `spawn_design`.**~~
   **Done 2026-08-27** — `spawn_weight`, [86](../decisions/86-static-galaxy-scenario.md).
2. ~~**One scenario, small, end to end.**~~ **Done** — 95 systems, 21 empires,
   coordinates harvested from STNH's default galaxy map. It shipped with **no**
   lanes, which cost the 2026-08-27 run; 162 are generated into the file now
   ([87](../decisions/87-static-map-lanes-are-generated.md)).
3. ~~**The generator** for the `create_country` initializers.~~ **Done** —
   `ai_empire_block` in `tools/gen_home_systems.py`, plus
   `tools/gen_empire_flags.py` for the country-flag half nobody had noticed was
   needed.
4. ~~**The check**, calibrated against vanilla and STNH.~~ **Done** —
   `check_static_galaxy`, floor 0 against vanilla and Ariphaos, 4,265 findings
   against STNH's own maps.
5. ~~**A live run.**~~ **Done 2026-08-27, and it moved the question** — three of
   decision 86's four questions came back good and the fourth, the hyperlanes,
   failed and is fixed ([87](../decisions/87-static-map-lanes-are-generated.md)).
   **What is left is one more run**, against the map with lanes in it: check you
   can fly out of Qo'noS, and that the setup screen comes up at all now the
   picker is locked ([88](../decisions/88-lock-the-galaxy-picker.md)).
6. **Then, in this order:** the AI Federation (Sol is Real Space's file — an
   `src/` override or a `vendor.yml` patch, and it is a content call);
   the Terran Empire and its Sol collision, which wants a mirror scenario;
   **scale to a full map**, adding the 15 minors that already have home systems;
   nebulae, which STNH hand-places by canon name. **Piece 3, the picker lock, is
   no longer last and is done** — its "not before, or there is nothing to
   select" condition was met the moment the map generated with lanes and 20 AI
   empires ([87](../decisions/87-static-map-lanes-are-generated.md),
   [88](../decisions/88-lock-the-galaxy-picker.md)).

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
([84](../decisions/84-static-galaxy-is-the-mechanism.md)).
