# 16 — Phase 3: real bodies for the STNH clothing triggers

**Date:** 2026-08-03
**Status:** applied
**Supersedes the "Phase 3 replaces this file" marker in**
`src/common/scripted_triggers/stg_stnh_art_triggers.txt` and the scripted-trigger
row of plan.md §3's four-dependency table.

## The problem

All 140 harvested STNH triggers were `always = no` ([decision 08](08-stnh-art-shadows-vanilla.md)).
That silenced the error records, and it also made **1,167 of 1,241 gated lines in
`humanoid_master_male_clothes_01.txt` (94%), and 1,208 of 1,280 in the female
file, unreachable** — every one of them requires some stub to be `yes`.

Every Starfleet entry needs *two* stubs true at once:

```
"…/starfleet_ds9/ds9_human_male_security.dds" = {
    has_worker_stratum_clothes = yes
    uses_starfleet_uniform_pop = yes    ← always = no
    ds9_clothing_era = yes              ← always = no
}
```

So no Trek uniform was reachable by anything, and each scope fell to its
`default =`:

| Scope | Fell through to | Read as |
|---|---|---|
| species / pop | `human_civilian/civ_human_male_clothes_01.dds` | plausible — STNH civilian art |
| leader | `all/generic_male_uniform_01.dds` | **vanilla generic** |
| ruler | `all/generic_male_uniform_01.dds` | **vanilla generic** |

That split is why it read as "off" rather than broken: civilians looked Trek and
every leader looked like stock Stellaris. The negated gates are what made it look
deliberate — `uses_borg_full_prosthetics = no` *passes* when the stub is `no`, so
the civilian entries genuinely did fire.

## Why STNH's own bodies could not be copied

Two independent reasons, either of which alone would have reproduced the bug.

**1. STNH's eras are `years_passed` windows.** It is a timeline conversion that
starts in the ENT era and advances:

```
ds9_clothing_era   = { years_passed > 214  years_passed < 221 }
tng_clothing_era2  = { years_passed > 209  years_passed < 217 }
```

STG starts **at** TNG/DS9 with all major powers established (plan.md §1), so
`years_passed = 0` at game start and every one of those windows is false —
exactly where `always = no` left us. **STG's era is a constant, not a clock.**

**2. STNH's identity triggers gate on country flags nothing in STG sets.**

```
is_starfleet_uniform_country = {
    owner = { OR = { has_country_flag = united_federation_of_planets … } }
}
```

`grep -c 'set_country_flag = united_federation_of_planets'` over `stg-build/` and
`src/` is **0**. This is the same hole the Breen and Romulan advisor voices had
(the 2026-08-08 analysis §6.2), and it
takes the same fix: gate on species class, which the empire genuinely has.

**3. (Bonus) STNH's role bodies name 4.4 vocabulary that no longer exists** —
`leader_class = legend`, `trait_fleet_admiral`, `trait_rear_admiral`,
`leader_trait_defender`, `leader_trait_attacker`, `subclass_admiral_engineer`.
Copying them would have traded silent fallback for dangling-reference records.

## What was decided

**Era: `ds9_clothing_era = { always = yes }`, every other era left `always = no`.**
Exactly one era may be true — two make two entries match and the first in file
order silently wins. plan.md §1 settles the era as "TNG / DS9"; DS9 is the later
and terminal look of that pair. Moving the whole mod to TNG S3+ is a one-token
change: clear this and set `tng_clothing_era2` instead.

**Identity: founder species class, not a country flag.**

```
is_starfleet_uniform_country = {
    exists = owner
    owner = { owner_species = { is_species_class = FED } }
}
```

`owner_species` in country scope is the form proven by the advisor-voice weights
in the 2026-08-09 run — zero `trigger_impl` records. `exists = owner` guards the
species scope, where `owner` does not resolve; there it correctly yields
"native clothes", which is what a bare portrait should be.

**Roles: mapped onto 4.4's four leader classes and twelve subclass traits.**
Verified against `/stellaris/common/leader_classes/00_base_classes.txt` and
`/stellaris/common/traits/`.

| 4.4 leader | Trigger made true | Lands on |
|---|---|---|
| commander, plain/councilor | `is_hero_or_admiral` | `ds9_*_command` (red) |
| commander + `subclass_commander_admiral` | `uses_starfleet_admiral` | `tng2_*_admiral` |
| commander + `subclass_commander_general` | `is_sec_ops` | `ds9_*_security` (gold) |
| commander + `subclass_commander_governor` | `is_military_governor` | `ds9_*_command` |
| scientist | `uses_science_uniform` | `ds9_*_science` (blue) |
| envoy | — (selector tests the class directly) | `tng2_*_envoy` |
| official | **none** | `human_president_male_*` |

**Officials deliberately match nothing.** This is the one non-obvious call. The
entry at `humanoid_master_male_clothes_01.txt:653` catches
`leader_class = official` with `is_military_governor = no` and dresses it in
`human_civilian/human_president_male_*.dds` — the Federation's civilian
administration, and the canon look. A first draft of this pass defined
`is_military_governor` as "commander-governor **or** official" so that officials
would reach a command uniform; that silently destroyed the president art for
every Federation official. `is_military_governor` now means literally a military
governor.

**Pop strata: 4.4 pop categories**, as vanilla's own selectors use them
(`/stellaris/gfx/portraits/asset_selectors/toxoid_clothes_15.txt:19`) —
`ruler` → command, `specialist` → science, `worker` → security.

**`uses_native_clothes` composed, not constant.** It is `uses_starfleet_uniform = no`
plus the two Borg checks, so every *non*-Federation species gets its own Trek
costume back at the same time — Vulcans, Klingons, Romulans and the rest — while
a Vulcan serving in the Federation still reads as Starfleet, which is canon.

## Verified, and how

`make validate`: **ok — 6 warnings**, the same six pre-existing
`common/random_names/` ones. No new finding.

**All 140 keys still defined**, checked by set-diffing declared keys before and
after: 140 in, 140 out, no drops, no duplicates. A dropped key is a dangling
reference and one error record per call site. *The first attempt at this check
used `^[a-zA-Z_]+ = \{`, which silently misses every key containing a digit
(`ds9_clothing_era`, `tng_clothing_era1`, `uses_starfleet_admiral_2`) and reported
10 false drops — the regex must be `^[A-Za-z][A-Za-z0-9_]* = \{`.*

**Reachability simulated per leader archetype** rather than eyeballed, walking
the leader scope in file order and evaluating each entry against the new bodies.
Six of seven archetypes land on the intended DS9/TNG2 art; `official` was a
simulator artifact (it skipped lines containing `NOT`) and line 653 was then
confirmed by hand. Both the simulator's own bugs are recorded here because each
one *inverted* the result: unhandled `has_leader_flag` made everything match a
Bajoran Kai entry, and an incomplete true-set made nothing match at all.

Art presence confirmed for every file the reachable entries name, male and
female.

## What this does not fix

**4.4 has no medical, CMO or spy leader concept**, so `is_medical_leader`,
`is_cmo_leader` and `is_spy_leader` cannot be mapped. The DS9 medical, CMO and
Section 31 uniforms stay unreachable and their art sits unused in the tree. That
is a content gap, not a defect — closing it means inventing STG leader traits to
hang them on, which is a separate piece of work.

**The other 199 selector files are untouched by intent.** They gate on species
classes that are Phase 2 work and still undefined (the 42 tokens in
`vendor.yml`'s `dangling_identifier_ack`), so their entries remain unreachable
for the reason they always were.
