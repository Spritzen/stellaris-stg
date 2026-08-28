# Glossary

> **What** — the project's vocabulary. Most of these terms mean something
> narrower here than they do generally.
> **Open when** — a term in another doc is opaque, or before using one of these
> words in something you write.
> **Then** — [Documentation map](../README.md) · [Architecture](../architecture/README.md)

| Term | Means, here |
|---|---|
| **source mod** | One of the 49 Workshop mods STG vendors. Listed in `vendor.yml`, pinned in `.source/`. |
| **harvest** | The act of copying a source mod's declared paths into the build. "Harvest order" is the order sources apply in. |
| **vendored** | A file in `stg-build/` that came from a source mod. **Never hand-edited** — change it via `src/`, a patch, or a rename. |
| **shadow** | A file at the same path as another, replacing it whole. `src/` shadows the sources *and* vanilla; a source shadows vanilla and every earlier source. |
| **declare, don't shadow** | Adding a *new* filename that supplies missing declarations, rather than replacing the file that lacks them. Preferred: a source update cannot silently revert it. |
| **additive-only** | A source that may only claim paths no earlier source claimed. STNH is additive-only; the rule protects earlier sources and **not vanilla**. |
| **skip** | A path an additive-only source wanted and did not get. Not an error, and nothing reports it. |
| **overwrite event** | One source writing over a path another already wrote. A path three sources claim scores two events. |
| **contested key** | Two sources defining one database key under **different filenames**. Harvest order does not reach this — filename sort does. |
| **FIOS / LIOS** | *First in, only served* / *last in, only served*: which end of the filename sort wins a contested key. Fourteen `common/` directories are FIOS; the rest are LIOS. A **borrowed** table — [decision 27](../decisions/27-merge-semantics-per-directory.md). |
| **rename** | A `vendor.yml` lever that changes a vendored file's *filename* to move it in that sort. The only way to change who wins a contested key. |
| **patch** | A `vendor.yml` edit to named bytes inside a vendored file. Fails loudly when the source changes — preferred over an `src/` copy for small edits. |
| **resample** | Re-cutting vendored art at harvest to dimensions read off vanilla (`resample_to_vanilla:`), in `crop` or `canvas` fit. |
| **the closure** | The reachability walk in `tools/clutter.py`: from every root, which files are named? Its complement is pruned or reported. [Details](../validation/clutter.md). |
| **reachable / shadowing / kept / orphan** | The closure's four classes for every file in the build. `kept` means listed in `clutter_keep:` with a reason. |
| **prune** | The closure deleting an unreachable file during `make vendor`. Scoped to three tiers by calibration, not convenience. |
| **root** | A file or directory the engine enters without being told to — a declaration file, `gfx/loadingscreens/`, `gfx/map/`. Getting the root set wrong deletes content. |
| **dangling** | A name that resolves to no declaration. The subject of most `validate.py` checks. |
| **ack** | A reviewed exception in `vendor.yml` under a `*_ack:` list, silencing one known finding. [Policy](../validation/acks.md). |
| **eyes-only** | A defect that produces **no log record**, so only the user looking at the screen can grade it. Rooms, mounts, geometry, music titles, name pools. |
| **the floor** | Vanilla's own rate for whatever a check measures — the false-positive baseline. Nothing means anything until read against it. |
| **calibration** | Establishing a check's scope by measuring findings against false positives, and **writing the ratio next to the scope**. |
| **live run** | The user actually playing. The only in-game evidence the container gets, via `/paradox/stellaris/logs/error.log`. |
| **slot label** | An analysis filename's `YYYY-MM-DD` — a **sequence position, not a date**. Several runs happen on one real day. [Conventions](../analysis/README.md). |
| **STNH** | Star Trek: New Horizons — the 3.12-era total conversion STG takes art from and script from never. |
| **Walshicus** | The author of the 22 Trek shipsets built on a vanilla chassis. 17 of the 22 cultures the majors, quadrant and frontier powers fly are his; the other five are generated STNH hulls. |
| **major / minor power** | 22 prescripted empires authored for STG / 77 converted from STNH. A naming split only: all 99 are playable and all 99 are in the pool the galaxy generator draws from ([decision 83](../decisions/83-design-database-is-not-the-cause.md)) — **being in the pool is not the same as being drawn, and none ever has been**. The galaxy's AI Trek empires come from the static map's `create_country` initializers instead ([decision 87](../decisions/87-static-map-lanes-are-generated.md)); the draw itself is still [an open question](../planning/open-questions.md). |
| **graphical culture** | A **name prefix**, not a directory: the engine resolves ship art as `<culture>_<entity>`. Also what a city set needs declared before an empire can use it. |
