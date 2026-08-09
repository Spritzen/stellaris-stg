# 45 — Unreferenced content goes by default, and the closure decides

**Status:** **closed 2026-08-07.** Phases 0–4 of the clutter-pass plan are
carried out. *(That planning file was deleted after the work landed; the
mechanism it described is now [validation/clutter.md](../validation/clutter.md).)* The tree went
from 23,555 files / 15.0 GB to **22,242 files / 14.0 GB**: 990 files removed by
a reachability closure that re-runs on every `make vendor`, and 323 by explicit
`vendor.yml` excludes with an argument each.

Static only. `make validate` is unchanged at `ok — 17 warning(s)` and no live
run has happened yet — which is the standing limit of every art change here
(decisions 08 and 42).

## The decision

**The burden of proof is inverted.** Before: content that nothing referenced
stayed unless someone argued it out. After: it goes unless someone argues it in,
and the argument goes in `vendor.yml` under `clutter_keep:` with a correctness
reason.

Every file in `stg-build/` is now in one of four classes, and `make clutter`
names which:

| class | meaning | count |
|---|---|---|
| **reachable** | a root the engine enters names it, directly or through a chain | 20,108 |
| **shadowing** | it sits at a vanilla path on purpose, so vanilla's own references reach it ([decision 08](08-stnh-art-shadows-vanilla.md)) | 1,428 |
| **kept** | `clutter_keep:` names it, with a written reason | 0 |
| **orphan** | none of the above | 706 |

706 is not zero and the definition of done in the plan asked for zero. See
*What is reported and not failed on* — that deviation is deliberate and it is
the calibration talking.

## What this reverses

**[Decision 37](37-attach-edges-into-pruned-art.md), second half.** It found
115 entities across 4 files reachable from nowhere and decided *"Not exclude
either… excluding them to buy back 9 log records would be trading content for
tidiness."* That trade is now made, on purpose, and for a reason decision 37
did not have available: it was weighing tidiness against content, and the real
currency is **intentionality** — a tree in which every file is accounted for is
one where the next include-list mistake is visible instead of absorbed.

Decision 37's specific four files are untouched: they live under `gfx/models`,
which this pass reports and does not prune. What changes is the default around
them.

**[Decision 03](03-content-scope.md)'s "STNH art — take all of it"** is softened,
not reversed, the way [decision 18](18-walshicus-shipsets-replace-stnh-hulls.md)
already softened it. 813 of STNH's 1,434 event pictures go because no
spriteType in the merged tree or in vanilla declares them.

**[Decision 12](12-fix-source-errors-dont-drop.md) does not reverse.** No source
mod is dropped. Rule 2 of it — *"an `exclude:` for files that are genuinely
inert here"* — already permitted everything below.

**plan.md §2's "Disk is not a concern" still holds.** The 1.0 GB is a
consequence, never the argument. Nothing here was removed for being large.

## The instrument, and the one thing to understand about it

`tools/clutter.py` asks the **dual** of every check in `tools/validate.py`.
Twenty-odd checks there ask *does this reference resolve*; none had ever asked
*is this file referenced*. That is exactly why the tree looked the way it did —
[decision 24](24-group-c-texture-references.md)'s lesson was that an include
list converges on whatever question the checks ask, and the question had only
ever been asked forward.

**This closure deletes, where every other check only reports, so its two errors
are not symmetrical.** An edge it fails to follow becomes a deleted file that
rendered perfectly. So it is deliberately generous at every choice:

- a reference resolves by exact path, then by path relative to the declaring
  file, then by filename, then by **stem**, against the built tree and vanilla
  at once
- every declaration file (`.txt`, `.gfx`, `.gui`, `.asset`, `.yml`, `.shader`,
  `.fxh`) is a root wherever it sits, not only where the engine really walks
- one regex catches any token that looks like an asset filename, rather than
  one regex per keyword the way the forward checks must
