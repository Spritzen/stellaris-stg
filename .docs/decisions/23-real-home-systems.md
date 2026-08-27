# 23 — Real home systems, and why §1 was wrong about them

*Decided 2026-08-03, at the user's direction. Reopens the "no hand-placed
homeworlds" half of plan.md §1's Trek-map row. Same pattern as the
minor-power harvest: STNH's identity, vanilla's mechanics.*

## The symptom

Play reported the Federation's Sol system containing **Bajor and Andoria**. The
natural reading was a leaked STNH scenario system, and it was not: no
initializer anywhere in the built tree mentions either world, and STNH's
`common/` is never vendored. It was ours.

## The cause, which is a general one

No STG empire declared `initializer =`. That was deliberate, on §1's grounds,
and the header of `stg_major_powers.txt` said so. The mistake is in what the
remaining fields do:

```
planet_name = "STG_planet_name_federation"   # "Earth"
system_name = "STG_system_name_federation"   # "Sol"
```

**These are labels, not contents.** Without an initializer the galaxy generator
builds an ordinary random system, the two keys rename its capital and the system
itself, and every *other* planet in it is named from the empire's name list
`planet_names` pool. The Federation's pool is a list of Federation **member
worlds** — Vulcan, Andoria, Tellar, Betazed, Bajor, Trill, Risa, Bolarus. So
"Sol" was a label on a random system stocked with other people's homeworlds.

All 101 empires had this. It is not a Federation bug.

Worth stating because it is the counter-intuitive half: `system_name` looks like
it places you somewhere. It does not. Only `initializer` does.

## What was built

`tools/gen_home_systems.py` writes
`src/common/solar_system_initializers/stg_home_systems.txt` — **37 initializers**
— and `initializer =` is wired into **39** prescripted empires (22 playable, 17
minors). Sources, in order of preference:

| | |
|---|---|
| **Federation** | vanilla's own `sol_system_initializer`. Nothing was authored: vanilla's Sol is *already* the extended one — 17 bodies, Mercury through Varuna, with Luna, the Galileans, Titan, Triton and two asteroid belts — and Real Space overrides that same key with a rescaled copy. |
| **28 converted from STNH** | 40 Eridani with Keid and T'Khut, Qo'noS with Boreth and Gorath, Romulus with Remus, Cardassia, Bajor, Procyon, Unimatrix Zero One, Founder's Planet. Geometry theirs; every line of their scripting dropped. |
| **9 authored** | Ferenginar, Trillius, Bolarus, Breen, Tholia, Yridia, Kyana, Malon, Vidiia — see below. |
| **Terran Empire** | Sol as well, and it **shares** the Federation's initializer. See below. |

**Conversion drops all of STNH's init_effect.** Those blocks set STNH country
flags, save STNH event targets, call STNH species flags and add STNH deposits —
precisely the `common/` we do not vendor. The capital keeps only what vanilla's
own Sol does: `starting_planet`, `prevent_anomaly`, `deposit_blockers = none`.
The engine generates pops and home-system resources itself; vanilla never
scripts them into an initializer and neither do we.

STNH's Trek planet taxonomy is mapped onto vanilla's — Class I and U to
`pc_gas_giant`, Class Y and N to `pc_toxic`, Class F and G to `pc_barren`, the
Great Link to `pc_ocean`, the Borg unimatrix to `pc_machine`. `sc_trinary_kdm`
becomes vanilla's `sc_trinary_k_m_d`, which is not an approximation: 40 Eridani
really is a K dwarf, a white dwarf and a red dwarf.

## The mirror Terran Empire shares Sol, deliberately

A first pass gave it a duplicate Sol under its own key so that both it and the
Federation could spawn. **That solved the wrong problem.** A galaxy holding both
the Federation and its mirror is the thing to avoid, not to accommodate, and the
user said so. Both now name `sol_system_initializer`, which is
`max_instances = 1`, so there is one Sol.

What the engine then does with the second empire is **not settled, and the
container cannot settle it**. The evidence is only suggestive: every vanilla
empire that shares an initializer — five on `sol_system_initializer`, two on
`deneb_system` — is `spawn_enabled = no`, so vanilla never puts two AI-spawnable
empires in competition for one system and offers no precedent either way.
(Vanilla *does* ship five AI-spawnable empires with a unique initializer, so the
combination STG uses everywhere else is ordinary.)

