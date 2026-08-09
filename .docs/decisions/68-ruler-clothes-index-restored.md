# 68 — An absent `clothes` is index 0, and index 0 is the file's first line

**Status:** SUPERSEDED 2026-08-08 by
[decision 69](69-ruler-clothes-dedicated-selectors.md). The Vulcan Confederacy
run drew all six of the empires below in garments this model does not predict,
so the enumeration is not "distinct texture paths in file order" — the section
*What is still not checkable*, at the bottom, is the half that held. The
indices are gone; the seven rulers now use a dedicated one-texture selector and
`clothes = 0`. Read this file for how the model was built and why one confirmed
data point was not enough, not for the mechanism.

**Originally decided:** 2026-08-08
**Closes the loose end** [decision 57](57-prescripted-rulers-unpin-clothes.md)
wrote down and could not settle: *"the remaining candidate is that an absent
`clothes` defaults to 0 rather than to unpinned — which the container cannot
establish."* A live run established it.

## The report

From the Terran Empire run: *"On the empire select screen the empress is set to
clothing 1 purple top."* Then, on the follow-up question: *"ufp was clothed
wrong in empire select"* — so it was never about the Terran Empire.

## The mechanism, and the one observation that pins it

`civ_human_female_clothes_13.dds` **is a purple jacket**, and it is
`humanoid_master_female_clothes_01`'s `game_setup` `default =` — the first
texture string in the file. The empress at "clothing 1" was wearing index 0 of
the enumeration the slider walks:

| | |
|---|---|
| index 0, female master | `human_civilian/civ_human_female_clothes_13.dds` — the purple jacket |
| index 0, male master | `human_civilian/civ_human_male_clothes_01.dds` |

So the enumeration is **the distinct texture paths in file order**, and an
unpinned prescripted ruler draws index 0 of it. Decision 57 removed `clothes`
from all 101 rulers believing that meant *unpinned*; it means *0*, exactly as
decision 23 was wrong about in the other direction.

**Only the master selectors are hurt by that, and that is the whole scope.** A
per-species selector's first line is that species' own `game_setup` default, so
index 0 is already right and unpinned is correct — which is why 95 rulers need
nothing and why nobody noticed for five days. Seven rulers use a
`humanoid_master_*`:

| | class | selector | pinned |
|---|---|---|---|
| United Federation of Planets | FED | male | 1 |
| Confederacy of Vulcan | VUL | female | 2 |
| Andorian Empire | ADR | male | 3 |
| Bajoran Republic | BAJ | male | 4 |
| Trill Symbiosis | TRI | female | 5 |
| Terran Empire | TER | female | 6 |
| Turei Commonwealth | TUR | male | — |

The indices are 1..6 because that is the order
[decision 22](22-empire-designer-clothes.md) and
[64](64-terran-empire-mirror-uniforms.md) appended the `game_setup` rows in.
**The value we most need is in the region of the model we are most sure about**
— immediately after the one index a live run has confirmed.

## Decision

Pin `clothes` on those six, **generated, never counted**:
`tools/gen_ruler_clothes.py` reads the merged selector, finds the `game_setup`
row gated on the empire's own species class, and writes its position in the
enumeration. That is decision 23's failure repaired rather than repeated —
`texture = 1 clothes = 1` on 101 rulers was nobody's choice and out of range on
74; this is one number per empire with a derivation behind it.

`check_prescripted_appearance` re-derives it every run, independently rather
than by importing the generator's function — a generator and its check sharing
one function can only agree with each other. Calibrated by setting the Terran
empress back to 0: **one finding, naming the purple jacket, and 0 when
correct.**

TUR is left unpinned and reported, not guessed at: it has no `game_setup` row
because it is AI-only and never reaches the designer, and its in-game ruler goes
on reading the `ruler` scope, which is right.

## The trade-off this makes, on one empire

A pinned index is resolved once and kept for the game, so the six rulers no
longer re-evaluate the selector. For five of them the pinned texture is what
the `ruler` scope resolves to anyway and nothing changes in play.

**The Federation is the exception and it is a real choice.** Its officials wear
`human_president_male_1..4.dds` — plain business suits — and `clothes = 1` is
STNH's dedicated `federation_president_male_1.dds`, a Starfleet formal robe.
Pinning it means the President stops matching his officials, which is the
literal complaint decision 57 fixed.

Taken deliberately, on the reading that decision 57's report was *"the president
looks like a random civilian"* rather than *"the president must wear the same
texture as an official"* — with `clothes = 0` he was wearing
`civ_human_male_clothes_01.dds`, which is neither. A President in Federation
robes is the thing decision 22 chose that art for.

**If that reads wrong in play, the one-line alternative is `clothes = 268`** —
`human_president_male_1.dds`, the officials' own first texture — plus the same
change to the FED `game_setup` row so the designer keeps agreeing with the game.

## What is still not checkable

The enumeration model has **one** confirmed data point. Index 0 is proven;
1..6 are inferred from it and from the row order we ourselves wrote. A live run
that shows the six empires in their own clothes confirms the rest; a run that
shows them wearing each other's would say the model is off by a constant, which
is exactly the shape that would be legible.

The count is the loose thread: this model gives 463 distinct textures for the
female master and the live run reported *"1 of 472"*. Decision 64 asserted the
slider *"enumerates every distinct texture in the portrait's clothes_selector"*
and quoted both numbers without noticing they disagree. The ordering at the
front is confirmed; the tail is not, and nothing here depends on it.

## The rule worth carrying

**"We removed the thing that was wrong" is not "we set it to the right value".**
Decisions 23 and 57 are the same mistake pointing in opposite directions: 23
wrote an index believing 0 meant *auto*, 57 removed the key believing absence
meant *auto*, and both times the engine had a third answer nobody had asked it
for. An absent field is a value. Say what the value is before relying on its
absence.
