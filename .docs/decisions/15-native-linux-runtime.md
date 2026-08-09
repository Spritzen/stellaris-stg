# 15 — Compatibility mode off: the game is the native Linux build, and the user-data folder moved back

**Decided 2026-08-02, after the user turned off Steam's "force compatibility
tool" for Stellaris. RESOLVED — confirmed by every live run since: `dlc_load.json`
records `enabled_mods: ["mod/star_trek_galaxies.mod"]` and the logs name files
that exist nowhere but `stg-build/`.**

> **Measured addendum, same day** — see §"What the new folder actually
> contained". This decision was first written while the new folder was still
> unmounted, and three of its predictions were wrong: the native build *had*
> already run, the registry entry *did* survive, and the playsets *did* carry
> over. The corrections are inline below, marked. Predicting and then measuring
> is the point; leaving the wrong prediction standing is not.

This reverses the *location* half of
[decision 07](07-launcher-local-mod-registration.md). It does not reverse its
reasoning, which was correct for the build installed at the time and is what let
this be diagnosed in one pass.

## What changed, and how we know when

Container clock is UTC; the game writes its own logs in BST (UTC+1). Both
columns are the same events.

| UTC | BST | Evidence |
|---|---|---|
| 19:01–19:03 | 20:01–20:03 | A game session ran. `logs/system.log` opens with `gfx_dx9.cpp`, `nvd3dum.dll` and a D3D device — **the Windows build under Proton**. `time.log`: startup 46,148 ms. |
| 19:03:49 | 20:03:49 | Last write into the Proton prefix (`settings.txt`, on exit). |
| **19:04:33** | **20:04:33** | `/stellaris/launcher-settings.json` rewritten. |
| **19:04:38** | **20:04:38** | `/stellaris/stellaris` written — **ELF 64-bit LSB executable, x86-64**. |

So the ~8pm run was the **last Proton run**, finishing about 45 seconds before
Steam swapped the depot.

~~The native build has not been launched yet.~~ **Wrong — corrected once the new
folder was mounted.** The native build ran at **20:05:25–20:06:24**, a minute
after the swap: `logs/system.log` opens with `gfx_opengl.cpp` and
`pdx_audio_sdl.cpp`/pulseaudio, and `time.log` gives startup **40,033 ms**. The
error was reasoning about a directory that was not mounted — the *absence* of
evidence in the prefix was read as evidence of absence everywhere.

`/stellaris` now holds `stellaris` (ELF), `libPDXSDK.so`, `libnakama-cpp.so`,
`libsteam_api.so` and `launcher-installer-linux_2024.14`. There is no
`stellaris.exe` and no `.dll` left — the inverse of the table in decision 07.

## The new location

`launcher-settings.json` is the authority, and it now reads:

```json
"gameDataPath": "$LINUX_DATA_HOME/Paradox Interactive/Stellaris",
"exePath": "./stellaris",
```

`$LINUX_DATA_HOME` is `$XDG_DATA_HOME`, i.e. `~/.local/share`. So the live
user-data folder — `mod/`, `launcher-v2.sqlite`, `logs/error.log` — is:

```
/home/odin/.local/share/Paradox Interactive/Stellaris/
```

That is the folder decision 07 called "dead since 2025-11-09". It is dead no
longer. The Proton prefix under `compatdata/281990` is now the stale one. **Both
directories exist on disk and only one is live**; which, follows from the
installed depot, which is why nothing in the pipeline hardcodes the answer any
more.

## What the pipeline does now

- **`tools/deploy.py:game_platform()`** reads `launcher-settings.json` and
  returns `linux` or `windows` from the `gameDataPath` token
  (`$LINUX_DATA_HOME` vs `%USER_DOCUMENTS%`). Both branches stay live code: the
  Steam checkbox that caused this can be flipped back in one click.
- **`launcher_path()`** renders `path=` per platform — the plain host path for
  native Linux, decision 07's `C:` drive-letter translation for Proton.
- **`check_mount_matches_platform()`** refuses to deploy when the mounted
  user-data folder and the installed build disagree. The mount is fixed at
  container-build time and the platform is not, so the two *will* drift apart
  again; without the guard that drift silently reproduces decision 07's exact
  failure — a correct mod folder written where nothing reads it. `$MOD_PATH`
  skips the guard, because the guard's own message offers it as the override.
- **`devcontainer.json`** binds the new source to the same `/paradox/stellaris`
  target, so every other path in the repo is unchanged.

One incidental finding, noted because it will otherwise read as a bug: **the
launcher rewrites the outer `.mod` file**. The prefix's
`star_trek_galaxies.mod` carries `picture="thumbnail.png"` and no trailing
newline, neither of which `render_mod_file()` emits, and its mtime is 19:01 —
the launcher's start, not any `make link`. So a deployed `.mod` that does not
byte-match what deploy.py wrote has not necessarily been tampered with.

