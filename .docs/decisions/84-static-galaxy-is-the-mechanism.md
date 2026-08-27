# 84 — STNH gets its Trek galaxy from static maps, not from the spawn lottery, and STG ships no map at all

**Status:** decided, 2026-08-26
**Follows** [decision 83](83-design-database-is-not-the-cause.md), which ruled out
the design database and left the lottery unexplained.
**Corrects** [decision 83](83-design-database-is-not-the-cause.md)'s reading of
STNH as a counterexample to the `randomized` hypothesis — STNH is not a working
control, because on random maps it has the same symptom.
**Corrects** the star-name harvest's "ten hand-built galaxy maps": STNH ships
**22** `static_galaxy_scenario` files, 17 of which contribute a system name.
The 1,444 names that harvest took are unaffected — the generator globs the
whole directory.
**Reframes** the `CUSTOM_EMPIRE_SPAWN_CHANCE` finding and this project's whole
approach to the question: `CUSTOM_EMPIRE_SPAWN_CHANCE` is a
lottery for sprinkling the occasional preset into an otherwise random galaxy. It
is not how a total conversion fills a galaxy with a named cast, and no amount of
tuning it will make it one.

## The comparison that settles it

STNH is the closest working reference this project has and its files are already
in `.source/688086068/`. Three things, all read off disk:

**1. STNH leaves the lottery at vanilla's 5%.**

```
.source/688086068/common/defines/sth_defines.txt:714
        CUSTOM_EMPIRE_SPAWN_CHANCE = 50
```

STG raised the same define to 1000 and got zero Trek empires in three galaxies.
STNH never touched it and has a Trek galaxy. **Whatever produces STNH's galaxy,
it is not this define** — which retires the last reason to keep looking at it.

**2. STNH ships twenty-two `static_galaxy_scenario` files. STG ships none.**

| | STNH | STG |
|---|---|---|
| `static_galaxy_scenario` | **22** | **0** |
| `setup_scenario` (random templates) | 5 | 14, all vendored from Ariphaos Galaxies |
| hand-placed systems | 468 - 3,757 per map | 0 |

STG's `map/setup_scenarios/` is vanilla's five sizes — `tiny`, `small`,
`medium`, `large`, `huge`, all overridden with Ariphaos Galaxies' content — plus
Ariphaos's nine size variants, fourteen in all: random-galaxy *parameters*, not
placed systems. The 2026-08-26 save confirms what was actually generated:
`template="medium"`, `shape="spiral_3"`.

**3. A static map binds a named empire to a named system.** STNH's Qo'noS:

```
system = { id = "372" name = "Qo'nos" position = { x = -189 y = 164 }
           initializer = klingon_homeworld
           spawn_weight = { base = 0 modifier = { add = 100000 has_country_flag = klingon_empire } } }
```

`base = 0` means no empire lands there *except* the one carrying the flag. STNH's
canon maps carry 99-152 such weighted systems out of 468-3,757. Vanilla documents
a second form in its own `map/setup_scenarios/static_galaxy_example.txt` —
`system = { … spawn_design = my_design }`, with the comment *"If system specifies
spawn_design, it will ignore spawn_weight"* — which names an empire design
outright.

## Why this also repairs decision 83's loose end

Decision 83 raised `randomized = no` on the species classes as the best remaining
candidate and recorded STNH as evidence against it, on the grounds that STNH
ships the same combination 94 times and has a Trek galaxy. **That reading was
wrong, and in an instructive way: STNH's Trek galaxy comes from the static maps,
so its prescripted pool is not under test there.** STNH's own workshop discussion
reports the same symptom STG has whenever the map is not static — *"AI spawns on
all random maps in STNH are currently borked, non trek randomly generated empires
are spawning as well"* (search snippet from the mod's discussions; the page body
could not be fetched to confirm it verbatim, so treat the wording as reported
rather than quoted).

**STNH is not a control. It is a second instance of the same failure, with a
workaround STG does not have.** That does not make `randomized` the cause — it
removes the strongest thing that was against it, and leaves the vanilla
cross-tab (32 of 33 spawn-eligible prescripted empires on a randomizable class;
STG 0 of 99) standing on its own.

## What the community material adds, and how far to trust it

[external-sources.md](../reference/external-sources.md)'s caveat applies in full:
this material is old, second-hand and was wrong twice before. Two claims recur
across a Paradox bug report and several Steam threads and are worth recording
because they name a *mechanism*:

- **`randomized = no` on a species class blocks a prescripted empire from
  spawning, even when force-spawned.**
- **`non_randomized_portraits` in `common/portrait_sets/` blocks it too**, and
  that is the more commonly reported of the two.

