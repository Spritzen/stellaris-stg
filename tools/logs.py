#!/usr/bin/env python3
"""Census the game's log directory, and fail when a file changes state.

WHY THIS EXISTS. `.docs/guides/live-runs.md` carried a six-row table of the log
files worth reading, and one of its rows said `debug.log`, `ai.log` and
`info.log` were "empty in every run so far". On 2026-08-29 `debug.log` was
10,663 bytes and had been since the 2026-08-28 run. Ten of the nineteen log
files in that directory had never been named by any document or tool at all, and
four of the ten are in `logs/script_documentation/` -- five files the engine
regenerates on every launch from the MERGED database, which is the only
version-exact description of our own build that exists anywhere.

Nothing had ever asked what was in that directory, so nothing noticed when the
answer changed. That is the whole defect, and it is the same shape as the one
`check_docs.py` was written for: a document can describe a repo that has moved
while every link in it still resolves.

WHAT THIS CHECKS, which is deliberately not "are there errors".

  * A file the table calls EMPTY now carries bytes. This is the one that
    matters and the one the user asked for: seven of the eight empties are
    written only by a console command or a debug build, so a non-zero
    `script_profiling.log` means somebody ran the profiler and the results are
    sitting there unread. It is reported as an ERROR -- not because content is
    a defect, but because it is evidence nobody has looked at, and this tool is
    the only thing that will ever say so.
  * A file appeared that the table does not name. A new game version adding a
    log channel should not be found by accident a year later.
  * A file the table calls CARRIES is empty or missing. Weaker: a run that
    quit at the menu never reaches the stages that write `time.log`, so this
    warns rather than fails.

WHAT IT DOES NOT CHECK. It never reads `error.log`'s contents, and it is not a
substitute for the live-run procedure in `.docs/guides/live-runs.md`. It
answers "has this directory's SHAPE changed", once, cheaply, so that the
procedure's assumptions stay true.

HOST STATE, NOT REPO STATE. The log directory belongs to the game, which runs
on the host; a container that has never launched it has nothing to census. That
is a skip with a message, not a failure -- the alternative is a check that
fails on every clone and is therefore ignored.

The table below is the source of truth. `check_docs.py` holds
`.docs/reference/game-logs.md` to it, so the two cannot drift the way
live-runs.md did.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

LOGS = Path(os.environ.get("STELLARIS_USER_DIR", "/paradox/stellaris")) / "logs"

# Rotated copies of error.log, kept by hand across runs -- decision 98 reads
# two of them as the before-side of a comparison. Matched, not enumerated.
ROTATED = re.compile(r"error\.log\.\d{4}-\d{2}-\d{2}$")

# state: CARRIES -- written in every normal run; EMPTY -- created at process
# start and never written by a release build on this install.
#
# "what fills it" is EVIDENCE, not recollection. The four marked (binary) were
# confirmed by string-searching /stellaris/stellaris, which ships unstripped;
# the four marked (no writer) are the ones where that search found no format
# string referencing them at all.
CARRIES, EMPTY = "carries", "empty"

TABLE: list[tuple[str, str, str]] = [
    # name, state, what it is / what fills it
    ("error.log", CARRIES,
     "the errors. The standard read after every live run -- live-runs.md"),
    ("setup.log", CARRIES,
     "a load manifest, not an error log. 15 classes, 13 of them dumps -- decision 103"),
    ("game.log", CARRIES,
     "version, defines, galaxy seed, and one line per event a player or the AI answered"),
    ("system.log", CARRIES,
     "GPU, audio and OS init. Written before the database loads; attached to crash reports"),
    ("time.log", CARRIES,
     "`Startup real time`, which is the only way to split init-window records from in-play ones"),
    ("debug.log", CARRIES,
     "engine load-time notices. 72 records in the 2026-08-28 run, 71 of them "
     "`Category already set to X, overriding`, 64 from vanilla's specimens.txt. None ours"),
    ("ai.log", EMPTY, "the AI debug channel (no writer)"),
    ("info.log", EMPTY, "general info channel (no writer)"),
    ("memory.log", EMPTY, "memory instrumentation (no writer)"),
    ("profiler.log", EMPTY, "engine profiler (no writer)"),
    ("event_data.log", EMPTY,
     "filled by the `dump_event_data` console command (binary)"),
    ("script_profiling.log", EMPTY,
     "filled by the `script_profiler` console command -- run it twice, the second dumps (binary)"),
    ("script_profiling_summary.log", EMPTY,
     "the summary half of the same dump (binary)"),
    ("pdxsdk.log", EMPTY,
     "written by libPDXSDK.so, not the game -- which is why it alone is mode 0644 (binary)"),
    ("script_documentation/effects.log", CARRIES,
     "1,056 engine effects with syntax and supported scopes -- decision 104"),
    ("script_documentation/triggers.log", CARRIES,
     "1,087 engine triggers, same shape -- decision 104"),
    ("script_documentation/scopes.log", CARRIES,
     "99 scope links, with supported scopes and output scope -- decision 104"),
    ("script_documentation/modifiers.log", CARRIES,
     "47,510 modifier names. NOT a complete allowlist -- decision 104"),
    ("script_documentation/localizations.log", CARRIES,
     "the `[Scope.Property]` vocabulary, 44 scopes -- decision 104"),
]

GRN, YEL, RED, DIM, OFF = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"


def size_str(n: int) -> str:
    if n == 0:
        return "0"
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n / 1024 / 1024:.1f} MB"


def main() -> int:
    if not LOGS.is_dir():
        print(f"{DIM}logs: {LOGS} not present -- the game runs on the host and "
              f"this container has no log directory to census. Skipped.{OFF}")
        return 0

    errors: list[str] = []
    warnings: list[str] = []
    named = {name for name, _, _ in TABLE}

    print(f"{DIM}{LOGS}{OFF}")
    for name, state, what in TABLE:
        p = LOGS / name
        if not p.is_file():
            warnings.append(f"{name}: named by the table, not on disk")
            print(f"  {YEL}missing{OFF}  {name}")
            continue
        n = p.stat().st_size
        if state is EMPTY and n > 0:
            errors.append(
                f"{name}: the table calls this EMPTY and it now holds "
                f"{size_str(n)}. READ IT. Then record what filled it in "
                f"tools/logs.py's table and .docs/reference/game-logs.md.")
            mark = f"{RED}FILLED {OFF}"
        elif state is CARRIES and n == 0:
            warnings.append(
                f"{name}: the table calls this CARRIES and it is empty -- "
                f"normal if the run quit before that stage")
            mark = f"{YEL}empty  {OFF}"
        else:
            mark = f"{GRN}ok     {OFF}"
        print(f"  {mark} {name:44s} {size_str(n):>8s}  {DIM}{what}{OFF}")

    # Anything on disk the table does not name.
    for p in sorted(LOGS.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(LOGS))
        if rel in named or ROTATED.search(rel):
            continue
        errors.append(
            f"{rel}: on disk and named by no row of the table. A game version "
            f"can add a log channel; find out what writes it, then add it to "
            f"tools/logs.py and .docs/reference/game-logs.md.")

    rot = sorted(p.name for p in LOGS.iterdir()
                 if p.is_file() and ROTATED.search(p.name))
    if rot:
        print(f"  {DIM}rotated  {len(rot)} kept copy(ies) of error.log: "
              f"{', '.join(rot)}{OFF}")

    for w in warnings:
        print(f"{YEL}warn{OFF}  {w}")
    for e in errors:
        print(f"{RED}error{OFF} {e}")
    if errors:
        print(f"\n{RED}{len(errors)} error(s){OFF}, {len(warnings)} warning(s)")
        return 1
    print(f"\n{GRN}ok{OFF} — {len(TABLE)} file(s) censused, "
          f"{len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
