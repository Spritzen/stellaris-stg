# Decision 10 — drop Cinematic Camera, Kammarheit and Apocryphos

**Resolved 2026-08-02.** Closes three of the keep-or-drop questions plan.md §8
raised off the back of the 2026-08-01 live run. Starbase Extended 3.0 and ASB
Ironman stay — SBX was left open here and was closed hours later by
[decision 11](11-fix-source-errors-dont-drop.md), which generalised what this
decision did by instinct: **a mod is dropped on content grounds, never on its
error count.**

> **REVERSED 2026-08-07 — Cinematic Camera is back in the harvest, and the
> diagnosis below is wrong.** It did not cause `PLANET_SCALE_SYSTEM does not
> match in size with ZOOM_STEPS_SYSTEM`. That error is still in `error.log` five
> days after the mod was dropped, with the build at 8 percentages against 8
> planet scales. `ZOOM_STEPS_SYSTEM` is set by no file in vanilla or in any
> snapshotted mod; measured across both live runs, the only surviving
> explanation is that it is fixed at vanilla's 7, so Real Space – System Scale's
> own 8-entry `PLANET_SCALE_SYSTEM` has been mismatched since it entered the
> harvest. [Decision 41](41-planet-scale-system-length.md) has the refutation
> table.
>
> **What survives is the argument this section made second, and it is the one
> that always mattered:** Cinematic Camera is *nothing but* camera defines,
> `zzzzz_` sorts last, and it takes **17 keys from `systemscale_defines.txt`**.
> There is no narrower version of it — patching out the contested keys leaves
> three vanilla-owned scalars. So restoring it is a straight choice between two
> camera tunings.
>
> **That choice was made deliberately on 2026-08-07: Cinematic Camera's.** The
> 17 keys are acked in `vendor.yml` under `defines_conflict_ack` as a group,
> with a note to delete the block if the mod is ever dropped again. What this
> section got wrong was not the trade-off — it was calling a taste decision a
> correctness one, on the strength of an error that belonged to another mod.

## Cinematic Camera (703156866) — dropped, because it was breaking something

One file, 2 KB, no Trek content. Its `zzzzz_cc_defines.txt` set
`NCamera.ZOOM_STEPS_SYSTEM_PERCENTAGES` to **13 entries** while Real Space –
System Scale's `systemscale_defines.txt` sets `NGraphics.PLANET_SCALE_SYSTEM`
to **8**. The engine requires the two to be the same length and says so —
`PLANET_SCALE_SYSTEM does not match in size with ZOOM_STEPS_SYSTEM`, error D13
of the live run. `zzzzz_` sorts last, so Cinematic Camera won the zoom steps and
left System Scale's planet scaling mismatched.

In-system planet scaling is the entire reason System Scale is in the harvest, so
this was a 2 KB mod quietly disabling a 700 KB one we chose on purpose. It also
set `ENTER_SYSTEM_ZOOM_STEP = 12`, an index that only makes sense against its
own 13 steps.

### Correction, 2026-08-02 — "port the pitch and FOV lines" was wrong advice

This decision originally said the camera feel could be recovered by porting
Cinematic Camera's pitch and FOV lines into an `src/` defines file and leaving
the zoom arrays to Real Space. **Measured, that is not possible: the pitch and
FOV lines are exactly the ones Real Space – System Scale already owns.**

Of Cinematic Camera's 19 non-zoom `NCamera` keys, **16 are set by
`systemscale_defines.txt`** — `FOV`, both pitch pairs, the focused-zoom mults,
rotation sensitivity, slide radius factor, the galaxy-zoom thresholds. And
System Scale is not merely incidentally touching them; it is deliberately
providing a freer camera of its own, tuned to the systems it rescaled:

| | vanilla | System Scale | Cinematic Camera |
|---|---|---|---|
| `SYSTEM_MIN_PITCH` | 20.0 | **1** | −79.0 |
| `SYSTEM_MAX_PITCH` | 80.0 | **89** | 179.0 |
| `FOCUSED_MIN_PITCH` | −80.0 | **−89** | −79.0 |
| `FOV` | 35 | **35** | 30 |
| `SYSTEM_SLIDE_RADIUS_FACTOR` | 4.0 | **0.25** | 1.0 |

