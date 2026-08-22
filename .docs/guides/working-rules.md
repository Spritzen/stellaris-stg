# Working rules for AI sessions

> **What** — the short list of rules that hold across every task in this repo,
> including the four that will bite you within the first hour.
> **Open when** — the start of any session; before proposing a change that
> touches the build.
> **Then** — [Workflow](workflow.md) · [Writing script](writing-script.md) · [Style guide](../style-guide.md)

## The four invariants

These are the ones that cost a session when they are missed.

### 1. STG is standalone

It vendors its own copy of every source mod it uses. There is **no load order to
lean on at runtime** — the merge is resolved at build time, in harvest order.
[Architecture](../architecture/vendored-merge.md) ·
[harvest order](../architecture/harvest-order.md).

### 2. Never hand-edit a vendored file

Anything under `stg-build/` comes from a source mod. A silent edit is lost on the
next `make vendor` and invisible in review. There are four levers instead, and
which one you want is a real decision:

| Lever | Use it when | Reference |
|---|---|---|
| `src/` override | you genuinely mean to own the whole file | [vendored merge](../architecture/vendored-merge.md#the-rules) |
| `patches:` in `vendor.yml` | you want to change named bytes in someone else's file | same |
| `resample_to_vanilla:` | vendored art shadows a vanilla texture path at the wrong pixel dimensions | [decision 42](../decisions/42-event-picture-geometry.md), [58](../decisions/58-city-set-geometry.md) |
| `renames:` in `vendor.yml` | you need to change *which* of two files defining one key the engine keeps | [decision 29](../decisions/29-merge-semantics-per-directory.md) |

`resample_to_vanilla:` reads its target off the vanilla file at harvest, so it
survives a game patch, and the output stays in the gitignored tree rather than
putting 154 MB of DDS in `src/`. It has two fit modes and which one a pattern
wants is a fact about the art: `crop` re-frames a picture; `canvas` pads a
trimmed file back onto the source's own canvas before scaling, for art
composited by exact pixel position.

`renames:` is the only lever for a contested key, because that is decided by
filename sort within the directory — neither a patch nor an `src/` override can
touch it.

### 3. The build reads `.source/`, never `/workshop`

`.source/<workshop-id>/` is our pinned copy of each source mod. `make sources-sync`
is the only thing that touches `/workshop`, and it is a deliberate act.
`.source/` is a mirror: **never hand-edit it either.**
[Source snapshots](source-snapshots.md) · [decision 09](../decisions/09-source-snapshot.md).

### 4. Fix a source mod's errors; never drop the mod to silence them

Error volume is a cost to pay down, not a reason to lose content. Reach for a
`vendor.yml` patch on the offending lines, an `exclude:` for files that are inert
compat shims for mods not in the harvest, or an `src/` override when we genuinely
mean to own the file.

A source is dropped only on **content** grounds — no Trek fit, breaks another
source, duplicates something we prefer — and the case is made in those terms,
**never by quoting an error count**.
[Decision 12](../decisions/12-fix-source-errors-dont-drop.md).

---

## The session rules

1. **Never hand-edit a vendored file, or anything in `.source/`.** Change
   `vendor.yml` or add to `src/`. `make validate` will catch you; catch yourself
   first.
2. **A source mod updating is a review, not an event.** `sources-status` to see
   it, `sources-diff ID=<id>` to read it, `sources-sync ID=<id>` to accept it,
   then `make vendor`. **Never sync blind.**
3. **Ground every script change in a vanilla file you actually opened.** Not a
   remembered one. Stellaris silently drops files with bad keys, so a
   plausible-looking guess costs a play session to discover.
4. **Never claim in-game verification.** The game runs on the host;
   container-side you validate structure, never behaviour. Say "validates clean"
   and stop. **But once the user reports a live run, read
   `/paradox/stellaris/logs/error.log`** — that is real evidence and it is
   readable from here. The first read of it found a 72 MB log and produced
   [decision 08](../decisions/08-stnh-art-shadows-vanilla.md), with
   `make validate` clean the whole time. [Live runs](live-runs.md).
5. **Never write to `/stellaris` or `/workshop`.** Read-only by design.
6. **Run `make validate` after any script edit**, `make clutter` after any change
   to what is harvested, `make gen-check` after touching a generator in `tools/`,
   and `make docs` after any change to documentation.
7. **Localisation: UTF-8 BOM, every key gets `:0`.** `make fix-bom` repairs it.
8. **When you resolve an open question, write `.docs/decisions/NN-slug.md`** and
   update [planning/status.md](../planning/status.md) and
   [planning/open-questions.md](../planning/open-questions.md) to match. **A stale
   plan is worse than none** — when you find a planning document contradicted by
   what is actually on disk, fix the document.
9. **Never repair only the instances a log names.** If the defect has a rule
   behind it, derive the rule and sweep the tree. See
   [live runs](live-runs.md#a-screen-nobody-opened-is-a-check-that-never-ran) and
   [prescripted empire rules](../reference/prescripted-empire-rules.md) for the
   case that established this.
