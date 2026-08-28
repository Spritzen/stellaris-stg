# 89 — The five live-run write-ups are retired, and a retired document leaves a provenance label behind, not a link

**Status:** decided, 2026-08-28 — the files went late on 2026-08-27 and the
sweep that rewrote what they left ran straight through into the 28th
**Follows** [decision 66](66-doc-inventory-checks.md), whose `make docs` measured
the cost of this removal before any of it was rewritten.
**Corrects** nothing in the record: every finding in the five files had already
landed in a decision, a check or the `error.log` baseline before they went.

## What went, and what it cost to say so

Five documents, **2,408 lines**, removed at the maintainer's direction:

| File | What it was | Where its findings live now |
|---|---|---|
| `analysis/2026-08-15.md` | a container-side audit of Phase 4 — every claim decisions 52–72 make, re-measured | [73](73-phase-4-count-corrections.md), [74](74-reachability-checks.md) |
| `analysis/2026-08-16.md` | the short Vulcan run of 2026-08-22, read end to end | [78](78-widen-attach-points-and-two-new-checks.md), [79](79-shipset-descs-and-home-system-names.md) |
| `planning/ufp-run-remediation.md` | the eight-item remediation plan for the 2026-08-10 Federation run | [76](76-random-names-are-loc-keys.md)–[80](80-selector-textures-that-resolve.md) |
| `runs/ufp-long-campaign.md` | the Federation run plan, with its observations inline | same |
| `runs/vulcan-long-campaign.md` | the Vulcan run plan, re-run five times | [83](83-design-database-is-not-the-cause.md), and [status.md](../planning/status.md)'s baseline |

**The cost was 51 references**, and `make docs` named every one of them: 44
markdown links across fourteen documents, and **7 citations from live code** —
`tools/validate.py` twice, `tools/gen_check.py` twice, `tools/fix_ship_locators.py`,
`vendor.yml` twice and one `src/` localisation header. That is the same asymmetry
[decision 66](66-doc-inventory-checks.md) was built for: the docs can link to
each other perfectly while a file header in `tools/` points at nothing.

## The rule this settles

**A retired run document leaves its label behind, not its link.** "The 2026-08-22
Vulcan run", "the 2026-08-10 Federation remediation plan, item 2", "the 2026-08-15
audit" — read as **provenance**, not as a path. It says the claim beside it was
measured against a run rather than reasoned from the container, which is the part
worth keeping; the decision that carries the finding is what gets linked.

That is not a new rule. [`analysis/README.md`](../analysis/README.md) already said
it of the back catalogue cleared on 2026-08-03 — *"read that as provenance, not as
a link"* — and this pass applies it to every reference the five files left behind
rather than inventing a second convention for them.

**The two categories stay, empty.** `runs/` is the before half of a live run and
`analysis/` the after half, and both READMEs now carry their conventions with no
catalogue under them — which is the normal state, not a gap. An analysis is
written on request and **written to be retired**: every number in one belongs in a
decision, a check or the baseline before the file itself is worth keeping.

## The check the sweep needed and did not have

The 2026-08-27 renumbering had already shown that a link can resolve perfectly
and still say the wrong thing — 415 labels rewritten twice, every href correct,
`make docs` clean. Finding the one survivor of that (`[Decision 83]` pointing at
`78-widen-attach-points…`) took a scan nothing in the repo performed.

**`check_link_labels` now performs it**: a link whose href names a decision file
must not name a different number in its own text. **780 labels are read today and
all 780 agree.**

Only labels that are *about* a number are read — a bare `[77]`, a range, or
anything saying "decision 77". `[230 attach points]` and `[the 2026-08-08 review]`
are prose that happens to contain digits, and reading a number out of those is
how this check would start lying ([rule 8](../validation/check-design.md#8-a-reference-has-a-written-form-as-well-as-a-name)).
Both shapes were mutation-tested in both directions: the two wrong-number forms
fire, the two prose forms stay silent —
[rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed).

## What else the pass found, none of it about the deleted files

A full read of `.docs/` and of the comment headers in `tools/`, `src/` and
`vendor.yml` against what is on disk, the day after the static galaxy shipped:

- **`src/common/defines/stg_defines.txt` still said "STG ships no map at all"** —
  the single most misleading line in the tree the morning after
  [87](87-static-map-lanes-are-generated.md) put 20 AI Trek empires in a galaxy.
- **Phase 6 read "PLANNED 2026-08-26. Not started."** It shipped and ran on
  2026-08-27. [`scope.md`](../planning/scope.md)'s Trek-map row still said a static
  map "should be recorded here when it lands", and it had landed.
- **Three stale decision numbers** — `93` three times in [87](87-static-map-lanes-are-generated.md)
  and `94` once in [`static-galaxy-plan.md`](../planning/static-galaxy-plan.md),
  all survivors of the renumber, all bare prose the sweep's keyword rules could
  not see.
- **The build figures had drifted**: 22,409 files and 947 overwrites against the
  build's own 22,397 and 952, in three documents.
- **70 name lists said "one of the 79 minor powers"** — the roster has been 77
  since [82](82-remove-mirror-timeline-duplicates.md) removed two.
- **`STNH does it 40 times`** in two documents, where
  [85](85-create-country-initializers.md) measures **43** `create_country` blocks
  across 40 files. Re-measured against `.source/`: 43.
- **The `error.log` baseline had no column for the 2026-08-27 run**, the only one
  taken against the static galaxy.

**None of these was a dangling reference, and `make docs` could not have found
one of them.** It checks that references resolve and that inventories agree; it
cannot check that prose is true. That is still what a session's eyes are for.
