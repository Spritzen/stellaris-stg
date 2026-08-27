# 74 — A site with no `weight` and a category with no `spawn_chance` are complete, clean and unreachable, and nothing asked

**Status:** decided, 2026-08-09
**Follows:** [70](70-trek-anomalies.md), [71](71-trek-archaeology.md),
[72](72-trek-story-events.md), [73](73-phase-4-count-corrections.md)

## The gap

[Decision 71](71-trek-archaeology.md) devotes its central section to a sentence
it calls the whole question:

> **`weight` is the whole question, and six of vanilla's ten decline it.**

A `weight = 0` site is complete, correct, validating clean and never placed. It
is [decision 59](59-city-set-cultures-undeclared.md)'s undeclared graphical
culture one database over, and it is the same defect
[`check_story_events`](72-trek-story-events.md) was written for in the
on_actions database.

**`check_archaeology` did not ask it.** The
[2026-08-15 audit](../analysis/2026-08-15.md) read the check and found the
substring `weight` nowhere in it: it asked about pictures, loc, `stages = N`,
stage events, rune icons and `RANDOM_EVENTS`, and stopped. The same asymmetry
existed in `check_anomalies`, which never looked at `spawn_chance` — a field
that **defaults to `base = 0`**, so a category with none can never be rolled.

That is [style guide §10](../style-guide.md#10-the-docs-get-the-same-treatment-the-mod-gets)
violated by the project against itself: *a rule with no check behind it is a rule
that erodes silently.* All six sites and all 21 categories passed the question by
hand when the audit put it to them. **The exposure was the seventh site somebody
adds** — `weight = 0 #set via initialiser` is what six of vanilla's ten base-game
sites look like, so it is precisely what a site copied from a vanilla template
inherits, and it would ship silently.

## Why the obvious check would have been a bad one

The audit proposed roughly ten lines: report any site with no positive `weight`,
scoped to STG's own file because vanilla's floor there is a known 6 of 10.

Measured, that floor is much worse than 6 of 10. **74 of vanilla's 123 site types
carry no positive weight**, and 49 of its 327 anomaly categories have no positive
`spawn_chance`. A check with a 74-finding floor is a check that gets scoped down
to our own file to stay quiet, and a scope adopted to keep a check quiet is the
thing [check-design rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter)
exists to refuse.

**The reason vanilla writes so many is that `weight` is not the only route in.**
It governs `create_archaeological_site = random` and nothing else; vanilla places
most of its sites by naming them from an initialiser or an event. So the question
"can this ever appear" has two halves, and asking only the first is asking the
wrong question rather than asking half of it.

## The second half, and what it costs

`_script_tokens_outside(directory)` sweeps every `.txt` in the built tree and in
vanilla, excluding the database's own directory, and collects every identifier
written anywhere. A key that appears in it is named by something, however the
engine reaches it.

**It is a token sweep, not a reference parse, and deliberately so.** Vanilla's
zroni chain is created by `create_archaeological_site = $DIGSITE$` inside an
inline script, with `DIGSITE = zroni_digsite_2` passed from an event four files
away — no parser that follows one effect name finds that, and a mod can invent a
route vanilla has not used. The sweep over-accepts by construction, which is the
right direction for a check whose finding is *"delete this or wire it up"*
([check-design rule 1](../validation/check-design.md#1-a-check-that-deletes-is-not-a-check-that-reports)).
Localisation is excluded with the definition directory: every key has a loc entry
by construction, so including `.yml` would make the question vacuous.

It costs one filesystem sweep of 3,939 files, about a second, cached and shared
between the two checks.

## The calibration, which is what decides the scope

| | no positive field | …and named nowhere else in script |
|---|---|---|
| `weight`, vanilla's 123 site types | **74** | **0** |
| `weight`, the built tree's 7 | 1 (Planetary Diversity's `pdcrystal_site`) | **0** |
| `spawn_chance`, vanilla's 327 categories | **49** | **3** |
| `spawn_chance`, the built tree's 21 | 0 | **0** |

Weight alone is a 74-finding check; the pair is a 0-finding one. **So neither
question needs a scope, and both are asked of the whole built tree** — scope is a
calibration result, and here the calibration says none is needed.

The anomaly floor is a known **3**, not 0: `ANCREL_MECHANO_CAT`, `VULTAUMAR` and
`YUHTAAN` appear only in their own file and in localisation, exactly as
`UBUME_BABY_CAT`'s dangling `anomaly.6791` is a known floor of 1 for the check
beside it. A floor is calibrated and written down, never assumed.

## What is not reported

`_no_positive` returns true **only when the zero is established**. A scripted
value, an `@variable` or a block shape it does not recognise is not reported — a
reachability check that guesses is worse than one that misses, because its
finding tells the reader to delete content. A `factor` does not count as positive
either: it multiplies, and vanilla writes `base = 0` with a `factor` under it,
which is still zero.

## That it fires

Both questions were run against a deliberately broken tree before being trusted
— [check-design rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed),
*distrust a check that has never failed.* `stg_site_hall_of_the_blade`'s weight
block replaced with `weight = 0`, and `stg_dilithium_matrix_category`'s
`spawn_chance` reduced to a `base = 0` with a `factor` under it. Both reported,
each naming the field, the consequence and vanilla's floor; the tree was restored
and both checks returned to 0.

## Where they live

`check_anomalies` and `check_archaeology` in `tools/validate.py`, as the seventh
and twelfth questions of their respective checks. `make validate` stands at
**0 errors, 0 warnings** with both in place, over 21 categories and 7 sites.
