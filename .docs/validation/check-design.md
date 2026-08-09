# How to write a check

> **What** — twelve rules the existing checks are built on, each earned by a
> check that reported a confident wrong answer.
> **Open when** — adding a check to `tools/validate.py`, widening one's scope, or
> deciding whether a finding is real.
> **Then** — [The check catalogue](checks.md) · [Acks](acks.md) · [Style guide](../style-guide.md)

Every rule below cost a live run to learn. They are ordered by how expensive
getting them wrong has been.

---

## 1. A check that DELETES is not a check that reports

**And its two errors are not symmetrical.** Most checks are free to be strict: a
false positive costs someone a look. `check_unreferenced` and the prune stage
behind it are the first that **remove files**, and an edge type they fail to
follow becomes a deleted file that rendered perfectly — the failure decisions
[24](../decisions/24-group-c-texture-references.md),
[34](../decisions/34-src-shadows-drop-source-declarations.md) and
[37](../decisions/37-attach-edges-into-pruned-art.md) already record three times
over, one file type further down each time.

So that closure is deliberately **generous** where the others are strict: it
resolves a reference by path, then filename, then stem, against the built tree
and vanilla at once; it treats every declaration file as a root wherever it sits;
it scans `.mesh` files as **bytes**, because a mesh names its textures inside the
binary and no text file mentions them.

**Ask which direction an error costs more before choosing how tight to make the
question.** [Decision 45](../decisions/45-clutter-pass.md).

### A rule that SUPPRESSES a finding belongs to this family too

And it looks nothing like it in the diff. *"One body is vanilla's own, so the
other is a deliberate override of it"* is true of a live 4.x mod and false of a
3.12 total conversion — on its first cut it swallowed a real finding, STNH's
dummy entity that was one coin-flip from becoming every empire's habitat art.

**Calibrate a suppression by watching what it removes, never by reading it**: it
reports a smaller number, which is exactly what you were hoping to see.
[Decision 53](../decisions/53-duplicate-entity-triage.md).

---

## 2. Establish *when* a reference resolves, not just whether it does

Almost every cross-file name in Stellaris resolves after the whole tree is read,
and every check here was built on that. **`clone` in a `.asset` does not**: it
resolves against entities *already loaded*, walking `gfx/models/ships/` as one
alphabetical sequence with files and directories interleaved.

"Declared somewhere" said yes 982 times while the Vulcan and Tholian shipsets did
not render at all — 537 records, `make validate` clean throughout.
[Decision 30](../decisions/30-clone-discards-sibling-locators.md).

---

## 3. Ask what is referenced, not what is defined

The 139-stub trigger harvest read STNH's *definitions* and so could not see
`isBajoranReligiousLeader`, which STNH references from 13 files and leaves
commented out in its own.

---

## 4. Derive allowlists from vanilla's own usage, never by hand

`X = yes` is ordinary engine vocabulary and `shader = "Collision"` is an engine
built-in vanilla uses and never declares. Both allowlists are computed by reading
what vanilla does, so they **survive a game patch**.

The BOM rule is the same idea: it asks vanilla *per folder* rather than asserting
one answer, because `common/name_lists/` is BOMed 76 times out of 76 and every
other database zero.

**This rule also kills checks before they ship.** A proposed check that five
databases must live in one file died against vanilla's own 40 files in
`common/ship_sizes` ([decision 29](../decisions/29-merge-semantics-per-directory.md)).

---

## 5. A fact you cannot derive from vanilla is borrowed, and must be labelled so

Which end of the filename sort wins a contested key lives in the engine's loader
and leaves no trace on disk — vanilla's FIOS and LIOS directories look identical.
That table comes from another project's record, so it sits in **one block at the
top of `tools/validate.py` with the provenance written next to it**, rather than
dissolved into the checks that read it.

Do not let a borrowed table pass as a measured one; the next reader needs to know
which of the two they are trusting.
[Decision 29](../decisions/29-merge-semantics-per-directory.md).

---

## 6. A screen nobody opened is a check that never ran

**And the log is a sample of that class, not a census.** Eleven runs reconciled
to the record while nine prescripted empires, the Borg included, could not be
selected at all; those records only appear when someone opens the empire
designer.

Worse, sweeping the *rule* behind those findings turned up nine more empires with
the same defect, all AI-only, which no log will ever show — the engine drops a
trait silently rather than refusing it.

**When the log reveals a defect that has a rule behind it** (a vanilla
`opposites` list, an archetype budget, an `allowed_ethics` gate), **never repair
only the instances it named: derive the rule and sweep the tree.** That is
`check_prescripted_empires` — calibrated by reverting the repairs, 21 findings
and no false positives. [Live runs](../guides/live-runs.md).

---

## 7. Compare declared identity, not block key — and distrust a check that has never failed

`check_vanilla_regression` compared depth-0 keys, which is identity in a `.txt`
and is **not** identity in an `.asset`, where every declaration reads
`entity = { name = "…" }`. It was examining 35 files, reporting the number, and
structurally incapable of finding the 119 dropped entity declarations in them.

**A check that cannot fail is worse than an absent one, because it reports a
number.**

