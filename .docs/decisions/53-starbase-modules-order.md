# 53 — `common/starbase_modules` fed by two sources: looked at, acked

**Resolved 2026-08-08.** Closes the last of plan.md §8's three standing-warning
items. `check_order_sensitive_databases` asks for exactly this — *"whether the
interleaving actually breaks anything depends on what the database does with
order… look once, then ack it"* — and until now nobody had looked.

## What the check was reporting

`common/starbase_modules` is one of five directories whose entries carry meaning
in the **order** they are declared across the whole directory rather than within
one file ([decision 27](27-merge-semantics-per-directory.md)'s borrowed list;
Irony re-emits each of them as a single file for that reason). STG cannot do
that — it ships the source mods' files as they stand — and here three files from
two sources contribute.

## The interleaving does not happen

Sorted, the merged directory reads:

```
00_arkship_spinal_modules.txt      vanilla   6
00_arkship_utility_modules.txt     vanilla   8
00_arkship_weapon_modules.txt      vanilla  25
00_example.txt                     vanilla   0
00_orbital_ring_modules.txt        vanilla   8
00_starbase_modules.txt            vanilla  12
00_waystation_modules.txt          vanilla  41
pd_unique_waystation_modules.txt   PD - Unique Worlds        3
sbx_3_0_orbital_ring_modules.txt   Starbase Extended 3.0     9
sbx_3_0_starbase_modules.txt       Starbase Extended 3.0    15
```

**Every source's entries stay contiguous and each keeps its internal order.** The
merged sequence is vanilla, then PD, then SBX — which is the harvest order, not a
shuffle. The hazard the check describes, one source's entries interspersed
between another's, is not present.

## And the residual ordering cannot matter

What order does in this database is the construction list: modules group by
`category` — a bare loc key with no declaring database of its own — and list in
declaration order within the group.

| source | entries | categories |
|---|---|---|
| PD - Unique Worlds | 3 `waystation_*` | `sm_utility_cat` |
| Starbase Extended | 24 | `sm_defense_cat`, `sm_economy_cat`, `sm_naval_support_cat`, `sm_research_cat` |

**No category is shared**, so there is no list in which one source's entries are
ordered against the other's. PD's three are waystation modules; SBX's are
starbase and orbital-ring modules.

Acked in `vendor.yml` under `order_sensitive_ack`, with the above written beside
it.

## One thing found on the way, which is a different check's question

SBX redefines **seven vanilla keys** from a differently-named file:
`gun_battery`, `missile_battery`, `hangar_bay`, `detection_array` and three
`orbital_ring_*`. `common/starbase_modules` is not in `FIOS_DIRS`, so it is LIOS
and `sbx_*` sorts after `00_*` — SBX wins, which is what SBX intends and what
[decision 37](37-sbx-citadel-slot-renumbering.md) already records it doing to
vanilla's citadel gun slots. `check_key_conflicts` does not report it because
vanilla's own files are not in the built tree, which is that check's deliberate
scope. Recorded here so the next reader does not re-derive it.
