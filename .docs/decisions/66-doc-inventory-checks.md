# 66 — A doc citation can resolve perfectly and still describe a repo that moved

**Status:** decided, 2026-08-09
**Follows** [decision 43](43-clutter-pass.md)'s dual-question shape and
[style guide §10](../style-guide.md#10-the-docs-get-the-same-treatment-the-mod-gets).

## The finding

`make docs` reported `ok — 0 warnings` throughout a full documentation pass that
found, in the same tree it had just passed:

| What was wrong | Why the checker could not see it |
|---|---|
| `.gitignore` cited `.docs/planning/plan.md §2`, split away a month earlier | `.gitignore` was outside `CODE_ROOTS` |
| `harvest-order.md` put Cinematic Camera at position 25; `vendor.yml` applies it at 21 | nothing compared the two |
| `check_texture_basenames` was in no document — the catalogue held 37 of 38 checks | nothing compared the catalogue to `validate.py` |
| `vendor.yml` said "any of the 48 sources"; the manifest declares 49 | nothing compared quoted counts to the manifest |
| `workflow.md`'s nav card promised "every `make` target" and listed 10 of 17 | nothing compared the list to the Makefile |
| the style guide's decision template required a `> **What changed**` line **no decision file has ever carried** | a rule with no check, which is the erosion §10 warns about |

**Every one of these is the same shape as the failure that created `make docs`** —
a pointer that reads as authoritative and is not — one level up. Decision 43
asked *is this file referenced* where every other check asked *does this
reference resolve*. This is that inversion applied to prose: not **does the path
resolve**, but **does the thing it describes still look like that**.

## What changed

Five inventory checks in `tools/check_docs.py`, and `CODE_ROOTS` widened to the
root dotfiles and `.devcontainer/`:

| Check | Compares |
|---|---|
| `check_make_targets` | documented targets ⟷ the Makefile's own `##` help lines |
| `check_validate_catalogue` | `validation/checks.md` ⟷ `validate.py`'s `def check_*` lines |
| `check_ack_keys` | `vendor.yml`'s `*_ack:` lists ⟷ the checks that read them |
| `check_harvest_order` | the numbered list in `harvest-order.md` ⟷ `vendor.yml`'s source order |
| `check_source_count` | every quoted source count ⟷ `len(vendor.yml sources)` |

**Each compares against a generated source of truth**, never a second
hand-written list — a check fed by a list somebody maintains is one more thing to
keep in sync, and it goes stale in the same breath as the doc it guards.

## Calibration

**Where a doc omits something, warn; where a doc names something that does not
exist, fail.** A curated list is allowed to be partial. A reader following a
pointer to nothing is not.

**Decision files are exempt from every one of these.** They name `make deploy`
and `make undeploy`, which became `link` and `unlink` in
[decision 12](12-build-dir-and-symlink-deploy.md). A decision records what was
true when it was made; treating that as a stale citation would push the checker
toward editing records, which is the one thing
[style guide §7](../style-guide.md#7-decision-files-have-a-fixed-head) forbids.

**Only plain `NN  Name` rows in the harvest list are compared.** The ranged rows
(`5–11  PD - …`) and the shipset block (`28+`) are deliberately a summary;
reading them as a spec is precisely how this check would start lying.

**A `make` target counts only inside backticks or a fence.** `two make two
entries match` and `not a change to make in passing` are both real sentences in
these docs. [Rule 8](../validation/check-design.md#8-a-reference-has-a-written-form-as-well-as-a-name)
— the written form is part of the name — applies to prose too.

## Rule 7, earned again, during the writing of this decision

Each new check was proven by re-introducing the defect it was written for and
watching it fail. `check_ack_keys` **passed its own mutation**: the test renamed
`dangling_art_ack:` to `dangling_art_acks:`, and a pattern anchored on `_ack:`
cannot match `_acks:` — so the key vanished from *both* sides of the comparison
and the difference was empty. The check was silent for the exact typo its
docstring named.

It now matches `_acks?:` and fails on both spellings.

> **A mutation test that the mutation passes is worth more than one it fails.**
> The check had looked correct, its docstring described the right defect, and it
> would have shipped reporting a number forever.
> [Rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed).

## Left alone

**`provenance.md` still says "48 sources".** It replays the previous build's
cached `patch_why` out of `.vendor-manifest.json`; `vendor.yml` is fixed and the
next `make vendor` carries it through. Generated files are not hand-corrected —
that is the whole reason they are generated.

**`check_source_count` does not read decisions or `provenance.md`**, for the two
different reasons above.
