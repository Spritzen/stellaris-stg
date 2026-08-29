# Star Trek Galaxies — documentation

> **What** — the map. Every category, what it is for, and which document answers
> which question.
> **Open when** — the start of a session, or any time you don't know where
> something is written down.
> **Then** — pick a row below. If you are new: [guides/working-rules.md](guides/working-rules.md).

STG is a total-conversion Stellaris mod, built by vendoring 49 Workshop mods into
one standalone tree. The build is generated; the inputs are `vendor.yml`, `src/`
and `.source/`. [`CLAUDE.md`](../CLAUDE.md) at the repo root is the short version
of this page.

---

## Start here, by what you are doing

| I want to… | Read |
|---|---|
| **start a session and not break anything** | [guides/working-rules.md](guides/working-rules.md) |
| know what state the project is in | [planning/status.md](planning/status.md) |
| know what to work on | [planning/open-questions.md](planning/open-questions.md) |
| run the build, or find a `make` target | [guides/workflow.md](guides/workflow.md) |
| write or edit content in `src/` | [guides/writing-script.md](guides/writing-script.md) |
| understand why a file in the tree came from where it did | [architecture/conflict-register.md](architecture/conflict-register.md) |
| change what is harvested | [architecture/harvest-order.md](architecture/harvest-order.md) |
| understand a `make validate` finding | [validation/checks.md](validation/checks.md) |
| write a new check | [validation/check-design.md](validation/check-design.md) |
| plan what a playthrough should cover | [runs/README.md](runs/README.md) |
| read `error.log` after the user played | [guides/live-runs.md](guides/live-runs.md) |
| **act on what the last live run found** | [planning/static-galaxy-plan.md](planning/static-galaxy-plan.md) — the plan that came out of it, and the answer to "why is the galaxy not Trek". **Built, and run twice** — [decision 86](decisions/86-static-galaxy-scenario.md) is what shipped, [87](decisions/87-static-map-lanes-are-generated.md) is the one thing the 2026-08-27 run broke on, and the 2026-08-28 Klingon run passed it; the reasoning is [85](decisions/85-create-country-initializers.md) and [84](decisions/84-static-galaxy-is-the-mechanism.md). Then [decisions/83-design-database-is-not-the-cause.md](decisions/83-design-database-is-not-the-cause.md) for the 2026-08-26 Vulcan run's save; then [planning/open-questions.md](planning/open-questions.md) for what is left. Baselines in [planning/status.md](planning/status.md). The write-ups of the earlier runs (Federation 2026-08-10, Vulcan 2026-08-22) were retired once every finding in them had landed in a decision — decisions [76](decisions/76-random-names-are-loc-keys.md)–[80](decisions/80-selector-textures-that-resolve.md) are what they left behind |
| find out whether a question is already settled | [decisions/README.md](decisions/README.md) |
| look up a term | [reference/glossary.md](reference/glossary.md) |
| write documentation | [style-guide.md](style-guide.md) |

---

## The categories

| Folder | What it holds | Index |
|---|---|---|
| [guides/](guides/) | **How to do a thing here** — environment, commands, conventions, the session rules | [README](guides/README.md) |
| [architecture/](architecture/) | **How the build is designed** — the vendored merge, harvest order, contested paths | [README](architecture/README.md) |
| [validation/](validation/) | **What enforces all of it** — the check catalogue, how to write one, acks, the prune closure | [README](validation/README.md) |
| [planning/](planning/) | **State and direction** — status, phases, open questions, scope | [README](planning/README.md) |
| [decisions/](decisions/) | **One numbered file per resolved question**, with the reasoning and what it cost | [README](decisions/README.md) |
| [reference/](reference/) | **Lookups** — glossary, repo layout, database rules, external links | [README](reference/README.md) |
| [runs/](runs/) | **What a live run should cover** — written before the run, one file per playthrough. **Empty today**, and that is the normal state: a plan is spent when its run is over | [README](runs/README.md) |
| [analysis/](analysis/) | **What a live run measured** — written only on request, one file per run, and **written to be retired** once its findings land in a decision. **Empty today** | [README](analysis/README.md) |

Plus two single files:

- [style-guide.md](style-guide.md) — how documentation here is written, and the
  `make docs` check behind it.
- [provenance.md](provenance.md) — **generated** by `make vendor`: every file →
  its source mod → the snapshot revision it came from.

---

## How to navigate this efficiently

**Every document opens with a nav card** giving what it is, when to open it, and
where to go next. Read the card before the body; it is there so you can decide
not to read the body.

**Follow the `Then` links rather than searching.** They are maintained, and
`make docs` fails if one of them dangles.

**Decisions are the ground truth.** Where a guide summarises and a decision
disagrees, the decision is right and the guide is stale — fix the guide.

**Cite by path.** `.docs/validation/check-design.md` from code, a relative link
from inside `.docs/`. Never a bare filename.

---

## Four things that are true before you read anything else

1. **STG is standalone.** No load order at runtime; the merge is resolved at
   build time.
2. **Never hand-edit `stg-build/` or `.source/`.** Both are generated. Change
   `vendor.yml` or `src/`.
3. **The build reads `.source/`, never `/workshop`.**
4. **Fix a source mod's errors; never drop the mod to silence them.**

The long form, with the levers for each, is
[guides/working-rules.md](guides/working-rules.md).
