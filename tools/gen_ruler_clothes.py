#!/usr/bin/env python3
"""Dress the prescripted rulers that sit on a shared master clothes selector.

THE DEFECT, corrected. An earlier model held that `clothes = N` indexes the
distinct texture strings of the portrait's clothes_selector in file order, and
pinned
1..6 on the six rulers whose portrait uses `humanoid_master_{male,female}_-
clothes_01`. The 2026-08-08 Vulcan run showed all six wearing garments that
model does not predict, so the enumeration is not that -- and nothing readable
from this container says what it is.

THE POINT IS THAT IT NO LONGER MATTERS. STNH never indexes into a master
selector: for the empire-select screen it gives the ruler a portrait whose
clothes_selector holds exactly ONE texture and pins `clothes = 0`, which is the
one index a live run has confirmed. `gfx/portraits/asset_selectors/Heroes/
leader_screen_clothes.txt` is that file and it has been in our tree since the
first harvest -- 15 of STNH's own empires use it, three of them with an index
out of range of a one-texture selector, which is exactly how little the number
matters once the selector has one entry.
See .docs/decisions/65-ruler-clothes-dedicated-selectors.md.

THE INTENT IS STILL DERIVED, NEVER COUNTED. The garment each empire should wear
is read from the `game_setup` row the master selector gates on that empire's own
species class -- the rows decision 20 added, which stay as the written record of
the intent. Where a class has no such row (the empires with no designer row, which never
reach the designer) the `species` scope's row for the same class is used, so the
rule is swept rather than the instances repaired.

    python3 tools/gen_ruler_clothes.py [--dry-run]

Writes two files and edits the prescripted rulers in place:

    src/gfx/portraits/asset_selectors/stg_ruler_clothes.txt
    src/gfx/portraits/portraits/stg_ruler_portraits.txt

The generated portrait clones its origin's entity, attachment selector,
greeting sound and character_textures, so only the clothes change -- the face,
the hair and `texture = 0` all keep meaning what they meant. The origin is
recorded as a comment in the generated file and read back on the next run, so
re-running after the prescripted file already names `stg_*_ruler` still clones
from the species portrait rather than from ourselves.
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "stg-build"
SRC = REPO / "src/prescripted_countries"
SEL_OUT = REPO / "src/gfx/portraits/asset_selectors/stg_ruler_clothes.txt"
POR_OUT = REPO / "src/gfx/portraits/portraits/stg_ruler_portraits.txt"

MASTER = "humanoid_master_"


def strip_comments(t: str) -> str:
    return re.sub(r"#[^\n]*", "", t)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace")


def block_at(text: str, open_brace: int) -> str:
    """The body between `open_brace` and its matching close."""
    depth, i = 0, open_brace
    while i < len(text):
        depth += (text[i] == "{") - (text[i] == "}")
        i += 1
        if depth == 0:
            return text[open_brace + 1:i - 1]
    return ""


def portrait_decls() -> dict:
    """portrait name -> (file, raw body), over the built tree, recursively."""
    out = {}
    for f in sorted((BUILD / "gfx/portraits/portraits").rglob("*.txt")):
        t = strip_comments(read(f))
        for m in re.finditer(r"^[ \t]*([\w'\-]+)\s*=\s*\{", t, re.M):
            body = block_at(t, t.index("{", m.end() - 1))
            if "clothes_selector" in body or "character_textures" in body:
                out.setdefault(m.group(1), (f.name, body))
    return out


def scope_rows(selector: str, scope: str) -> dict:
    """species class -> texture, for one scope of one master selector.

    One row per line, here and in every selector vanilla or STNH ships; a
    row's trigger nests, so a brace-avoiding regex would match nothing.
    """
    f = BUILD / "gfx/portraits/asset_selectors" / f"{selector}.txt"
    if not f.is_file():
        return {}
    t = strip_comments(read(f))
    m = re.search(rf"^\t{scope}\s*=\s*\{{(.*?)^\t\}}", t, re.M | re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        tex = re.search(r'"([^"]+\.dds)"\s*=\s*\{', line)
        # STNH writes `is_species_class = "HOLO"` quoted in places; the form is
        # cosmetic in this field, so accept both. Decision 30.
        cls = re.search(r'is_species_class\s*=\s*"?(\w+)"?', line)
        if tex and cls:
            out.setdefault(cls.group(1), tex.group(1))
    return out


def known_origins() -> dict:
    """generated portrait name -> origin portrait, from our own last output."""
    if not POR_OUT.is_file():
        return {}
    return dict(re.findall(r"#\s*origin:\s*(\S+)\s*->\s*(\S+)", read(POR_OUT)))


def empire_blocks(text: str):
    for m in re.finditer(r"^(\w+)\s*=\s*\{", text, re.M):
        depth, i = 0, m.end() - 1
        for j in range(i, len(text)):
            depth += (text[j] == "{") - (text[j] == "}")
            if depth == 0:
                yield m.group(1), m.end(), j
                break


_RULER_RE = re.compile(r"(\truler\s*=\s*\{)(.*?)(\n\t\})", re.S)

HEADER = (
    "# GENERATED by tools/gen_ruler_clothes.py -- do not hand-edit.\n"
    "#\n"
    "# {what}\n"
    "#\n"
    "# A prescripted ruler whose species portrait uses a humanoid_master_*\n"
    "# clothes selector cannot be dressed by an index: that selector is shared\n"
    "# by 44 species classes, and what `clothes = N` enumerates in it is not\n"
    "# something this container can establish -- a model inferred from one\n"
    "# data point was falsified by a live run at all six positions.\n"
    "# STNH's own answer is a one-texture selector plus `clothes = 0`, which is\n"
    "# the one index a live run HAS confirmed. See\n"
    "# .docs/decisions/65-ruler-clothes-dedicated-selectors.md.\n\n"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    decls = portrait_decls()
    if not decls:
        sys.exit(f"no portraits under {BUILD} — run `make vendor` first")
    origins = known_origins()

    intent = {}
    for sel in (f"{MASTER}male_clothes_01", f"{MASTER}female_clothes_01"):
        rows = scope_rows(sel, "species")
        # game_setup is the designer's own statement and wins where it exists;
        # the species scope covers the classes that have no designer row.
        rows.update(scope_rows(sel, "game_setup"))
        intent[sel] = rows

    picked, unresolved = [], []
    for f in sorted(SRC.glob("*.txt")):
        text = read(f)
        edits = []
        for key, i, j in empire_blocks(text):
            body = text[i:j]
            cls = re.search(r'\bclass\s*=\s*"?(\w+)"?', body)
            rm = _RULER_RE.search(body)
            if not (cls and rm):
                continue
            pm = re.search(r'portrait\s*=\s*"([^"]+)"', rm.group(2))
            if not pm:
                continue
            name = pm.group(1)
            origin = origins.get(name, name)
            if origin not in decls:
                continue
            sel = re.search(r'clothes_selector\s*=\s*"([^"]+)"', decls[origin][1])
            if not sel or not sel.group(1).startswith(MASTER):
                continue
            want = intent.get(sel.group(1), {}).get(cls.group(1))
            if want is None:
                unresolved.append((key, cls.group(1), origin))
                continue
            gen = f"stg_{cls.group(1).lower()}_ruler"
            picked.append((key, cls.group(1), origin, gen, want))

            rb = rm.group(2)
            new = re.sub(r'(portrait\s*=\s*")[^"]+(")', rf"\g<1>{gen}\g<2>",
                         rb, count=1)
            if re.search(r"^\s*clothes\s*=", new, re.M):
                new = re.sub(r"^(\s*)clothes\s*=\s*\d+", r"\g<1>clothes = 0",
                             new, count=1, flags=re.M)
            else:
                new = re.sub(r"^(\s*)texture\s*=\s*(\d+)",
                             r"\g<1>texture = \g<2>\n\g<1>clothes = 0",
                             new, count=1, flags=re.M)
            if new != rb:
                edits.append((i + rm.start(2), i + rm.end(2), new))
        if edits and not a.dry_run:
            out, last = [], 0
            for s, e, rep in sorted(edits):
                out.append(text[last:s])
                out.append(rep)
                last = e
            out.append(text[last:])
            f.write_text("".join(out), encoding="utf-8")

    picked.sort(key=lambda r: r[3])

    sel_txt = HEADER.format(
        what="One-texture clothes selectors, one per prescripted ruler that "
             "would\n# otherwise index a master selector.")
    for _key, _cls, _origin, gen, want in picked:
        sel_txt += f'{gen}_clothes = {{\n\tdefault = "{want}"\n}}\n\n'

    por_txt = HEADER.format(
        what="Ruler portraits for the empire-select screen: each clones its\n"
             "# species portrait outright and changes only the clothes "
             "selector,\n# so the face, the hair and `texture = 0` keep "
             "meaning what they meant.")
    por_txt += "portraits = {\n"
    for _key, _cls, origin, gen, _want in picked:
        body = decls[origin][1]
        ent = re.search(r'entity\s*=\s*"([^"]+)"', body)
        att = re.search(r'attachment_selector\s*=\s*"([^"]+)"', body)
        snd = re.search(r'greeting_sound\s*=\s*"([^"]+)"', body)
        ct = re.search(r"character_textures\s*=\s*\{([^}]*)\}", body, re.S)
        por_txt += f"\t# origin: {gen} -> {origin}\n"
        por_txt += f"\t{gen} = {{\n"
        por_txt += f'\t\tentity = "{ent.group(1) if ent else ""}"\n'
        por_txt += f'\t\tclothes_selector = "{gen}_clothes"\n'
        por_txt += f'\t\tattachment_selector = "{att.group(1) if att else "no_texture"}"\n'
        if snd:
            por_txt += f'\t\tgreeting_sound = "{snd.group(1)}"\n'
        por_txt += "\t\tcharacter_textures = {\n"
        for tex in re.findall(r'"([^"]+)"', ct.group(1) if ct else ""):
            por_txt += f'\t\t\t"{tex}"\n'
        por_txt += "\t\t}\n\t}\n"
    por_txt += "}\n"

    if not a.dry_run:
        for p, t in ((SEL_OUT, sel_txt), (POR_OUT, por_txt)):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(t, encoding="utf-8")

    for key, cls, origin, gen, want in picked:
        print(f"   {key:38s} {cls:6s} {origin:20s} -> {gen:22s} "
              f"{Path(want).name}")
    for key, cls, origin in unresolved:
        print(f"!! {key:38s} {cls:6s} {origin:20s} "
              f"no game_setup or species row — left on the master selector")
    print(f"\n  {len(picked)} ruler(s) given a dedicated selector, "
          f"{len(unresolved)} unresolved{' (dry run)' if a.dry_run else ''}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
