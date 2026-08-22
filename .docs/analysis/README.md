# Analyses

> **What** — measurements taken against a live run, one file per run, plus the
> filename convention that has tripped people up.
> **Open when** — writing up a live run, or a decision cites an analysis by a
> date-looking label.
> **Then** — [Live runs](../guides/live-runs.md) · [Status](../planning/status.md) · [Decisions index](../decisions/README.md)

| File | |
|---|---|
| [2026-08-15](2026-08-15.md) | **Phase 4, audited against disk.** Every claim decisions 55–77 make, re-measured: the content resolves and the ship-name and music figures verify exactly; three file headers cite the wrong count, the story pool's "21%" is the Federation's rate alone, and `weight` — decision 76's own headline finding — has no check behind it. **All four findings actioned the same day** ([78](../decisions/78-phase-4-count-corrections.md), [79](../decisions/79-reachability-checks.md)); **its finding 1 is still open** — the two runs since have both ended before reaching any of decisions 74–77 |
| [2026-08-16](2026-08-16.md) | **The short Vulcan run, 2026-08-22.** The cleanest log yet — 4 post-init records against 174 — and the 98-record Planetary Diversity cluster and the 19 missing-localisation records are both gone, so two 2026-08-10 fixes are confirmed in game by silence. The play window was 26 minutes, so dig sites, anomalies, story events and every hull above corvette went unreached again. Six findings and **all six are now closed**, none by a live run. Finding 1 — the **female** master clothes selector, never patched — landed with the check that holds it ([83](../decisions/83-widen-attach-points-and-two-new-checks.md)). Findings 3 and 4 were **both larger than recorded**: the shipset descriptions were 30 keys wrong rather than 7, and the 40 Eridani duplicate was seven names in six systems from three generator bugs rather than one paste. Finding 2 — six declared cultures with no city art — was **not a defect**, because `fallback` is the mechanism and vanilla's own header says so ([84](../decisions/84-shipset-descs-and-home-system-names.md)). Findings 5 and 6 were **struck on measurement** and the file records why. **Three of the six dissolved or grew on re-measurement, which is the thing to expect of a finding taken once** |

**The back catalogue is gone.** The slots `2026-08-01` through `2026-08-14` were
cleared on 2026-08-03, before the initial commit, so git does not hold them
either. Analyses are now written only when asked for, one file per live run.

**[2026-08-15](2026-08-15.md) is the exception that proves the convention**: it
is a container-side audit, not a reading of `error.log`, and it says so in its
own first paragraph. Everything else here should be a live run, as
[2026-08-16](2026-08-16.md) is.

What survived the clearing is in [`../planning/status.md`](../planning/status.md)
and [`../guides/live-runs.md`](../guides/live-runs.md): the current baseline, the
per-group floors, and the rules below.
Findings that had a decision behind them are in
[`../decisions/`](../decisions/), which states each one in full. Several
decisions still cite a cleared analysis by its slot label ("the 08-12
analysis"). **Read that as provenance, not as a link** — it says the claim beside
it was measured against a live run rather than reasoned from the container. The
file itself is gone and is not coming back.

## Conventions for whatever gets written next

**Filenames are sequence slots, not dates.** Several runs happen on one real day,
so each analysis takes the next free `YYYY-MM-DD` rather than the day it was
written. Every file's header states the real session time. Order by filename, and
never read a gap between two filenames as elapsed time. The highest-numbered
filename is the current state of the build.

**The slot labels leaked**, and this is the one trap in the convention: decisions
and code comments name runs by these slots too ("the 2026-08-11 run"), so a label
can sit ahead of the real calendar date. A run label is an ordinal. Only a
decision's own `**Date:**` header is a real date.

**Say which platform.** Everything before 2026-08-02 was measured on Windows
under Proton, which is no longer installed
([decision 15](../decisions/15-native-linux-runtime.md)). Script-error counts
carry across that boundary; startup times and anything gfx-adjacent do not.

## What a new analysis owes the next one

[`../guides/live-runs.md`](../guides/live-runs.md) is the full procedure. In short: state a number before the run; reconcile group by group,
not at the total; split the load window from the play window; make the register
sum to the whole log; publish each group's per-message breakdown so the next run
can reconcile it; and say **which screens were opened**, treating an unopened one
as unmeasured rather than as passing.
