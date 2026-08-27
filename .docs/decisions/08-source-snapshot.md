# 08 — The build reads `.source/`, not `/workshop`

**Decided:** 2026-08-01. **Supersedes the "no source-mod archive; the
deployed mod is the backup" position taken earlier the same day.**

`make vendor` no longer reads `/workshop`. It reads `.source/<workshop-id>/`, a
byte-exact copy of each source mod that we take deliberately with
`make sources-sync`.

```
/workshop/<id>        upstream. Steam's. Changes when a mod author publishes,
                      disappears when you unsubscribe.
  │  make sources-sync            ← deliberate, reviewable, the only step that
  ↓                                 reads /workshop
.source/<id>          our pinned copy. The input to the build.
  │  make vendor
  ↓
stg-build/            the mod tree
  ↑  symlink (make link, once) — decision 12
/paradox/stellaris/mod
```

## Why

The earlier position accepted two risks to avoid an archive. Both turned out
to be cheaper to fix than to carry.

**1. Unsubscribing destroyed the ability to rebuild.** Its mitigation was "the
deployed mod is the backup" — which is a 17 GB *output*, not an input. You
cannot re-run a merge from it, diff it against an update, or tell which of
23,507 files came from where. It backs up playing, not building.

**2. Upstream changes arrived silently.** With `/workshop` as the build input,
any `make vendor` picks up whatever Steam last downloaded. A source mod
updating between two rebuilds changes the mod with nothing recording that it
happened — exactly the archaeology problem plan.md §2 built the vendoring
pipeline to prevent, reintroduced one level up. plan.md §2 already claimed
"**Updatable.** A source mod updates on Steam? Re-run, diff, review just what
changed." There was nothing to diff *against*. This is what makes that true.

## What made it free

`/workshop` and this repo are the **same btrfs subvolume**
(`/dev/nvme0n1p2`, `subvol=/@home`), so the copy is a reflink:

| | |
|---|---|
| 40,778 files, 18.7 GB snapshotted | **21 s** |
| Disk consumed | **none measurable** — 146 G free before and after |
| `make sources-status` (size+mtime) | 1.6 s |
| `make sources-status DEEP=1` (sha256, both trees) | 15 s |

Reflinked extents are shared until one side is written to, so this is a real
independent copy, not a link: Steam replacing a file upstream leaves ours
intact. `cp --reflink=auto` degrades to a full copy on a filesystem without
reflink support — correct, just no longer free.

Verified: the tree built from `.source/` is identical to the tree previously
built from `/workshop`, per-source file counts across all 29 sources.

## The rules this adds

1. **`make vendor` never reads `/workshop`.** A source that has not been
   snapshotted is an error naming the fix, never a silent fallback. Falling
   back would defeat the entire point.
2. **`make sources-sync` is the only thing that reads `/workshop`** — and it
   is a deliberate act, not a build step. Nothing runs it automatically.
   Look before you accept: `make sources-status`, then
   `make sources-diff ID=<id>`, then `make sources-sync ID=<id>`.
3. **Never hand-edit `.source/`.** Same rule as the vendored tree, one level
   up. It is a mirror; the next sync overwrites it. Changes belong in `src/`
   or in `vendor.yml`. `make sources-status` reports an edited snapshot as
   drift against upstream, which is confusing in exactly the way a silent
   edit deserves.
4. **An orphaned snapshot is a success, not a failure.** If a source is in
   `.source/` but gone from `/workshop`, `sources-status` says `orphan` and
   the build still works. That is the whole purpose.

## What is recorded

| Path | Tracked in git | What it holds |
|---|---|---|
| `.source/<id>/` | no (18.7 GB) | the mirror |
| `.source/.meta/<id>.json` | no | every file with a sha256 — the basis for `DEEP=1` |
| `sources.lock.yml` | **yes** | one entry per source: name, file count, bytes, snapshot time, declared version, and `tree_sha256` |

`tree_sha256` is the sha256 of the sorted per-file hash listing. It identifies
an upstream revision exactly: re-run `make sources-sync` and if the hash is
unchanged, the mod did not update. `.docs/provenance.md` now carries it per
source too, so the provenance report answers *which version* of a source mod
is in the tree, not just which mod.

## What did not change

`descriptor.mod`, thumbnails and licences still sit at each source's root and
are still never vendored — `.source/` mirrors them, `make vendor` skips them
(vendor.yml, "Root-level files"). The snapshot is deliberately the **whole**
mod, not just the paths `include:` selects: a filtered snapshot could not show
you that upstream added something worth including.

## Revisit if

The repo moves to a filesystem without reflink support and 18.7 GB of real
duplication starts to matter. The fallback then is snapshotting only the
`include:` prefixes, at the cost described just above.