- extension-less quoted tokens resolve by stem, because `.anim` and `.animsm`
  are named that way constantly
- `.mesh` files are scanned as **bytes**, because a mesh names its textures
  inside the binary and no text file mentions them: vanilla's
  `danielsfinatestskepp.mesh` carries `ship_mask.dds`, `nonormal.dds` and
  `nospec.dds` and nothing else in the tree does

Over-approximating reachability costs a file left in the tree. The other
direction costs a screen going blank, and that is the failure decisions
[24](24-group-c-texture-references.md),
[34](34-src-shadows-drop-source-declarations.md) and
[37](37-attach-edges-into-pruned-art.md) already record three times over, one
file type further down each time.

## The root set is the part that deletes content if it is wrong

A file the engine picks up **by existence**, or whose path it derives from a
database key, looks exactly like an orphan. Getting one wrong is the whole risk
of this pass, and the set was established by measurement rather than memory:
run the closure over `/stellaris` alone, and a convention the closure cannot
see shows up as a directory that is almost entirely unreferenced.

That found four conventions, none of which is visible in any file:

| directory | vanilla orphan / reachable | the convention |
|---|---|---|
| `gfx/interface/icons/` | 4,579 / 4,834 | path derived from a database key — `icons/deposits/d_ash_storms.dds` is `d_ash_storms` in `common/deposits`, and 1,600 of the 4,579 are literally a depth-0 key in some `common/` file. The rest are the same convention with an affix, and there is no achievements database on disk at all. |
| `gfx/portraits/city_sets/` | 361 / 1 | `<graphical_culture>_city_l0N[_devastated].dds` |
| `gfx/portraits/environments/` | 152 / 2 | `pc_<planet_class>_sky*.dds` |
| `gfx/map/` | 38 / 39 | fixed renderer names plus `star_classes/<key>.dds` |

Plus `gfx/animation_state_machines/*.animsm` — 99 of vanilla's 100 are named by
nothing anywhere. Its sibling `.editordata` is deliberately **not** a root:
vanilla ships 99 of those and they are editor output, so leaving them findable
is a result, not a blind spot.

Each entry in `ROOT_DIRS` carries its vanilla count in the comment beside it.

## The floor, and what it is for

`make clutter-vanilla` runs the identical closure over `/stellaris` alone. Every
finding there is a false positive **by construction** — a file vanilla ships and
vanilla itself never names.

> **42,335 files examined, 1,132 unreferenced — 2.67%.**

And the residue is real rather than blindness: 99 `.editordata`, 6 `.bak`, 2
`.ods` spreadsheets in `common/component_templates`, and ~950 meshes, anims,
textures and wavs Paradox shipped and stopped using.
`gfx/models/portraits/avian/avian_05_portrait_sad_2.anim` is one of them, and
vanilla's own `_avian_portrait_animations.asset` declares avian_01, 02, 04 and
06 while shipping 05's four anims. **Vanilla has the fourth class too.**

The floor is not one number. It varies thirty-fold between tiers, so it is
recorded per tier in `VANILLA_FLOOR` and every finding is read against its own.

## What is pruned and what is only reported

Scope is a calibration result, not a convenience filter. `PRUNE_TIERS` in
`tools/clutter.py` carries this table beside it:

| tier | floor | stg-build | verdict |
|---|---|---|---|
| `gfx/event_pictures` | 0.3% | 813 / 1,434 | **prune** — 190× the floor, and the edge is a single hop: a texture no spriteType names cannot draw |
| `gfx/portraits` | 0.0% | 72 / 3,919 | **prune** — floor is zero over 797 non-convention vanilla files |
| `sound` | 1.6% | 107 / 886 | **prune** — 7.5×. STNH ships 73 weapon `.wav` files and declares none of them in any `.asset`, in its own tree or anywhere in `/workshop` |
| `gfx/models` | 4.9% | 634 / 11,943 | report — 5.3% is vanilla's own leftover rate; indistinguishable |
| `gfx/interface` | 1.7% | 24 / 2,254 | report — 1.1%, below the floor |
| `gfx/particles` | 1.3% | 22 / 591 | report — 3.7%, same order |
| `gfx/ui_overhaul_qhd` | — | 28 / 412 | report — mod-only path, so there is no vanilla floor to read it against at all |

