# 31 — `@variables` in art files are file-local, and copying an entity leaves them behind

**Status:** decided, 2026-08-07

## The report

The 2026-08-07 live run threw 137 `persistent.cpp:41` records, 6.8% of
`error.log`:

```
Error: "Malformed token: @general_scale, near line: 70
" in file: "gfx/models/ships/zz_stg_shipsets.asset" near line: 70
```

Six variables, 137 references: `@general_scale` (50), `@sovereign_scale` (43),
`@assault_cruiser_scale` (15), `@adv_cruiser_scale` (15), `@saber_scale` (11),
`@corvette_scale` (3). All in one file — the one `tools/gen_shipsets.py`
generates.

## What was wrong

`zz_stg_shipsets.asset` held **137 `@name` references and zero `@name`
declarations.**

`Emitter.expand` copies a donor entity's declaration out of its source `.asset`
verbatim, because `clone` discards sibling locators
([decision 30](30-clone-discards-sibling-locators.md)). Those donor files declare
their own scale variables at the top:

```
@general_scale = 0.85          # yridian_transport.asset, line 1
…
entity = { name = "…" scale = @general_scale … }
```

The copy took the `scale = @general_scale` line and left the declaration behind
in a file the engine reads separately. Every one of those 137 entities loaded
with no scale.

## Two things that make the fix non-obvious

**There is no single value to hoist.** Across the source tree `@general_scale`
takes 22 distinct values (0.45 … 1.6) and `@corvette_scale` 26 (1 … 12.0) —
these are per-shipset art scalars that happen to share a name. Lifting one
value to a global would silently resize ships in every set but one. The
substitution has to happen **per donor file, as the body is read**, which is
what `resolve_vars` does.

**The scope is not file-local, and assuming it was would have broken the check.**
The obvious rule — "an `@name` must be declared in the file that uses it" —
reports 96 references across 18 *vanilla* files as broken. `@large_trail_L` is
referenced by 17 vanilla `.asset` files, every one of which leaves its own copy
**commented out**, because `common/scripted_variables/03_scripted_variables_ships.txt`
declares it globally.

So the resolvable set is: **the file's own declarations, plus
`common/scripted_variables/`.** Under that rule vanilla's own 1,788 art files
score exactly 0, which is what says the rule is right, and STG's 6 are the only
findings.

## Decision

1. **`tools/gen_shipsets.py` resolves a donor's `@variables` as it reads the
   body** (`resolve_vars`), per file, never hoisted.
2. **The generator refuses to write an output with a surviving `@name`.** It
   fails naming the variables, because the donor is still known at that point
   and is not recoverable from the output afterwards.
3. **`check_asset_variables` in `tools/validate.py`** checks the whole built
   tree — this defect had already been hand-patched once in a *vendored* file
   (`@plasmasmallplasmuzzle` in ASB Ironman's `_ballistics_entities_ap.asset`,
   see `.docs/provenance.md`), so it is not only ours to get wrong.

Calibrated by reintroducing one reference into the built tree: reported.

## The rule worth keeping

**Copying script out of its file takes the text and leaves the context.** An
`@variable` is the visible case; anything else resolved relative to the
declaring file will behave the same way. `Emitter.expand` already knew this
about `clone` and locators (decision 30) — same lesson, one level down.
