# 44 — `common/random_names/` pools append; the six "silently gone" warnings are false

**Resolved 2026-08-07.** Settled from the source mods' own file layouts, because
the web does not document it and vanilla cannot answer it.

## The report

`check_key_conflicts` raised six warnings against `common/random_names/base/`,
five of them of this shape:

```
'realspace_starlord_partons_random_names.txt' [Real Space 4.0] redefines
'star_names' with 15 entries where vanilla's 00_random_names.txt has 1763.
IF these pools replace rather than append, 1748 entries are silently gone.
```

Plus one three-way key conflict: `star_names` is defined by three files across
two sources, and LIOS means the last filename in sort order wins outright.

The `IF` was load-bearing and unanswered. If pools replace, the galaxy draws
every star name from a pool of **15**.

## Neither of the usual authorities can answer it

- **Vanilla cannot.** `common/random_names/base/` holds exactly one file,
  `00_random_names.txt`, declaring all ten keys. Vanilla never splits a pool
  across two files, so "ask vanilla's own usage" — the rule most of
  `tools/validate.py` is built on — has nothing to read here.
- **The wiki cannot.** [Modding § common](https://stellaris.paradoxwikis.com/Modding)
  carries an overwrite column per directory, and `random_names` is one of the
  rows marked `❓`, which the page's own legend defines as *"information not
  documented or extensively tested"*. Every search around it returns the generic
  FIOS/LIOS explanation, which is about *keys*, not about whether a **list body**
  merges.

## What settles it: Real Space ships both files itself

`common/random_names/base/` in the built tree holds four files. Two are Real
Space's, and **both declare `star_names`**:

| file | source | `star_names` |
|---|---|---|
| `00_random_names.txt` | Real Space 4.0 | 1,569 |
| `ariphaos_astro_names.txt` | YAGEM | — |
| `ariphaos_astro_names_constellation.txt` | YAGEM | — |
| `realspace_starlord_partons_random_names.txt` | Real Space 4.0 | **15** |

The 15 are Patreon patron names — `Bluehawk`, `Ushakov_Star`, `Zhenn` — and
**none of them appears in Real Space's own `00_random_names.txt`**. The patron
file sorts last, so under a replacing rule Real Space would be reducing its own
galaxy, in one of the most-subscribed mods on the Workshop, to fifteen backer
names. **No author ships that against themselves.** The layout only makes sense
if pools append, and the author is the one person who has certainly tested it.

The second source agrees independently. YAGEM's `asteroid_prefix` pool has
**zero of its 60 entries in common** with the 136 already in the base file, and
they are catalogue designations — `0232-`, `4016-J-` — built to sit alongside
vanilla's rather than stand in for them.

Two mods, two authors, both writing partial pools into separate files. **Pools
append.** All six warnings are acked.

## The evidence is inference, and it is labelled as such

This is not a measurement of the engine — it is what two authors' file layouts
entail, plus the fact that the failure mode would be famous. That is weaker than
reading vanilla and stronger than the wiki's `❓`, and CLAUDE.md's rule about
borrowed facts applies: the next reader needs to know which of the three they
are trusting. The cheap confirmation, if it is ever wanted, is one live run —
star names varied rather than fifteen repeats.

## Found on the way: Real Space curates vanilla's star names, and nothing sees it

`00_random_names.txt` in the built tree is **Real Space's**, shadowing vanilla's
at the same path, and it declares **1,569** star names against vanilla's 1,763.
194 names are gone, deliberately — Real Space replaces much of the galaxy with
real star systems and drops the vanilla names that would collide.

`check_vanilla_regression` cannot see it, and correctly so: it compares
*declarations*, all ten keys are still declared, and pool contents are not its
question. Worth recording only so a future reader does not rediscover the 194 as
a defect.

> **The pool figure this paragraph originally gave was wrong — corrected
> 2026-08-08 by [decision 52](52-trek-star-names.md).** It read "the effective
> pool is 1,569 + 15 = **1,584**", which counts Real Space's two files and
> misses YAGEM's `ariphaos_astro_names.txt` (1,994) and
> `ariphaos_astro_names_constellation.txt` (2,143) — in the same directory,
> feeding the same key, and listed in the table above with a `—` in the
> `star_names` column that should have read otherwise. Deduplicated the pool was
> **5,702**, and is **6,531** since STG added 829 Trek names. The reasoning
> above is unaffected and in fact strengthened: four files from three sources
> all ship partial pools under separate filenames. Only the arithmetic was
> short, and it was short by 3.6×.
