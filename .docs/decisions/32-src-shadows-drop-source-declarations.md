# 32 — An `src/` override shadows the *sources* too, not just vanilla

**Decided 2026-08-07**, from the live run of that morning.

## What happened

`error.log` carried four records nobody had a category for:

```
pdxassetutil.cpp:604  Failed to create material with shader PdxMeshPlanetRingsRS
                      for mesh [patternShape] in gfx/models/planets/gas_giant_rings_0{1,2}.mesh
pdxmeshobject.cpp:62  Attempt to draw textured mesh 'gfx/models/planets/gas_giant_rings_0{1,2}.mesh'
                      with an effect 'Effect doesn't exist' that has no samplers in pixel shader
```

Real Space's gas giant rings were drawing with no material. The reference is
ordinary and plain-text — `shader="PdxMeshPlanetRingsRS"` in
`gfx/models/planets/rs_rings_entities.asset`, four times.

Real Space declares that effect **twice on purpose**: once in its own
`gfx/FX/rs_pdxmesh.shader`, and again in its `gfx/FX/pdxmesh.shader`, which is
vanilla 4.4 byte-for-byte plus 411 appended lines. We ship the first and not the
second, because `src/gfx/FX/pdxmesh.shader` — written for decision 07 as
"vanilla 4.4 plus STNH's five effects" — replaces the whole path. The effect
survived in a file the engine loads and the material still failed, so the
operative file for a mesh material is `pdxmesh.shader` and nothing else.

## Why nothing caught it

Two checks each had a reason to stay silent, and both were correct on their own
terms:

- `check_vanilla_regression` compares an override against **vanilla**. Vanilla
  never declared `PdxMeshPlanetRingsRS`, so there was nothing to lose.
- `check_dangling_shaders` asks whether a named effect is **declared in any
  `.shader` file**. It was — in `rs_pdxmesh.shader`. The check's regex reads
  `shader="X"` with no spaces perfectly well; the model of "declared anywhere is
  good enough" is what was wrong, and the engine's answer is narrower.

The gap between them is the whole finding: **`src/` is applied last and beats
vendored content, so an override at a path a source also ships silently replaces
the source's copy — and no check was asking about that half.**

## Decision

1. `src/gfx/FX/pdxmesh.shader` carries a second marked block with the four Real
   Space effects that resolve: `PdxMeshPlanetRingsRS`,
   `PdxMeshPlanetRingsRSShadow`, `PdxMeshShipHalo`, `PdxMeshPlanetHalo`.
2. The other 37 are **not** restored, and this is not a preference. 36 are the
   `OmniMesh*` family, whose four pixel shaders (`PixelOmniMeshShip`,
   `PixelOmniMeshED`, `PixelOmniMeshEDSphere`, `PixelOmniMeshWhiteHole`) exist
   nowhere in vanilla, in Real Space, or in the merged tree — they are dead in
   Real Space itself and importing them would import 37 effects that cannot
   compile. The 37th, `PdxMeshNavigationButtonGate`, is the **last block of Real
   Space's file and is unterminated upstream**: its closing brace is simply
   missing, the file ends on a commented-out field, and nothing references it.
   Inventing a repair for a block nobody uses is not our call to make.
   Recorded in `vendor.yml` under `src_regression_ack`.
3. `tools/validate.py` gains `check_src_source_regression`, which asks
   `check_vanilla_regression`'s question about sources instead of vanilla. It
   needs no guessing about which source an override beat: `.vendor-manifest.json`
   already records all 162 such paths with the loser named.

## The two things worth carrying

**Identity has three shapes, and this check needs all three.** Depth-0 block keys
are identity in a `.txt`; the nested `name` is identity in an `.asset`
(decision 31); the `Effect`/state declaration line is identity in a `.shader`.
`_declared_keys` is now shared rather than reimplemented per check.

**A dropped declaration is not a lost one, and the first cut of this check said
otherwise twice.** Sources move declarations between their own files: Real Space
keeps 11 star classes in `realspace_planet_classes.txt` rather than
`00_planet_classes.txt`, and `rs_pdxmesh.shader` repeats the three render states
its `pdxmesh.shader` block also declares. Both read as regressions until the
rescue existed — a declaration counts as present if any sibling in the same
database directory (or, for a shader, anywhere in `gfx/FX/`) still makes it.
Without that, the check's first run produced 2 confident false positives out of
3 findings.
