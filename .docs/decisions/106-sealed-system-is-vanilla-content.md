# 106 — The lane-less trinary star next to Ferenginar is vanilla's Sealed System, isolated on purpose, and the same save grades every question decision 87 left open

**Status:** decided, 2026-08-29
**Answers** [decision 87](87-static-map-lanes-are-generated.md)'s four closing
questions, all four, from the 2026-08-29 UFP save. 87 is confirmed, not
falsified.
**Corrects** [status.md](../planning/status.md)'s init-window table, which names
seven classes where the log has eight — see "What the sweep found" below.
**Confirms** [decision 35](35-attach-edges-into-pruned-art.md): its acked
`attach` price is unchanged at 9 records, three weeks on.

## What was reported

A UFP run on 2026-08-29: *"a trinary star near Ferenginar that wasn't attached
to any hyperlanes"*, reported with the caveat that it might be event-driven
rather than a defect. **The caveat was right.** It is
`distar_sealed_1_2` — vanilla's **Sealed System**, from Distant Stars.

## Why the log could never have answered it

`error.log` holds **no record of it**, and would not have held one under any
outcome. This is the second time the same shape has come up
([87](87-static-map-lanes-are-generated.md)): a system with no hyperlanes is not
an engine error. The save settled it, in minutes, exactly as
[live-runs.md](../guides/live-runs.md) says it would.

## The finding

The system is spawned at game start by vanilla's own
`events/distant_stars_events_2.txt`, and the engine is *told* to strip its lanes:

```
#Isolate Sealed System
if = {
	limit = { exists = event_target:sealed_system }
	event_target:sealed_system = {
		isolate_system = yes
```

`/stellaris/common/solar_system_initializers/distant_stars_initializers.txt:3706`
declares it `class = "rl_trinary_stars"` — hence a trinary star — with
`flags = { sealed_system crisis_spawn_exclude antique_threat_system }`.

**Access is a wormhole pair, not a lane**, and both halves are intact in the
save:

| | |
|---|---|
| system 95 | `Tonatiuh`, `distar_sealed_1_1`, the entry point — 1 lane, natural wormhole 1, bypass 2 |
| system 96 | `Delta Cancri`, `distar_sealed_1_2`, the sealed system — **0 lanes**, natural wormhole 2, bypass 3 |
| the pair | bypass 2 `linked_to=3`, bypass 3 `linked_to=2`, **`active=yes` on both** |

Its nearest neighbour is Ferenginar at **12.5 units**, which is the "near
Ferenginar" in the report.

> **Nothing to fix.** This is vanilla DLC content working as designed, placed
> into our static galaxy by vanilla's own event, and reachable by the route
> vanilla intends. The one thing worth having is the *reason*, written down, so
> the next run does not spend a session on it again.

## The same save answers all four of decision 87's questions

87 shipped generated lanes and ended with four questions it could not grade.
Read off `2216.03.01`:

| 87's question | answer |
|---|---|
| **1. Do the lanes render, is the map traversable?** | **Yes.** 99 of 100 systems reachable from Sol by hyperlane alone; the only exception is the Sealed System above, which is unreachable *by design* and reachable by wormhole |
| **2. Is 3.4 lanes per system right?** | It held. Over the 95 scenario systems: degree **min 2, max 5, mean 3.45**, no zero-lane system, no isolated component |
| **3. Does anything still call `spawn_system` and fail?** | **No.** Zero `spawn_system` records this run, against three on 2026-08-27. They were symptoms of the lane defect, as 87 argued, not a Planetary Diversity finding |
| **4. The picker lock and the AI Federation** | untouched here, still open |

**Five systems were spawned at runtime and every one of them attached**, which
is the direct evidence for question 3: ids 95–99, one lane each except the
sealed one — `distar_sealed_1_1`, `distar_sealed_1_2`, `pd_init_floating`,
`pd_init_crystal`, `pd_init_biosynth`. A `spawn_system` needs an existing lane
network to attach to, and now there is one.

> **The rule this run confirms.** A generated MST guarantees the *declared*
> systems are connected; it says nothing about systems the engine adds later.
> Runtime-spawned systems attach themselves — and one that does not is either a
> `spawn_system` failure the log *will* name, or a deliberate `isolate_system`
> that it never will. **Check which before calling it a defect.**

## What the sweep found: the init-window table names seven classes and there are eight

