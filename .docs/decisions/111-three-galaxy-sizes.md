# 111 — The Known Galaxy comes in three sizes, and medium and large are vanilla's own star count and radius

**Status:** decided, 2026-09-01
**Follows** [decision 86](86-static-galaxy-scenario.md), which built the map,
[decision 87](87-static-map-lanes-are-generated.md), which put the lanes in it,
and [decision 88](88-lock-the-galaxy-picker.md), which made it the only thing
the picker offers.
**Advances** [the plan](../planning/static-galaxy-plan.md)'s step 6, *"scale to
a full map"* — the scale half of it. The 15 minors that already have home
systems are still not placed, in any of the three.
**Built and unrun.** Three live runs graded the small map
([106](106-sealed-system-is-vanilla-content.md)); the medium and large ones have
had none.

## The finding

STG shipped one galaxy: 95 systems over a radius of 218. The picker offered it
and nothing else ([88](88-lock-the-galaxy-picker.md)), so *"how big a galaxy do
you want"* — a question every Stellaris player expects to answer on the setup
screen — had no answer at all.

The map is generated, so a size is not a file to write; it is a row in a table.
**And the row that matters is vanilla's own.** Vanilla's five scenarios pair a
star count with a radius:

| | stars | radius | density |
|---|---|---|---|
| vanilla `tiny` | 200 | 200 | 15.9 |
| vanilla `small` | 400 | 300 | 14.1 |
| vanilla `medium` | 600 | 400 | 11.9 |
| vanilla `large` | 800 | 450 | 12.6 |
| vanilla `huge` | 1000 | 450 | 15.9 |

*(density in stars per 10,000 square units.)* Matching a vanilla row on **both**
numbers matches it on density too, and density is what every distance in the
game is implicitly tuned against — survey time, fleet range, how long a border
takes to reach. So STG's two new sizes are vanilla's `medium` and vanilla's
`huge`, to the unit.

## What shipped

Three files from one generator, one `SIZES` row each:

| | systems | radius | density | separation | scale | lanes | mean degree | longest lane |
|---|---|---|---|---|---|---|---|---|
| **Small** — `stg_alpha_beta_quadrant.txt` | 95 | 218 | 6.4 | 70 | 0.36 | 162 | 3.41 | 49 |
| **Medium** — `…_medium.txt` | **600** | **399** | **12.0** | 19 | 0.66 | 1,058 | 3.53 | 41 |
| **Large** — `…_large.txt` | **1000** | **448** | **15.9** | 11 | 0.74 | 1,814 | 3.63 | 40 |

Against vanilla's 600/400/11.9 and 1000/450/15.9. The scales are 0.66 and 0.74
rather than round numbers **because that is what lands the radius**: STNH's
cloud reaches 605 units, and 605 × 0.66 = 399, 605 × 0.74 = 448.

**Large is the top of the ladder and vanilla says so.** Its own files carry
`radius = 450` under the comment *"should be less than 500, preferably less
than ~460"*. A bigger STG galaxy has to widen the cloud, not the scale.

### The two knobs, and why the count needed a third step

- **`separation`** is the minimum gap between filler systems *in STNH's own
  coordinates*; the thinning pass keeps a star only if it is that far from every
  star already kept. It sets **density**.
- **`scale`** multiplies every position on the way out. It sets **radius**.
- **`systems`** is the exact star count, and it is a target rather than a
  result, because `separation` is a threshold and **the count it yields moves in
  steps**. Measured at scale 0.66: separation 19.11 gives 599 systems and 19.10
  gives 603. There is no separation in between and no separation that gives
  600 — likewise 989 and 1002 either side of 1000.

So each separation is chosen to overshoot by as little as it can and `trim`
cuts the excess: **4 stars for medium, 11 for large, 0 for small**. It removes,
one at a time, the filler star currently closest to any other surviving star —
never an empire home, since a seat is the one thing on this map that is not
interchangeable. That is the removal the map misses least, and it raises the
minimum spacing rather than lowering it. One at a time and re-measured after
each: dropping the *n* closest in a single pass takes both halves of a tight
pair and leaves the hole the pair was filling.

### Small does not move, and is now the odd one out

**Its systems and lanes are byte-identical** to what shipped before — only the
header comment changed. It is the map three live runs graded, and `default = yes`
stays on it: a new size is not graded by being generated.

The honest consequence is that **small is about a third the density of the other
two**, where before all three were within a fifth of each other. Small was
measured against a different reference — 95 systems is 4.5 stars per empire,
against the 4.7 of STNH's smallest canon map (`09 botf`, 468 stars for 99
weighted systems) — and vanilla has no scenario that sparse. It is a Trek-scale
galaxy; medium and large are Stellaris-scale ones. That is a real difference in
texture between the three and it is worth saying rather than smoothing over.

**What survives it is the lane rule.** Mean degree comes out 3.41 / 3.53 / 3.63
and the longest lane 49 / 41 / 40 units, all three under vanilla's
`max_hyperlane_distance = 50`, because `LANE_NEIGHBOURS` is a *count* of nearest
stars and the distance cap only ever binds on the sparse map.

### The picker text is generated now

`stg_galaxy_maps_l_english.yml` was hand-written and said `95 Star Systems` — a
copy of a number the generator computes, in a file next to the generator's
output. Three sizes make three such numbers, so the loc file joined the
generator's output and `make gen-check` covers it. A hand-written copy of a
generated fact is a fact that goes stale in silence, and this one would have.

`default` is a column of `SIZES` so exactly one row can carry it, and `priority`
runs 0, 1, 2 — ascending, the way vanilla's own five run tiny=0 through huge=4.

## Why there is no new check

`check_static_galaxy` already asks its six questions of **every** file in
`map/setup_scenarios/`, so the two new maps were in its population the moment
they were generated: 3 scenarios, 0 findings, and the connectivity question —
the expensive one, the one [87](87-static-map-lanes-are-generated.md) bought
with a live run — is re-proved over all **3,034** lanes rather than trusted to
the MST that built them. Adding a check here would report a number forever,
which is [104](104-script-documentation-is-a-version-exact-oracle.md)'s rule.

## What this does not close

- **A run on the medium or large map.** Everything above is structural. The
  questions a live run would answer are whether a 1,000-system static map
  generates in a sensible time, whether 21 empires spread over a radius of 448
  meet each other before the mid-game, and whether the AI expands into that much
  empty space or stalls in it. `make validate` and `make gen-check` were clean
  over a galaxy with one hyperlane in it, and that is the standing warning
  ([87](87-static-map-lanes-are-generated.md)).
- **21 empires in a 1,000-system galaxy.** Vanilla's `huge` defaults to 15
  empires plus fallen empires, marauders and nomads, none of which this scenario
  generates ([86](86-static-galaxy-scenario.md) sets them all to zero on
  purpose). 47 stars per empire is a lot of room, and whether it is *too* much
  is a content question a run has to answer.
- **The 15 minors.** Step 6 of the plan wants them placed; more room to place
  them in is not the same as placing them, and all three maps still carry 21
  empires.
- **The Terran Empire's Sol collision**, unchanged and still open
  ([86](86-static-galaxy-scenario.md)).
