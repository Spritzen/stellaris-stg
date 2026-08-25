# 19 — STNH's remaining prescripted empires, as AI-only minor powers

**Date:** 2026-08-03
**Status:** accepted; mechanism falsified 2026-08-25
**Builds on:** [18 — Walshicus' shipsets replace STNH's hulls](18-walshicus-shipsets-replace-stnh-hulls.md)
**Falsified in part by** [decision 88](88-playable-gates-the-design-database.md).
The 79 empires stay and everything below about their content still holds. What
does not is "AI-only": `playable` gates the engine's design DATABASE, not the
empire picker, and the galaxy generator draws AI empires from that database — so
`playable = stg_never` did not make these 79 AI-only, it made them unreachable.
They spawned in no galaxy in four live runs. The engine has no AI-only
prescripted empire; all 79 are playable now.

## What this adds

STNH ships 110 prescripted empires. After decision 18's eight frontier powers,
STG covered 22 of them. This brings across the remaining **79 as AI-only minor
powers** — spawnable, diplomatic, at war with each other, and absent from the
empire picker.

`101 prescripted empires`: 22 playable, 79 AI-only.

## Their identity is STNH's; their mechanics are not

This is the whole shape of the conversion, and it was forced by measurement
rather than chosen. Validating all 110 STNH empires against vanilla 4.4:

```
110 STNH empires; 0 use only vanilla-4.4-valid keys throughout
  29  origin:origin_galactic_explorers      7  trait:trait_reptilian
  17  origin:origin_militaristic            6  trait:trait_consummate_warriors
  14  origin:origin_materialists            6  trait:trait_untrustworthy
   …plus 23 STNH rooms and civic_antede_1 and friends
```

Every one of them names at least one origin, trait, civic or room defined in
STNH's `common/`, which STG does not vendor. So nothing political could be taken
across as written.

What *could*, and is the expensive half to author by hand, came across intact:

| Taken from STNH | Replaced |
|---|---|
| Empire name, adjective, ship prefix | authority / government / civics |
| Species name, plural, adjective | origin (→ `origin_default`) |
| Portrait group and ruler portrait | traits (→ vanilla, budget exactly 2) |
| Homeworld name, planet class, home system | room (→ vanilla personality room) |
| Heraldry | flag colours (STNH's `customcolorNNNN` come from `flags/colors.txt`, which vendor.yml excludes) |
| **Name lists** — see below | species class key |

Ethics were the one mechanical field that survived: STNH's are all vanilla's.
Each empire's authority/government/civic tuple is then **lifted whole from the
vanilla prescripted empire whose ethics its own most resemble**, for the reason
decision 18 gives — the game does not report an invalid combination, it refuses
to start.

## The name lists are converted, not invented

STNH's 169 name lists reference its own localisation (`CAITIAN_SHIP_Atrox`), and
bucket ships by *its* ship ladder (`saber`, `sovereign`, `steamrunner`), so they
are not usable as-is. But every token resolves — 135 of 135 on the first file
tested — so they were converted: tokens resolved through STNH's own English
localisation, re-keyed as `STG_N_`, and re-bucketed onto vanilla's ladder.

**70 name lists, 6,302 new loc keys**, all real Trek names rather than
constructed ones. This is the single largest content import in the project and
it cost no authoring.

## Ship art: 34 keep their own hulls, 45 borrow

The affordability of this whole file turns on one number. Of the 79:

- **34 keep their own STNH culture**, because it is one of
  `generic_01/02/05/06/07` — already harvested as donor art for the five
  cultures decision 18 left on the generator. `tools/gen_shipsets.py` now
  declares those five as graphical cultures and gives them vanilla-shaped
  entities, which is what makes 34 empires fly Trek hulls **for no new files**.
- **45 point at a Walshicus set** instead of their own STNH directory, by a
  quadrant default with per-species overrides.

The 45 are a deliberate compromise and should be read as one. A Gorn empire
flying Xindi hulls is wrong. The alternative was harvesting 38 more STNH culture
directories and running each through the generator at roughly 153 log records
apiece — **~5,800 records** — for empires you mostly meet as a portrait and an
occasional fleet. If a Walshicus set for one of them ever appears, moving it is
a one-line change.

`generic_06` has no cruiser, battleship, titan or juggernaut hull in STNH, so
empires on it fall back to `mammalian_01` at those sizes. Known and accepted.

Other fallbacks, all reported by the generator rather than assumed: **22 of 79
have no flag in `flags/trek/`** and use `neutral.dds`; one has no portrait group
and uses `human`; five had no convertible name list and borrow a sibling from
the same quadrant file.

## AI-only

`playable = stg_never`, a scripted trigger in
`src/common/scripted_triggers/stg_prescripted_triggers.txt` that is always
false. `playable` on a prescripted country takes a trigger **name** — vanilla
only ever writes `playable = has_shroud_dlc`, never an inline block — so an
always-false trigger is the mechanism, not `playable = { always = no }`.

`spawn_enabled = yes` throughout, so all 79 remain in the AI pool.

## Verification

`make validate` is clean (6 warnings, all the pre-existing
`common/random_names/` ones). Beyond it, every key all 101 empires name was
resolved against vanilla and the built tree — authority, government, civic,
ethic, planet class, room, species class, name list, graphical culture, portrait
group, flag, trait — with **0 unresolved**, and every trait budget checked
against vanilla's costs.

That check found two pre-existing defects in the original 22, neither of which
`make validate` can see:

- **The Borg spent 1 of their 2 trait points** (`enhanced_memory` +2,
  `learning_algorithms` +1, `uncanny` −1, `high_maintenance` −1), while
  `stg_quadrant_powers.txt`'s header claimed every list sums to exactly 2.
  Fixed with `trait_robot_durable`.
- The Bolians' `flag_spherical_5.dds` is **vanilla's**, in the `spherical`
  category, not STG's — correct, and the header already says STNH ships no
  Bolian flag. Recorded here because it looked like a dangling reference twice.

**A prescripted-empire key check belongs in `make validate`.** ~~Nothing in it
currently reads `src/prescripted_countries/`.~~ **Done** — `check_prescripted_empires`
exists, and it goes further than key resolution: it resolves traits, ethics and
portraits against vanilla's own `cost` / `opposites` / `allowed_archetypes` /
`allowed_ethics` / `leader_class` and the archetype trait budgets. It found 21
defects on its first calibrated run, 12 of them repairs applied that day.

**One of the two defects above turned out to be a repair that traded one failure
for another.** `trait_robot_durable` was added here to balance the Borg's trait
points; it is `opposites` with the `trait_robot_high_maintenance` it sits beside,
so the engine was not counting it at all and the empire was hidden from the
designer for eleven runs. The rule: **balance a trait budget against the list
that survives validation, not the one written down.**

## What only a live run can grade

1. ~~**Do 101 prescripted empires break galaxy generation?**~~ **No** — measured
   over two runs since (the 08-12 analysis,
   the 08-13 analysis).
2. ~~**Do the 34 on `generic_0*` render?**~~ **Costed, not graded.** The four
   `generic_*` donor cultures added 224 of the 506 missing mount points
   (08-12 §3) — 56 each, exactly the per-culture rate decision 18 predicted.
   Whether they *look* right is still item 3.
3. Whether 45 borrowed shipsets read as acceptable or as obviously wrong. Still
   open; only the user's eyes can settle it.
