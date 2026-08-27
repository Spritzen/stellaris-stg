# Architecture — a vendored merge, driven by a manifest

> **What** — why STG carries its own copy of everything, how `vendor.yml` drives
> the build, and the four rules that follow from it.
> **Open when** — changing what is built, or wondering why a file cannot simply
> be edited.
> **Then** — [Harvest order](harvest-order.md) · [Conflict register](conflict-register.md) · [Source snapshots](../guides/source-snapshots.md)

Standalone means STG carries its own copy of everything it uses. There is no load
order to lean on — **whatever we don't ship, we don't have.**

The naive version is `cp -r` from `/workshop` and pray. Do it once by hand and it
works until the first Stellaris patch, after which nobody — human or AI session —
can tell which of 22,000 files came from where, which are stale, or which were
deliberately edited. That failure is guaranteed, not hypothetical.

**Instead: a manifest-driven vendoring pipeline.** `vendor.yml` declares every
source mod, what to take from it, the order it is applied, and every hand-made
merge decision. `make vendor` replays that manifest to produce the tree.

```
/workshop/<id>        ← Steam's. Read by ONE command, and never by the build.
  ↓  make sources-sync   (deliberate; diff first with make sources-status/-diff)
.source/<id>          ← our pinned copy of each source mod — decision 08
  ↓  make vendor      ← driven by vendor.yml, plus the prune closure (decision 43)
     + src/           ← hand-written STG content, applied last, always wins
stg-build/            ← generated; regenerable; never hand-edited — decision 12
  ↑  symlink (make link, once)
/paradox/stellaris/mod
```

The last arrow points the other way on purpose: the mod folder holds a **link**
to `stg-build/`, not a copy, so `make vendor` alone changes what the game loads.
A copy is a step you can forget, and on 2026-08-02 one sat five hours stale —
[decision 12](../decisions/12-build-dir-and-symlink-deploy.md).

## What this buys, none of which comes from hand-copying

- **Reproducible.** Blow the tree away, `make vendor`, get the same mod back.
- **Auditable.** [`.docs/provenance.md`](../provenance.md) maps every file to its
  source mod and the snapshot revision it came from. When something breaks in 4.5
  you know whose file to look at.
- **Updatable.** `make sources-status` → `make sources-diff ID=<id>` →
  `make sources-sync ID=<id>`. Without `.source/` to diff *against*, this was
  aspirational and every Stellaris patch was an archaeology project.
- **Honest about edits.** Anything hand-modified lives in `src/` or as a declared
  patch, never as a silent edit to a vendored file.

## The rules

### 1. Never hand-edit a vendored file

Change it through `src/` or a `patches:` entry in `vendor.yml`. `make validate`
enforces this by checksum, so an edit **fails the build** rather than surviving to
confuse someone.

**Choose between them by how much of the file you want to own.** A patch changes
named bytes in someone else's file; an `src/` override replaces the whole file. A
one-line typo in a 500-line particle asset is a patch; a file you genuinely mean
to own, like `gfx/FX/pdxmesh.shader`, is `src/`.

Prefer a patch for **how it fails**: if the `from` text stops matching, the build
stops and names the file, where a stale `src/` copy silently keeps shipping our
version of a file the author has since fixed.

> **An `src/` override shadows the SOURCES, not only vanilla.** It is applied
> last, so an override at a path a source also ships replaces that source's copy
> outright. `src/gfx/FX/pdxmesh.shader` was written as "vanilla 4.4 plus STNH's
> five effects" and dropped all 41 that Real Space appends to the same path; Real
> Space's gas giant rings drew with no material and `make validate` was clean
> throughout. `check_src_source_regression` now asks that question over every
> such path — 182 on the build of 2026-08-25, read off the manifest's
> `overwrites`. [Decision 32](../decisions/32-src-shadows-drop-source-declarations.md).

Two further levers exist for what neither can do:

- **`renames:`** changes which of two files defining the same key the engine
  keeps — see [conflict register](conflict-register.md).
- **`resample_to_vanilla:`** re-cuts vendored art that shadows a vanilla texture
  path at the wrong pixel dimensions, reading the target off the vanilla file at
  harvest so it survives a game patch
  ([40](../decisions/40-event-picture-geometry.md),
  [55](../decisions/55-city-set-geometry.md)).

### 2. Never hand-edit `.source/` either

Same rule one level up: it mirrors upstream and the next `make sources-sync`
overwrites it.

### 3. `src/` always wins

It is applied after all vendored content.

### 4. Our own script is prefixed `stg_`

Except compat and override files, which must keep the vanilla or source filename
in order to shadow it. Every such file needs a header comment saying what it
overrides and why, and `make validate` enforces that.
[Writing script](../guides/writing-script.md).

## Size

**Read the numbers off the build, not off this table.** They move on every
harvest change and this section has been stale more than once.
[`.docs/provenance.md`](../provenance.md) is the generated report;
`.vendor-manifest.json` has the per-source split.

*(Read off the build of 2026-08-25. GiB, as `make vendor` prints.)*

| | |
|---|---|
| Gameplay/UI tier — [26 harvest positions](harvest-order.md), 25 with surviving files | 4.7 GiB, 8,026 files |
| STNH — art paths only, ship tree pruned per [decision 17](../decisions/17-walshicus-shipsets-replace-stnh-hulls.md) | 7.0 GiB, 10,929 files |
| Walshicus' 22 Trek shipsets | 2.5 GiB, 3,092 files |
| `src/` — hand-written | 5.0 MB, 359 files |
| **Built mod, total** | **14.3 GiB**, 22,406 files, 49 sources + `src/` |
| `.source/` — 51 mods: the 49 harvested plus Kammarheit and Apocryphos | 22 GB apparent, **~0 real** (reflinked; [decision 08](../decisions/08-source-snapshot.md)) |

*(The gameplay/UI tier holds 26 harvest positions but only 25 leave a file
behind: URP harvests one file and `src/` shadows it —
[harvest order](harvest-order.md#why-the-universal-resource-patch-is-last-not-first).
Re-derive the whole table by counting `generated[*].id` in
`.vendor-manifest.json`, which is where these figures came from.)*

*(Ariphaos is subscribed but was never snapshotted — [decision 02](../decisions/02-drop-ariphaos.md)
predates `.source/`. It is the one mod in `/workshop` with no copy here.)*

Disk is not a concern, and it is **never the argument for removing anything** —
[decision 43](../decisions/43-clutter-pass.md) removed 1.0 GB and says so
explicitly. Two things that *do* follow from the size:

- **Git tracks the inputs, never the output.** The generated tree and `.source/`
  are ignored; `sources.lock.yml` records which revision of each source they were
  built from. Full list: [repo layout](../reference/repo-layout.md#what-is-generated-and-what-is-not).
- **Game load time is 45–55 s**, of which almost all is `init application`,
  against a 40 s native-vanilla floor. Six runs between 2026-08-08 and
  2026-08-25 measured 49.3 / 49.4 / 55.4 / 46.8 / 48.5 / 45.1 s on content that
  only grew, so **the spread is noise and the trend is flat** — settled, not
  worth another sample. Not painful enough to act on, and the obvious lever —
  the ship-model prune — has already been pulled. Every run's figure is
  `init application` in `/paradox/stellaris/logs/time.log`.

## Line endings

Several sources ship CRLF (PD - Planet View's `planet_view.gui` among them), so a
naive `diff` against vanilla reports *every* line as changed — 16,964 on a file
whose real delta is 74. The vendor tool normalises line endings before
checksumming, or `make validate`'s hand-edit detection produces false positives
on every rerun.
