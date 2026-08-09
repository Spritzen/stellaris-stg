# 13 — The mod tree moves to `stg-build/`, and the deploy is a symlink

**Decided 2026-08-02, after the deployed copy was found five hours stale.**
Supersedes the copy half of [decision 07](07-launcher-local-mod-registration.md);
the `path=` derivation that decision settled is unchanged.

## What prompted it

`make deploy` copied the built tree into `/paradox/stellaris/mod/`. On
2026-08-02 the tree was rebuilt at 12:04 with every repair from
the 08-02 analysis in
it, and the deployed copy was still the 07:2x one — 23,432 files against 23,726.

Nothing was wrong. `make vendor` and `make validate` were both clean, and both
were clean about the *repo*, which is not what the game reads. Had the next live
run happened in that state it would have measured the pre-repair build, produced
~7,600 records against a prediction of ~1,751, and the obvious reading — "the
repairs did not work" — would have been wrong. That is a whole day of false
archaeology, available at any time, from a step someone forgot to run.

**A link cannot go stale.** That is the entire argument. The 16 GB write it also
saves is incidental.

## Two changes, and the second is what makes the first clean

**1. The tree moved from the repo root to `stg-build/`.** The repo root used to
*be* the mod root — `common/`, `gfx/`, `events/` and the rest sat beside
`tools/`, `src/`, `.docs/` and `.source/`.

**2. The deploy is one symlink to that one directory.**

The second needs the first. Symlinking a repo root that is also the mod root
hands the game `.source/` — 18.7 GB of source mods — along with `src/`, `tools/`
and `.docs/`. The copy path handled that with an `EXCLUDE` list of eleven
entries, and an exclude list is a thing you have to remember to update. With the
tree in its own directory the question does not arise: `stg-build/` contains the
mod and nothing else, so the deploy is `dest.symlink_to(host_ws/stg-build)` and
there is nothing to forget.

The link target is a **host** path, so it reads as broken inside the container
and resolves for the game — the same trick the `.mod` `path=` already used.

## What was deleted rather than kept

Three things stopped being able to fail, so they went:

- **`EXCLUDE` in `deploy.py`** (11 entries) and the whole copy path.
- **`reserved:` in `vendor.yml`** and `guard_reserved()`. It refused to write
  `tools/`, `src/`, `.docs/`, `.devcontainer/`, `.claude/`, because a source
  shipping `tools/` — *a real vanilla game directory as well as ours* — would
  have overwritten the build scripts with game data. Under `stg-build/` that
  collision is structurally impossible. It also un-breaks the case it guarded:
  `stg-build/tools/` is now just the game folder of that name, which a source is
  entitled to ship. None in the current harvest does.
- **`make deploy` and `make undeploy`**, now `make link` and `make unlink`. Two
  targets that did the same job by different mechanisms was one target too many.

`make dist`'s eighteen-pattern exclude list went the same way: it zips
`stg-build/` and nothing else.

## The near-miss during the port, which is the transferable part

`check_key_conflicts` looks a file's owning source up in
`.vendor-manifest.json`, whose keys are tree-relative. Repointing the scan at
`BUILD` while leaving the lookup as `f.relative_to(REPO)` made every key
`stg-build/common/…`, matched nothing, and fell through to the default — so
**every file in the build reported its source as `src/`**.

It did not error. It reported `386 common/ file(s) checked` exactly as before.
What it lost was the ability to see a conflict at all, because a conflict is two
*different* sources claiming a key and now there was only ever one. The
`star_names` warning — the one that blocks Phase 2 — vanished, and the other
five kept printing with the wrong mod named.

This is `CLAUDE.md`'s rule arriving from a new direction: **a check that cannot
fail is worse than an absent one, because it reports a number.** The failure
mode was not a check that never fired; it was a check whose *evidence* silently
became uniform. Caught only because the six standing warnings are a known
baseline and one of them disappeared.

**So: after any change to where a check reads from, diff the findings against
the previous run. Equal counts are not equal findings.** Post-restructure output
is warning-for-warning and attribution-for-attribution identical to
pre-restructure, which is the check that the port was faithful.

## What this does not change

- `descriptor.mod` and `thumbnail.png` now live in `src/`, like every other
  hand-written file that ends up in the mod, and vendor copies them into
  `stg-build/`. `check_descriptor` reads `src/descriptor.mod` so it still works
  before the first build.
- The launcher registry question is untouched — the `.mod` file and its `path=`
  are byte-identical to before.

## Confirmed by the next launch

This decision shipped with one open question: whether the launcher and the game
traverse a symlinked mod directory, which is not reasoning the container can
settle. **They do.** The link was created at 13:26 and the 13:35 run
(the 08-03 analysis) read
the build through it — `error.log` names
`gfx/models/ships/megastructures/quantum_catapult/stg_restored_vanilla_entities.asset`,
a file that exists nowhere but `stg-build/`. Wine resolves the link at the
filesystem layer, as reasoned.
