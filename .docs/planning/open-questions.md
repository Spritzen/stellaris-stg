# What is actually open

> **What** — the questions still live, split by what would settle them: a live
> run, somebody's eyes, or a decision nobody has made yet.
> **Open when** — asking what to do next, or after the user reports a live run
> and you need to know what to look for.
> **Then** — [Live runs](../guides/live-runs.md) · [Status](status.md) · [Phases](phases.md)

Every question the plan originally marked `[OPEN]` is decided, and the
keep-or-drop calls on source mods are closed. The *rule* that closed them is what
carries forward, not the verdicts: **error count is a cost to pay down, not a
reason to drop a mod; sources go on content grounds only**
([decision 11](../decisions/11-fix-source-errors-dont-drop.md)).

---

## Needs a content call

*Three items were opened here on 2026-08-28 while working
[decision 91](../decisions/91-src-contests-its-own-name-lists.md) and its
siblings. **All three are now closed and nothing in this section needs a call** —
it is kept because what closed each one is the reusable part. Two were closed by
making the call ([93](../decisions/93-power-lists-win-the-contested-keys.md),
[95](../decisions/95-colony-pools-drop-home-system-bodies.md)); the third turned
out to have no defect behind it. **The pattern across all three: the blocker was
never the decision, it was a floor nobody had measured yet** — and in two cases
measuring it also corrected the finding's own numbers.*

> **The one that did make `make validate` warn is closed.** Three name-list keys
> were declared twice by files we wrote — `STG_CAITIAN`, `STG_KLINGON`,
> `STG_VULCAN` — and the call was made the same day: **the hand-written power
> list wins all three and the converted duplicates are deleted**
> ([decision 93](../decisions/93-power-lists-win-the-contested-keys.md)).
> `src/common/name_lists/` is now **89 files declaring 89 keys** and the tree is
> back to **0 warnings**.

> **Closed the same day, and the count was wrong**
> ([decision 95](../decisions/95-colony-pools-drop-home-system-bodies.md),
> 2026-08-28). This item recorded *"sixteen home-system bodies are also offered
> as colony names"* across eleven empires and left the content call unmade for
> want of a vanilla floor. Both halves moved.
>
> **The floor exists and it is not vanilla's nine.** STNH, whose home systems
> STG's are harvested from, answers the same question **0 times** across the ten
> of its empires that have both a real home system and a real colony pool —
> **four of them on a 32-body Sol with a 160-name pool**. Vanilla is **0 of 8**
> comparable, its United Nations of Earth being 18 Sol bodies against `HUMAN1`'s
> 59 names with no overlap. STG was **12 of 37**. STNH also shows what the
> convention *is*: home-system bodies go in **`ship_names`** — Starfleet's own
> naming convention — and the only Mars in any of its colony pools is
> `TERRAN_PLANET_NewMars`.
>
> **The count was 17 across 12 empires, not 16 across 11.** The extra one is the
> **Terran Empire's Mars**: its home system is Sol, so the body carries
> vanilla's `NAME_Mars` while the pool offers our `STG_N_Mars` — one name, two
> keys, invisible to the key-wise comparison that produced the sixteen.
> `check_colony_name_collisions` had said in its own docstring since
> [decision 23](../decisions/23-real-home-systems.md) that this class of
> collision is between **values**; the measurement did not read it. **Third
> instance** of [decision 79](../decisions/79-shipset-descs-and-home-system-names.md)'s
> lesson.
>
> **The call was made and applied**: the 17 tokens are dropped from
> `planet_names`, every `ship_names` copy is left alone, and the check now
> carries the question as a third flavour. **Two drafts of it under-reported —
> 11 empires, then 10 — and only reverting the repair caught either**, which is
> [check design rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)
> earning its place: a clean `make validate` would have read as success both
> times.

> **The third quadrant of that hole is closed, and it was empty**
> ([decision 94](../decisions/94-src-contests-its-own-identities.md), 2026-08-28).
> The two contention checks walk one directory each — `src/common/` and
> `src/localisation/` — and `check_duplicate_entities` walks `*.asset` only, which
> left **384 declarations of ours across 11 directories** unasked: `events/`,
> `prescripted_countries/`, `interface/`, `gfx/`, `map/`.
> `check_src_identity_contention` asks the same question there and **`src/`
> contests nothing — 0 findings across 193 identities against vanilla's 11,857.**
> So the shape decisions 91 and 92 found twice is now covered everywhere it can
> occur inside `src/`. **The item below is what is left, and it is a different
> question**: two *sources* contesting a key, not two files of ours.

> **~~`check_key_conflicts` cannot see a contested localisation key~~ — closed
> 2026-08-29** ([decision 109](../decisions/109-two-sources-one-loc-key.md)).
> This item said the widening was *"worth doing when something else touches that
> check; not worth doing alone"*, and the reason it was never one line is now on
> record: `check_key_conflicts` asks its question of `key = { … }` blocks and
> **a localisation file has no blocks**, so there was nothing to widen. It is a
> sibling check, `check_loc_key_conflicts`, the way
> [91](../decisions/91-src-contests-its-own-name-lists.md) and
> [92](../decisions/92-src-contests-its-own-loc-keys.md) are siblings.
>
> **The numbers this item recorded held**: 41 contested keys, 8 differing, all
> Planetary Diversity overriding its own placeholders through its own
> extensions, every one resolving to the extension. The `key_conflict_families`
> filter empties it, and the parser is shared with the sibling rather than
> copied. Population **27,742 keys, 0 findings**, calibrated on four controls.

---

## Mostly answered — the first contact stage alert is one alert for every site

**The 2026-08-28 UFP run reported that first contact stopped notifying part way
through the session**: the sound would play, no alert appeared, and every site
had to be opened by hand to find which one was waiting. It had worked earlier in
the same run.

**The user was asked one question and it settled the mechanism: the game was not
pausing.** `alert_first_contact_stage_done` is `enabled=yes` with
`pausegame=yes` in their own `alert_settings.txt`, so **the alert was never
newly raised** — which rules out the entire UI half of the question. It is not
the alert row's position, not `GFX_alerticons`, not UIOD's `main_alerts.gui`,
not the icon frame. Those were all cleared on disk beforehand and are now
cleared by observation too.

**What is left is vanilla's design, and vanilla's own string says so.** There is
exactly one alert for the whole system:

```
alert_first_contact_stage_done_title:0   "First Contact Event Pending"
alert_first_contact_stage_done_instant:1 "Something has happened in ONE OF the
                                          first contact investigations we are
                                          currently undertaking."
```

It never names the site — *"one of"* is the design. `alert_site_event` and
`alert_espionage_event` are word for word the same shape. An alert that is
already lit raises nothing and pauses nothing when the next one arrives, so the
sound is the only per-event signal left, and **"check them all to find out which
one" is literally the instruction the alert gives.**

