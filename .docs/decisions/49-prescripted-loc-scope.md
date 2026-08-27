# 49 — the other three prescripted-power files are clean; the truncation check stays where it is

**Resolved 2026-08-08.** Closes the first open item in plan.md §8.

## The question

[Decision 45](45-minor-power-names-truncated.md) found `stg_z_minor_powers.txt`
shipping **78 of its 79 empire names truncated** and 16 loc values that were
still the loc key. `check_prescripted_loc` was written to catch that class and
scoped to that one file. plan.md §8 then recorded the obvious worry:

> `stg_frontier_powers.txt`, `stg_major_powers.txt` and `stg_quadrant_powers.txt`
> came from the same source by the same hand and are **not** covered. Their names
> read plausibly — so did `Sovereignty`, `Commonwealth` and `Hegemony` for five
> months.

That is the right instinct — "reads plausibly" is exactly what decision 45's
defect looked like — so the three files were swept before deciding anything.

## The sweep: 0 real findings

Both of decision 45's failure modes were run against all 22 empires in the three
files, using the check's own predicates rather than by eye.

| | result |
|---|---|
| Values still shaped like a loc key (`^(PRESCRIPTED\|NAME\|EMPIRE_DESIGN\|SPEC)_\w+$`) | **0** |
| Ours a proper substring of any of STNH's 111 empire names | **1, and it is false** |

The single hit is `STG_EMPIRE_federation` — our `United Federation of Planets`
against STNH's `tngUnitedFederationofPlanets`, whose name resolves to
**`United Federation of Planets (2300s)`**. That is a *different empire*, one of
STNH's alt-timeline 2300s set, and the `(2300s)` era suffix is what makes our
canonical name read as a truncation of it. Ours is right and STNH's is a
differently-scoped entry.

## Why the premise did not hold

**These three files were hand-authored; only the minors were generated.**
Truncation is a *generator* failure — decision 45's names lost their leading
token because the conversion script split on a separator it did not handle. The
five majors landed in Phase 1 and the seventeen others in Phase 2, written
directly against Trek canon, so there was never a generator in the path to drop
a token. §8's "same source by the same hand" describes who *decided* the
content, not what *produced* the file, and only the second matters for this
defect class.

## The two halves therefore get different scopes

Recorded in the docstring of `check_prescripted_loc`, because someone will read
the narrow scope as an oversight.

- **Truncation stays on `stg_z_minor_powers.txt` alone.** Widening it needs an
  STG-empire → STNH-empire mapping, and there isn't one: these 22 diverge from
  STNH *on purpose*. `Bolian Union` against STNH's `Bolian League`, `Trill
  Symbiosis` against `Trill Administration`, `Confederacy of Vulcan` against
  `Vulcan High Command`, `Bajoran Republic` against `Bajoran Second Republic`.
  A check over them would be reporting a preference — the same reason decision
  45 left the six `Kessoks`/`Kessok` fields alone. Widening it would also mean a
  permanent ack for the Federation false positive, on a file with no generator
  behind it: an ack that can never start being useful, which is the ack-rot
  CLAUDE.md warns about. **The fix is cheap here only because the answer is "do
  nothing".**
- **The leaked-key half now covers all four files.** It asks nothing of the
  source — only whether our own value is still shaped like somebody's loc key,
  which is wrong no matter who wrote the file. It needs no mapping, produces no
  false positives, and costs nothing. It reports 0 outside the minors today; it
  exists so that a future hand-edit or a new generator cannot reintroduce the
  class silently.

The reported count moves **79 → 101**, which is now every prescripted empire STG
ships.

## What this is worth carrying forward

A suspicion in a planning document is a *hypothesis with a sweep attached*, not
a defect. This one was recorded honestly — with the reason it was plausible —
and it cost one sweep to retire. The failure would have been to widen the check
on the strength of the worry, buy a false positive, ack it, and end up with a
check that reports a number and cannot fail — decision 31's trap, reached from
the planning side instead of the code side.
