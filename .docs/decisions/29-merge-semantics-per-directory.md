# 29 — which file wins is a property of the directory

*Decided 2026-08-03, from a read of
[Irony Mod Manager](https://github.com/bcssov/IronyModManager)'s merge
algorithms. Adds a table this repo cannot measure for itself, a check, and a
`renames:` mechanism.*

## The question

`vendor.yml`'s opening rules say:

> Sources apply in listed order. Later sources overwrite earlier ones on
> identical paths — a load order resolved at build time, so we can see it.

That is true, and it is half the story. It settles two sources claiming the
same **path**. It says nothing about two sources claiming the same **key** in
differently-named files — and once 48 mods are one mod there is no load order
left to separate them. Both files ship. The engine picks by filename sort order
within the directory, and the harvest order has no say in it whatsoever.

[`check_key_conflicts`](../../tools/validate.py) already found this on
2026-08-02 without generalising it: `star_names` is defined by four files in
`common/random_names/base/`, none sharing a name, across YAGEM, Real Space and
vanilla. What it could not do was say who wins, because it asserted one answer
for every directory.

## What Irony knows that we did not

Irony resolves the same problem at load time instead of build time, so it has
had to answer this question for every Paradox game, and its Stellaris tables
have been maintained against bug reports for six years. Three of them matter
here (`IronyModManager.IO/Mods/InfoProviders/StellarisDefinitionInfoProvider.cs`
and `IronyModManager.Parser/Games/Stellaris/`):

**FIOS.** Fourteen directories keep the **first** filename in ordinal sort, not
the last: `component_sets`, `component_templates`, `event_chains`,
`global_ship_designs`, `governments/authorities`, `scripted_variables`,
`section_templates`, `ship_behaviors`, `solar_system_initializers`,
`special_projects`, `start_screen_messages`, `strategic_resources`, `traits`,
and `events/`. Everything else is LIOS and the last wins. We vendor into four
of them from more than one source.

**Whole-file databases.** In nineteen directories — `species_classes`,
`name_lists`, `random_names`, `inline_scripts`, `gfx/portraits/portraits`,
`map/galaxy` and the rest — the unit is the file, not the key. Key-level
reasoning does not hold there.

**Order-sensitive databases.** In five — `ethics`, `governments/authorities`,
`ship_sizes`, `starbase_modules`, `strategic_resources` — the order entries are
declared across the whole directory carries meaning, which is why Irony re-emits
each as a single file when it writes a patch mod.

**How to force a winner.** `!!!_` to win a FIOS sort, `zzz_` to win a LIOS one,
prepending further characters until the name really does sort where it needs to
(`BaseDefinitionInfoProvider.EnsureRuleEnforced`).

## What was rejected, and why it matters

The first cut of the order-sensitive check asserted that those five databases
**must live in a single file**, which is what Irony's `OverwrittenObjectSingleFile`
does. Vanilla ships **40 files** in `common/ship_sizes` and **7** in
`common/starbase_modules`. Single-file is Irony's *output* strategy for writing
a patch mod whose entry order it controls — not a rule of the engine. Shipped,
that check would have been permanently red against vanilla's own layout.

The whole-file table was likewise going to **suppress** key-level findings in
those nineteen directories. That would have deleted the live
`random_names/star_names` finding, which is real. It annotates instead.

## Why this table is quarantined

Every other allowlist in `validate.py` is computed by reading what vanilla does,
so it survives game patches — that is the rule CLAUDE.md states and the reason
the BOM check asks vanilla per folder rather than asserting one answer.

**This table cannot be derived that way and no future reader should try.** The
difference between a first-wins and a last-wins directory lives in the engine's
loader and leaves no trace on disk: vanilla's `common/ship_sizes` (40 files) and
`common/strategic_resources` (1 file) are both FIOS and look nothing alike, and
`common/buildings` (28 files) is LIOS and looks like the first. So it is
transcribed from another project's record, and it is kept in one block at the
top of `validate.py` — `FIOS_DIRS`, `WHOLE_TEXT_DIRS`, `ORDER_SENSITIVE_DIRS` —
rather than spread through the checks that read it, so that the borrowed part is
visible as borrowed.

It has not been confirmed in game. Nothing here changes what the build emits;
it changes what the checks *say*, and adds a mechanism that is opt-in and
asserts its own effect.

## What changed

1. **`check_key_conflicts` names the winner** and picks the end of the sort from
   the directory. It said "Last loaded alphabetically wins" everywhere, which is
   right for LIOS and backwards for FIOS. It now computes the winner over
   vanilla's files as well as ours — under FIOS vanilla's `00_` prefix usually
   wins, meaning a mod's key never takes effect at all, which is worth seeing.

2. **`check_order_sensitive_databases`** reports an order-sensitive directory fed
   by more than one source. It states a fact rather than a defect: whether the
   interleaving breaks anything depends on what the database does with order,
   which cannot be settled from the container. Acked in `vendor.yml` under
   `order_sensitive_ack`. It currently reports one: `common/starbase_modules`,
   two files from Starbase Extended and one from PD - Unique Worlds.

3. **`renames:` in `vendor.yml`.** Changes a vendored file's name, leaving its
   contents alone — the one thing neither a patch nor an `src/` override could
   do, since both change contents and neither changes which file wins a sort.
   Before this the nearest thing was an `src/` copy of the whole losing file
   altered in no way but its name.

   `why` is mandatory, for the reason `patches:` demands one. `win: first|last`
   asserts the new name really does sort that way, against vanilla's files as
   well as ours — Irony's "keep prepending characters until it sorts right" loop
   expressed as a check rather than a fixup. **A rename whose whole purpose is
   to win a sort and which is never checked to have won it looks correct in the
   diff forever.** No renames are declared yet; the mechanism exists so the next
   contested key has an answer that is not a whole-file copy.

## Not taken

Irony's definition-level merge — parse every file into `<directory>/<extension>-<key>`
records, hash each body with whitespace normalised, and resolve per record — is
the rest of its architecture and would be a rewrite of `vendor.py`, not an
addition to it. It buys conflict *resolution* at key granularity where we
currently have file granularity plus `patches:`. Worth revisiting only if
file-granularity merging is what is actually costing us something; today it is
not, and this decision deliberately takes the tables and the rename lever
without the machine.

Its content hashing was left out of the first round and **taken in the second**;
see below.

## Addendum, same day — content hashing (Irony's algorithm 3)

`_body_sha` in `validate.py` is Irony's `DefinitionSHA`: flatten a declaration
body to one line, collapse whitespace runs, delete the spaces adjacent to `=`,
`{` and `}`, hash. Bodies are sliced in the same tokenizer pass that collects
the keys, so a body can never be filed under a key it did not come from. Both
`check_key_conflicts` and `check_defines_conflicts` now drop a finding when
every claimant's content hashes alike — contested by name, identical in
substance, so whichever the engine keeps the game is the same.

Results, measured rather than assumed:

- **`check_key_conflicts`: 3 keys suppressed** —
  `scripted_triggers/pd_aw_is_lithoid_planet`,
  `static_modifiers/pc_pd_nuked_arcology`, `static_modifiers/pd_pelagic_planet`,
  each shipped twice by the Planetary Diversity family.
- **`check_defines_conflicts`: 2 defines suppressed** —
  `NShip.FLEET_BASE_FORMATION_SCALE` (0.6) and
  `NInterface.NOTIFICATION_MESSAGE_YPOS` (0), both set by two sources to the
  same value. **Their `defines_conflict_ack` entries were deleted**, taking the
  list from five to three. That is the stricter state, not the laxer one: an ack
  keeps quiet forever, where the check starts firing again the moment a source
  update makes the two values diverge.

**The prediction that this would shrink `key_conflict_families` was wrong.**
Measured by disabling the family ack: it suppresses **63** findings and hashing
accounts for **3** of them. Obvious in hindsight — a submod overriding its
parent exists precisely to change the content, so the bodies differ. The
families list stays exactly as it is.

**The whitespace normalisation is, so far, doing no work.** All three key
matches were byte-identical before normalising. So the part of the algorithm
that earns its keep on other trees is unexercised on ours, and an unexercised
path is the kind that rots unnoticed. It is verified by 10 hand-checks instead
(tabs vs spaces, `=` spacing, brace spacing, line breaks — and the negatives:
different value, different key, different case, reordered tokens, a missing
field). Re-run those before trusting it if the normalisation is ever widened.

The normalisation errs toward calling two things equal — it collapses
whitespace inside quoted strings too. Nothing in the tree has a double-spaced
string literal, but that is the direction the risk runs: toward silence.
