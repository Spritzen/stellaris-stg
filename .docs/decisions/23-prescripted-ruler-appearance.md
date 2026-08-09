# 23 — Prescripted rulers pin no appearance index

**Status:** decided, 2026-08-03
**Follows** [decision 22](22-empire-designer-clothes.md), which fixed the same
complaint in the empire designer and left the in-game starting ruler wrong.

## The report

After decision 22 shipped, the user reported that the *starting ruler* clothes
were still wrong for the United Federation of Planets, the Andorian Empire and
the Bajoran Republic — the same three empires, now in the running game rather
than the picker. Decision 22 had fixed the `game_setup` scope only.

## What was actually wrong

A prescripted `ruler = { }` block can pin the leader's appearance:

```
texture = 1
clothes = 1
```

Those are indices, not flags. STG set `texture = 1 clothes = 1` on 20 of its 22
playable empires and on all 79 minor powers, and neither value was chosen — the
first empire file set them and every later batch copied the block.

**`texture = 1` is out of range on 74 of the 101 rulers.** Vanilla varies the
index freely because a vanilla portrait carries several body textures; most STNH
Trek portraits carry exactly one, so index 1 is off the end of the list.
`bajoran_male_01`, `andorian_male_01`, `klingon_male_05`, `cardassian_male_01`
and 70 more declare a single `character_textures` entry. The engine falls back
silently rather than refusing.

**`clothes = 1` is the half that produced the reported symptom**, and the
evidence for it is circumstantial rather than proven from the container:

- STNH sets `clothes = 0` on **91 of its 112** prescripted empires, using these
  same portraits and these same selectors. The 21 that differ (`9`, `88`, `109`)
  are deliberate picks, and `109` shows the index space is a long flat list, not
  a per-entry offset.
- The species that looked wrong are exactly the five whose portraits share
  `humanoid_master_*_clothes_01` — FED, VUL, ADR, BAJ, TRI. Every other Trek
  people has a per-species selector, where pinning index 1 still lands on that
  species' own clothing, which is why none of them was ever reported.

A pinned index means something different in a 44-species shared list than in a
one-species list. That is the same shape as decision 22's finding — *a shared
selector cannot be treated like a per-species one* — arriving through the other
door.

## Decision

**`texture = 0` and `clothes = 0` on all 101 prescripted rulers**, matching
STNH's own convention for these portraits and letting the clothes selector decide
— which is the whole point of the trigger bodies decision 16 wrote and the
`game_setup` gating decision 22 added.

Swept across all 101 rather than repaired on the three the user named, per
`CLAUDE.md`: 74 of them carry the out-of-range `texture` and none would ever
produce a log record. The 17 species with their own selector change from index 1
to index 0 of their own list — still their own clothing, possibly a different
outfit, and now consistent with the rest.

## How this class of defect gets caught next time

`check_prescripted_appearance` resolves each ruler's `portrait` to its
`character_textures` count and fails on an index past the end. Calibrated by
restoring `texture = 1` in `stg_major_powers.txt`: **exactly the two rulers whose
portraits declare one texture** (Klingon, Cardassian), and silence on the three
whose portraits declare three or eight. No false positives.

**Only `texture` is checked, and that limit is the point.** It is the one index
with a declared length to check against. `clothes` indexes whatever the selector
produces at evaluation time, which the container cannot see — so the check
cannot verify the half that actually caused the report, and saying so is better
than a check that looks like it covers both. What protects `clothes` is that
nothing pins it any more.

## Loose end

Two files in `src/prescripted_countries/` briefly gained a UTF-8 BOM during this
edit and had it stripped again. Vanilla's `prescripted_countries/` is BOM-free in
all 20 files; only `common/name_lists/` is BOMed, 76 of 76. `make validate`
derives that per folder and would have caught it.
