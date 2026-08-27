# 64 — The artist's vocabulary is not the game's

**Status:** decided, 2026-08-08
**Fixes the tier-2 half of** [decision 57](57-mounts-share-existing-points.md),
whose own docstring named `torpedo_01` as an example of a hardpoint it could
borrow and which had never been able to see one.

## The report

From the live Terran Empire run: *"Intrepid-class corvette — I don't know where
the artist drew them but they all sit in 1 point which looks fine, check there
are no more than 1 artist point for this model."*

There were two.

## What the mesh bakes

```
terran_nx_corvette.mesh
  medium_gun_01      ( 0.000, -0.694, -1.509)   ventral, forward
  point_gun_01       ( 0.000,  1.801,  3.360)   dorsal, aft
  target_locator_01/02                          aim points, correctly ignored
```

`terran_nx_corvette_S3_entity` wants three small guns and the mesh bakes none of
them, so decision 57's tier 2 applies: round-robin the missing mounts over the
other hardpoints the same mesh bakes. It found **one**, and stacked all three
guns on it.

## Why the second one was invisible

`mount_vocabulary()` is the set of `locatorname` values **vanilla's** section
templates use — 201 names, derived from vanilla per CLAUDE.md rather than
asserted. That is the right answer to *"what does the game bolt a gun to?"*, and
it is what decides which mounts a section requires.

It was also being used to answer *"where did the artist draw a gun?"* — and
those are different questions. Vanilla's own art answers both with one
vocabulary, so nothing distinguished them; the Trek shipsets do not:

| the thing | Trek art | vanilla |
|---|---|---|
| torpedo tube | `torpedo_NN` | no stem at all |
| point-defence mount | `point_gun_NN` | `pd_gun_NN`, `pd_turret_NN` |
| spinal mount | `extra_large_gun_NN` | `xl_gun_NN`, `extra_large_turret` |

**164 meshes bake `point_gun_01` and 189 bake `torpedo_01`.** Every one was
invisible as an anchor. So were `small_gun_14..18`, `medium_gun_14` and
`large_gun_10..12` — vanilla's own stems, at indices vanilla's art never needed.

## Decision

Split the two questions. `mount_vocabulary()` keeps meaning what it meant, and a
new `is_hardpoint()` answers the artist's question with three rules:

1. vanilla's templates mount on this exact name — derived;
2. vanilla mounts on this **stem** at some other index — derived, and what
   recovers `small_gun_14` and `large_gun_12`;
3. the stem is one of three the Trek art uses and vanilla has no word for —
   **borrowed, and labelled as borrowed**, in one block at the top of the file
   with the provenance next to it, per CLAUDE.md's rule for facts vanilla cannot
   supply.

Only the *anchor* side reads it. Widening the required set would invent mounts
no section template asks for.

## What it actually changed, which is less than it sounds

Re-derived across all 27 shipsets by decision 57's own procedure — delete the
generated overrides, re-vendor, re-run, re-vendor:

| | before | after |
|---|---|---|
| mounts placed | 1,626 | 1,626 |
| on a point the artist drew | 599 (34%) | 599 (34%) |
| bounding-box spread | 1,152 | 1,152 |
| **positions that moved** | — | **242, across 65 section entities** |
| files rewritten | 157 | 157 (62 differ) |

**No mount changed tier, and that is the finding.** Tier 3 is reached only when
the mesh bakes *no* hardpoint at all, and a mesh that bakes `point_gun_01`
usually bakes a `medium_gun_01` too — so nothing was ever left on a guessed
position by this. Every one of the 242 was already on a point somebody drew;
they are now spread over more of them instead of doubling up. The Terran
corvette's `small_gun_02` moved from `medium_gun_01` to `point_gun_01`, which is
what the report asked for.

That ratio is worth stating plainly: this bug cost **spread, not correctness**.
Had it been the other way round — guns in places nobody drew — it would have
been decision 26's defect returning, and it was not.

