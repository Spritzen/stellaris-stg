# 98 — A withdrawn setup scenario is still referenced by name, and the picker lock dangled 113 of vanilla's own triggers

**Status:** decided, 2026-08-28 — the content call is made and the lock stands.
**Corrects** [decision 88](88-lock-the-galaxy-picker.md) on the one sentence
that mattered: *"nothing references a scenario by name"* is false.
**Graded by** the Klingon run of 2026-08-28, the first live run since the lock
shipped and the run that made the cost visible at all.
**Follows** [decision 86](86-static-galaxy-scenario.md) and
[decision 87](87-static-map-lanes-are-generated.md), which are confirmed by the
same run's save.

## The finding

[Decision 88](88-lock-the-galaxy-picker.md) withdrew vanilla's five galaxy
sizes by occupying `map/setup_scenarios/{tiny,small,medium,large,huge}.txt`
with files that declare nothing. It reasoned the withdrawal was free:

> The setup screen enumerates the directory; nothing references a scenario by
> name. So there is no list to edit and no flag to unset.

**The first half is true and the second is false.** The *setup screen* does not
reference a scenario by name. **Script does**, and the game documents it:

```
galaxy_size - Checks whether the galaxy size if of a certain type
galaxy_size=medium
                        — logs/script_documentation/triggers.log
```

`galaxy_size` resolves a `setup_scenario` **by its `name`**. Withdrawing the
five declarations dangled every reference to them, and the engine says so at
load, once per site:

```
[19:48:57] parser_deferred_database_objects.cpp:84
           Failed to deferred read key reference tiny from database
           file: common/storm_types/00_storm_types.txt line: …
```

> **A declaration withdrawn by occupying its path is withdrawn from *script*
> too, not only from the screen that enumerates the directory.** "Nothing
> references it" is a claim about the whole merged tree, and it has to be
> measured there rather than reasoned from how the feature is presented.

## What it cost, measured

**353 records in the 2026-08-28 log, against 0 in every log on disk from before
the lock shipped** — `error.log.2026-08-08` and `error.log.2026-08-10` both
carry zero. It was the largest change in that log by two orders of magnitude,
and it is the entire +355 the run's record count moved by.

**The cost is behavioural, not cosmetic, and that is the part worth keeping.**
The references are almost all five-way ladders that scale something by galaxy
size, and with none of the five resolvable **each ladder collapses to its
base**:

| | before the lock | now |
|---|---|---|
| `storm_size_multiplier` (`03_script_values_cosmic_storms.txt`) | `base = 1`, then ×0.6 / ×0.8 / ×1 / ×1.2 / ×1.4 by size | **1, always** |
| `ai_habitat_cap` (`00_script_values.txt`) | `base = 0`, then `set =` 2 / 4 / 6 / 8 / 10 by size | **the base, 0**, until a later modifier moves it |

**113 sites in 11 of vanilla's own files** — `00_script_values.txt`,
`03_script_values_cosmic_storms.txt`, `05_script_values_grand_archive.txt`,
`06_script_values_biogenesis.txt`, `07_script_values_shroud.txt`,
`00_scripted_effects.txt`, `01_start_of_game_effects.txt`,
`gamesetup_settings.txt`, `overlord_initializers.txt`, and the Grand Archive,
nemesis, machine-age and galactic-features event files. **The harvest adds
none: all 113 are vanilla's**, which is why nothing in `src/` could have been
inspected to find this.

## The call: the lock stands

**Keep it.** The reasons decision 88 gave have not changed — STG is a total
conversion whose galaxy *is* the Alpha and Beta Quadrants, and there is
nothing to size. What changed is only that the price is now known instead of
assumed to be zero. **STNH pays the identical price** with five 0-byte files at
the same five paths, so this is the standing cost of the approach rather than
something STG does unusually.

Two things follow from making the call this way rather than by silence:

- **the ladders' collapse is now a written fact**, not a surprise waiting in a
  balance discussion six months from now. If storm sizes or AI habitat counts
  ever read wrong, this page is the first place to look;
- **the reversal is still one commit** and it is now a *smaller* one than
  decision 88 described: delete five files from `src/`, drop the YAGEM
  `exclude:`, and empty `galaxy_size_ack`. The check below goes to zero by
  itself the moment the sizes come back.

## What shipped

- **`check_galaxy_size_references`**, the fifty-third check. Every
  `galaxy_size = <name>` in the merged tree — vanilla's `common/` and `events/`
  and ours — must name a scenario something in `map/setup_scenarios/` declares,
  resolved with our copy of a path **shadowing** vanilla's rather than sorting
  against it, which is what makes a comment-only override contribute nothing.
- **`galaxy_size_ack` in `vendor.yml`**, holding exactly the five names, with
  what they cost written beside them. This is
  [decision 35](35-attach-edges-into-pruned-art.md)'s shape: **the ack silences
  the check, not the engine**, and 353 records a run is the standing price. The
  check prints the acked count on every run rather than hiding it, so the
  number stays in front of whoever reads the summary line.
- **A sixth name is a different defect and must not be acked without one.** It
  would mean a source mod referencing a galaxy size nobody declares, which
  vanilla never does.
- **The wrong sentence is corrected in `vendor.yml`'s `src_regression_ack`
  comment**, where it had been copied, as well as here. Decision 88 itself keeps
  its text and gains a `Corrected by` line
  ([style guide §7](../style-guide.md#7-decision-files-have-a-fixed-head)).

**Vanilla's floor is 0 of 113, necessarily** — vanilla declares all five sizes
it references — and that is exactly what makes the merged tree's 113 a
measurement of the lock rather than of the game. The control that says the check
can fail is emptying the ack, which reports all 113 and names
`00_script_values.txt:2486` first, the same file and ladder the engine did.

## Decision 88's own open question, answered the same day

**Both halves, and only one of them needed the game.**

- **Preselected — yes**, reported from the 2026-08-28 run. This is also what
  rules out the failure mode 88 was watching for, *a galaxy list the engine
  finds empty*: an empty list cannot preselect anything.
- **The only choice — yes, countable from disk.** Seven files reach
  `map/setup_scenarios/` after shadowing and **six declare nothing**: our five
  picker-lock overrides and vanilla's `static_galaxy_example.txt`, which is
  entirely commented out. Exactly one declaration reaches the engine,
  `STG_galaxy_alpha_beta`. `/stellaris/dlc` ships no `setup_scenarios`, so that
  one path is the whole population.

**88 counted this and was right**; what is new is that the count is no longer a
one-off. The `declared()` helper inside `check_galaxy_size_references` rebuilds
it on every run, because it is the same shadowing-aware enumeration the check
needs to resolve `galaxy_size` at all.

> **Half of what was filed as eyes-only was a disk question wearing a screen's
> clothes.** 88's own finding — *a scenario is offered because a file at that
> path declares it* — makes "is it the only choice" a count, not a look. Split a
> two-part question before spending a live run on it; here one half was thirty
> seconds of somebody's attention and the other was already in the tree.
