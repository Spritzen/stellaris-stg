# Documentation style guide

> **What** — how documentation in this repo is written, named and linked, and the
> checks that enforce it.
> **Open when** — writing any `.docs/` file, splitting one, or adding a header
> comment to code that cites one.
> **Then** — [The documentation map](README.md) · [Decisions index](decisions/README.md)

Everything here exists for one reader: **a session that starts cold, knows
nothing, and has a budget.** Every rule below is a rule about getting that reader
to the one paragraph they need without reading the other forty thousand words.

---

## 1. Every document opens with a nav card

The first thing after the `# Title` is a blockquote of two to four lines:

```markdown
> **What** — one sentence saying what is in this file.
> **Open when** — the trigger that should make a session open it.
> **Before this** — a doc to read first, if one is genuinely required.
> **Then** — where to go next, as links.
```

`What` and `Open when` are **required**. `Before this` appears only where reading
out of order would actually mislead. `Then` is the important one and the one
that gets skipped: it is the hop that saves the next session a search.

**`Open when` is a trigger, not a summary.** "Open when a file came from the
wrong source mod" is useful; "Open when you want to know about harvest order"
is the title again.

## 2. One document answers one question

If a file needs two nav cards to describe itself, it is two files. Splitting is
cheap; a session reading 1,300 lines to find a paragraph is not.

**Length is a symptom, not a rule.** A 400-line file that answers one question
is fine. A 150-line file that answers three should be three files in a folder,
with a `README.md` naming them.

## 3. Folders are categories, and every folder has a README

A folder without a `README.md` is a folder a session has to `ls` and guess at.
The README states what the category is for and lists its files with a one-line
hook each — the same hook as the file's own `What` line, so the two can be
checked against each other.

`.docs/decisions/` is the one exception to "categorise by folder": it is a
numbered log, the number is the address, and several hundred citations in
`tools/`, `src/` and `vendor.yml` point at `.docs/decisions/NN-slug.md`. It is
categorised by [its index](decisions/README.md) instead. See §9. Re-measure with:

```bash
grep -rhoE '\.docs/decisions/[0-9]{2}-[a-z0-9-]+\.md' tools src vendor.yml | wc -l
```

## 4. Cite, don't summarise

If a fact is written down somewhere, link it. A summary beside a link is a
second copy that drifts, and the drift is invisible — both files read as
confident.

The exception is the **one-line hook**, which is deliberately too short to drift
into a contradiction: `[decision 40](…) — event pictures are re-cut at harvest`.
If your summary needs a subordinate clause, link instead.

## 5. If it is written down nowhere else, it is not a comment — it is a missing doc

Carried over from the code-comment rule, and it is the rule that keeps this
guide from losing things. Non-derivable facts — a value that broke a live run, a
key that cannot be prefixed, a measurement — must survive somewhere with a path.
Write the doc, then cite it. **Never delete the fact to shorten the prose.**

Where a fact belongs:

| The fact is… | It goes in |
|---|---|
| a resolved question, with the reasoning and what it cost | [`decisions/`](decisions/) — one file, numbered |
| how to *do* something in this repo | [`guides/`](guides/) |
| how the build is *designed* | [`architecture/`](architecture/) |
| what a check asks and why it is calibrated that way | [`validation/`](validation/) |
| what is done, what is next, what is open | [`planning/`](planning/) |
| what a live run measured | [`analysis/`](analysis/) |
| a lookup table, a layout, an external link | [`reference/`](reference/) |

## 6. Numbers get a date and a source

Every count in these docs was true of one build on one day. Write it as
`22,311 files (build of 2026-08-08)`, not `22,311 files`. A number with no date
is a number nobody can retire, and this project has had four sections go stale
for exactly that reason.

**Prefer telling the reader how to re-measure it.** `Read the count off
.vendor-manifest.json` outlives any figure in prose.

## 7. Decision files have a fixed head

```markdown
# NN — <the finding, as a sentence>

**Status:** decided | closed | superseded by NN | reviewed and left, YYYY-MM-DD
**Supersedes / Follows / Falsified by:** links, where any apply
```

The title is the *finding*, not the topic: `58 — The music player draws the
declaration name, and 16 had no key` beats `58 — Music player names`. The index
is written from these titles, so a vague one costs every future session.

Decisions have **no nav card** — this head answers the same question in a
different shape, and `make docs` checks them accordingly. What it enforces is
the title (`# NN — …`, number matching the filename), a dated status line, and
a row in [the index](decisions/README.md).

