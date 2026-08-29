# 103 — `setup.log` is a load manifest, its one four-figure error class is the engine asking for loc no version of the game ships, and its trait dump is an external control we did not have

**Status:** decided, 2026-08-29
**Follows** [decision 102](102-syntax-checking-stopped-at-src.md), which named
the 1,605 records and deliberately did not chase them.

## Why it was opened

`setup.log` was found while answering a question about syntax coverage and
recorded as untriaged: 11,922 lines, never opened by anybody working on this
repo, carrying a four-figure class nothing had counted. The user's call was
that it is worth checking and that **the file is from the same run**, which it
is: its window is 20:36:59 → 20:37:30, entirely inside that run's 48.8 s
startup.

## What the file is

**A load manifest, not an error log**, and that is why 13 of its 15 classes are
worth nothing:

| | | |
|---|---|---|
| 3,347 | `modifier.cpp:3938` | `Static Modifier #N tag = … name = …` — a dump |
| 3,307 | `diplo_phrase.cpp:141` | every diplomatic phrase, numbered |
| **1,605** | **`ship_size.cpp:710`** | **`Missing ship size Localization Key: …`** |
| 767 / 481 | `trait.cpp:2918` / `:2904` | every trait, twice, in two shapes |
| **607** | **`trait.cpp:663`** | **`Made X into opposite of Y`** — derived, not a dump |
| 498 / 498 | `opinion_modifier.cpp:393` / `onaction.cpp:486` | dumps |
| 399 | `planet_class.cpp:595` | dump |
| 146 | `eventmanager.cpp:303` | namespace offsets |
| 28 / 23 / 17 / 2 | resources, songs, ethics, totals | dumps |

Two classes are not dumps. One is noise and one is evidence, and it is the
second that made the file worth opening.

## The 1,605 — closed, and not a defect at all

`Missing ship size Localization Key` resolves to **321 ship sizes × exactly
five suffixes**, with nothing left over:

```
build_speed_mult   build_cost_mult   upkeep_mult   hull_mult   hull_add
     321                321              321          321        321
```

Every declared ship size in the merged tree is hit — 321 of 322, and the
322nd is a `resources = {` block at column 0 that the size scan picks up and
the engine does not.

**Ours or theirs: 1,500 of the 1,605 belong to sizes only VANILLA declares.**
95 are sizes both trees declare and 10 are sizes only the mod declares —
Starbase Extended's `starbase_stronghold` and `starbase_headquarters`, five
keys each.

**And vanilla defines none of this family, for any size, including its own
corvette.** `corvette_build_speed_mult` is reported missing and exists in no
localisation file in vanilla or the build; so do `battleship_hull_add`,
`titan_upkeep_mult`, `starbase_citadel_hull_mult`. The engine asks every ship
size for a five-key modifier family and the game ships zero of them.

So the class is **0% ours by cause and not a defect in anything**. The ten
mod-only keys are deliberately left: defining them would make STG the only
thing in the game that answers a lookup all 319 vanilla ship sizes ignore, for
a tooltip family nothing else populates. **A uniform constant is not a
finding** — the same conclusion decision 50 reached about
`Duplicate of … added to entity system`, by the same route of counting it
rather than describing it.

## The 607 — an external control on `check_prescripted_empires`

`trait.cpp:663 Made X into opposite of Y` is the engine's **computed**
`opposites` graph: 607 undirected pairs over 333 traits, including the reverse
edges it derives rather than reads.

That is the database
[prescripted-empire-rules](../reference/prescripted-empire-rules.md) reasons
about, and the one whose mis-reading hid nine STG empires from the designer for
eleven runs ([83](83-design-database-is-not-the-cause.md)).
`check_prescripted_empires` derives it from files — merged tree, `stg-build/`
shadowing vanilla by path, through `_list_field` and `_balanced` — and until now
it was calibrated **only by reverting its own repairs**, which is an internal
control: it proves the check notices when the repair is undone, not that it is
reading the game's own relation.

Compared pair for pair:

```
engine (setup.log)  607
files  (validate)   607
agree               607      engine-only 0      files-only 0
```

**Exact.** The parser, the shadowing rule and the field reader are all confirmed
against the engine rather than against ourselves. That is the first external
oracle any check in this repo has had, and it cost one grep of a file that was
already on disk.

**One reading it corrects on the way.** A first pass concluded "zero STG traits
are in the graph", which is wrong: **59 of the 69 traits `src/` declares are in
it**, because those are vanilla keys we shadow and their `opposites` edges
survived the override — itself worth knowing, since dropping them is exactly
what [decision 07](07-stnh-art-shadows-vanilla.md) is about. It is the **120
vendored-only traits** that appear zero times, which is a different and much
weaker statement.

## What changes

Nothing in the build. `.docs/guides/live-runs.md` gains `setup.log` in the
procedure, because the cost of this triage was entirely in nobody having written
down what the file is — and its 1,605 will be in every log forever.

## The correction

[Decision 102](102-syntax-checking-stopped-at-src.md) and the open-questions
item it produced both say **1,375**. The real count is **1,605**; 1,375 was two
per-second buckets added together rather than the class counted. The decision
keeps its text ([style guide §7](../style-guide.md#7-decision-files-have-a-fixed-head));
the number is corrected here and in the item.
