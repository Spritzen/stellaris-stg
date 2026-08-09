# 02 — Drop the Ariphaos Unofficial Patch

**Decided:** 2026-08-01

The `~~Ariphaos Unofficial Patch (4.2)` (workshop id 1995601384) is not part of
the harvest set.

**Why:** it declares `supported_version="v4.2.4"` against our 4.4 target and
shadows 256 vanilla files, of which **247 differ from current 4.4 vanilla**.
Each of those is either a fix worth having or a silent reversion of 4.4 content,
and telling which is which is a 247-file audit nobody is going to do.

**Consequence:** removes 24 of the 30 cross-mod conflicts that were counted at
the time. The remaining set was later measured properly and is larger than the
six recorded here — see decision 05 and plan.md §4.

**Revisit if:** you hit a specific 4.4 bug that Ariphaos is known to fix. Pull
that one file, not the mod.
