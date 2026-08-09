# Validation — the checking system

> **What** — what `make validate` and `make clutter` ask, why each check exists,
> and the rules for adding one.
> **Open when** — a check fires, or you are about to write one.
> **Then** — [Workflow](../guides/workflow.md) · [Architecture](../architecture/README.md)

| File | |
|---|---|
| [checks.md](checks.md) | The catalogue: every check, grouped by the kind of question it asks |
| [check-design.md](check-design.md) | **Read before writing one.** Eleven rules, each earned by a check that lied |
| [acks.md](acks.md) | Where reviewed exceptions live, and the kind of ack that rots |
| [clutter.md](clutter.md) | The reachability closure — the one check that **deletes** |

## Why this category is this large

On 2026-08-01 `make validate` reported **`ok — 0 warnings` against a build
throwing ~8,780 errors.** Structure was fine; nothing was checking that one
file's *names* resolved against another's.

Everything here follows from that: the checks are the only thing standing between
a clean-looking build and a broken one, because **almost nothing in Stellaris
fails loudly.** A dropped file, a mistyped key, a texture at the wrong size and a
name that resolves to itself all produce exactly the same log output — none.

Two habits that follow, and they are the whole discipline:

- **A check that cannot fail is worse than an absent one, because it reports a
  number.** [Rule 7](check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed).
- **Calibrate against vanilla, and write the ratio next to the scope.**
  [Rule 4](check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand),
  [rule 11](check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter).