**The run makes it a load problem and that part is ours.** The player began
**14** first contacts in 70 minutes and finished **4** — around ten running at
once, and the backlog in `game.log` becomes permanent at 21:19, which is when
the user says it stopped. Archaeology carries the identical alert and nobody has
ever complained, because nobody digs ten sites at once. **STG's galaxy is what
turns a one-alert-per-system design into a defect**: the mod's whole premise is
a crowded, known galaxy, so the player meets far more empires far faster than
vanilla ever asks this alert to cover.

### What is still open, and it is a content call rather than a diagnosis

**Whether to add a per-site signal, and whether one can be added at all.**
Nothing is broken to repair — the question is whether STG should carry its own
notification where vanilla carries a shared alert. Two findings for whoever
takes it:

- **There is no `on_action` for it.** Vanilla declares `on_first_contact`,
  `on_first_contact_started`, `on_first_contact_finished`,
  `on_first_contact_stage_1_no_path` and `on_first_contact_generic_stage_2` —
  and nothing that fires when a stage completes. The obvious hook does not
  exist.
- **The one file in that path we now own is not a safe carrier.**
  `common/inline_scripts/first_contact_event_sounds.txt` is ours as of
  [101](../decisions/101-first-contact-sounds-are-species-class-gated.md) and it
  is spliced into every stage-done event, which looks like a way in. It is not:
  an `immediate` or `after` block added there would sit beside the event's own,
  and `first_contact.350` and `.355` both carry one doing
  `set_site_progress_locked`. Clobbering that breaks first contact outright.

**What a next run could still add**, cheaply: whether the alert icon is
*visibly* lit the whole time. That is the last untested half of the reading
above — permanently lit and ignored, versus never lit at all.

---

## Needs a live run to settle — and all of it is eyes-only

> **Two things built 2026-08-29 that the next run should grade first, because
> both are one glance and both have a falsifiable prediction.**
>
> **1. Is there an AI Federation, and is there exactly one?**
> ([decision 107](../decisions/107-the-ai-federation.md)) The map reserved Sol
> for the Federation and nothing created one; it does now, through a generated
> `inline_script` fragment spliced into Real Space's Earth. **One** in the
> contacts list is the pass. **Two** means the guard did not see the player's
> own country flag — the failure mode `common/prescripted_flags/` exists to
> prevent, and the same one the other 36 empires would show. **None** means the
> include did not take, and the first thing to read is whether `error.log`
> mentions `stg_federation_ai_empire`.
>
> **2. Roughly one anomaly in twelve should be Trek**, up from one in nineteen
> ([decision 108](../decisions/108-anomaly-weights-not-levels.md)). All 33 spawn
> weights were raised `1 → 2`, `2 → 3`, `3 → 5`, taking the 21 Trek categories
> from 5.3% of the merged pool's spawn weight to 8.3% against a fair share of
> 8.4%. Survey a few dozen bodies and count how many of the anomalies carry
> `stg_` names. This is the rare item on this page that a run can **falsify**
> rather than merely observe.


**A reference that resolves produces no log record.** `make validate` clean is not
evidence for anything in this section — the standing lesson of decisions
[07](../decisions/07-stnh-art-shadows-vanilla.md) and
[40](../decisions/40-event-picture-geometry.md).

> **The Federation run of 2026-08-10 and the Vulcan run of 2026-08-22 answered
> most of this section between them**, and several items now have a confirmed
> cause on disk rather than an eyes-only question — so the thing to do next is
> *grade a fix*, not re-diagnose. Both runs' write-ups have since been retired;
> what each established is stated in full in the decision it produced, and the
> items below name them.
>
> **Both planned runs ended before the long half of their plan.** The dig sites,
> the anomalies, the story events and every hull above corvette are **unreached
> in every run since**, which is unmeasured, not negative. The long runs of
> 2026-08-24 onward had **no run plan and no analysis**, and reported only what
> the empire-spawn investigation records, so they add nothing here either:
> **the next run's first job is a plan, then length.**
>
> **The three questions the Vulcan run opened are all closed** as of 2026-08-22
> ([decision 79](../decisions/79-shipset-descs-and-home-system-names.md)) and
> none of them needed a live run or a content call. Two were mechanical and both
> were **larger than the analysis recorded** — 30 shipset description keys wrong
> rather than 7, and seven duplicate body names from three separate generator
> bugs rather than one paste. The third, the six cultures with no city art, was
> **not a defect at all**: `fallback` is the mechanism and vanilla's own header
> says so. See "Confirmed on disk" below.

### Starbase modules on the two tiers that were remapped

**Added 2026-08-28, by
[decision 100](../decisions/100-starbase-slot-tables-outrun-the-art.md).** Every
module past the third on a starport, past the fifth on a starhold, and past the
third and fourth on orbital ring tiers 1 and 2, used to attach to nothing and
render nowhere; they now share a hardpoint with an earlier module instead. That
is strictly better than invisible and it is **not the same as right**: six
modules over two hardpoints on a starport may read as overlap.

**What to look at:** build a starport and fill its six module slots, then the
same on a starhold and on a tier-1 orbital ring. Modules bunched or clipping
into each other is the failure; modules spread around the ring is the pass. 16
starports, 16 starholds and 40 rings share the fix, so one of each grades all
72. `make validate` clean says only that the locator now exists.

### The first contact sting for 129 species

**Added 2026-08-28, by
[decision 101](../decisions/101-first-contact-sounds-are-species-class-gated.md).**
Every first contact in the game played `event_first_contact_aquatic` because no
block in vanilla's list matched a Trek species class. All 129 are now mapped,
and the mapping is a made content call — the Kobali are a necroid, the Bynars a
machine, the Sheliak a plantoid.

**What to listen for:** whether the sting fits the species. The cheap half is
free and needs no ears at all — **`error.log` should carry zero
`Failed to pick an event sound` records**, against ten in the run that found it.

### The galaxy picker — answered 2026-08-28, half by eye and half from disk

**Closed.** [Decision 88](../decisions/88-lock-the-galaxy-picker.md) asked two
things: does the setup screen come up with *The Known Galaxy* already selected,
and is it the only choice.

- **Preselected: yes, seen in the 2026-08-28 run.** That is the half no check
  could reach, and it also rules out the failure mode 88 named — *a galaxy list
  the engine finds empty* — because an empty list cannot preselect anything.
- **Only choice: yes, and this half never needed eyes.** Seven files reach
  `map/setup_scenarios/` after shadowing and **six of them declare nothing** —
  our five picker-lock overrides plus vanilla's own `static_galaxy_example.txt`,
  which is entirely commented out. One declaration reaches the engine,
  `STG_galaxy_alpha_beta`. There is no other directory: `/stellaris/dlc` has no
  `setup_scenarios`, so the path is the whole population.

> **Half of what was filed as eyes-only was a disk question wearing a screen's
> clothes.** 88's own rule — *a scenario is offered because a file at that path
> declares it* — makes "is it the only choice" countable, and the helper written
> for `check_galaxy_size_references` counts it on every run. **Say which half of
> a two-part question actually needs the game before spending a run on it.**

### Two orbital-ring modules whose art is a guess

