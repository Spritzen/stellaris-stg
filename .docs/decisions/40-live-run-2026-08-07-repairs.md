# 40 — The 2026-08-07 15:41 run's small defects, and what each one cost

**Status:** decided, 2026-08-07

The run loaded STG (`enabled_mods:["mod/star_trek_galaxies.mod"]`), threw 1,309
errors in 193 KB, and crashed nothing. [Decision 38](38-real-space-drops-sol-neighbours.md)
and [decision 39](39-sbx-citadel-slot-renumbering.md) cover the two structural
findings. This file covers the rest: nine small defects, each traced to a named
line, each fixed by a `vendor.yml` patch or an additive `src/` file.

Nothing here changes a balance value. Every removal deletes a clause that could
never fire.

| # | Symptom in `error.log` | Cause | Fix |
|---|---|---|---|
| 1 | `Invalid government species_class reference [CRYO]` | PD - Unique Worlds gates two origins on a species class **nothing declares** — not PD, not any of the 48 sources, not vanilla. It belongs to a PD companion mod we do not harvest. | Patch: delete both `NOT = { value = CRYO }` lines. |
| 2 | `Failed to deferred read key reference legend` ×2 | STNH's Klingon clothes selector tests `leader_class = legend`. 4.4 declares four leader classes and `legend` is not one. | Patch: drop the term. |
| 3 | `Failed to deferred read key reference assembly_line_manufacturing` ×4, `mining_manager` ×1 | SBX carries New Ship Classes compat hooks; NSC is not in the harvest. | Patch: delete the five gated `produces`/`upkeep` blocks. |
| 4 | `Missing localization key [nsc.requires.asteroid]` | Same NSC gap, in a `custom_tooltip` fail_text. The build tooltip's requirement line was blank. | Loc key added. |
| 5 | `Error in scripted trigger, cannot find: category` ×2 | `financial_space_center` has a `resources` field copy-pasted into its `potential` block, where the engine tries to resolve `category` as a trigger. | Patch: delete that one line. |
| 6 | `Missing name localisation for deposit rs_d_dark_matter_deposit_1..3` | Real Space declares three dark-matter deposits and localises none. | Loc keys added, yields read from the deposit file, wording and icon vanilla's. |
| 7 | `Missing modifier localization: fire_rate_reduction, hp_increased` | Two Ships in Scaling static modifiers with no loc — raw keys in any tooltip listing them. | Loc keys added, named from what the file sets. |
| 8 | `invalid shield_impact "none"` | ASB's alt strike-craft weapon. Valid sizes are small/medium/big, so the shield-hit effect played not at all. | Patch: `none` → `small`, vanilla's value for every strike craft. |
| 9 | `Could not find animation file fallen_empire_0{2,3,4}_citadel_idle.anim` | SBX built its FE 02/03/04 starbase assets by copying 01 and renumbering every name **including the animation's `file =`**. Vanilla ships only `fallen_empire_01_citadel_idle.anim`. | Patch: repoint all three at the file that exists. The animation *name* is untouched — entities reference it. |

## The one worth its own section: a case-sensitivity bug the platform switch created

```
texturehandler.cpp: Couldn't find texture file: gfx/particles/Cloud_3.dds
```

Vanilla ships `gfx/particles/cloud_3.dds`, lower case. ASB references
`Cloud_3.dds`, capital C, from 14 sites across its particle-lance, tachyon-lance
and perdition-beam muzzle effects. **On Windows that resolves; on the native
Linux build it does not** — so this defect was created by
[decision 15](15-native-linux-runtime.md), not by ASB, and would be invisible
on the platform ASB was written for.

Swept rather than spot-fixed, per CLAUDE.md's rule about deriving the rule
behind a finding: every `.dds` reference in the built art was resolved
case-insensitively against both trees and compared for exact case.
**Exactly one mismatch in the whole tree**, this one. So it is a real class, and
it has exactly one member today.

The fix is `src/gfx/particles/Cloud_3.dds`, a byte copy of vanilla's
`cloud_3.dds` (22,000 bytes). One file fixes all 14 references and survives ASB
updates, where patching 14 reference sites would not. **This is a `.dds` copied
from vanilla and that fact is derivable from nothing on disk** — hence this
paragraph, per CLAUDE.md's "if it is written down nowhere else, it is not a
comment — it is a missing doc".

## Resolved after this file was written

The trait errors below were traced and fixed the same day —
[decision 41](41-civic-granted-species-traits.md). The section is kept because
its reasoning was wrong in an instructive way: it looked for the *requirement*
in PD's origin overrides, where `trait_aquatic` appears only as an exclusion,
and concluded the container could not settle it. The actual mechanism was a
civic **granting** a trait the species did not carry, in STG's own
`stg_z_minor_powers.txt` — six empires, reported as three log lines because the
engine deduplicates by trait name.

## Left unfixed, deliberately

**`empire_design.cpp: Design species was missing trait trait_aquatic /
trait_storm_touched / trait_tankbound`** (3 errors). Traced as far as the
container allows and stopped there. All three traits *are* declared in the built
tree; no prescripted country in the tree names any of them; the user's
`user_empire_designs_v3.4.txt` contains no traits at all. The only references
are requirement clauses in PD's `zz_pd_overwrite_origins.txt` and
`zz_pd_overwrite_civics.txt`, which suggests an empire design pairing one of
those origins with a species lacking the trait. Which empire that is, the log
does not say and the container cannot: `empire_design.cpp` fires at design
validation, and per CLAUDE.md's rule that *a screen nobody opened is a check
that never ran*, attributing it needs a run that opens the empire designer.

Not acked, because it is unexplained rather than understood. Left for the next
run to name.

## Not defects

- **`Variable name ... is already taken`** ×10 against
  `common/scripted_variables/00_scripted_variables.txt`. Every file in
  `common/solar_system_initializers/` redeclares `@distance`,
  `@base_moon_distance` and `@jumps` — that is the directory's normal practice,
  vanilla included. Inherent to the merge, costs nothing, and the reason
  `stg_restore_sol_neighbors.txt` substitutes literals instead of adding three
  more (decision 38).
- **`Invalid supported_version in file: mod/ugc_*.mod`** ×5. Other subscribed
  mods' descriptors sitting in the mod folder. Not loaded, not ours.
