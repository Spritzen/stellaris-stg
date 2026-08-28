# 94 — The third quadrant of the contention hole is `src/` outside `common/` and `localisation/`, and it was clean

**Status:** decided, 2026-08-28 — **the check is in and the tree is at zero.**
No content call, no live run, and **no defect found**: this closes a hole rather
than repairing one.
**Follows** [decision 92](92-src-contests-its-own-loc-keys.md), which is the same
hole one directory over, and which ends by telling the next session to ask where
else the shape can hide. This is that question asked a second time.

## Where this came from

Decisions [91](91-src-contests-its-own-name-lists.md) and
[92](92-src-contests-its-own-loc-keys.md) are one finding in two places.
`check_key_conflicts` gates on **two sources**, so a key `src/` contests with
*itself* can never satisfy it; 91 wrote `check_src_key_contention` to close that
for `src/common/`, and 92 found the identical hole in `src/localisation/` and
closed it with `check_src_loc_key_contention`.

**Neither covers the rest of `src/`.** The tree also writes into `events/`,
`prescripted_countries/`, `interface/`, `gfx/` and `map/`, and nothing asked the
question there at all:

- `check_key_conflicts` walks `stg-build/common/` only;
- `check_src_key_contention` walks `src/common/` only;
- `check_src_loc_key_contention` walks `src/localisation/` only;
- `check_duplicate_entities` reaches art, but walks **`*.asset` only**, so it
  sees no `.txt` and no `.gfx`.

That is **384 declarations of ours across 11 directories** where the question had
never been put.

## Why it is worth asking even though nothing was found

**The failure it guards is total and silent.** Two files declaring one event id
is not a cosmetic duplicate the way five of decision 92's six were: one of the
two events never reaches the game, **filename sort decides which, and nothing is
logged**. `events` is in `FIOS_DIRS`, so it is the *first* filename that wins —
the opposite of the usual last-wins reading, which is exactly the sort of thing
a session gets backwards under time pressure.

That is [decision 90](90-add-anomaly-target-scope.md)'s shape. There, an anomaly
was never added on any planet the event ever fired for, the anomaly was the whole
payload of the event, and the tell was eight lines away in the same file. A
contested event id loses the whole event the same way and leaves even less
evidence.

**And the population is about to grow.** The story-event pool is the one place
[open questions](../planning/open-questions.md) marks as a cheap content gap —
eleven of the 22 majors, quadrant and frontier powers are outside the species
gate entirely, and growing the pool is the recorded fix. Event ids in
`stg_story.*` are hand-assigned. The next session to add ten of them is precisely
the one that can collide one, and this check is what tells them.

## The hard part is identity, not contention

**The block key is not the identity here, in two of the three forms** — which is
[rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed),
and the first three cuts of this check each got it wrong in a different way. All
three are recorded because each was a *confident* wrong answer:

