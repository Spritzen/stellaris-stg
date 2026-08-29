# 104 — The engine writes a version-exact, merge-aware script reference on every launch, and its modifier list is not the allowlist it looks like

**Status:** decided, 2026-08-29
**Follows** [decision 103](103-setup-log-is-a-load-manifest.md), which opened the
log directory as a surface worth reading rather than a place `error.log` lives.

## Why it was opened

The user noticed a `script_documentation/` folder beside `setup.log` and asked
what it contains and whether it is any use. Nothing in `.docs/` named it. One
citation reached into it — [98](98-withdrawn-scenarios-are-referenced-by-name.md)
quotes `triggers.log` for the sentence that `galaxy_size` is a trigger resolving
a `setup_scenario` by name, which is the finding behind 353 records — but that
was a session reaching for evidence, not a documented source.

## What it is

Five files the engine writes at the end of database load
(`game_application.cpp:1397-1432`, `modifier.cpp:2308`):

| file | contents |
|---|---|
| `effects.log` | 1,056 effects — description, syntax example, `Supported Scopes` |
| `triggers.log` | 1,087 triggers, same shape |
| `scopes.log` | 99 scope links — `Supported Scopes` → `Output Scope` |
| `modifiers.log` | 47,510 modifier names with categories |
| `localizations.log` | 44 loc scopes, 333 promotions and properties |

**They are written from the merged database, not from vanilla**, and that is the
whole reason they are worth anything. Evidence, all from the 2026-08-28 run:
568 modifier lines are derived from our own `sr_acean` and `sr_eludium`; 757 job
families include vendored `pd_` jobs; the same run's `setup.log` carries 3,345
static modifiers with `stg_` tags and three `stg_` event namespaces. All five
files are stamped `19:37`, the same load window as `setup.log` and `game.log`,
against a `Game Version: Pegasus v4.4.6` line — **the version we target**.

So it is the one description of *our own build* that is both version-exact and
merge-aware, which is exactly what the wiki cannot be
([external-sources.md](../reference/external-sources.md) already records that at
least one page there contradicts another).

## The check that was built and then not shipped

The obvious use is an allowlist: a **misspelled modifier is the one failure mode
that produces no `error.log` record at all** — the engine drops it silently — so
it is precisely the class [validate.py](../../tools/validate.py) exists to see.
`check_modifier_names` was written and measured before being proposed.

**It fails on vanilla.** Read as an allowlist over `/stellaris/common/`, the dump
scores **125 unknown names in 12,464 modifier references — a 1.0% floor, not 0**.

**And the 125 are not noise.** Sorted against vanilla's own English
localisation, **117 of the 125 have a loc key** — `biologist_jobs_bonus_workforce_mult`,
`defensive_stations_armor_mult`, `arkship_fire_rate`, the whole
`<category>_jobs_bonus_workforce_mult` family. A modifier vanilla ships loc for
is a real modifier. The remaining 8 are arithmetic and structural fields
(`days`, `divide`, `icon_frame`, `is_difficulty`, `max`, `min`, `multiply`,
`subtract`) that the extractor should never have counted. **The dump is a lower
bound on what exists, and reading it as a census inverts its meaning.**

Widening the oracle to *dump ∪ vanilla loc keys* — 193,463 names — repairs the
floor: **vanilla 0, `src/` 0, the merged build 0**. Confirmed a second time with
a wider extractor that flattens nested blocks and covers the eight
`*_modifier = { }` variants: **vanilla 6** (five of them triggers inside weight
blocks, one a real omission), **`src/` 0 of 96 references, build 0 of 2,167**.

**So the check is not shipped, and that is the finding.** Our content has no
unknown modifier name to catch, under any oracle variant tried.
[validate.py's own rule](../../tools/validate.py) is that a check must have a
defect it would have caught, "because a check that cannot fail is worse than an
absent one — it reports a number". A `check_modifier_names` here would report
`0 of 2,167` forever and buy a 117-entry ack list of *vanilla's own names* for
the privilege. That ack would not be an acknowledgement; it would be an
admission that the oracle is wrong.

The measurement is the deliverable. It is also reusable: if a future run ever
does produce a silently-dropped modifier, the union oracle and its floors are
written down here and the check is an afternoon.

## Not snapshotted into the repo

Considered and rejected. The five files run to 4.7 MB, `modifiers.log` alone 4.1
MB, and they regenerate on every launch. `.source/` is the obvious home and is
**gitignored** ([repo-layout.md](../reference/repo-layout.md)), so a snapshot
there would not survive a clone and any check reading it would silently degrade
to a no-op — the failure this decision is otherwise avoiding. With no check
depending on the files, there is nothing to make reproducible, and committing a
4 MB generated artefact to serve a reference use is cost without a reader.

**What ships instead** is that they are named, described and censused:
[reference/game-logs.md](../reference/game-logs.md) documents all five, and
`make logs` ([105](105-ten-log-files-nothing-had-named.md)) fails if one stops
being written. Read them live, at `/paradox/stellaris/logs/script_documentation/`,
after any run.
