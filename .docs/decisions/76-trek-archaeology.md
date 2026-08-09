# 76 — Trek archaeology, and the one field in the format that decides whether any of it is ever seen

**Status:** decided, 2026-08-09
**Follows:** [75](75-trek-anomalies.md)
**Gains the check it asked for:** [79](79-reachability-checks.md) — the `weight`
question below had no check behind it for as long as this file has existed; it
does now, together with the second half it needs.

## What this closes

[Decision 75](75-trek-anomalies.md) split Phase 4's remaining work into
**anomalies first, archaeology and story events after**, and shipped the first
half. This is the second half. Story events are still unstarted, and still
deliberately so.

The starting position was the same one 75 found: `common/archaeological_site_types/`
in the built tree held **one** file, `pd_uniques_arc_sites.txt`, from Planetary
Diversity. The harvest takes no `events/` from STNH by design
([architecture/stnh-art.md](../architecture/stnh-art.md)), so there is nothing to
fold or remap — every word here is written rather than converted.

## What shipped

| | |
|---|---|
| `src/common/archaeological_site_types/stg_arc_sites.txt` | **6 sites**, 27 stages |
| `src/events/stg_arcsite_events.txt` | **27 stage events**, one namespace, no chains |
| `src/interface/stg_arcsite_pictures.gfx` | **54 sprites over 27 STNH pictures** |
| `src/common/static_modifiers/stg_archaeology_modifiers.txt` | **9 finale modifiers** |
| `src/localisation/english/stg_archaeology_l_english.yml` | **117 keys, ~3,800 words** |

Six sites: the Hall of the Blade, the Ark in the Sand, the Sealed Mechanism, the
Desert Sanctuary, the Hebitian Vaults, the Lost Colony. Two of five stages, four
of four, and so on — 27 stages between them.

**The yardstick is vanilla's base game, as it was for the anomalies.**
`00_base_game_arc_sites.txt` ships **10** sites (123 across all files, most of
them DLC). Six against ten, thin rather than padded, which is
[decision 73](73-class-name-thematic-fill.md)'s call about pool sizes applied to
a third database.

**Every field, trigger, difficulty and idiom is copied from a vanilla file that
was opened** — the sites from `00_base_game_arc_sites.txt`, the stage events from
`events/arcsite_events.txt`, the modifier fields from
`common/static_modifiers/02_static_modifiers.txt`. No `specimen`, no minor
artifacts, no `has_ancrel` branch: STG is standalone, and vanilla's own comment
at the head of the base-game file says the same thing from the other side — *"a
base-game arc site must offer a reward other than Minor Artifacts"*.

## The finding: `weight` is the whole question, and six of vanilla's ten decline it

A site type has a `weight` block, and the obvious reading — this is how often the
site turns up — is wrong in a way that would have shipped six sites nobody could
ever find.

**`weight` is read by exactly one thing: `create_archaeological_site = random`.**
The README says so, and the sweep agrees — the only caller in the whole game is
`ancrel.9999` in `events/ancient_relics_site_spawn_event.txt`, hung on
`on_survey_planet`, firing on a 5-in-405 roll per surveyed body. Its trigger asks
about existing sites, carrier flags and trade-value deposits, and **nothing about
DLC ownership**, so a weighted site reaches every host.

**Six of vanilla's ten base-game sites carry `weight = 0`**, with a comment
saying `#set via initialiser` or `#Generated from an event`. Those six are placed
by a story chain that knows where it wants them. STG writes no story chain, so a
`weight = 0` site here would be a site with no way into a galaxy at all —
correct, complete, validating clean, and unreachable. All six of ours carry real
weights, keyed on planet class the way vanilla's four weighted sites are.

That is the same class of defect as [decision 62](62-city-set-cultures-undeclared.md)'s
undeclared graphical cultures: everything present, nothing dangling, and the
content simply never appears.

## The art, and the eleven rejections

27 pictures, all STNH's, all of them art the clutter closure had been pruning
until something declared it — [decision 74](74-event-picture-families.md) is what
makes them usable at 450×150 at all. The prune fell 935 → **909** with no edit to
`vendor.yml`, exactly as it did for the anomalies.

