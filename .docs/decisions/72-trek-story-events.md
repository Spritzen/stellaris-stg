# 72 — Trek story events, and the merge question the design refuses to ask

**Status:** decided, 2026-08-09, and **corrected in part by
[decision 73](73-phase-4-count-corrections.md)** — vanilla has **485** on_action
keys, not the 452 quoted below, and the 21% story rate is the **Federation's
alone**: the other ten gated classes see 17.8% and eleven playable empires see
14.3%. The calibration argument holds; the figures moved. The body is left
exactly as written.
**Follows:** [71](71-trek-archaeology.md)

## What this closes

[Decision 70](70-trek-anomalies.md) split Phase 4's remaining work into
**anomalies first, archaeology and story events after**.
[Decision 71](71-trek-archaeology.md) shipped the second. This is the third and
last, so the scope 75 set is complete.

The starting position was the one both of them found: `stg-build/events/` holds
47 files and not one of them is a country event with a Trek voice in it — the
harvest takes no `events/` from STNH by design
([architecture/stnh-art.md](../architecture/stnh-art.md)). Every word here is
written rather than converted.

## What shipped

| | |
|---|---|
| `src/common/on_actions/stg_on_actions.txt` | **3 hooks**, one of them our own |
| `src/events/stg_story_events.txt` | **21 story events** + a 2-event pulse gatekeeper |
| `src/interface/stg_story_pictures.gfx` | **42 sprites over 21 STNH pictures** |
| `src/localisation/english/stg_story_l_english.yml` | **84 keys, ~4,000 words** |

Twelve of the 21 belong to one people and are gated on species class — the
Academy and the Council (FED), the road to Gol (VUL), a challenge on the floor
of the Great Hall (KDF), the Continuing Committee (ROM), a Cardassian tribunal,
an amendment to the Rules of Acquisition (FER), the Celestial Temple (BAJ), an
efficiency deviation in a Borg node cluster, a Founder's visit (DOM), the
Symbiosis Commission (TRI), the Ushaan (ADR). Eight are open to every empire and
are the life of a starfaring service: a transporter fault, a holodeck program
that outgrew its design, the cartography office, shore leave, a convoy, a
frontier ward, a warp core taken past its rating, a small treaty. The
twenty-first hangs on first contact.

**Every field, trigger, reward tier and idiom is copied from a vanilla file that
was opened** — the two-step pulse from `action.220` / `action.221` in
`events/on_action_events_2.txt`, the reward tiers and the
`set_timed_country_flag` cooldown from `events/country_events_1.txt` and
`events/envoy_events.txt`, the scopes from the comments in
`common/on_actions/00_on_actions.txt`. No DLC-gated effect, no `specimen`, no
event chain: STG is standalone.

## The finding: we hook somebody else's `events`, and nobody else's `random_events`

The obvious design is to add STG's twenty events straight into vanilla's
`on_five_year_random_pulse_country`, which is the slot the base game reserves
for exactly this and which is **very nearly empty on a standalone host** — of
its 435 points of content, all but `action.2211` are Federations, Envoys,
Situations or First Contact.

`events = { }` lists demonstrably merge across files: four of the vendored mods
declare `on_colonized` between them and the game reads all four. **Whether a
second file's `random_events` merges with vanilla's or replaces it is a question
nothing on disk answers** — no source mod in the harvest adds one to an
on_action that already has one, so there is no worked example either way. Being
wrong the replacing way deletes vanilla's own `1900 = 0` along with everything
else in the block, and a story event fires nearly every pulse for the rest of
the game.

