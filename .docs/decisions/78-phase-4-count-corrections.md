# 78 — Four numbers in Phase 4 were wrong, and the worst of them was another database's right number

**Status:** decided, 2026-08-09
**Follows:** [75](75-trek-anomalies.md), [76](76-trek-archaeology.md),
[77](77-trek-story-events.md)
**Corrects in part:** [75](75-trek-anomalies.md)'s restricted-category tally and
[77](77-trek-story-events.md)'s on_action count and story rate. Both keep their
text ([style guide §7](../style-guide.md#7-decision-files-have-a-fixed-head));
this file is where the right figures live.

## Where this came from

The [2026-08-15 audit](../analysis/2026-08-15.md) re-measured every quantity
decisions 55–77 state against what is on disk. **Every cross-reference resolved
— roughly 350 of them, 0 dangling — and every figure in the ship-name and music
group verified exactly.** The four below are what did not, plus one the audit
itself got wrong.

Nothing here is a content defect. Three are hand-written header comments in
`src/` that a future session would have read as authority, and the fourth is a
rate presented as general that is true of one empire in twenty-two.

## The four

| Where | Said | Is | Why it was wrong |
|---|---|---|---|
| `src/common/anomalies/stg_anomaly_categories.txt:4` | vanilla's **137** anomaly categories | **327** | no derivation reaches 137; decision 75's own body says 327 |
| `src/common/archaeological_site_types/stg_arc_sites.txt:3` | vanilla's **327** site types | **123** | **327 is the anomaly number, in the archaeology file** |
| `src/common/on_actions/stg_on_actions.txt:5`, and `check_story_events`' docstring | vanilla's **452** on_actions | **485** | 396 + 33 + 56; 452 is the sum with `01_planet_destruction.txt` silently dropped |
| `src/common/on_actions/stg_on_actions.txt:49` | an STG empire sees a story event **21%** of pulses | **21.1% / 17.8% / 14.3%** | only the Federation holds two gated events |

**The arc-sites header is the one that mattered.** A wrong number that is
another database's *right* number reads as confident, survives a skim, and is
the exact failure mode [decision 71](71-doc-inventory-checks.md) added
`make docs`' inventory family for — except that family compares documented
inventories against generated sources of truth, and a prose count of *vanilla's*
contents in a `src/` header is neither. It is checked by somebody re-deriving it,
which is what the audit was.

Every command that re-derives these is in the audit's last section.

## And the third tier of the story rate, which is a content gap

The 12 species-gated story events cover **11 distinct species classes**. Only
FED holds two, so `random_events` presents three different pools:

| Empire | gated events in pool | weight against `1200 = 0` | rate per pulse |
|---|---|---|---|
| Federation (FED) | 2 | 320 | **21.1%** |
| the other 10 gated classes | 1 | 260 | **17.8%** |
| 11 playable empires, and all 79 AI minors | 0 | 200 | **14.3%** |

The eleven playable empires with no institution of their own are **BOL, BRE,
THO, CAI, XIN, SUL, YRI, KRE, MAL, VID and TER**. The last is the notable one: a
headline playable empire from Phase 2 with its own ENT-era uniforms
([64](64-terran-empire-mirror-uniforms.md)), and nothing in the story pool for
it.

**Left as a content gap on purpose, not closed here.** Growing the pool is cheap
— `random_events` fires exactly one winner, so eleven more gated events cannot
make anyone see more popups, only different ones — but writing eleven events is
Phase 4 content work rather than an audit repair, and it needs the same eyes the
first twenty-one still need. It is now named in
[open-questions.md](../planning/open-questions.md) beside "does the right empire
get the right story?", because **a Malon player seeing only the eight open events
is not a broken gate and would not read as one.**

A second-order note recorded with it: `stg_recent_story` runs 3,600 days (9.86
years) and every story event sets it, so one fired event blanks the next
five-year pulse. The long-run frequency is about `p / (1 + p)` — **~17% for the
Federation, ~13% for an ungated empire** — rather than the headline rate. That is
a fine outcome, just not the one the comment described.

## Nine restricted anomaly categories, not seven

[Decision 75](75-trek-anomalies.md) says "seven of the 21 are `max_once` or
`max_once_global`". The file has **nine**: five `max_once_global`
(`planet_killer_remnant`, `iconian_gateway`, `tox_uthat`, `deep_space_probe`,
`omega_signature`) and four `max_once` (`resonator_cache`, `living_ship`,
`cetacean_probe`, `transwarp_conduit`).

**The rule is right and the file follows it** — every restricted category names a
specific thing, every unrestricted one names a kind. Only the tally was off.
That makes STG **43% restricted against vanilla's base-game 8 of 40**, which is a
defensible consequence of a Trek set naming more specific objects, and is worth
stating rather than under-reporting. The figure now sits in the file's own
header.

## What was changed, and what deliberately was not

**Changed:** the three `src/` headers, `check_story_events`' docstring, and the
weights comment in `stg_on_actions.txt`, which now carries the three-tier table
instead of the single rate.

**Not changed:** the bodies of decisions 75 and 77. A decision records what was
true when it was made; retrofitting one is editing a record
([style guide §7](../style-guide.md#7-decision-files-have-a-fixed-head)). Their
status lines gained a pointer here, in the shape
[decision 17](17-stnh-shipsets-on-a-vanilla-chassis.md) uses.

## Two things the audit itself got wrong or overstated, corrected here

**The anomaly difficulty means.** The audit puts vanilla's base-game mean level
at 2.2; re-derived it is **2.4** (96 over 40 categories), against STG's **3.86**.
The shape of the observation survives intact and is the interesting part: vanilla
puts 65% of its base-game categories at level 1–2 and 10% at level 5+, STG puts
19% and **43%**. The table is now in
[open-questions.md](../planning/open-questions.md), where "do the levels and
rewards feel right" already sat as an eyes-only question with no number beside
it.

**`clear_deposits` is not absolute in vanilla**, though decision 75 states it as
if it were ("vanilla puts it before every research deposit it adds"). Measured
over `events/anomaly_events_[0-9].txt`: **40 of 69** research-deposit adds carry
the guard, and the split is the real pattern — **29 of the 42 that also add a
permanent planet modifier, against 11 of the 27 that do not.** STG guards 5 of 8
and the 5 are exactly the ones that add a modifier, **so the implementation
follows vanilla's real practice and only the stated rule was absolute.** Recorded
in the events file's own header.

## The one finding this file does not carry

Finding 5 — that decision 76's headline `weight` claim had no check behind it —
is [decision 79](79-reachability-checks.md), because it is a check rather than a
correction.
