# 47 — The shipsets' 39 extra flags, the 22 empires on a grey placeholder, and the Trek city sets

**Resolved 2026-08-08.** Closes the *flags* and *city sets* items in plan.md §6
Phase 3's "Outstanding" list. Extends
[decision 17](17-walshicus-shipsets-replace-stnh-hulls.md), which kept STNH as
the flag source and never looked at what the shipsets add.

## The 39 flags: harvested, additively, and the mechanism is new

The 22 Walshicus shipsets were harvested for `gfx` and
`common/graphical_culture` only. Their `flags/trek/` was left out with a note
that the 39 files they add were an open item.

Measured against STNH's 142 `flags/trek/*.dds`: the shipsets carry **13
basenames STNH has not got** — `Borg`, `dominion`, `elachi`, `federation_01`
through `_07`, `krenim_old`, `lukari`, `malon` — and **14 that collide**
(`Klingon`, `Cardassian1/2`, `Romulan1/2/3`, `betazoid`, `borg-cooperative`,
`borg-rogue`, `ferengi`, `krenim`, `suliban`, `tholian`, `vidiian`). 12 of the 14
differ from STNH's byte-for-byte, and they differ in *size*: 87,508 bytes against
22,000, which is 256×256 DXT5 against 128×128. The 39 is 13 × the `map/` and
`small/` variants.

Harvest order puts the shipsets after STNH, so a plain `include: flags/trek`
would have taken the 13 **and replaced 12 of STNH's flags** — including the
Klingon, Romulan and Cardassian heraldry five major powers fly. Decision 17
settled that STNH is the flag source; that is not a change to make in passing.

`additive_only` already means "skip any path an earlier source claims", but it
was a per-source boolean and the shipsets **must** beat STNH on `gfx/` — that is
decision 17's whole point. So `additive_only` now also takes a **list of path
prefixes**:

```yaml
    include: [gfx, common/graphical_culture, flags/trek]
    additive_only: [flags]
```

STNH wins every contested flag path; the shipsets contribute exactly the 39 files
STNH has not got. Verified in the manifest: Borg 3, Dominion 3, Elachi 3, Krenim
3, Lukari 3, Malon 3, Starfleet TNG 21 = 39, and STNH's 541 untouched.

The one empire that gains from it is the **Malon**, who were flying the Talaxian
flag because no Malon flag existed. The other twelve are alternates — seven more
Federation designs, an older Krenim, a second Borg — that nothing points at yet
and the empire designer now lists.

## The 22 on `neutral.dds`: the shipsets do not close it either

plan.md put the 39 flags and the 22 minor powers falling back to
`flags/trek/neutral.dds` in one bullet, which reads as though the first fixes the
second. It does not. Swept against all 155 Trek flags now in the tree, **exactly
one** of the 22 has art: `hur'q.dds`, which the conversion missed on the
apostrophe. For Anticans, Brunali, Cheronites, Dosi, El-Aurians, Garidians,
Hazari, Karemmans, Kinshaya, Kraylor, Lyridians, Morali, Nausicaans, Norcadians,
Nyberrites, Nygeans, Rigellians, Selay, Skrreea, T'Rogorans and Zahl, **no Trek
flag exists in any source in the harvest.**

STNH had the same problem and answered it the same way: of its own prescripted
empires, the four that reach STG's list are given a **vanilla** flag —
`pirate/flag_pirate_4` for the Cheronites, `pirate/pirate_12` for the Hazari,
`ornate/flag_ornate_9` for the Kraylor, `spherical/flag_spherical_5` for the
Rigellians. Vanilla's own prescripted empires draw on fifteen such categories.

So the 21 get a distinct vanilla icon each, taking STNH's pick where it made one
— except the Rigellians, moved to `spherical/flag_spherical_13` because STNH's
choice is already the Bolian Union's and the Bolians are playable. One flat grey
emblem repeated 22 times becomes 22 heraldries. The Bolian Union stays on a
vanilla icon: STNH ships no Bolian flag and neither does any shipset, which is
what plan.md already recorded.

**No flag-resolution check was added**, deliberately. Measured first: 0 of STG's
202 `icon`/`background` references dangle, and 0 of STNH's 47 do either. There is
no defect to calibrate against, and CLAUDE.md's rule is explicit — a check
without one is worse than no check, because it reports a number.

## City sets: most of them were already Trek, and that is why this item was small

`city_graphical_culture` is the same kind of reference as a room: a bare texture
**prefix**, declared nowhere, resolved as
`gfx/portraits/city_sets/<name>_city_l01.dds`. Vanilla has no database of them.

STNH ships 256 city textures under 28 prefixes, and **most of them shadow
vanilla's own** — `humanoid_01`, `mammalian_01`, `reptilian_01`, `avian_01`,
`molluscoid_01` and eleven more are STNH's Trek re-cuts at vanilla's paths. So
every STG empire left on a vanilla prefix has been drawing Trek cities since the
first harvest. plan.md's "city sets" item, and two prescripted-file headers
asserting `city_graphical_culture` was "still vanilla", were describing a
problem that the vendoring had already solved.

What was genuinely unreached: the six prefixes STNH ships under **its own** name,
`borg_01`, `cardassian_01`, `klingon`, `tholian_01`, `undine_01`, `vulcan_01`.
They are now named by the six empires they were cut for — the Borg Collective,
the Cardassian Union, the Klingon Empire, the Tholian Assembly, the Undine
Vanguard and the Confederacy of Vulcan.

Each of the six ships `l01`..`l06` and **no `_devastated` variants**, where
vanilla's sets carry them. That is not a defect to fix: vanilla's own `ai_01`
set is `l01`..`l05` with no devastated variant either, so a set without them is
something the engine already handles.

`future_starfleet.dds` is **not** a city set. It is a single texture whose name
reads like a prefix, and it is exactly the kind of thing
`check_room_references`' fifth question exists to catch.
