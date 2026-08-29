# 105 — Ten of the nineteen log files had never been named by any document, and the one the guide called empty had been carrying content for a day

**Status:** decided, 2026-08-29
**Follows** [decision 103](103-setup-log-is-a-load-manifest.md), which opened
`setup.log` and left the rest of the directory unread.
**Corrects** one row of [live-runs.md](../guides/live-runs.md).

## The defect

[live-runs.md](../guides/live-runs.md) carried a six-row table of the logs worth
reading. Its last row said:

> `debug.log`, `ai.log`, `info.log` — empty in every run so far

On 2026-08-29 `debug.log` was **10,663 bytes** and had been since the 2026-08-28
run — the same run three decisions were written from. The table had six rows for
a directory holding **nineteen log files** — 14 at the top level, five more
inside `script_documentation/`, plus two hand-kept rotations of `error.log`.

**Ten of the nineteen had never been named by any document or tool in the
repo**: `memory.log`, `profiler.log`, `event_data.log`, `script_profiling.log`,
`script_profiling_summary.log`, `pdxsdk.log`, and four of the five in
`script_documentation/` — the only version-exact description of our own build
that exists ([104](104-script-documentation-is-a-version-exact-oracle.md)). Only
its `triggers.log` had ever been cited, once, by
[98](98-withdrawn-scenarios-are-referenced-by-name.md).

Nothing was wrong with the *procedure* — `error.log` is still the right first
read. What was wrong is that a claim about the directory's shape was written once
and then had nothing holding it to the directory. That is the same failure
[check_docs.py](../../tools/check_docs.py) was written for, one level out: every
link in that table resolved perfectly while the sentence was false.

## What `debug.log` actually holds, since nobody had looked

72 records in the 2026-08-28 run. **71** are `economic_unit_template.cpp:29`
*Category already set to `X`, overriding*; **64 of those 71 come from vanilla's
own `common/specimens/specimens.txt`**, and the rest from vanilla buildings,
jobs, decisions and component templates. One `building_type.cpp:261` notice that
says in its own text it is expected. **0% ours** — the same verdict
[103](103-setup-log-is-a-load-manifest.md) reached about `setup.log`'s big class,
by the same method. Low value as evidence; the point is that a document said it
was empty and it was not.

## The eight empty channels, and what fills them

This is a different eight from the ten above — a file can be named by a document
and still have gone unread. Seven are created in one syscall at process start — `19:36:58.641`, before the
game version line — and never written. Their writers were established by string
search over `/stellaris/stellaris`, which ships **unstripped, with debug info**,
rather than from recollection:

* `event_data.log` — the `dump_event_data` console command
* `script_profiling.log`, `script_profiling_summary.log` — the `script_profiler`
  console command, run twice; the second run dumps
* `pdxsdk.log` — written by `libPDXSDK.so`, not the game, which is why it alone
  is mode `0644` where every other log is `0600`
* `ai.log`, `info.log`, `memory.log`, `profiler.log` — **no writer found.** The
  search that located the four above found no format string for these, so on
  this install nothing in a release build writes them

That asymmetry is worth keeping: four are *verified* writers and four are
*verified absences*, and the second claim is only as strong as the search that
made it.

## What ships

**`tools/logs.py` and `make logs`.** It censuses the directory against a table of
nineteen log files and fails when one changes state:

* a file the table calls **EMPTY now holds bytes** — an error, because seven of
  the eight are written only by a console command, so content there is *evidence
  somebody generated and nobody read*. This is the case the user asked for.
* a file **on disk that no row names** — an error. A game version can add a
  channel, and the whole point is not to find that out a year later.
* a file the table calls CARRIES that is empty or missing — a warning only, since
  a run that quits at the menu never reaches the stage that writes `time.log`.

It never reads `error.log`'s contents and does not replace the live-run
procedure. It asks whether the directory's **shape** changed, once, cheaply.

**Host state, so it skips rather than fails** where there is no log directory —
a check that fails on every clone gets ignored, and an ignored check is worse
than none.

**Control.** Against a scratch copy of the real directory with 16 bytes written
into `script_profiling.log` and one unnamed `newchannel.log` added, it reports
**2 errors and exits 1**; against the real directory, **19 files censused, 0
warnings**. Floor 0, and it can fail.

**And the table is held to the document.** `check_docs.py` compares
`tools/logs.py`'s table against
[reference/game-logs.md](../reference/game-logs.md) in both directions, so the
row that started this cannot rot again — which is the actual repair, the census
being only the half that finds it.
