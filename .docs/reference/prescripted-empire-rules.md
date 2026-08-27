# Prescripted empire validity — the five databases that can veto

> **What** — the rules a prescripted empire must satisfy, derived from vanilla's
> own databases, and the one that is routinely missed.
> **Open when** — authoring or editing anything in `src/prescripted_countries/`,
> or triaging an empire that will not appear in the designer.
> **Then** — [decision 39](../decisions/39-civic-granted-species-traits.md) · [validation checks](../validation/checks.md) · `check_prescripted_empires` in `tools/validate.py`

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

## The government wants an authority, and usually a civic or an ethic too

The `possible` block of every government STG uses, flattened. Read it as *what
the empire must already be* before the government is legal:

```
gov_representative_democracy  is_democratic_authority
gov_moral_democracy           is_democratic_authority + is_pacifist
gov_direct_democracy          is_democratic_authority + is_materialist
gov_theocratic_republic       is_democratic_authority + is_spiritualist
gov_science_directorate       is_oligarchic_authority + civic_technocracy
gov_citizen_stratocracy       is_oligarchic_authority + civic_citizen_service
gov_irenic_bureaucracy        is_oligarchic_authority + is_pacifist
gov_military_junta            is_oligarchic_authority + is_militarist
gov_military_dictatorship     is_dictatorial_authority + is_militarist
gov_martial_empire            is_imperial_authority + civic_warrior_culture
gov_star_empire               is_imperial_authority + is_militarist
gov_divine_empire             is_imperial_authority + civic_imperial_cult
gov_trade_league              is_megacorp + civic_free_traders | civic_trading_posts
gov_machine_assimilator       is_machine_empire + civic_machine_assimilator
```

Re-derive rather than trusting this block — it is a convenience copy and the
authority is `/stellaris/common/governments/`:

```bash
grep -A15 '^gov_star_empire' /stellaris/common/governments/*.txt
```

## Traits: two points, and the archetype gates the list

The budget is vanilla's default of **2 points** and every list must sum to
exactly 2. Beyond the arithmetic, **the species archetype decides which traits
exist at all** — `trait_adaptive`, `trait_slow_breeders` and `trait_fleeting`
are BIOLOGICAL-only, so the Tholians take lithoid-legal traits and the Borg
robot ones.

## `graphical_culture` is set on the EMPIRE too, and the empire's copy wins

This is the one that produces no error and no log line. `graphical_culture`
appears both in `common/species_classes/` and in the prescripted empire, and
**the empire's value overrides the class's**. Remapping one without the other
does not dangle and does not warn — the empire silently drops to
`fallback = mammalian_01` and flies vanilla mammalian hulls.

Two fields beside it resolve by bare name with nothing declaring them, so a typo
is equally silent: `city_graphical_culture` is a texture **prefix**
(`= "klingon"` finds `gfx/portraits/city_sets/klingon_city_l01.dds`) and `room`
is a `*_room.dds`. `check_room_references` and `check_graphical_culture_art` ask
both questions — [decision 46](../decisions/46-room-selector-merge.md),
[47](../decisions/47-flags-city-sets.md),
[59](../decisions/59-city-set-cultures-undeclared.md),
[79](../decisions/79-shipset-descs-and-home-system-names.md).

## A vanilla tuple is not automatically legal here: three availability rules

Copying an authority/government/civic/ethic tuple whole from a vanilla empire is
the standing advice above, and it is **sound but insufficient** — the tuple also
has to survive the DLC set and the species classes STG actually ships. Three
rules, all added 2026-08-26 after five STG empires were hidden from the designer
and **two of the five printed no reason at all**
([decision 83](../decisions/83-design-database-is-not-the-cause.md)):

1. **A civic whose `playable` is satisfied only when a DLC is ABSENT.** Vanilla
   ships these as stand-ins for a DLC's own civic —
   `playable = { NOT = { host_has_dlc = "…" } }`. `civic_corporate_dominion` is
   the whole set today, and vanilla ships it on `iferyx`, which is hidden on a
   full install too. **STG targets a full install**, so naming one hides the
   empire. Four minor powers lifted it from `iferyx` and all four were hidden;
   `gov_trade_league` names the civic in its own `possible`, so the government
   had to move with it.
2. **A civic whose `possible` gates `species_class` to a POSITIVE list.** All 99
   STG empires carry STG's own classes and those lists name vanilla's, so no STG
   empire can ever satisfy one. `civic_tankbound` wants
   `{ AQUATIC INF NECROID TOX }`.
3. **A trait vanilla declares `species_possible_add = { always = no }`.** A
   civic's `modification` block grants it; a species block can never carry it
   directly. `trait_tankbound` is the worked example — and it is two defects on
   one empire, not one, because the civic and the trait each break a rule.

All three are read out of vanilla's own databases by
`check_prescripted_empires`, not hardcoded, so they follow vanilla forward.

## Every empire needs a `flag = empire_<its own key>`, and it is not heraldry

`empire_flag = { icon … }` is the coat of arms. **`flag = empire_<key>` is
something else entirely**: it names an entry in `common/prescripted_flags/`,
and that entry's `flags` are set on the country as **country flags** the moment
it is created — before a single system is generated.

That is the join a static galaxy scenario runs on. The map pins an empire to its
home system with `spawn_weight = { base = 0 modifier = { add = 100000
has_country_flag = <key> } }`, and that home system's initializer creates the AI
copy only when nothing already carries the flag. **Without this line the
player's own copy carries no flag, so picking that empire puts a second one on
its homeworld.** Vanilla's `humans2` is the model: `flag = empire_human_2`,
declared as `empire_human_2 = { flags = { human_2 custom_start_screen } }`.

In STG **the country flag is the design key** — `stg_klingon_empire` is the
block key, the country flag, the string the map tests and the string the
initializer sets. So a new empire needs two things and
`check_static_galaxy` fails without either:

1. `flag = empire_<key>` in the empire's own block, and
2. a re-run of `python3 tools/gen_empire_flags.py`, which writes
   `src/common/prescripted_flags/stg_empire_flags.txt` off the roster.

[Decision 86](../decisions/86-static-galaxy-scenario.md).

## A civic can grant a species trait the species block must also carry

The engine reports this **once per trait name**, so six broken empires read as
three log lines. [Decision 39](../decisions/39-civic-granted-species-traits.md).

## Why this is a swept rule and not a list of fixes

Vanilla's `opposites` lists, archetype budgets and ruler-trait ethic gates hid
**nine** STG empires from the designer for eleven runs. Sweeping the rule behind
them found **nine more** on empires that were then gated out of the designer and
would never have produced a record at all. (Those nine reach the designer now:
the `playable = stg_never` gate is gone from all 79.)

`check_prescripted_empires` enforces all of it against vanilla's own databases,
calibrated by reverting the repairs: 21 findings, no false positives. The three
availability rules above are calibrated the same way — reverting their five
repairs yields **six** findings over those five empires and nothing else
([83](../decisions/83-design-database-is-not-the-cause.md)).

**Never repair only the instances a log names.**
