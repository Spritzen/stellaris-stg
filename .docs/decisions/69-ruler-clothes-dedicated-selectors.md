# 69 — A shared master selector cannot be indexed; give the ruler its own

**Status:** decided, 2026-08-08
**Supersedes** [decision 68](68-ruler-clothes-index-restored.md), whose
enumeration model a live run falsified at all six positions it set.
**Closes** the loose end 68 left open for TUR as well.

## The report

From the Vulcan Confederacy run, six empires clicked through in the empire
designer:

| Empire | class | selector | pinned | decision 68 predicted | what was drawn |
|---|---|---|---|---|---|
| United Federation of Planets | FED | male | 1 | `federation_president_male_1` | "black leather or machine like top" |
| Confederacy of Vulcan | VUL | female | 2 | `civ_vulcan_female_clothes_02` | "grey red-trimmed, enterprise-era Starfleet" |
| Andorian Empire | ADR | male | 3 | `andorian_male_clothes_admiral` | "black top with tubes, red and green lights" |
| Bajoran Republic | BAJ | male | 4 | `bajoran_male_clothes_01` | "another federation top" |
| Trill Symbiosis | TRI | female | 5 | `trill_female_clothes_01` | "another different federation top" |
| Terran Empire | TER | female | 6 | `ent_mirror_human_female_ruler` | "black-trimmed red federation top, not purple" |

The predicted textures were rendered out of the built tree and compared against
those descriptions. Index 2 of the female master is a white-and-gold Vulcan
robe; index 6 is the gold-and-black ENT mirror coat. Neither is what was drawn.
The user's own summary is the finding: *"blindly trying to select something
isn't working, and we could be going back and forth through all 400 odd
different clothes."*

## What decision 68 got wrong, and the part that was right

68 inferred the enumeration — *the distinct texture paths of the selector, in
file order* — from **one** confirmed data point, the Terran empress drawn at
"clothing 1" in the purple jacket that is the female master's first texture
string. It said so explicitly: *"Index 0 is proven; 1..6 are inferred from it
and from the row order we ourselves wrote."* It even recorded the arithmetic
that disagreed — the model gives 463 textures where the designer reported 472 —
and set the disagreement aside.

Index 0 still looks right. Everything above it does not, and **nothing readable
from this container establishes what the enumeration actually is.** The
selector is 278 KB of STNH art wiring; the engine builds its list somewhere we
cannot see.

## The decision: stop indexing

**STNH never indexes into a master selector, and that is the convention we were
missing.** For the empire-select screen it gives the ruler a portrait whose
`clothes_selector` holds exactly **one** texture, and pins `clothes = 0` — the
one index a live run has confirmed.

The file is `gfx/portraits/asset_selectors/Heroes/leader_screen_clothes.txt`
and it has been in our tree since the first harvest:

```
human_leader_clothes_03 = {
	default = "gfx/models/portraits/human_civilian/federation_president_male_1.dds"
}
vulcan_leader_clothes_01 = {
	default = "gfx/models/portraits/vulcan/civ_vulcan_female_clothes_02.dds"
}
```

Two of those defaults are the exact garments our own `game_setup` rows name.

**Measured, not assumed.** Of STNH's 112 prescripted rulers, **2** sit on a
`humanoid_master_*` selector and one of those two is vanilla's `default.txt`
template. 91 of 112 pin `clothes = 0`. Of the 21 that pin something else,
**three are out of range of a one-texture selector** — `leader_female_03` pins
`clothes = 109` against `trill_leader_clothes_01`, which declares one texture.
That is how little the number matters once the selector has one entry, and it
is the strongest evidence available that STNH treats the index as inert.

STG had **7 of 101** rulers on a master selector.

## What was built

`tools/gen_ruler_clothes.py`, rewritten. It writes two generated files and
edits the seven ruler blocks to name the new portrait with `clothes = 0`:

- `src/gfx/portraits/asset_selectors/stg_ruler_clothes.txt` — seven one-texture
  selectors.
