# STNH art is additive-only

> **What** — which STNH paths are taken, the skip rule that protects earlier
> sources, and the four ways STNH's art is wired to a `common/` we never vendor.
> **Open when** — touching anything from Star Trek: New Horizons, or an STNH
> reference resolves to nothing.
> **Then** — [Harvest order](harvest-order.md) · [Conflict register](conflict-register.md) · [decision 08](../decisions/08-stnh-art-shadows-vanilla.md)

Take from STNH only these paths — `gfx/portraits`, `gfx/models/ships`,
`gfx/models/portraits`, `gfx/particles`, `gfx/event_pictures`,
`gfx/loadingscreens`, `flags/`, `music/`, `sound/`, plus eleven loose files at the
top of `gfx/models/` — and **skip any path an earlier source already claims**.

**Never** STNH's `common/`, `events/`, `interface/` or `map/`: that is the
total-conversion script we are deliberately not shipping.

> **`gfx/models/portraits` is not a typo for rooms.** Stellaris keeps room
> entities there too (vanilla `ar_baol_01_room.asset`) and there is no
> `gfx/models/rooms` in either tree. That path carries STNH's Trek species
> portrait *textures*; the `gfx/portraits/portraits` above it is 1.2 MB of `.txt`
> declarations pointing at them. **Both halves, or every Trek portrait resolves
> to nothing.**

## Two path families are re-cut at harvest

**`gfx/event_pictures`** is resampled to vanilla's dimensions
(`resample_to_vanilla:`). STNH ships 569 vanilla paths at 620×264 where vanilla is
450×150, and `additive_only` has never protected vanilla — so vanilla's sprites
and UIOD's `eventwindow.gui`, both cut for 450×150, drew them at 930×396 inside a
693×239 frame. [Decision 42](../decisions/42-event-picture-geometry.md).

**`gfx/portraits/city_sets`** is re-cut the same way, and it needed a second fit
mode — and then a second way of getting a target.

The six prefixes STNH ships under its own Trek names shadow no vanilla path, so
reading the target off *a vanilla file* had no answer for them and they stayed at
70% through two live runs. `target: family` reads it off vanilla's own *family*
instead — 266/271 at 800×400, 91/91 at 952×340 — which is still derived rather
than asserted. Opt-in per rule, because vanilla's event pictures have no such
single answer. [Decision 63](../decisions/63-city-set-family-targets.md).

Vanilla ships all 266 of its `*_city_l0N.dds` at 800×400 with each layer's content
at its own offset inside that canvas; STNH's is 560×280 — **exactly 70%** —
because its own `interface/`, which we never take, was cut for it. 153 files, all
STNH's, and the live symptom was the city art sitting low and small on every
planet while the backdrop behind it looked right.

*The backdrop was right because `additive_only` makes STNH lose all 121
`environments/` paths to the mods that own them, so only the half nobody else
claims was ever wrong.*

`fit: canvas` pads a trimmed file back onto the source's own canvas,
bottom-aligned, before scaling — a centre crop would have cut 20% off the width of
41 of them. [Decision 58](../decisions/58-city-set-geometry.md).

> **A third door into the same symptom, and the last: the ten files *larger* than
> that canvas.** The pad grew the box to fit them rather than cropping, which fed
> the scale a box of the wrong aspect and squashed `vulcan_01`'s city — a playable
> empire's — to 76% of its height. The pre-resize height is now derived from the
> canvas, so the scale is always uniform and the failure mode is gone **by
> construction** rather than checked for.
> [Decision 66](../decisions/66-city-set-canvas-overflow.md).

## What the skip rule protects

Vendored last without it, STNH would win **162 contested paths** against mods we
kept on purpose:

| Contested | vs | What it would cost |
|---|---|---|
| 121 × `gfx/portraits/environments/pc_*_sky.dds` | PD - Vanilla Replacements (98), UIOD (17), Real Space (5), PD (1) | Planet-view backdrops keyed to planet classes those mods own |
| 26 × `gfx/particles/` | ASB Ironman (17), Real Space (9) | Combat VFX and star particles those mods own |
| 10 × `gfx/event_pictures/*_planet.dds` | PD - Vanilla Replacements | Vanilla-named planet pictures; we keep PD's planets, so PD's pictures should match |
| 5 × `gfx/models/ships/{mammalian_01,other}/` | ASB Ironman | A vanilla shipset entity definition and shared VFX textures — no Trek content |

