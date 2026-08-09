# 53 — the 13 duplicate entity declarations, triaged

**Resolved 2026-08-08.** Closes the first of plan.md §8's three standing-warning
items. Continues [decision 33](33-duplicate-entity-declarations.md), which built
the check and shipped `duplicate_entity_ack` empty because none of its findings
had been looked at.

## The question

One entity name declared by two files, where the engine keeps one, logs the
other, and **records nowhere which** — so the duplicate silently decides what
renders. Thirteen of these stood in `make validate` with no triage path.

Reading the bodies split them into four classes, and only one of the four is a
defect our merge created.

| | count | disposition |
|---|---|---|
| One body is **vanilla's own**, the other a live 4.x mod's deliberate override of it | 6 | suppressed by content, no ack |
| STNH's 3.12 copy against **Real Space – System Scale's rescale** | 5 | repaired — renamed in `vendor.yml` |
| STNH's dummy against **vanilla's habitat art** | 1 | repaired — renamed in `vendor.yml` |
| Two PD-family files, no visible difference | 1 | acked, with the measurement |

## 1. Six that were never a merge conflict

`ai_planet_01_entity`, `machine_planet_01_entity`, `infernal_01_city_planet_entity`,
`toxic_planet_04_entity`, `debris_medium_01_entity`, `debris_medium_02_entity`.

Decision 33 established that a mod redeclaring a **vanilla** entity from a
differently-named file is how it overrides vanilla art without shadowing the
path — deliberate, and 558 of the 576 duplicate records in the 2026-08-07 run.
Those are invisible to the check because vanilla's own file is not in the tree.

**Except when a source forks the vanilla file and carries the body in with it.**
PD - More Arcologies ships `gfx/models/planets/_planetary_entities.asset`, and
its bodies for those four planet entities are **byte-identical to vanilla 4.4's**
— measured, not assumed. So the pair the engine faces is exactly the pair a stock
PD install faces, with PD's `_zz_pd_overwrite_` and `_vanilla_pd_arcologies_overwrites`
files doing what their names say. The same is true of the two `debris_medium`
entities, where STNH's copy of the vanilla path carries vanilla's body and Real
Space – System Scale supplies the override.

`check_duplicate_entities` now drops a copy whose body is vanilla's own before
comparing. **Suppressed by content rather than by ack**, per CLAUDE.md's
preference: an ack stays silent forever, where this starts reporting again by
itself the day either side stops matching vanilla.

### The narrowing that the first cut needed, which is the part worth keeping

The rule as first written — "one body is vanilla's, so it is the deliberate
override idiom" — suppressed **seven**, and the seventh was
`orbital_habitat_01_entity`, a real finding (§3 below). The premise hidden inside
it is that the *other* declaration is a live mod's considered override of 4.4. For
a 3.12-era total conversion it is not; it is a leftover from the game that source
was written against.

That distinction already exists in `validate.py` — it is what
`check_vanilla_regression` scopes itself to (`additive_only` sources plus any
declaring a `supported_version` below the target), and what
[decision 38](38-real-space-drops-sol-neighbours.md) reasoned about from the other
side. It is now factored out as `_legacy_sources()` and shared by both checks, so
the suppression applies only when the overriding declaration comes from a current
source. STNH is not one, and the habitat finding came back.

**A suppression rule is a check that deletes.** It was calibrated by watching what
it removed, not by reading it — which is how the over-reach was caught at all.

## 2. Five that undo Real Space – System Scale

`collapsar_globule_entity_{small,medium}`, `purple_globule_entity_{small,medium}`,
`debris_large_01_entity`.

System Scale declares each of these rescaled — `@entity_scale_1 = 1.5` is
vanilla's own value and `@entity_scale_3 = 4.5` is three times it. STNH's copies
carry the unscaled originals (1, 5, 1.5). Neither body is vanilla's, so nothing
suppresses them, and if STNH's wins the object renders at a third of the size the
system around it was built at.

plan.md §4 settled this class already for
`common/scripted_variables/00_realspace_scripted_variables.txt`: **System Scale
wins, because Real Space's copy would undo the submod entirely.** The same
reasoning, one database over. STNH's five declarations are renamed `stnh_*` by
`vendor.yml` patch — renamed rather than deleted, per decision 33's Saturn
precedent, so the art stays in the tree under a name nothing places.

Nothing dangles. System Scale still declares every one of the five names, so the
three `attach` edges inside STNH's own `_other_entities.asset` bind to the
rescaled entity — which is what an ordinary Real Space install does.

## 3. The one that decided what every habitat looks like

`gfx/models/ships/suliban_01/suliban_01_helix.asset` declares
`orbital_habitat_01_entity` as a clone of `suliban_01_orbital_habitat_entity`,
commented in STNH's own source as a *"Dummy entity to remove error logs from
planet class"*.

In STNH's tree that comment is the whole story: nothing else declares the name, so
any body silences the error. In ours vanilla's real habitat art declares it too —
and **the name is not Suliban art**. It is what `entity = "orbital_habitat"` in
`common/planet_classes/` resolves to, on five planet classes across four files.
So the undetermined winner decides whether every empire's habitats render as
vanilla's orbital ring or as the Suliban helix.

Vanilla wins: habitat art is shared by all 101 empires and the helix is one
species' ship. The Suliban empire flies the Walshicus `suliban` set anyway
([decision 18](18-walshicus-shipsets-replace-stnh-hulls.md)). Renamed, not
deleted; `suliban_01_orbital_habitat_entity` and its eight growth stages are
untouched.

**Nothing would have reported this.** It logs one `Duplicate of …` line among
576, and habitats that render as a helix are not an error — they are art. Only
reading the two bodies says which is which.

## 4. The one that is genuinely inert

`pd_machine_planet_shield_effect_entity`, declared by PD - More Arcologies'
`_pd_gestalt_arcologies.asset` and PD's `_pd_ma_hive_arcologies.asset`, pointing
at `pd_machine_planet_shield_effect_mesh` and `pd_ma_machine_planet_shield_effect_mesh`.

**The winner cannot change what renders**, and that is measured rather than
assumed: both meshes name the same `planet_shield_effect.mesh` with the same
`PdxMeshAlphaAdditiveAnimateUV` shader, and their two diffuse textures are
byte-identical — same sha256, 2,097,280 bytes each. Both files also attach the
entity only from their own arcology entities.

Acked, because there is no difference to decide. Proving it automatically would
mean resolving mesh names to their `.gfx` bodies and comparing the textures those
name — the indirection [decision 35](35-station-section-attach-points.md) warns
about — to buy one finding.

## Result

`duplicate_entity_ack` holds one name. `make validate`'s 13 duplicate-entity
warnings are 0, and two of the thirteen were real defects nothing else could see.
