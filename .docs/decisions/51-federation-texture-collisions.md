# 51 — the federation/ vs starfleet_tng/ texture pairs are the same artwork

**Resolved 2026-08-08.** Closes the second of plan.md §8's three standing-warning
items. Continues [decision 44](44-coalition-of-hope-takes-vul.md), which built
`check_duplicate_textures`, acked the Walshicus shared library on plan.md §4's
review, and deliberately left these three findings unacked as *"a different
boundary — two shipsets, not one library meeting one family"*.

## The question

A `.mesh` names its textures **by bare filename inside the binary**, so the engine
keeps one global filename → texture map and one file wins for every mesh that
asks. Vanilla repeats exactly 1 basename in 7,711. Three pairs stood:

| basename | STNH | Walshicus |
|---|---|---|
| `starfleet_olympic_{diffuse,normal,specular}.dds` | `federation/olympic` | `starfleet_tng/cruiser` |
| `starfleet_galaxy_hull_01_specular.dds` | `federation/galaxy` | `starfleet_tng/battleship` |
| `ESD-Lights1_normal.dds` | `federation/starbase` | `starfleet_tng/starbase` |

Both sides are live. `starfleet_tng` is the Walshicus set six STG empires fly
(decision 17); STNH's `federation/` is kept as the donor `tools/gen_shipsets.py`
borrows stations and civilian craft from for the five cultures with no Walshicus
set.

## Measured, not judged

Decision 44 could only say of the Walshicus library that last-wins *"rests on the
two variants looking alike, which no static check can confirm and only eyes on a
live run can"*. For these three, that is not true — the files can be decoded and
compared. Mean absolute difference at 64×64, RGB:

| file | difference | formats |
|---|---|---|
| `starfleet_olympic_specular.dds` | **0.000%** | 1024² raw vs 1024² DXT5 |
| `starfleet_galaxy_hull_01_specular.dds` | **0.000%** | 1024² raw vs 1024² DXT5 |
| `starfleet_olympic_diffuse.dds` | **0.001%** | 1024² raw vs 1024² DXT1 |
| `ESD-Lights1_normal.dds` | **0.044%** | 256×16 both |
| `starfleet_olympic_normal.dds` | **1.164%** | 1024² raw vs **2048²** DXT5 |

**The control matters more than the numbers.** Two textures that genuinely differ
score 23–27% on the same metric — `starfleet_olympic_diffuse` against
`starfleet_galaxy_hull_01_specular` is 27.1%, and against its own specular map
23.6%. So the metric discriminates, and 0.001% is not a degenerate comparison of
two blank decodes.

The filenames were the clue and the pixels confirm it: each names the ship class
it belongs to on *both* sides, because both authors cut them from the same source
art. STNH ships them uncompressed, Walshicus as DXT.

## Disposition

Acked, on the STNH side only. Whichever copy the engine keeps, both shipsets draw
the same picture; the one real consequence is that if STNH's 1024² Olympic normal
map wins, the Walshicus cruiser's normal map is half resolution — a sharpness
difference, not a hull wearing another ship's skin, which is the failure the check
exists for.

Acking `federation/{olympic,galaxy,starbase}` rather than `starfleet_tng/*` keeps
the live Walshicus shipset unacked, so a **new** collision against it still
reports.

## Why the check was not taught to do this

Suppressing by decoded content would be strictly better than an ack — CLAUDE.md's
standing preference — and it is not worth what it costs here. `validate.py`
hand-parses YAML rather than take a dependency on PyYAML; decoding DDS means
Pillow, and a check that silently downgrades when an optional import is missing
reports differently on two machines, which is the "a check that cannot fail"
family one step along. The measurement is recorded above instead, with its method,
so it can be re-run in ten lines against any future pair.