Asked for a full sweep of the log directory. `make logs` — **19 files, 0
warnings**, no file changed state. `error.log` is **1,735 records / 283 KB**,
**1,723 of them inside the 47.5 s init window** and **12 after it**, none of the
12 ours (vanilla trait scope errors on a leader, two `Luxury Residences`
placements, a Nemesis `add_intel`, an audio sample-rate notice, and
`PLANET_SCALE_SYSTEM`, acked in [41](41-planet-scale-system-length.md)).

The seven init classes in [status.md](../planning/status.md) reproduce **record
for record, a third identical measurement**: 568 / 353 / 143 / 110 / 103 / 31 /
23. The 353 is [decision 88](88-lock-the-galaxy-picker.md)'s picker lock, still
exactly its stated price.

**But grouping by `.cpp:line` fresh, rather than checking the seven off a list,
returns eight.** The missing one is the **third largest in the log**:

| 172 | `game_singleobjectdatabase.h:170` — *Object with key: X already exists, using the one at* |
|---|---|

**172 in this log, 172 in `error.log.2026-08-10`, 172 in `error.log.2026-08-08`**
— an init-window constant across three weeks, like the 568. **0% ours**: every
record names a Planetary Diversity, Starbase Extended, Ariphaos or
`vanilla_ow_` file redeclaring a key it also declares elsewhere — the same
deliberate override idiom the 568 was triaged as in
[31](31-duplicate-entity-declarations.md) and [50](50-duplicate-entity-triage.md).
Benign, and now counted.

> **This is the failure mode that table's own sidebar warns about, committed by
> the fix for it.** The sidebar says *"a triage sorted by remembered wording
> samples the classes you can already name — group by the emitting `.cpp:line`
> instead"*. The table was then written by grouping once and **checking the
> result against the classes already named**, which is the same error one level
> up. It caught the 568 and missed the 172. The old sentence it replaced also
> claimed *"nothing above nine"*, and that is false in four more places:
> `pdx_entity.cpp:135` (18), `pdx_audio.cpp:1111` (11), `reader.cpp:209` (10)
> and `pdx_entity.cpp:266` (10). **Re-derive the census; never reconcile it.**

## One class in the sweep looked like a defect and is a priced ack

`pdx_entity.cpp:424`, **9 records, and 9 in every log on disk** — 2026-08-08,
2026-08-10 and today alike. Every one names a Trek ship entity
(`romulan_rom_bop_rea_section_1_entity`, `klingon_corvette_coreA_entity`,
`kdf_naval_museum_test_entity`), all nine are `attach = { "partN" = "…" }` lines
in `fed_ent_naval_museum.asset` and `rom_naval_museum.asset`, and the names are
declared nowhere in `gfx/`.

**This is [decision 35](35-attach-edges-into-pruned-art.md), already triaged and
already acked**, and it was written up here as a new finding before the ack was
checked. `check_attach_targets` does follow `attach =` edges — vanilla floor 0
of 5,672 — and both files are listed in `vendor.yml` under `attach_target_ack`
with a correctness argument: their consumers live in STNH's `common/`, which STG
does not vendor, and the nine recoverable entities sit in the two directories
[decision 17](17-walshicus-shipsets-replace-stnh-hulls.md) pruned, so restoring
them would re-open a known collision to feed art nothing can reach.

**What this run adds is only that the price is stable.** Decision 35 priced it
at *"9 records of 1,308 in the 2026-08-07 run"*; it is 9 of 1,735 today, and 9
in both archived logs. An ack whose count has not moved in three weeks is an ack
behaving as documented.

> **The lesson is about the sweep, not the museums.** Grouping fresh by
> `.cpp:line` is the right way to *find* a class, and it correctly surfaced this
> one. But "no document names this class" is a claim about the documents, and it
> has to be checked against the ack lists and the decision index before it is
> written down — `check_attach_targets` and decision 35 both existed, and a
> `grep attach_target_ack vendor.yml` would have cost nothing. **Find by
> re-deriving; classify by reading what is already recorded.**

## What this closes

**Closes** the top item on [open-questions](../planning/open-questions.md) —
*"not yet run with lanes, so the top item on this page is still a live run:
check you can fly out of Qo'noS"*. You can. The galaxy is connected, and the
only hole in it is vanilla's, on purpose.

**Does not close** the picker lock, the AI Federation, or the prescripted-pool
question — none of them is touched by this run.
