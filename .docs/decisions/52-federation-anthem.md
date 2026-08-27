# 52 — the Federation anthem plays, and a check that a track is reachable

**Resolved 2026-08-08.** The first piece of Phase 4, and the one piece of it
plan.md named with a definition of done.

## The finding, which plan.md had already written down

> Music integration — including
> `music/Anthem_of_the_United_Federation_of_Planets.ogg`, which STNH ships and no
> `music/*.txt` declares a `song` for, so it never plays.

Accurate, and one level short. `music/` has **two** halves that must meet:

```
music/stg_music.asset   music = { name = "X" file = "X.ogg" volume = 0.80 }
music/stg_music.txt     song  = { name = "X" }
```

The `.asset` maps a name to a file; the `.txt` puts that name in the playlist.
The anthem had **neither**. It is the only `.ogg` of the 17 in the built `music/`
directory that nothing declares — the other 16 all resolve, including STNH's
eleven `newhorizons*` tracks and the Extended Soundtrack's five.

Nothing logged it and nothing could have. A file no loader is asked to open is
not an error; the clutter closure counted it as one orphan among 706.

## What was written

`src/music/stg_music.asset` and `src/music/stg_music.txt`, both new files, both
`stg_`-prefixed, declaring the track as `stg_ufp_anthem` and adding it to the
rotation.

`volume = 0.80` is vanilla's own default rather than a guess: of the 21 vanilla
music declarations that set a volume, **18 set 0.80**, and the Extended
Soundtrack's five do too.

**No trigger, because the database has none.** Across vanilla's 24 `song` blocks
the only field beside `name` is `chance`, used once as `chance = { factor = 0 }`
to keep a DLC main-menu theme out of the in-game rotation. There is no example
anywhere of a `song` gated on a country, so an anthem that plays only for
Federation players is not something the files support, and inventing a scope for
it is the failure [decision 25](25-quoted-class-keyword.md) records. It plays for
everyone, Klingon and Borg included — acceptable in a Trek conversion, and the
alternative was leaving it unheard.

The main menu was already right and needed nothing: STNH shadows vanilla's
`music/maintheme.asset` to point the `maintheme` name at `newhorizonstheme.ogg`.

## `check_music_declarations`

Added, because this class is silent in both directions and the include-list
lesson of [decision 22](22-group-c-texture-references.md) applies to `music/` as
much as to textures — the tree converges on whatever question the checks ask.

**The rule is vanilla's own and it is exact: 30 `.ogg` files, 30 named by a music
declaration, and 0 declarations naming a file that is not there.** Both directions
score zero, so both are checked. A declaration may name a file vanilla ships
rather than one of ours — STNH's `songs.asset` lists 17 of vanilla's tracks that
way — so the file must resolve against the built tree **or** `/stellaris`.

Calibrated in both directions per [decision 28](28-clone-discards-sibling-locators.md):
with the fix reverted it names the anthem; against a synthetic declaration of a
track that does not exist it names that; against the repaired tree and against
vanilla it reports nothing.

**Not checked: that every music declaration has a `song` entry to play it.** Four
of STNH's spare `maintheme` aliases have none, and whether the main menu picks its
theme by song entry or by declaration name is not something the files settle —
vanilla's one piece of evidence, `chance = { factor = 0 }` on a DLC main theme,
says the two are separable without saying how. A check there would rest on a guess
about the engine and would report four findings no one could dispose of honestly.
