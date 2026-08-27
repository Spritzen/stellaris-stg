# 31 — One entity name declared twice silently decides which art renders

**Status:** decided, 2026-08-07

## The report

`Duplicate of <name> added to entity system` was the **largest single group in the
2026-08-07 live run: 576 records, 28.6% of `error.log`** — and the largest in
every live run before it, as [decision 16](16-stnh-shipsets-on-a-vanilla-chassis.md)
already noted.

## Most of it is deliberate, and that took measuring to establish

**558 of the 576 names are also declared by vanilla.** ASB Ironman
(`_ballistics_entities_ap.asset`) and Starbase Extended 3.0
(`_starbase_entities_SBX_3_0_*.asset`) redeclare vanilla entities from
*differently-named* files, which is how a mod overrides vanilla art without
shadowing its path. The engine notes the second declaration and moves on. Not
ours, and not a defect.

Reporting the 576 as a number would have been useless. The 18 that vanilla does
not declare are the whole of the interesting part, and one of them was real.

## The one that was ours

`yridian_destroyer_entity` was declared twice inside our own tree:

| File | Source | `pdxmesh` |
|---|---|---|
| `gfx/models/ships/other/yridian_destroyer.asset` | Star Trek: New Horizons | `federation_01_corvette_frame_mesh` |
| `gfx/models/ships/yridian/destroyer/yridian_destroyer.asset` | Yridian Shipset (+ our decision-28 override) | `yridian_destroyer_mesh` |

Yridian ship art comes from the Walshicus shipset now
([decision 17](17-walshicus-shipsets-replace-stnh-hulls.md)); STNH's leftover copy
points the same name at a **Federation** hull. `other/` sorts before `yridian/`,
so STNH's is read first — and **which of two duplicate declarations the engine
keeps is recorded nowhere and leaves no trace on disk.** Rather than bet on it,
the conflict is removed: STNH's file is excluded in `vendor.yml`. The only name
unique to it, `yridian_destroyer_section_1_entity`, is referenced by nothing in
the built tree.

The other 17 are third-party files duplicating within themselves (SBX declares
its `*_stronghold_entity` pairs twice in one file) or within their own mod family
(PD Gestalt vs PD Machine arcologies). Inert, and not ours.

## The check, and the rule it rests on

**Vanilla declares 8,409 entities and never names one twice — not once.** So a
second declaration inside one tree is something only the merge produces, and that
is a rule derived from vanilla rather than asserted.

`check_duplicate_entities` reports cross-file duplicates **within the built tree**
as warnings, modelled on `check_key_conflicts`: the finding is "confirm this is
the winner you want", and only a live run or the source's intent settles it.

Scoping to the built tree is the useful choice, not a limitation — a mod file
redeclaring a *vanilla* name is the deliberate-override case above, and vanilla's
own file is not in the tree, so those 558 never surface.

It stands at **13** findings, all third-party against third-party, none acked.

## The second one that mattered: Saturn in Sol

`gas_giant_saturn_entity` was the first finding chased down, and it was not
cosmetic. PD declared it with `gas_giant_saturn_diffuse.dds` at `scale = 1.2`;
Real Space with `gas_giant_31_diffuse.dds` at `@gas_giant_scale` (= 1). Same
mesh, same normal and specular maps, two different diffuse paintings — so the
undetermined duplicate was deciding **what Saturn looks like on every Sol start.**

**Real Space wins, because it owns the name.** All six
`solar_system_initializers` that place the entity are Real Space's — `sol`,
`sol_solsector_small`/`large`, `federations`, `pre_ftl`, `unplugged` — at
`size = 35`, `has_ring = yes`, `orbit_angle = 170`, and `@gas_giant_scale` is the
variable keeping its other gas giants consistently sized. PD's 1.2 would have
rendered Saturn 20% larger than the system built around it.

PD's declaration is **renamed, not deleted** (`pd_gas_giant_saturn_entity`, a
`vendor.yml` patch), so its art stays in the tree under a name nothing places and
switching later is a one-line change. Nothing dangles: PD's own
`events/pd_engine.txt` still calls
`set_planet_entity = { entity = "gas_giant_saturn_entity" }`, which Real Space
declares — and that event gates on `planet_size = 30` where Real Space builds
Saturn at 35, so it is unlikely to fire here at all.

### A note on the request that started it

This came in as "rescale `gas_giant_saturn_diffuse.dds` to match
`gas_giant_31_diffuse.dds`", and there was nothing to rescale: **both are already
2048×1024.** The 2 MB against 1 MB is DXT5 against DXT1, and the `1.2` against
`@gas_giant_scale` is the *entity* scale, not the texture. Worth recording
because the file sizes and the word "scale" both invite the wrong conclusion, and
resizing either texture would have changed nothing while leaving the real defect
in place.

PD's DXT5 alpha is fully opaque across all 131,072 blocks, so that extra megabyte
carries no information — but converting it would mean owning a vendored texture in
`src/` and masking upstream art updates to save 1 MB out of 15 GB, which is not a
trade worth making.

## The mistake this check made first, which is the part worth keeping

The check shipped reporting **0** against a pair it was written for, and the
cause was not the walk or the scope. Finding a declaration used a
nesting-limited regex ending at the name:

```python
_ENT_DECL = re.compile(r'entity\s*=\s*\{(?:…)*?name\s*=\s*"([^"]+)"', re.S)
…
seen.setdefault(m.group(1), []).append((rp, m.group(0)))   # "body"
```

`m.group(0)` on a lazy match is `entity = { name = "X"` **and nothing more**. So
every declaration of one name normalised to the same string, the
bodies-differ test was comparing a value against itself, and the content
comparison that was supposed to suppress false positives suppressed *everything*.

This is [check-design.md](../validation/check-design.md)'s "a check that cannot fail is worse than an
absent one" for the third time, and the second time in the same shape as
`check_vanilla_regression`: **finding a name is not the same problem as getting
the body, and a regex that solves the first will quietly hand you the wrong
answer to the second.** Bodies are brace-counted now (`_entity_declarations`).

Calibrated by restoring the excluded file: reported. It also tripped
`check_vendored`'s hand-edit guard on the way, which is that check working.