So the design does not ask. `stg_on_five_year_story_pulse` is **our own
on_action key**, reached by a one-line entry in an `events` list — the merge
behaviour that is proven — and we own every weight inside it, including the one
for "nothing happens". That the README licenses this ("Custom on actions can be
defined in script and triggered by the `fire_on_action` effect") is what makes
it legal; that it removes an unanswerable question is why it was chosen.

**The weights are calibrated against vanilla rather than picked.** Vanilla's own
five-year pool produces anything at all 18.6% of the time (435 against
`1900 = 0`). An STG empire sees its own two species-gated events at 60 and all
eight open ones at 25 — 320 against `1200 = 0`, or 21%. Close to vanilla's rate
on purpose: this is a flavour slot, not a second anomaly system. `random_events`
fires exactly one winner, so **adding to the pool later cannot make the player
see more popups, only different ones**, which is the property that makes the
whole slice extensible.

## The check, and the defect class it was written for

`check_story_events` in `tools/validate.py`. A story event is **four files that
have to agree**, and none of them dangles when they do not.

**The first question has no counterpart in `check_anomalies` or
`check_archaeology`: is the on_action KEY itself one the engine will ever
fire?** A hook whose key is wrong parses cleanly, its events exist, its art
loads, its localisation resolves — and nothing under it ever runs. That is
[decision 71](71-trek-archaeology.md)'s `weight = 0` and
[decision 59](59-city-set-cultures-undeclared.md)'s undeclared graphical culture
arriving in a seventh database: everything present, nothing dangling, the
content simply never appears.

**Vanilla is the calibration**, over its 452 on_action keys and the events they
name:

| Question | Findings |
|---|---|
| on_action key is declared or fired | **0** in the built tree — 6 before the empty-block filter, all six Planetary Diversity's |
| on_action names an event that exists | **0** in the built tree, **17 in vanilla** |
| event's picture is declared | 0 |
| event title / desc / option loc key | 0 |

Two of those rows are results rather than numbers.

**The six that became zero are all `on_x = { events = { } }`** — Planetary
Diversity hooking `on_survey`, `on_pop_added`, `on_planet_zero_pops` and three
more that Stellaris renamed some versions ago. They are vestigial stubs with
nothing in them, and *a hook with nothing in it cannot fail to fire anything*.
Reporting them would be reporting a fact about PD's changelog, not a defect.

**The 17 are Paradox's own** — `origin.5094`/`5104`/`5114`/`5124`,
`anomaly.6793`, `action.41`, six `shroud.103xx` and five `grand_archive.70xx`,
all hooked in `00_on_actions.txt` and none of them shipped. A known floor, the
same shape as `UBUME_BABY_CAT` is for [70](70-trek-anomalies.md) and
`cstorms.1300` is for [71](71-trek-archaeology.md).

**A third source of legitimacy had to be modelled, and it is
[rule 4](../validation/check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand)
rather than thoroughness.** `on_destroy_planet_with_<KEY>` is generated by the
*engine* from a planet-killer component's own key. Vanilla declares the four for
its own components in `01_planet_destruction.txt` and says nothing about
anyone else's, so Planetary Diversity's Necro Ray hook reads as dangling while
being perfectly live. The allowlist comes from `common/component_templates/`,
not from a hand-written name.

**The fifth question has a scope**, for the reason it does in both siblings: *"a
story event no on_action names"* is meaningless over vanilla, which reaches most
of its events by chaining them off each other. Over `stg_story_events.txt` the
shape is different by construction.
[Check design rule 11](../validation/check-design.md#11-scope-is-a-calibration-result-not-a-convenience-filter).

> **Its first run against real content found a defect in the two checks beside
> it, not in the content.** 26 hooks in Real Space, Planetary Diversity,
> Ariphaos and System Scale were reported as firing events nobody declares, and
> every one of those events was sitting in the tree — declared as a **bare
> `event = { }`**, which is legal, which vanilla itself writes in forty-odd of
> its own files, and which `kind.endswith("_event")` does not match. The same
> line was in `check_anomalies` and `check_archaeology`; all three now share
> `_is_event_block`. **Missing the bare form does not make an event dangle — it
> makes a check believe one does**, which is the worse failure, because a
> reviewer's next move is to go and repair content that was never broken.
>
> It did not move either sibling's floor: `anomaly.6791` really is absent from
> the tree, so [70](70-trek-anomalies.md)'s floor of 1 stands as recorded.

**Then deliberately, against a broken tree:** a typo'd hook key, a hook naming
an event id that does not exist, an event orphaned out of the pool, an
undeclared sprite and a `desc` pointing at a key nothing defines — all five
reported, and the hand-edit guard fired on top of them because the mutations
were made in `stg-build/`.

## The art

21 pictures, all STNH's, all of them art the clutter closure had been pruning
until something declared it. The prune fell 909 → **888** with no edit to
`vendor.yml`, exactly as it did for the anomalies' 24 and the sites' 27.

**Every candidate was looked at as the build will cut it** — frame 0 of the
strip, centre-cropped to 450×150 — and **eight were rejected on what that crop
showed**: two Lower-Decks-animated frames (the same call
[70](70-trek-anomalies.md) made on `mugato_world.dds`), three close-ups of a
named character's face, one near-featureless star field, and two that read as a
different subject than the filename promised.

> **Three more were rejected for the opposite reason, and that filter is new.**
> `engineering_bay`, `cargoship_caravan` and `galactic_market` are STNH shipping
> **vanilla's own picture under vanilla's own name** — Stellaris concept art, in
> a Trek directory, with a Trek-sounding filename. They are neither Trek nor
> ours to declare. The filter is one line: 580 of STNH's 1,350 event-picture
> names also exist in `/stellaris/gfx/event_pictures`, and only the other 770
> are art STNH added. **A filename cannot make this call and neither can the
> directory it sits in.**

None of the 21 is declared by either sibling `.gfx`. One picture, one subject.

## What only eyes can grade

Whether the writing sounds like Star Trek and not like a different mod, whether
the 21 pictures match the text under them, and whether a story event every five
years or so reads as texture rather than as interruption. None of that produces
a log record. [Open questions](../planning/open-questions.md).