Porting Cinematic Camera's column over System Scale's would be the *same defect
this decision exists to fix*, in a quieter form: one mod's camera tuning
partially overwriting another's. D13 was only caught because two arrays had to
match in length and the engine said so. Scalars have no such check — they would
just be wrong.

Three keys are genuinely unclaimed: `SYSTEM_CAMERA_RESTRICT_EXTRA_SPACE`
(100→200), `FOCUSED_ZOOM_RATE` (0.2→0.1, a slower zoom) and `SYSTEM_SLIDE_SPEED`
(100→50). The last of those interacts with `SYSTEM_SLIDE_RADIUS_FACTOR`, which
System Scale *does* set, so taking Cinematic Camera's speed without its factor
gives neither mod's intended behaviour.

**So: nothing was ported, and the honest reason is that there was almost nothing
portable.** Most of what Cinematic Camera offered, Real Space – System Scale
already provides. The mod itself should not come back.

## Kammarheit (1409667987) and Apocryphos (1430192994) — dropped, on taste

919 MB and 78 files of dark-ambient soundtrack in a Star Trek total conversion.

Nothing was wrong with them: zero errors, zero contested paths, purely additive.
That is exactly why plan.md §8 flagged it — a conflict-free mod is never removed
by any process except a decision, so without one it stays forever by inertia.
The decision: **dark ambient is not what Star Trek sounds like.** STNH's own
Trek score and Extended Soundtrack's vanilla tracks carry the mod.

Reversing this is two lines in `vendor.yml` and a `make vendor`. Both remain in
`.source/`, so it survives unsubscribing from them on Steam.

## What was NOT dropped, and why

**Starbase Extended 3.0** and **ASB Ironman** both stay. SBX was left open here
on the grounds that its cost is real (duplicates vanilla 4.4's orbital-ring
sections, no Trek content) but is a cost, not a breakage — which
[decision 11](11-fix-source-errors-dont-drop.md) then made into the rule, and
its errors were repaired in place.

**ASB Ironman is no longer an open question, because the analysis had the mod
wrong.** The 2026-08-01 analysis described it as "a ship-appearance mod that
has taken over vanilla's combat VFX" and concluded "its Trek value is nil — STG's
ships will be STNH's". The combat VFX is not an overreach; it is the mod. ASB is
*Amazing Space Battles*, and its content breaks down as:

| | files |
|---|---|
| `gfx/particles` — weapon, muzzle, shield-hit and explosion effects | 230 |
| `gfx/models` — of which 147 are one vanilla shipset (`mammalian_01`) | 187 |
| `gfx/projectiles` | 13 |
| `sound/weapons` + `ASB_soundeffects.asset` | 3 |

Only the 147 `mammalian_01` files are ship appearance, and only those become
redundant when Trek shipsets land. **Weapon and explosion VFX are not replaced by
a shipset** — STNH ships are hulls, not muzzle flashes — so ASB's value survives
Phase 3 intact rather than disappearing at it. Dropping it would remove combat
VFX we chose on purpose and get nothing back.

What remains true is narrower and was fixed on 2026-08-02: **46 parse errors,
all ASB's**, across 21 3.x-era files. (An intermediate count of 64 was wrong —
it counted filename mentions in the log rather than pairing each message to its
file. The analysis's original "~46" was right.)

Most turned out not to be version drift at all but plain typos ASB's 3.x
Stellaris tolerated: an `animation` block spelled `nimation` in five files, a
comment banner missing its leading `#`, three `@` variables whose names are
transposed against the definitions in the same file. The rest are genuine 4.x
changes — `volume` removed from entity sound blocks, `box_emitter_yaw/_pitch/
_velocity` gone, `delay_random_offset` now a range, `max_duration` valid only on
ballistic projectiles.

All 46 are fixed by 23 `patches:` entries in `vendor.yml`, using the patch
mechanism plan.md and CLAUDE.md had always described and nobody had built. Three
of the fixes are judgement rather than reconstruction and say so in their own
`why` text.

## The general lesson, which outlived the specific mods

Cinematic Camera is a **key-level** conflict: two mods, differently-named files,
same define. plan.md §4's conflict register enumerates contested *paths* and
structurally cannot see this class. That blind spot is now closed by
`check_defines_conflicts` in `tools/validate.py`, which reads defines in the
order the game merges them and flags both length-mismatched coupled arrays and
any key set by more than one source. Verified by restoring Cinematic Camera's
file and watching it fail.
