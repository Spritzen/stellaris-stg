# 08 — STNH's art shadows vanilla, and its art is script

**Decided 2026-08-01, after Phase 0 shipped and launched successfully in-game.**

> **Correct but incomplete.** The art depends on STNH's `common/` in four ways —
> scripted triggers, species classes, leader traits and shader effects — and this
> decision addressed only the first. The other three were measured against a
> later run; see plan.md §3 and
> the 08-01 analysis §4.
> All four are closed now; the species-class one was blocking Phase 3 and is
> [decision 10](10-species-class-keys-unprefixed.md).

## What was wrong

plan.md §3 says: take STNH's art, never its `common/`, and skip any path an
earlier source already claims (`additive_only`). Phase 0 implemented that
faithfully. Two things it does not cover turned up on inspection of the built
tree.

### 1. `additive_only` protects earlier sources, not vanilla

STNH is a 3.12-era total conversion. Where it ships a file at a vanilla path,
its copy is generally the 3.12 file — which is the 4.4 file minus whatever 4.4
added. The game loads it in place of the real thing and says nothing.

1,031 STNH files shadow a vanilla path. 838 are `.dds` and 149 `.wav` — art
replacement, which is the point. The script files were the problem:

| File | What it dropped |
|---|---|
| `flags/colors.txt` | **47 of vanilla's 72 flag colours** (`dark_red`, `white`, `off_white`, …), while adding 2,075 STNH ones. Vanilla prescripted empires still ask for the dropped names. |
| `gfx/portraits/portraits/00_portraits_main.txt` | The arkship planet-view layers, the `origin_fallen_empire_hive` environment override, and the psionic-ascension `portrait_evolution` entry. Also repointed the main menu at STNH's `frontend_background_entity` and imposed STNH's 3.12 planet-view layout over UIOD's. **Added nothing.** |
| `gfx/portraits/portraits/07_portraits_human.txt` | The ten `human_legacy_*` portraits and the `human_legacy` portrait group — both still referenced by vanilla's `common/portrait_sets/00_portrait_sets.txt`, which we ship unchanged. |
| `gfx/portraits/asset_selectors/paragon_backgrounds.txt` | The four vanilla legendary paragon backgrounds (`azaryn`, `beholder`, `keides`, `skrand`). |

**Resolution.** The first, second and fourth are excluded from STNH in
`vendor.yml`. The third is *kept* — it is what repoints `human_male_01..05` and
`human_female_01..05` at Starfleet-uniformed textures, which is exactly the Trek
dressing we want on the Federation — and the dropped definitions are restored
verbatim from vanilla in `src/gfx/portraits/portraits/stg_human_legacy_portraits.txt`.
A new filename merges rather than shadows, so that works additively.

`paragon_backgrounds.txt` was the interesting call. STNH's version carries
per-era Starfleet leader backgrounds (ENT, Kelvin, DIS, SNW, TOS, WoK, TNG, FC,
PIC) which are genuinely wanted — but every entry is gated on STNH scripted
triggers from its `common/`, so **none of them could ever fire** while it
simultaneously deleted four working vanilla ones. Excluding costs nothing today.
Phase 3 rebuilds it properly against our own country flags.

### 2. STNH's art wiring *is* script, and it depends on STNH's `common/`

This is the deeper one. "Take the art, not the script" assumes the two are
separable. They are not. `gfx/portraits/asset_selectors/*.txt` choose a leader's
clothing by era, leader class and empire identity, and they do it with scripted
triggers defined in STNH's `common/scripted_triggers/`.

Vendoring the art without the triggers left **139 trigger names undefined across
510 vendored files** — every one an `error.log` entry on load.

It is not a crash: every selector carries a `default =` at each scope, so an
undefined trigger falls through to the default texture. Trek portraits render;
they render in each species' plain clothing rather than era-appropriate
uniforms.

**Resolution.** `src/common/scripted_triggers/stg_stnh_art_triggers.txt` defines
all 139 as `always = no`. Behaviour is identical — the fallback was already
happening — but it is now deliberate and the log is clean.

