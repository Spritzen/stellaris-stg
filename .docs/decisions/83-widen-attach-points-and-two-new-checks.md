# 83 — A stale ratio was guarding the hull family, the female selector was never swept, and no generator was ever a checked fixpoint

**Status:** decided, 2026-08-22
**Follows** [decision 82](82-hull-section-attach-points.md), whose repair this
finally puts a check behind.
**Follows** [decision 35](35-station-section-attach-points.md), whose scope
constant this widens — and whose reason for the scope had expired.
**Follows** [decision 71](71-doc-inventory-checks.md): all three items below came
out of reading the docs against the tree, not out of a live run.

## Where these came from

A sweep of `.docs/` for check-shaped suggestions — places where a document says
*nothing guards this*, *the check was never written*, or *this argues for one
check over the pattern*. The sweep turned up ten candidates. Three were taken;
this records those three and what measuring them changed.

**Two of the ten closed themselves on measurement and needed no work at all**,
which is recorded here so nobody re-opens them:

- **[Analysis 2026-08-16](../analysis/2026-08-16.md) finding 5** — the six
  `pd_tree_of_life_01` city layers at 4×4 — is not a defect and was already
  answered in code. `_vanilla_family_sizes()` in `tools/validate.py` records
  that **vanilla itself ships `ai_01_city_l01..l05` at 4×4 to mean "this layer
  is empty"** and that Planetary Diversity uses the same idiom. `.source/`
  ships them at 4×4. Struck.
- **[Analysis 2026-08-16](../analysis/2026-08-16.md) finding 6** — the nine
  `Failed to find entity … for attachment` records, described there as "never
  triaged" — **were** triaged, in
  [decision 37](37-attach-edges-into-pruned-art.md), and the four referencing
  files carry a twelve-line rationale in `vendor.yml` under
  `attach_target_ack`. What is true and worth keeping is the *shape*: **the ack
  silences `check_attach_targets`, not the engine.** Those nine records are a
  standing init cost that no amount of clean `make validate` will remove.

---

## 1. The ratio that closed the hull scope had expired

`check_section_attach_points` was scoped to the station family by
[decision 35](35-station-section-attach-points.md), and its docstring recorded
why: over all 317 sizes with `section_slots`, **41 vanilla findings against 147
mod findings**, "not a signal anyone can act on". Both
[checks.md](../validation/checks.md) and
[ufp-run-remediation](../planning/ufp-run-remediation.md) item 1 then said the
hull family had nothing guarding it.

**Re-measured against the build of 2026-08-11, that whole population is 12** — 7
vanilla-only and 5 in vendored files. Decision 82's 230 attach points collapsed
the mod side, and the scope's own justification went with it. The ratio had been
true when written and nobody had reason to look again.

### But widening on that number alone would have shipped false positives

This is the part worth keeping, because the number looked like permission.

- **`ancient_destroyer_entity [part2]` is vanilla's own body.** It declares
  `root` and `part1` and nothing else, in both `/stellaris` and our tree, carried
  through unchanged by a shadow. The existing `vanilla_only` guard could not see
  it: that set holds entities **vanilla alone declares**, not entities we shadow
  without editing. A widened check would have reported Paradox's content as our
  defect.
- **The other four fly their own culture's art**, and **28 of vanilla's 33
  `*_constructor_entity` declare no `part1` in the `.asset` either.** The point
  comes from the animated rig, which the container cannot read — the identical
  caveat decision 82 records for vanilla's titan and colossus frames, which name
  no part locators and work.

So the widened half is gated on the frame being **borrowed** — `pdxmesh` not
prefixed by the entity's own culture — which is exactly how
`hull_entities()` in `tools/fix_ship_locators.py` scopes the repair. **The check
now guards the population that tool writes, and nothing else.** `part1` is
dropped from the wanted set for the same reason decision 82 dropped it: every
borrowed frame in this tree is a corvette's, and a corvette always has one.

