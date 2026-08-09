# Deployment — a symlink at `/paradox/stellaris/mod`

> **What** — how the built tree reaches the game, how the `.mod` path is derived,
> and the three separate systems that must all agree before the mod loads.
> **Open when** — `make link` fails, the launcher can't see the mod, or a run
> looks suspiciously clean.
> **Then** — [Live runs](live-runs.md) · [decision 15](../decisions/15-native-linux-runtime.md) · [decision 07](../decisions/07-launcher-local-mod-registration.md)

**Confirmed working on the native Linux build.** Every run since the platform
switch records `enabled_mods: ["mod/star_trek_galaxies.mod"]` in `dlc_load.json`
and reads files that exist nowhere but `stg-build/`, so the registry entry, the
playset and the symlink all survived
([decision 15](../decisions/15-native-linux-runtime.md)). The link is an ordinary
Linux symlink read by an ordinary Linux process, with no Wine layer in between.

## The `path=` is derived, never assumed

The `path=` in the outer `.mod` file has to make sense to the **launcher**, which
runs on the host — so its form depends on which build is installed.
`tools/deploy.py` derives it automatically:

1. reads `gameDataPath` from `launcher-settings.json` to get the platform;
2. translates the container path back through the bind mount in
   `.devcontainer/devcontainer.json` (`$HOST_PARADOX_MOD_DIR` overrides);
3. emits the plain host path for native Linux, or swaps the prefix's
   `pfx/drive_c` stem for `C:` under Proton.

`$MOD_PATH` overrides the result outright.

> **If `make link` or `make mod-file` errors that the mount and the installed
> build disagree, that is the guard working, not a bug** — the container's mount
> is fixed at build time and the game's platform is not. Fix the mount in
> `devcontainer.json` and rebuild the container; don't reach for `$MOD_PATH` to
> silence it, because the mod folder itself would still be the wrong one.

Use `make mod-file` to rewrite just the descriptor without touching the link.

## Three systems, and all three must agree

`make link` succeeding proves the **first** of these and nothing else. Do not
report one as evidence of another.

### 1. The files are in place

The symlink at `/paradox/stellaris/mod/<id>` and the outer `.mod` beside it.
This is all `make link` does.

### 2. The launcher's registry knows the mod exists

The launcher lists mods from its registry, which only Steam Workshop
subscriptions populate — it does **not** scan `mod/` for `.mod` files. Copying or
linking files registers nothing.

On this install the registry is `launcher-v2.sqlite` and **there is no
`mods_registry.json`** — that is the older launcher's file, worth knowing only so
you don't go looking for it.

**STG is registered** in the live (native-Linux) `launcher-v2.sqlite` —
`source=local`, `status=ready_to_play` — and survived the 2026-08-02 platform
switch, because that entry was written by the Aug-1 deploy into what was then the
dormant folder. Full diagnosis in
[decision 07](../decisions/07-launcher-local-mod-registration.md).

### 3. A playset contains it, and that playset is active

`mods` membership and `playsets_mods` membership are **different tables**. A mod
can be `ready_to_play` and still contribute nothing because it is in no playset,
or because no playset is `isActive`. Both were true on 2026-08-02 and the run
recorded `"enabled_mods":[]`.

> **When a run looks suspiciously clean, read `dlc_load.json` before concluding
> anything about the build — an empty `enabled_mods` means you measured vanilla.**

Back up `launcher-v2.sqlite` before writing to it; the playsets live in there.
