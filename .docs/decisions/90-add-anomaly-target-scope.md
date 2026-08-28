# 90 — `add_anomaly` runs on a planet nobody owns, so `target = owner` resolves to nothing

**Status:** decided, 2026-08-28
**Follows** [decision 11](11-fix-source-errors-dont-drop.md) — a source mod's
error is a cost to pay down in a `vendor.yml` patch, never a reason to drop the
mod.
**Corrects** nothing. This is the queue item
[status.md](../planning/status.md) has carried since the 2026-08-25 evening run,
worked without a live run because the fix is a line vanilla already writes.

## The record

One line, from the 2026-08-25 evening Vulcan run — **the first post-init record
to name a file we ship since 2026-08-10**, and it recurred in the 2026-08-26 run:

```
[18:14:33] eventscope.cpp:3383  add_anomaly: Unable to resolve country from 'owner'
                                (country scope) at events/!!!!!!ariphaos_precursor_cosmic.txt line: 127
```

Vendored from **Assorted Precursor Adjustments** (harvest position 13).

## What it is

`cstorms.200` is a `ship_event`: `root` is the surveying ship and `from` is the
planet it just surveyed. Ariphaos rewrote vanilla's line as a bare
`target = owner`, which inside `from = { … }` asks **the planet** for its owner
— and the event's own trigger requires an uncolonised body:

```
FROM = {
    NOR = {
        has_anomaly = yes
        is_star = yes
        can_have_habitable_deposits = yes
        has_planet_flag = precursor_world
        exists = archaeological_site
        is_planet_class = pc_gas_giant
    }
}
```

So there is never an owner there to find, and the adAkkaria anomaly is **silently
not added** on every planet the event ever fires for. Not a cosmetic record: the
whole payload of the event is the anomaly.

**The tell is eight lines up in the same file.** `cstorms.100`, the identical
event for the Inetian precursor, still carries vanilla's `prev.owner`. One of the
two was rewritten and the other was not — which is why this reads as a slip
rather than as an intended change, and why restoring vanilla's line costs the
source mod nothing it meant to say.

## The fix

A `vendor.yml` patch restoring vanilla's own
`/stellaris/events/precursor_events_cosmic_storms.txt` line:

```
target = owner   →   target = root.owner
```

`root` is the surveying ship, whose owner the trigger already requires to exist
(`owner = { is_ai = no … }`). Vanilla writes `root.owner` on this exact event.

## Why this generalises, and where it stops

**Swept before it was fixed** ([check design rule 6](../validation/check-design.md#6-a-screen-nobody-opened-is-a-check-that-never-ran)):
the build holds **29** `add_anomaly` sites, 27 of them the
`solar_system_initializers/` form that takes no target at all. Of the two that
name a target, this was the only one that named a bare relative property. One
instance, and the sweep is what says so.

**The rule behind it is about this effect and not about `target =` generally,
and getting that backwards would have shipped a false check.** A bare
`target = owner` is perfectly ordinary elsewhere — **vanilla writes one 8 times**,
on `begin_event_chain` and `start_situation`, where the scope really does have an
owner. Measured across both trees, `target =` appears at **3,067** sites in
vanilla over 124 effect kinds and **1,171** here over 9.

What makes `add_anomaly` different is a mechanism, not a coincidence of samples:
**an anomaly is what a science ship finds on an unsurveyed body, so the planet
scope this effect runs in is systematically unowned.** Vanilla's own 29
`add_anomaly` targets bear it out — 14 `root`, 8 `solar_system`, 6 `prev`,
1 `prevprev`, and **not one** that reads the planet's own ownership.

## The check

`check_anomaly_targets`, new in `tools/validate.py`. Every `add_anomaly` that
names a `target` must anchor it at a scope, not at a property of the planet it is
standing on. **The allowlist is read out of vanilla at run time** rather than
written into the check ([rule 4](../validation/check-design.md#4-derive-allowlists-from-vanillas-own-usage-never-by-hand)),
so it survives a game patch; `from`/`fromfrom` and `event_target:` are accepted
beside it because each *names* a scope, while `this` is rejected — `this.owner`
is this defect spelled out in full.

**Vanilla's floor is 0 of 29. STG is 0 of 2.**

**Calibrated by reverting the repair**
([rule 7](../validation/check-design.md#7-compare-declared-identity-not-block-key--and-distrust-a-check-that-has-never-failed)):
with `target = owner` put back, the check reports it at
`events/!!!!!!ariphaos_precursor_cosmic.txt:127` — **the same file and the same
line number the engine printed**, which is the closest a container-side check
gets to agreeing with a live run.

## What it cost, and what it did not

The population is small — 2 targets — and that is worth stating plainly rather
than dressing up. What earns the check its place is not the count but the
direction: this is a **source mod's** defect class, so it grows with the harvest
rather than with `src/`, and the next mod that adds a Trek anomaly event will be
read by it on the first `make vendor`. The failure it guards is invisible to
every other check in the tree and produces at most one log line, and only if
somebody surveys that exact planet.

**Still unconfirmed in game**, and it cannot be confirmed cheaply: grading it
means surveying the adAkkaria precursor system's barren bodies and seeing the
anomaly appear. The honest statement is that the tree validates clean and the
line now matches vanilla's.