| form | identity | what went wrong first |
|---|---|---|
| `events/` | the `id` **inside** a top-level `*_event = { … }` | matching every `id =` conflates declaring an event with **firing** one. `country_event = { id = x days = 10 }` in an effect body is a reference. Counting those reports **33 collisions in vanilla** and none of them is real; reading only depth-0 blocks, vanilla's floor is **0 across 9,995** |
| `*.gfx` | the `name` of each **direct child** of the depth-0 container | two written forms, and an anchored `^\s*name = …$` sees only one: `stg_paragon_backgrounds.gfx` writes all **28** of its sprites on a single line each, so it found **0** of them ([rule 8](../validation/check-design.md#8-a-reference-has-a-written-form-as-well-as-a-name)). Matching `\w*Type` rather than "any child" then missed all **14** `pdxparticle` declarations, because the block key had been guessed instead of read |
| everything else | the depth-0 block key | nothing; this is `check_src_key_contention`'s form, and it covers `prescripted_countries/`, where the key is the country id |

**And reading the `name` anywhere in a block body is wrong too.** The first cut
reported `cardassian_01_orbital_station_mesh` as declared twice in
`src/gfx/models/ships/stg_stnh_restored_station_meshes.gfx`. It is declared
once: the file wraps its declarations in a depth-0 container, so the container
and its single child each yielded the **child's** name. The field has to be read
at the block's own depth 0.

> **This is decision 78's lesson for the third time.** *Finding a name is not the
> same problem as getting the body.* A regex that solves the first hands you a
> confident wrong answer to the second — and here it handed out four of them
> before the numbers stopped moving.

## The gate is derived from vanilla, and half the directories exclude themselves

[Rule 4](../validation/check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand):
a directory is asked about only if vanilla's own copy of it **declares at least
one identity and contests none** — neither across two files nor twice inside one.
Nothing is hand-listed. Of the eleven directories `src/` writes into outside
`common/` and `localisation/`, five pass and five are excluded by vanilla itself:

| excluded | ours | why vanilla contests it |
|---|---|---|
| `gfx/portraits/asset_selectors` | 9 | vanilla contests **11**, the shared `*_hair_1` selectors that a dozen clothes files each declare |
| `gfx/portraits/portraits` | 3 | `portraits` **is** the block key, so every file declares it — which is what `WHOLE_TEXT_DIRS` already says: the file is the unit |
| `interface` | 172 | vanilla's `fonts.gfx` declares `large_title_font` and seven others **five times each**, once per charset |
| `map/setup_scenarios` | 1 | all five vanilla files declare `setup_scenario`; the key is the type |
| `music` | 1 | `song` likewise — 17 of them in `songs.txt` alone |

**These are not a convenience filter.** Each is a database where "one name, one
declaration" is simply not an invariant, and vanilla says so in its own tree
rather than us deciding it. The `interface` exclusion is the one someone will
want to widen: it costs the check 172 of our sprite names, and what stands in
the way is real per-language font declarations, not an accident.

**A directory with no vanilla population is not asked either**
([rule 5](../validation/check-design.md#5-a-fact-you-cannot-derive-from-vanilla-is-borrowed-and-must-be-labelled-so)).
A floor of 0 out of 0 is not a calibration. That costs exactly one place: the
five `pdxmesh` names in
`src/gfx/models/ships/stg_stnh_restored_station_meshes.gfx`, in a directory where
vanilla ships no `.gfx` or `.txt` at all — and `check_duplicate_entities` does
not reach them either, because it walks `*.asset`. **Widening to them means
finding a real floor first, not dropping the requirement for one.**

## The floor, and the finding

The five asked databases hold **193 of our identities against 11,857 of
vanilla's, and vanilla contests none of them**:

| database | ours | vanilla |
|---|---|---|
| `events` | 77 | 9,995 |
| `prescripted_countries` | 99 | 53 |
| `gfx/particles` | 14 | 1,740 |
| `gfx/models/planets` | 2 | 47 |
| `interface/resource_groups` | 1 | 22 |

**`src/` contests nothing. The finding is zero, and that is the result.**

## The check

`check_src_identity_contention`, new in `tools/validate.py`, beside its two
siblings. Two reports: an identity declared by **two files** of ours, naming the
FIOS/LIOS winner, and one declared **twice inside one file**.

**It is calibrated two ways, because a check that cannot fail is worse than an
absent one** ([rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)).

**Pointed at the built tree, the same code reports 6** — and every one is a
source overriding itself, which is why the scope is `src/` and what
[decision 11](11-fix-source-errors-dont-drop.md) forbids second-guessing:

| finding | family |
|---|---|
| `pdmaengine.40` in `pd_ma_engine.txt` vs `zzz_pd_ma_engine_cryo.txt` | Planetary Diversity's own `zzz_` override — the family decision 91 already met |
| `toxoids.1` in `!vanilla_toxoids_events.txt` vs `…_fix.txt` | a mod's base/`_fix` pair |
| three `pd_*_laser_muzzle_particle` | PD declaring each twice in one file |
| `NInterface` across two UIOD defines files | UIOD's own split |

**And by injection**, the way decision 90 was calibrated: a second
`stg_story.1` added to `stg_anomaly_events.txt` and a second `stg_arcsite.100`
inside its own file. Both reports fire, name both files, and name
`stg_anomaly_events.txt` as the FIOS winner. Reverted; the tree is at 0.

## The thing worth carrying forward

**"Ask where else this hole is" terminates, and it is worth running it to the
end.** Decision 91 found a defect, 92 asked the question again and found another,
and 94 asks it a third time and finds nothing. **The third answer is the valuable
one** — it is what turns "we fixed two instances" into "the shape is now covered
everywhere it can occur", and it costs one session rather than a live run.

**A zero finding is only worth as much as the proof the check can fail.** This
one is worth stating because the check reports 6 on the tree next door and 2 on
demand. Without those, "0 findings across 193 identities" would be
indistinguishable from the blind checks
[rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)
was written about — and this check was blind, in three different ways, before it
was measured.
