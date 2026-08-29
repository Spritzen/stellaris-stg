# 110 — Our own script names no effect or trigger the engine does not have, and the merge-wide version of that question cannot be asked from the dump alone

**Status:** decided, 2026-08-29
**Follows** [decision 104](104-script-documentation-is-a-version-exact-oracle.md),
which opened `logs/script_documentation/` as a version-exact, merge-aware oracle,
measured its **modifier** list and declined to ship a check on it. This is the
same oracle's other two files, asked the same way, with the same kind of answer
and a different reason.

## The question 104 left

104 read `modifiers.log` — 47,510 names — and found no defect to catch. It said
the measurement was reusable and named the obvious extension in passing:
`effects.log` (**1,056** effects) and `triggers.log` (**1,087** triggers) are
the engine's own list of every effect and trigger *this build* understands, and
a misspelt one is the same class of silent failure a misspelt modifier is.

That matters more for `src/` than the modifier question did. Our hand-written
content is **21 anomaly categories, 6 dig sites, 27 stage events, the story
events and the home-system initializers** — roughly 7,300 words of script
grounded in vanilla examples ([70](70-trek-anomalies.md),
[71](71-trek-archaeology.md), [72](72-trek-story-events.md)) — and an effect the
engine does not know is a line that does nothing.

## What was measured

A context-aware scanner: parse each file into blocks, descend from the known
effect entry points (`immediate`, `after`, `on_success`, `complete_effect`,
`abort_effect`, …) and trigger entry points (`trigger`, `limit`, `potential`,
`allow`, `possible`, `weight`, …), and ask of every key inside them whether it
is one of

* the 1,056 effects or 1,087 triggers the engine dumped;
* a scope link from `scopes.log`, or an event scope (`root`, `from`, `prev`,
  `event_target:…`);
* a scripted effect or trigger declared anywhere in the merge — **1,917 and
  2,143**, vanilla plus DLC plus the build;
* flow (`if`, `else`, `switch`, `random_list`, `hidden_effect`, …).

**`src/`: 154 script files, and 14 distinct unmatched tokens, every one of them
an artifact of the scanner rather than a name in the tree.**

| unmatched | what it actually is |
|---|---|
| `NOT`, `NOR` | flow keywords in their uppercase spelling |
| `days`, `flag`, `id`, `resource`, `on_action` | **sub-fields of an effect**, e.g. `set_timed_country_flag = { flag = x days = y }` |
| `authority`, `ethics`, `weight` | database fields inside a block the descent should not have entered |
| `<`, `>` | comparison operators |
| `contact_country?`, `RANDOM_EVENTS` | a scope-with-question-mark and an inline-script parameter |

**Zero real findings.** Nothing in `src/` names an effect, trigger or scope this
build does not have.

## Why the merge-wide version is a different question, and is not asked

The same scanner over **vanilla's own** `common/` and `events/` — 2,110 files —
reports **48,622 unmatched tokens in 1,612 distinct names**. Sorted by
frequency the top of that list is `id` (4,961), `weight` (4,612), `days`
(3,242), `which` (2,568), `type` (2,340), `name` (2,109).

**Those are not names the engine does not know. They are the sub-fields of
effects it does know**, and the dump documents them — but only inside each
entry's free-text *syntax example*:

```
add_blocker - Adds a blocker to a colony carrier, …
add_blocker = {
	type = <key>
	…
}
```

So the oracle has the information and does not expose it as data. Reading it as
a flat allowlist of top-level names, as this scanner does, **models the language
wrongly**, and a floor of 48,622 against vanilla is that model reporting itself
rather than the tree — the identical failure 104 diagnosed when
`check_modifier_names` scored 125 unknown names against vanilla and 117 of them
turned out to be real modifiers.

**A merge-wide check would first have to parse 1,056 syntax examples into a
per-effect field table.** That is a day's work whose payoff is unknown, and
nothing on disk currently suggests a defect for it to find.

## No check shipped, for [validate.py](../../tools/validate.py)'s own reason

For `src/` the population is real and the answer is **0 of 154 files**. A check
there would report `0` forever, which is what
[104](104-script-documentation-is-a-version-exact-oracle.md) declined to ship
and what the rule in `validate.py` forbids: *a check that cannot fail is worse
than an absent one, because it reports a number.*

For the merged build the check is not blocked by having nothing to find — it is
blocked by not having an oracle in the right shape yet. **The two halves fail
for opposite reasons and it is worth keeping them apart**: if a live run ever
produces an effect the engine drops, the `src/` half is an hour and the numbers
are here; the build-wide half still needs the field table first.

**What is reusable, written down so the next session does not re-derive it:**
the extraction is `^(\w+) - ` against `effects.log`, `triggers.log` and
`scopes.log`; the scripted-effect and scripted-trigger declaration sets must
include **`/stellaris/dlc/*`** or the floor is nonsense; and the entry-point
lists above are what turn a flat token sweep into a context-aware one.

## What this does not settle

**It says nothing about whether an effect that resolves does the right thing.**
Every name in `src/` is real; whether `stg_anomaly.1` awards what its text
promises is [open-questions.md](../planning/open-questions.md)'s eyes-only
question about the Trek anomalies, unchanged.