### What is reported and not failed on, and why the plan's "done" moved

the clutter-pass plan's definition of done asks that
`make validate` fail when any file is outside the three classes. It fails only
inside the prune scope. Gating on `gfx/models` would be gating on noise: at 5.3%
against vanilla's 4.9% the check cannot tell our leftovers from Paradox's, and a
gate that fires on a number it cannot interpret is the thing CLAUDE.md warns
about from the other direction. 706 orphans remain, all in report tiers, and
`make validate` prints the count on every run so it cannot be forgotten.

Widening the scope means moving a tier in `clutter.py` **with a new ratio
written beside it** — which reads as the piece of work it is, the way
`check_section_attach_points` records 66:1 over stations against 147:41 over all
ship sizes.

## Not an `exclude:` list — a prune stage

813 event-picture paths written into `vendor.yml` would be correct the day they
were written and silently wrong after the next `make sources-sync`. That is
precisely the artefact [decision 24](24-group-c-texture-references.md) showed
cannot track reference edges.

So `tools/vendor.py` gained a **prune stage**, after every source, after `src/`,
after patches and after renames — because whether a file is referenced can only
be asked of the merged tree. It re-derives itself every build, so **a source mod
that starts declaring a sprite over one of these gets its picture back with no
edit anywhere.**

Nothing is destroyed. `.source/` is untouched and holds 805 of the 813 pruned
event pictures and all 52 leader backgrounds. The
`gfx/portraits/leaders/*.dds` are a case in point: they became unreachable when
`gfx/portraits/asset_selectors/paragon_backgrounds.txt` was excluded (it is
gated on STNH scripted triggers we do not vendor), and `vendor.yml` says
"Rebuild properly in Phase 3". When that selector is written, the art returns by
itself.

**The cost is real and belongs on the record:** `vendor.yml` alone no longer
describes the output. The manifest plus the closure do, and
`.docs/provenance.md` gained a *Pruned files* section listing every removal.

## One pass, no cascade

Every declaration file is a root, and every root is reachable by construction,
so the prune can never remove something that was making something else
reachable. One pass is sufficient and a second would find nothing.

## Calibrated by reverting, because a check that cannot fail is worse than none

Reporting 990 removals proves nothing on its own — that is the
`check_vanilla_regression` and `check_duplicate_entities` trap, twice
(decision 33). So the closure was blinded to one declaration file at a time:

| hidden | files that fall out of the closure |
|---|---|
| `interface/realspace_eventpictures.gfx` | 12 event pictures |
| `interface/pd_unique_event_pictures.gfx` | 3 event pictures |
| `gfx/models/ships/federation/federation_all_ships.gfx` | **159** — 104 textures, 53 meshes |
| `sound/sth_soundeffects.asset` | 0 — it groups names that other files map to disk |

The chain is genuinely followed, and the zero is the *right* zero.

The findings were then cross-checked by a method the closure has nothing to do
with: `rg` for the basename of ten sampled pruned files across `stg-build` and
`/stellaris`. All ten: named by 0 files.

Finally, the gate itself was tested by putting an unreferenced `.dds` into
`gfx/event_pictures/` and confirming `make validate` goes from
`ok — 17 warning(s)` to `1 error(s)`, and back on removal.

## Phase 1 — the junk tier, and the glob that would have deleted the VO system

Editor by-products are **not** a reachability question and `make clutter` is not
asked to answer one; they go in `global_excludes:` by extension:
`*.bak` (3), `*.wip` (3), `*.wavorig` (2), `*.pdn` (1), `*.dcm` (2), plus
`stnc_shipset_shared/textures/*.png` (3 — each has a `.dds` twin that
declarations name by path 1, 7 and 19 times) and STNH's extensionless
`borg_01/test_diff`, which is a 128×128 DDS no loader can open by any name.

