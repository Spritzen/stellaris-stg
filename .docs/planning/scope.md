# What we're building

> **What** — the product STG is, the explicit non-goal, and the settled calls
> that define its shape.
> **Open when** — proposing content, or weighing whether something belongs.
> **Then** — [Phases](phases.md) · [Architecture](../architecture/vendored-merge.md) · [Decisions index](../decisions/README.md)

A Star Trek reskin of Stellaris that **keeps playing like Stellaris**. Vanilla +
DLC mechanics, familiar Trek faces. You pick the Federation, the Klingon Empire,
the Romulans, the Cardassians, the Dominion — and the game underneath is still the
one Paradox ships, sharpened by the quality-of-life and galaxy-generation mods
worth having.

Target: **Stellaris 4.4.x "Pegasus"** (`modsCompatibilityVersion` 4.4).

## The explicit non-goal

Becoming Star Trek: New Horizons. STNH is the best Trek mod in existence and it
rebuilds the game from the ground up — 54 replaced technology files, its own
traditions, its own map scenarios. That is a different product. **We want the Trek
*dressing* on a vanilla *chassis*.**

> **Design test for any proposed change:** would a Stellaris player who has never
> watched Star Trek still recognise the game? If no, it probably doesn't belong.

## Settled

| | |
|---|---|
| **Distribution** | Personal use only, permanently. Never published to the Workshop. |
| **Shape** | **Standalone and self-contained** ([decision 01](../decisions/01-standalone-vendored-mod.md)). One mod, no dependencies. Enabling STG must be the only thing in the playset, and subscribing to or unsubscribing from anything must not change how STG behaves. |
| **Era** | TNG / DS9. All major powers established at game start ([decision 03](../decisions/03-content-scope.md)). |
| **Ariphaos Unofficial Patch** | **Dropped** ([decision 02](../decisions/02-drop-ariphaos.md)). Declares 4.2.4 against our 4.4 target and shadows 256 vanilla files, 247 of which differ from current 4.4 — as likely to be silent reversion as fixes. |
| **STNH art** | Take the art paths, never the script. The ship tree is pruned to the directories declarations actually name ([18](../decisions/18-walshicus-shipsets-replace-stnh-hulls.md)); unreferenced files are pruned by the closure ([45](../decisions/45-clutter-pass.md)); everything else is taken whole. [Details](../architecture/stnh-art.md). |
| **Ship art** | **17 of the 22 cultures the majors, quadrant and frontier powers fly** are Walshicus' vanilla-chassis shipsets; five (BAJ, TRI, ADR, BOL, BRE) stay on generated STNH hulls. [Decision 18](../decisions/18-walshicus-shipsets-replace-stnh-hulls.md) moved nine of the then-fourteen and superseded [17](../decisions/17-stnh-shipsets-on-a-vanilla-chassis.md) in part; the eight frontier powers of Phase 2 exist *because* the other Walshicus sets were already in the tree. |
| **Borg & Dominion** | Playable prescripted empires. No crisis scripting. |
| **Trek map** | Trek-named systems in a normally generated galaxy, **and home systems ARE placed**. The no-hand-placed-homeworlds half was wrong in a way only play showed: `system_name` is a *label*, so "Sol" was a label on a random system whose other planets came from the Federation's `planet_names` pool — Bajor and Andoria among them. 37 empires now name a real `initializer`. [Decision 25](../decisions/25-real-home-systems.md). **The "normally generated galaxy" half is now under revision**: six galaxies contained no Trek AI empire, and the mechanism that places them is a **static galaxy scenario** rather than the spawn lottery — [decision 92](../decisions/92-create-country-initializers.md), planned as [Phase 6](phases.md#phase-6--the-static-galaxy). A static map is a change to this settled call and should be recorded here when it lands. |
| **Source backup** | **`.source/` — a pinned copy of every source mod, and the build's only input.** `make vendor` never reads `/workshop`. Free: same btrfs subvolume, so it reflinks. [Decision 09](../decisions/09-source-snapshot.md), superseding [04](../decisions/04-no-source-archive.md). |

## On STNH's licence

*Stated once, then dropped.*

`/workshop/688086068/license.txt` forbids redistribution and modification. On your
own machine, for your own play, that binds nothing anyone will act on and it is
your call to make. It matters exactly once: **a build containing STNH assets can
never be published or shared.**

Since STG is permanently personal this costs nothing. Recorded here so a future
session doesn't propose a Workshop release without knowing. *(No other mod in
`/workshop` ships a licence file at all.)*