[Decision 99](../decisions/99-starbase-modules-name-sections-too.md) repointed
Starbase Extended's `orbital_ring_shield_module` and `orbital_ring_armor_module`
at `SOLAR_PANEL_ORBITAL_RING_SECTION`, because the sections they named are
declared in no file anywhere — not vanilla's, not SBX's, not any source in
`.source/`. **The repair is sound and the art is a guess**: nothing in either
tree records what SBX meant them to look like.

**What to look at:** build a shield or an armor module on an orbital ring and
see whether the segment reads as defensive plating or as an obvious solar panel.
If it reads wrong, changing it is one word twice in `vendor.yml`. Note that this
is a *new* thing to look at rather than a regression — before the repair the
engine found no section at all for either module.

### Whether the prescripted pool can ever be drawn from — six galaxies, six times zero

**This is the biggest open question in the project and the only one that has
survived three fixes.** The 2026-08-26 Vulcan run was the **sixth** galaxy with no
Trek AI empire in it. The player met every empire in it. **Not one of the 18 was
Trek.**

**It is also the first run since 2026-08-22 to leave a save on disk, and that
save closed half the question** —
[decision 83](../decisions/83-design-database-is-not-the-cause.md). `ironman` is
off now, so keep it that way.

> **The question below is framed wrongly and is kept only for its measurements.**
> Everything under it asks *why is the lottery not drawing*. The answer is that
> the lottery is not how a total conversion places AI empires at all: they are
> **created by their home system's initializer**, which a **static galaxy
> scenario** puts on the map — vanilla's own `com_sol_system` does it for the
> United Nations of Earth, and STNH does it 43 times
> ([85](../decisions/85-create-country-initializers.md),
> [84](../decisions/84-static-galaxy-is-the-mechanism.md)).
>
> **The work is planned in
> [static-galaxy-plan.md](static-galaxy-plan.md). Go there.** What stays live
> below is the narrower question of whether the prescripted *pool* can ever be
> drawn from — it still matters for the player's roster, and `randomized` is
> still its suspect — but it no longer gates whether the galaxy is Trek.
>
> **And the mechanism has now run, and it works**
> ([86](../decisions/86-static-galaxy-scenario.md),
> [87](../decisions/87-static-map-lanes-are-generated.md)): a 95-system static
> map with 21 empires on their canon positions, 36 `create_country`
> initializers, and the `common/prescripted_flags/` join that lets an
> initializer tell "nobody is playing this empire" from "the player is". The
> 2026-08-27 Klingon save holds **20 AI Trek empires, one each, no duplicates**,
> and no randomly generated empire at all. **The galaxy is Trek.** That is the
> question this whole page was built around, and it is answered.
>
> **What that run also found was a galaxy with one hyperlane in it** — the map
> declared none and nothing built them. Fixed and regenerated (162 lanes).
>
> **~~Not yet run with lanes~~ — run 2026-08-29, and the lanes work**
> ([106](../decisions/106-sealed-system-is-vanilla-content.md)). **99 of 100
> systems are reachable from Sol by hyperlane**; degree min 2, max 5, **mean
> 3.45** over the 95 scenario systems, no isolated component, and **zero
> `spawn_system` failures** against three the run before. The one unreachable
> system is vanilla's **Sealed System** — `isolate_system = yes`, reached by a
> wormhole pair, working as designed and reported from the run as a suspected
> defect. **You can fly out of Qo'noS.** That was the top item on this page and
> it is answered; the picker lock is not. **The AI Federation is, as of
> 2026-08-29** ([decision 107](../decisions/107-the-ai-federation.md)) — the
> map had reserved system `0` for it and nothing created one, because Sol is
> Real Space's file and no `src/` file can add a line to a block another mod
> declares. It is built and unrun: **one glance at the contacts list asks
> whether there is an AI Federation in the galaxy, and exactly one.**

That does not falsify the `playable` fix — the gate it removed was real and had
to go — but it does say the gate was **not the whole cause**. Both levers are now in and
neither moved the number:

| lever | in since | what the run says |
|---|---|---|
| `CUSTOM_EMPIRE_SPAWN_CHANCE = 1000` — 100% of AI slots draw from the prescripted pool | 2026-08-24 | **three** galaxies at 100%, zero drawn. At 100% the die roll is not the variable |
| `playable = stg_never` removed from the minors, so they load into the design database | 2026-08-25 | pool went from 22 to 100 designs. Still zero |
| — | 2026-08-26 | **the save proves the pool is right**: 99 `design=` blocks, `spawn_enabled=yes` on each, and 1 of 77 countries prescripted. The database is not the cause ([83](../decisions/83-design-database-is-not-the-cause.md)) |

**Verified on disk after the run**, so none of these is still a candidate: the
build under test was stamped 16:56:28 and the run started at 18:02, so it
carried both fixes; `stg_defines.txt` sets `CUSTOM_EMPIRE_SPAWN_CHANCE` in
`NGameplay`, the namespace vanilla declares it in, and no defines file sorting
after it in the merge contests the key; all 99 empires are `spawn_enabled = yes`
bar the Federation's `always`; no two of them name the same `initializer`; every
DLC is installed and none disabled; and `error.log` has nothing in it about any
of this, before or after init.

#### What vanilla does, and the one thing every STG empire does that vanilla never does

Cross-tabulating the 51 vanilla prescripted empires that declare
`spawn_enabled` — read `/stellaris/prescripted_countries/` and follow each
`initializer` to its `usage`:

| | no initializer, or a reusable one | a unique, identity-bearing home system |
|---|---|---|
| `spawn_enabled = yes` | 33 | **0** |
| `spawn_enabled = no` | 9 | **9** |

The nine are vanilla's marquee empires and nothing else: the **United Nations of
Earth**, the **Commonwealth of Man** (each twice, base and variant), the
**Gundersen Research Society**, the **Federated Theian Preservers**, the **Blooms
of Gaea** and the **Earth Custodianship** — on `sol_system_initializer`,
`deneb_system`, `vela_system` and `titawin_init` between them. **Every one is
`spawn_enabled = no`, and it is exactly the set of empires players complain never
turn up as AI.** The six empires that carry an `initializer` and are not in that
set all name an *origin* initializer — `ocean_paradise_start`,
`toxic_knights_start`, `red_giant_start`, `mindwarden_system_init`,
`custom_starting_init_01`/`_02` — a reusable system *shape* rather than a named
place, and five of the six are `spawn_enabled = yes`.

**Vanilla never ships a prescripted empire that both owns a named home system
and can spawn as AI.** 37 of STG's 99 do, including all 22 of the majors,
quadrant and frontier powers, and that is
[decision 23](../decisions/23-real-home-systems.md) working exactly as intended:
40 Eridani with Keid and T'Khut, Qo'noS with Boreth, Romulus with Remus. The
community advice on the same symptom says the same thing from the other end —
*set every custom empire's starting system to Random* — and the engine's own
`AI_EMPIRE_PREVIEW_TOOLTIP_INCOMPATIBLE_SYSTEM` string shows it has a concept of
starting systems that lock each other out.

