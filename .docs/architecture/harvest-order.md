# Harvest order

> **What** — the order sources apply in, why the Universal Resource Patch is
> last, and which sources are unpacked or dropped.
> **Open when** — adding, reordering or dropping a source, or a file turned out
> to come from the wrong mod.
> **Then** — [STNH art is additive-only](stnh-art.md) · [Conflict register](conflict-register.md) · [decision 04](../decisions/04-harvest-order.md)

Sources apply in order; later ones overwrite earlier ones on identical paths.
Same reasoning as a load order, resolved at build time so the outcome is visible
and recorded.

```
 1  Real Space 4.0                       # owns system generation
 2  Real Space - System Scale            # rescales RS — must beat it
 3  Real Space - Ships in Scaling
 4  Planetary Diversity                  # base before its extensions
 5–11  PD - Vanilla Replacements, Gaia Worlds, Unique Worlds, Ascension Worlds,
       More Arcologies, City Sets, Planet View
12  Yet Another Galaxy Enhancement Mod
13  Assorted Precursor Adjustments
14  Sensor Expansion
15  Starbase Extended 3.0
16  !! K !! - Realistic Asteroids        # zip: hd_asteroids.zip
17  Whiter Stars                         # minus 2 excluded paths
18  !The Galaxy Is Flat                  # zip: !flat_galaxy.zip
19  ASB Ironman
20  Diverse Rooms (Updated)              # minus its second room_selector — decision 46
21  Cinematic Camera                     # camera defines only; `zzzzz_` sorts last
22  UI Overhaul Dynamic                  # UI tier
23  UIOD - Extended Topbar for DLCs      # overrides 23 UIOD files
24  UIOD - Dark UI                       # overrides 189 UIOD files
25  Extended Soundtrack                  # additive; zip: exst.zip
26  !!!Universal Resource Patch          # LAST of the gameplay/UI tier — see below
27  Star Trek: New Horizons              # art paths only, additive-only
28+ Walshicus' 22 Trek shipsets          # decision 17; gfx/, common/graphical_culture
                                         # and flags/trek ADDITIVELY — decision 47
      Betazoid, Borg, Caitian, Cardassian, Dominion, Elachi, Ferengi, Klingon,
      Krenim, Lukari, Malon, Romulan, Starfleet TNG, Suliban, Talarian,
      Terran NX, Tholian, Tuterian, Vidiian, Vulcan, Xindi, Yridian
──  src/                                 # our own content, always last
──  the prune closure                    # decision 43; removes what nothing names
```

**`vendor.yml` is the authority; the list above is the shape, not the spec.** The
shipset tier is last before `src/` because it must beat STNH on the `klingon` and
`romulan` directory names it shares
([decision 17](../decisions/17-walshicus-shipsets-replace-stnh-hulls.md)).

## Sources that ship as `.zip`

Three are unpacked by the vendor tool rather than copied:
`1318671320/hd_asteroids.zip`, `1407858645/!flat_galaxy.zip`,
`1224507727/exst.zip`.

## Why the Universal Resource Patch is last, not first

Its README states the requirement verbatim: *"Load order: Absolute bottom, below
all mods, including UI mods."*

URP's `interface/resource_groups/topbar_other_resource_groups.txt` is **1,271
lines** against vanilla's 41 and is a strict superset of every other contender —
it carries Planetary Diversity's `sr_eludium` / `sr_acean` / `astral_threads`
*and* an explicit STNH block (`sr_latinum`, `sr_dilithium`, `sr_ketracel_white`,
`sr_crew`). Loaded early, PD - Unique Worlds' 42-line version overwrites all of it
and STG silently loses Trek resource display in the topbar.

> **But the superset argument is about the future, not today.** URP's file lists
> 942 resource tokens; in a standalone STG **13 resolve**, and vanilla's own copy
> already lists 10 of those, so URP adds exactly **three** working entries —
> `biomass`, `sr_acean`, `sr_eludium`. The other 929 belong to mods not in the
> harvest and reported themselves as errors on every parse: 929 records, the
> largest class in the 2026-08-02 log.
>
> The file is therefore pruned to what resolves, in
> `src/interface/resource_groups/topbar_other_resource_groups.txt`, and URP stays
> last for the reason above. The superset argument becomes true the moment STG
> defines the four Trek resources, and the override's header says where to add
> them.

## Sources dropped, and one that came back

**Kammarheit and Apocryphos were dropped 2026-08-02** — 919 MB of dark ambient in
a Trek conversion, a taste call
([decision 10](../decisions/10-drop-cinematic-camera-and-ambient-soundtracks.md)).

**Cinematic Camera went with them and came back 2026-08-07**, once the error
blamed on it turned out to be Real Space – System Scale's own
([decision 41](../decisions/41-planet-scale-system-length.md)). Keeping it is a
taste call between two camera tunings, not a correctness one.

**Ariphaos Unofficial Patch is dropped** on content grounds: it declares 4.2.4
against our 4.4 target and shadows 256 vanilla files, 247 of which differ from
current 4.4 — as likely to be silent reversion as fixes
([decision 02](../decisions/02-drop-ariphaos.md)).

> A source is dropped **only** on content grounds, never by quoting an error
> count. [Decision 11](../decisions/11-fix-source-errors-dont-drop.md).

Full inventory of what is subscribed against what is harvested:
[subscribed mods](../planning/subscribed-mods.md).
