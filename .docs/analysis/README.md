# Analyses

> **What** — measurements taken against a live run, one file per run, plus the
> filename convention that has tripped people up.
> **Open when** — writing up a live run, or a decision cites an analysis by a
> date-looking label.
> **Then** — [Live runs](../guides/live-runs.md) · [Status](../planning/status.md) · [Decisions index](../decisions/README.md)

**This folder is empty, and that is the normal state.** Analyses are written only
when asked for, and retired once every finding in them has landed somewhere that
outlives them — a decision, a check, or the baseline table in
[`../planning/status.md`](../planning/status.md).

**Two analyses stood here and were retired on 2026-08-27**
([decision 89](../decisions/89-retired-run-write-ups.md)): `2026-08-15`, a
container-side audit of Phase 4 (all four of its findings actioned the same day —
[73](../decisions/73-phase-4-count-corrections.md),
[74](../decisions/74-reachability-checks.md)), and `2026-08-16`, the short Vulcan
run of 2026-08-22 (six findings, all closed —
[78](../decisions/78-widen-attach-points-and-two-new-checks.md),
[79](../decisions/79-shipset-descs-and-home-system-names.md)). Their numbers live
on in those decisions and in the `error.log` baseline. **The slot labels leaked
into prose before they were retired**, so decisions and code comments still name
a run as "the 2026-08-16 analysis" or "the 08-12 analysis". **Read that as
provenance, not as a link** — it says the claim beside it was measured against a
run rather than reasoned from the container. Those files are gone and are not
coming back.

The back catalogue went the same way earlier: the slots `2026-08-01` through
`2026-08-14` were cleared on 2026-08-03, before the initial commit, so git does
not hold them either.

What survives every clearing is in [`../planning/status.md`](../planning/status.md)
and [`../guides/live-runs.md`](../guides/live-runs.md): the current baseline, the
per-group floors, and the rules below.

## Conventions for whatever gets written next

**Filenames are sequence slots, not dates.** Several runs happen on one real day,
so each analysis takes the next free `YYYY-MM-DD` rather than the day it was
written. Every file's header states the real session time. Order by filename, and
never read a gap between two filenames as elapsed time. The highest-numbered
filename is the current state of the build.

**A run label is an ordinal.** Only a decision's own `**Date:**` header is a real
date. This is the one trap in the convention and it is the reason the retired
labels above still need explaining.

**Say which platform.** Everything before 2026-08-02 was measured on Windows
under Proton, which is no longer installed
([decision 14](../decisions/14-native-linux-runtime.md)). Script-error counts
carry across that boundary; startup times and anything gfx-adjacent do not.

## What a new analysis owes the next one

[`../guides/live-runs.md`](../guides/live-runs.md) is the full procedure. In
short: state a number before the run; reconcile group by group, not at the total;
split the load window from the play window; make the register sum to the whole
log; publish each group's per-message breakdown so the next run can reconcile it;
and say **which screens were opened**, treating an unopened one as unmeasured
rather than as passing.

**And write it to be retired.** Every number an analysis establishes belongs in a
decision, a check or the baseline before the file itself is worth keeping — the
two that stood here were retired precisely because that had already happened.
