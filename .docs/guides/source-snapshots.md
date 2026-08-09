# Source snapshots — `.source/`

> **What** — why the build reads a pinned copy of every source mod rather than
> `/workshop`, and the four-step procedure for accepting an upstream change.
> **Open when** — a source mod has updated, or you are about to run any
> `sources-*` target.
> **Then** — [Vendored merge](../architecture/vendored-merge.md) · [decision 09](../decisions/09-source-snapshot.md)

The pipeline has four stages, and the first one is not automatic:

```
/workshop/<id>  --make sources-sync-->  .source/<id>  --make vendor-->  stg-build/  <--symlink--  /paradox/stellaris/mod
```

`/workshop` is Steam's directory: it changes whenever a mod author publishes and
disappears if you unsubscribe. So the build doesn't read it. `.source/<id>/` is a
byte-exact copy of each source mod that we take on purpose, and it is what
`make vendor` harvests. A source that isn't snapshotted is a build error naming
the fix — there is deliberately **no fallback to `/workshop`**.

`.source/` is a mirror. **Never hand-edit it** — the next sync overwrites it.

## The procedure

```bash
make sources-status              # what changed upstream (size+mtime; seconds)
make sources-status DEEP=1       # hash all 44,584 files instead
make sources-diff ID=937289339   # read the actual change, file by file
make sources-sync ID=937289339   # accept it for that one source
make sources-sync                # re-snapshot everything
make sources-list                # what .source/ holds, with versions
```

**Never sync blind.** `status` → `diff` → `sync` → `vendor` → `validate` is the
order; the whole point is that a source-mod update is something you **read and
accept** rather than something that happens to you mid-rebuild.

## It costs nothing

`/workshop` and this repo are the same btrfs subvolume, so the copy reflinks: 51
snapshots, 22 GB, no measurable disk consumed
([decision 09](../decisions/09-source-snapshot.md) has the timings as first
measured, when only 29 mods were snapshotted).

`sources.lock.yml` — the one part of this that git tracks — records a
`tree_sha256` per source, so you can tell at a glance whether a mod actually
changed. [`.docs/provenance.md`](../provenance.md) carries it too: provenance
answers *which version* of a source mod is in the tree.

## `orphan` is a success

`orphan` in `sources-status` output means a mod is in `.source/` but no longer in
`/workshop` — unsubscribed on Steam. The build still works. **That is what the
snapshot is for.**
