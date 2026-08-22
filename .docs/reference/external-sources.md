# External sources

> **What** — curated external links, annotated with what each is good for and
> where each is wrong.
> **Open when** — before searching the web. Check here first.
> **Then** — [Reference index](README.md) · [Writing script](../guides/writing-script.md)

Links worth returning to, with what each is actually good for. Stellaris modding
is undocumented enough that finding the right page again is half the work.

**Caveat that applies to everything below.** Community pages are written against
whatever version the author had. We target 4.4.x. Treat every page as a lead to
verify against `/stellaris`, never as fact — this is the same rule [writing-script.md](../guides/writing-script.md)
applies to script, and it applies just as hard to launcher behaviour, which
changes between launcher releases without announcement.

---

## Official wikis

| Source | Good for |
|---|---|
| [Mods](https://stellaris.paradoxwikis.com/Mods) | Manual mod installation, the `mod/` folder layout, `.mod` vs `descriptor.mod`. Documents the **relative** `path="mod/<foldername>/"` form for manual installs. |
| [Modding tutorial](https://stellaris.paradoxwikis.com/Modding_tutorial) | The launcher's *Mod Tools → Create a Mod* flow and exactly what it generates: an outer `<name>.mod` carrying the path, plus an inner `descriptor.mod` with metadata only. Says the outer one holds "the full file path specification" — i.e. **absolute**, contradicting the Mods page above. This install answers **absolute** — Windows-side under Proton (decision 07), and **plain native-Linux since 2026-08-02** (decision 15), which is what `tools/deploy.py` emits today. Both forms are confirmed by live runs; see "This install, verified from disk" below. |
| [Modding](https://stellaris.fandom.com/wiki/Modding) (Fandom) | Mirror of much of the same material. Occasionally more current, occasionally more wrong. Cross-check. **Returns HTTP 402 to `WebFetch`** — use the paradoxwikis copy or search snippets. |

### The per-directory overwrite table — [Modding § common](https://stellaris.paradoxwikis.com/Modding)

The one page worth returning to for merge semantics. It carries a row per
`common/` subdirectory with an **Overwrite** column — `FIOS` (first in, only
served), `LIOS` (last in, only served), `DUPL` (duplicates), `NO` (cannot
individually overwrite), `❓` (*"information not documented or extensively
tested"*) — plus the error-log message each conflict produces. Rows read
2026-08-07:

| directory | overwrite | log message |
|---|---|---|
| `random_names` | **❓** | — |
| `name_lists` | `DUPL` | ❓ |
| `starbase_modules` | `LIOS` | `Object key already exists` |
| `starbase_types` | `LIOS` | `Object key already exists` |
| `defines` | `LIOS` | — |
| `section_templates` | `NO DUPL/FIOS` | `duplicate section template found…` |

Also states the rule the whole build rests on: *"The order in which files is
processed is based on ASCIIbetical order of the filenames"* — reverse-ASCIIbetical
before patch 2.5.

**Two limits, both of which bit on 2026-08-07.** The table covers `common/`
only — **the `gfx/` tables have no overwrite column at all**, so duplicate
`.asset` entity precedence is undocumented anywhere online. And `❓` is common
on exactly the rows you want: `random_names` is one, and it had to be settled
from the source mods' own file layouts instead (decision 44).

## Launcher and local-mod registration

The launcher builds its mod list from a registry, **not** by scanning `mod/`.
This is the single most useful fact on this page and it cost a session to find.

| Source | Good for |
|---|---|
| [Local mods not appearing in launcher](https://forum.paradoxplaza.com/forum/threads/stellaris-local-mods-not-appearing-in-launcher-v2-8-1.1451562/) | The canonical thread for our exact symptom. Note: Cloudflare-gated, so `WebFetch` returns a browser-validation stub — read it via search snippets or a real browser. |
| [Local (non-workshop) mods help](https://forum.paradoxplaza.com/forum/threads/local-non-workshop-mods-help.1268378/) | Registering a local mod, and the warning that a mod present **both** locally and as a Workshop subscription will refuse to load. |
| [mods_registry troubleshooting](https://steamcommunity.com/app/281990/discussions/0/1693843461183501594/) | That `mods_registry.json` is updated by Workshop mods only, never by mods dropped in the folder. Includes the hand-written registry-entry format (`gameRegistryId`, `source: "local"`, `dirPath`, `status: "ready_to_play"`). |
| [launcher-v2.sqlite / 30% CTD](https://steamcommunity.com/app/281990/discussions/0/3200369647698480651/) | Repairing the launcher database — the `dirPath` and `status` columns, and the delete-and-rebuild procedure. |
| [Paradox mod registry fixer (gist)](https://gist.github.com/Perhelion/90733950e78a68c0fe89282edb0eaeff) | A script for "invalid mod" registry corruption. Prior art if we ever automate registration. Old (2.5-era) — read for the approach, not the code. |

## Where the launcher keeps its state

In the Stellaris user-data folder — the **parent** of the `mod/` directory we
deploy into, mounted here at `/paradox/stellaris`:

```
<user-data>/
├── launcher-v2.sqlite     what the launcher lists: mod state
│                          (dirPath, status) AND playsets
├── dlc_load.json          what a run ACTUALLY loaded — read this before
│                          concluding anything from a clean error.log
├── logs/error.log         the log that matters
└── mod/                   the deploy target
```

There is **no `mods_registry.json` here.** The threads above discuss it because
it was the older launcher's registry; on this install `launcher-v2.sqlite` is
the whole story, and the Proton prefix that did hold one is the dormant folder
(see below). Corrected 2026-08-07 — this diagram had listed it for five days.

**`<user-data>` is not a fixed path — it follows the installed build**, and this
machine has used both. Ask `/stellaris/launcher-settings.json:gameDataPath`
rather than remembering:

| `gameDataPath` | Build | Folder |
|---|---|---|
| `$LINUX_DATA_HOME/…` | native Linux — **current, since 2026-08-02** | `~/.local/share/Paradox Interactive/Stellaris/` |
| `%USER_DOCUMENTS%/…` | Windows under Proton | `…/compatdata/281990/pfx/drive_c/users/steamuser/Documents/Paradox Interactive/Stellaris/` |

Both directories exist on disk and each holds a plausible-looking registry, so
reading the wrong one yields confident wrong answers. Decision 15; decision 07 is
the session that cost.

Back up both registry files before touching either. Playsets live in the sqlite
file, so deleting it to force a rebuild costs you them — and note they are
per-folder, so they do **not** follow the game across a platform switch.

## Running Steam games on CachyOS

The host is CachyOS, and Steam runs games inside its own container. Relevant
because it decides where the launcher's files actually live. Proton is **not**
in use as of 2026-08-02 — compatibility mode was turned off — but the toggle is
one click, so this stays.

| Source | Good for |
|---|---|
| [Gaming with CachyOS](https://wiki.cachyos.org/configuration/gaming/) | The official guide: Steam install, Proton variants, Lutris. **Returns HTTP 403 to `WebFetch`** — read it in a browser or via search snippets. |
| [proton-cachyos](https://github.com/CachyOS/proton-cachyos) | CachyOS's Proton fork. Ships `proton-cachyos-native` and `proton-cachyos-slr`; **`-slr` is the recommended one** and is built on the Steam Linux Runtime, i.e. the containerised path. |
| [steamtinkerlaunch: Compatdata](https://github.com/sonic2kk/steamtinkerlaunch/wiki/Compatdata) | Clear explanation of what a `compatdata/<appid>` prefix is and how to navigate `pfx/drive_c`. |
| [Stellaris mod file locations](https://aerolfos.github.io/stellaris_mod_deploy_action/General%20Stellaris%20mod%20support/mod_file_locations/) | Per-platform user-data paths. Covers Windows / Linux-native / macOS but **not** Proton — which is exactly the case that bit us. |

Stellaris' Steam AppID is **281990**, so its prefix is
`steamapps/compatdata/281990/pfx/drive_c/users/steamuser/`.

## This install, verified from disk

Facts established by reading `/stellaris` and `/paradox/stellaris` directly.
**Re-verified 2026-08-02 after compatibility mode was turned off** — the first
two bullets are the ones that flipped.

- **Stellaris here is the native Linux build** — `/stellaris/stellaris` is ELF
  64-bit x86-64, alongside `libPDXSDK.so`, `libnakama-cpp.so`, `libsteam_api.so`
  and `launcher-installer-linux_2024.14`. No `.exe`, no `.dll`. `gameDataPath` is
  `$LINUX_DATA_HOME/Paradox Interactive/Stellaris`. Written by Steam at
  20:04 BST on 2026-08-02, ~45 s after the last Proton session exited.
- **The Proton prefix is now the stale folder**, and `~/.local/share/Paradox
  Interactive/Stellaris/` is live again. Before the switch the prefix held the
  only `mods_registry.json`; the native folder had `launcher-v2.sqlite` alone,
  last written 2025-11-09. Its 33 Workshop `.mod` entries carry absolute native
  Linux paths — **evidence about the native launcher, which is the one running
  now**, and the thing decision 07 rightly warned against reading as evidence
  about Proton. Same files, opposite conclusion, because a different build is
  installed. Check what wrote a file *and* whether that thing is still what you
  are reasoning about.
- **A local mod's `path=` works as an absolute path on both builds**, and both
  are confirmed by live runs rather than inferred: under Proton as
  `C:/users/steamuser/Documents/Paradox Interactive/Stellaris/mod/<name>`, and
  on native Linux as the plain host path, which is what `tools/deploy.py` emits
  now. Every run since the switch records
  `enabled_mods: ["mod/star_trek_galaxies.mod"]`.
- `supported_version` **does** need the leading `v`. The launcher stores the
  string verbatim and does not normalise it: `4.4.6` registers fine but badges
  the mod "made for a different version", where `v4.4.6` does not. (An earlier
  version of this line said the `v` was optional, generalising from mods whose
  stale `2.1.*`-era versions could not discriminate.) Decision 07's addendum has
  the 26-mod distribution that settles it.
- Installed game: `Pegasus v4.4.6`, `modsCompatibilityVersion 4.4`.
