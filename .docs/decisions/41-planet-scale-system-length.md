# 41 — `PLANET_SCALE_SYSTEM` is measured against an array no script can set

**Status:** **closed 2026-08-07** by the visual test, on the third live run of
that day. `PLANET_SCALE_SYSTEM` keeps its 8 entries and the line is acked. The
occurrence-count test, run earlier the same day, **did not settle it** — see
*The occurrence test, and why it was the wrong discriminator*; the visual test
that did is in *The visual test, and what it ruled out* at the bottom.

## The report

The 2026-08-07 live run's `error.log` ends with one line, and it is the **only**
error outside the startup window:

```
[16:51:12][planet.cpp:2058]: NDefines::NGraphics::PLANET_SCALE_SYSTEM
                             does not match in size with NDefines::NCamera::ZOOM_STEPS_SYSTEM
```

## This was supposedly fixed five days ago

[Decision 10](10-drop-cinematic-camera-and-ambient-soundtracks.md) dropped
Cinematic Camera on 2026-08-02 for causing **this exact message** (error D13 of
the 2026-08-01 run). The reasoning: Cinematic Camera set
`ZOOM_STEPS_SYSTEM_PERCENTAGES` to 13 entries, Real Space – System Scale sets
`PLANET_SCALE_SYSTEM` to 8, `zzzzz_` sorts last so Cinematic Camera won, and the
two must match.

Cinematic Camera is gone. **The error is still here.**

## What the build actually merges

`common/defines/` is LIOS, and exactly one file in the build sets either array:

| key | winner | entries |
|---|---|---|
| `NCamera.ZOOM_STEPS_SYSTEM_PERCENTAGES` | `systemscale_defines.txt` | **8** |
| `NGraphics.PLANET_SCALE_SYSTEM` | `systemscale_defines.txt` | **8** |
| `NCamera.ZOOM_STEPS_GALAXY` | `systemscale_defines.txt` | 6 |
| *vanilla, read alone* | `00_defines.txt` | 7 / 7 / 7 |

8 against 8. The pair the repo believed was coupled **already agrees**, and the
engine complains anyway.

## `ZOOM_STEPS_SYSTEM` is not a define anyone can set

It appears **nowhere in vanilla** — only `ZOOM_STEPS_SYSTEM_PERCENTAGES` does —
and nowhere in any of the 51 snapshotted workshop mods either (grepped: zero
hits for a bare `ZOOM_STEPS_SYSTEM =`). It is engine-side. So its length is not
something the tree sets, and the only question is what the engine derives it
from.

Three candidates, tested against every run on record:

| run | `ZOOM%` | `PLANET_SCALE` | `ZOOM_GALAXY` | engine complained |
|---|---|---|---|---|
| vanilla alone | 7 | 7 | 7 | no |
| 2026-08-01 (Cinematic Camera present) | **13** | 8 | **8** | **yes** |
| 2026-08-07 (Cinematic Camera dropped) | **8** | 8 | **6** | **yes** |

- **`len == len(ZOOM_STEPS_SYSTEM_PERCENTAGES)`** — what decision 10 and
  `COUPLED_DEFINE_ARRAYS` assume. Predicts 2026-08-01 fails (8 ≠ 13) ✓, and
  predicts **2026-08-07 clean** (8 = 8) ✗. **Refuted.**
- **`len == len(ZOOM_STEPS_GALAXY)`** — predicts **2026-08-01 clean** (8 = 8) ✗.
  **Refuted.**
- **`len == vanilla's 7`, fixed** — predicts vanilla clean, 2026-08-01 fails,
  2026-08-07 fails. **The only survivor.**

So `PLANET_SCALE_SYSTEM` must have **7 entries, whatever the percentages say**,
and Real Space – System Scale's 8 have been mismatched since the day it entered
the harvest. **Cinematic Camera never caused this error.** Its 13 entries were a
real defect of a different kind — and `ENTER_SYSTEM_ZOOM_STEP = 12` indexes a
step that has never existed — but the message decision 10 pinned on it was
always System Scale's own.

The same reasoning flags a second thing in that file, not yet acted on: System
Scale sets `ENTER_SYSTEM_ZOOM_STEP = 7`, which with 7 steps (indices 0–6) is
also out of range.

## What is still unknown

**Whether this costs anything.** Two readings survive the evidence:

- The engine cannot map zoom step → planet scale, and falls back to a default.
  In-system planet scaling is *the entire reason System Scale is in the harvest*
  (decision 10), so under this reading we have been shipping the mod with its
  main feature inert.
- The engine rebuilds the array and the line is a one-shot complaint with no
  consequence.

