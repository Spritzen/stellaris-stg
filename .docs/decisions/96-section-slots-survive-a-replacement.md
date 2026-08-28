# 96 — A section replacement must keep every slot vanilla's own designs mount on, and the 23 duplicate-section records say nothing about whether it did

**Status:** decided, 2026-08-28 — measured from disk, no live run required.
**Generalises** [decision 37](37-sbx-citadel-slot-renumbering.md) from the one
instance a live log named into the swept rule behind it, which is
[session rule 9](../guides/working-rules.md) and
[check rule 6](../validation/check-design.md#6-a-screen-nobody-opened-is-a-check-that-never-ran).
**Triages** the 23 `ship_design_templates.cpp:216` records in the `error.log`
baseline, which no document had ever named.
**Corrects** the vanilla floor quoted for `common/name_lists` by
[decision 91](91-src-contests-its-own-name-lists.md): **80 keys in 76 files**,
not 78.

## The finding

Every run logs 23 of these, and they have sat in the baseline untriaged since
the first live run:

```
[20:35:09][ship_design_templates.cpp:216]: duplicate section template found.
    Multiple sections are named [CITADEL_STARBASE_SECTION].
    file: common/section_templates/starbase.txt line: 247
```

They name **vanilla's** files. Starbase Extended 3.0 ships its sections as
`!!!_sbx_3_0_starbase_sections.txt` and `!!!_sbx_3_0_orbital_ring_sections.txt`;
`common/section_templates` is a FIOS directory and `!` sorts first, so SBX takes
all 23 keys outright and each vanilla declaration it displaces is logged. **The
record is the receipt for a replacement, not a defect** — and it is silent on
the only question that matters about one.

That question is what the slots did. A `ship_design` mounts components by slot
**name**:

```
section = {
    template = "CITADEL_STARBASE_SECTION"
    component = { slot = "MEDIUM_GUN_010"  template = "MEDIUM_BIO_PLASMA_3" }
```

so a replacement that renames or drops a slot leaves that mount empty, and the
engine says so only if somebody builds the ship. [Decision
37](37-sbx-citadel-slot-renumbering.md) is exactly that: SBX tidied the citadel's
thirteen medium mounts to `MEDIUM_GUN_10..12`, stopped at twelve, and vanilla's
Biogenesis bio-citadel lost four guns. Four `ship_growth_stage.cpp` records in
one run, patched the same day — **one instance, from one screen somebody
opened.**

## The sweep, and it is clean

The rule is *every slot a ship design names must exist in the section template
that wins the key*, asked of the **merge** rather than of `src/`: vanilla owns
all 412 designs, SBX owns the only section file the build ships, and the defect
is what the two make together.

| | designs | component references | slots missing | sections missing |
|---|---|---|---|---|
| vanilla alone — the floor | 412 | 6,882 | **0** | **0** |
| the merged tree | 412 | 6,882 | **0** | **0** |
| control: SBX's **unpatched** source | 412 | 6,882 | **4** | 0 |

The control is decision 37 reverted, and it reports `MEDIUM_GUN_010`,
`011`, `012`, `013` on `CITADEL_STARBASE_SECTION` — **the same four slots the
live log named, recovered from disk alone.** A second control, an injected
replacement that claims `elderly_tiyanki_key` and offers no slots at all,
reports 16. So the zero is a measurement and not an artefact
([check rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)).

**And the stronger form of the same measurement:** across all 23 sections SBX
takes from vanilla, the set of slots it offers is a **superset** of the set it
replaced — zero vanilla-only slots in 22 of them, and in the citadel only
because decision 37's patch put the four back. SBX adds throughout — `SMALL_GUN_01..08` and `LARGE_GUN_01..12` on the
orbital rings, utility banks out to `LARGE_UTILITY_50` — and, once patched,
takes nothing away. **The 23 records are benign, by measurement rather than by
assumption**, and the one thing standing between the merge and four dead mounts
is a fifteen-line patch that nothing was guarding from the other direction.

## What shipped

`check_section_slot_references` in `tools/validate.py` asks both halves — a
design naming a section nothing declares, and a design naming a slot the
section has not got — because vanilla's floor is 0 on both. It resolves both
databases FIOS, the way the engine does, so *"who wins"* here is who wins
in-game.

**It reads two written forms of a slot, and reading only the first would have
made it a check that cannot fail.** Named mounts are
`component_slot = { name = "MEDIUM_GUN_01" }`; utility banks are a **count** —
`large_utility_slots = 6` — which the engine expands to `LARGE_UTILITY_1..6`.
A design names both kinds identically. The injected control reports 16 findings
of which **14 are utility slots** — a check reading only `component_slot`
would have found two of them.

## The second defect, found on the way

`_top_level_blocks` anchored its key at **column 0**. That is identity in most
of vanilla and it is identity nowhere: leading whitespace at depth 0 is
cosmetic to the engine, so refusing to read it deletes the declaration rather
than the defect —
[check rule 8](../validation/check-design.md#8-a-reference-has-a-written-form-as-well-as-a-name),
the cosmetic-form half, third instance.

Vanilla indents six `ship_section_template` declarations, five in
`distant_stars.txt` and one in `reanimated.txt`. On its first cut this check
lost all six, and so reported **six vanilla designs naming a section template
nothing declares** — a confident wrong answer, in the direction that looks like
a finding rather than like a bug.

Sweeping the same question over every database gave one more, and it is a floor
rather than a finding: **`common/name_lists/LITH1.txt` and `LITH2.txt` indent
`LITHOID1` and `LITHOID2`**. `check_src_key_contention` had its own column-0
regex, so the floor decision 91 published — *"0 across 78 keys in 76 files"* —
counted 78 of vanilla's 80. The verdict is untouched, in both directions: the
database gate still admits exactly the same fourteen databases, and `src/` still
contests nothing. **A floor that is wrong by two is still a number somebody will
cite.**

Both are fixed: `_top_level_blocks` tracks depth instead of columns, and
`check_src_key_contention` uses it. Every count on the `make validate` summary
line is byte-identical afterwards, which is what says this is a parser repair
and not a change of question.

**Measured and left alone:** `check_key_conflicts`' `list_re`, the shrunk-pool
half, carries the same anchor. Its exposure is **48 depth-0 flat lists in
vanilla and 18 in the build, and not one of them is a pool**: vanilla's are
`inline_scripts/` fragments and `HOW_TO_MAKE_NEW_SHIPS.txt`, where a depth-0 key
is a chunk of script and not a name at all; the build's 18 are six `common/defines`
files' `NGraphics`/`NCamera`/`NGameplay` groups and two more PD inline scripts.

**And widening it would be wrong rather than merely unnecessary.** A defines
group *is* a flat depth-0 `key = { … }`, so an indent-tolerant `list_re` would
start reading `NGameplay` as a name pool and comparing its length against
vanilla's — a question `check_defines_conflicts` already owns, asked in the
wrong vocabulary. The column-0 anchor is doing no work there, but nothing behind
it wants the two databases confused.

## What this does not answer

**Whether the mounts render where they should.** Every one of SBX's 25 citadel
slots shares `locatorname = "medium_gun_01"` — SBX's own choice, recorded in
decision 37 — so the guns exist and resolve, and where they sit on the model is
the ungraded shipset question in
[open-questions](../planning/open-questions.md), not this one.

**The other two duplicate families in the baseline.** 110 `An item with name`
and 103 `a 3d-type with the name` records are the ASB projectile
reimplementations and the STNH/Walshicus texture library, both already triaged;
this decision covers only the 23 that name `common/section_templates/`.
