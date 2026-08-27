# 06 — The deploy target is inside the Proton prefix; the launcher does not scan `mod/`

**Decided 2026-08-01, after `make deploy` produced a correct 17 GB deployment
that the Paradox launcher would not list. RESOLVED — confirmed by a live run the
same day.**

> **SUPERSEDED ON LOCATION, 2026-08-02 — [decision 14](14-native-linux-runtime.md).**
> Steam's compatibility mode was turned off, the native Linux depot replaced the
> Windows one, and the live user-data folder moved back to
> `~/.local/share/Paradox Interactive/Stellaris`. Everything below that says
> that folder is *dead* was true of the Windows build and is now false. The
> `C:` path derivation is still live code for the Proton case and still correct;
> it is simply no longer the case in use.
>
> `make deploy` no longer exists: the copy became a symlink and the target
> became `make link` — [decision 12](12-build-dir-and-symlink-deploy.md).
>
> **What is worth reading here regardless of platform:** the *secondary cause*
> below (the launcher registers mods from a registry, never by scanning `mod/`)
> and the two rules at the end. Neither depends on which build is installed.

## Symptom

`make deploy` wrote a complete mod folder and a well-formed `.mod` file. The
launcher showed no *Star Trek Galaxies* to add to a playset, and restarting it
did not help.

## Cause: we were deploying into a directory nothing reads

Stellaris on this machine is the **Windows build running under Proton**:

| Evidence | Value |
|---|---|
| `/stellaris/stellaris.exe` | `PE32+ executable (GUI) x86-64, for MS Windows` |
| native Linux binary | absent |
| Windows DLLs in the game dir | 4 (`steam_api64.dll`, `PDXSDK.dll`, …) |
| `launcher-settings.json` → `gameDataPath` | `%USER_DOCUMENTS%/Paradox Interactive/Stellaris` |

So the launcher's user-data folder is inside the Proton prefix, and
`%USER_DOCUMENTS%` is a real directory in there rather than a symlink out to the
host's `~/Documents`:

```
/home/odin/.local/share/Steam/steamapps/compatdata/281990/pfx/drive_c/
    users/steamuser/Documents/Paradox Interactive/Stellaris/
```

`~/.local/share/Paradox Interactive/Stellaris/` is a **leftover from when the
native Linux build was in use**. Last written 2025-11-09, zero writes in 2026
despite the launcher being used. Everything deployed there went nowhere.

The host runs CachyOS, where Steam additionally runs games inside its own
container (Steam Linux Runtime / pressure-vessel; CachyOS ships
`proton-cachyos-slr`, built on it). That affects what the game sees at runtime,
but the prefix on disk is still `compatdata/281990`.

## Resolution — what it looks like now

- `devcontainer.json` mounts that folder at `/paradox/stellaris`, read-write.
  There is no `/paradox/mod` bind any more: the mod folder is
  `/paradox/stellaris/mod`, reached through the parent mount, so there is one
  bind whose source is known to exist rather than two. This also made
  `logs/error.log` readable from the container for the first time.
- `PARADOX_MOD_DIR` defaults to `/paradox/stellaris/mod`.
- `deploy.py:host_mod_dir()` matches the **longest mount target that is a prefix**
  of the wanted path and appends the remainder, so paths *inside* a mount resolve,
  not just mount roots.
- `deploy.py:windows_path()` then swaps the prefix's `pfx/drive_c` stem for `C:`,
  because the launcher is Windows-side. `$MOD_PATH` overrides the result outright.

**The `path=` question is settled empirically.** The deployed descriptor carries

```
path="C:/users/steamuser/Documents/Paradox Interactive/Stellaris/mod/star_trek_galaxies"
```