`check_duplicate_entities` repeated it on 2026-08-07 in the same shape: it found
each declaration with a lazy regex ending at `name = "…"` and then compared
`m.group(0)` as the *body*, so every declaration of one name normalised to the
same string and the bodies-differ test compared a value against itself — 0
reported against a pair it was written for.

**Finding a name is not the same problem as getting the body**, and a regex that
solves the first hands you a confident wrong answer to the second. Brace-count
the body. [Decision 33](../decisions/33-duplicate-entity-declarations.md).

---

## 8. A reference has a written form as well as a name

Normalising the form away can delete the defect. `class = "star"` is not
`class = star` — `star` is an engine keyword, and quoted it stops being one, so
the body is never created. Three separate checks over that one file made the
quotes optional in a regex, and all three were blind to 23 missing stars across
20 home systems while reporting clean.

Quoting is semantic in that position, and **vanilla says so per name**: 0 quoted
against 671 bare for the keywords, 891 quoted for the `pc_*` names. Ask vanilla
which form each name takes rather than asserting a rule about the *class* of name
— asserting one produced 14 false positives against 1 true finding.
[Decision 27](../decisions/27-quoted-class-keyword.md).

**The converse is a separate trap, and it looks identical in a regex.** Where the
form is *cosmetic*, refusing to read one of the two deletes the reference instead
of the defect: STNH writes `is_species_class = "HOLO"` quoted, three checks read
that field with a bare-only `(\w+)`, and all three were blind to it — the one key
of 34 that no ack covered, reported by nothing while the engine reported it twice.

**Ask whether a field's written form changes its *meaning* before deciding
whether to normalise it.** If it does, keep the form and check it; if it does
not, accept every form the sources use.
[Decision 32](../decisions/32-declare-stub-species-classes.md).

---

## 9. Recalibrate on the far side of the fix, not only the near side

The section-locator check *was* calibrated against a live log — 676 mounts found,
0 missed — and it fell to 0 once they were repaired **while the engine went on
reporting the same 506**, because the repair put those declarations beside a
`clone`, which discards them.

A check calibrated against one shape of the data is not calibrated against the
shape the repair leaves behind, and this one had a number to show for itself the
whole time. [Decision 30](../decisions/30-clone-discards-sibling-locators.md).

---

## 10. "Declared somewhere" is not "declared where the engine looks"

**And a declaration name is not a filename.** Two ways the same check can be
satisfied by the wrong thing.

Real Space declares `PdxMeshPlanetRingsRS` in two files on purpose; we shipped
one of them, `check_dangling_shaders` found the name and was satisfied, and the
gas giant rings drew with no material anyway — because a mesh material resolves
against `pdxmesh.shader` and nothing else
([34](../decisions/34-src-shadows-drop-source-declarations.md)).

The mirror of it: `pdxmesh = "X_mesh"` names a *declaration*, and the `.mesh`
file it stands for is named by a `.gfx`. A check that globbed for `X_mesh.mesh`
found nothing anywhere and reported **1,279 findings, most of them vanilla's**
([35](../decisions/35-station-section-attach-points.md)).

**Resolve the indirection, then ask the question.**

---

## 11. Scope is a calibration result, not a convenience filter

**And say so where someone will try to widen it.** `check_section_attach_points`
finds 66 real defects against 1 vanilla false positive over the station family,
and 147 against 41 over all 317 ship sizes. The narrow scope is a constant in the
code **with the ratio written next to it**, so widening it reads as the piece of
work it is rather than an oversight. The same reasoning kept
`check_asset_load_order` scoped to entities STG owns.

**A check can want two scopes at once.** `check_prescripted_loc`'s truncation
half stays on the one *generated* file, because truncation is a generator failure
and the 22 hand-authored empires diverge from their source deliberately; its
leaked-key half covers all four, because it asks nothing of the source, so it
costs nothing and cannot produce a false positive.
[Decision 51](../decisions/51-prescripted-loc-scope.md).

---

## 12. "Can this ever appear" has more than one route — ask them all, then read the scope off the answer

**A high floor is usually a missing half of the question, not a reason to
scope.** `weight` on an archaeological site governs
`create_archaeological_site = random` and nothing else; **74 of vanilla's 123
sites carry no positive weight**, and every one of them is placed by an
initialiser, an event or a parameterised effect that names it outright. Ask the
weight question alone and the check reports 74 findings and has to be scoped to
our own file to stay quiet. Ask it together with "and nothing in script names
this key" and vanilla's floor is **0**, so no scope is needed at all.

The scope [rule 11](#11-scope-is-a-calibration-result-not-a-convenience-filter)
would have permitted was hiding an incomplete question. **Widen the question
before narrowing the population.**

**The second half over-accepts on purpose.** It is a token sweep of every `.txt`
in the merged tree, not a parse of `create_archaeological_site`, because vanilla
reaches its own zroni chain through `$DIGSITE$` inside an inline script and a mod
can invent a route vanilla has not used. For a check whose finding is *"delete
this or wire it up"*, over-accepting is the safe direction
([rule 1](#1-a-check-that-deletes-is-not-a-check-that-reports)).
[Decision 79](../decisions/79-reachability-checks.md).
