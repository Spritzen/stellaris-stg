# 108 — The Trek anomalies were written a notch stingier than vanilla in every body class, and the level skew that looked like the problem costs the player two points

**Status:** decided, 2026-08-29
**Corrects** [decision 73](73-phase-4-count-corrections.md)'s level yardstick and
the copy of it in [open-questions.md](../planning/open-questions.md), both of
which compare 21 Trek categories against **vanilla's base-game 40** and read
*"vanilla puts 10% at level 5+"*. The pool a player actually surveys is **327**
categories and it puts **24.2%** there. 73 keeps its text; the figure it was
measured against was never wrong, only never the right yardstick.
**Follows** [decision 70](70-trek-anomalies.md), which wrote the 21 categories,
and [decision 74](74-reachability-checks.md), which established that a category
with no positive `spawn_chance` is complete, validates clean and is never
rolled.

## The question

[Decision 70](70-trek-anomalies.md) shipped 21 Trek anomaly categories — 27
outcome events, 24 pictures, ~3,500 words — and nothing since has asked **how
often a player meets one**. `check_anomalies` asks whether each is *reachable*
([74](74-reachability-checks.md)); reachable and *met* are different questions,
and only the first had ever been put.

## The measurement, and the trap in it

**The first number was wrong and it was wrong in our favour's opposite
direction.** Summed raw, the 21 categories hold **68 of 2,477** points of
anomaly spawn weight — 2.7% — against a category count of 6%. That reads as a
mod whose own content is invisible.

**It is an artifact of four vanilla categories.** Vanilla writes four modifiers
at `add >= 100`, and `DISTAR_DEAD_GOD_CAT` alone is **`add = 1000`** — a
scene-specific guaranteed spawn behind a long conjunction of triggers, not a
weight competing for an ordinary survey. Excluding those four:

| | weight | spawnable categories | median `add` |
|---|---|---|---|
| vanilla | 1,209 | 274 | 3.0 |
| STG | **68** | 21 | **2.0** |

**5.3% of the weight for 7.2% of the categories.** A real shortfall, about
1.6×, not the 3× the raw figure claimed.

**And the shape of it is the finding.** A survey rolls only among categories
that can match the body in front of it, so the honest comparison is per body
class:

| body class | vanilla weight / categories | STG weight / categories | STG share | fair share |
|---|---|---|---|---|
| asteroid | 148 / 41 | 11 / 5 | 6.9% | 10.9% |
| star | 40 / 9 | 8 / 3 | 16.6% | 25.0% |
| gas giant | 131 / 35 | 5 / 3 | 3.7% | 7.9% |
| habitable | 315 / 41 | 10 / 2 | 3.1% | 4.7% |
| uninhabitable planet | 554 / 137 | 31 / 11 | 5.3% | 7.4% |
| moon | 3 / 1 | 3 / 1 | 50.0% | 50.0% |

**Under fair share in every class, by roughly the same factor.** That is not a
weighting mistake in one place; it is a hand that wrote `add = 2` where vanilla
writes `add = 3`, consistently, across a whole file. The medians say it in one
line: vanilla 3.0, STG 2.0.

## What was changed

**`1 -> 2`, `2 -> 3`, `3 -> 5`. All 33 `add` values in
`src/common/anomalies/stg_anomaly_categories.txt`, and nothing else in the
file.** Every target is a vanilla idiom rather than a computed number — vanilla
writes `add = 3` 143 times, `add = 2` fifteen times and `add = 5` eleven. Five
candidate mappings were scored against fair share before this one was picked:

| mapping | resulting share | fair share |
|---|---|---|
| `1→2, 2→3`, 3 unchanged | 7.1% | 8.4% |
| **`1→2, 2→3, 3→5`** | **8.3%** | **8.4%** |
| `1→3, 2→3, 3→5` | 8.7% | 8.4% |
| `1→2, 2→4, 3→5` | 9.6% | 8.4% |
| `1→3, 2→4, 3→5` | 10.0% | 8.4% |

