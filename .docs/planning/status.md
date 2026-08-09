# Where things stand

> **What** — the current state of the build: phase completion, the `error.log`
> baseline, and what the last live runs established.
> **Open when** — starting a session, or before quoting any number about the
> build.
> **Then** — [Open questions](open-questions.md) · [Phases](phases.md) · [Live runs](../guides/live-runs.md)

*Last updated against the build of 2026-08-09 and the runs of 2026-08-08. Every
number here has a date because every number here goes stale —
[style guide §6](../style-guide.md).*

| | |
|---|---|
| **Phase 0** — vendoring pipeline | **complete** |
| **Phase 1** — playable Federation | **complete**, run in-game repeatedly |
| **Phase 2** — the rest of the galaxy | **complete**. 101 prescripted empires (22 playable, 79 AI-only minors), 101 species classes, 92 name lists, 37 real home systems |
| **Phase 3** — art and identity | **complete 2026-08-08**. Clothing triggers, shipsets, weapon mounts, flags, rooms, city sets, loading screens, `paragon_backgrounds.txt`, the shipsets' 39 extra flags |
| **Phase 4** — polish | **started 2026-08-08**: music ([55](../decisions/55-federation-anthem.md)), then the ship registries ([59](../decisions/59-ship-name-pools.md)) and their class names ([72](../decisions/72-ship-class-names.md), [73](../decisions/73-class-name-thematic-fill.md)), then **21 Trek anomalies** on 24 reclaimed STNH event pictures ([75](../decisions/75-trek-anomalies.md), [74](../decisions/74-event-picture-families.md), 2026-08-09), then **6 Trek archaeological sites** on 27 more ([76](../decisions/76-trek-archaeology.md)), then **21 Trek story events** on 21 more ([77](../decisions/77-trek-story-events.md)), all 2026-08-09. All three things [decision 75](../decisions/75-trek-anomalies.md) scoped are shipped |
| **Phase 5** — the clutter pass | **complete 2026-08-07** (pipeline work, taken out of order) |

`make docs` stands at **0 warnings, 0 errors** and now asks a second family of
question — whether the documented inventory still matches the repo, not only
whether its citations resolve. The pass that added it found six live
inconsistencies against a tree the old checker had just passed
([decision 71](../decisions/71-doc-inventory-checks.md)).

`make validate` stands at **0 warnings, 0 errors**, now including
`check_shadowed_texture_geometry`'s second question — whether art that shadows
*no* vanilla path still matches the family vanilla is uniform about, calibrated at
113 findings before [decision 63](../decisions/63-city-set-family-targets.md)'s
fix and 0 after — and `check_anomalies`, which asks the six questions vanilla
scores 0 on across its 327 anomaly categories, and a seventh scoped to the one
file where its floor is not 114 of 310
([decision 75](../decisions/75-trek-anomalies.md)).

