# The clutter closure — is every file referenced?

> **What** — the reachability closure behind `make clutter` and the prune stage
> of `make vendor`: what it asks, how its scope was calibrated, and why it is the
> one check built to be generous.
> **Open when** — a file disappeared from the build, or you are changing what is
> harvested.
> **Then** — [decision 43](../decisions/43-clutter-pass.md) · [check design, rule 1](check-design.md#1-a-check-that-deletes-is-not-a-check-that-reports) · [Workflow](../guides/workflow.md)

```bash
make clutter          # census the built tree
make clutter-vanilla  # the same closure over /stellaris — the calibration floor
make clutter ARGS=--list            # print the paths
make clutter ARGS='--list gfx/models'  # narrow to one tier
```

`tools/clutter.py` asks the **dual** of every check in `validate.py`: twenty-odd
of those ask *does this reference resolve*; none had ever asked *is this file
referenced*. Every file is **reachable**, **shadowing** (a vanilla path, so
vanilla's own references reach it — [decision 07](../decisions/07-stnh-art-shadows-vanilla.md)),
**kept**, or **orphan**.

## The burden of proof is inverted

Content that nothing referenced used to stay unless someone argued it out. It now
**goes unless someone argues it in**, under `clutter_keep:` in `vendor.yml` with
a correctness reason.

That supersedes [decision 35](../decisions/35-attach-edges-into-pruned-art.md)'s
second half, which had looked straight at 115 unreachable entities and kept them
("trading content for tidiness"). The trade is now made deliberately, and for a
currency decision 35 did not have available: not tidiness, but **intentionality**
— a tree where every file is accounted for is one where the next include-list
mistake is visible instead of absorbed.

## Four things about it that are not obvious

**1. It deletes where every other check reports.** An edge it fails to follow
becomes a deleted file that rendered perfectly. It is therefore deliberately
*generous* — resolving by path, then filename, then stem; treating every
declaration file as a root wherever it sits; scanning `.mesh` files as **bytes**,
because a mesh names its textures inside the binary and no text file mentions
them.

**2. The root set is the part that deletes content if it is wrong.** It was
established by running the closure over `/stellaris` alone, where a convention
the closure cannot see shows up as a directory that is almost entirely
unreferenced. That found four: `gfx/interface/icons/` (path derived from a
database key), `gfx/portraits/city_sets/`, `gfx/portraits/environments/` and
`gfx/map/`. **Each carries its vanilla count in the code beside it.**

**3. The floor is 2.67%.** Vanilla runs 1,132 of its own 42,335 files
unreferenced, including 99 `.editordata`, 6 `.bak` and ~950 meshes, anims and
wavs Paradox shipped and stopped using. **Vanilla has the fourth class too.** The
floor varies **thirty-fold** between tiers, so it is recorded per tier and every
finding is read against its own. `make clutter-vanilla` re-measures it.

**4. Prune scope is a calibration result, not a convenience filter.** Only
`gfx/event_pictures` (0.3% floor, 56.7% found), `gfx/portraits` (0.0%, 1.8%) and
`sound` (1.6%, 12.1%) are pruned. `gfx/models` at 5.2% against vanilla's own 4.9%
is **reported**, because at that rate the check cannot tell our leftovers from
Paradox's and gating on it would be gating on noise. **700 orphans remain (build
of 2026-08-25**, against the 706 [decision 43](../decisions/43-clutter-pass.md)
measured — the difference is art a later `.gfx` reached, not a change to the
closure**)**, and `make validate` prints the count every run. Read the current
figure off that line rather than this sentence.

> Widening the prune scope means moving a tier in `tools/clutter.py` **with a new
> ratio written beside it**.

## Not an `exclude:` list, deliberately

813 event-picture paths written into `vendor.yml` would be correct the day they
were written and silently wrong after the next `make sources-sync` — the exact
artefact [decision 22](../decisions/22-group-c-texture-references.md) showed
cannot track reference edges. The closure re-derives itself every build.

**Nothing is destroyed:** `.source/` is untouched, and a source mod that starts
declaring a sprite over one of these gets its picture back with no edit anywhere.

## The consequence to know about

`vendor.yml` alone no longer describes the output. **The manifest plus the
closure do**, and [`.docs/provenance.md`](../provenance.md) lists every removal.
