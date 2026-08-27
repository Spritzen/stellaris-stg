# 39 — Six Trek empires took a civic without the trait it grants

**Status:** decided, 2026-08-07

## The report

Three errors in the 2026-08-07 15:41 run, left unresolved by
[decision 38](38-live-run-2026-08-07-repairs.md):

```
empire_design.cpp:622: Design species was missing trait trait_aquatic
empire_design.cpp:622: Design species was missing trait trait_storm_touched
empire_design.cpp:622: Design species was missing trait trait_tankbound
```

## Three log lines, six broken empires

Some civics **grant a species trait**, written `trait = trait_x` at the top of
the civic body — `civic_anglers` grants `trait_aquatic`, `civic_storm_callers`
grants `trait_storm_touched`, `civic_tankbound` grants `trait_tankbound`. The
engine expects the design's species to already carry it.

Vanilla's own empires do: `sathyrel` carries `trait_aquatic`,
`yatunan_radicals` carries `trait_storm_touched`, `tankbound` carries
`trait_tankbound`. **STG's minor powers were templated from those three empires
— the civic pairings are copied verbatim, down to
`"civic_astrometeorology" "civic_storm_callers"` — but the required trait was
not carried across.** Six empires, in one file:

| Empire | Civic | Missing |
|---|---|---|
| `stg_minor_acamarian_sovereignty` | `civic_storm_callers` | `trait_storm_touched` |
| `stg_minor_fen_domar_states` | `civic_storm_callers` | `trait_storm_touched` |
| `stg_minor_tng_coalition_hope` | `civic_storm_callers` | `trait_storm_touched` |
| `stg_minor_brunali_empire` | `civic_tankbound` | `trait_tankbound` |
| `stg_minor_tamarian_unity` | `civic_tankbound` | `trait_tankbound` |
| `stg_minor_skrreean_republic` | `civic_anglers` | `trait_aquatic` |

Resolved as: trait added for Acamarian, Fen Domar, TNG Coalition and Brunali;
civic replaced for Tamarian (`civic_memorialist`) and Skrreea
(`civic_agrarian_idyll`).

**The log deduplicates by trait name, not by empire.** Three lines for six
defects — and it would have printed three for sixty. Reading the count as the
damage would have fixed half of one file.

## Four take the trait; two changed civic instead

`trait_storm_touched` (cost 0, no opposites) and `trait_tankbound` (cost 0,
opposites `trait_weak`/`trait_hollow_bones`/`trait_photoadaptive`, DLC *Shadows
of the Shroud* which is installed) are both free and conflict with nothing these
species carry. Added after `trait_organic`, which is where vanilla puts them.
**No trait-point budget changes**, so `check_prescripted_empires`' archetype
budgets are untouched.

Thematically, two are better than defensible and two are the author's own civic
choice made to work:

- **Brunali** — VOY's genetic engineers, who engineered their crops and their
  children. Vat-bred `trait_tankbound` fits them squarely.
- **TNG Coalition of Hope** (Vulcan) — Vulcan has sandfire storms and the
  Forge's plasma storms. Storm-touched is canon-supported.
- **Acamarians, Fen Domar** — no storm lore either way. The trait is what the
  already-chosen civic implies, not an independent flavour claim, so adding it
  changes nothing about who they are.

**Tamarians did not take the trait — their civic changed instead.** They were
initially given `trait_tankbound` along with the other four, and that was the
weakest call in the set: the Children of Tama are a myth-and-metaphor people
("Darmok and Jalad at Tanagra"), and nothing about them is vat-bred. On review
`civic_tankbound` → **`civic_memorialist`**, and `trait_tankbound` was removed
again, since nothing grants it now. A people who speak entirely by citing
remembered events are memorialists almost by definition, and it sits with the
`ethic_spiritualist` and `gov_theocratic_republic` they already had.

Checked rather than assumed: `civic_memorialist` needs the Necroids Species
Pack (installed, `dlc024_necroids`), forbids gestalt and corporate authority
(they are `auth_democratic`), and is excluded only by
`civic_relentless_industrialists`, `civic_scorched_earth` and
`civic_entropy_drinkers` — none of which they hold. Their surviving
`civic_superstitious_beliefs` excludes only its own corporate variant.
`civic_memorialist` grants no trait, so nothing replaces what was removed.

**Brunali keep `civic_tankbound` and `trait_tankbound`** — for them the vat
lore is the point.

**The Skrreea could not take theirs.** `trait_aquatic` is restricted by
Planetary Diversity's `pd_aquatic_allowed_planet_classes` to ocean and wetland
classes, and the Skrreean Republic's homeworld is `pc_desert`. Adding it would
have been invalid as well as wrong: DS9's "Sanctuary" Skrreea are three million
**agrarian** refugees seeking Kentanna, a promised farmland — farmers, not
fishers.

So the civic changed instead: `civic_anglers` → **`civic_agrarian_idyll`**.
Checked against its gates rather than assumed — it requires pacifist or fanatic
pacifist (they are `ethic_fanatic_pacifist`), forbids corporate authority (they
are `auth_dictatorial`), forbids a volcanic homeworld, and excludes
`civic_dystopian_society`, `civic_tankbound` and the relentless-industrialist
civics, none of which they hold. Their surviving civic `civic_environmentalist`
excludes none of it, and they already carry `trait_agrarian`.

## The sweep, and the false positive it produced first

Per CLAUDE.md: a defect with a rule behind it gets the rule swept, not the
instances repaired. Every civic and origin in vanilla plus the built tree was
read for `trait = trait_x` grants — **32 of them** — and every prescripted
empire checked against the ones it takes.

The first sweep read only the `species` block and reported a seventh empire:
**`stg_borg_collective`, missing `trait_cybernetic` for `civic_machine_assimilator`.
It was already correct.** Assimilator civics want the trait on the *secondary*
species, which is where vanilla's Tebrid Homolog puts it and where STG's Borg
puts it too — its own comment says so. Reading one of two species blocks is the
same error shape as [decision 31](31-duplicate-entity-declarations.md): finding
the name is not the same problem as asking the right question about it.

Corrected to pool both species blocks: **101 empires in our tree, 0 findings.**

## The check

`check_prescripted_empires` now carries it. Calibrated by reverting all six
repairs:

| Tree | Findings |
|---|---|
| repaired | 0 |
| reverted | **6** — one per empire, naming the civic and the trait |
| vanilla's own 51 empires | **0** |

Zero against vanilla is what makes it a rule rather than a preference — vanilla
never once takes a granting civic without the trait. Reported as an error, not a
warning: the engine drops the trait silently, and per CLAUDE.md an AI-only minor
power will never show up in `error.log` at all.