Per class after the change: asteroid 10.3% against 10.9% fair, uninhabitable
8.3/7.4, gas giant 6.4/7.9, habitable 4.5/4.7, star 24.5/25.0. Moon lands
62.5/50.0 and is one vanilla category against one of ours — noise, not a
finding.

**No category gained or lost a trigger, a level, an outcome or a restriction.**
The nine `max_once` / `max_once_global` categories
([73](73-phase-4-count-corrections.md)) are untouched, so the specific things —
the Iconian gateway, the Tox Uthat, the Omega signature — are still once each.

## The levels were left alone, and this is the part that needed measuring

The standing worry, written into
[open-questions.md](../planning/open-questions.md), is that the Trek set leans
too hard: *"the Trek half is the slow, failure-prone half … early-game
scientists will bounce off it."*

**The lean is real.** By category, STG is 19.0% at level 1–2 and **42.9% at
level 5+**, mean 3.86.

**The yardstick it was measured against was not.** Decision 73 compared it to
vanilla's **base-game 40** — 65% at level 1–2, 10% at 5+, mean 2.40. But the mod
does not ship beside the base game; it ships beside every DLC, and the pool a
survey draws from is **327 categories**: 37.4% at level 1–2, **24.2% at 5+**,
mean 3.28. Half the gap was the comparison.

**And the half that is left costs two points.** Weighting each category by the
spawn weight it actually carries — which is what a player meets, rather than
what a file lists:

| pool | level 1–2 | level 3–4 | level 5+ |
|---|---|---|---|
| vanilla alone | 31.3% | 43.5% | 25.2% |
| the Trek 21 alone | 23.9% | 35.8% | 40.4% |
| **the merged pool, after the rescale** | **30.3%** | **42.4%** | **27.4%** |

**25.2% to 27.4%.** The Trek set is 8% of the pool, so its skew moves the galaxy
the player surveys by 2.2 percentage points — and the rescale, which makes Trek
anomalies *more* common, moves it by 2.2 rather than 1.4. That is the whole
price.

**So the levels stay.** A level is content: the Iconian gateway and the Omega
signature are supposed to be beyond an early scientist, and that is the point of
them. Flattening the curve would cost the set its character to buy back two
points of a difficulty the player does not experience as Trek's, because 92% of
what they survey is vanilla's.

**The general form, and it is the third time this project has hit it:** the
finding was not wrong, the *floor* it was measured against was. The same shape
as [decision 95](95-colony-pools-drop-home-system-bodies.md) and
[decision 79](79-shipset-descs-and-home-system-names.md) — *the blocker was
never the decision, it was a floor nobody had measured yet.* Here measuring it
killed half the finding and rescued the other half.

## No check, and the reason is decision 104's

**A `check_anomaly_weight_share` would report a percentage forever.** There is
no defect it could catch: a weight is a judgement, any positive value is valid,
and `check_anomalies` already asks the only binary question in the database —
whether a category can be rolled at all
([74](74-reachability-checks.md)). Shipping one would buy a number and no
failure, which is what
[decision 104](104-script-documentation-is-a-version-exact-oracle.md) declined
to do with `check_modifier_names` and what
[validate.py](../../tools/validate.py)'s own rule forbids.

**The measurement is the deliverable, and it is reusable**: the per-class table,
the `add >= 100` exclusion that makes it honest, and the weight-weighted level
profile are all above, and the same method applies unchanged to the archaeology
weights if anybody ever asks the same question of
[decision 71](71-trek-archaeology.md)'s six dig sites.

## What this does not settle

**Whether a Trek anomaly now turns up often enough to notice**, which is a live
run's question and a cheap one: survey a few dozen bodies and count how many of
the anomalies are `stg_`. The prediction is falsifiable — **roughly one in
twelve**, up from one in nineteen.

**Nothing about the writing, the pictures or the outcomes.** Those are
[open-questions.md](../planning/open-questions.md)'s three eyes-only questions
about the Trek anomalies and this decision does not touch them.