**The plan's insistence on sweeping the submod shims individually rather than
with a glob on `*submod*` was load-bearing.** Of the seven files:

- `sound/sth_submod_sound.asset`, `sound/sth_submod_category.asset` and
  `sound/gui/STH_submod_gui_sound_effects.asset` are the **entire Trek
  diplomacy VO system** — 968 lines of `soundeffect` blocks mapping Antedean,
  Bajoran, Borg, Breen and Bynar greetings onto files
- `music/songs_submod.{asset,txt}` declare STNH's own ten `newhorizonssong*`
  tracks

A `*submod*` glob would have silently deleted all five.

The two that do go are the Planetary Diversity placeholders, and **not** for
the URP reason the plan predicted — the submod they stub for *is* in the
harvest, and their names *are* referenced. The argument is different and
stronger: each declares a key that a mod in the harvest defines for real, with
a body of `potential = { always = no }`. `common/governments/civics` is LIOS so
the real file wins on filename sort today; the stub `!_pd_placehold_…` sorts
**first** and would win outright in any FIOS directory, and nothing on disk
records which of the two this is ([decision 29](29-merge-semantics-per-directory.md)).
Real Space's `patrons_list.yml` goes too: two keys read by nothing, naming real
people.

`common/component_templates/*.csv`, which the plan listed as junk from an
extension census, turned out to **shadow a vanilla path** — vanilla ships both
files. They are class 2 and stay.

## Phase 2's other finding — two directories that are 100% unreferenced

`gfx/speeddial/` (30 files) and `gfx/tiny_outliner/` (8) are the only
directories in the tree with **zero reachable siblings**. Both come from UIOD -
Dark UI, which re-skins the Speed Dial and Tiny Outliner mods — neither of
which is in the harvest, so nothing declares a sprite over either directory.
Excluded in `vendor.yml`; same class as the five URP topbar-compat files
decision 12 excluded, and the one nobody swept for afterwards.

## Phase 3 — the nine non-English localisation trees

Not unreachable; deliberate upstream content. 235 files across nine language
directories plus 38 loose per-language files at `localisation/` root and under
`replace/`. Dropped on the same taste grounds as
[decision 11](11-drop-cinematic-camera-and-ambient-soundtracks.md): STG is
personal and never published (plan.md §1) and is played in English, so each is
a file the engine parses and never reads a key from. **Asked and answered
explicitly rather than swept.** `localisation/` went 314 files → 45.

Both glob forms are needed: the directory globs catch four files whose names
carry no language tag (`pd_uniques_l_spanish..yml`,
`…_l_vanilla_overwrites_french.yml`, one `_l_chinese` inside `simp_chinese/`),
and the filename globs catch the 38 where no directory names a language.

## What is left, and what to look at next

Of the 706 report-tier orphans, two are worth a look and neither is this
decision's to settle:

- **`music/Anthem_of_the_United_Federation_of_Planets.ogg`.** STNH ships it and
  no `music/*.txt` declares a `song` for it, so it never plays. That is a
  defect to repair with an `src/` addition, not clutter to delete — which is
  why `music` is not in the prune scope.
- **`gfx/worldgfx/`, 6 files at 11.5% against a 2.4% floor.** Colour-correction
  and lava textures. Small, but above its floor.

## Files

- `tools/clutter.py` — the closure, the root set, `VANILLA_FLOOR`, `PRUNE_TIERS`
- `tools/vendor.py` — `apply_prune()`, and the *Pruned files* provenance section
- `tools/validate.py` — `check_unreferenced()`, gating the prune scope
- `Makefile` — `make clutter`, `make clutter-vanilla`
- `vendor.yml` — `clutter_keep:`, the junk extensions, the localisation trees,
  and six per-source excludes with an argument each
