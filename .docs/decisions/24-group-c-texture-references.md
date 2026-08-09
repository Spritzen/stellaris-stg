# 24 — Group C is a texture problem, and the include list could not see it

*Decided 2026-08-03. Closes the "open since the last run — group C" item in
plan.md §8. Supersedes nothing; it is the third round of the same lesson as
[decision 18](18-walshicus-shipsets-replace-stnh-hulls.md)'s prune.*

## What the run showed

The 2026-08-03 live run (startup 51 s, 3,187 records, `enabled_mods` correct)
carried 190 group-C records: **139** `pdxassetutil.cpp` *Failed to find
texture*, **25** `texturehandler.cpp` naming the resolved path, and **26**
`Couldn't find mesh` / `Failed to find entity` across five mesh names.

The previous reading of this class was that bare filenames resolve relative to
the declaring file's own directory, which made it look unfixable — the engine
would go on looking in `federation/defiant/` no matter which directory we
vendored. That reading was wrong, and the measurement that settles it is blunt:

**Not one of the 139 named textures was anywhere in the built tree.** 132 were
in `.source/688086068/` and 7 existed in no source and no vanilla install.
There was nothing subtle about the resolution rule to work around; the files
were simply absent.

The engine keeps a global texture index keyed by basename, and says so itself:

```
Duplicate texture 'Hull_Main_1_TMP.dds' found
  (current path  gfx/models/ships/stnc_shipset_shared/textures/Hull_Main_1_TMP.dds,
   previous path gfx/models/ships/federation/constitution_refit/Hull_Main_1_TMP.dds)
```

That is one basename compared across two directories. So a texture is found if
its *filename* is loaded anywhere, and the 25 resolved-path records are the
engine reporting where it looked after the index missed — not evidence that the
index is per-directory.

## Why the include list missed them

A `.gfx` `meshsettings` block names its textures as bare filenames:

```
meshsettings = {
    texture_diffuse = "transparent_diffuse.dds"
    ...
}
```

`vendor.yml`'s STNH `include:` is scoped by directory. It had been driven to
closure against the *mesh name* check and the *mesh file* check, both of which
were satisfied — and textures live apart from the meshes that use them. 98 of
the 132 were in one place, `gfx/models/ships/shared_assets/`, STNH's
cross-culture texture library, which no include prefix had ever named.

This is the same shape as the two earlier bites recorded in plan.md §6:
*an include list scoped by directory does not respect reference edges*, and it
converges on whatever question the checks are asking. One file type further
down each time.

## What was done

**Textures — 132 recovered.** `gfx/models/ships/shared_assets` is taken as a
directory: 251 `.dds` and one `.ini`, with no `.gfx`, `.asset` or `.mesh` in it,
so it declares nothing and cannot drag a culture back in. The other 34 are named
file by file, because a directory there would pull back the ship meshes decision
18 pruned. Each of the 132 had exactly one home in `.source/`, so no path is
ambiguous.

**Meshes — 5 recovered, by declaring rather than shadowing.** Each is *used* by
an `.asset` in a directory we keep and *declared* by a `.gfx` in one we prune.
Those four `.gfx` files declare 2, 3, 11, 20 and 77 meshes between them, so
taking them whole would have traded 5 dangling references for roughly 100. The
five declarations are re-issued in
`src/gfx/models/ships/stg_stnh_restored_station_meshes.gfx`, verbatim from STNH,
with the `.mesh` and `.dds` files they name added to the include list — plan.md
§4's *prefer declaring to shadowing*.

**8 acked as absent.** Six `infernal_ring_world_*` named by Real Space – System
Scale's planetary entities asset, plus `ross_deflector_out_diffuse.dds` and
`transp_green.dds` from STNH. All exist in no source and in no vanilla install,
so no include can reach them; they are upstream bugs, and the cost is one
untextured material each, not a missing mesh. Vanilla 4.4's own
`_planetary_entities.asset` names none of the six, so these are *not* a
4.4 regression of decision 08's kind — System Scale invented references to art
it does not carry. Listed under `texture_basename_ack` in `vendor.yml`.

Build: 23,247 → 23,550 files. `make validate` clean, and the 676 ship
mount-point baseline did not move.

## The check that now asks the question

`check_gfx_file_refs` deliberately skipped bare filenames, on the correct
grounds that resolving them *from the mod root* produced 330 false positives.
The consequence was that `texture_*` was never asked about **in any form** —
the class was unchecked, not partially checked.

`check_texture_basenames` asks the question the engine actually answers: is this
basename loaded anywhere in the built tree or in vanilla? Zero false positives,
where the root-relative form had 330.

Two details, both taken from CLAUDE.md's rules rather than invented:

- **Match on the stem, not the filename.** Vanilla's own
  `gfx/models/ships/other/_other_meshes.gfx` asks for `event_ship_07_diffuse.tga`
  and `ancient_destroyer_normal.tga` while vanilla ships only the `.dds` — all
  five of vanilla's `.tga` references. An extension-sensitive check reports
  vanilla itself. *Derive the allowlist from what vanilla does.*
- **Sweeping the rule beat reading the log.** The log named 139; the check found
  five more the log never could — the Borg unicomplex adaptor lights, which are
  only drawn by someone who flies to one. *A screen nobody opened is a check
  that never ran.*

**Calibrated by reverting**: with `gfx/models/ships/shared_assets` removed from
the built tree the check raises errors; with it restored, `make validate` is
clean. It can fail.

## What is still open

The single `planets\nospec.dds` record is a Windows path separator baked into a
`.mesh` binary, which no text check can reach — no `.gfx` or `.asset` in the
tree contains a backslash reference. The check reports backslash references
rather than normalising them away, so if one ever appears in a text file it
fails instead of silently passing.

Whether the 132 recovered textures actually improve what is on screen is
something only the user's eyes can grade; a texture that resolves produces no
log record. The next live run should show group C at its floor.
