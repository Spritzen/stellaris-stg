# Run plans

> **What** — what to *do* in a live run, written **before** it, so the hours at
> the keyboard land on the questions nothing container-side can reach.
> **Open when** — the user says they are about to play, or asks what a
> playthrough should cover.
> **Then** — [Live runs](../guides/live-runs.md) · [Open questions](../planning/open-questions.md) · [Analyses](../analysis/README.md)

This category is the **before** half of a live run. [`../analysis/`](../analysis/)
is the after half — one file per run, written only on request, reading
`error.log` and reconciling it group by group.

The split exists because the two documents answer different questions. An
analysis says what a run measured. A run plan says what a run *can* measure and
what it would waste, which is a decision to make while the game is still closed:
**a screen nobody opened is a check that never ran**
([live-runs.md](../guides/live-runs.md#a-screen-nobody-opened-is-a-check-that-never-ran)),
and no amount of after-the-fact reading recovers an hour spent on the wrong
empire.

**This folder is empty, and that is the normal state.** A run plan is spent when
its run is over, and the two that stood here — a long Federation playthrough run
2026-08-10, and a long Confederacy of Vulcan playthrough run five times between
2026-08-22 and 2026-08-26 — were retired on 2026-08-27 once every observation
in them had landed in a decision
([89](../decisions/89-retired-run-write-ups.md)). What they found is in decisions
[76](../decisions/76-random-names-are-loc-keys.md)–[80](../decisions/80-selector-textures-that-resolve.md)
and [83](../decisions/83-design-database-is-not-the-cause.md); what they never
reached is in [status.md](../planning/status.md) under *what still has no in-game
evidence at all*.

**Write a new plan rather than re-running an old one.** The Vulcan plan was
re-run five times because each session was cut short on the same question —
whether the galaxy is Trek at all — so nothing further down its checklist was
ever reached. That question now has an answer and a plan of its own
([static-galaxy-plan.md](../planning/static-galaxy-plan.md)), and the 2026-08-27
Klingon run confirmed the mechanism works
([87](../decisions/87-static-map-lanes-are-generated.md)). **The next plan
written here can finally be about the checklist rather than the galaxy** — the
hulls above corvette, the dig sites, the anomalies and the story events, none of
which any run has reached.

## What a run plan owes the run

- **Name the empire, and say what it cannot reach.** That half is only cheap to
  know in advance.
- **Order the checklist by what a short session would still answer.** Every run
  so far has ended earlier than planned.
- **Leave room for observations inline**, under the item they answer, in a fenced
  block opening with `#OBSERVATIONS`. An observation under the wrong item is
  worth much less than one under the right item, because the item carries the
  expectation it should be read against.
- **State the build under test** — the `.vendor-manifest.json` stamp and the
  commit — so the write-up can say which fixes the run actually carried.