**Every candidate was looked at as the build will cut it** — frame 0 of the strip,
centre-cropped to 450×150 — and **eleven were rejected on what that crop showed**:
four TAS-animated frames (the same call
[75](75-trek-anomalies.md) made on `mugato_world.dds`), three close-ups of a
named character's face, two near-featureless gradients, and two too dark to read
at this size. Three of those eleven were named after exactly the subject a site
wanted. A filename cannot make this call.

**Four first choices were already spent.** `theChase`, `undergroundTunnels`,
`stone_of_gol` and `ancientCapsule1` are all declared by the anomalies' `.gfx`,
so the sites took `stone_of_gol_1`/`_3` and `ancientCapsule2` and found other art
for the caves. One picture, one subject — otherwise a dig site and an anomaly
show the player the same photograph and the tree looks smaller than it is.

## Our own modifiers, for a reason that is not about numbers

Five of the six sites end on a choice, and a choice needs two outcomes that
differ. The shortcut is to reuse a vanilla static modifier —
`ice_trauma_insights_colony` has precisely the effect the Lost Colony wants.

It also has precisely the **name** *"Frozen Submariners' Legacy"*, which is what
the player reads on their modifier list under a Trek dig that has nothing to do
with submarines. **A static modifier is a loc key with numbers attached, and the
loc key is the half that shows.** Hence nine of our own, with fields copied from
vanilla's file and magnitudes set beside vanilla's own arc-site rewards.

The five `max_instances = 1` sites hand out permanent modifiers, as vanilla's
unique sites do. **The Lost Colony is the one site with no `max_instances`** — it
names a *kind* of thing rather than a specific one, which is
[75](75-trek-anomalies.md)'s split applied here — so its modifier is timed, and
cannot be stacked into an empire-wide bonus by digging.

## The check

`check_archaeology` in `tools/validate.py`. A dig site is **five files that have
to agree**, and none of them dangles when they do not.

**Vanilla is the calibration**, over its 123 site types and the 475 stage events
they name:

| Question | Vanilla findings |
|---|---|
| site's picture is declared | 0 |
| site name / desc loc key | 0 / 0 |
| stage names an event that exists | 0 |
| stage rune icon is declared | 0 |
| **`stages = N` matches the `stage` blocks** | **0** |
| `RANDOM_EVENTS` names a scripted effect | 0 |
| stage event's picture is declared | 0 |
| stage event title / desc loc key | 0 |
| stage event option loc key | **1** — `cstorms.1300` offers `NAME_Hold_the_line_habitat`, which no localisation file defines |
| stage event's awarded modifier is declared, and localised | 0 / 0 |

So all ten are asked of every site in the built tree.

**`stages = N` has no counterpart in `check_anomalies`** and is the question most
worth having. It is a hand-written integer beside a list of blocks; vanilla's
README says only that it *"should match"*; nothing enforces it; and a site that
claims more stages than it has cannot be finished, while one that claims fewer
never fires its last event. Vanilla is 0 for 123, so the floor is exact.

**The eleventh question has a scope**, for the reason it does in
`check_anomalies`: *"an archaeology event no site names"* scores **157 of
vanilla's 628** `archaeology = yes` events, because vanilla chains dig-team
interruptions off scripted effects this check does not read. Over
`stg_arcsite_events.txt` the shape is different by construction, so the question
is exact there and meaningless anywhere else.
[Check design rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter).

> **One floor was 1 and became 0, and the fix is a calibration result rather than
> thoroughness.** `modifier = X` inside an event is written identically for an
> empire modifier and an opinion modifier, and reading only
> `common/static_modifiers/` reports vanilla's own `strange_worlds.2050` for
> awarding `opinion_gift_given`. Reading `common/opinion_modifiers/` beside it is
> one line. [Rule 4](../validation/check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand):
> the allowlist comes from vanilla's usage, not from a guess about which database
> a field means.

**Then deliberately, against a broken tree:** a dangling stage event, an
undeclared site sprite, a `stages = 5` over four blocks, a `RANDOM_EVENTS` naming
nothing, an undeclared modifier award and an orphaned event — all six reported,
and the hand-edit guard fired on top of them because the mutation was made in
`stg-build/`.

## What only eyes can grade

Whether the writing sounds like Star Trek and not like a different mod, whether
the 27 pictures match the text under them, and whether six sites at these weights
turn up often enough to notice and rarely enough to stay interesting. None of
that produces a log record. [Open questions](../planning/open-questions.md).
