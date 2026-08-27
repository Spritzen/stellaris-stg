# Architecture — how the build is designed

> **What** — the vendored-merge design: what `vendor.yml` drives, in what order
> sources apply, and how contested paths are settled.
> **Open when** — changing what is built, or explaining why a file in the tree is
> the one it is.
> **Then** — [Guides](../guides/README.md) for the commands · [Validation](../validation/README.md) for what enforces this

| File | |
|---|---|
| [vendored-merge.md](vendored-merge.md) | **Start here.** Why STG vendors everything, the four rules, and the size of the result |
| [harvest-order.md](harvest-order.md) | The order sources apply in, why URP is last, what was dropped |
| [stnh-art.md](stnh-art.md) | The additive-only rule, the 162 contested paths, and the four namespace wirings |
| [conflict-register.md](conflict-register.md) | Every contested path and how it was settled; the explicit excludes |

## The shape in one diagram

```
/workshop/<id>        Steam's. Read by ONE command, never by the build.
  ↓  make sources-sync
.source/<id>          our pinned copy — decision 08
  ↓  make vendor      driven by vendor.yml, then the prune closure
     + src/           hand-written STG content, applied last, always wins
stg-build/            generated; never hand-edited — decision 12
  ↑  symlink
/paradox/stellaris/mod
```

**There is no load order to lean on at runtime.** The merge is resolved at build
time, and every hand-made call in it is recorded either in `vendor.yml` or in
[a decision](../decisions/README.md).
