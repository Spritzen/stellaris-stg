# 03 — Content scope: era, art, empires, map

**Decided:** 2026-08-01

## Era — TNG / DS9

All major powers established at game start. Drives prescripted empire tech
levels and means the Federation exists as an empire rather than something you
form in-game.

## STNH art — take all of it

The full ~10 GB, art paths only: `gfx/portraits`, `gfx/models/ships`,
`gfx/models/portraits`, `gfx/particles`, `gfx/event_pictures`,
`gfx/loadingscreens`, `flags/`, `music/`, `sound/`, plus eleven loose files at
the top of `gfx/models/`. **`vendor.yml` is the authority on this list; it has
been corrected twice.**

*(It originally read `gfx/models/rooms`, which exists in neither STNH nor
vanilla — room entities live under `gfx/models/portraits/`, which is also where
STNH's 794 MB of Trek portrait textures are. `gfx/particles` and the loose
`gfx/models/*` files were added 2026-08-02 because the art we already took
referenced them — an include list scoped by directory does not respect
reference edges. plan.md §3 has that story.)*

**Never** STNH's `common/`, `events/`, `interface/` or `map/` — that is the
total-conversion script we are deliberately not shipping. Taking it would undo
the entire point of the mod.

*(The ship-model prune this section held in reserve as the load-time lever has
since happened, forced by a directory-name collision rather than chosen —
[decision 17](17-walshicus-shipsets-replace-stnh-hulls.md). "Take all of it" no
longer describes `gfx/models/ships`; `vendor.yml` is the list.)*

## Borg and Dominion — playable empires

Ordinary prescripted empires, not scripted crises. No crisis machinery needed.
*(The Borg were built from vanilla's Driven Assimilator —
`auth_machine_intelligence` + `civic_machine_assimilator`. Not hive mind, as
this originally said: the assimilator civic only exists on the machine side.)*

## Map — Trek names only

Trek-named systems in a normally generated galaxy. No hand-placed Sol, Qo'noS or
Cardassia. Real Space and YAGEM keep ownership of galaxy generation. Revisit in
Phase 4 if it feels thin.