**The hypothesis was written down in 2026-08-10 and ruled out on a miscount.**
The 2026-08-10 Federation remediation plan's item 4 carried an elimination table
with the row *"Excluded because their home systems are hand-placed — 23 of
vanilla's own 33 spawn-eligible empires also carry an `initializer`, and those
spawn as AI routinely — **Ruled out**"*. That counted the `initializer` **line**.
**18 of those 23 are `initializer = ""`.** The real figure is 5 of 33, all five
origin initializers. So the one hypothesis that would explain five empty galaxies
has been sitting dismissed for a fortnight on a number that was never true:

```bash
grep -c 'initializer = ""' /stellaris/prescripted_countries/*.txt
```

**There is a competing reading of that same table, and it is not weak.** All
nine are Earth-and-human variants from `00_top_countries.txt`, and five of them
start on Sol. Paradox may set `spawn_enabled = no` on them because a galaxy with
three Earths in it is bad *flavour*, not because the engine cannot place them.
The table cannot tell those two apart on its own — what it establishes for
certain is only that **vanilla ships no example of the thing STG does 37 times**,
so there is no positive evidence anywhere that the combination works.

**And the reading has a hole, which the 2026-08-26 save turned from a doubt into
a result.** 62 of the 99 designs carry no `initializer` at all. On the
initializer theory those 62 were free to spawn and none did. That left two
readings — they were still not in the design database, or the cause is something
else again — and **the save settles it: all 99 are in the database**
([decision 83](../decisions/83-design-database-is-not-the-cause.md)). It is
something else again. The initializer theory survives only as a *second* filter
over the 37 that do carry one; it cannot reach the other 62, so it is no longer
a candidate for the whole cause.

#### What is left to do, in order

**1. There is no UI test — the force-spawn button is player-made-only.**
Confirmed at the UI by the maintainer, 2026-08-26, against a same-day
recommendation here that said otherwise on the strength of vanilla's loc strings
saying "empire **template**". `spawn_enabled` in script is the only forcing lever
STG has. Build a test instead: **`randomized = yes` on three major powers'
species classes only**, everything else left at `no`, and one galaxy separates
"the draw is the problem" from "the engine will not place these at all" —
[decision 84](../decisions/84-static-galaxy-is-the-mechanism.md).

