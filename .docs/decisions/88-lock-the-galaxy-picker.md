# 88 — The picker offers one galaxy, and withdrawing a scenario means occupying its path and declaring nothing

**Status:** decided, 2026-08-27
**Completes** [the plan](../planning/static-galaxy-plan.md)'s piece 3, the one it
deliberately left undone until an STG scenario was known to generate.
**Follows** [decision 87](87-static-map-lanes-are-generated.md), which is what
made the map worth defaulting to, and
[decision 86](86-static-galaxy-scenario.md), which built it.
**Corrected by** [decision 98](98-withdrawn-scenarios-are-referenced-by-name.md)
on one sentence below — *"nothing references a scenario by name"* is false.
`galaxy_size` is a trigger that resolves a `setup_scenario` by its name, so the
five withdrawals dangled 113 of vanilla's own references. The lock stands; the
text here is left as written and the price is recorded there.

## The finding

A galaxy scenario is offered **because a file at `map/setup_scenarios/` declares
it.** The setup screen enumerates the directory; nothing references a scenario
by name. So there is no list to edit and no flag to unset — **the way to
withdraw a scenario is to occupy its path and declare nothing.**

That splits the fifteen maps STG was shipping into two groups that need
different treatment, and getting the split wrong is the trap:

| | how it is removed | why not the other way |
|---|---|---|
| **9 `ariphaos_*.txt`** — Colossal 3k–6k, Enormous, Gargantuan, Massive, Nano, Titanic | `exclude:` on the source in `vendor.yml` | nothing else claims these paths, so excluding them removes them outright |
| **5 vanilla names** — tiny, small, medium, large, huge | a file in `src/` that declares nothing | **excluding these would do nothing.** Drop YAGEM's copies and *vanilla's own* load in their place. `/stellaris` is always underneath |
| **3 `map/ridiculous/*`** | `exclude:` | the engine never reads that folder; YAGEM ships them for a player to copy in by hand |

> **A vendored file is not the only thing at its path.** Excluding a source's
> copy of a contested path does not delete the path — it hands it to whoever is
> next, and vanilla is always next. When the goal is *absence*, exclusion is the
> wrong lever and an override that declares nothing is the right one.

STG already vendored a fix for this and lost it: **STNH ships all five vanilla
names as 0-byte files for exactly this reason**, but STNH is `additive_only` and
YAGEM sits ahead of it, so YAGEM's real scenarios won all five paths — carrying
`default = yes` on `medium.txt` with them.

## What shipped

- **`src/map/setup_scenarios/{tiny,small,medium,large,huge}.txt`** — comment-only
  files. STNH uses 0 bytes; a comment-only file parses identically and can say
  why it exists, which `make validate` requires of anything in `src/` shadowing
  vanilla. Vanilla's own `static_galaxy_example.txt` is the precedent for a
  scenario file that is entirely comments and declares nothing.
- **`exclude:` on Yet Another Galaxy Enhancement Mod** for its nine scenarios and
  `map/ridiculous/`. **The mod stays** — its other twelve files (defines,
  on_actions, astro and species names, `setup.gui`, loc) are why it is vendored,
  and [decision 11](11-fix-source-errors-dont-drop.md) governs the rest. This is
  a content call about twelve files, not a verdict on the source.
- **`default = yes` on STG's scenario**, generated. It was withheld while YAGEM's
  `medium.txt` still carried it — two defaults is worse than none — and that
  reason is now gone. STNH's `01 STH_galaxy_default_galaxy_map.txt` is the
  precedent for the key on a `static_galaxy_scenario`.
- **An `src_regression_ack` entry for the five.** The check that fired is
  [32](32-src-shadows-drop-source-declarations.md)'s, and it was right to: each
  override drops a `setup_scenario` declaration. Here that *is* the change, so
  it is acked with the reason rather than repaired.

**The result, counted rather than assumed: exactly one scenario declaration
reaches the engine.** The five overrides declare nothing, vanilla's five are
masked, and vanilla's `static_galaxy_example.txt` — which loads, and always did —
is entirely commented out.

`map/` is 19 files down to 7. `make validate`, `make clutter`, `make docs` and
`make gen-check` are clean.

## What this costs, said plainly

**There is now no way to play a random galaxy in STG.** Every galaxy size is
gone; the only game the mod offers is 95 systems, 21 empires, on canon
positions. That is the intent — a total conversion whose galaxy *is* the
Alpha and Beta Quadrants — but it means:

- **the map is the single point of failure.** Before this, a defect in
  `stg_alpha_beta_quadrant.txt` left fourteen working galaxies to fall back to.
  Now a defect in it is the whole mod. [87](87-static-map-lanes-are-generated.md)
  is the example of the kind of defect that reaches a live run;
- **restoring the sizes is one commit** — delete five files from `src/` and the
  exclude from `vendor.yml` — so this is reversible, and cheaply.

## What is still open

The picker has never been *seen* locked. The next run answers, before anything
else: **does the setup screen come up with The Known Galaxy already selected,
and is it the only choice?** A galaxy list the engine finds empty is the failure
mode to watch for, and it would be visible immediately.

The AI Federation remains open from [86](86-static-galaxy-scenario.md); nothing
here touches it.