## The one this does not fix

`terran_nx_corvette_M1S1_entity` wants `medium_gun_01` and `small_gun_01`; the
frigate mesh bakes `small_gun_01`, `small_gun_02` and `torpedo_01`. Tier 1 fires
because one wanted mount is baked, and *the tiers do not mix* (decision 57), so
`medium_gun_01` doubles onto `small_gun_01` while `small_gun_02` and
`torpedo_01` sit unused. That rule was deliberate and is left alone: mixing
tiers would let a section's own answer be diluted by another section's. Named
here so the next reader knows it is a choice rather than the same bug again.

## The second sweep — asked the other way round

*"How was this missed? Recheck all ships again for artist mounts and ensure we
are capturing them all."*

The first pass fixed the three names the report led to. That is repairing the
instances a log named, which CLAUDE.md forbids — so the whole corpus was
enumerated instead: **1,182 ship meshes, every baked locator name, classified.**
Three more families fell out, none of which the corvette would ever have shown:

- **A trailing `.001` / `.002`** — Blender's duplicate-object numbering, on 44
  gun names. Not a rename: **153 of 157 sit in the same mesh as their own base
  name at a DIFFERENT position**, so each is a second emplacement the artist
  copied and moved.
- **A trailing `_l` / `_r` / `_X` / `_V`** — `large_gun_02_r`,
  `medium_gun_01_X`. The `_l`/`_r` half is *vanilla's own* convention
  (`large_gun_01_l` and `medium_gun_01_r` are in its templates), so recovering
  it is derived, not borrowed.
- **`support_gun_NN`, `hangarbay_NN`, `large_hangarbay_L/R`** — two more stems,
  and `hangar_NN` is vanilla's word for the same emplacement.

Handled by stripping **one** suffix and re-asking, which is safe by
construction: the base has to be a hardpoint in its own right, so the rule can
only promote a name that already means a gun and can never invent a kind of
point. It also covers the next exporter artefact without another edit.

Result: **157 distinct names accepted (9,096 occurrences), up from 94 (8,913)**,
and of the 381 still rejected **not one mentions a weapon in its name** — the
remainder is lights, aim points, engines, exhausts, explosion nodes, hull parts
and stray Blender object names (`USS_Edison`, `Excelsior_Class`). Re-derived
again: **21 more positions moved across 6 section entities**, 263 over both
passes, and once more no mount changed tier.

## How this class of defect gets caught next time

**How it was missed is the useful half of the answer, and it is a shape worth
naming: every number decision 57 reported counts what the rule DID.** Mounts
placed, tiers used, 0 outside the bounding box, 0 unplaceable — a rule that
stops recognising a whole kind of point moves none of them, because the mount
it cannot anchor is quietly spread instead and still counted as placed. The one
artefact that could have exposed it was the docstring, and the docstring
*asserted* `torpedo_01` was an example of what tier 2 caught, so the thing to
check read as already checked.

That is decision 43's lesson in a fourth database: **the reverse question**. All
of this asked "does every mount get a position?" and none of it asked "what does
the art carry that we do not recognise?"

So `fix_ship_locators.py --all` now prints exactly that: the distinct baked
locator names it did *not* treat as hardpoints, with counts, at the end of every
run. It is a census and not a check, on purpose — no derivation from vanilla can
say `support_gun_01` is a gun, only a person reading the list, and the job is to
put the list where whoever re-derives will read it. The borrowed table beside it
is a named constant for the same reason: the next shipset with a fifth word for
a gun should be a two-line edit, not an archaeology exercise.

## The rule worth carrying

**Deriving from vanilla answers vanilla's question.** CLAUDE.md's allowlist rule
is right and this obeyed it — the set really is computed from vanilla and really
does survive a game patch. It was still the wrong set, because it was derived
for one question and read for another, and a derived allowlist carries no sign
saying which question it answers. Ask what the set *means* before reusing it,
not just where it came from.