Faithful vendoring of STNH's real definitions was considered and rejected on two
grounds. It would not change the outcome: the era triggers gate on
`years_passed > 198` against STNH's own map scenarios, so they are false in a
normally generated galaxy regardless. And STNH's definitions pull in 33 leader
traits (`leader_trait_doctor_3`, `trait_fleet_admiral`, `leader_trait_talshiar`,
…) that live in STNH's `common/`, so it would move the undefined-identifier
problem rather than solve it.

**Phase 3 owns the rest.** Giving those triggers real bodies — era pinned to
TNG/DS9 per plan.md §1, role triggers mapped onto vanilla leader classes,
identity triggers keyed to our own country flags — is precisely the Phase 3 job,
and the stub file is where it happens. Switching them on piecemeal leaves
leaders in a mix of uniforms, so it should be done in one pass.

## The guard

`tools/validate.py` grew `check_vanilla_regression()`: for every file vendored
over a vanilla path, it warns about anything vanilla declares that we dropped.

> **Both halves of how it was first written turned out to be wrong, and the
> corrections are the interesting part.** It compared **depth-0 block keys**,
> which is identity in a `.txt` and is not identity in an `.asset` — where every
> declaration reads `entity = { name = "…" }` — so it was examining those files
> and structurally unable to find anything in them. And it was scoped to
> `additive_only` sources on the reasoning that *every other mod in the harvest
> is a live 4.x mod that overrides vanilla deliberately, which is what mods are
> for*. True, and beside the point: **nobody overrides art in order to delete a
> shipset; they simply have not resynced.** 116 of the 119 dropped vanilla
> entities the fixed check found were in Real Space – System Scale, a current
> 4.x mod. It now compares declared identity across every source.

Reviewed-and-fine cases go in `vanilla_regression_ack:` in `vendor.yml` with a
reason. Eight are listed: five clothes selectors where the dropped
`avian_hair_1` / `molluscoid_hair_1` is still defined by vanilla files we don't
shadow, and three `music/*.txt` where STNH comments out the vanilla soundtrack
in favour of its own Trek one — on-theme, and deliberate.

Anything **not** in that list is an unreviewed regression.

## Confirmed against a live run

Both findings were made statically, then confirmed against
`/paradox/stellaris/logs/error.log` from the 2026-08-01 Phase 0 session
(20:43:24–20:46:53, Pegasus v4.4.6). That log is **72 MB / 414,627 lines**.

**The undefined triggers.** 406,916 lines — **98.1% of the entire log** — are
`gfx/portraits/asset_selectors` trigger errors. Worst offenders:
`uses_starfleet_uniform` (36,118), `is_tng_era` (33,296), `is_hero_or_admiral`
(14,015), `is_spy_leader` (12,438).

It is a **load-time cost, not a gameplay one**, and the log proves it two ways:

- *Timing.* The whole burst is 20:44:01→20:44:06 — six seconds, entirely inside
  the init window that `time.log` reports as `Startup real time: 50,803 ms`
  (`init application: 48,406 ms`). After init completes at 20:44:13 there are
  **zero** of these errors for the remaining 2m40s of play. The only post-init
  errors are four instances of an unrelated vanilla Machine Age scope bug.
- *Counting.* Log hits track textual occurrences in the tree almost exactly —
  `uses_starfleet_uniform` appears 38,447 times in `gfx/` and logs 36,118. That
  is one hit per site at parse, not repeated evaluation per pop or per frame.

So the bill was roughly six seconds of a fifty-second startup plus a 72 MB disk
write, and nothing per-frame. Worth fixing, but it was never a framerate
problem — which is not what the raw number suggests, and is why the timing check
matters more than the volume.

**The flag colours.** `empire_flag.cpp:236` logged `invalid color` for **23
distinct colours** — `dark_orange` ×11, `dark_red` ×9, `white`, `off_white`,
`ochre_brown` and 18 more. Every one is a vanilla colour present in
`/stellaris/flags/colors.txt` and absent from STNH's. A 100% match with the
static analysis above, and real empires were failing to render their flags.

## What this costs

Nothing the mod had before — the excluded files added nothing we wanted except
the paragon backgrounds, which never worked.
