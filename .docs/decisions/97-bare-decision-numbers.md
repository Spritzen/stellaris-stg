# 97 — A third of every decision citation carries no path and no link, and three of them named the wrong decision

**Status:** decided, 2026-08-28 — measured from disk, no live run required.
**Follows** [decision 66](66-doc-inventory-checks.md), which established that a
citation can resolve perfectly and still describe a repo that has moved, and
[decision 89](89-retired-run-write-ups.md), whose renumbering sweep added
`check_link_labels` for the form it *had* got wrong.
**Corrects** three citations that sweep could not see: `tools/validate.py` said
`decision 88` for the `playable` gate, `tools/sources.py` said `decision 09` for
the source snapshot, and two `src/interface/*.gfx` files said `decision 42` for
event-picture geometry.

## The finding

A decision citation takes three forms, and only two of them had ever been read:

| form | example | read by |
|---|---|---|
| a path | `.docs/decisions/40-event-picture-geometry.md` | `check_code_citations` |
| a link | `[40](../decisions/40-event-picture-geometry.md)` | `check_link_labels` |
| **a bare number** | **`decision 40`, in a sentence** | **nothing** |

The first two carry a slug, so the 2026-08-27 renumbering could rewrite them
mechanically and `make docs` could check the result. The third carries no slug
and no href. There are **519 of them** — 245 in `tools/`, `src/` and
`vendor.yml`, 274 in the documents — which is about **a third of every decision
citation in the repo**, and no tool had looked at one.

## What was actually wrong

**Every bare number in the repo resolved.** All 519 named a decision file that
exists, which is why nothing anywhere said so and why an existence check would
not have found the defect. Three named the **wrong** decision, and all three are
survivors of the renumbering — confirmed against the pre-sweep tree rather than
inferred:

| site | said | pre-sweep filename | means today |
|---|---|---|---|
| `tools/validate.py` | `decision 88` | *(the removed `playable` decision)* | no number; the gate went on 2026-08-25 |
| `tools/sources.py` | `decision 09` | `09-source-snapshot.md` | [08](08-source-snapshot.md) |
| `src/interface/stg_arcsite_pictures.gfx`, `stg_story_pictures.gfx` | `decision 42` | `42-event-picture-geometry.md` | [40](40-event-picture-geometry.md) |

Today's `09` is *species-class keys*, today's `42` is *random-names pools
append*, and today's `88` is *the galaxy picker*. **All three read as plausible
citations**, which is the whole hazard: a renumbering does not leave a dangling
number, it leaves a number pointing somewhere else.

**One of them was invisible to grep as well as to the checker.** In
`tools/validate.py` the word `decision` ended one line and `88` began the next,
so every line-wise search — including the sweep's own — looked straight past it.
Joining wrapped comment lines before matching is not a nicety here; it is the
difference between finding that one and not.

## The decision

**Split the question, because only half of it is checkable.**

**`check_bare_decision_numbers` in `tools/check_docs.py`** asks the exact half:
does a bare number name a decision that exists? Floor **0 of 519** over live code
and every document, so there is no scope and no ratio
([rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter)).
It joins wrapped lines, reads ranges (`decisions 76 through 80`), and skips
markdown links because `check_link_labels` owns those and reading them twice
would report one defect in the weaker form. **The count goes on the summary
line**, which is the actual deliverable: a renumbering needs a worklist, and the
2026-08-27 sweep did not have one for this form.

**The semantic half is an audit, not a check**, and it is recorded in
[style guide §9](../style-guide.md#9-renaming-a-document-is-a-repo-wide-edit)
where the renumbering rule lives. After a sweep, `git blame` every bare citation
and read the ones whose line **predates** it — those are exactly the lines it
could not rewrite. That returned **12**, of which **3** were wrong, and it is
the thing that found all of them.

## What was measured and rejected

A vocabulary heuristic — does a word of the decision's slug appear near the
number — was built and measured against the real corpus first. **Its floor was
27 to 101 false positives** depending on the window, every one of them a correct
citation that simply did not repeat a slug word, and it could still pass a wrong
number on a single shared word. A check firing on forty correct things gets
ignored wholesale ([acks.md](../validation/acks.md)), so it was not shipped.

Requiring every bare number to carry a path was measured too: **240 of 245**
would have had to gain one within ±300 characters, against a rule that would
still have to be written into the style guide as prose nobody can enforce.

## Proof it can fail

Three controls, all reverted
([rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)):
a plain bare number in code, **the wrapped shape** with the number starting the
next line, and a range in a document. All three reported; the wrapped one is the
control that matters, because it is the shape that got past everything else.

**It also reported its own docstring twice**, on the worked example and then on
the comment explaining the first fix — the *documentation of a citation is not a
citation* class `strip_code()` exists for. Stripping backticks out of code files
was measured as the fix and **rejected**: docstring prose carries unpaired
backticks, so the span regex swallows whole sentences and would have hidden two
real citations to buy one. The examples are worded around instead. **A check
weakened to spare its own docstring is worth less than the docstring.**
