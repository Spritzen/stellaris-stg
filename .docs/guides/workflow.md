# Workflow — the make targets and the day-to-day loop

> **What** — every `make` target, what the daily loop is, and what each step
> actually guarantees.
> **Open when** — starting any piece of work, or unsure which command to run
> after an edit.
> **Then** — [Source snapshots](source-snapshots.md) · [What `make validate` checks](../validation/checks.md) · [Live runs](live-runs.md)

`make help` prints this list from the Makefile itself, so it can never go stale.

```bash
# sources — the only things that read /workshop
make sources-status  # has anything updated upstream since we snapshotted it?
make sources-diff ID=<id>   # read that change before accepting it
make sources-sync [ID=<id>] # accept it into .source/
make sources-list    # what is snapshotted right now

# build
make vendor          # rebuild stg-build/ from .source/ + src/, then prune
make provenance      # regenerate .docs/provenance.md from the last build
make clean-vendor    # remove every generated file

# check
make validate        # BOM, brace balance, loc syntax, descriptor drift, cross-references
make clutter         # census: is every file reachable, shadowing, or kept?
make clutter-vanilla # the same closure over /stellaris — the calibration floor
make docs            # every doc link and code citation resolves
make gen-check       # every generator still reproduces src/ (DEEP=1 to round-trip)
make logs            # census the game's log directory for any file that changed state
make fix-bom         # add the missing UTF-8 BOM to src/localisation/*.yml

# deploy and ship
make link            # ONE-TIME: symlink stg-build/ into /paradox/stellaris/mod
make mod-file        # rewrite just the .mod descriptor, without relinking
make unlink          # remove it again
make dist            # zip the built mod (for archiving — STG is never published)
make game-version    # confirm what the installed game expects
```

## The loop

**`make vendor` → `make validate` → launch.**

The mod folder holds a symlink to `stg-build/`, so a rebuild is live the moment
it finishes and there is no copy step to forget. `make link` is needed once, or
again only if the mod folder is wiped. That is
[decision 12](../decisions/12-build-dir-and-symlink-deploy.md), and it exists
because a copy sat five hours stale and would have made the next live run
measure the wrong build.

Run `make validate` after **any** script edit — it catches the silent-drop
failures CWTools doesn't flag. CWTools itself lints live in the editor against
`/stellaris`.

Run `make clutter` after any change to **what is harvested**.

Run `make docs` after any change to `.docs/` or to a code comment that cites it.

Run `make logs` after a live run, beside reading `error.log`. It censuses
`/paradox/stellaris/logs/` against the table in `tools/logs.py` and fails when a
file changes state — an "empty" channel that now carries bytes is evidence
somebody generated and nobody read. It skips cleanly where there is no log
directory, because the game runs on the host.
[Every file in that directory](../reference/game-logs.md), and
[decision 105](../decisions/105-ten-log-files-nothing-had-named.md) for the
stale row that earned it.

Run `make gen-check` after touching a `tools/gen_*.py` or `tools/fix_*.py`, and
before committing anything they produced. It runs each generator over the tree it
already made and diffs `src/` against itself: **a correct generator is a
fixpoint**, so the floor is 0 by construction rather than by calibration. It
backs `src/` and `.vendor-cache/` up first and restores them in a `finally`, so
it is safe to run against a dirty tree.

`DEEP=1` inserts a `make vendor` between two runs of each generator that reads
the built tree. That is the only level that can catch a generator **feeding on
its own output** — the defect that made `gen_star_names.py` write a pool a third
the size on its second run, found after the 2026-08-10 Federation run reported
unlocalised nebula names
([decision 78](../decisions/78-widen-attach-points-and-two-new-checks.md)) — and
it costs a full build per generator.

## `make vendor` also deletes

`make vendor` removes files nothing references, which is the one way the build's
output is **not** fully described by `vendor.yml` — the manifest plus the closure
in `tools/clutter.py` describe it together, and
[`.docs/provenance.md`](../provenance.md) lists every removal.

Nothing is destroyed: `.source/` is untouched and the closure re-derives itself
every build, so content that gains a declaration comes back by itself.
[Decision 43](../decisions/43-clutter-pass.md), and
[the clutter closure](../validation/clutter.md) for how it decides.

## What each step does and does not prove

| Command | Proves | Does **not** prove |
|---|---|---|
| `make vendor` | the manifest replayed cleanly | that any of it resolves |
| `make validate` | names resolve against the merged tree | that anything renders, or is the right size |
| `make clutter` | every file is reachable, shadowing or kept | that a kept file is used well |
| `make link` | the symlink and `.mod` are written | that the launcher can see the mod ([deployment](deployment.md)) |
| a clean `error.log` | nothing *logged* | that a screen nobody opened is fine ([live runs](live-runs.md)) |

That last column is the whole reason this project's checks exist. `make validate`
once reported `ok — 0 warnings` against a build throwing ~8,780 errors.