This is [rule 12](../validation/check-design.md#12-can-this-ever-appear-has-more-than-one-route--ask-them-all-then-read-the-scope-off-the-answer)
arriving from the other direction. Rule 12 says a high floor is usually a missing
half of the question. Here a floor that had *fallen* was equally misleading:
five findings that all looked actionable, and not one of them was.

**Mutation-tested**, as [rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)
requires: stripping every `part2` / `part3` / `frame_ship` locator from the built
tree takes the check from 0 to **267 findings**, including hulls
(`betazoid_battleship_entity [part2 part3]`) that the old scope could not see.

## 2. `check_selector_texture_paths` — the syntax half, landed alone

[ufp-run-remediation](../planning/ufp-run-remediation.md) item 2 specified this
check on 2026-08-10 and it was never written. The Vulcan run of 2026-08-22 then
logged three of its findings, and
[analysis 2026-08-16](../analysis/2026-08-16.md) finding 1 established that the
29 patches of 2026-08-10 had all landed in the **male** master selector while the
female file — carrying the exact female mirror of the seven president rows — was
never touched.

**The question splits in two and only one half is mechanical.** *Does the path
end in `.dds`* is pure syntax: appending it cannot be the wrong answer. *Does the
path resolve* has 196 findings whose fix is either deleting a row — changing
which garment a species wears — or supplying art. The first half shipped; the
second waits for the content call.

**Vanilla is the calibration and it is exact:** 7,845 quoted portrait paths
across 1,044 distinct files in its own `asset_selectors`, and **every one ends
`.dds`.** No other extension appears in that position at all, so the floor is 0
and no scope is needed.

**Ten rows found, all ten fixed**, by `patches:` in `vendor.yml` — nine `.dds`
appends in the female master, one in the male, plus one row naming a real texture
under `brunali/` that exists only under `norcadian/`. Zero extension-less rows
remain tree-wide.

> **One consequence, taken deliberately.** The `brunali` row now names the same
> texture as line 534 of the same file, so that selector lists one garment twice.
> The alternative — deleting the row — shifts every index after it and changes
> what other species wear, which is the content call this half was scoped to
> avoid. A duplicate entry draws the right clothes; a fallback does not.

**Why the log could never have found the rest of them.** A texture that fails to
load falls back silently, and the engine records the miss only for a row it
actually draws. Two live runs produced three records out of ten. That is
[live-runs.md](../guides/live-runs.md#a-screen-nobody-opened-is-a-check-that-never-ran)'s
rule in its purest form: the log is a sample of the rows somebody scrolled past.

## 3. `make gen-check` — a generator is supposed to be a fixpoint

**Six of the eleven generators read `stg-build/`** — the tree built from their own
output — **and none of them is invoked by any `make` target.** That is the exact
loop that broke `gen_star_names.py`, which subtracted its own 580 names and wrote
a pool a third the size on its second run
([ufp-run-remediation](../planning/ufp-run-remediation.md) item 3). Nothing had
ever established that the other five were safe.

`tools/gen_check.py` runs each generator over the tree it already produced and
diffs `src/` against itself. **A correct generator is a fixpoint, so the floor is
0 by construction** — the rare case where a check needs no vanilla ratio beside
it, because the property is definitional rather than empirical.

**Two levels, because the two failures have different shapes.** The default pass
catches *drift*: committed output that is no longer what today's inputs produce,
which is what had quietly dropped 22 star names as the tree grew around a tool
nobody re-ran. `DEEP=1` inserts a `make vendor` between two runs and is the only
level that can catch a generator feeding on its own output — at a full build per
generator, so it is opt-in.

**All eleven are fixpoints today.** That is a baseline, not a result.

**Mutation-tested**: corrupting one loc value in
`src/localisation/english/stg_random_names_l_english.yml` makes the harness
report drift against `gen_star_names` and **only** that generator, naming the
file.

`src/` is hand-written content and this tool runs generators over it, so `src/`
and `.vendor-cache/` are snapshotted before anything runs and restored in a
`finally` — including on exception and on Ctrl-C.

## What this cost the docs

`make docs` caught both omissions by itself — the missing catalogue row and the
undocumented `make` target — which is [decision 71](71-doc-inventory-checks.md)'s
inventory family doing the job it was written for, on the first change since it
shipped.