and the launcher lists STG as `ready_to_play`, the sole enabled mod of the sole
active playset, and the game loads it. The wikis disagree on absolute vs relative
for local mods ([Mods](https://stellaris.paradoxwikis.com/Mods) says relative,
[Modding tutorial](https://stellaris.paradoxwikis.com/Modding_tutorial) says full
path); this install answers absolute-Windows. Match what works rather than
re-arguing it.

The old native-Linux folder may still hold a stale 17 GB deployment. Nothing
reads it; it is safe to delete on the host to reclaim the space:

```bash
rm -rf ~/.local/share/"Paradox Interactive"/Stellaris/mod/star_trek_galaxies \
       ~/.local/share/"Paradox Interactive"/Stellaris/mod/star_trek_galaxies.mod
```

## Secondary cause — still true, still relevant

**The launcher builds its mod list from a registry, not by scanning `mod/`.** The
registry is `mods_registry.json` plus `launcher-v2.sqlite`, and only Steam
Workshop subscriptions populate it. A `.mod` file placed in the folder by hand
registers nothing, however correct that file is. STG is registered now, but a
rename or a fresh install re-opens this.

Two things this ruled out, verified rather than assumed:

- **Our file structure is correct.** The launcher's own *Mod Tools → Create a Mod*
  generates exactly what we produce: an outer `<name>.mod` holding the path, plus
  an inner `descriptor.mod` with metadata only.
- **`supported_version` format is not the problem.** Working mods on this disk use
  `v4.1.*`, `3.*` and `2.1.*` interchangeably, so our `4.4.*` is fine.

Registration is unautomated and should stay that way until it has been done once
by hand and understood. Writing to `launcher-v2.sqlite` blind risks the user's
playsets — back it up first.

## Two rules this cost a session to learn

1. **An artefact's timestamp is part of its evidence.** This was got wrong twice
   in one session by reasoning from the 33 Workshop `.mod` files in the dead
   folder, which all carry absolute *native Linux* paths — and all date from
   2025-11-09, the native era. They say nothing about the Proton launcher in use
   now. CLAUDE.md's original "runs under Proton" claim was right all along and
   was overturned on worse evidence than it was written on. Check whether a file
   *could* have been written by the thing you are reasoning about before you
   reason from it.
2. **Never claim a deployment is visible to the launcher.** Files copying
   successfully says nothing about whether the launcher will list the mod — they
   are separate systems, and this repo has been bitten by treating them as one.
   Deployment is verified only when the user reports the mod appears.

## Addendum, 2026-08-02 — `supported_version` needs the `v`

Registration is not the last thing the launcher can get wrong about a local mod.
STG was listed and `ready_to_play` and still badged **"made for a different
version of the game"**, with `supported_version="4.4.6"` against an installed
Pegasus **v4.4.6**. The numbers were right; the string was not.

**The launcher stores `supported_version` verbatim and does not normalise it.**
`launcher-v2.sqlite`'s `mods.requiredVersion` held the literal `4.4.6` for STG.
Read across all 26 registered mods, the distribution settles it:

| Count | `requiredVersion` |
|---:|---|
| 14 | `v4.4.*` |
| 4 | `v4.4.6` |
| 3 | `v4.*.*` |
| 1 each | `v4.2.4`, `v4.2.*`, `v4.1.*`(×2), `v4.**.*` |
| 3 | `2.1.*`, `2.0.2`, `3.*` — all genuinely stale, so they cannot discriminate |
| **1** | **`4.4.6` — STG, the only 4.4 mod without the prefix** |

Four mods carry `v4.4.6` — Real Space 4.0, both ambient soundtracks, Diverse
Rooms — the identical numeric version on the identical install, differing from
STG's value in nothing but the leading `v`. That is as close to a controlled
comparison as this container gets.

**Fixed as `v4.4.6`, not `v4.4.*`,** even though `v4.4.*` is the modal value.
The wildcard would silently disarm `tools/validate.py`'s descriptor-drift check,
which exists because a patch-level game update is precisely what invalidates a
vendored copy of a vanilla file ([decision 07](07-stnh-art-shadows-vanilla.md)).
`*` matches every future patch, so the check could never fire again — the
"reports a number and cannot fail" failure CLAUDE.md warns about, reintroduced
to save one edit per hotfix. An exact patch version keeps the check sharp; the
cost is bumping `src/descriptor.mod` when Stellaris moves, which is the moment
you want to be re-reading the vendored shadows anyway.

`validate.py` now warns on a missing `v` and strips it from both sides before
the numeric comparison, so the declared `v4.4.6` does not itself read as drift.
The check was verified to fire on the old value and stay silent on the new one —
a version check that has never failed is not a version check.

**Rule 2 above applies unchanged.** The badge is the launcher's, the launcher is
on the host, and it re-reads `mod/star_trek_galaxies.mod` only when it starts.
This is not confirmed fixed until the launcher has been restarted and the user
says the badge is gone.
