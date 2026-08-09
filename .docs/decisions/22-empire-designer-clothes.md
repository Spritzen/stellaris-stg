# 22 — `game_setup` is a scope, and a shared selector has to gate it too

**Status:** decided, 2026-08-03
**Completes** [decision 16](16-phase-3-clothing-triggers.md), which gave the STNH
clothing triggers real bodies for every scope the *game* reads and left the one
the *empire designer* reads untouched.

## The report

After a live run the user reported that the United Federation of Planets, the
Andorian Empire and the Bajoran Republic had the wrong ruler clothing —
specifically, human civilian clothes on non-humans. `error.log` had nothing:
another silence failure, like decisions 20 and 21.

## What was actually wrong

An asset selector has five scopes, and `game_setup` is the only one the empire
designer consults — vanilla's own comment says so: *"will run with a limited
country scope. species and government is set but the country does not actually
exist."* STNH's two master selectors give it a single line:

```
game_setup = {
    default = "gfx/models/portraits/human_civilian/civ_human_male_clothes_01.dds"
}
```

That is correct for a *per-species* selector, and every other Trek species has
one — `cardassian_male_clothes_01` defaults to a Cardassian command tunic,
`bolian_male_clothes_01` to Bolian clothes, `caitian_male_clothes_01` to Caitian
clothes. A per-species selector's single default *is* that species' look.

`humanoid_master_male_clothes_01` is shared by 44 species classes, so its single
default is a statement that all 44 are human. **Five STG empires point at the
master pair — FED, VUL, ADR, BAJ and TRI — and all five were drawn as humans in
the picker.** The user named three of the five; the Vulcans and the Trill have
the same defect and simply were not looked at.

The in-game `ruler` scope was working the whole time. It gates on species class,
and FED, ADR and BAJ each land on their own civilian ruler art there. Nothing was
wrong after the game started, which is why one live run's log could not show it.

## Decision

Two `vendor.yml` patches gate `game_setup` by species class in both master
selectors, keeping the human default as the fallback for the 39 classes STG has
no designer entry for.

| Class | Designer art | Why |
|---|---|---|
| FED | `human_civilian/federation_president_male_1.dds` | STNH's dedicated Federation President art, which nothing else in the tree reaches — the in-game ruler scope falls back to the generic `human_president_*` set. |
| VUL | `vulcan/civ_vulcan_male_clothes_02.dds` | The species scope's own entry. |
| ADR | `andorian/andorian_male_clothes_admiral.dds` | Andor is an imperial militarist power with a `leader_class = commander` ruler, and the admiral coat is what its species scope already names. |
| BAJ | `bajoran/bajoran_male_clothes_01.dds` | The Republic's First Minister is a civilian. The Kai, Vedek and Ranjen robes stay unreachable, which is correct — a theocratic look for a republic. |
| TRI | `trill/trill_male_clothes_01.dds` | The species scope's own entry. |

Female equivalents throughout; all ten files verified present.

**A patch, not an `src/` override**, per plan.md §2: the selector is 2,846 lines
of someone else's file and we want to own six of them. If STNH ever rewrites that
block the build stops and names it, rather than shipping our stale copy.

**`owner_species = { is_species_class = X }` is the country-scope form**, and it
is grounded rather than guessed: `game_setup` is a country scope — vanilla and
STNH both gate it on `has_country_flag` in `room_textures.txt` — and vanilla uses
this exact trigger in `common/start_screen_messages/00_start_screen_messages.txt`,
which runs in the same place. The existing Romulan advisor-voice patch in
`vendor.yml` uses the same form.

## How this class of defect gets caught next time

`check_portrait_clothes_selectors` gained a second half. It already asked whether
a selector's class gating names the empire's class; it now asks the same question
of `game_setup` *specifically*, for playable empires only, because nothing else
reaches the designer. Tracking the scope separately is the whole point — a
selector can gate all four other scopes correctly and leave this one bare, and
the first question returns clean while the designer draws humans.

Calibrated by reverting the patches: **exactly six findings** — the five empires
plus the Borg's assimilated-human secondary species, which is a real instance —
and nothing else. Every other playable empire has a per-species selector whose
`game_setup` default is already right.

## The rule worth carrying

**A default is a claim about every case that reaches it.** Harvesting a
per-species file's shape into a shared one silently converts "this species looks
like this" into "all 44 of them do". The same reasoning that made
`check_prescripted_empires` sweep a rule rather than repair the instances a log
named applies here: when a scope has no gates at all, there is nothing for a
name-resolution check to fail on, so the check has to know the scope exists.
