# Subscribed Steam Workshop Mods

> **What** — inventory of the `/workshop` mount, and which of those mods STG
> actually harvests.
> **Open when** — checking whether a mod is available, subscribed, or snapshotted.
> **Then** — [Harvest order](../architecture/harvest-order.md) · [Source snapshots](../guides/source-snapshots.md)

Inventory of the read-only `/workshop` mount as seen from the dev container.
Everything below is read straight from each mod's `descriptor.mod`.

- **Mods on disk:** 54
- **Total size:** ~24 GB
- **Regenerated:** 2026-08-09
- **Our target:** Stellaris 4.4.x "Pegasus"

This is an inventory of what is *subscribed*, not what STG builds from. **49 of
these 54 are harvested**, and the build reads pinned copies in `.source/`, never
this mount. The five not harvested are marked **`not harvested`** below — two
of them are still snapshotted, so restoring one is a `vendor.yml` edit away:

| Mod | Why | In `.source/`? |
|---|---|---|
| Ariphaos Unofficial Patch | [Decision 02](../decisions/02-drop-ariphaos.md) | **no** — dropped before `.source/` existed |
| Kammarheit | [Decision 11](../decisions/11-drop-cinematic-camera-and-ambient-soundtracks.md) — taste | yes |
| Apocryphos | [Decision 11](../decisions/11-drop-cinematic-camera-and-ambient-soundtracks.md) — taste | yes |
| More Events Mod (MEM) | [Decision 80](../decisions/80-mem-integration-deferred.md) — **deferred, not declined** | **no** — snapshot it when the pass starts |
| MEM planetary-shields compatch | Ships with MEM; same deferral | **no** |

> **The last two rows are not the same kind of row as the three above them.**
> Ariphaos, Kammarheit and Apocryphos were *declined* on content grounds; MEM is
> *queued*, and its `supported_version` is current. Do not read one column as one
> verdict. [Decision 80](../decisions/80-mem-integration-deferred.md) has the
> reasoning and the one trap: **the compatch's name says Planetary Shields and
> all 19 of its files are `mem_*`.**

Cinematic Camera was a sixth row in that table until 2026-08-07 and is now
harvested like any other source. Decision 11 dropped it for breaking Real Space –
System Scale;
[decision 43](../decisions/43-planet-scale-system-length.md) showed the error was
System Scale's own, present with and without it, and restored it.

For what is actually in the tree, in harvest order and at which upstream
revision, see `sources.lock.yml` and `.docs/provenance.md` — both generated, so
neither can go stale the way this file can. Regenerate the tables here by
walking `/workshop/*/descriptor.mod`; nothing derives them automatically.

Workshop URL pattern: `https://steamcommunity.com/sharedfiles/filedetails/?id=<ID>`

---

## Total conversions / large overhauls

