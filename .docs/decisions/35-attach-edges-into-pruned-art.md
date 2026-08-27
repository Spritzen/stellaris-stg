# 35 — `attach` edges into pruned STNH art — kept, not integrated

**Decided 2026-08-07**, from a sweep of the source mods' model directories
against the built tree. **No content change** — this records what was looked
for, what was found, and why nothing needed vendoring.

## The question

Decision 22's lesson was that *an include list scoped by directory does not
respect reference edges*, and that it converges on whatever the checks ask
about — mesh **names**, then mesh **files**, then **textures**, one file type
further down each time. So: is there another type further down again?

## What was swept, and what came back clean

| Sweep | Result |
|---|---|
| Every file inside every **included** directory of every source, against the build | **0 missing.** The include lists deliver what they name. |
| Extension census of `gfx/models/` across all 51 snapshots vs the build | Only `desktop.ini` (deliberately excluded) and one `sheliak_01/list.txt` in an already-pruned directory. Nothing else absent by type. |
| `.anim` files referenced by a vendored `.asset` | 361 referenced, **9 unresolved — and all 9 exist nowhere**: not in vanilla, not in any of the 51 snapshots. Six are `mammalian_01`'s `corvette_frame_*` / `destroyer_frame_*`, three are SBX's `fallen_empire_0{2,3,4}_citadel_idle`. Stale references in the sources' own files, not an integration gap. |

## What came back dirty: `attach`

`attach = { "part3" = "some_entity" }` hangs one entity off another's locator.
Nothing was checking it, and 23 references across 4 files name entities the tree
does not declare — 9 of which the 2026-08-07 log reported as
`Failed to find entity … for attachment`.

**Vanilla is unusually clean here and that is what makes this a finding rather
than a judgement call: 5,672 attach references, 2,461 distinct targets, 0
unresolved.** Same shape as the 8,409 entity names it never repeats
(decision 31).

Nine of the 23 **are** recoverable, from
`.source/688086068/gfx/models/ships/{romulan,klingon,klingon/kdf_yard}`.

## Decision: do not integrate, and do not exclude either

**Not integrate**, because those are precisely the two directories
[decision 17](17-walshicus-shipsets-replace-stnh-hulls.md) pruned — Walshicus
ships a `romulan` and a `klingon` of its own and loads later, so restoring
STNH's would put the newer art's `.gfx` back in conflict with the older art's
`.asset`. Re-opening a known collision to feed art that cannot be reached is a
straight loss.

*Cannot be reached* is measured, not assumed. The four files declare **115
entities between them and not one is referenced from anywhere else in the merged
tree** — not `common/`, not `events/`, not another `.asset`. Their consumers are
in STNH's `common/`: a naval-museum megastructure, a Maquis empire, Federation
attack wings. We do not vendor any of it, and `maquis_01` and `federation` are
not graphical cultures in STG (`federation_32`, `klingon` and `romulan` are).

**Not exclude either**, per [decision 11](11-fix-source-errors-dont-drop.md).
The Federation attack wings, the Galileo and Delta Flyer shuttles and the Maquis
ships are real Trek content with no home *yet*, and Phase 4 may well want them —
excluding them to buy back 9 log records would be trading content for tidiness.
Acked in `vendor.yml` under `attach_target_ack`, priced at **9 records of 1,308**
in the 2026-08-07 run.

This is an ack with a correctness argument behind it rather than a cost
estimate, which is the distinction `CLAUDE.md` draws: integrating is *worse*,
not merely more expensive. If a future phase wires up a Maquis empire, the ack
names exactly which directories to re-include.

## `check_attach_targets`, and the regex that nearly buried it

The first pass looked for `attachment = { entity = "…" }` — which is not a thing
Stellaris writes — and **reported 0 unresolved against 23 that exist**. The real
form is an assignment whose *key* is the locator and whose *value* is the
entity, and vanilla writes the key both quoted (2,763×) and bare (1,000+×), so
the key's quoting is cosmetic and both are accepted while the value is always
quoted. One more instance of the rule in `CLAUDE.md`: ask vanilla what the form
actually is, because a plausible guess returns a confident zero.
