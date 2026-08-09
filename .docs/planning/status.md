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
| **Phase 2** — the rest of the galaxy | **complete**. 101 prescripted empires (22 playable, 79 AI-only minors) over 100 distinct species classes, 92 name lists, 37 real home systems. `src/` declares **131** classes in all — the extra 31 are the STNH selector stubs of [decision 32](../decisions/32-declare-stub-species-classes.md) |
| **Phase 3** — art and identity | **complete 2026-08-08**. Clothing triggers, shipsets, weapon mounts, flags, rooms, city sets, loading screens, `paragon_backgrounds.txt`, the shipsets' 39 extra flags |
| **Phase 4** — polish | **started 2026-08-08**. Music, the ship registries and their class names, then the three slices [decision 75](../decisions/75-trek-anomalies.md) scoped: **21 Trek anomalies** ([75](../decisions/75-trek-anomalies.md)), **6 dig sites** ([76](../decisions/76-trek-archaeology.md)) and **21 story events** ([77](../decisions/77-trek-story-events.md)), all 2026-08-09. All three are shipped; what remains in the phase has no scope written for it |
| **Phase 5** — the clutter pass | **complete 2026-08-07** (pipeline work, taken out of order) |

## The build, as it stands

**Read every figure below off the build rather than off this page** —
`.vendor-manifest.json` and the `make validate` summary line carry the live
ones.

| | Build of 2026-08-09 |
|---|---|
| Files / size | **22,405 / 14.3 GB** ([the per-tier split](../architecture/vendored-merge.md#size)) |
| Re-cut at harvest / pruned | 1,661 / **888** |
| `make vendor` | 80 s |
| `make validate` | **0 warnings, 0 errors** |
| `make docs` | **0 warnings, 0 errors** |

**The prune has fallen 935 → 909 → 888 across three passes with no edit to
`vendor.yml`**, and that is the property worth knowing rather than the number:
the 27 pictures [decision 76](../decisions/76-trek-archaeology.md)'s dig sites
declare and the 21 [decision 77](../decisions/77-trek-story-events.md)'s story
events declare came back out of `.source/` by themselves, exactly as the
anomalies' 24 did. Declaring art un-prunes it; nothing has to be excluded.

`make validate` gained `check_anomalies`, `check_archaeology` and
`check_story_events` over Phase 4 and `make docs` gained a second family of
question — whether the documented inventory still matches the repo, not only
whether its citations resolve ([71](../decisions/71-doc-inventory-checks.md)).
What each asks, and the vanilla floor each is calibrated against, is in
[the check catalogue](../validation/checks.md); the floors themselves are
constants in `tools/validate.py` with the ratio written beside them
([rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter)).

---

## The `error.log` baseline

**From the 2026-08-08 Terran Empire run:** `error.log` is **1,261 records /
187 KB**, against the ~1 MB a clean vanilla run produces. **Exactly 1 record falls
after the 49.3 s startup window.** No record names anything `stg_`, and none names
clothes, city sets or ship locators — all four of that run's findings were
eyes-only, which is now the standard shape.

> **The baseline predates the whole of decisions 74–77.** `error.log` was last
> written 2026-08-08 20:45; the anomalies landed at `cba8a81` (2026-08-09 09:15)
> and the dig sites and story events at `272f3c7` (2026-08-09 13:31). So the
> 1,261 records describe a build containing **none** of the largest single
> addition the project has made — 21 anomaly categories, 6 dig sites, 23 story
> events, 144 sprites, 72 re-cut pictures, 324 loc keys and ~11,200 words.
> `make validate` covers the references and nothing covers the rest.
>
> **The next live run should open the situation log and let a survey fleet
> work**, and reconcile group by group against these 1,261
> ([live-runs.md](../guides/live-runs.md)). Three things are unmeasured and
> nothing container-side can reach them: whether the 72 event pictures render at
> the right size in the popup; whether `stg_on_five_year_story_pulse` fires at
> all; and whether any dig site is ever placed.
> [The 2026-08-15 audit](../analysis/2026-08-15.md), finding 1.

The game has been the **native Linux build** since 2026-08-02
([decision 15](../decisions/15-native-linux-runtime.md)) — content unaffected,
deployment re-confirmed on it, startup and gfx counts **not comparable across that
boundary**.

Analyses are written only on request, one file per live run
([`../analysis/`](../analysis/README.md)); until the next one exists, this
section is the baseline.

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

**The 17 warnings standing on 2026-08-07 were triaged to 0, and two of them were
real defects** — five nebula and debris entities rendering at a third of System
Scale's size, and every empire's habitats at risk of drawing as a Suliban helix.
Decisions [53](../decisions/53-duplicate-entity-triage.md),
[54](../decisions/54-federation-texture-collisions.md),
[56](../decisions/56-starbase-modules-order.md). **Nothing in that has been seen
by a live run yet.**
