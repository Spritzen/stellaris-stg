# 101 — Every first contact in the game plays the aquatic sting, because vanilla picks the sound off a species class list STG replaced wholesale

**Status:** decided, 2026-08-28
**Follows** [decision 09](09-species-class-keys-unprefixed.md) and
[decision 19](19-species-class-localisation.md), which are the same shape: the
engine derives something from the species class key, and 129 unprefixed keys
that vanilla has never heard of get nothing.

## The report

Ten records in the 2026-08-28 UFP run — every first contact in 70 minutes of
play, and nothing else in that class:

```
event.cpp:896  Failed to pick an event sound from among the available options
               for event first_contact.5000 / .15 / .5 / .50 / .60 / .390
               / .10 / .5070 / .350 / .355  (defaulting to first on list)
```

Found while reading the log after a live run, and **not** the bug the run was
reported for. That one is still open — see the note at the end.

## Why

Vanilla's first-contact events do not carry a sound. They carry

```
inline_script = first_contact_event_sounds
```

and that inline script is thirteen `show_sound` blocks, each gated on the
contact's `is_species_class` against one of **vanilla's own thirteen classes**:
AQUATIC, ART, AVI, FUN, HUM, LITHOID, MACHINE, MAM, MOL, NECROID, PLANT, REP,
TOX.

STG declares **129 classes of its own** and, by
[decision 09](09-species-class-keys-unprefixed.md), declares them under STNH's
unprefixed keys — FED, KDF, ROM — because the vendored clothing selectors gate
730 `is_species_class` tests on exactly those spellings. None of the 129 is one
of vanilla's thirteen. So for a Trek contact **no block passes**, and the engine
does what its message says: it takes the first entry on the list.

The first entry on the list is `event_first_contact_aquatic`. **Every first
contact in a Trek galaxy plays the aquatic sting** — Klingons, Vulcans,
Cardassians, the Borg — and has done since the class file was written.

Nothing else in the merge is at fault and no source mod is involved: the events
are vanilla's, the inline script is vanilla's, and the classes are ours.

## The fix

`src/common/inline_scripts/first_contact_event_sounds.txt`, which replaces
vanilla's by path — the only way to reach it, since the script is spliced into
vanilla first-contact events we shadow none of. It carries **vanilla's thirteen
blocks unchanged and first**, then eleven of our own covering all 129 classes.

**The mapping is a content call and it is made rather than deferred.** Star Trek
is a humanoid franchise, so the honest shape is a short list of species with a
louder non-humanoid reading and a long tail that is simply humanoid:

| sound | classes | |
|---|---|---|
| `machine` | BRG, HOLO, CRA, PRA, BYN | Borg, photonics, the Pralor/Cravic robots, and the Bynars |
| `reptilian` | CAR, GOR, TRO, SEL, SAU, VOT, XIN, HAZ, TZE | 9 |
| `mammalian` | CAI, KZI, LYR, LYRI, ANTI | four felinoids and a canine |
| `necroid` | KOB, VID, MED | reanimators, the Phage, and a non-corporeal |
| `lithoid` | THO, BRIK | crystalline and rock-bodied |
| `arthropoid` | UND, HUR | Species 8472 and the Hur'Q |
| `aquatic` | ANT, MON | piscine, and a species that lives in a water world |
| `molluscoid` | DOM | the Founders, liquid-state |
| `plantoid` | SHE | the Sheliak, chlorophyll-based |
| `avian` | KIN | the Kinshaya, on the wings |
| `toxoid` | MAL | the Malon, toxic by trade |
| `humanoid` | the other 97 | |

`fungoid` is deliberately unused: nothing in the roster reads as fungal, and
assigning one to reach thirteen for thirteen would be worse than leaving it.
`avian` very nearly went the same way — the Aurelians are the franchise's birds
and STG declares no class for them, only clothes art — and the Kinshaya carry it
instead.
Every entry above carries its reason in the generator, because *why is the
Kobali a necroid* is the question the table exists to answer and it is not
recoverable from a three-letter key.

## Two things about the shape of the file

**No triggerless catch-all, which would have been four lines instead of 129.**
Vanilla has the form — `events/unrest_events.txt:192` is a `show_sound` with a
sound and no trigger — but the engine's own message says it picks *"from among
the available options"*, so it filters by trigger and then chooses among the
survivors. A block that always passes is therefore always in the running and
would take contacts away from the specific blocks rather than backstopping them.
Every class is named instead and the blocks stay mutually exclusive, which is
how vanilla writes its own.

**It is generated, by `tools/gen_first_contact_sounds.py`.** The mapping has to
be TOTAL — every declared class in exactly one block — because a class left out
is not an error anybody sees: it is one more wrong sound and one more log
record. The tool checks the table against
`src/common/species_classes/stg_species_classes.txt` in both directions and dies
on either mismatch, so a class added later without a sound cannot be committed;
`make gen-check` asks every run whether the output is still what the inputs
produce, which is also what turns a game patch re-cutting vanilla's thirteen
into a diff rather than a silence. It is the fourteenth generator.

## What this is not

**It is not the bug the run was reported for.** The report was that the first
contact window stopped raising its stage-done alert part way through the
session — a sound, no notification, and every site to be checked by hand. This
is a different defect in the same feature, found by reading the log because
[the procedure](../guides/live-runs.md) says to. `error.log` carries no record of
the alert failing and nothing STG ships is anywhere in that path: no
`common/first_contact/`, no first-contact events, no override of `alerts.gfx`,
its textures or its loc, and `alert_first_contact_stage_done` enabled with
`pausegame=yes` in the user's own `alert_settings.txt`. What corroborates the
report is **`game.log`**, which stamps a `playerEventId` on every answered event
and shows ten first-contact events answered out of order in bursts from 21:36,
the oldest queued around 21:19 — with no other event type ever out of sequence.
Open, in [open questions](../planning/open-questions.md).

**Nothing here is confirmed in game.** A sound that plays is graded by ear or
not at all; `make validate` clean says the blocks parse and the classes resolve.
What the next run can say cheaply is whether the ten records are gone.
