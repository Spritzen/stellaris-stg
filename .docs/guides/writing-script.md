# Writing script — read vanilla first, then the naming rules

> **What** — the conventions every hand-written file in `src/` follows, and the
> one habit that prevents most silent failures.
> **Open when** — adding or editing anything in `src/`.
> **Then** — [Conventions for comments](#keep-comments-concise) · [Repo layout](../reference/repo-layout.md) · [Validation checks](../validation/checks.md)

## Before writing script, read vanilla

Stellaris script is undocumented and version-sensitive. Guessing at effect,
trigger, or scope names produces files the game **silently drops**. Always ground
a change in a real vanilla example first:

```bash
rg -l "pop_job_" /stellaris/common/pop_jobs/ | head
rg -n "create_species" /stellaris/events/ | head
ls /stellaris/common/                      # discover the right folder
```

Match vanilla's structure for whatever you're adding, then diverge deliberately.
Not a remembered example — an opened one. A plausible-looking guess costs a play
session to discover.

## Prefix everything `stg_`

Script keys, file names, loc keys (`STG_` for loc). Stellaris merges mods into
one namespace; unprefixed keys collide with other mods.

**Two exceptions, both about meeting someone else's content at a shared name:**

### 1. Compat and override files keep the name they shadow

A file in `src/` that means to replace a vanilla or source file must carry that
file's name in order to shadow it, and each needs a **header comment saying what
it overrides and why**. `make validate` enforces the header.

### 2. Keys that vendored art references verbatim are not ours to prefix

Where STG's own script has to meet vendored STNH art at a shared key — species
classes, leader traits, scripted triggers, shader effects — the key takes STNH's
name, because the art references it by name and we cannot edit the art.

That is why `src/common/species_classes/stg_species_classes.txt` declares `FED`
and not `STG_FED`: a prefixed key fails `is_species_class = FED` in 500+ vendored
selectors and no Trek species can ever wear a Trek uniform. The *file* still
takes the `stg_` prefix; only the keys do not, and each such file says so in its
header. [Decision 10](../decisions/10-species-class-keys-unprefixed.md) has the
reasoning and the collision risk we accepted.

> **This reaches the loc keys too, and that is the easy half to miss.** The
> engine derives a species class's whole loc family from the class key —
> `FED_desc`, `FED_organ`, `FED_insult_01` — so `STG_FED_organ` is a key nothing
> ever looks up. STG shipped 14 classes that way and 87 with no loc at all, and
> the symptom was a raw three-letter key on screen with nothing in `error.log`.
> [Decision 21](../decisions/21-species-class-localisation.md).

## File-level rules

- **Tabs**, not spaces, in `.txt` / `.gui` / `.gfx`.
- **Overwrite vs. append**: a file at the same path as a vanilla file *replaces*
  it entirely. Prefer adding a new prefixed file. Only shadow a vanilla file when
  you genuinely mean to replace all of it, and say so in the commit message.
- `common/` files with the *same name* as vanilla replace them; files in
  `events/` and `localisation/` are additive by key.
- **Localisation files must be UTF-8 with BOM** and every key needs a `:0`
  version (`STG_FOO:0 "Bar"`). Without the BOM the game drops the whole file.
  `make validate` catches both; `make fix-bom` repairs the BOM.

## A reference with no declaration behind it is still a reference

Rooms (`room = "klingon_room"`), city sets
(`city_graphical_culture = "klingon"`) and paragon backgrounds resolve by **bare
name against a directory**, with nothing declaring them anywhere.
`make validate`'s cross-reference family is built on "does this declaration
resolve", so it saw none of them until
[decision 48](../decisions/48-room-selector-merge.md).

**When you add art addressed this way, add the check with it.**

## Keep comments concise

A file header is what the file is, why it exists, and a link — a few lines, not
an essay. An inline comment is one line explaining the non-obvious *why*.

Prose that argues a case, records a measurement, weighs alternatives or narrates
a repair belongs in [`.docs/decisions/`](../decisions/) or
[`.docs/analysis/`](../analysis/); the comment cites it by path instead of
restating it. Two rules keep this from losing anything:

1. **Cite, don't summarise.** If the reasoning is already written down, one
   `See .docs/decisions/NN-slug.md` beats a paragraph that will drift out of
   sync with it.
2. **If it is written down nowhere else, it is not a comment — it is a missing
   doc.** Non-derivable facts (a `.dds` copied from vanilla, a key that cannot be
   prefixed, a value that broke a live run) must survive. Write the doc, then
   cite it. Never delete the fact to shorten the comment.

The same two rules govern the docs themselves — [style guide](../style-guide.md).