What the logs settle: `game.log` records `2113 defines loaded` at 16:47:53, the
error at 16:51:12, and play continuing to 16:54:36 — **3½ further minutes,
without a repeat.** Defines were long since merged when it fired, which argues
against a startup-ordering artifact and for the array genuinely not being 8. But
one occurrence is also just what a log-once guard looks like.

**The discriminating test is cheap and needs the game:** enter several different
systems in one session and count occurrences of `planet.cpp:2058`. Repeats mean
the check keeps failing and the scaling is really falling back; exactly one
means a log-once guard, and the visual question (do planets change size across
zoom steps at all?) settles the rest.

## The occurrence test, and why it was the wrong discriminator

Run 2026-08-07 (second run of the day; `error.log` 187 KB / 1,269 lines, startup
49.0 s, galaxy generated 17:52:50, play to 17:57:11). The user confirms they
**viewed several different systems**. `planet.cpp:2058` fired **exactly once**,
at 17:53:03 — thirteen seconds after galaxy generation, and never again.

By the test as written above, exactly one means "log-once guard" and the
worrying reading was supposed to recede. **It does not, and the test was
mis-framed.** The emitter is in `planet.cpp`. Either it sits on a per-planet
path — in which case several systems' worth of planets producing one line means
it is guarded to log once, which is precisely what a permanently-failing check
looks like — or it sits in a one-time setup routine that merely lives in that
file, in which case one line was guaranteed before the game was ever launched
and the count carries no information at all. Which of the two cannot be
established from the container either. The two readings the test was meant to
separate both predict one line:

| reading | predicts |
|---|---|
| engine rebuilds the array; line is cosmetic | 1 |
| check fails on every planet, logs once, scaling falls back | 1 |

The count therefore rules out only a third possibility nobody held — that the
check re-fires per system entry. **It cannot distinguish the two that matter,
and if anything it leans toward the fallback reading**, because "cosmetic" needs
the engine to both complain and then quietly succeed, while "log-once guard" is
the ordinary shape of engine logging on a hot path.

The lesson is decision 31's, in a new place: *a measurement that both hypotheses
predict is not evidence.* Work out what each reading forbids before spending a
live run on it. This one was spent on a number that was never going to separate
them.

**What is still open is the visual question, and it is the only one left:** in
system view, do planets visibly change size as you zoom through the steps, and
are they at System Scale's intended sizes rather than vanilla's? If yes, the
line is cosmetic and gets acked. If planets are all one size or vanilla-sized,
the scaling is inert, System Scale's main feature is not working, and
`PLANET_SCALE_SYSTEM` must be re-cut to 7 entries.

## The visual test, and what it ruled out

Run 2026-08-07, **third** of the day and distinct from the two above
(`error.log` 187,392 bytes / 1,268 lines, startup 49.2 s, galaxy generated
21:23:45, play to 21:28:00). `planet.cpp:2058` fired **once**, at 21:24:03 —
the only error of the run outside the 21:22:36–21:23:25 startup window, 1,267
of 1,268 lines falling inside it.

The user reports **planets visibly rescaling across the zoom steps and looking
right**, and the camera feeling right. That is the discriminator the occurrence
count could not be, because — unlike the count — the two readings predict
*different pictures*:

| ramp actually in force | entries 2–6 | what the user would see |
|---|---|---|
| System Scale's 8 | 1.4757 1.1130 1.0479 1.5006 1.119 | planets sized to the enlarged systems |
| vanilla's 7, fallen back to | 0.325 0.35 0.5 0.5 0.5 | **3–4.5× smaller**, specks in a System-Scale system |

System Scale enlarges the systems themselves, so vanilla's sub-1.0 ramp inside
one does not read as "looked good" — it reads as planets that have gone. **The
costly reading is refuted: the feature is working.**

**What is still not established is which of the two harmless readings is true**
— the engine using all 8, or truncating to 7 — and it no longer matters, which
is why this closes rather than staying open. The 7 a truncation would keep are
System Scale's *own* first seven; the entry it would drop is `0.773`, against a
neighbour of `0.7815`. **1.1% apart, at one end of the zoom range.** Every
surviving reading produces the same picture, so there is nothing left for a
further live run to separate.

Two further things this run settled, both of them watch items left above:

- **`ENTER_SYSTEM_ZOOM_STEP = 12` is fine in game.** Cinematic Camera's value
  assumes its own 13 zoom steps, and the section above flagged that entering a
  system might dump the camera somewhere strange if the camera really only has
  the 7 that `ZOOM_STEPS_SYSTEM` has. It does not. So the camera does offer
  the steps `ZOOM_STEPS_SYSTEM_PERCENTAGES` declares, and `ZOOM_STEPS_SYSTEM`
  is measuring something else — which is additional support for the line being
  cosmetic, arrived at from the opposite side.
