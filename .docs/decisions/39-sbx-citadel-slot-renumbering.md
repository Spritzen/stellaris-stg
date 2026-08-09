# 39 — SBX renumbers vanilla's citadel gun slots and vanilla's own design breaks

**Status:** decided, 2026-08-07

## The report

Four `ship_growth_stage.cpp` errors in the 2026-08-07 15:41 run:

```
invalid component slot "MEDIUM_GUN_010".  common/global_ship_designs/biogenesis_ship_designs.txt:4020
invalid component slot "MEDIUM_GUN_011".  ...:4024
invalid component slot "MEDIUM_GUN_012".  ...:4028
invalid component slot "MEDIUM_GUN_013".  ...:4032
```

`biogenesis_ship_designs.txt` is **vanilla's**, unshadowed. So vanilla's own
Biogenesis bio-citadel design was asking for four mounts that did not exist.

## Why

Vanilla names the citadel's thirteen medium slots `MEDIUM_GUN_01`…`09` and then
— inconsistently — `MEDIUM_GUN_010`, `011`, `012`, `013`. The three-digit form
appears in exactly two files in the entire game: `section_templates/starbase.txt`
declaring them, and `biogenesis_ship_designs.txt` calling them.

Starbase Extended 3.0 replaces that section. Its file is `!!!_sbx_3_0_starbase_sections.txt`
— the `!!!_` prefix is Irony's FIOS-winning convention and it works, so SBX's
`CITADEL_STARBASE_SECTION` is the one the engine keeps and vanilla's is logged as
a duplicate. SBX tidied the numbering to the conventional `10`, `11`, `12` **and
stopped at twelve**. Vanilla's design asks for thirteen, by the old names, and
gets none of the last four.

Two mods each correct alone; the merge is what breaks. Same shape as
[decision 38](38-real-space-drops-sol-neighbours.md), found in the same run.

## The fix, and the option not taken

A `vendor.yml` patch renames SBX's `10/11/12` back to `010/011/012` and adds the
`013` SBX never had. The section then carries vanilla's exact thirteen slot
names and the design resolves in full.

**Why not fix the design instead.** The alternative was an `src/` copy of
vanilla's `biogenesis_ship_designs.txt` renumbered to SBX's scheme. That means
owning 4,085 lines of vanilla to change four, and re-merging it every game patch,
to fix one design. The patch is fifteen lines and *fails loudly* if SBX ever
renumbers again — which is the whole argument for patches over overrides.

**Why adding a slot is safe here, and would not be elsewhere.** Adding a
component slot normally strands a weapon with no locator, which fires from the
middle of the ship ([decision 28](28-weapon-locator-positions.md)). It cannot
here: **every one of this section's 25 slots already shares
`locatorname = "medium_gun_01"`** — large, medium and small alike. That is SBX's
own choice, not something this patch introduces, so slot 013 sits exactly where
SBX's other twelve already sit and no locator is missing.

**Scope.** SBX's `STRONGHOLD_STARBASE_SECTION_XL` and
`HEADQUARTERS_STARBASE_SECTION_XL` also carry `MEDIUM_GUN_10`…`12` — and already
run to 16 and 20. They are SBX's own sections, no vanilla design references
them, and they are deliberately left alone. The patch anchors on the one place
`MEDIUM_GUN_12` is followed by `SMALL_GUN_01`, which is unique to the citadel;
verified `count: 1`.

## The balance delta, stated plainly

SBX citadels go from 12 medium mounts to 13. That is a real change to SBX's
rebalance, made knowingly: it is vanilla's own number, it restores a vanilla
design the merge had broken, and the alternative left one gun permanently
unmountable and an error in every run.