The rule is nearly free, because **none of STG's Trek identity is in the contested
set.** STNH's ship directories, every species portrait, every room, and everything
under `flags/`, `music/` and `sound/` are uniquely STNH's and arrive untouched.
The only contested `gfx/portraits/` files are under `environments/`.

> **"Nearly" is doing work, and it is the one way this rule bites.** Where STNH
> *forked* an earlier source's file rather than shipping its own, the skip
> silently drops STNH's additions — while STNH art that references them is
> vendored and calls for them anyway. That happened twice, both against Real
> Space; [the conflict register](conflict-register.md#needs-a-real-merge--write-the-file-in-src) has the
> fix. **Nothing reports this class**: from the vendor tool's point of view a
> skipped path is the rule working correctly.

## Additive-only protects earlier sources, not vanilla

STNH is a 3.12-era conversion, so where it ships a file at a vanilla path its copy
is generally the 3.12 file — the 4.4 one minus whatever 4.4 added. The game loads
it and says nothing. `flags/colors.txt` cost 47 of vanilla's 72 flag colours that
way. Fourteen files are excluded in `vendor.yml`, one is kept with the dropped
definitions restored in `src/`, and `check_vanilla_regression` guards the rest.
[Decision 08](../decisions/08-stnh-art-shadows-vanilla.md).

> **The hazard is not about STNH, and that is the part to carry forward.** ASB
> Ironman — a live mod, not a total conversion — ships a 3.x
> `gfx/particles/_ships_particles.gfx` declaring 151 of vanilla 4.4's 155 ship
> particles, and Real Space – System Scale's Dyson sphere and quantum catapult
> `.asset` files drop **116** vanilla entities between them. Nobody overrides art
> in order to delete a shipset; they simply have not resynced.
>
> The check therefore scopes to *every* source, not just stale and additive-only
> ones — and since 2026-08-07 to **script** as well as art, because a current mod
> may replace a vanilla database on purpose and still strand a **third** mod
> calling the old keys
> ([decision 38](../decisions/38-real-space-drops-sol-neighbours.md)).

## STNH's art is wired to STNH's *namespace* — in four ways

"Take the art, not the script" assumes the two are separable. They are not. STNH's
art depends on the `common/` we don't vendor in four distinct ways. **All four are
closed**, and [decision 08](../decisions/08-stnh-art-shadows-vanilla.md) had found
only the first — the gap between "one" and "four" cost a live run to discover.

| Dependency | Status |
|---|---|
| **Scripted triggers** (clothing/era selectors) | Closed. All of STNH's art triggers are declared in `src/common/scripted_triggers/stg_stnh_art_triggers.txt` — 141 as it stands, **25 of them with real bodies** and the rest inert `always = no`. Era is pinned to TNG/DS9 rather than STNH's `years_passed` windows, identity keyed to species class rather than country flags STG never sets. [Decision 16](../decisions/16-phase-3-clothing-triggers.md) recorded the 140 it harvested. |
| **Species classes** | Closed. [Decision 10](../decisions/10-species-class-keys-unprefixed.md) renamed the five majors to STNH's bare keys; [decision 32](../decisions/32-declare-stub-species-classes.md) declared the remaining **34** selector keys as stubs after the 08-07 run priced them at 439 errors, 22% of `error.log`. STG declares **131** classes and `dangling_identifier_ack` is empty. Four of the 34 were misspellings of our own (DELT→DEL, ELAU→ELA, MONE→MON, PARA→PAR) — [decision 20](../decisions/20-minor-power-species-class-keys.md). |
| **Leader traits** | Closed. `leader_trait_starfleet_32` and `trait_pc_assimilated_preference` stubbed inert in `src/common/traits/`. |
| **Shader effects** | Closed. `src/gfx/FX/pdxmesh.shader` is vanilla 4.4 verbatim plus STNH's five effect blocks — an additive merge, not a 3.12 file shadowing vanilla's. |

`make validate` enforces all four: the cross-reference checks read the merged tree
and fail on any name the vendored art references that nothing defines. That is
what makes "take the art, not the script" **checkable rather than hopeful**.

> One thing this taught, worth keeping: the original 139-stub harvest read STNH's
> trigger *definitions* and therefore could not see `isBajoranReligiousLeader`,
> which STNH references from 13 files but leaves commented out in its own. **Ask
> what the art references and whether it resolves — never what the source
> defines.** [Check design, rule 3](../validation/check-design.md#3-ask-what-is-referenced-not-what-is-defined).
