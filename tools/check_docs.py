#!/usr/bin/env python3
"""Validate the documentation the way validate.py validates the mod.

Two families of question, in the order a broken doc tree usually breaks.

DOES EVERY REFERENCE RESOLVE?

  1. Does every markdown link in .docs/ (and CLAUDE.md, README.md) resolve --
     file, and heading anchor where one is given?
  2. Does every `.docs/...` path cited from live code -- tools/, src/,
     vendor.yml, Makefile, and the root dotfiles -- point at a file that exists?
  3. Does every document carry the nav card the style guide requires?
  4. Does every category folder have a README that names its files?

(1) and (2) are the ones that earned this tool: a planning file named
clutter-pass.md was cited from tools/clutter.py and from decision 45 for five
days after it stopped existing, and nothing anywhere said so. That is why (2)
exists at all -- the docs can link to each other perfectly while every file
header in tools/ points at nothing. See .docs/style-guide.md.

DOES THE DOCUMENTED INVENTORY MATCH THE REPO?

  5. Is every `make` target documented, and does every target the docs name
     exist?
  6. Is every check in validate.py in the catalogue, and vice versa?
  7. Is every `*_ack` list in vendor.yml actually read by a check?
  8. Does the harvest order in architecture/ still match vendor.yml?
  9. Does the source count the docs quote still match vendor.yml?

These are the SAME asymmetry as (2), one level up: a citation that resolves to
a real file can still describe a repo that has moved. All five were added on
2026-08-09 after a documentation pass found one live instance of each --
notably Cinematic Camera sitting four positions from where harvest-order.md
put it, and check_texture_basenames missing from the catalogue entirely.

An inventory check is only worth its noise if it can fail, so each of these
compares against a GENERATED source of truth (the Makefile, validate.py's own
`def` lines, vendor.yml) rather than a second hand-written list.
See .docs/validation/check-design.md rule 7.

This checks that references resolve and that inventories agree. It still cannot
check that prose is true.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DOCS = REPO / ".docs"

# Docs outside .docs/ that take part in the link graph.
ROOT_DOCS = ["CLAUDE.md", "README.md"]

# Where live code may cite a .docs/ path. The root dotfiles are here because
# .gitignore carried a citation to the long-deleted planning/plan.md for a
# month: it is config, it is read by people, and it was outside every scan.
CODE_ROOTS = ["tools", "src", "vendor.yml", "Makefile", ".gitignore",
              ".editorconfig", ".devcontainer"]
CODE_SUFFIXES = {".py", ".txt", ".yml", ".yaml", ".asset", ".gfx", ".shader",
                 ".gui", ".mod", ".json", ".json5", ".sh", ""}

# `NN-slug.md` in CLAUDE.md and the style guide is the FORM of a decision path,
# not a path. Citation-shaped, deliberately not a file.
CITE_PLACEHOLDERS = {".docs/decisions/NN-slug.md"}

# Generated; nobody hand-writes a nav card into it.
GENERATED = {DOCS / "provenance.md"}

# Folders that are categories: each needs a README naming its files.
CATEGORY_DIRS = ["guides", "architecture", "validation", "planning",
                 "reference", "decisions", "analysis"]

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_CITE = re.compile(r"\.docs/[A-Za-z0-9_./-]*[A-Za-z0-9_-]")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$", re.M)
FENCE = re.compile(r"^```.*?^```", re.M | re.S)
INLINE_CODE = re.compile(r"`[^`\n]+`")

RED, YEL, GRN, DIM, OFF = "\033[31m", "\033[33m", "\033[32m", "\033[2m", "\033[0m"

errors: list[str] = []
warnings: list[str] = []


def anchor(heading: str) -> str:
    """GitHub's slug: lowercase, drop punctuation, spaces to hyphens.

    Derived from what GitHub actually does rather than asserted -- inline code
    and links keep their text, everything else non-alphanumeric goes.
    """
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_]", "", text)
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    # One hyphen per space, NOT per run: GitHub does not collapse, so
    # "Phase 0 — The pipeline" loses the dash and keeps both spaces, giving
    # `phase-0--the-pipeline`. Collapsing here silently invents an anchor that
    # renders nowhere, and the check then fails against correct links.
    return re.sub(r"\s", "-", text)


def strip_fences(text: str) -> str:
    """Blank out fenced blocks, keeping the line count so numbers still line up."""
    return FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def strip_code(text: str) -> str:
    """Blank out code, fenced and inline -- for finding LINKS, not headings.

    A path or a `[link](...)` inside an example is documentation OF a citation,
    not a citation; the style guide's own examples proved it, producing three
    false findings.

    Headings must NOT go through this: `src/` in a heading is part of the slug
    GitHub generates, and dropping it here invents an anchor that matches
    nothing -- which is this function's own first false finding, against a
    link that was correct.
    """
    return INLINE_CODE.sub("", strip_fences(text))


def md_files() -> list[pathlib.Path]:
    out = sorted(p for p in DOCS.rglob("*.md"))
    out += [REPO / n for n in ROOT_DOCS if (REPO / n).exists()]
    return out


def code_files():
    for name in CODE_ROOTS:
        p = REPO / name
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix in CODE_SUFFIXES:
                    yield f


def check_links() -> int:
    """Every markdown link resolves -- file, and anchor where one is given."""
    anchors: dict[pathlib.Path, set[str]] = {}
    for f in md_files():
        text = f.read_text(encoding="utf-8-sig")
        anchors[f] = {anchor(h) for h in HEADING.findall(strip_fences(text))}

    n = 0
    for f in md_files():
        text = strip_code(f.read_text(encoding="utf-8-sig"))
        for raw in LINK.findall(text):
            if raw.startswith(("http://", "https://", "mailto:")):
                continue
            n += 1
            path_part, _, frag = raw.partition("#")
            target = f.parent if path_part else f
            if path_part:
                target = (f.parent / path_part).resolve()
            if not target.exists():
                errors.append(f"{f.relative_to(REPO)}: link to missing "
                              f"{path_part or raw}")
                continue
            if frag and target.suffix == ".md":
                if frag not in anchors.get(target, set()):
                    errors.append(f"{f.relative_to(REPO)}: no heading "
                                  f"'#{frag}' in {path_part}")
    return n


def check_code_citations() -> int:
    """Every .docs/ path named from live code exists.

    The failure this is for: a doc is renamed, the docs still link correctly to
    each other, and thirty file headers quietly point at nothing.
    """
    n = 0
    for f in code_files():
        try:
            text = f.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        for cite in set(CODE_CITE.findall(text)):
            if cite in CITE_PLACEHOLDERS:
                continue
            n += 1
            target = REPO / cite
            if not target.exists():
                errors.append(f"{f.relative_to(REPO)}: cites missing {cite}")
    return n


def check_nav_cards() -> int:
    """Every document opens with the style guide's nav card.

    Required: a blockquote in the first few lines carrying **What** and
    **Open when**. Style guide section 1.

    Decision files are exempt and get check_decision_heads() instead -- they
    carry the fixed head of style guide section 7, which answers the same
    question in a different shape. CLAUDE.md and README.md are exempt because
    each IS an entry point rather than a document you route to.
    """
    n = 0
    for f in md_files():
        if f in GENERATED or f.name in ROOT_DOCS:
            continue
        if f.parent.name == "decisions" and f.name != "README.md":
            continue
        n += 1
        head = f.read_text(encoding="utf-8-sig").split("\n")[:14]
        card = "\n".join(l for l in head if l.startswith(">"))
        if not card:
            errors.append(f"{f.relative_to(REPO)}: no nav card "
                          f"(.docs/style-guide.md section 1)")
            continue
        for field in ("**What**", "**Open when**", "**Then**"):
            if field not in card:
                warnings.append(f"{f.relative_to(REPO)}: nav card has no "
                                f"{field}")
    return n


# A dated status marker, in every form the 70 existing decisions use. The two
# older ones are accepted rather than rewritten: a decision records what was
# true when it was made, so retrofitting its head is editing a record.
DECISION_STATUS = re.compile(
    r"^\s*(?:\*\*(?:Status|Decided|Resolved)\b|\*(?:Decided|Originally|Resolved)\b)",
    re.M)
DECISION_TITLE = re.compile(r"^#\s+(?:Decision\s+)?(\d{2})\s*[—-]\s*\S")


def check_decision_heads() -> int:
    """Every decision file is numbered, titled, indexed and dated.

    The index membership is the half that rots: a decision written and not
    added to README.md is invisible to every future session that browses by
    category rather than by ls.
    """
    index = (DOCS / "decisions" / "README.md").read_text(encoding="utf-8-sig")
    n = 0
    for f in sorted((DOCS / "decisions").glob("*.md")):
        if f.name == "README.md":
            continue
        n += 1
        text = f.read_text(encoding="utf-8-sig")
        first = text.split("\n", 1)[0]
        m = DECISION_TITLE.match(first)
        if not m:
            errors.append(f"{f.relative_to(REPO)}: title is not "
                          f"'# NN — <the finding>' "
                          f"(.docs/style-guide.md section 7)")
        elif m.group(1) != f.name[:2]:
            errors.append(f"{f.relative_to(REPO)}: title says {m.group(1)}, "
                          f"filename says {f.name[:2]}")
        if not DECISION_STATUS.search("\n".join(text.split("\n")[:10])):
            errors.append(f"{f.relative_to(REPO)}: no dated status in the "
                          f"head (.docs/style-guide.md section 7)")
        if f.name not in index:
            errors.append(f"{f.relative_to(REPO)}: not in "
                          f".docs/decisions/README.md")
    return n


def check_category_readmes() -> int:
    """Every category folder has a README, and it names every file in it."""
    n = 0
    for name in CATEGORY_DIRS:
        d = DOCS / name
        if not d.is_dir():
            errors.append(f".docs/{name}/: category folder missing")
            continue
        n += 1
        readme = d / "README.md"
        if not readme.exists():
            errors.append(f".docs/{name}/: no README.md "
                          f"(.docs/style-guide.md section 3)")
            continue
        listed = readme.read_text(encoding="utf-8-sig")
        for f in sorted(d.glob("*.md")):
            if f.name == "README.md":
                continue
            if f.name not in listed:
                warnings.append(f".docs/{name}/README.md does not name "
                                f"{f.name}")
    return n


def check_orphans() -> int:
    """The dual: a document no other document links to.

    Reported, never failed -- a doc reachable only from a code comment is
    legitimate, and this is the same asymmetry clutter.py is built on
    (.docs/validation/check-design.md rule 1).
    """
    linked: set[pathlib.Path] = set()
    for f in md_files():
        text = strip_code(f.read_text(encoding="utf-8-sig"))
        for raw in LINK.findall(text):
            if raw.startswith(("http", "mailto:")):
                continue
            p = (f.parent / raw.partition("#")[0]).resolve()
            if p.suffix == ".md":
                linked.add(p)
    orphans = [f for f in md_files()
               if f.resolve() not in linked
               and f.name != "README.md"
               and f not in GENERATED
               and f.name not in ROOT_DOCS]
    for f in orphans:
        warnings.append(f"{f.relative_to(REPO)}: no other document links here")
    return len(orphans)


# ── The inventory checks ────────────────────────────────────────────────────
#
# Each compares a document against a generated source of truth. Where a doc
# omits something, that is a warning: a curated list is allowed to be partial
# unless it claims otherwise. Where a doc names something that does not exist,
# that is an error -- a reader following it lands nowhere.

MAKE_TARGET = re.compile(r"^([a-z][a-z-]*):.*?## ", re.M)
# A command, not prose: `make vendor` in backticks, or a fenced line starting
# with it. "two make two entries match" and "a change to make in passing" are
# both real sentences in these docs, and reading them as commands is how this
# check would start lying. See .docs/validation/check-design.md rule 8 --
# the written form is part of the name.
MAKE_INLINE = re.compile(r"`make\s+([a-z][a-z-]+)[^`]*`")
MAKE_FENCED = re.compile(r"^\s*make\s+([a-z][a-z-]+)", re.M)

WORKFLOW = DOCS / "guides" / "workflow.md"
CHECKS_DOC = DOCS / "validation" / "checks.md"
VALIDATE_PY = REPO / "tools" / "validate.py"
VENDOR_YML = REPO / "vendor.yml"
HARVEST_DOC = DOCS / "architecture" / "harvest-order.md"


def check_make_targets() -> int:
    """Every documented `make` target exists; every real target is documented.

    workflow.md's nav card promises "every make target" and listed 10 of 17 --
    sources-sync, sources-diff, provenance, clean-vendor, mod-file and fix-bom
    were reachable only by reading the Makefile.
    """
    makefile = (REPO / "Makefile").read_text(encoding="utf-8-sig")
    real = set(MAKE_TARGET.findall(makefile))

    for f in md_files():
        # Decisions name `make deploy` and `make undeploy`, which became link
        # and unlink in decision 13. A decision records what was true when it
        # was made; it is not a stale citation.
        if f.parent.name == "decisions":
            continue
        text = f.read_text(encoding="utf-8-sig")
        for t in set(MAKE_INLINE.findall(text)) | set(MAKE_FENCED.findall(text)):
            if t not in real:
                errors.append(f"{f.relative_to(REPO)}: names `make {t}`, which "
                              f"the Makefile does not define")

    wf = WORKFLOW.read_text(encoding="utf-8-sig")
    documented = set(MAKE_INLINE.findall(wf)) | set(MAKE_FENCED.findall(wf))
    for t in sorted(real - documented):
        warnings.append(f"{WORKFLOW.relative_to(REPO)}: does not document "
                        f"`make {t}`")
    return len(real)


def check_validate_catalogue() -> int:
    """Every check in validate.py is in the catalogue, and vice versa.

    check_texture_basenames ran on every build and was in no document: the
    catalogue listed 37 of 38. A check nobody can look up is one the next
    session re-derives from scratch or, worse, writes again.
    """
    defined = set(re.findall(r"^def (check_\w+)", VALIDATE_PY.read_text(
        encoding="utf-8-sig"), re.M))
    documented = set(re.findall(r"`(check_\w+)`",
                                CHECKS_DOC.read_text(encoding="utf-8-sig")))

    for c in sorted(defined - documented):
        errors.append(f"{CHECKS_DOC.relative_to(REPO)}: does not document "
                      f"{c}(), which tools/validate.py defines")
    for c in sorted(documented - defined):
        errors.append(f"{CHECKS_DOC.relative_to(REPO)}: documents {c}(), which "
                      f"tools/validate.py does not define")
    return len(defined)


def check_ack_keys() -> int:
    """Every `*_ack` list in vendor.yml is read by a check.

    An ack list nothing reads is silent in exactly the way a working ack is:
    the entries sit there looking reviewed and suppress nothing, and the check
    they were meant to quiet goes on firing until somebody acks it twice.

    Trailing `s` is matched deliberately. `dangling_art_acks:` is the typo this
    is for, and a pattern anchored on `_ack:` cannot see it -- which is what
    the first version of this check did, and it passed the mutation that was
    supposed to prove it worked. Rule 7, earned again.

    The other direction is NOT reported: a check reading an ack list that
    vendor.yml does not declare is the normal state of an exception nobody has
    needed yet -- three of them sit that way today. See .docs/validation/acks.md.
    """
    text = VENDOR_YML.read_text(encoding="utf-8-sig")
    declared = set(re.findall(r"^([a-z_]+_acks?):", text, re.M))
    read = set(re.findall(r"[\"']([a-z_]+_ack)[\"']",
                          VALIDATE_PY.read_text(encoding="utf-8-sig")))
    for k in sorted(declared - read):
        errors.append(f"vendor.yml: `{k}:` is read by no check in "
                      f"tools/validate.py — it suppresses nothing")
    return len(declared)


def check_harvest_order() -> int:
    """The numbered list in harvest-order.md still matches vendor.yml.

    Cinematic Camera was dropped, then restored at a different position, and
    the document kept it four rows late for two days. vendor.yml is the
    authority and the doc says so -- this makes the doc say so accurately.

    Only plain `NN  Name` rows are compared. The ranged rows (`5-11 PD - ...`)
    and the shipset block (`28+`) are deliberately a summary, and reading them
    as a spec is what would make this check lie.
    """
    try:
        import yaml
    except ImportError:                                    # pragma: no cover
        return 0
    sources = yaml.safe_load(VENDOR_YML.read_text(encoding="utf-8-sig"))["sources"]
    actual = {s["name"]: i for i, s in enumerate(sources, 1)}

    n = 0
    for line in HARVEST_DOC.read_text(encoding="utf-8-sig").split("\n"):
        m = re.match(r"^\s*(\d{1,2})\s\s+(\S.*?)\s*(?:#.*)?$", line)
        if not m:
            continue
        pos, name = int(m.group(1)), m.group(2).strip()
        if name not in actual:
            continue
        n += 1
        if actual[name] != pos:
            errors.append(f"{HARVEST_DOC.relative_to(REPO)}: '{name}' listed "
                          f"at {pos}, vendor.yml applies it at {actual[name]}")
    return n


SOURCE_COUNT = re.compile(r"(\d+)\s+(?:Workshop mods|sources\b)")


def check_source_count() -> int:
    """Docs that quote a source count agree with vendor.yml.

    "49 Workshop mods" is written into CLAUDE.md, README.md, .docs/README.md
    and two more. Adding a source means editing all of them, which means one
    day it will mean editing all but one of them.
    """
    try:
        import yaml
    except ImportError:                                    # pragma: no cover
        return 0
    real = len(yaml.safe_load(
        VENDOR_YML.read_text(encoding="utf-8-sig"))["sources"])
    n = 0
    for f in md_files():
        # Decisions record what was true then; provenance.md is generated from
        # vendor.yml, so a count inside it is a vendor.yml comment's problem.
        if f.parent.name == "decisions" or f in GENERATED:
            continue
        for claimed in SOURCE_COUNT.findall(
                strip_fences(f.read_text(encoding="utf-8-sig"))):
            n += 1
            if int(claimed) != real:
                errors.append(f"{f.relative_to(REPO)}: says {claimed} sources, "
                              f"vendor.yml declares {real}")
    return n


def main() -> int:
    link_n = check_links()
    cite_n = check_code_citations()
    nav_n = check_nav_cards()
    dec_n = check_decision_heads()
    cat_n = check_category_readmes()
    orph_n = check_orphans()
    mk_n = check_make_targets()
    chk_n = check_validate_catalogue()
    ack_n = check_ack_keys()
    hv_n = check_harvest_order()
    src_n = check_source_count()

    print(f"{DIM}docs: {nav_n} document(s) for a nav card, {dec_n} decision(s) "
          f"for a head and an index row, {link_n} internal link(s), "
          f"{cite_n} citation(s) from code, {cat_n} category folder(s), "
          f"{orph_n} unlinked  |  inventory: {mk_n} make target(s), "
          f"{chk_n} check(s) against the catalogue, {ack_n} ack list(s), "
          f"{hv_n} harvest position(s), {src_n} source count(s){OFF}")

    for w in warnings:
        print(f"{YEL}warn{OFF}  {w}")
    for e in errors:
        print(f"{RED}error{OFF} {e}")

    if errors:
        print(f"\n{RED}{len(errors)} error(s){OFF}, {len(warnings)} warning(s)")
        return 1
    print(f"\n{GRN}ok{OFF} — {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
