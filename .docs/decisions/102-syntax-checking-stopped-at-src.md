# 102 — The brace checker only ever read `src/`, so nothing had asked whether the tree the game loads parses at all

**Status:** decided, 2026-08-28
**Follows** [decision 77](77-hull-section-attach-points.md), which found the same
scanner wrong about comments — and found it only because a vendored file briefly
became an `src/` override and so came into scope for the first time. That was
the warning; this is the gap it was pointing at.

## The question

Asked after the 2026-08-28 UFP run, about the first-contact alert that never
fired: *"how good is our syntax checking on our final build? my thought is that
a bug somewhere else prevented the window firing, it could just be a missing
close or something akin."*

**The honest answer was that we did not know, because nothing had ever asked.**

## What the coverage actually was

`check_script` walks `src/` — `walk((".txt", ".gui", ".gfx", ".asset"),
under="src")`, 340 files we wrote and reviewed. **Nothing walked the build.**
The mod tree is 22,395 files, but the parseable surface is **3,934**; the rest
is `.dds`, `.mesh`, `.wav`. That tenth was entirely unchecked, and it is the
half that matters more: `src/` is ours, while the build is 49 mods merged,
patched, resampled and pruned, and every one of those steps writes bytes.

**A missing brace does not fail loudly.** The Clausewitz parser swallows the
rest of the file, so everything below the defect is silently absent — no log
record, no error, just content that is not there. That is precisely the failure
mode the question imagined, and precisely the one nothing was looking for.

## The measurement

Two classes, both swept against vanilla as the control.

**Braces and unterminated strings.** The build: **3,934 files, 0 unbalanced, 0
unterminated.** Vanilla, over the identical scanner: **3** —
`common/scripted_loc/scripted_loc_ruloc.txt` and two `nomads` `.gfx`, none of
which the build ships. Vanilla failing its own parser three times is why
`check_build_script_syntax` reports rather than errors: a source is entitled to
ship what vanilla ships.

**So the specific hypothesis was wrong, and the check that should have said so
did not exist.** Both halves of that are worth recording.

**`@variables` that resolve.** `check_asset_variables` has covered art files
since [decision 29](29-asset-local-variables.md); `common/` had nobody asking. An
unresolved `@` does not keep its name — **the field it feeds gets nothing** —
which is the defect `vendor.yml`'s own `nsc_starbases` patch documents: two
`@` names left the two ship sizes that file exists to declare with no
build-block radius and no formation priority.

The build carries **one**, and it is a source's own:

```
common/technology/ariphaos_sensors_techs.txt   @ap_technological_ascendancy_rare_tech   ×6
```

Sensor Expansion reads it six times and declares it nowhere — not in that file,
not in any other Ariphaos mod in the harvest, not in vanilla, not anywhere in
`.source/`. It belongs to a companion mod we do not vendor.

## The scope rule, and getting it wrong first

**A first cut treated `@` as file-local and reported 592 vanilla files — 29% of
`common/`.** That measures the model, not the tree. Resolution is
`common/scripted_variables/` as a **global** database *plus* the file's own
`@name =` lines. `vendor.yml`'s nsc note says "`@` variables in Stellaris script
are file-scoped", and that is true of the case it describes — a name defined in
a **sibling file in the same directory**, which does not carry — but it is not
the whole rule. With both halves, vanilla drops from 592 to 25.

**And 24 of those 25 are not references at all.** `@bio_ship_armor_$SIZE$` is an
inline-script parameter concatenated at splice time, and reading a name out of it
is [check-design](../validation/check-design.md) rule 8 again: the written form
is part of the name. A `$` immediately after the match is the tell. Skipping
those leaves vanilla's floor at exactly **1** —
`@max_unlocked_council_positions` in `01_script_values_paragon.txt`, which
vanilla declares nowhere either.

**Vanilla 1, ours 1, and they are different kinds**: vanilla's is its own
oversight in its own file; ours is a source reaching for a mod we do not harvest.

## The fix, and why it is a deletion

A `vendor.yml` patch removes all six blocks:

```
modifier = {
    factor = @ap_technological_ascendancy_rare_tech
    has_ascension_perk = ap_technological_ascendancy
}
```

**Deleted rather than given a number, and vanilla is the reason.** The block
boosts six rare sensor techs while the player holds Technological Ascendancy,
and **no rare tech in vanilla carries such a modifier**:
`has_ascension_perk = ap_technological_ascendancy` appears across the whole of
vanilla's `common/technology/` exactly **once**, on a megastructure tech, at
`factor = 9`. There is nothing to read off, and inventing a number is authoring
somebody else's balance. Removing the block puts the six on vanilla's own
footing for a rare tech.

It is also the safe direction. Deletion is behaviour-identical to what the
engine does with the line today **at best**; at worst it removes a factor the
parser is reading as zero, which would make those six techs undrawable under
the very perk meant to favour them. The same argument as the `sbx_3_0` NSC-hook
removal already in `vendor.yml`.

## The two checks

| | asks | floor |
|---|---|---|
| `check_build_script_syntax` | every `.txt` / `.gui` / `.gfx` / `.asset` in `stg-build/` balances its braces and closes its strings | **0 of 3,934**; vanilla 3, none of them vendored |
| `check_script_variables` | a `common/` file reads no `@variable` that neither it nor `common/scripted_variables/` declares | **0 of 497** once patched; vanilla **1**, ours **1** before the patch |

Both share `_brace_scan` / the `@` scope rule with the checks that already
existed, so there is one answer to each question rather than two that can drift.

## What this does not settle

**It does not explain the first-contact alert, and it was never going to.** The
events fired — they played their sounds, which is what the ten
`event.cpp:896` records in that run *are*, and the player answered seven of the
ten once they went looking. An event killed by a parse failure does not fire at
all. What is open there is
[101](101-first-contact-sounds-are-species-class-gated.md)'s sibling question in
[open questions](../planning/open-questions.md), and it is a content call about
a shared alert rather than a defect to find.

**And one class remains unread.** `setup.log` — 11,922 lines nothing in this
repo has ever opened — carries **1,375** `ship_size.cpp:710 Missing ship size
Localization Key` records. It is an inventory dump rather than an error log,
which is why it has been ignored, but a four-figure class in it has never been
triaged. Named in [open questions](../planning/open-questions.md).