**And `check_archaeology`, the same shape one database over**: ten questions
across vanilla's 123 site types and 475 stage events, nine of them at 0 and the
tenth at a floor of 1 (`cstorms.1300`'s undefined option key), plus an eleventh
scoped to our own events file, where vanilla's floor would be 157 of 628. One of
the ten — **`stages = N` against the `stage` blocks beside it** — has no
counterpart in `check_anomalies` and nothing else in the game enforces it
([decision 76](../decisions/76-trek-archaeology.md)).

**And `check_story_events`, the same shape a third time**, over the built tree's
58 non-empty on_action hooks. Its first question has no counterpart in either
sibling — **is the on_action KEY one the engine will ever fire?** — and vanilla
scores 0 there once empty stubs are excluded, against **17 dangling event ids in
its own `00_on_actions.txt`** ([decision 77](../decisions/77-trek-story-events.md)).

> That first run found a defect in the two checks beside it rather than in the
> content: a bare **`event = { }`** declaration is legal, vanilla writes it in
> forty-odd of its own files, and `kind.endswith("_event")` does not match it —
> so 26 live hooks in four source mods read as dangling. All three checks now
> share `_is_event_block`. Neither sibling's floor moved.

**That family question now covers `gfx/event_pictures` as well**, where it had
been declined on a measurement that read one directory as one family. It is two:
the top level is 580 of 580 at 450×150 and `origins/` is 59 of 59 at 220×115.
Splitting them is what makes a Trek event picture usable at all
([decision 74](../decisions/74-event-picture-families.md)). Build of 2026-08-09:
**22,405 files, 14.3 GB**, 1,661 re-cut at harvest, 888 pruned, `make vendor`
in 80 s. The prune has fallen 935 → 909 → **888** with no edit to `vendor.yml`
across three passes: the 27 pictures
[decision 76](../decisions/76-trek-archaeology.md)'s dig sites declare and the
21 [decision 77](../decisions/77-trek-story-events.md)'s story events declare
came back out of `.source/` by themselves, exactly as the anomalies' 24 did.

---

## The `error.log` baseline

**From the 2026-08-08 Terran Empire run:** `error.log` is **1,261 records /
187 KB**, against the ~1 MB a clean vanilla run produces. **Exactly 1 record falls
after the 49.3 s startup window.** No record names anything `stg_`, and none names
clothes, city sets or ship locators — all four of that run's findings were
eyes-only, which is now the standard shape.

The game has been the **native Linux build** since 2026-08-02
([decision 15](../decisions/15-native-linux-runtime.md)) — content unaffected,
deployment re-confirmed on it, startup and gfx counts **not comparable across that
boundary**.

`.docs/analysis/` was cleared on 2026-08-03 and is written only on request; until
one exists, this section carries the baseline.

---

## The four runs of 2026-08-08

Each row's findings are in its decisions; only the shape is kept here.

| Run | Records | Left | Confirmed |
|---|---|---|---|
| Klingon Empire | 2,020 | ruler clothes index [57](../decisions/57-prescripted-rulers-unpin-clothes.md), city canvas [58](../decisions/58-city-set-geometry.md), ship name pools [59](../decisions/59-ship-name-pools.md), designer clothes gating [22](../decisions/22-empire-designer-clothes.md) | |
| Cardassian Union | 1,269 / 187 KB | city prefixes [63](../decisions/63-city-set-family-targets.md), mirror uniforms [64](../decisions/64-terran-empire-mirror-uniforms.md), music rotation [65](../decisions/65-music-rotation-dedupe.md) | hidden empires back [62](../decisions/62-city-set-cultures-undeclared.md), room list >300 [48](../decisions/48-room-selector-merge.md), star names append [52](../decisions/52-trek-star-names.md) |
| Terran Empire | 1,261 / 187 KB | ruler clothes [68](../decisions/68-ruler-clothes-index-restored.md), NX corvette guns [67](../decisions/67-source-art-hardpoint-names.md), Vulcan city art [66](../decisions/66-city-set-canvas-overflow.md) | mirror uniforms reach leaders, rotation is 27 tracks |
| Vulcan Confederacy | 1,279 / 187 KB | city framing [70](../decisions/70-vulcan-city-framing.md) — reviewed and left | |

**Every finding across all four was eyes-only.** That is now the standard shape:
`make validate` was clean throughout, and the 590-record room-selector `weight`
defect visible in the Klingon count is the last one a log carried.

**The one falsification worth carrying forward.** The Vulcan run killed
[decision 68](../decisions/68-ruler-clothes-index-restored.md) outright — all six
rulers it pinned an index for wore a garment the model does not predict, so
`clothes = N` on a *shared* master selector is not an enumeration, and nothing in
the container can say what it is. The seven affected rulers now take STNH's own
convention: a dedicated **one-texture** selector and `clothes = 0`, the one index a
live run has ever confirmed. [Decision 69](../decisions/69-ruler-clothes-dedicated-selectors.md).

---

## The warning triage of 2026-08-08

The 17 warnings standing on 2026-08-07 were triaged to **0**, and **two of them
were real defects**: five nebula and debris entities rendering at a third of
System Scale's size, and every empire's habitats at risk of drawing as a Suliban
helix. Decisions [53](../decisions/53-duplicate-entity-triage.md),
[54](../decisions/54-federation-texture-collisions.md),
[56](../decisions/56-starbase-modules-order.md). **Nothing in that has been seen
by a live run yet.**
