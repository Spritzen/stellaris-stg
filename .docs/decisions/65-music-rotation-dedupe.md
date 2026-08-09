# 65 — The rotation is 27 tracks, not 86, and six of them were one recording

**Status:** decided, 2026-08-08
**Reverses the "kept at the user's direction" half of**
[decision 61](61-music-player-track-names.md), at the same user's direction.

## The report

*"Music player; seems to be 86 (roughly counted) tracks, this seems a lot, let's
actually remove duplicate tracks to see where we are really at, I suspect there
is an issue here."*

The suspicion was right. The number was not, and establishing what the number
actually is was most of the work.

## The measurement

`music/` is read as a directory of files, so a mod file at a vanilla path
**replaces** it. Counting without that gives 94 `song` blocks; counting with it
gives 32. Two further traps sit in the way of a correct count:

- **Comments.** STNH's `songs.txt` and `songs_submod.txt` are mostly
  `# song = { … }`. A regex that does not strip comments reads 18 phantom
  entries and reports `newhorizonstheme` as a dangling playlist entry it is not.
- **`chance = { factor = 0 }`.** Vanilla's own way of keeping a main-menu theme
  out of the in-game rotation.

| | |
|---|---|
| playlist entries, before | **32** |
| distinct recordings behind them | **27** |
| `.ogg` files reachable at all | 47 (17 in the mod, 30 vanilla's) |

**Nothing on disk produces 86.** 55 is the merged declaration count and 47 the
audio-file count; the rough count was simply high, and the real number was low
enough to be the more interesting finding.

## The duplication

**Twelve declaration names point at `newhorizonstheme.ogg`** — `maintheme` and
STNH's added `maintheme1`–`maintheme10`, `maintheme12`. Six of the twelve carry
a playlist entry, so STNH's theme held **6 of the rotation's 32 slots, 19%**,
since Stellaris picks uniformly across `song` entries. Decision 61 found the six
and gave them six distinct titles rather than one repeated six times, keeping
them at the user's direction. That direction is now reversed.

## Decision

Five comment-only `src/music/*.txt` shadow the five alias playlist files, the
decision 14 pattern. `maintheme` is the one kept — vanilla's own name, and the
main menu's.

**The `music = { }` declarations are deliberately NOT removed.** A declaration
is what keeps the `.ogg` reachable; only the `song = { }` puts it in the
rotation, and those are the two halves decision 55 exists to keep apart. The
five loc keys stay too: a key nothing looks up costs nothing, where a missing
one would draw a raw alias if a future pass re-lists an entry.

| | before | after |
|---|---|---|
| playlist entries | 32 | **27** |
| distinct recordings | 27 | **27** |
| duplicated recordings | 1 (×6) | **0** |

## Left open — vanilla's 17 tracks

**STNH's `songs.txt` shadows vanilla's and comments out all 17 vanilla tracks**,
which is why the rotation is 27 rather than 44. That is a total conversion doing
what a total conversion does, and STG is not one — but restoring them is a taste
call about how much non-Trek music belongs in a Trek mod, in the direction
opposite to the one this report asked for. Deliberately not taken here.

`check_vanilla_regression` was blind to it for a reason worth recording: the
**declarations** all survive in STNH's `songs.asset`, so the file's identity is
intact and only the playlist entries are gone. `music/` has three halves
(decision 55 found the second, 61 the third), and *which of the declared tracks
are in the rotation* is a fourth question none of the three asks.

## The rule worth carrying

**A count the user reports is a symptom, not a measurement.** "86" was wrong by
3×, and chasing it down was what surfaced the shadowing, the comment-stripping
and the 12-to-1 fan-out — none of which the reported number named. Reproduce the
count before acting on it, and say what the real one is.