**1b. The AI empire preview, before generating anything.** The galaxy setup
screen previews the AI empires that will spawn; vanilla ships tooltips for
`AI_EMPIRE_PREVIEW_TOOLTIP_RANDOM` ("Random AI Empire"),
`..._TOO_MANY_FORCED` and `..._INCOMPATIBLE_SYSTEM` ("The following empires have
incompatible starting systems, so only one of them can appear"). If the preview
shows 18 *Random AI Empire* slots, the generator never consults the pool. If it
shows Trek empires and the galaxy does not contain them, the question is
placement. **One glance, before pressing start.** The database half of what this
used to discriminate is now closed
([83](../decisions/83-design-database-is-not-the-cause.md)), so this glance now
answers the whole of what is left, and it is the only cheap thing still
outstanding.

**2. A save — done, and keep doing it.** The 2026-08-26 run left two on disk and
they closed half the question in minutes. `settings.txt` no longer carries
`ironman`, so saves land in `save games/<empire>_<id>/` by themselves. **Do not
turn ironman back on while this is open.** The one trap:
`design={…}` blocks are nested inside `galaxy={…}` with the brace on the
following line, so an earlier `grep 'design={'` finds zero in a 4.4.6 save —
match `^\tdesign=$` instead.

**3. The `randomized` question, which is now stronger than it was.** Vanilla is
32 of 33 spawn-eligible prescripted empires on a *randomizable* species class;
STG is 0 of 99. The STNH counterexample that was against it **fell** — STNH's
Trek galaxy comes from static maps, not from its prescripted pool, so the pool
was never under test there
([84](../decisions/84-static-galaxy-is-the-mechanism.md)). What remains against
it: vanilla's own `mindwardens`, and the fact that the fix is not one line —
vanilla ships a `common/species_names/` entry for every class it randomizes and
STG ships none. Community material names the same mechanism and names
`non_randomized_portraits` alongside it, which catches **three** STG empires on
the `human` portrait, the Federation among them. Both sides in
[83](../decisions/83-design-database-is-not-the-cause.md) and
[84](../decisions/84-static-galaxy-is-the-mechanism.md).

**4. ~~The static galaxy scenario~~ — built 2026-08-27, run the same day, and
it works.** Not a fallback — the mechanism.
[Decision 86](../decisions/86-static-galaxy-scenario.md) has what shipped and
what was deliberately absent from it — **the AI Federation is no longer, as of
[decision 107](../decisions/107-the-ai-federation.md); the Terran Empire still
is, and deliberately** —
[decision 87](../decisions/87-static-map-lanes-are-generated.md) has what the
run returned: 20 AI Trek empires created, the flag guard firing, and a galaxy
with no hyperlanes in it because the map declared none. The lanes are generated
now and want one more run. **Since 2026-09-01 there are three
sizes of it** — 95, 600 and 1,000 systems from the one generator, the last two
matching vanilla's own `medium` and `huge` on star count and radius
([111](../decisions/111-three-galaxy-sizes.md)); only the smallest has ever been
run, so a run on the 1,000-system map is the new open half of this item. Items 1, 1b and 3 above are all about the *pool*, and
the pool no longer gates the galaxy — do them after that run, not before it.

#### What not to do yet

**Do not strip the `initializer` lines.** It is the change the vanilla table
points at, and it would cost decision 23 in full — the real home systems are one
of the most visible things in the mod, and the last run confirmed 40 Eridani
reads correctly. **The 2026-08-26 save strengthened this, not weakened it**: 62
of the 99 designs carry no `initializer` and were not drawn either, so stripping
the other 37 could not have reached most of the pool anyway
([83](../decisions/83-design-database-is-not-the-cause.md)).

### Devastated Trek city sets — six sets, no `_devastated` art

**None of STNH's six Trek city sets ships the `_devastated` layers every vanilla
set has.** `vulcan_01`, `klingon`, `cardassian_01`, `borg_01`, `tholian_01` and
`undine_01` have none; `humanoid_01`, `avian_01`, `reptilian_01` and
`molluscoid_01` have five each.

**No check can ask for them and no log will name them.** The engine composites
these purely by naming convention — there is no `.gfx` or `.gui` declaration for
a city set anywhere in vanilla or in UIOD — so nothing in the tree references
them and the reachability closure sees nothing missing.

What to look for: **bombard a Trek homeworld, or let a crisis devastate one, and
open the planet view.** The question is only whether the engine falls back to
the intact layers or draws nothing. If it falls back cleanly this is not a
defect at all; if it draws nothing it is a content gap and the fix is art, which
is a call nobody has made.
[Decision 81](../decisions/81-city-horizon-band.md), "What this does not fix".

### The shipsets' weapons

Whether the Walshicus shipsets draw their weapons — 17 of the 22 majors,
quadrant and frontier powers fly one — and whether the pruned event pictures
took anything visible with them.

Then the weapon-mount re-derivation
([57](../decisions/57-mounts-share-existing-points.md),
[64](../decisions/64-source-art-hardpoint-names.md)) across all 27 shipsets — the
thing to look for is a mount that no longer breaks the pattern of the ones beside
it, and, on the 66% still placed from the bounding box, whether any of them reads
as badly as the corvette's third gun did.

> **Three shipsets graded, all on the corvette: Klingon and Cardassian
> 2026-08-08, Vulcan 2026-08-22.** The user reports the mounts on the
> Bortas-class, the Hideki-class — all three of the latter — and the Vulcan
> corvette as well placed. Three of 27, and the corvette is the hull class the
> original defect was found on, so these are the strongest single checks
> available rather than a sample of the rest. **24 shipsets still ungraded.**

> **The corvette was the only hull that could have graded well.** The
> 2026-08-10 run reported the Federation destroyer's stern mounts as plainly
> wrong, and the log gave the reason: **132 hulls across all 22 Trek shipsets were
> missing the section attach points their `ship_size` names**, so those sections
> never attached and their guns were placed against nothing. A corvette needs only
> `part1` and so was never affected — which is why three corvette gradings in a
> row looked like evidence about the shipsets.
>
> **Fixed the same day** — 230 attach points over 100 files
> ([77](../decisions/77-hull-section-attach-points.md)) — and **nothing about it
> is confirmed in game after six runs.** The 2026-08-22 run flew corvettes and
> science ships only. The 2026-08-24 run played ~7 hours and its `error.log`
> carries **zero** `has no attach point` records against 2026-08-10's eight —
> **suggestive and not confirmation**, because nothing in that log or in its one
> write-up says which hulls were flown, and a hull nobody built logs nothing
> either way.
>
> **The 2026-08-28 UFP run carries four, and they say nothing about the hulls.**
> They are `starbase_starport`, a family decision 77 never touched and the check
> was never scoped to: Starbase Extended sizes every starbase tier's slot table
> off the citadel's, so the smaller tiers name attach points vanilla's art does
> not carry. **72 entities**, swept and remapped
> ([100](../decisions/100-starbase-slot-tables-outrun-the-art.md)). The hull
> question is exactly where it was. Grading the mounts above corvette is now a live question rather
> than an unanswerable one, and it is the single most valuable unmeasured thing
> in the project.
> Recorded as item 1 of the 2026-08-10 Federation remediation plan. The check
> that now guards the repair is [78](../decisions/78-widen-attach-points-and-two-new-checks.md);
> a clean check only says the locators exist.

### The ruler clothes

The plainest form this question has ever taken: **the president in a Starfleet
formal robe, the Vulcan councillor in her white robe, the Terran empress in the ENT
mirror coat** — each empire in exactly the garment its `game_setup` row names, with
no index between the two.

If any one of them is still wrong, the one-texture selector is not being reached at
all and the portrait clone is the thing to doubt, not a number.
[Decision 65](../decisions/65-ruler-clothes-dedicated-selectors.md), which
falsified the earlier index model.

> **Answered for Vulcan, 2026-08-22: T'Pau draws in a Vulcan civilian robe.**
> The dedicated one-texture selector is reached, which is the clean test
> [decision 65](../decisions/65-ruler-clothes-dedicated-selectors.md) was waiting
> for. **The president and the Terran empress are still ungraded** — different
> empires, different selectors, and a Vulcan run says nothing about either.
>
> **The malformed paths behind the 2026-08-10 "president is still wrong" report
> are now all gone.** 29 rows were patched that day in the *male* master
> selector; the **female** master was never touched and still held eleven, which
> the Vulcan run logged three of. All eleven landed 2026-08-22 and
> `check_selector_texture_paths` holds the tree at zero
> ([78](../decisions/78-widen-attach-points-and-two-new-checks.md)).
>
> **The caveat that used to sit here is closed.** The same sweep found selector
> rows pointing at textures that exist in no source mod at all, recorded as 196
> and each believed to need a content call. **Measured 2026-08-24 the population
> was 117 rows — vanilla had been left out of the resolution set — 76 of them
> needed no call at all, and the remaining 41 took one policy rather than
> thirteen decisions.** Every row now resolves, and
> `check_selector_texture_files` holds it there, so a ruler that still looks
> wrong is no longer explained by a missing garment.
> [Decision 80](../decisions/80-selector-textures-that-resolve.md); opened as
> item 2 of the 2026-08-10 Federation remediation plan.
>
> **And the clothes-slider wrap is arithmetic, not a defect.** The designer's
> slider runs to 499; the male pool is 495 wide and the female 472, so
> 496–499 address nothing — exactly the range the 2026-08-10 run named.
> **Prediction the next run can falsify in a minute: on a female portrait the
> wrap begins at ~472, on a male at ~496.** Measured for the 2026-08-22 Vulcan
> run.

### The 2026-08-08 warning triage

Six `vendor.yml` renames changed which declaration the engine is left with, and a
rename that works produces no log record. The 2026-08-10 run graded one half —
**nebula sizing on the galaxy map is correct**. What is still unseen: whether
habitats draw as vanilla's orbital ring rather than a Suliban helix.
[Decision 50](../decisions/50-duplicate-entity-triage.md).

### Music

**Closed 2026-08-10, by measurement rather than by a change.** The anthem is in
rotation ([52](../decisions/52-federation-anthem.md)) and the track names are all
distinct ([58](../decisions/58-music-player-track-names.md)). Nothing in the tree
needed fixing; the *expectation* did.

> **The two figures count different things, and a run plan must carry both.** The
> player lists **55 declarations**; the rotation is **27 playlist entries**,
> reproducing [decision 62](../decisions/62-music-rotation-dedupe.md) exactly. A
> run reporting "approx. 70 tracks" is eyeballing the 55. Recorded as item 6 of
> the 2026-08-10 Federation remediation plan.

What is still ungraded by ear: whether the four chosen main-theme titles sit
right beside the eighteen derived ones.

### Ship registries and their class names

Whether the Trek registries read right on the right hulls, and whether the class
names fold by the same tonnage table without leaking across empires.
[Decisions 56](../decisions/56-ship-name-pools.md),
[67](../decisions/67-ship-class-names.md),
[68](../decisions/68-class-name-thematic-fill.md). Five things to watch, in
descending order of how obviously they would be wrong:

- **A Nebula-class name on a corvette.** The tonnage table is a judgement and
  this is how it fails. The class half is the easier of the two to catch by eye:
  *Nebula – Interceptor* is one glance.
- **Whether the Klingon and Romulan lists read as their own.** The fuzzy join
  that would have put Saber, Steamrunner and Sovereign in the Klingon fleet was
  deleted before it shipped; this is a check that nothing else does the same.
- **Whether the invented English sits beside the canon names.** Decision 68
  filled the empty tiers from vanilla's own second idiom (NEC4's vices, AQU1's
  water), so what to look for is `Stormwall` next to `Bolarus` and `Escrow` next
  to `Jaglom Shrek` — and whether the Xindi species names read as classes or
  just as species labels. **All 22 of the majors, quadrant and frontier powers carry all
  five core tiers**, against 13 when decision 68 was written.

  > **The Caitian `titan` exception is withdrawn**
  > ([decision 93](../decisions/93-power-lists-win-the-contested-keys.md),
  > 2026-08-28). It was carried here from 2026-08-22 as *"the gap is Caitian,
  > which has no `titan` block"*, and it was measured against
  > `stg_minor_caitian.txt` — **one of two files then contesting `STG_CAITIAN`**,
  > and not the one anybody intended to ship. `stg_caitian.txt` carries all five
  > tiers and is now the only one there is. A Caitian titan draws a Caitian class
  > name, so there is **no empire where a tonnage-mismatched class name is
  > expected rather than a defect** — which makes this bullet easier to grade,
  > not harder.