It was taken anyway because **the failure mode is benign**: if the engine does
place the loser somewhere, it is a generated home system — exactly where all 101
empires sat before this decision. The downside is bounded by the status quo
ante, so the untested path is worth the one live run it takes to confirm.
Check it there rather than assuming either way.

## Colony names could still collide, and now cannot

Pinning the home system removed the reported symptom without removing the cause.
`planet_names` pools name **colonies**, and the Federation's was a list of member
worlds — so it would still have named some distant colony "Vulcan" while the
Vulcan Confederacy sat on the real one. Two flavours, both wrong:

- **another empire's capital** — two Vulcans in one galaxy;
- **the empire's own capital** — an Andorian colony called Andoria, which only
  became possible once `planet_name` pinned the capital for real.

**40 tokens across 23 name lists** were removed. Only the Federation was left
thin (18 → 8), and it is topped back up to 20 with Federation colony worlds no
empire claims: Sherman's Planet, Cestus III, Setlik III, Dorvan V, Ronara Prime,
Volan III, Caldos, Pacifica, Casperia Prime, Argelius II, Nimbus III, New Berlin.

`check_colony_name_collisions` enforces it. The comparison has to be on
localised **values**, not keys, because `STG_N_Vulcan` and
`STG_planet_name_vulcan` are different keys that both render "Vulcan" — a
key-level check would see nothing. Calibrated by putting Vulcan back in the
Federation's pool: it fails, and names the owning empire.

One repair bit back and is worth recording: the removal script re-wrapped each
pool using `STG_N_[A-Za-z_0-9]+`, which **excludes hyphens**, so
`STG_N_Nol-Ennis` was silently truncated to `STG_N_Nol` — a token with no loc
key. `check_name_lists` caught it immediately. Trek names carry hyphens and
apostrophes; a token regex that assumes otherwise will quietly corrupt them.

## Why only 37, and what is still generated

STNH ships 156 usable home systems and **122 of them are procedural** —
`class = "rl_starting_stars"`, `size = { min max }`, `count = { }` — resolving
against random lists in STNH's own `common/random_lists/`. Converting one means
either vendoring that `common/` or inventing the geometry, so the generator
takes only the **34 with fixed geometry** and reports the rest.

That covered 13 of the 22 playable empires. The other nine had procedural
sources and are **authored** instead, vanilla-shaped and canon-led rather than
decorated: Bolarus IX is the ninth planet and has eight ahead of it; Tholia is
hot and high-radiation around an F star because Tholians are crystalline; Breen
is frigid around a red dwarf; Malon Prime is ringed by the industrial waste its
people export.

**62 AI-only minor powers are still on generated home systems** — their STNH
originals are all procedural. They are AI-only, so the cost is much lower than
it was for the Federation, but it is not zero and it is the obvious next piece
of this work.

## Two bugs the conversion hit, both worth keeping

- **The capital is not always a `planet`.** Andoria is a *moon* of the gas giant
  Onlith, which is canon and which STNH models faithfully; so is Alrond. A
  converter that walked only `planet` blocks silently dropped both empires. It
  recurses now.
- **STNH names the Andorian system's primary star "Andoria" too**, and our
  `planet_name` renames the capital moon to Andoria — the same name twice on one
  map. Vanilla's convention settles it (Sol's star is called Sol), so a star
  whose name collides with the capital's takes the system's name instead.

A third was pure parsing: `orbit_angle = { min = 30 max = 270 }` had its braces
flattened away and the regex then matched the *next* key's name, emitting
`orbit_angle = size`. Ranges collapse to their midpoint now, and a value that
comes back as one of our own key names is treated as absent.

## The check

`check_prescripted_initializers` asserts that every `initializer =` names a
system that (a) is declared somewhere in `common/solar_system_initializers/` and
(b) is `usage = custom_empire` — the engine applies both, and a system with the
wrong usage resolves by name and then never spawns. The engine does log
`Invalid initializer`, but only for empires it tries to place, so an AI-only
minor with a typo could sit undetected until someone rolled it. Sweeping the
rule beats reading the log, as with the traits in `check_prescripted_empires`.

**Calibrated by reverting**: a bogus name and a declared-but-wrong-usage name
each produce their own error; restored, `make validate` is clean.

## What this does not settle

**62 AI-only minor powers are still on generated home systems**, and whether two
empires sharing Sol behaves as intended is a live-run question (above).

Nothing here is confirmed in game. `make validate` is clean and the geometry is
grounded in vanilla's own Sol, but only a live run shows the systems.