Five decisions — [22](decisions/22-group-c-texture-references.md) through
[27](decisions/27-merge-semantics-per-directory.md), bar 26 — write their status
as an italic `*Decided 2026-08-03…*` paragraph instead. Those **stay as written**:
a decision records what was true when it was made, so retrofitting its head is
editing a record. The checker accepts both forms. See §9 and the migration note
in the index.

A decision is never edited to say something different. When it turns out wrong,
it keeps its text and gains a `Falsified by` line — [63](decisions/63-city-set-canvas-overflow.md)
and [81](decisions/81-city-horizon-band.md) are the worked
example, and the pair is worth more than either would be alone.

## 8. Link with relative paths, always

`[decision 40](../decisions/40-event-picture-geometry.md)` from inside `.docs/`,
`[decision 40](.docs/decisions/40-event-picture-geometry.md)` from the repo root.
Never a bare filename, never an absolute path.

Code cites by **repo-relative path** in a comment: `See .docs/validation/check-design.md`.
`tools/check_docs.py` reads both forms and fails on either dangling.

**Never link into a generated tree** — `stg-build/`, `.source/`, `.vendor-cache/`
or `dist/`. Such a link resolves only after a build and disappears while one is
running, so it makes `make docs` pass or fail on the state of the working tree
rather than on the documentation. Cite the tracked input instead: `src/` for our
own content, [`provenance.md`](provenance.md) for what the merge did with it.
`check_docs.py` rejects these by name rather than reporting them as missing, so
the message names the rule. Added 2026-08-25, after the one such link in the tree
failed the check transiently during a rebuild.

## 9. Renaming a document is a repo-wide edit

`.docs/` paths appear in `tools/*.py` docstrings, `src/` file headers,
`vendor.yml` comments and other docs. Moving a file without rewriting them
leaves citations that resolve to nothing while still reading as authoritative.

**Run `make docs` before and after any move.** That is the whole enforcement
story, and it is why the numbered decision files stay where they are by default.

**They moved once, on 2026-08-27**, when seven superseded decisions were removed
and the remaining 88 renumbered to 01–88 with no gaps. That is the measure of
what a move costs: the number is the address for several hundred citations, a
number used before that date does not map onto today's index, and the sweep that
rewrote them introduced a second bug of its own — 415 link *labels* renumbered
twice, invisible to `make docs` because it validated hrefs and not the text
beside them. [The index](decisions/README.md) carries the dated note; the label
check now exists (§10).

## 10. The docs get the same treatment the mod gets

Every rule above that can be checked, is:

```bash
make docs        # references resolve, and documented inventories match the repo
```

A rule with no check behind it is a rule that erodes silently — the standing
lesson of this project, applied to its own documentation. `make docs` exists
because `.docs/planning/clutter-pass.md` was cited from `tools/clutter.py` and
[decision 43](decisions/43-clutter-pass.md) for five days after it stopped
existing, and nothing anywhere said so.

It asks two kinds of question:

| | |
|---|---|
| **Does every reference resolve?** | every markdown link and heading anchor; **every numbered link label, against the decision its href names**; every `.docs/` path cited from `tools/`, `src/`, `vendor.yml`, the `Makefile` and the root dotfiles; every doc's nav card; every category README |
| **Does the documented inventory match the repo?** | `make` targets against the Makefile; the check catalogue against `validate.py`'s own `def` lines; `vendor.yml`'s `*_ack` lists against the checks that read them; the harvest order against `vendor.yml`; every quoted source count |

**The second family exists because a citation can resolve perfectly and still
describe a repo that has moved.** It was added on 2026-08-09 after one pass
found a live instance of each: Cinematic Camera four rows from where
harvest-order.md put it, `check_texture_basenames` in no document at all, a
`.gitignore` comment pointing at `plan.md` a month after the split, and `48`
where the manifest had 49. **Every inventory check compares against a generated
source of truth**, never a second hand-written list — otherwise it is one more
thing to keep in sync.

**The label check was added 2026-08-27**, the day a renumbering sweep proved a
link can resolve perfectly and still say the wrong thing: 415 labels were
rewritten twice, every href stayed correct, and `make docs` reported clean. A
number in a link's text now has to agree with the decision the link points at.

**What `make docs` deliberately does not check:** whether the prose is true. No
tool can. That is what a live run and the next session's eyes are for.
