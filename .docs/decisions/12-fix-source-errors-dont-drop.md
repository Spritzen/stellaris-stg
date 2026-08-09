# 12 — Fix a source mod's errors; don't drop the mod to silence them

**Decided 2026-08-02.** Supersedes the keep-or-drop framing that
the 08-02 analysis
§6 applied to Starbase Extended 3.0, and closes the last of plan.md §8's
"judgement calls the live run surfaced".

## The decision

**Starbase Extended 3.0 stays in the harvest, and its errors get fixed here.**
More generally, and this is the part that outlives SBX:

> A harvested mod's error count is a cost to pay down, not a reason to drop it.
> Sources are dropped on **content** grounds only.

## Why the analysis got this the wrong way round

§6 measured SBX at ~476 errors — the second-largest source in the build after the
Universal Resource Patch — and recommended dropping it. The measurement was
right; three of its four supporting arguments were about noise rather than
content:

| §6's argument | What it actually establishes |
|---|---|
| "second-largest error source in the build" | that it is noisy |
| "two of the seven post-load errors are its" | that it is noisy during play |
| "stale against 4.4, duplicates definitions vanilla now ships" | that **part of it** is redundant — not that any of it is broken |
| "contributes no Trek identity" | a content argument, and the only one of the four |

A duplicate definition is the engine reporting that it already had one. It is
not a defect in the thing SBX adds; SBX's 19 extra starbase levels, 16 starbase
ship sizes, and its modules, buildings and components are unaffected by it. The
recommendation converted "loud" into "worthless" without an argument connecting
the two.

Meanwhile the drop was scored as `−472` errors, which reads like a fix and is
not one: the same log line disappears whether you repair the cause or delete the
content. Only one of those two leaves the mod working.

## What the rule is

When a source mod throws errors, in order of preference:

1. **A `vendor.yml` patch** on the offending lines. Preferred because of how it
   fails: if the source mod changes underneath it the build stops and names the
   file, so a fix that is no longer needed cannot silently persist.
2. **An `exclude:`** for files that are genuinely inert here — compat shims for
   mods that are not in the harvest, `.bak` files, editor junk. Excluding a file
   nothing references costs nothing.
3. **An `src/` override** when we genuinely mean to own the file.
4. **An `*_ack:` entry** when the error is understood, harmless and the fix
   would cost more than it is worth. An ack is a reviewed decision with a
   recorded reason, not a shrug.

Dropping the mod is not on that list. It remains available as a **content**
decision — decision 11 dropped Cinematic Camera because it was breaking Real
Space, and Kammarheit/Apocryphos because dark ambient is not what Star Trek
sounds like. Both cases were argued on what the mod *is*, and neither would have
changed had the mods been silent.

## Consequence for the analysis' recommended order

Item 2 ("Drop Starbase Extended 3.0") is withdrawn and replaced by a repair of
the same ~476 errors in place. Item 1 (URP's five topbar-compat files) survives
unchanged — those are rule 2, not a drop: five files that are compatibility
shims for Improved Topbar, Compact UI Topbar and Star Trek: New Civilisations,
none of which is in the harvest, whose declared group names nothing in STG or
vanilla references.

## Correction carried out of this

The analysis' register attributed four `Malformed token:
@starbase_formation_priority` / `@build_block_radius_starbase` records to ASB
Ironman. They are SBX's, from
`common/ship_sizes/sbx_3_0_starbases.txt` and `nsc_starbases.txt`. Had SBX been
dropped they would have vanished with it and the misattribution would have gone
unnoticed, which is a small illustration of the general point.
