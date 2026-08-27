# 44 — Three findings from the 2026-08-07 fourth run, and the two checks they bought

**Status:** decided, 2026-08-07
**Extends** [decision 18](18-minor-power-species-class-keys.md) with a fourth
case, and [decision 31](31-duplicate-entity-declarations.md) with the texture
analogue of its question.

## The run

`error.log` 187,783 bytes / 1,284 lines against the previous run's 187,392 /
1,268 — flat, and ~1/5 of the multi-MB volume that counts as a defect. Startup
real time 50,221 ms; **1,281 of 1,284 lines fall inside the 23:10:15–23:10:48
load window**. Three errors fired during play:

| time | site | outcome |
|---|---|---|
| 23:11:58 | `effect_utils.cpp:96`, `events/utopia_on_action_events.txt:867` | vanilla's file, vanilla's cyberization on-action. Not ours. |
| 23:12:00 | `planet.cpp:2058` `PLANET_SCALE_SYSTEM` | known, acked, cosmetic — [decision 41](41-planet-scale-system-length.md). |
| 23:14:45 | `trigger_impl.cpp:1213` `Invalid context switch [solar_system]` | **ours**, and repaired below. |

## 1. The context switch — SBX's one unguarded block

The message names no file. Its **scope dump** does:

```
Script Error: Invalid context switch [solar_system] from HCevasia!
… file: common/starbase_buildings/sbx_3_0_starbase_buildings.txt line: 772, Scope:
type=starbase
```

`HCevasia` is a runtime object name and appears nowhere in the tree, vanilla or
any name list — chasing it was wasted motion. **The scope dump under the message
is the evidence, not the message.** Line 772 reads

```
potential = { solar_system = { any_system_planet = { is_owned_by = from } } }
```

`solar_system` from a starbase scope is not categorically wrong — vanilla writes
it 42 times in `common/starbase_buildings`. What separates this one is the
guard, and the counts settle it rather than an assertion about scopes:

| file | `potential` blocks | of those, reaching `solar_system` | unguarded |
|---|---|---|---|
| vanilla `00_starbase_buildings.txt` | 48 | 1 (opens `is_normal_starbase = yes` + `exists = owner`) | 0 |
| SBX `sbx_3_0_starbase_buildings.txt` | 38 | 9 (eight gate on `has_starbase_size >=` first) | **1 — line 772** |

One block in either file switches unguarded, and it is the one that failed.
Patched in `vendor.yml` with vanilla's own pair. `potential` is a plain AND, so
it narrows nothing a normal starbase in a system would have passed, and
`is_normal_starbase` is SBX's own vocabulary — it uses it eight times in this
file.

## 2. `TNG` → `VUL` — decision 18's fourth case, with a cost decision 18 did not have

`check_portrait_clothes_selectors` flagged `stg_minor_tng_coalition_hope`:
species class `TNG`, portrait group `vulcan`, whose portraits use
`humanoid_master_{male,female}_clothes_01`. Those gate on 46 class keys
including `VUL` and never on `TNG`, so the empire fell through to the selectors'
`default` — human civilian clothes under a Vulcan face, decision 18's failure
exactly.

**Unlike decision 18's eight, `TNG` was not a misspelling.** It is a deliberate
class carrying its own loc family (`TNG:0 "Coalition Vulcan"`, with a desc about
the Federation Charter never being signed) and `graphical_culture =
starfleet_tng`. So this trade was real where decision 18's was free:

- **Keep `TNG`, gate the selectors on it.** 19 branches across two vendored
  files, each with different surrounding context — 19 fragile line-patches into
  art that re-breaks on the next source update.
- **Take `VUL`.** One line. Loses the class label "Coalition Vulcan"; the class
  desc goes with it.

Took `VUL`. The clothes failure is visible on every pop and leader portrait the
empire ever draws; the class label is one string in a species tooltip, and the
empire keeps its own name, adjective, ship prefix `VAS`, homeworld, and
`STG_VULCAN` name list. The country-level `graphical_culture = "starfleet_tng"`
is untouched, so its ships are unaffected — only the species-class fallback
culture changes, and for a Vulcan people `vulcan` is the better fallback anyway.

`TNG` stays declared and is now claimed by nothing. It is not a decision-32 stub
— no vendored art names it — so it survives only as the reversal path if the
flavour is ever worth 19 patches. `TNGK` is unaffected: the Klingon-Cardassian
Alliance uses portrait group `klingon`, which has dedicated
`klingon_*_clothes_combined` selectors that gate on no class at all.

> **This section's subject no longer exists.** Both the Coalition of Hope — by
> then localised *Republic of Hope (2300s)* — and the Klingon-Cardassian
> Alliance were removed on 2026-08-25, and `TNG` and `TNGK` went with them:
> [decision 82](82-remove-mirror-timeline-duplicates.md). The reversal path this
> paragraph kept `TNG` alive for is closed, which is the only part of the
> reasoning above that the removal touches. The clothes-selector finding itself
> stands and is why the check exists.

## 3. The check reported two empires that were fine

The same run flagged `KRI` (kriosian) and `VALT` (valtese) identically. **Both
were false positives, and the fix it prescribed would have been actively
wrong** — respelling a class whose people already have a complete wardrobe.