The symlink half of [decision 13](13-build-dir-and-symlink-deploy.md) is
unaffected and gets simpler: `mod/star_trek_galaxies` → `$HOST_WORKSPACE/stg-build`
is now an ordinary Linux symlink read by an ordinary Linux process, with no Wine
filesystem layer to resolve it.

## What this costs, and what has to happen on the host

1. ~~**The container must be rebuilt.**~~ **Done 2026-08-02.** The mount is baked
   in at build time, so until it was, `/paradox/stellaris` still pointed into the
   Proton prefix, `make link` and `make mod-file` refused by design, and
   `error.log` could not be read. `make link` has since run: the mod folder holds
   the symlink and a `.mod` carrying
   `path="/home/odin/.local/share/Paradox Interactive/Stellaris/mod/star_trek_galaxies"`.
2. ~~**Add STG to a playset and make that playset active.**~~ **Done** — this
   was the only outstanding host-side step (not re-registration; see the
   measured section below for why), and every run since has loaded the build.
3. **Startup and error counts are not comparable across the switch.** The
   baseline in the 08-08 analysis
   was measured on the D3D/Proton stack. A different renderer and a different
   filesystem layer can move both the load-window count and the 46 s startup in
   either direction. Treat the first native run as a **new baseline**, and say
   so in its analysis rather than scoring it as a regression against a number it
   cannot be compared to.

## What the new folder actually contained

Measured after the container was rebuilt against the new mount, 2026-08-02.
Three of the predictions above were wrong, all in the same direction: **the
native folder was not a blank slate, it was a live folder from before the Proton
era that had simply been dormant.**

- **The registry entry survived.** `launcher-v2.sqlite` here holds 38 mods
  including one `displayName = "Star Trek Galaxies"`, `source = local`,
  `status = ready_to_play`, `gameRegistryId = mod/star_trek_galaxies.mod`,
  `dirPath` the correct native path. It dates from the Aug-1 deploy that
  decision 07 diagnosed as going to the "dead" folder — that deploy *did*
  register, into the database that is live again today. **Registration does not
  need re-doing.**
- **The playsets carried over** — `Initial playset` (14 mods) and
  `oO Spritz Mix Oo` (33 mods), both populated. They were never in the prefix's
  database to begin with.
- **But STG is in neither playset, and neither playset is `isActive`.** That,
  not registration, is why the 20:06 run recorded `"enabled_mods":[]` in
  `dlc_load.json`. `mods` membership and `playsets_mods` membership are separate
  tables and a mod can be perfectly registered and still load nothing.
- **`requiredVersion` is the stale `4.4.*`**, from the Aug-1 descriptor, not the
  `v4.4.6` that decision 07's addendum established. The deployed `.mod` now
  carries `v4.4.6`; whether the launcher refreshes the column from it on restart
  is unverified. **If the "made for a different version" badge appears, this
  column is why.**
- **The stale 17 GB copy was really there** — `mod/star_trek_galaxies/` as a real
  directory dated Aug 1 16:11, carrying the pre-repair build. `make link`
  replaced it with the symlink, which is the point: had it been left, a live run
  would have measured the Aug-1 build while the repo showed the Aug-2 one.

### The native vanilla baseline, free

The 20:06 run loaded **no mods at all**, which makes it something the repo has
never had: a clean native-Linux vanilla measurement on this hardware.

| | native vanilla, 0 mods | Proton + STG (2026-08-07) |
|---|---|---|
| `error.log` | **2,083 B, 9 records** | 268 KB, 1,702 records |
| startup | **40,033 ms** | 48.5 s |

Two things follow. The 9 records are **not ours** — 5 are `dlc.cpp:339 Invalid
supported_version` from third-party `ugc_*.mod` files and 4 are a vanilla
`founder_species` context switch in `00_origins.txt`; expect them in every native
run and do not register them as STG's. And **STG's true startup cost is far
smaller than the raw numbers suggest** — 40 s of the Proton run's 48.5 s is the
base game, so a native run with STG should be compared against 40 s, not zero.

## Rules this confirms

Decision 07's rule 1 — *an artefact's timestamp is part of its evidence* — is
what made this cheap. The same 33 native-era `.mod` files it warned against
reasoning from are, today, evidence about the live launcher again; what changed
is not the files but which build is installed. **Check what wrote a file and
when, then check whether that thing is still the thing you are reasoning
about.** The answer has now flipped twice.

Its rule 2 stands unchanged: **the container cannot confirm the launcher sees
anything.** This decision was resolved in the pipeline and stayed unconfirmed
until the user reported a run — which is exactly the sequence the rule
prescribes, and the one to repeat next time.
