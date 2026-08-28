# 80 — The 196 was 117, two thirds of it was never a content call, and the thirteen that were took one policy rather than thirteen decisions

**Status:** decided, 2026-08-24
**Follows** [decision 78](78-widen-attach-points-and-two-new-checks.md), which
landed the syntax half of this question and left this half for a content call.
**Corrects** the count carried by the 2026-08-10 Federation remediation plan's
item 2, [open-questions](../planning/open-questions.md),
[status](../planning/status.md) and [checks.md](../validation/checks.md) since
2026-08-10.

## Where this came from

A question about the standing item: *what do we need to do to address the 196
dangling selector textures — a content decision per row?* Answering it meant
re-running the loop that produced the 196, and the loop did not produce it.

## 1. The number was wrong, and the way it was wrong is the finding

Measured against the build of 2026-08-24, four resolution rules:

| rule | rows | textures | files |
|---|---|---|---|
| missing from `stg-build/` only | 1,169 | 147 | 83 |
| **missing from `stg-build/` and `/stellaris`** | **117** | **45** | **43** |
| …directory itself absent | 267 | 70 | 37 |
| …masters excluded | 82 | 29 | 41 |

None of them is 196, and nothing since 2026-08-22 changed the portrait harvest —
decision 78's eleven patches only *add* to this population, by moving ten rows
from malformed to dangling. So the 196 is a rule difference, not drift, and
**the document that carries it named the rule**: that plan's item 2 said
to *walk every quoted `gfx/models/portraits/…` in that directory and test it
against `stg-build/`*. That is the first line of the table, with vanilla left
out of the resolution set.

**STG is a total conversion but it does not replace vanilla's art.**
`gfx/models/portraits/` under `/stellaris` is still loaded, and **1,052 of the
1,169 rows name a file that is in it** — they draw correctly. Resolving against
the built tree alone reports nine false findings for every true one, which is
how a population of 117 came to be carried as 196 and priced as unaffordable.

This is [check-design rule 4](../validation/check-design.md) arriving as a
count rather than as a check: the resolution set has to be what the *engine*
loads, not what we ship.

## 2. What the 45 actually were

| bucket | textures | rows | fix |
|---|---|---|---|
| **A** — the exact basename is in the tree under another directory | 22 | 59 | repoint |
| **B** — a typo with exactly one possible target | 6 | 6 | repoint |
| **C** — art no source mod ships | 17 | 52 | a content call |

`.source/` was searched for every one of the 45 basenames across all 52 mods:
**bucket C exists in none of them**, so "supply the art" means authoring it, not
re-harvesting. All 43 affected selector files come from a single source, Star
Trek: New Horizons (688086068).

**Two rows would have been repaired wrongly by the basename heuristic alone**,
and both were caught by reading the row's trigger:

- `starfleet_next_generation_02_mirror/tng2_human_female_admiral.dds` has exactly
  one same-named file in the tree — under `starfleet next generation 02/`, the
  **prime** folder. Its trigger is `uses_terran_uniform_pop`. The mirror folder
  it already names holds `tng2_mirror_human_female_admiral.dds`: the row drops
  the `mirror_` infix, and the right repair keeps the Terran Empire in a mirror
  uniform. Same for the male row.
- `starfleet_picard/picard_era_human_female_command.dds` matches nothing by
  basename at all, but lines 92–93 of the same selector already draw
  `pic_human_female_command.dds` for `picard_era = yes`. The target is forced by
  the file itself.

**A row is repointed, never deleted.** 33 of the 117 sit inside a `list = { }`,
where deleting an entry shifts every index after it and changes what other
species wear — the same reason decision 78 accepted a duplicated entry rather
than drop one. The other 84 are `"path" = { trigger }` conditionals, where a
deletion shifts nothing but still changes what that trigger draws.

**No `default =` row dangles**, before or after. Every miss is a candidate row,
so no selector was left with a broken fallback.

## 3. What landed

**28 textures, 67 occurrences, 32 files, 52 `patches:` replacements** in
`vendor.yml` — buckets A and B, none of which needed a call. 65 of the 67 are
live rows; two are commented-out rows in the tellarite selectors that the
literal replace carries along, which leaves those comments naming a path that
exists.

**Then four of bucket C fell as well, and that is the more useful half of this
decision.** Bucket C is *art no source ships*, so no rename can fix it — but the
substitute does not have to be chosen, because the tree keeps saying which one
was meant:

- `tos_mirror_human_female_ruler.dds`, **8 rows**, the largest single item.
  There is no mirror-TOS ruler top for either gender. The **male master answers
  the identical trigger itself**: `is_military_governor = yes
  uses_mirror_starfleet_uniform = yes snw_clothing_era = yes` draws
  `tos_mirror_human_male_admiral.dds` at line 1967. The female rows take the
  female admiral coat — copied across, not invented, exactly as
  [decision 20](20-empire-designer-clothes.md) took the male file's gating.
- `starfleet_tmp/tos_human_female_engineering.dds`. Its trigger is
  `uses_tmp_engineering = yes tmp_clothing_era = yes`, so the era is TMP and the
  `tos_` prefix is the typo; the male row with the same trigger set names
  `tmp_human_male_engineering.dds` in that same folder.
- `kelpian/kelpian_clothes_02.dds`. Kelpian clothes are gendered and nothing is
  named `kelpian_clothes_*`; the three rows around it in the same leader scope
  all name `kelpian_male_*`.
- `pakled/pakled_male_hair_bald.dds`. Pakled ships no bald texture — miradorn
  and tarlac do, which is why the name looks plausible — and the tree's shared
  one, `gfx/models/portraits/all/bald.dds`, is named by **55** selector files.