- **Whether the Defiant showing at two tonnages** — destroyer and cruiser, which
  is STNH's own modelling — reads as wrong or as fine.
- **Whether any list draws a class name plainly belonging to another tonnage**,
  which would mean a `generic` token escaped demotion.

> Two things left standing on purpose. **Malon's inherited pools name a type, not
> a class** — STNH declares `Waste Extraction Cruiser`, which will read as *"Waste
> Extraction Cruiser – Interceptor"*; it is a source's content, so it is flagged
> rather than cut. And **the 46 minors on generic shipsets stay generic-only**, where
> `generic` is drawn 100% of the time and thin is not broken.

### The Trek anomalies

**21 categories, 27 outcome events, 24 pictures, 123 loc keys and ~3,500 words**,
none of which any check can grade
([decision 70](../decisions/70-trek-anomalies.md)). Three separate questions, and
they fail differently:

- **Does the writing sound like Star Trek, or like a different mod?** The
  register is a survey officer's report, which is vanilla's own — so what to
  watch for is a description that reads as a *plot summary* of an episode rather
  than as something a science officer wrote.
- **Does the picture match the text under it?** All 24 were looked at before
  they were chosen, and two rejected on tone. **Nine of the 24 are frames
  extracted from a 9315×264 animation strip**, and a wrong frame is the failure
  mode there.
- **Do the rewards feel right?** An anomaly level gates which scientist can
  crack it and how often the roll fails, and the mapping is a judgement.

  > **The levels half of this item is closed, and the yardstick under it was
  > wrong** ([decision 108](../decisions/108-anomaly-weights-not-levels.md),
  > 2026-08-29). It used to read *"vanilla puts 65% of its base-game categories
  > at level 1–2 and 10% at level 5+; STG puts 19% and 43% … early-game
  > scientists will bounce off it."* Both STG figures are right. The comparison
  > was to vanilla's **base-game 40**, and the pool a survey actually draws from
  > is **327**: **37.4% at level 1–2 and 24.2% at 5+**, mean 3.28 against STG's
  > 3.86. Half the gap was the yardstick.
  >
  > **And the half that is left costs two points.** Weighted by the spawn weight
  > each category carries — what a player meets, rather than what a file lists —
  > the merged pool sits at **27.4%** of weight at level 5+ against vanilla's own
  > **25.2%**. The Trek set is 8% of the pool, so its lean moves the galaxy by
  > 2.2 percentage points. **The levels were deliberately left alone**: a level
  > is content, an Iconian gateway is meant to be beyond an early scientist, and
  > flattening the curve would cost the set its character to buy back a
  > difficulty the player does not experience as Trek's.
  >
  > **What the same measurement did find was the weights, and they moved.** The
  > 21 categories held **5.3% of the merged pool's spawn weight for 7.2% of its
  > spawnable categories** — under fair share in *every* body class by the same
  > factor, medians vanilla 3.0 and STG 2.0. All 33 `add` values were remapped
  > `1 → 2`, `2 → 3`, `3 → 5` and the set now sits at **8.3%**. **A live run can
  > falsify it in a few dozen surveys: roughly one anomaly in twelve should be
  > `stg_`, up from one in nineteen.**

> **And the framing question underneath all three.**
> [Decision 69](../decisions/69-event-picture-families.md) centre-crops these
> pictures from 620×264 to 450×150, losing 21 px top and bottom. For the 569
> that shadow a vanilla path that crop was verified against the vanilla scene
> they replace; **the anomalies' 24 shadow nothing, so there is no control** —
> twelve were looked at and read correctly, which is a sample. A subject cropped
> at the chin is what it would look like. The archaeology's 27 and the story
> events' 21 were each looked at in the exact crop before being chosen
> ([71](../decisions/71-trek-archaeology.md),
> [72](../decisions/72-trek-story-events.md)), **so if a framing problem shows
> up, the anomalies' 24 are where to look first.**

### The Trek archaeology

**6 dig sites, 27 stage events, 27 pictures, 117 loc keys and ~3,800 words**
([decision 71](../decisions/71-trek-archaeology.md)). The writing and picture
questions above apply here unchanged. Three that are specific to a dig:

- **Do they turn up at all?** This is the one question a live run answers
  cheaply and nothing else answers. The sites spawn through `ancrel.9999` on
  `on_survey_planet`, at vanilla's own 5-in-405 roll, weighted on planet class —
  so the test is whether a dig site appears in the situation log over a few dozen
  surveys, and whether more than one of the six ever shows in one galaxy. If
  **none** appears, the weights are the thing to doubt, not the content.
- **Does a five-stage dig hold up over the hours it takes?** An anomaly is one
  popup; a site is four or five, spread across a scientist's career. The failure
  mode is a middle stage that reads as filler between the hook and the payoff.
- **Do the finale choices feel like choices?** Five of the six end on two options
  with different modifiers — take the blade or seal the hall, return the ark or
  keep reading it, wake the mechanism or backfill the shaft. If one side is
  obviously correct every time, it is not a choice, it is a tax.

### The Trek story events

**21 events, 21 pictures, 84 loc keys and ~4,000 words**
([decision 72](../decisions/72-trek-story-events.md)). The writing and picture
questions above apply here unchanged. Four that are specific to a story event:

- **Do they fire at all, and at the right rate?** The pool is calibrated against
  vanilla's own 18.6% per five-year pulse, and `stg_recent_story` blanks the
  pulse after a hit, so the long-run figure is ~17% for the Federation and ~13%
  for an ungated empire — roughly one story event per decade per empire
  ([73](../decisions/73-phase-4-count-corrections.md) has the three tiers). If
  **none** appears in a long game the thing to doubt is the hook, not the
  weights: a custom on_action reached only by `fire_on_action` is exactly the
  arrangement `check_story_events` was written to police, and a check that has
  never failed in the live game is not yet evidence
  ([check design rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)).
- **Does the right empire get the right story?** Twelve are gated on species
  class. A Klingon empire seeing the Federation Council, or a Federation empire
  seeing none of its own two in a whole game, are the two ways the gate is
  wrong, and they fail in opposite directions.

  > **And a third way, which is not a broken gate and would not read as one:
  > eleven of the 22 majors, quadrant and frontier powers are outside the gate entirely** — BOL, BRE,
  > THO, CAI, XIN, SUL, YRI, KRE, MAL, VID and the mirror **TER**, plus all 77
  > AI minors. They see only the eight open events. **A Malon player reporting "I
  > never see my own story" is reporting the content, not the gate**, so ask
  > which empire before doubting the trigger. Left open as a content gap;
  > growing the pool is cheap, because `random_events` fires exactly one winner
  > ([73](../decisions/73-phase-4-count-corrections.md)).
