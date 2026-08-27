# 19 — Species class loc keys hang off the class key, unprefixed

**Status:** decided, 2026-08-03
**Extends** [decision 09](09-species-class-keys-unprefixed.md) and
[decision 18](18-minor-power-species-class-keys.md) from the class key to the
localisation keys derived from it.

## The report

After a live run the user reported that the Caitian, Xindi, Suliban, Yridian,
Krenim, Malon, Vidiian and Terran empires "have a three-letter species class".
They were reading the raw key — `CAI`, `XIN`, `SUL` — because nothing localised
it. `error.log` said nothing: this is a silence-failure class, like decision 18's.

## What was actually wrong

Two defects in one file, `src/localisation/english/stg_species_l_english.yml`.

**87 of STG's 101 species classes had no localisation at all.** The eight the
user named are the Phase 2 frontier powers; the other 79 are the AI-only
minor powers, which have the same defect and which no empire designer
screen would ever have shown. Phase 1 and Phase 2 wrote loc for the fourteen
majors and quadrant powers and each later batch of empires added classes without
adding their loc.

**The fourteen that did have it prefixed every sub-key `STG_`,** so only the
title ever resolved. The engine derives the whole family off the class key —
`FED_desc`, `FED_plural`, `FED_organ` — exactly as vanilla does for `HUM` in
`localisation/english/name_lists/name_lists_l_english.yml` and STNH does for
`BAJ` in `STH_main_l_english.yml`. `STG_FED_organ` is a key nothing looks up, so
26 keys per class × 14 classes were inert: an event that says a species was
struck in the `$organ$` printed the raw key.

## Decision

**The family keys take the class key's own spelling, with no `stg_` prefix** —
convention exception 2 in `CLAUDE.md`, for the same reason as the class keys
themselves: the name is not ours to choose. The *file* keeps its `stg_` prefix.

All 101 classes now carry the 27-key family in vanilla's order. Names and plurals
come from the empire that declares each class in `src/prescripted_countries/`;
nine of them had taken the species name from the polity (`VALT` was "Senate",
`CRA` was "CravicImperative") and were corrected by hand. Anatomy follows
vanilla's `HUM` block, varied for the reptilian, felinoid, aquatic and machine
peoples, and flavoured per species where Trek gives something to say.

STNH's own English families were read and mostly not used: 68 of them are
generic ("friend"/"enemy"/"laughing") with a scattering of typos
(`VAU_spawn_plural:0 "Chldren"`), and STNH titles every class "Humanoid", which
is the thing being fixed.

## How this class of defect gets caught next time

`check_species_class_loc` in `make validate`. For every class declared in
`src/common/species_classes/` it requires the loc family, and reports a class
whose keys are prefixed `STG_` separately from one with no loc at all, because
the repairs differ.

**The required suffix set is derived from vanilla, not listed here.** Vanilla's
usage is bimodal — 27 classes carry a 27-38 key family, 5 (EXD, IMPERIAL,
SOLARPUNK, SWARM, CYBERNETIC) carry only a title and are engine bookkeeping — so
intersecting all 32 demands nothing but the title and the check cannot fail.
It intersects over the fully localised half, split at half the largest family
rather than at a hand-picked key, and lands on 23 required keys.

Calibrated by reverting the repair: **exactly 101 findings**, the 87 unlocalised
plus the 14 prefixed, no false positives and no misses.

## What this does not fix

Nothing here touches clothing. The user's other finding in the same run — the
Federation, Andorian and Bajoran ruler portraits — is a separate question about
`humanoid_master_*_clothes_01`'s `ruler` scope and is not settled by this file.
