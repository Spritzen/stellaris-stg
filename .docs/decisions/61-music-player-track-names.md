# 61 — The music player draws the declaration name, and 16 had no key

**Status:** decided, 2026-08-08
**Follows** [decision 55](55-federation-anthem.md), which got the Federation
anthem *playing* and left it listed as `stg_ufp_anthem`.

## The report

*"check the music names, some of the names look like references instead of
tracks in the music player."*

## The mechanism

The music player shows the **declaration name**, looked up as a localisation
key. Vanilla writes both halves side by side:

```
music/maintheme.asset            music = { name = "cradleofthegalaxy" … }
musicplayer_l_english.yml        cradleofthegalaxy:0 "Cradle of the Galaxy"
```

A name with no key is drawn **verbatim**, and nothing is logged — *a name that
resolves to itself still resolves*. That is decision 47's silence in a different
database, and no check here had ever asked the question: `check_music_declarations`
asked whether a file has a declaration and whether a declaration has a file, in
both directions, and never what either one is called on screen.

**16 of the built tree's 22 playlist entries had no key**: `newhorizonssong1`
through `newhorizonssong10`, `maintheme7/8/9/10/12`, and our own
`stg_ufp_anthem`.

Extended Soundtrack's five are the exception that shows the rule — it writes
`name = "Battle For Supremacy"`, the title itself as the key, so drawing it
verbatim is exactly right.

## Where the titles came from

Every value is derived, in this order of preference:

1. **STNH's own `localisation/`**, which STG does not vendor (plan.md §3 takes
   its art paths and not its script) — so the titles had to be harvested the
   same way [decision 52](52-trek-star-names.md) harvested star names.
   Eight of them: `newhorizonssong1`–`8`.
2. **The `.ogg`'s embedded Vorbis TITLE tag** — the composer's own. This is what
   named `newhorizonssong9` ("New Horizons - Make A Note In The Log", Samuel
   Pierce) and gave `newhorizonstheme.ogg` its full title ("New Horizons - Where
   No One Has Gone Before: Star Trek / TNG / DS9 / VOY", Sam Dillard), neither of
   which STNH names in any of its 51 localisation files.
3. **The filename**, for `stg_ufp_anthem`.

**The keys are not ours to prefix.** A key here is the `name =` inside a vendored
`music/*.asset` that we do not own and cannot rename, so it takes STNH's
spelling and vanilla's — the same exception as
[decision 10](10-species-class-keys-unprefixed.md). Only `stg_ufp_anthem` is
ours and carries the prefix.

`maintheme` **overrides vanilla's own key**, which reads "Creation and Beyond":
correct for vanilla's file, wrong here, because STNH repoints `maintheme` at its
own theme and the label stayed vanilla's. It played the Star Trek theme under
Andreas Waldetoft's title through every run.

## The second finding: six entries, one recording

`maintheme` and STNH's added `maintheme7`, `8`, `9`, `10` and `12` **all declare
`newhorizonstheme.ogg`**. Stellaris picks uniformly across `song` entries, so
this is STNH weighting its main theme to 6 of 22 — 27% of the ambient rotation.
STNH itself commented out vanilla's `maintheme2`–`6` in the same pass, so the
technique is deliberate.

**Kept, at the user's direction (2026-08-08), with six distinct titles.** Only
the first two are derived — `maintheme` is STNH's own loc value and `maintheme7`
is the composer's tag in full; the other four are chosen, in the same register
and avoiding collisions with the eight harvested titles. The loc file says so at
the point of use, because six titles over one recording is exactly the kind of
thing a later reader would take at face value.

The alternative — one title repeated six times — is what "derived only" would
have produced, and it reads as a bug in the player.

## How this class of defect gets caught next time

`check_music_declarations` gained a third direction: **every `song` entry's name
must resolve to a loc key, unless it contains a space.**

The space rule is not a loophole — it is the question a player actually asks,
separating a name that reads as a key from one that reads as a title, and it is
what lets Extended Soundtrack's prose names through without an ack.

Calibrated by moving `stg_music_l_english.yml` aside: **exactly 16 findings, and
0 after.** Vanilla's own `music/` scores 6 of 30 — `towardsutopianovaflare`,
`syntheticgod`, `maintheme3` and three more Paradox never gave a key — but STG
ships none of those files, so vanilla's rate is a floor worth knowing rather
than a false-positive source.