- **13 percentages against 8 planet scales renders correctly**, which is the
  first direct evidence that `COUPLED_DEFINE_ARRAYS` is not an engine
  requirement. Until now the pair had only ever been observed unequal in runs
  that were also throwing this error, so the two claims could not be told
  apart. The rule stays as a coherence warning — vanilla does hold them equal
  — but this instance is acked rather than left firing.

## Consequence: Cinematic Camera came back

Same day. With the D13 attribution withdrawn, the correctness case for dropping
it was gone, and [decision 10](10-drop-cinematic-camera-and-ambient-soundtracks.md)
is reversed. Restoring it neither causes nor fixes the `PLANET_SCALE_SYSTEM`
error — `PLANET_SCALE_SYSTEM` stays System Scale's 8 either way, and
`ZOOM_STEPS_SYSTEM` stays 7.

What restoring it *does* do is the argument decision 10 made second and buried:
the mod is nothing but camera defines, `zzzzz_` sorts last, so it takes **17
keys from `systemscale_defines.txt`** — `FOV`, both pitch pairs, the zoom
arrays, `SYSTEM_SLIDE_RADIUS_FACTOR`. There is no coexisting version; patching
out the contested keys leaves three vanilla-owned scalars and nothing else. So
it is a straight choice between two camera tunings, System Scale's tuned to the
systems it rescaled and Cinematic Camera's to vanilla-scale ones — **a taste
call, made deliberately, not a correctness one.** The 17 keys are acked as a
group in `vendor.yml`, with a note to delete the block if the mod goes again.

One value is worth watching in game: `ENTER_SYSTEM_ZOOM_STEP = 12`, which
assumes Cinematic Camera's own 13 zoom steps. **Whether the camera actually
offers 13 usable system zoom steps or the 7 that `ZOOM_STEPS_SYSTEM` has is not
established** — this decision could settle the length of the array
`PLANET_SCALE_SYSTEM` is measured against, and nothing more. If entering a
system dumps the camera at a strange zoom, that is the line to suspect.

### The heuristic that was left behind

`COUPLED_DEFINE_ARRAYS` (percentages ↔ planet scale) **claimed to be an engine
requirement and its only evidence was D13.** With D13 reattributed, nothing
supports the claim: Cinematic Camera shipped 13 against 8 and the engine's only
complaint was the `ZOOM_STEPS_SYSTEM` one, present with and without it. The rule
is kept — vanilla does hold the two equal, so a mismatch is worth seeing — but
demoted to a warning that says which of the two it is. Leaving it as an error
would have failed the build on a rule this investigation had just disproved.

## Not fixed, and now deliberately never

The repair would have been to re-cut `PLANET_SCALE_SYSTEM` to 7 entries, which
means choosing which of System Scale's 8 zoom steps to drop and re-deriving its
scale ramp. That is re-tuning someone else's camera design, and decision 10's
own correction is the argument against doing it casually: *"scalars have no
length coupling, so nothing would log an error — it would just be wrong."*

The visual test removed the reason to take that risk. The array keeps its 8
entries and `NGraphics.PLANET_SCALE_SYSTEM` is acked in `vendor.yml` under
`defines_conflict_ack`. **The ack rests on a reviewed correctness argument — the
picture is right under every reading that survives — not on a cost estimate**,
which is the kind CLAUDE.md warns rots. The standing cost is one log line per
run, outside the startup window, non-recurring.

**If System Scale is ever dropped or its ramp changes, delete the ack with it.**
The argument above is about *these* eight values; it does not transfer to
whatever sets the key next.

## The check

`check_defines_conflicts` gains `ENGINE_FIXED_LENGTH_ARRAYS`: for an array
coupled to something no script can set, **the required length is read off
vanilla** rather than written into the table, so a game patch that re-tunes the
camera moves it with them. Reported as a `warn`, not an `error`, because the
consequence is genuinely unsettled from the container — the same severity and
the same "check in game, then ack or fix" framing the `common/random_names`
warnings already use.

The pairwise `COUPLED_DEFINE_ARRAYS` rule stays. It is necessary and it was not
wrong; it was **not sufficient**, and it reported clean for five days while the
engine reported the same error every run.

**This is the decision-30 trap, repeated exactly.** That check, too, was
calibrated against a live log, had a number to show for itself, and fell to zero
once the thing it measured was repaired — while the engine went on reporting the
same defect. Decision 10 even records the calibration: *"Verified by restoring
Cinematic Camera's file and watching it fail."* That is the **near** side of the
repair. Nobody re-read `error.log` on the far side, where the answer was one
grep away.
