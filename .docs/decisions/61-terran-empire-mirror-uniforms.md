# 61 — The Terran Empire's mirror uniforms, and four female rows with no species gate

**Status:** decided, 2026-08-08
**The in-game half of** [decision 20](20-empire-designer-clothes.md), whose
`game_setup` gate was the designer half. Found by the live Cardassian Union run.

## The report

*"Terran Empire's empress; Hoshi Sato … clothing 1 (of 472). I think the
clothing shouldn't be that many available to select from for this empire. This
likely could lead us to leader clothes fix … We need to check to see if STNH
defines which clothing sets belong to which empires."*

## What the 472 is, and why it is not the defect

The empire designer's clothes slider enumerates **every distinct texture in the
portrait's `clothes_selector`**, ignoring the trigger on each row. The Terran
Empire's species uses `portrait = "human"`, whose portraits name
`humanoid_master_{male,female}_clothes_01` — 491 and 463 distinct textures,
shared by 44 species classes. That is the shared master selector working as
built, and gating that list is not possible from the selector: the only lever is
pointing a portrait at a narrower one, and `human` is shared with the
Federation.

**But the user's inference from it was right, and it found a real defect.**

## STNH does define which clothes belong to which empire — by trigger, not class

Two vocabularies, and the mirror universe uses both:

```
leader rows: uses_mirror_starfleet_uniform = yes … enterprise_era = yes
ruler rows:  uses_terran_uniform_ruler     = yes … enterprise_era = yes
```

All three were on [decision 15](15-phase-3-clothing-triggers.md)'s INERT list at
`always = no`, so **all ten `starfleet_enterprise_mirror/` textures were
unreachable in every gameplay scope.** `TER` appears in 0 rows of the master
selectors' `ruler`, `leader`, `species`, `pop` and `pop_group` scopes, so every
Terran leader fell through to the selector's own
`all/generic_female_uniform_01.dds` — while the designer showed the mirror coat
correctly, because decision 20 had gated `game_setup` on 2026-08-08.

**Getting one scope right says nothing about the others.** That is decision 20's
lesson read in the opposite direction, and it is why the symptom was visible
only as *"the wrong number of choices"*: the one scope the user could see was
the one already fixed.

## Decision

`enterprise_era` is true **for the Terran Empire only** — not globally.

```
is_terran_empire = { exists = owner
                     owner = { owner_species = { is_species_class = TER } } }
enterprise_era            = { is_terran_empire = yes }
uses_mirror_starfleet_uniform = { is_terran_empire = yes }
uses_terran_uniform_ruler     = { is_terran_empire = yes }
ds9_clothing_era              = { is_terran_empire = no }
```

The file's *"exactly one era may be true"* rule is **a constraint on what one
leader sees, not a constant**, and the header now says so. Two eras true for two
different empires never meet in one evaluation. The Terran Empire's own
prescripted header already calls it the Empire of ENT *'In a Mirror, Darkly'*
and flies `terran_nx`, so ENT is the era its art was cut for.

Verified by evaluating every row against TER's trigger state rather than by
inspection: **the ruler scope resolves to exactly one live row per gender**
(`ent_mirror_human_{g}_ruler.dds`) and the leader scope to the four mirror
role uniforms. The six `ent_human_*` rows also want `enterprise_era` but require
`uses_starfleet_uniform`, which is FED-only, so they stay dead; the four
`32c_human_*` rows require `leader_trait_starfleet_32`, stubbed inert.

## The second finding, which the first one uncovered

**Four rows in the FEMALE master selector lost their species gate**, where the
male file gates the same four properly:

| | male file | female file |
|---|---|---|
| `kelpian_female_clothes_02` | `uses_kelpien_uniform = yes` | `uses_native_clothes = yes` |
| `talosian_female_clothes_03` | `uses_talosian_uniform = yes` | `uses_native_clothes = yes` |
| `barzan_female_clothes_03` | `uses_barzan_uniform = yes` | `uses_native_clothes = yes` |
| `vulcan_female_clothes_01` | a stratum `OR` | `uses_native_clothes = yes` |

`uses_native_clothes` is true for **every non-Federation species**. The four sit
at lines 1290–1296, after the species-gated rows at 724–803 and before the
mirror rows at 1798 — so any female operations commander of a species with no
gated row of its own wore **Vulcan** clothes, the first of the four. It would
have pre-empted the Terran mirror uniforms too.

Fixed by four `vendor.yml` patches applying **the male file's own gating**,
copied across rather than invented. All four triggers are INERT, so the rows go
dead and each species falls to its own entry; `VUL` is unaffected, having proper
`species = { is_species_class = VUL }` rows 500 lines earlier.

## Still open — five more classes fall through, and four can never be logged

The sweep that found TER found five others landing on a shared selector with no
gating in at least one gameplay scope. Only the first is playable:

| Class | Empire | Missing |
|---|---|---|
| TRI | Trill Symbiosis (playable) | male `leader` |
| CON | Confederation of Earth | every scope |
| VAU | Vau N'Akat Order | female `ruler` |
| MOR | Morali States | every scope (`sth_humanoid_02_female`) |
| TRO | T'Rogoran Empire | every scope (`sth_humanoid_01_female`) |

Four are AI-only and so **would never produce a log record at all** — the same
shape as `check_prescripted_empires`' nine hidden empires. Left open because
each needs a content choice about what that people should wear, not a mechanical
fix.

## The rule worth carrying

**"How many options does it offer?" is a question about the designer; "which one
does it pick?" is a question about five other scopes.** The user read a wrong
count in the one scope that was already correct and inferred a defect in the
scopes they could not see. The count itself was working as built.
