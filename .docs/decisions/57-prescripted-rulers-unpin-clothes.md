# 57 — A prescripted ruler pins no clothes index at all

**Status:** decided, 2026-08-08
**Supersedes the second half of** [decision 23](23-prescripted-ruler-appearance.md),
which set `clothes = 0` on all 101 rulers believing that meant *let the selector
decide*. It does not. 0 is an index like any other.

## The report

From the 2026-08-08 live run: *"UFP start leaders are correctly clothed for
officials, commanders and scientists, except the starting president, which in
this game run is an official so should have matching clothes."*

## What the script actually resolves to

Read straight out of `humanoid_master_male_clothes_01.txt`, both scopes agree:

| Scope | Entry a Federation official matches | Art |
|---|---|---|
| `leader` (rel. line 45) | `leader_class = official`, `is_species_class = FED`, `is_military_governor = no`, `uses_starfleet_admiral = no` | `human_president_male_1..4.dds` |
| `ruler` (rel. line 33) | `is_species_class = FED`, `ruler_normal_clothes = yes` | `human_president_male_1..4.dds` |

The DS9 Starfleet block in the `leader` scope has entries for scientist,
security, command, governor, envoy and admiral and **none for `official`**, so a
Federation official has no Starfleet entry to reach at all — decision 16 chose
that deliberately and its comment says so. Officials and the ruler therefore
draw from the same four textures, and the president should already have matched.

## What was overriding it

`ruler = { clothes = 0 }`. A pinned index is resolved once, when the empire is
created, and the ruler keeps it for the rest of the game while every other
leader re-evaluates the selector on every promotion. The president was wearing
whatever index 0 resolved to in the empire designer —
[decision 22](22-empire-designer-clothes.md) put
`federation_president_male_1.dds` in that scope — while his own officials went
on evaluating the `ruler`/`leader` scopes. Two different pictures from one
selector, which is exactly the symptom.

**This is the third time the same shape has been reported**, and the shape is
worth naming: *a shared selector cannot be treated like a per-species one.*
Decision 22 found it in the designer, decision 23 in the pinned index's value,
this one in the pin itself. STNH sets `clothes = 0` on 91 of its own 112 empires
and is not wrong to: its Trek peoples use **per-species** selectors, where index
0 is that species' own clothing. On a selector 44 classes share, index 0 is
whatever happens to be first.

## Decision

**Remove `clothes` from all 101 prescripted rulers.** `texture = 0` stays — it is
the one index with a declared length to check against, and
`check_prescripted_appearance` checks it.

Omitting it is a state vanilla itself ships: 2 of vanilla's 53 prescripted
rulers (`glebsig`, `blorg`) carry `texture` and no `clothes`.

## What this does and does not settle

It removes the only thing that could make the ruler diverge from the officials
while both read one selector. If the president still differs on the next live
run, the remaining candidate is that an absent `clothes` defaults to 0 rather
than to *unpinned* — which the container cannot establish, for the same reason
decision 23 recorded: `clothes` indexes whatever the selector produces at
evaluation time and nothing on disk says what that list is.

The designer keeps decision 22's dedicated Federation President art. That the
designer and the running game show different clothing for the same character is
now a deliberate split — the designer states the office, the game states the
leader class — rather than an accident of a pinned index.

## How this class of defect gets caught next time

It does not, and saying so is better than a check that looks like it covers it.
`check_prescripted_appearance` verifies `texture` against a declared length;
there is no equivalent length for `clothes`. **What protects it is that nothing
pins it any more** — which is what decision 23 claimed while still writing an
index into all 101 files.
