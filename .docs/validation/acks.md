# Acks — silencing a check for a case someone has looked at

> **What** — where reviewed exceptions live, and the standing warning about the
> kind of ack that rots.
> **Open when** — a check fires on something you believe is fine, and you are
> about to silence it.
> **Then** — [The check catalogue](checks.md) · [How to write a check](check-design.md)

Known and reviewed exceptions live in `vendor.yml` under `*_ack:` lists. **A
check that cannot be silenced for a case someone has actually looked at gets
ignored wholesale**, which is worse. Anything not in an ack list is a new finding.

## Prefer a content comparison to an ack

An ack entry stays silent **forever**. A content comparison starts firing again
by itself the day the two bodies diverge.

Both conflict checks compare *content*, not just names: two sources claiming one
key with bodies that differ only in whitespace, or setting one define to the same
value, are not in conflict and are not reported. Two `defines_conflict_ack`
entries were deleted on those grounds rather than kept.
[Decision 29](../decisions/29-merge-semantics-per-directory.md).

Where an ack is genuinely right, **scope it as narrowly as the evidence you
have**: `check_duplicate_textures` is acked *by directory* on the STNH side, so
the reviewed library stays silent and a **new** collision against the live
Walshicus set still reports
([46](../decisions/46-coalition-of-hope-takes-vul.md),
[54](../decisions/54-federation-texture-collisions.md)).

## Price an ack against a live run before writing one — and re-price the ones you inherit

`dangling_identifier_ack` held 33 species classes on the reasoning that the cost
was load-time only and would *"shrink by one per Phase 2 addition"*.

It shrank by nothing for five days. The 2026-08-07 run priced it at **439 errors,
21.8% of `error.log`** — and the cost was never load-time only, because an
unresolved species class falls through to the clothes selector's `default` and
**dresses a Trek people in human civilian clothing**.

The list is now empty and all 34 classes are declared
([decision 32](../decisions/32-declare-stub-species-classes.md)).

> **An ack whose justification is a *cost estimate* rather than a reviewed
> correctness argument is the kind that rots**: the estimate is never revisited,
> and `make validate` reports `ok` while the defect recurs every run.
> **If the fix is cheap, take the fix.**

## What an ack entry owes the next reader

- What was looked at, and against what evidence — a live run, a decoded texture
  comparison, a count against vanilla.
- Why it cannot fire falsely later, or what would make it start firing again.
- A decision link where the reasoning runs longer than two lines.
