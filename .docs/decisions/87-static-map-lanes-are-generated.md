# 87 — STNH builds its lane network in script, not in the map, and copying the empty map shipped a galaxy with one hyperlane in it

**Status:** decided, 2026-08-27
**Answers** [decision 86](86-static-galaxy-scenario.md)'s question 2, which named
this shape as "the single largest unknown in what shipped" and named the right
fallback. 86 is answered, not falsified.
**Corrects** [the plan](../planning/static-galaxy-plan.md)'s inference that a
lane-less STNH map means the engine builds the network, and the same inference
in `tools/gen_static_galaxy.py` and in `check_static_galaxy`'s own docstring.

## What the run showed

A Klingon game on *The Known Galaxy*, 2026-08-27, reported as having no
hyperlanes. The evidence, in the order [live-runs.md](../guides/live-runs.md)
asks for it:

| | |
|---|---|
| `error.log` | 187 KB, 1,267 lines — **1,263 of them inside the 47.1 s init window**. Ordinary load cost. |
| after galaxy generation | **four** errors: three `spawn_system: found no possible system for the new system to connect with` from Planetary Diversity's `events/pd_unique.txt`, and one `PLANET_SCALE_SYSTEM`/`ZOOM_STEPS_SYSTEM` size mismatch |
| the save | 98 galactic objects, **one hyperlane** — system 2 ↔ 95, length 12.13 |

**The log named the symptom and not the defect, and would never have named it.**
Those three `spawn_system` failures are a *consequence* of there being no lanes
to connect to; the one lane in the galaxy is the fourth such spawn, which found
a partner by luck. A galaxy with no lanes is not an engine error, so it produces
no record. The save is what settled it, again — the standing lesson of
[decision 83](83-design-database-is-not-the-cause.md).

## The finding

`map/setup_scenarios/stg_alpha_beta_quadrant.txt` declared 95 systems, set
`random_hyperlanes = no`, and carried no `add_hyperlane` line. Nothing else
built lanes, so there were none.

That shape was taken from STNH, where 21 of 22 maps carry exactly it. **The half
that was not taken is a script.** STNH builds the network at game start:

```
# events/STH_start.txt, after a "REMOVE DISTANT HYPERLANES" pass
every_system = { connect_neighbour_stars = yes }
```
```
# common/scripted_effects/STH_system_effects.txt
connect_neighbour_stars = {
	every_neighbor_system_euclidean = {
		limit = { NOT = { has_hyperlane_to = prev } }
		add_hyperlane = { from = this to = prev }
	}
}
```

STG vendors neither — `connect_neighbour_stars` appears nowhere in `stg-build/`.
`random_hyperlanes = no` with no lanes and no builder means exactly what it says.

> **The rule, and it is not about hyperlanes.** A parameter block copied from a
> source mod carries only what is *in the file*. STNH's scenario headers are
> half of a mechanism whose other half is an event, and a header read on its own
> reads as complete. **When a vendored parameter appears to work for its source
> and not for us, look for the script that source runs beside it** before
> changing the parameter.

`num_hyperlanes` was never the dial 86 hoped it might be: it is the density the
setup screen offers for **random** generation, so `random_hyperlanes = no` makes
it inert. It is left at 04's `{ min = 0.5 max = 1.0 }` untouched, so that the
next run grades the lanes and nothing else.

## What shipped

**The lanes are generated, from the same positions as the systems** — BotF's
road, the only one of STNH's 22 maps that puts its lanes in the file.
`tools/gen_static_galaxy.py` now emits them: each system links to its 3 nearest
stars within 50 units (vanilla's own `max_hyperlane_distance`, against a median
nearest neighbour of 26 here), unioned with a minimum spanning tree over the
same points. The MST is the part that matters — it is connected by construction
whatever the distances, so an unreachable component is impossible rather than
merely unlikely.

**162 lanes over 95 systems**: degree 2 to 5, mean 3.4, longest 49, every one of
the 21 empire homes reachable, and byte-identical on a re-run (`make gen-check`).

**`check_static_galaxy` is inverted.** It used to document that "a scenario with
no lanes is a valid scenario", and `if not lanes: continue` skipped the
connectivity test it already had. A static map declaring systems with
`random_hyperlanes = no` and no `add_hyperlane` is now an **error**. A scenario
that leaves `random_hyperlanes` on stays exempt: there the engine really does
build the network. Verified by regenerating the shipped defect against the new
check — it fails the build.

> **A check that tolerates the defect it was written to catch is worse than no
> check**, because it is also the thing that reports clean. `make validate` was
> green over that galaxy every time, and the tolerance was written into the
> docstring as though it were knowledge.

## What the same save settles for free

[86](86-static-galaxy-scenario.md)'s questions 3 and 4, both answered, both good:

- **20 AI Trek empires, one each, no duplicates** — `STG_EMPIRE_klingon` through
  `STG_EMPIRE_vidiian`, ids 0–19. 21 home systems are placed and the Federation
  is deliberately absent ([86](86-static-galaxy-scenario.md)), so 20 is the
  number that means the mechanism works end to end.
- **Exactly one Klingon Empire** while playing the Klingons. The
  `prescripted_flags` guard fired — the one thing in 86 that could not be
  validated statically.
- **No randomly generated empire appeared.** The four `%ADJECTIVE%` countries
  all carry primitive governments, which is `primitive_odds = 1.0`, not a breach
  of `num_empires = { min = 0 max = 0 }`.

**So decisions 84, 85 and 86 are confirmed by a live run.** The static galaxy is
the mechanism, the initializers create the empires, and the flag joins the
player's copy to the map. Only the roads between them were missing.

## What is still not known

The galaxy has never been played *with* lanes. This decision is graded by the
next run, and the questions are:

1. **Do the lanes render, and is the map traversable** from Qo'noS to Sol?
2. **Is 3.4 lanes per system the right density?** It is a choice, not a
   measurement — vanilla's own maps are the comparison, and `LANE_NEIGHBOURS` in
   `tools/gen_static_galaxy.py` is the dial.
3. **Does anything still call `spawn_system`** in `pd_unique.txt` and fail? With
   a connected graph those three errors should be gone; if they are not, they
   are a real Planetary Diversity finding rather than a symptom of ours.
4. The picker lock and the AI Federation remain open from
   [86](86-static-galaxy-scenario.md); neither is touched here.
