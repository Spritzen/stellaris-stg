#!/usr/bin/env python3
"""Validate the documentation the way validate.py validates the mod.

Two families of question, in the order a broken doc tree usually breaks.

DOES EVERY REFERENCE RESOLVE?

  1. Does every markdown link in .docs/ (and CLAUDE.md, README.md) resolve --
     file, and heading anchor where one is given?
  2. Does a link to a decision NAME that decision in its own label? The href is
     the authority and the label is what a reader believes. On 2026-08-27 a
     renumbering sweep rewrote 415 labels twice while every href stayed correct,
     and this tool passed clean over links whose visible text named the wrong
     decision. That is the failure check_link_labels() exists for.
  3. Does a decision named by NUMBER ALONE -- no path, no link -- name a
     decision that exists? This is the third form a citation takes and the last
     one to get a check: 519 of them, a third of every decision citation in the
     repo, sat outside both (2) and (4) until 2026-08-28.
  4. Does every `.docs/...` path cited from live code -- tools/, src/,
     vendor.yml, Makefile, and the root dotfiles -- point at a file that exists?
  5. Does every document carry the nav card the style guide requires?
  6. Does every category folder have a README that names its files?

(1) and (4) are the ones that earned this tool: a planning file named
clutter-pass.md was cited from tools/clutter.py and from decision 43 for five
days after it stopped existing, and nothing anywhere said so. That is why (4)
exists at all -- the docs can link to each other perfectly while every file
header in tools/ points at nothing. See .docs/style-guide.md.

DOES THE DOCUMENTED INVENTORY MATCH THE REPO?

  7. Is every `make` target documented, and does every target the docs name
     exist?
  8. Is every check in validate.py in the catalogue, and vice versa?
  9. Is every `*_ack` list in vendor.yml actually read by a check?
 10. Does the harvest order in architecture/ still match vendor.yml?
 11. Does the source count the docs quote still match vendor.yml?

These are the SAME asymmetry as (4), one level up: a citation that resolves to
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

# Trees `make vendor` / `make sources-sync` generate. A doc link into one of
# these resolves only after a build and vanishes mid-rebuild, so it is a check
# that passes or fails on the state of the working tree rather than on the
# documentation. Cite the git-tracked input instead -- `src/` for our own
# content, `.docs/provenance.md` for what the merge did with it.
# Found 2026-08-25: one link into stg-build/ failed this check transiently
# while a background `make vendor` was rewriting the tree.
GENERATED_TREES = ("stg-build", ".source", ".vendor-cache", "dist")
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
                 "reference", "decisions", "analysis", "runs"]

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
LABELLED_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
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
            try:
                head = target.relative_to(REPO).parts[0]
            except ValueError:
                head = ""
            if head in GENERATED_TREES:
                errors.append(f"{f.relative_to(REPO)}: link into the generated "
                              f"tree {head}/ ({path_part}) -- cite the tracked "
                              f"input under src/, or .docs/provenance.md")
                continue
            if not target.exists():
                errors.append(f"{f.relative_to(REPO)}: link to missing "
                              f"{path_part or raw}")
                continue
            if frag and target.suffix == ".md":
                if frag not in anchors.get(target, set()):
                    errors.append(f"{f.relative_to(REPO)}: no heading "
                                  f"'#{frag}' in {path_part}")
    return n


# A link whose href names a decision file: `[... 77 ...](../decisions/77-slug.md)`.
# The label is the half no other check reads, and on 2026-08-27 a renumbering
# sweep rewrote 415 of them twice while every href stayed correct -- `make docs`
# passed clean over links whose visible text named the wrong decision. The href
# is the authority; a number in the label has to agree with it.
DECISION_HREF = re.compile(r"(?:^|/)(\d{2,3})-[a-z0-9-]+\.md$")


def _num(f: pathlib.Path) -> str:
    """A decision file's number: the digits before the first dash.

    Not `name[:2]`, which is what every one of these read until 2026-08-28.
    The corpus was two digits wide for 99 decisions and the hundredth broke
    four checks at once -- the title/filename comparison, the `have` set the
    bare-number check tests against, and the href regex behind both link
    checks -- each of them silently, by reading `10` out of `100-`.
    """
    return f.name.split("-", 1)[0]
# Only labels that are ABOUT a decision number are read. A bare "[77]", a range
# "[76]-[80]", or anything saying "decision 77" is a claim about which decision
# this is; "[230 attach points]" and "[the 2026-08-08 review]" are not, and
# reading a number out of those is how this check would start lying
# (.docs/validation/check-design.md rule 8 -- the written form is part of the
# name). Dates go first, so a label may carry one without being read as one.
DATE_IN_LABEL = re.compile(r"\d{4}-\d{2}-\d{2}")
LABEL_IS_NUMBER = re.compile(r"^[\s\d,&/:;.–—-]*\d[\s\d,&/:;.–—-]*$")
LABEL_SAYS_DECISION = re.compile(r"decisions?\s*§?\s*((?:\d{1,3})"
                                 r"(?:\s*(?:[-–—,]|and|to|through)\s*\d{1,3})*)",
                                 re.I)
LABEL_NUM = re.compile(r"\d{1,3}")


def check_link_labels() -> int:
    """A link to a decision does not name a different decision in its text.

    The href is the authority: `make docs` already proves it resolves, and the
    label is the half a reader actually believes. A label naming several
    numbers passes if any of them is the target -- "decisions 76 through 80" is
    one link, deliberately.
    """
    n = 0
    for f in md_files():
        text = strip_code(f.read_text(encoding="utf-8-sig"))
        for m in LABELLED_LINK.finditer(text):
            label, href = m.group(1), m.group(2)
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            target = DECISION_HREF.search(href.partition("#")[0])
            if not target:
                continue
            plain = DATE_IN_LABEL.sub(" ", label)
            says = LABEL_SAYS_DECISION.search(plain)
            if says:
                nums = LABEL_NUM.findall(says.group(1))
            elif LABEL_IS_NUMBER.match(plain):
                nums = LABEL_NUM.findall(plain)
            else:
                continue
            n += 1
            if not any(x.zfill(2) == target.group(1) for x in nums):
                errors.append(f"{f.relative_to(REPO)}: link labelled "
                              f"'{label}' points at decision "
                              f"{target.group(1)} ({href})")
    return n


# A citation with no path and no link: `decision 40`, `decisions 76 through 80`.
# Same shape as LABEL_SAYS_DECISION above and deliberately so -- ranges are a
# real form in these docs, and reading only the first number leaves the rest
# outside the sweep this exists to make possible.
BARE_DECISION = re.compile(r"[Dd]ecisions?\s+((?:\d{1,3})"
                           r"(?:\s*(?:[-\u2013\u2014,]|and|to|through)\s*\d{1,3})*)")
# Comment and docstring wrapping is not decoration here: it is what hid the one
# defect this check was written after. `decision` ended line 4191 of
# tools/validate.py and `88` began 4192, so every line-wise grep -- including
# the renumbering sweep's own -- looked straight past it.
CODE_WRAP = re.compile(r"\s*\n\s*(?:#|\*)?\s*")
DOC_WRAP = re.compile(r"\s*\n\s*>?\s*")


def check_bare_decision_numbers() -> int:
    """A decision named by NUMBER ALONE still names a decision that exists.

    THE THIRD FORM A CITATION TAKES, and the only one nothing had ever read.
    check_code_citations() reads `.docs/decisions/NN-slug.md` and
    check_link_labels() reads `[NN](...)`; between them they cover the 983
    citations the 2026-08-27 renumbering rewrote. A bare `decision 40` in a
    comment or a sentence carries neither a path nor an href, so it was outside
    both -- 509 of them, a third of every decision citation in the repo, none of
    which any tool had looked at.

    WHAT IT ASKS, AND IT IS EXACT. Does the number name a decision file that
    exists? Floor 0 of 509 across live code and every document, so there is no
    scope and no ratio to write beside one
    (.docs/validation/check-design.md rule 11). It fails on a number one past the
    last decision written, and on every bare citation to one that is removed.

    IT READS ITS OWN PROSE, WHICH IS NOT A BUG TO EXEMPT. The first run of this
    check reported the worked example in this docstring, which named a number
    that did not exist yet -- the "documentation OF a citation is not a
    citation" class strip_code() was written for. Stripping backticks out of
    code files was measured as the fix and rejected: docstring prose carries
    unpaired backticks, so the span regex swallows whole sentences and would
    HIDE two real citations to buy this one. The example is worded around
    instead. A check weakened to spare its own docstring is worth less than the
    docstring.

    WHAT IT CANNOT ASK, AND THE HONEST LIMIT IS THE POINT (rule 5). It cannot
    tell whether the number names the RIGHT decision. Every number in the repo
    resolved on 2026-08-28 and three were still wrong -- `decision 88` for the
    playable gate, `decision 09` for the source snapshot, `decision 42` for
    event-picture geometry -- because the renumbering moved what each addressed
    while leaving a number that still resolves. A vocabulary heuristic was
    measured against the real corpus before this was written and rejected: its
    floor was 27 to 101 false positives depending on the window, and it could
    still pass a wrong number on one shared word.

    SO THE SEMANTIC HALF IS AN AUDIT, NOT A CHECK, and it is exact when it is
    run at the right moment: after a renumbering, `git blame` every bare
    citation and read the ones whose line predates the sweep, because those are
    exactly the lines it could not rewrite. That recipe found all three, and it
    lives in .docs/style-guide.md section 9 with the renumbering rule it belongs to.

    THE COUNT ON THE SUMMARY LINE IS THE DELIVERABLE. A renumbering needs a
    worklist and the 2026-08-27 sweep did not have one for this form, which is
    why it rewrote 415 link labels twice and these three not at all.
    """
    have = {int(_num(f)) for f in DOCS.glob("decisions/[0-9]*.md")}
    n = 0

    def scan(where: pathlib.Path, text: str) -> None:
        nonlocal n
        for m in BARE_DECISION.finditer(text):
            nums = LABEL_NUM.findall(m.group(1))
            n += len(nums)
            # One finding per CITATION, not per number: a citation naming a
            # range is one thing a reader followed and one edit to make, and
            # reporting it once per number, under the same quoted text, reads
            # as several defects where there is one.
            missing = [x for x in nums if int(x) not in have]
            if missing:
                quote = " ".join(m.group(0).split())
                errors.append(
                    f"{where}: '{quote}' names no decision file "
                    f"({', '.join(missing)}). The number is the address "
                    f"(.docs/style-guide.md section 3); cite the slug it "
                    f"should read.")

    for f in code_files():
        try:
            text = f.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        scan(f.relative_to(REPO), CODE_WRAP.sub(" ", text))

    for f in md_files():
        if f in GENERATED:
            continue
        # Linked citations belong to check_link_labels, which reads the href as
        # the authority; reading them here too would report one defect twice and
        # in the weaker form.
        text = LINK.sub(" ", strip_code(f.read_text(encoding="utf-8-sig")))
        scan(f.relative_to(REPO), DOC_WRAP.sub(" ", text))

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


# A dated status marker, in every form the existing decisions use. FIVE of them
# -- 24, 25, 26, 27 and 29 -- write it as an italic `*Decided ...*` paragraph
# rather than a bold `**Status:**` line, and are accepted rather than rewritten:
# a decision records what was true when it was made, so retrofitting its head is
# editing a record. See .docs/style-guide.md section 7. Re-measure the split
# rather than trusting this comment -- the count moves whenever a decision lands:
#   grep -LE '^\*\*(Status|Decided|Resolved)' .docs/decisions/[0-9]*.md
DECISION_STATUS = re.compile(
    r"^\s*(?:\*\*(?:Status|Decided|Resolved)\b|\*(?:Decided|Originally|Resolved)\b)",
    re.M)
DECISION_TITLE = re.compile(r"^#\s+(?:Decision\s+)?(\d{2,3})\s*[—-]\s*\S")


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
        elif m.group(1) != _num(f):
            errors.append(f"{f.relative_to(REPO)}: title says {m.group(1)}, "
                          f"filename says {_num(f)}")
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
LOGS_PY = REPO / "tools" / "logs.py"
LOGS_DOC = DOCS / "reference" / "game-logs.md"
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
        # and unlink in decision 12. A decision records what was true when it
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


def check_log_inventory() -> int:
    """Every log file tools/logs.py censuses is named in game-logs.md, and back.

    live-runs.md said `debug.log` was "empty in every run so far" while it held
    10,663 bytes, and had six rows for a directory of nineteen log files. Every
    link in that table resolved; the sentence was simply false, and nothing
    anywhere could say so (.docs/decisions/105-ten-log-files-nothing-had-named.md).

    So the census gets the same treatment check_validate_catalogue gives the
    check catalogue: the table in the TOOL is the source of truth, the document
    is held to it in both directions, and a game version adding a log channel
    breaks the build rather than quietly aging the page.

    Compared by BASENAME. The tool addresses `script_documentation/` members by
    path because it opens them; the page lists them by bare filename under a
    heading that supplies the directory, which is the right way to write it.
    """
    table = {f.rsplit("/", 1)[-1]: f for f in re.findall(
        r'^\s*\("([\w./]+\.log)",', LOGS_PY.read_text(encoding="utf-8-sig"), re.M)}
    documented = {n for n in re.findall(
        r"`([\w.-]+\.log)`", LOGS_DOC.read_text(encoding="utf-8-sig"))
        if not re.match(r"error\.log\.\d{4}", n)}

    for base in sorted(set(table) - documented):
        errors.append(f"{LOGS_DOC.relative_to(REPO)}: does not name "
                      f"`{table[base]}`, which tools/logs.py censuses")
    for base in sorted(documented - set(table)):
        errors.append(f"{LOGS_DOC.relative_to(REPO)}: names `{base}`, which no "
                      f"row of tools/logs.py's table censuses")
    return len(table)


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
    label_n = check_link_labels()
    bare_n = check_bare_decision_numbers()
    cite_n = check_code_citations()
    nav_n = check_nav_cards()
    dec_n = check_decision_heads()
    cat_n = check_category_readmes()
    orph_n = check_orphans()
    mk_n = check_make_targets()
    chk_n = check_validate_catalogue()
    ack_n = check_ack_keys()
    logi_n = check_log_inventory()
    hv_n = check_harvest_order()
    src_n = check_source_count()

    print(f"{DIM}docs: {nav_n} document(s) for a nav card, {dec_n} decision(s) "
          f"for a head and an index row, {link_n} internal link(s), "
          f"{label_n} numbered link label(s), "
          f"{bare_n} bare decision number(s), "
          f"{cite_n} citation(s) from code, {cat_n} category folder(s), "
          f"{orph_n} unlinked  |  inventory: {mk_n} make target(s), "
          f"{chk_n} check(s) against the catalogue, {ack_n} ack list(s), "
          f"{logi_n} log file(s) against game-logs.md, "
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
