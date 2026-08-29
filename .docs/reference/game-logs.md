# Game logs — every file in `/paradox/stellaris/logs/`

> **What** — all nineteen files the game writes, what each contains, what fills
> it, and whether it is any use to us.
> **Open when** — you are about to read a log after a live run and want to know
> whether you are reading the right one, or `make logs` has just told you a file
> changed state.
> **Then** — [Live runs](../guides/live-runs.md) for the procedure · [Decision 104](../decisions/104-script-documentation-is-a-version-exact-oracle.md) · [Decision 105](../decisions/105-ten-log-files-nothing-had-named.md)

The game runs on the **host**. Its user data is at `/paradox/stellaris/`, and
the logs one level below that. Every file here is rewritten from scratch on each
launch — there is no history, so **a log is evidence about exactly one run**.

**The table in [`tools/logs.py`](../../tools/logs.py) is the source of truth for
this page**, and `make docs` holds the two to each other. That is not ceremony:
this page exists because [live-runs.md](../guides/live-runs.md) claimed for weeks
that `debug.log` was empty while it was not ([105](../decisions/105-ten-log-files-nothing-had-named.md)).

Run **`make logs`** after a live run, beside reading `error.log`. It censuses the
directory and fails when a file changes state.

---

## The six that carry content

| file | what it holds |
|---|---|
| `error.log` | **the errors.** The standard read after every run — [live-runs.md](../guides/live-runs.md). ~282 KB in the 2026-08-28 run |
| `setup.log` | **a load manifest, not an error log.** 15 classes, 13 of them numbered dumps of what loaded. ~1.1 MB is normal — it is proportional to content, not to failure. Triaged in [103](../decisions/103-setup-log-is-a-load-manifest.md), and its `trait.cpp:663` dump is an external control for `check_prescripted_empires` |
| `game.log` | game version, defines counts, galaxy seed, and **one line per event a player or the AI answered**, with a `playerEventId`. The only record of what the player actually saw and in what order. It settled the 2026-08-28 first-contact report when `error.log` had nothing |
| `system.log` | GPU, audio and OS init, written *before* the database loads. Attached to crash reports alongside `error.log` |
| `time.log` | `Startup real time`, and the per-phase breakdown. **The only way to split init-window records from in-play ones**, which changes what a record means |
| `debug.log` | engine load-time notices. 72 records in the 2026-08-28 run: 71 `economic_unit_template.cpp:29` *Category already set to X, overriding* — **64 of them from vanilla's own `specimens.txt`** — and one `building_type.cpp:261`. **None of it ours.** Low value, but it is not empty, and a document said it was |

Plus `error.log.YYYY-MM-DD` — **rotated copies kept by hand**, not by the game.
Two survive (`2026-08-08`, `2026-08-10`) and they are load-bearing: decision
[98](../decisions/98-withdrawn-scenarios-are-referenced-by-name.md) uses both as
the before-side of a comparison. Do not delete them.

## The eight that are empty, and what would fill them

All eight are created in the same syscall at process start — `19:36:58.641` in
the 2026-08-28 run, before the game version line — and then never written. They
are **channels, not evidence**: an empty one means the feature was not switched
on, not that nothing went wrong.

| file | what fills it |
|---|---|
| `event_data.log` | the **`dump_event_data`** console command (`player_events_only` narrows it) |
| `script_profiling.log` | the **`script_profiler`** console command — run it once to start, again to dump |
| `script_profiling_summary.log` | the summary half of that same dump |
| `pdxsdk.log` | **`libPDXSDK.so`**, not the game. It alone is mode `0644` where the rest are `0600`, because a different process writes it |
| `ai.log` | the AI debug channel — no writer |
| `info.log` | general info channel — no writer |
| `memory.log` | memory instrumentation — no writer |
| `profiler.log` | the engine profiler — no writer |

The four console/SDK writers were confirmed by string-searching
`/stellaris/stellaris`, which ships **unstripped and with debug info**. The four
marked *no writer* are the ones that search found **no** format string for — so
on this install nothing in a release build writes them, and the honest reading is
that they need a debug build rather than a command we have not found.

**If one of these ever holds bytes, read it.** That is a state nobody has seen on
this install, and `make logs` fails on it deliberately so it cannot pass
unnoticed.

## `script_documentation/` — five files, regenerated every launch

Written at the end of database load, **from the merged database** — so they
describe *our build*, not vanilla. Full analysis in
[104](../decisions/104-script-documentation-is-a-version-exact-oracle.md).

| file | contents |
|---|---|
| `effects.log` | **1,056 effects** — description, syntax example, `Supported Scopes` |
| `triggers.log` | **1,087 triggers**, same shape |
| `scopes.log` | **99 scope links** — `Supported Scopes` → `Output Scope` |
| `modifiers.log` | **47,510 modifier names** with categories. **Not a complete allowlist** — see below |
| `localizations.log` | the `[Scope.Property]` vocabulary: 44 scopes, 333 promotions and properties |

**This is the best reference we have for writing script**, and better than the
wiki on the two axes that bite: it is *version-exact* (Pegasus v4.4.6, whatever
is installed) and *merge-aware* — 568 of those modifier lines are derived from
our own `sr_acean` and `sr_eludium`, and 757 job families include vendored `pd_`
jobs. It is already load-bearing:
[98](../decisions/98-withdrawn-scenarios-are-referenced-by-name.md) rests on
`triggers.log` saying `galaxy_size` resolves a `setup_scenario` by name.

> **`modifiers.log` is not the allowlist it looks like.** Vanilla's own
> `common/` uses **117 modifier names it does not list** — the entire
> `<category>_jobs_bonus_workforce_mult` family among them — and vanilla ships
> loc keys for all 117. Checked against it as an allowlist, vanilla scores
> **125 unknown names in 12,464 references**. Read it as a *lower bound* on what
> exists, never as proof that a name does not.