- `src/gfx/portraits/portraits/stg_ruler_portraits.txt` — seven portraits, each
  a clone of the species portrait's `entity`, `attachment_selector`,
  `greeting_sound` and `character_textures`, changing **only** the clothes
  selector. The face, the hair and `texture = 0` keep meaning what they meant.

**The intent is still derived, never counted.** The garment each empire should
wear is read from the `game_setup` row the master selector gates on that
empire's own species class — the rows [decision 22](22-empire-designer-clothes.md)
added, which stay as the written record of the intent even though the engine
never reaches them (see below). Where a class has no such row, the `species`
scope's row for the same class is used. That is what fixed **TUR**, the Turei
Commonwealth, which decision 68 reported and left unpinned because it is AI-only
and has no designer row: the rule was swept rather than the instance repaired,
and the seventh ruler came with it.

The origin portrait is recorded as a comment in the generated file and read back
on the next run, so re-running after the prescripted file already names
`stg_*_ruler` still clones from the species portrait rather than from ourselves.
Verified idempotent.

## The second finding, which explains decision 57 as well

**Vanilla writes 0 trigger rows inside a `game_setup` scope, across all 169 of
its asset selectors. STNH writes 0, across 563 blocks.** 732 real examples of
the construct, and every one of them is a bare `default =`.

Decision 22 invented conditional rows in that scope, and
[decision 57](57-prescripted-rulers-unpin-clothes.md)'s observation — every
master-selector ruler falling to the human-civilian default once the pins were
removed — is exactly what a scope that ignores its rows would produce. Decision
68 read that same observation as proof that *an absent `clothes` is 0*, and
never asked whether the rows fire at all. **One observation, two explanations,
and 68 picked one without ruling out the other.**

Both are now moot: a one-texture selector renders the same garment whichever is
true. The `game_setup` rows are kept as the intent record and the generator
reads them; nothing depends on the engine evaluating them.

## The check

`check_prescripted_appearance` no longer re-derives an index. **Asking a
question whose answer we cannot establish is worse than not asking it** — it
reported `ok` on six wrong rulers for a day, with a number to show for itself,
which is the failure [decision 33](33-duplicate-entity-declarations.md) names.

It now asks the question that needs no enumeration: **a prescripted ruler must
not sit on a `humanoid_master_*` selector at all.** Calibrated by reverting the
repair: **7 findings before, 0 after.** The in-range half stays and now covers
every selector, because a one-texture selector makes an out-of-range index cheap
to write and impossible to see.

One bug was fixed in the same pass and is worth naming, because it silently
shrank an existing check: the selector lookup globbed
`gfx/portraits/asset_selectors/*.txt`, and **STNH keeps 530 of its 531 selectors
in per-species subdirectories** where vanilla has none. A top-level glob finds a
handful of files. `rglob` now, in both trees.

## What is still not settled

- **The enumeration itself.** Unknown, and now unused. If a future change ever
  needs it, the cheap experiment is to step the designer's clothes slider from 0
  and record the first half-dozen garments against a rendered contact sheet of
  the candidate order — one screen, not 400 clicks.
- **Whether the Federation president should wear the Starfleet formal robe at
  all.** Decision 68 raised this and it is unchanged: `federation_president_male_1`
  is a robe, his officials wear plain suits (`human_president_male_1`). The
  one-line alternative is to change the FED `game_setup` row and re-run the
  generator — the intent lives in one place now, so it is a one-word edit.
- **Whether the seven portraits belong in a `portrait_group`.** They are in
  none, which is what STNH does for 15 of its own leader portraits. A prescripted
  empire names its ruler portrait explicitly, so membership should not be needed
  — but nothing in the container can confirm the designer agrees.

## The rule worth carrying

**When a value cannot be derived, change the design so it is not needed.**
Decisions 23, 57 and 68 are three attempts to write the right number into a
field whose meaning the container cannot see — one wrote an index, one removed
it, one computed it — and all three were wrong in a way that took a live run to
find. The fix was never a better number. It was a selector with one entry, in a
file the source mod had already written.