- **Does a five-year flavour popup read as texture or as interruption?** This is
  the one question the anomalies and dig sites do not raise, because those are
  answers to something the player did. A story event arrives unbidden. If it
  reads as a tax on the pause key the weights are too high, and `1200 = 0` is
  the one number to move.
- **Does the register hold at country scope?** The dig sites are a survey
  officer's report; these are a service dispatch, written from inside an
  institution. The failure mode is a description that reads as a narrator
  summarising an episode instead of a civil servant writing a minute.

### Answered by the runs of 2026-08-08

Kept as one line each, because the *shape* of the answer is what transfers; the
finding itself is in the decision.

- Rooms and hidden empires — all four hidden empires are back and the designer's
  room list is *"realistically over 300"*
  ([46](../decisions/46-room-selector-merge.md),
  [59](../decisions/59-city-set-cultures-undeclared.md)).
- Star names **append** rather than replace, confirmed by the three-way mix on
  the galaxy map — the property, not the total, is what carries: STG's 806 names
  add to Real Space's and YAGEM's 5,702 rather than displacing them
  (the Trek star-name harvest, correcting
  [42](../decisions/42-random-names-pools-append.md)).
- The Vulcan city framing needed no change (2026-08-08) — **falsified
  2026-08-24.** It needed a change on the axis that review ruled out: the
  skyline filled 325 of 400 rows against a family median of 289, and UIOD's
  window cut the top 33 off. That review measured the canvas three ways and
  never measured the *content*
  ([81](../decisions/81-city-horizon-band.md)).

---

## Confirmed on disk — all three worked, and one was not a defect

*[Decision 79](../decisions/79-shipset-descs-and-home-system-names.md), 2026-08-22.
This section held three items each described as needing somebody to decide what
the right answer was. **None of them did.** Two were mechanical once measured
properly and both turned out larger than recorded; the third dissolved on
reading vanilla's own file header. The section is kept, rather than deleted,
because the pattern is the lesson: **each had been measured once, and each
measurement stopped one question short of the mechanism.***

- **The shipset descriptions — fixed, and it was 30 of 30 rather than 7.**
  Seven keys named a *city-set* culture instead of a *shipset* one and 23 flown
  cultures had no key at all, so every Walshicus set — the Federation's own
  `starfleet_tng` and the Vulcans' `vulcan` included — drew a raw key. Seven
  renames plus sixteen new descriptions, the new prose grounded in the hull
  textures rather than in lore. `check_shipset_descriptions` now asks both
  directions; vanilla's floor is **0 and 0**, while vanilla keys only 20 of its
  52 declared cultures — **flown is the population, declared is the bound.**
- **The 40 Eridani duplicate — fixed, and it was three bugs in six systems.**
  Recorded as *"small, certain, one edit"*; swept across all 37 generated home
  systems it was **seven duplicate names from three unrelated causes** — a
  `sub_blocks` that matched at every nesting depth, a star/capital de-collision
  rule blind to the bare `star` keyword, and STNH naming both moons of S'latas
  alike. All three fixed in `tools/gen_home_systems.py`, because the file is
  generated. `check_home_system_body_names` guards it: vanilla fails the
  question **62 times in 357** initializers overall and **0 times in 9** home
  systems, which is where the scope comes from.
- **The six cultures with no city art — NOT A DEFECT, and no call was needed.**
  Vanilla's own `00_graphical_culture.txt` says in its header that `fallback`
  lets the game use another culture's asset when one is missing, and all six
  declare `fallback = mammalian_01`. **24 of vanilla's own 52 declared cultures
  ship no city art either** — 46%, so the premise could never have been the
  rule. `check_graphical_culture_art` asks the invariant that does have a floor
  — an offerable culture reaches art, its own or its fallback's — and vanilla is
  0 of 22 with STG 0 of 41. The orphan `generic_01`–`generic_06` art is
  `check_unreferenced`'s question and [decision 43](../decisions/43-clutter-pass.md)'s
  standing policy, not a defect.

> **What generalises, and it has now happened twice.** [Decision
> 78](../decisions/78-widen-attach-points-and-two-new-checks.md) struck the
> 2026-08-22 Vulcan run's finding 5 for the same reason this strikes finding 2: **both were measurements taken without reading
> the thing that had already measured them** — a helper in `tools/validate.py`
> in one case, three lines of vanilla's own file header in the other. Before
> writing a check for a finding, read vanilla's header and the check next door.

**What genuinely still needs eyes** out of all this: whether the sixteen new
shipset descriptions read as Trek, and whether the four stars whose colliding
names were dropped now draw with their system's name the way vanilla's twelve
unnamed ones do.

## Log-level leftovers

*Init-window groups that are third-party or reviewed, listed with their share of
the 2026-08-07 run's 1,308 records — the run that triaged them. Counts against
the current build are in the shape table on [status.md](status.md), which is
sorted by the emitting `.cpp:line` rather than by wording.*

- **Duplicate entity declarations — 568 records, and much the largest class in
  the log.** `pdx_entity.cpp:2560`, `Duplicate of <name> added to entity system`:
  a mod redeclaring a **vanilla** entity from a differently-named file, which is
  how a mod overrides vanilla art without shadowing the path. Triaged in
  [31](../decisions/31-duplicate-entity-declarations.md) and
  [50](../decisions/50-duplicate-entity-triage.md), which measured 576 in the
  2026-08-07 run and found **558 of them to be that deliberate idiom**; the
  thirteen that were a real merge contest were repaired or acked there, and
  `check_duplicate_entities` watches for new ones.
  **Listed here for the first time on 2026-08-28, and that is the point of the
  entry.** It is exactly **568 in the 2026-08-08 log, 568 in the 2026-08-10 log
  and 568 today** — an init-window constant across three weeks that both this
  list and status.md's shape triage had left out, while status.md positively
  asserted there was *"nothing above nine"* below the third class. The triage
  existed; the count did not. **A class nobody has written a number for reads as
  a class nobody has looked at.**
- **ASB's projectile reimplementations — 213 records, the largest class left.**
  `alt_*` and `ap_*` in `gfx/projectiles/` redeclare vanilla names and the engine
  keeps one. **Still open: which one renders.**
