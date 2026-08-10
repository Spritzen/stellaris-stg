# 52 — Trek star names come from STNH's MAPS, not its star_names pool

**Resolved 2026-08-08.** Closes Phase 2's last unwritten item (plan.md §6) and
corrects a measurement in [decision 44](44-random-names-pools-append.md).
**Falsified in part by [decision 81](81-random-names-are-loc-keys.md),
2026-08-10:** the source and the written form below stand, but a **quoted**
entry is a localisation key, not a literal — all 110 of vanilla's own are
defined — and the 330 this shipped had no keys.

## The item

plan.md, Phase 2:

> **Trek names for systems and stars.** Unblocked as of 2026-08-07:
> `common/random_names/` pools **append**, so writing into that database is safe
> (decision 44). **Not yet written.**

§1's galaxy is "Trek-named systems in a normally generated galaxy". The 37 home
systems are hand-placed (decision 25); everything else is generated and drew its
names from the merged pool, which contains no Trek content at all.

## The obvious source is the wrong one

STNH's `common/random_names/base/00_random_names.txt` declares **5,992** star
names against vanilla's 1,763, in two labelled sections. Neither is what it
looks like:

| section | entries | of which already vanilla's |
|---|---|---|
| `### FICTIONAL ###` | 836 | **796** |
| `### EXTRA###` | 5,156 | 6 |

So the Trek-sounding half is **vanilla's own list relabelled** — `Amgathorra`,
which reads as convincingly alien as anything in the file, is a vanilla star
name — and STNH's genuinely original 5,156 are filler: tree names, foods
(`Enchilada`, `Bruscetta`, `Arugala`), scientists, animals and several thousand
surnames. Vendoring that pool would have added ~5,000 names, almost none of them
Trek, and put `Enchilada` in the Alpha Quadrant.

**The mistake it would have caused is the one decision 33 names: finding *a*
source is not the same problem as finding *the* source.** A 5,992-entry pool in
the Trek mod is a confident wrong answer, and the overlap with vanilla is the
only thing that exposes it.

## Where the Trek names actually are

`map/setup_scenarios/` — STNH's ten hand-built galaxy maps, 1,436 systems in the
default map alone, each placed by name. Harvested across all ten: **1,444
distinct system names**, every one chosen by the Trek mod for a Trek galaxy.

This is STNH's `map/`, which STG deliberately does not vendor (§3) — we take the
*names* into a file of our own, exactly as decision 19 took the 79 minor powers'
identity and 70 name lists out of STNH's `common/` without vendoring it.

## What was kept

`tools/gen_star_names.py` → `src/common/random_names/base/stg_star_names.txt`.

| | |
|---|---|
| Placed by STNH across ten maps | 1,441 |
| Already in the merged pool | −354 |
| Names STG already owns | −183 |
| **Written** | **829 star, 80 nebula** |

The 183 are the important subtraction. `Khitomer`, `Boreth`, `Risa`, `Betazed`,
`Denobula`, `Tellar`, `Benzar`, `Coridan` and `Rura Penthe` are all excluded
because STG already uses them as a home system or a capital — a random system
called Bajor while the Bajoran Republic sits at Bajor is the class of confusion
[decision 25](25-real-home-systems.md) was written about, arriving from the
other direction. The filter reads STG's own loc and name lists rather than a
hand-written list, so it stays correct as empires are added.

Nebulae are routed to `nebula_names` on their trailing word (`Nebula`,
`Expanse`, `Badlands`, `Cluster`, `Drift`, `Rift`, `Void`, `Patch`) — the forms
vanilla's own `nebula_names` uses. That is where `Badlands`, `Bassen Rift` and
`Azure Nebula` belong, and putting them in `star_names` would have named a star
after a nebula.

## Two written forms, both measured off vanilla

Guessing either would have failed silently, which is why both are in the
generator's docstring.

- **Multiword names take vanilla's quoted underscore form.** Of vanilla's 1,763
  star names, **0 contain a space**; the 55 multiword ones are written
  `"Epsilon_Eridani"`, `"Tau_Ceti"`, `"Alpha_Hydri"`. Real Space's patron file
  agrees (`Ushakov_Star`, `Da_Gwim_Weaper`). Writing `Ler Zumon` with a space
  would most likely have parsed as two separate names, and nothing would have
  said so.
- **Apostrophes are ordinary here, and unquoted.** Vanilla ships `Spoo'a`,
  `Gor'kaner`, `Pala'orolin`, `T'u`. This is the **opposite** of the Phase 1
  name-list rule ("no vanilla name list contains a bare apostrophe"), and the
  reason is that these are the one name database that is **not** loc keys:
  vanilla defines localisation for none of its 1,763 star names. `common/name_lists/`
  tokens are keys and must be; `common/random_names/` entries are literals.
  Do not carry the apostrophe rule across that boundary in either direction.

## Correction to decision 44

Decision 44 closed with "The effective pool is 1,569 + 15 = **1,584**." That is
wrong: it counted Real Space's two files and missed YAGEM's, which sit in the
same directory and contribute to the same key.

| file | source | star_names |
|---|---|---|
| `00_random_names.txt` | Real Space 4.0 | 1,569 |
| `ariphaos_astro_names.txt` | YAGEM | 1,994 |
| `ariphaos_astro_names_constellation.txt` | YAGEM | 2,143 |
| `realspace_starlord_partons_random_names.txt` | Real Space 4.0 | 15 |
| `stg_star_names.txt` | **STG** | **829** |

Deduplicated, the pool was **5,702** before this change and is **6,531** after;
`nebula_names` goes **71 → 151**. Decision 44's reasoning is untouched — pools
append, and the two YAGEM files are two more authors shipping partial pools into
separate filenames, which is further evidence for it. Only the arithmetic was
short, and it was short by 3.6×.

## Side effect: three event pictures came back, and the mechanism is new

The prune count fell **967 → 964** with no edit to `vendor.yml`, and the three
files are `gfx/event_pictures/{Lembatta_Cluster,fluidic_space,ion_storm}.dds`.

They came back because our new names include `Lembatta_Cluster`, `Fluidic_Space`
and `Ion_Storm`, and the clutter closure resolves a reference **by path, then
filename, then stem** ([decision 45](45-clutter-pass.md)). A star name is a
*content literal* — it names nothing on disk and is not a reference at all — but
it is a bare token that matches those stems, so the closure counts it.

**This is the closure erring in the direction it was built to err**, and no
change is wanted. Decision 45's rule is that a check which deletes must be
generous, because a missed edge is a deleted file that rendered perfectly while
a spurious edge costs a few hundred KB. Here it costs three files that remain
*inert* — nothing declares a `spriteType` over them, so they still do not draw.

What is new is the **class**: every previous stem match was an identifier
resolving to art. This is the first time ordinary content — a name in a name
pool — has retained a file. Anything added to `common/random_names/` or a name
list can now hold art alive by coincidence of spelling, and the count moving is
the only symptom. Worth knowing before the next unexplained shift in the prune
number sends someone hunting for an include-list mistake.

## Still inference, one live run from proof

Decision 44 labelled append semantics as inference from file layout rather than
measurement, and that is unchanged. If pools in fact replace, the last file in
sort order wins outright — and `stg_star_names.txt` now sorts last, so the
galaxy would draw from **829** names. The confirmation is the same one decision
44 named and is now cheaper to read: one generated galaxy showing a mix of Trek
names, Real Space's real stars and YAGEM's catalogue designations means append;
Trek names *only* means replace, and this file would then need to carry the
other 5,702.