**Then the last thirteen, under one policy rather than thirteen decisions.**
These are the genuine content calls: art no source ships, and nothing in the
tree naming the substitute. The policy, approved 2026-08-24, is **repoint at the
nearest surviving sibling in the same family, never delete** — §5 records what
each one took and what its family had left to offer.

**45 textures, 125 occurrences over 46 files — 56 `patches:` entries, 79
replacements. 117 rows → 0.** `check_selector_texture_files` holds the tree
there.

**The lesson is where the answer lives.** Bucket C was defined as *needs a
content call*, and a third of it did not: the male mirror of the same row, the
neighbouring rows in the same scope, and a convention 55 files wide each named a
substitute that nobody had to choose. Read the trigger before pricing the call.

## 4. `check_selector_texture_files` — the resolves half

The question decision 78 split now has both halves in
[tools/validate.py](../../tools/validate.py): `check_selector_texture_paths`
asks *does it end `.dds`*, `check_selector_texture_files` asks *does it resolve*.

- **Resolution set is `BUILD` + `GAME_DIR`**, the pair `check_texture_basenames`
  already uses, for the reason §1 gives.
- **No scope and no floor.** The check reads only our own
  `gfx/portraits/asset_selectors/`. Vanilla's own selectors carry 7 unresolved
  rows over 5 textures — two `.dds.dds`, two that differ from the file only in
  case (`reptilian_slender_outfit_Admiral.dds`), three genuinely absent paragon
  textures — but those are vanilla's files, which this never opens.
- **Matching is exact, case included.** A case-only difference is the one form
  of this defect the container cannot test, since the game runs on the host. Our
  population is identical under either rule, so the strict choice costs nothing
  today and fails loudly if a copied vanilla row ever brings one in.
- **Findings are warnings, not errors, and nothing is acked.** The 17 that
  remain are open content calls, not reviewed exceptions;
  [acks.md](../validation/acks.md)'s warning about the ack that rots is exactly
  this case — an ack here would silence the open item forever. The check reads a
  `selector_texture_ack` list for the day a row is genuinely reviewed and left,
  and `vendor.yml` declares no such block.

**Mutation-tested**, as [rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)
requires, in two directions: against the repaired tree, whose floor is now **0**,
repointing one resolving row at a name nothing ships takes it to 1 row / 1
texture; and running with `STELLARIS_GAME_DIR` pointed at an empty directory
takes it to **1,053 rows / 103 textures**, which is the false-positive
population §1 describes, measured rather than argued.

## 5. The thirteen that were the content call

One policy covers all of them: **repoint at the nearest surviving sibling in the
same family, never delete.** Deleting an entry from a `list = { }` shifts every
index after it and changes what other species wear, so a duplicated entry is the
cheaper half of that trade — decision 78's reasoning, applied thirteen times.

| rows | texture | took | why that one |
|---:|---|---|---|
| 11 | `sth humanoid 08/sth_humanoid_08_male_clothes_01` | `_02` | male art is `_02`–`_04`; the female `_01` exists, which is where the name came from. One row is the single-entry Capellan civilian ruler |
| 6 | `human_civilian/human_terran_ruler_female_2` | `human_terran_ruler_female_1` | the Terran set has male `_1` and `_2` but only female `_1` |
| 6 | `human/sth_human_male_hair_black_style_05a` | `_05` | there is no male `05a`; `_05` and `_06a` exist, and the female set has its `05a`. Three of the six are commented-out rows |
| 6 | `doopler/doopler_male_clothes_01` + `_02` | `_03` and `_04` | the male art *is* `_03`/`_04` and the selector never named them; `_01`/`_02` exist only for the female. **No duplicate** — each list now names the two male textures that exist |
| 4 | `klingon_starfleet/pic_human_{f,m}_science_kdf` | the `pic2_` science top | the `pic_` era ships admiral, command and security and no science; `pic2_` ships the full set |
| 3 | `malon/malon_female_clothes_04` | `_05` | `_04` is absent for both genders and the list runs `_01`–`_06` around the hole, so any substitute duplicates one entry of six |
| 2 | `kriosian/kriosian_{f,m}_clothes_05` | `_04` | kriosian clothes stop at `_04`. Both were single-entry Mizar civilian ruler rows, so both missed on every draw |
| 1 | `confederation/…/coe_ent_human_male_security` | `coe_ent_human_male_command` | the male security top is the one member missing from that folder. The faction's own command top beats prime Starfleet's security top: the folder exists to make the Confederation look unlike Starfleet |
| 1 | `elaysian/elaysian_female_clothes_04` | `argrathian/argrathian_female_clothes_04` | the elaysian folder ships no clothes at all, and this selector flies argrathian throughout, including every `default`. Keeping the author's `_04` inside that family leaves the ruler distinct from the default, which is what a ruler row is for |
| 1 | `sth_avian/sth_avian_clothes_02` | `sth_avian_scientist` | that folder names its outfits by role and nothing is `_clothes_*`; this is the `leader_class = scientist` row, and the `official` row beside it draws the same file |

**Three of these rows were deterministic misses** — the Capellan and the two
Mizar civilian rulers are single-entry trigger-gated rows, so they fell back
every single time the trigger fired rather than one draw in N. Those three are
the ones a player would have reported.

**Two substitutes duplicate an entry already in the same list** — malon and
sth_avian. That is the trade above taken deliberately, not an oversight.

## 6. What this cost, and what it is worth watching for

The whole of it — 45 textures, 79 replacements, both checks, this file — came
out of **re-running a measurement rather than trusting the number beside it**.
The 196 had been carried in five documents for two weeks, it was priced as a
per-row content decision nobody wanted to start, and the real population was
117 rows of which 76 were somebody's typo.

`check_selector_texture_files` is now the thing that would have caught it: a
number in a document goes stale in silence, and a check that reports 0 does not.
