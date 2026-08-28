# 99 — A starbase module names a section template too, and two of SBX's name one that exists nowhere

**Status:** decided, 2026-08-28 — repaired in `vendor.yml`, art half is eyes-only.
**Widens** [decision 96](96-section-slots-survive-a-replacement.md)'s
`check_section_slot_references` into the reference direction it did not walk.
**Found by** the Klingon run of 2026-08-28, in two records that are in every
`error.log` on disk and that no document had ever named.

## The finding

[Decision 96](96-section-slots-survive-a-replacement.md) asked whether a ship
design's section and slot references survive a replacement, and answered it
across the merge: **0 and 0 over 6,882 component references**. That question was
asked in one direction — `common/global_ship_designs` → `common/section_templates`
— because that is the direction [decision 37](37-sbx-citadel-slot-renumbering.md)'s
defect ran in.

**It is not the only direction.** A `starbase_module` names its section too, and
in a different shape: a bare

```
section = "HABITAT_ORBITAL_RING_SECTION"
```

rather than the `section = { template = … }` block a ship design writes. Nothing
had ever asked whether those resolve. **Two do not**, and the engine had been
saying so at load in every log on disk:

```
[19:48:57] ship_design_templates.cpp:480
           Failed to get section template for key: SHIELD_ORBITAL_RING_SECTION
           Failed to get section template for key: ARMOR_ORBITAL_RING_SECTION
```

Both belong to Starbase Extended 3.0's own `orbital_ring_shield_module` and
`orbital_ring_armor_module` — modules SBX invented, since vanilla has no shield
or armor orbital-ring module at all.

> **A check is scoped by the reference direction someone thought of.** 96's
> floor of 0 and 0 was true and was never the whole question: the same
> database, referenced from a directory nobody walked, was 2.

## It is SBX's defect, not a harvest loss

The distinction is the first thing to establish and it is cheap: **grepping all
of `.source/` for either key finds only the modules file**. Neither section is
declared in SBX's own `!!!_sbx_3_0_orbital_ring_sections.txt`, in vanilla's
`orbital_ring.txt`, or in any other source we vendor. There is nothing to
un-prune and nothing to restore — the sections were never written.

So [invariant 4 / decision 11](11-fix-source-errors-dont-drop.md) applies:
**fix it, keep the mod.**

## What shipped

- **Two `vendor.yml` patches**, one line each, repointing both modules at
  `SOLAR_PANEL_ORBITAL_RING_SECTION`.
- **`check_section_slot_references` gains the module direction.** Population is
  `common/` minus `global_ship_designs` and `section_templates`, resolved
  against the same merged section map the ship-design half uses.

**Why that section and not a new one.** It is the only orbital-ring section SBX
declares that **no module claims** — measured 0 references across vanilla and
the merged tree — and it carries **no `component_slot`**, which is what a
weaponless stat module needs; both of these add shields or armor and mount
nothing. Reusing one section across several modules is vanilla's own idiom, four
times over: `SHIPYARD_ORBITAL_RING_SECTION` serves two modules,
`HANGAR_ORBITAL_RING_SECTION` two, `SCIENCE_STARBASE_SECTION` three.

**Repointed rather than authored, deliberately.** Declaring the two missing
sections in `src/common/section_templates/` would reach the same art with more
files, and would end the property decision 96 relies on — that **SBX owns the
only section file the build ships**. One word twice is the smaller change and
the reversible one.

## What is a guess, and it is only the art

Both modules now render as a solar-panel ring segment. **Nothing in either tree
says what SBX meant them to look like**, so this is an eyes-only outcome in the
sense [live runs](../guides/live-runs.md#eyes-only-findings) means it — a
reference that resolves produces no log record, and `make validate` clean is not
evidence for it. It is listed in
[open questions](../planning/open-questions.md) with what to look at: build a
shield or armor module on an orbital ring and see whether the segment reads as
defensive plating or as an obvious solar panel.

## The floors

| | |
|---|---|
| Vanilla alone | **0 dangling of 96** module section references |
| Merged tree, patched | **0 of 123** |
| Merged tree, patch reverted | **2** — `SHIELD_` and `ARMOR_ORBITAL_RING_SECTION`, the same two keys the live log named, and nothing else |

The third row is the control
([rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)):
it recovers the finding from disk alone, which is what says the check can fail.
