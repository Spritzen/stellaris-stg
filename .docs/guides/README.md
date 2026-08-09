# Guides — how to do a thing in this repo

> **What** — the procedural half of the documentation: environment, commands,
> conventions, and the rules that hold across every task.
> **Open when** — you are about to *do* something rather than understand
> something.
> **Then** — [Architecture](../architecture/README.md) for *why* the build looks
> the way it does · [Documentation map](../README.md)

| File | |
|---|---|
| [working-rules.md](working-rules.md) | **Start here.** The four invariants and the nine session rules |
| [environment.md](environment.md) | The four mounts, which are writable, and the host boundary |
| [workflow.md](workflow.md) | Every `make` target, the daily loop, and what each step proves |
| [writing-script.md](writing-script.md) | Read vanilla first; `stg_` prefixing and its two exceptions; tabs, BOMs, shadowing |
| [source-snapshots.md](source-snapshots.md) | `.source/` and the `status → diff → sync` procedure |
| [deployment.md](deployment.md) | The symlink, the derived `.mod` path, and the three systems that must agree |
| [live-runs.md](live-runs.md) | Reading `error.log` after the user plays — standard practice |

## The one-minute version

```bash
make vendor && make validate     # the loop
```

Never hand-edit `stg-build/` or `.source/`. Never write to `/stellaris` or
`/workshop`. Never claim a change works in-game — the game runs on the host.