All ten kriosian portraits use `kriosian_{male,female}_clothes_01`, all ten
valtese use `valtese_*`, and those dedicated selectors gate on no class, so the
check's own "a dedicated selector is not a finding" guard should have excluded
them. It did not, because group membership was scraped as

```python
groups[name] = set(re.findall(r"\b([a-z][\w']*)\b", b))
```

— *every lowercase token in the block*. STNH's kriosian and valtese groups both
open `default = trill_female_01`, and `trill_female_01` uses the master
selector. The group's borrowed fallback portrait was being read as one of its
members. On the benzite group that scrape yields 46 "members" where 6 portraits
exist.

Now members come from `add = { portraits = { … } }` lists, falling back to
`default` only when a group has no list at all. **Recalibrated in both
directions**, per decision 28: KRI and VALT stop reporting, TNG still reports,
and the benzite group — one of decision 18's original eight — still resolves to
its 6 real portraits on the master selectors, so respelling `BEN` back to `BENZ`
would still fire.

This is decision 31's lesson in a new place: *a scrape that finds names is not a
scrape that finds the right ones.* The check had a number to show for itself and
three of its four findings were noise.

## 4. `check_duplicate_textures` — 142 ships wearing another ship's skin

The run logged 143 `Duplicate texture 'X' found` records, 137 of them
`stnc_shipset_shared/textures` against the per-ship folders it was split out of.
Nothing was checking it, and it is the texture analogue of decision 31: a
`.mesh` names its textures **by bare filename inside the binary**, so the engine
keeps one global filename → texture map, one file wins for every mesh that asks,
and the loser's ship renders wearing the winner's skin.

**The rule is vanilla's own and it is nearly absolute:** across 7,711 distinct
texture basenames under `gfx/models`, vanilla repeats exactly **one**. The built
tree repeats **142** — and, checked by hash, *all 142 differ in content*. There
is no benign-duplicate tail to filter out here; every one of them is a real
decision about which texture wins.

**This was already reviewed, and the check does not overturn it.** plan.md §4
prices these same 143 records and calls last-wins correct: the 22 Walshicus
shipsets are one author's family sharing a `stnc_shipset_shared/` vocabulary,
so where that library meets STNH's `shared_assets/` the two files are variants
of one texture under one name rather than unrelated art colliding. The
content-differs measurement is new and does *not* refute that — two variants of
one Federation hull plate differ byte-for-byte and still look alike. What it
does establish is what the review actually rests on: a taste call about whether
the variants are close enough, which no static check can settle and only eyes on
a live run can. So the library is **acked**, by directory, with that reasoning
written next to it, and the check earns its keep on what the review did not
cover.

That leaves **3 findings, not 142** — `federation/{olympic,galaxy,starbase}`
against `starfleet_tng/{cruiser,battleship,starbase}`. A different boundary:
two shipsets, not one library meeting one family, and outside what §4 reviewed.

Ack entries are **directories, not basenames**. 137 basenames would be a list
nobody rereads that goes stale the moment a shipset is re-cut; one directory
survives that, and acking one side still lets a collision between two unreviewed
folders report.

Two scoping results worth keeping:

- **Within the built tree only**, for check_duplicate_entities' reason. A build
  file reusing a vanilla basename in the *same relative directory* is an
  ordinary path shadow and deliberate — there are 142 of those, and counting
  them as findings would have doubled the noise with zero signal. In a
  *different* directory it is a genuine cross-collision; there is 1.
- **Content is compared, not names** (decision 27). It happens to eliminate
  nothing this run, which is itself the finding: byte-identical copies in two
  folders would cost disk and nothing else.

Output is grouped by directory pair — 142 files are about 20 real decisions, and
one line per file would bury every other warning in the run.

## Not repaired, and larger than all of the above

`src/localisation/english/stg_minor_powers_l_english.yml` has **79 empire names
and nearly all of them are truncated**. `STG_EMPIRE_minor_confederation_earth`
reads `"of Earth"`; the Coalition of Hope reads `"of Hope (2300s)"` and its
species plural `"of Hope (2300s)s"`. The leading token was stripped without
separator handling, which is why the damage is legible in the survivors:

| source | ours |
|---|---|
| `NAME_elaurian_auditorium` "El-Aurian Auditorium" | `-Aurian Auditorium` |
| `NAME_trogoran_empire` "T'Rogoran Empire" | `'Rogoran Empire` |
| `NAME_hurq_stagnancy` "Hur'Q Stagnancy" | `'Q Stagnancy` |
| `NAME_Confederation_of_Earth` "Confederation of Earth" | `of Earth` |

A separate 16 entries carry an unresolved loc **key** as their on-screen value
(`STG_species_adjective_minor_tng_coalition_hope:0
"PRESCRIPTED_species_adjective_VulcanHighCommand"`), and one — `"CravicImperative"` —
is a leaked camelCase source stem. All 16 resolve against `.source/`; 15 by their
own key and one via `ConfederacyEarth`, a stem the generator got wrong where it
wrote `ConfederationEarth`.

This is a silence failure — no `error.log` line will ever mention it, because
loc that resolves to the wrong string resolves.

**Repaired the next day**, along with the check that keeps it repaired:
[decision 45](45-minor-power-names-truncated.md). 100 values, and the count in
this section was two short — the sweep found 78 truncations, not 79 minus the
handful that looked intact.
