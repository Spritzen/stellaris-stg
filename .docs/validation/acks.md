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
[Decision 27](../decisions/27-merge-semantics-per-directory.md).

Where an ack is genuinely right, **scope it as narrowly as the evidence you
have**: `check_duplicate_textures` is acked *by directory* on the STNH side, so
the reviewed library stays silent and a **new** collision against the live
Walshicus set still reports
([44](../decisions/44-coalition-of-hope-takes-vul.md),
[51](../decisions/51-federation-texture-collisions.md)).

## Price an ack against a live run before writing one — and re-price the ones you inherit

`dangling_identifier_ack` held 33 species classes on the reasoning that the cost
was load-time only and would *"shrink by one per Phase 2 addition"*.

It shrank by nothing for five days. The 2026-08-07 run priced it at **439 errors,
21.8% of `error.log`** — and the cost was never load-time only, because an
unresolved species class falls through to the clothes selector's `default` and
**dresses a Trek people in human civilian clothing**.

The list is now empty and all 34 classes are declared
([decision 30](../decisions/30-declare-stub-species-classes.md)).

> **An ack whose justification is a *cost estimate* rather than a reviewed
> correctness argument is the kind that rots**: the estimate is never revisited,
> and `make validate` reports `ok` while the defect recurs every run.
> **If the fix is cheap, take the fix.**

## The largest ack in the project is a content call, and it says so

`galaxy_size_ack` holds five names and silences **353 records a run** — more
than every other ack combined. It is worth reading precisely because it is the
shape the section above warns about and is *not* the failure that section
describes.

The lock in [decision 88](../decisions/88-lock-the-galaxy-picker.md) withdrew
vanilla's five galaxy sizes, and `galaxy_size` turns out to resolve a
`setup_scenario` **by name**, so all five dangle
([98](../decisions/98-withdrawn-scenarios-are-referenced-by-name.md)). What
makes the ack legitimate is not that the cost is small — it is the largest in
the tree — but that:

- **the cost is measured, not estimated.** 353 records, 113 references, 11 files,
  and the behavioural consequence named specifically: each five-way size ladder
  in vanilla script collapses to its base, `ai_habitat_cap` to 0;
- **the thing being silenced is a deliberate content call**, re-made with that
  measurement on the table, not a defect waiting for someone to get around to;
- **it empties itself.** Restore the five sizes — the one-commit reversal
  decision 88 promises — and the list goes to `[]` and the check to 0 with no
  further edit;
- **a sixth entry is a different defect**, and the ack's own comment says so.
  A source mod referencing a size nobody declares is not this.

> **"The fix is cheap, take the fix" still holds — and here the fix has a price
> in content that the records do not.** That is the one case where a large ack
> beats a small repair, and it has to be argued in those terms rather than in
> record counts.

## What an ack entry owes the next reader

- What was looked at, and against what evidence — a live run, a decoded texture
  comparison, a count against vanilla.
- Why it cannot fire falsely later, or what would make it start firing again.
- A decision link where the reasoning runs longer than two lines.