Vanilla's whole `non_randomized_portraits` set is four portraits — `human`,
`human_legacy`, `mam_rat`, `cyb12` — and **three STG empires use `human`**:
`stg_united_federation_of_planets`, `stg_terran_empire` and
`stg_minor_confederation_earth`. That is a specific, checkable explanation for
the Federation's `spawn_enabled = always` never firing, which the `playable`
fix closed and then had falsified. It explains three empires, not 99. There is also a documented 4.3.3 /
4.3.4 regression in which more than one force-spawned human-portrait empire fails
to spawn, reported fixed on a test branch; STG targets 4.4.6 and whether that fix
landed is unverified here.

STG's own `common/portrait_sets/stg_portrait_sets.txt` declares neither
`randomizable` nor `non_randomized_portraits` on any of its 99 sets, so on the
portrait side only those three empires are exposed.

## What to do, in order

**1. A three-class `randomized` experiment, because there is no UI test.**

*This section replaces a recommendation that was wrong when first written.* It
proposed opening the empire designer and setting Trek empires to **Empire
Spawning Forced**, on the strength of vanilla's loc strings saying "empire
**template**" (`EMPIRE_SPAWN_ALLOWED` / `_DISALLOWED` / `_ALWAYS`,
`EMPIRE_SPAWN_TOOLTIP_DELAYED`). **The maintainer confirmed at the UI the same
day that the force-spawn button exists only on player-made empires and a
prescripted empire cannot reach it** — which is what
`src/common/defines/stg_defines.txt` had said all along. Reading a loc string as
a UI affordance is the mistake; do not repeat it. `spawn_enabled` in script is
the only forcing lever STG has, and on the Federation's `always` it does not
fire.

That removes the cheap test, so build one instead. **Set `randomized = yes` on
three major powers' species classes only** — Klingon, Romulan, Cardassian, say —
and leave the other 126 at `no`. One galaxy then discriminates cleanly:

- those three turn up and nothing else Trek does → `randomized` gates the
  prescripted draw, and the fix is known and mechanical;
- nothing turns up → `randomized` is not the gate, and the lottery is dead as a
  route, leaving the static map as the only one.

Three classes rather than 99 keeps the blast radius small: the confound is that
vanilla ships a `common/species_names/` entry for every class it randomizes and
STG ships none, so a randomly generated empire on one of the three would have no
name pool. Three classes is also three small `species_names` entries if that
confound needs removing.

**2. Either way, a static galaxy scenario is what a Trek galaxy actually needs.**
Not as a fallback — as the mechanism. It is also strictly better than the
lottery, which would give a different random 18 of 99 every game with no control
over who is where. STG already owns the expensive half: **36 hand-built home
system initializers** ([23](23-real-home-systems.md)) and the **1,444 Trek
systems placed by name in STNH's maps** that this project has already
harvested once for their names. The smallest STNH canon map
is 468 systems with 99 weighted; that is the scale, and it is a scoped piece of
work rather than an open question.

**Do not raise or lower `CUSTOM_EMPIRE_SPAWN_CHANCE` again.** STNH proves the
define is not the road, and three galaxies at 1000 already proved it is not the
variable.

## Sources

- [Preset empires](https://stellaris.paradoxwikis.com/Preset_empires) — presets
  have "a small random chance of being spawned instead of a randomly-generated AI
  empire"; and **"Unlike non-human empires, human empires don't randomly spawn."**
- [Empire modding](https://stellaris.paradoxwikis.com/Empire_modding) —
  `spawn_enabled` values; `always` gives priority over randomised species.
- [Map modding](https://stellaris.paradoxwikis.com/Map_modding) —
  `static_galaxy_scenario`, `spawn_weight` with `has_country_flag`, and the
  warning that a static map must define nearly everything because "the galaxy
  generator will break things if some stuff is predefined and other things are
  generated".
- [Forced spawn for custom human empires not working (1.9.0)](https://forum.paradoxplaza.com/forum/threads/stellaris-1-9-0-a2c2-forced-spawn-for-custom-human-empires-not-working.1059396/)
  — the `non_randomized_portraits` and `randomized = no` claims.
- [Human Portrait Force Spawn Fix 4.3.7](https://steamcommunity.com/sharedfiles/filedetails/?id=3724067393)
  — the 4.3.3/4.3.4 human-portrait force-spawn regression. **Steam rate-limits
  `WebFetch`**; read via search snippets only.
- [ST: New Horizons discussions](https://steamcommunity.com/workshop/filedetails/discussion/688086068/3040480988279247223/)
  — canon static maps start each faction "in their (near to) canon (static)
  location".