| Mod | ID | Version | Supported | Size |
|---|---|---|---|---|
| [Star Trek: New Horizons](https://steamcommunity.com/sharedfiles/filedetails/?id=688086068) | 688086068 | 4.4.6 | v4.4.6 | 13.7 GB |
| [Real Space 4.0](https://steamcommunity.com/sharedfiles/filedetails/?id=937289339) | 937289339 | 4.0.10 | v4.4.6 | 1.2 GB |
| [Planetary Diversity](https://steamcommunity.com/sharedfiles/filedetails/?id=819148835) | 819148835 | — | v4.4.\* | 2.0 GB |

**Star Trek: New Horizons is the single most relevant prior art in this mount** —
same setting, same total-conversion shape, and it is current for our exact target
version. Grep it before designing anything Trek-specific. STG takes its art paths
only, never its `common/`, `events/`, `interface/` or `map/`.

## Walshicus' Trek shipsets — the *Star Trek: New Civilisations* family

22 standalone shipsets, one culture each, all built on vanilla's ship chassis
natively. They are the reason nine playable cultures fly real Trek warships with
working weapon mounts, and the raw material eight frontier powers were built
from. [Decision 18](../decisions/18-walshicus-shipsets-replace-stnh-hulls.md).

All 22 declare `supported_version="v4.3.*"` and carry no `version`. STG takes
only `gfx/` and `common/graphical_culture/` from them — never `interface/`
(each ships a stale `credits.txt`), `common/species_classes/`, `flags/` or
`localisation/`.

| Mod | ID | Size | | Mod | ID | Size |
|---|---|---|---|---|---|---|
| Starfleet TNG Era | 3118844461 | 239 MB | | Klingon | 2672884318 | 145 MB |
| Dominion | 3323680661 | 222 MB | | Terran NX Era | 2679512490 | 139 MB |
| Suliban | 3200287636 | 188 MB | | Ferengi | 3059310220 | 133 MB |
| Vidiian | 3629202562 | 185 MB | | Malon | 2945365572 | 109 MB |
| Talarian | 2891668465 | 178 MB | | Vulcan | 2804194007 | 106 MB |
| Krenim | 3243439669 | 166 MB | | Lukari | 3443849210 | 104 MB |
| Xindi | 2851692297 | 158 MB | | Elachi | 3401984530 | 103 MB |
| Romulan | 2702005349 | 156 MB | | Tuterian | 2833499231 | 91 MB |
| Cardassian | 2728498280 | 148 MB | | Betazoid | 2990277402 | 82 MB |
| Yridian | 2745386732 | 47 MB | | Caitian | 2687653241 | 34 MB |
| Borg | 2953073033 | 20 MB | | Tholian | 2683475897 | 16 MB |

## Planetary Diversity family

`Planetary Diversity` (819148835) is the base; the rest extend it.

| Mod | ID | Supported | Size | Depends on |
|---|---|---|---|---|
| [PD - Ascension Worlds](https://steamcommunity.com/sharedfiles/filedetails/?id=3241119393) | 3241119393 | v4.4.\* | 593 MB | — |
| [PD - More Arcologies](https://steamcommunity.com/sharedfiles/filedetails/?id=1732447147) | 1732447147 | v4.4.\* | 587 MB | Planetary Diversity |
| [PD - Unique Worlds](https://steamcommunity.com/sharedfiles/filedetails/?id=1740165239) | 1740165239 | v4.4.\* | 124 MB | — |
| [PD - Vanilla Replacements](https://steamcommunity.com/sharedfiles/filedetails/?id=3173239930) | 3173239930 | v4.4.\* | 106 MB | — |
| [PD - Gaia Worlds](https://steamcommunity.com/sharedfiles/filedetails/?id=2284514368) | 2284514368 | v4.4.\* | 77 MB | — |
| [PD - City Sets](https://steamcommunity.com/sharedfiles/filedetails/?id=3142294658) | 3142294658 | v4.4.\* | 19 MB | — |
| [PD - Planet View](https://steamcommunity.com/sharedfiles/filedetails/?id=1866576239) | 1866576239 | v4.4.\* | 17 MB | Planetary Diversity |

Note: *Vanilla Replacements* replaces vanilla planet assets outright — worth a
conflict check before we shadow anything under `common/planet_classes/` or the
matching `gfx/`.

## UI

| Mod | ID | Version | Supported | Size |
|---|---|---|---|---|
| [UI Overhaul Dynamic](https://steamcommunity.com/sharedfiles/filedetails/?id=1623423360) | 1623423360 | 4.4.\* | v4.4.\* | 232 MB |
| [UIOD - Dark UI](https://steamcommunity.com/sharedfiles/filedetails/?id=1993018111) | 1993018111 | 4.4.\* | v4.4.\* | 170 MB |
| [UIOD - Extended Topbar for DLCs](https://steamcommunity.com/sharedfiles/filedetails/?id=3090328185) | 3090328185 | 4.4.\* | v4.4.\* | 1.1 MB |

UIOD rewrites large parts of `interface/`. Any `.gui` we ship that shadows a
vanilla file is a likely collision — check `rg -l "<filename>" /workshop/1623423360`.

## Gameplay / balance

| Mod | ID | Version | Supported | Size |
|---|---|---|---|---|
| [Real Space - System Scale](https://steamcommunity.com/sharedfiles/filedetails/?id=1887282318) | 1887282318 | 1.8.9 | v4.4.\* | 1.0 MB |
| [Real Space - Ships in Scaling](https://steamcommunity.com/sharedfiles/filedetails/?id=1915620447) | 1915620447 | 1.18 | v4.4.\* | 974 KB |
| [Starbase Extended 3.0](https://steamcommunity.com/sharedfiles/filedetails/?id=3250900527) | 3250900527 | 1.3.5. | v4.\*\*.\* | 1.7 MB |
| [Yet Another Galaxy Enhancement Mod](https://steamcommunity.com/sharedfiles/filedetails/?id=1327874725) | 1327874725 | 4.2.0 | v4.2.\* | 1.1 MB |
| [Sensor Expansion](https://steamcommunity.com/sharedfiles/filedetails/?id=2002751329) | 2002751329 | 4.1 | v4.1.\* | 915 KB |
| [Assorted Precursor Adjustments](https://steamcommunity.com/sharedfiles/filedetails/?id=1326381312) | 1326381312 | 3.13.0 | v4.1.\* | 861 KB |
| [Cinematic Camera](https://steamcommunity.com/sharedfiles/filedetails/?id=703156866) | 703156866 | 2.6.1 | v4.\*.\* | 429 KB |
| [More Events Mod](https://steamcommunity.com/sharedfiles/filedetails/?id=727000451) | 727000451 | 2.20.0 | v4.4.\* | 2.3 GB — **not harvested yet** |

## Patches / fixes

| Mod | ID | Version | Supported | Size |
|---|---|---|---|---|
| [~~Ariphaos Unofficial Patch (4.2)~~](https://steamcommunity.com/sharedfiles/filedetails/?id=1995601384) | 1995601384 | 4.2.4 | v4.2.4 | 13 MB — **not harvested** |
| [!!!Universal Resource Patch [2.4+]](https://steamcommunity.com/sharedfiles/filedetails/?id=1595876588) | 1595876588 | 4.1.\* | v4.\*.\* | 272 KB |
| [RS System Scale / Planetary Shields Compatch 2.0](https://steamcommunity.com/sharedfiles/filedetails/?id=2993881965) — **a MEM patch despite the name** | 2993881965 | 1 | 3.11.2 | 3.6 MB — **not harvested** |

The Universal Resource Patch is the conventional compatibility layer for mods
adding new strategic resources — relevant if STG introduces any. STG ships a
pruned copy of its topbar file; see
[harvest order](../architecture/harvest-order.md#why-the-universal-resource-patch-is-last-not-first).

## Graphics / visual

| Mod | ID | Version | Supported | Size |
|---|---|---|---|---|
| [Diverse Rooms (Updated)](https://steamcommunity.com/sharedfiles/filedetails/?id=3397828987) | 3397828987 | 4.4.\* | v4.4.\* | 94 MB |
| [ASB Ironman](https://steamcommunity.com/sharedfiles/filedetails/?id=1880071041) | 1880071041 | 2.6 | v4.\*.\* | 114 MB |
| [!! K !! - Realistic Asteroids](https://steamcommunity.com/sharedfiles/filedetails/?id=1318671320) | 1318671320 | — | — | 5.6 MB |
| [Whiter Stars](https://steamcommunity.com/sharedfiles/filedetails/?id=1506079770) | 1506079770 | 3.\* | 3.\* | 406 KB |
| [!The Galaxy Is Flat](https://steamcommunity.com/sharedfiles/filedetails/?id=1407858645) | 1407858645 | — | — | 635 B |

## Sound / music

| Mod | ID | Supported | Size |
|---|---|---|---|
| [Kammarheit - A Dark, Otherworldly Ambient Soundtrack](https://steamcommunity.com/sharedfiles/filedetails/?id=1409667987) | 1409667987 | v4.4.6 | 534 MB — **not harvested** |
| [Apocryphos - A Dark Ambient Soundtrack](https://steamcommunity.com/sharedfiles/filedetails/?id=1430192994) | 1430192994 | v4.4.6 | 430 MB — **not harvested** |
| [Extended Soundtrack](https://steamcommunity.com/sharedfiles/filedetails/?id=1224507727) | 1224507727 | — | 71 MB |

---

## Notes for grepping

Three mods ship as a `.zip` and are invisible to a plain `rg /workshop` — their
`descriptor.mod` is inside the archive too, which is why they show no name or
version above. Unzip to a temp dir first:

| ID | Archive |
|---|---|
| 1224507727 | `exst.zip` |
| 1318671320 | `hd_asteroids.zip` |
| 1407858645 | `!flat_galaxy.zip` |

```bash
unzip -o /workshop/1318671320/hd_asteroids.zip -d "$SCRATCH/hd_asteroids"
```

### Declared support below our 4.4 target

These declare an older `supported_version` than the 4.4.x we target. The launcher
flags them, and they are the least reliable as prior art for current-version
script:

`1326381312` (v4.1), `1327874725` (v4.2), `1995601384` (v4.2.4), `2002751329`
(v4.1), `1506079770` (3.\*), `2993881965` (3.11.2), and **all 22 Walshicus
shipsets** (v4.3.\*). The three `.zip` mods declare nothing readable from
outside the archive.

Note that `supported_version` is author-declared, not verified — several of these
still work fine, the shipsets conspicuously so. Treat it as a caution flag, not a
fact about the code.
