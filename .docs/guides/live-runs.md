# Live runs — reading `error.log` after the user plays

> **What** — the standard procedure for the only in-game evidence the container
> ever gets, and what a clean log does not mean.
> **Open when** — the user reports they have launched the game. Every time,
> before saying anything about how the run went.
> **Then** — [Run plans](../runs/README.md) · [Deployment](deployment.md) · [Analyses](../analysis/README.md) · [Open questions](../planning/open-questions.md)

The game runs on the **host**, not in the container. After `make vendor`, restart
the Stellaris launcher, enable *Star Trek Galaxies* in the playset, and launch.
No deploy step: the mod folder is a symlink to `stg-build/`.

**Container-side you can only validate statically. Never claim a change is
confirmed working in-game unless the user reports back that it is.** Say
"validates clean" and stop.

Game logs sit in the user-data folder one level above `mod/`, so they read at
`/paradox/stellaris/logs/`. `error.log` is the one that matters.

---

## Read `error.log` after every live run — standard practice

**Whenever the user reports they have launched the game, read
`/paradox/stellaris/logs/error.log` before saying anything about how the run
went.** It is the only in-game evidence the container ever gets, and it is cheap.
Skipping it means guessing.

Three things to establish, **in this order**:

1. **Volume.** A multi-MB `error.log` is a defect, not noise. Compare against the
   ~1 MB a clean vanilla run produces, and against the current baseline in
   [planning/status.md](../planning/status.md).
2. **When.** Cross-reference the per-second histogram against `time.log`'s
   `Startup real time`. Errors *inside* the init window are a one-off load cost;
   errors *after* it recur during play and matter far more per occurrence.
3. **Ours or theirs.** Grep the file paths in the messages. Vanilla and
   third-party mod errors exist and are not ours to fix — say which is which
   rather than reporting a total.

Distinguishing (2) is the part that is easy to get wrong and changes the
conclusion completely, so do it explicitly rather than assuming.

## A screen nobody opened is a check that never ran

The log is a **sample of that class, not a census.** Eleven runs reconciled to
the record while nine prescripted empires, the Borg included, could not be
selected at all — those records only appear when someone opens the empire
designer.

Worse, sweeping the *rule* behind those findings turned up nine more empires with
the same defect, all AI-only, which no log will ever show: the engine drops a
trait silently rather than refusing it.

> **When the log reveals a defect that has a rule behind it** — a vanilla
> `opposites` list, an archetype budget, an `allowed_ethics` gate — **never
> repair only the instances it named. Derive the rule and sweep the tree.**

## Eyes-only findings

A reference that resolves produces **no log record**. Rooms, city sets, weapon
mount positions, leader backgrounds, music titles, texture dimensions and ship
name pools are all graded by eye or not at all — `make validate` clean is not
evidence for any of them. That is the standing lesson of
[decision 08](../decisions/08-stnh-art-shadows-vanilla.md) and
[decision 42](../decisions/42-event-picture-geometry.md).

[Open questions](../planning/open-questions.md) keeps the list of what is
currently waiting on somebody's eyes, and what specifically to look at.

**Decide that before the game opens, not after.** A run plan in
[`../runs/`](../runs/README.md) turns that list into an ordered checklist for one
empire — including what that empire *cannot* reach, which is the part that is
only cheap to know in advance.

## Writing it up

Analyses are written **only when asked for**, one file per live run, under
[`.docs/analysis/`](../analysis/) — see that folder's README for the filename
convention, which is a sequence slot rather than a date and has tripped people up.