- **SBX — 67 records**, naming techs from an older Stellaris, plus the only in-play
  findings in that run. SBX also renumbers vanilla's citadel gun slots, breaking
  vanilla's own design ([37](../decisions/37-sbx-citadel-slot-renumbering.md)). Its
  `advanced_military_program` — the one `potential` block in either its file or
  vanilla's that switched to `solar_system` unguarded — is patched as of 2026-08-07
  ([44](../decisions/44-coalition-of-hope-takes-vul.md)).
  **A third SBX defect landed 2026-08-28 and it is post-init, not part of this
  count**: its starbase and orbital-ring sizes all share the largest tier's slot
  table, so the smaller tiers name attach points the art does not carry — 72
  entities, remapped in `vendor.yml` and guarded by `check_slot_table_widening`
  ([100](../decisions/100-starbase-slot-tables-outrun-the-art.md)). Three
  separate defects in one mod, all repaired rather than quoted as a reason to
  drop it ([11](../decisions/11-fix-source-errors-dont-drop.md)).
- **23 `duplicate section template` records — triaged 2026-08-28, and benign
  by measurement.** Starbase Extended ships its sections as `!!!_sbx_3_0_*`,
  `common/section_templates` is FIOS, so SBX takes all 23 keys and each vanilla
  declaration it displaces is logged. **Nothing was open here; nothing had ever
  asked.** The question a replacement actually raises is whether the slot names
  vanilla's own designs mount on survived it — one did not, which was
  [decision 37](../decisions/37-sbx-citadel-slot-renumbering.md) — and the swept
  answer is that SBX's slots are a **superset** of vanilla's in all 23.
  `check_section_slot_references` holds it there: vanilla's floor 0 and 0 over
  6,882 component references, and reverting decision 37's patch recovers the
  same four slots the live log named
  ([96](../decisions/96-section-slots-survive-a-replacement.md)).
- **1,605 `Missing ship size Localization Key` records in `setup.log` — TRIAGED
  AND CLOSED 2026-08-29, and not a defect in anything**
  ([103](../decisions/103-setup-log-is-a-load-manifest.md)). Opened the previous
  day at a count of 1,375, which was two per-second buckets added rather than
  the class counted. They are **321 ship sizes × exactly five suffixes**
  (`build_speed_mult`, `build_cost_mult`, `upkeep_mult`, `hull_mult`,
  `hull_add`), **1,500 of them on sizes only vanilla declares** — and vanilla
  defines that family for **no** ship size at all, its own
  `corvette_build_speed_mult` included. The engine asks every size for a loc
  family the game never ships. The ten keys belonging to Starbase Extended's two
  new starbase tiers are **deliberately left**: answering them would make STG the
  only thing in the game that does. **Do not reopen without new evidence.**
  The same file's `trait.cpp:663` dump turned out to be worth more than the
  error class was — see the decision.
- **143 duplicate textures** where STNH's `shared_assets/` meets Walshicus'
  `stnc_shipset_shared/` — [the conflict register](../architecture/conflict-register.md)
  explains why last-wins is correct here. Now watched by
  `check_duplicate_textures` and acked by directory, so the reviewed library stays
  silent and a *new* collision reports.
- **`legend` — 2 records**, inside vendored Klingon art at
  `gfx/portraits/asset_selectors/klingon/klingon_male_clothes_combined.txt:42,48`.
- **2 `Failed to get section template for key` — fixed 2026-08-28, and they
  were never triaged either.** `ship_design_templates.cpp:480`, SBX's
  `orbital_ring_shield_module` and `orbital_ring_armor_module` naming sections
  declared in no file in any tree. In every log on disk, named by no document,
  and outside the only check that walks that database because
  `check_section_slot_references` asked the ship-design direction and a module
  writes a bare `section = "KEY"` instead. Repaired in `vendor.yml` and the
  check now walks both directions
  ([99](../decisions/99-starbase-modules-name-sections-too.md)).
- **353 `Failed to deferred read key reference … from database` — new on
  2026-08-28, ours, and staying.** The picker lock withdrew the five galaxy
  sizes and `galaxy_size` resolves a `setup_scenario` by name. Acked with its
  price under `galaxy_size_ack`
  ([98](../decisions/98-withdrawn-scenarios-are-referenced-by-name.md)); **the
  ack silences the check, not the engine**, and it empties itself if the sizes
  are ever restored.
- The small defects of that run and what each cost are in
  [decision 38](../decisions/38-live-run-2026-08-07-repairs.md).

---

## Reviewed and deliberately left alone — do not reopen without new evidence

- **Real Space's oversized systems.** `System Mintaka … is too big` is Real Space's
  own initializer against Real Space's own raised threshold, five of its 198
  systems exceed it, and System Scale makes them *smaller*. Changing either the
  geometry or the threshold would be inventing or silencing. STG's own home systems
  top out at 515 and are clear.
  [Decision 34](../decisions/34-oversized-real-space-systems.md).
- **`PLANET_SCALE_SYSTEM` keeps its 8 entries.** The engine measures it against
  `ZOOM_STEPS_SYSTEM`, an array no script can set, and the visual test found
  13-against-8 rendering correctly.
  [Decision 41](../decisions/41-planet-scale-system-length.md).
- **700 report-tier orphans** from the clutter closure (build of 2026-08-24;
  [decision 43](../decisions/43-clutter-pass.md) recorded 706, and `make
  validate` prints the live figure). At vanilla's own 4.9%
  leftover rate in `gfx/models`, a finding there is indistinguishable from
  Paradox's. Widening the prune scope means moving a tier in `tools/clutter.py`
  **with a new ratio written beside it**. [The clutter closure](../validation/clutter.md).
- **`descriptor.mod` declares `"Total Conversion"`, `"Species"`, `"Events"`,
  `"Graphics"`.** Accurate for a vendored merge, and cosmetic since STG is never
  published. Leave it.
- **Nine `Failed to find entity … for attachment` records every run** — five
  Romulan bird-of-prey sections, three Klingon cores, one named `_test_`. Triaged
  in [decision 35](../decisions/35-attach-edges-into-pruned-art.md): STNH art
  whose consumers live in a `common/` STG does not vendor, with a twelve-line
  rationale under `attach_target_ack` in `vendor.yml`. Stable across three runs
  and costing nothing at runtime. **The shape worth keeping: the ack silences
  `check_attach_targets`, not the engine** — nine records a run is its standing
  price — **and it is scoped by *file***, so a genuinely new unresolved attach in
  those four files would also go unreported.
- **The prescripted-power sweep is done and clean.** `stg_minor_powers` shipped
  with 78 of its 79 empire names truncated and 16 loc values that were the loc key
  itself; all 100 are repaired
  ([45](../decisions/45-minor-power-names-truncated.md)). The other three files
  were swept and are clean: **0 leaked loc keys, 0 truncations** across all 22
  empires.

  > The premise behind worrying about them was wrong in a specific way worth
  > keeping: **those three were hand-authored and only the minors were generated**,
  > and truncation is a *generator* failure. "Same hand" describes who chose the
  > content, not what produced the file, and only the second matters for this
  > defect class. [Decision 49](../decisions/49-prescripted-loc-scope.md).

---

## Queued, and deliberately not started

**More Events Mod and its compatch are subscribed for a later integration pass**
— in scope, waiting on this page's eyes-only surface being graded first.
**Only the timing is closed**; which paths are taken and how MEM's events sit
beside Trek ones are the pass itself and are open.
[Decision 75](../decisions/75-mem-integration-deferred.md).
