# Prescripted empire validity — the five databases that can veto

> **What** — the rules a prescripted empire must satisfy, derived from vanilla's
> own databases, and the one that is routinely missed.
> **Open when** — authoring or editing anything in `src/prescripted_countries/`,
> or triaging an empire that will not appear in the designer.
> **Then** — [decision 41](../decisions/41-civic-granted-species-traits.md) · [validation checks](../validation/checks.md) · `check_prescripted_empires` in `tools/validate.py`

An empire names five databases and **every one can veto**: the authority, the
government, each civic, the origin, and the species class. The traits veto each
other too.

The game does not report an invalid combination — it **refuses to start**. Copy
every authority/government/civic/ethic tuple whole from a vanilla prescripted
empire rather than assembling one.

## The authority constrains the ethics, and this is the half that gets missed

Checking the government's `possible` block is the obvious half and is not enough.
`common/governments/authorities/00_authorities.txt` carries its own, and it
constrains ethics:

```
auth_democratic   forbids ethic_(fanatic_)authoritarian
auth_oligarchic   forbids ethic_fanatic_egalitarian AND ethic_fanatic_authoritarian
auth_dictatorial  forbids ethic_(fanatic_)egalitarian
auth_imperial     forbids ethic_(fanatic_)egalitarian
auth_machine_...  REQUIRES ethic_gestalt_consciousness + a MACHINE species
```

The Cardassian Union shipped as `auth_oligarchic` with
`ethic_fanatic_authoritarian` — which line two forbids — under a header asserting
every combination had been checked against "the `possible` block of the thing it
names". It had been; just not the authority's.

## A civic can grant a species trait the species block must also carry

The engine reports this **once per trait name**, so six broken empires read as
three log lines. [Decision 41](../decisions/41-civic-granted-species-traits.md).

## Why this is a swept rule and not a list of fixes

Vanilla's `opposites` lists, archetype budgets and ruler-trait ethic gates hid
**nine** STG empires from the designer for eleven runs. Sweeping the rule behind
them found **nine more** on empires that were then gated out of the designer and
would never have produced a record at all. (Those nine reach the designer now —
[decision 88](../decisions/88-playable-gates-the-design-database.md).)

`check_prescripted_empires` enforces all of it against vanilla's own databases,
calibrated by reverting the repairs: 21 findings, no false positives.

**Never repair only the instances a log names.**
