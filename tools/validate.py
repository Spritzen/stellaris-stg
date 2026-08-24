#!/usr/bin/env python3
"""Fast structural checks that catch the Stellaris failure modes CWTools can't.

CWTools validates script semantics inside the editor. This covers the file-level
mistakes that make the game silently ignore content at load time:

  * localisation .yml missing its UTF-8 BOM  -> file dropped, keys show raw
  * localisation key missing its :0 version  -> line dropped
  * unbalanced braces in script              -> parser drops the rest of the file
  * descriptor supported_version drift       -> launcher flags the mod outdated

Plus the two failure modes the vendored-merge architecture introduces:

  * a hand-edit to a generated file  -> silently lost on the next `make vendor`
  * a src/ file shadowing a vanilla or vendored path with no explanation

Plus the class the 2026-08-01 live run found this file could not see. It had
been reporting `ok — 0 warnings` against a build throwing ~8,780 attributable
errors, because it checked file structure and never checked whether one file's
NAMES resolve against another's. That started as four checks — a script
identifier resolving nowhere, a shader effect nothing declares, length-coupled
define arrays of different lengths, a name-list token with no loc key — and has
grown one live run at a time to most of this file.

Each check's docstring records the live run that made it necessary. Do not add
one without a defect it would have caught: a check that cannot fail is worse
than an absent one, because it reports a number.

Scope: the structural checks run over `src/` — the content we actually author.
The generated tree is verified by checksum against .vendor-manifest.json
instead. Brace-checking 20,000 vendored files on every run would be slow and
would only ever report problems in other people's mods that we cannot fix.
The cross-reference checks are the exception: they must read the generated
tree, because "does this name resolve" is a question about the merged whole and
is meaningless per-file.
"""

from __future__ import annotations

import collections
import functools
import hashlib
import json
import os
import re
import struct
import sys
from fnmatch import fnmatch as _fnmatch
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# The generated mod tree (decision 13). Every check that asks "what will the
# game load" reads BUILD; every check that asks "what did we write" reads
# REPO/src. Keeping the two apart in the path is the point of the split -- the
# cross-reference checks exist precisely because those are different questions.
BUILD = REPO / "stg-build"
STATE = REPO / ".vendor-manifest.json"
GAME_DIR = Path(os.environ.get("STELLARIS_GAME_DIR", "/stellaris"))
SKIP_DIRS = {".git", ".devcontainer", ".vscode", "tools", "dist", "__pycache__",
             ".claude", ".source", ".vendor-cache"}

# Kept in step with tools/vendor.py: text is hashed with line endings
# normalised, because several sources ship CRLF.
TEXT_SUFFIXES = {
    ".txt", ".gui", ".gfx", ".asset", ".yml", ".yaml", ".csv",
    ".json", ".mod", ".settings", ".dlc", ".md", ".shader", ".fxh",
}

# ── Per-directory merge semantics ────────────────────────────────────────────
#
# Which of two files claiming the same key the engine keeps. Transcribed from
# Irony Mod Manager, which maintains it against years of bug reports; see
# .docs/decisions/29-merge-semantics-per-directory.md for what was taken, what
# was rejected, and why this one table is not measured against /stellaris the
# way every other allowlist here is.
#
# THE REST OF THIS FILE DERIVES ITS RULES FROM VANILLA'S OWN USAGE AND THIS
# TABLE CANNOT BE. Vanilla ships 40 files in common/ship_sizes and 1 in
# common/strategic_resources; nothing in the layout distinguishes a directory
# that resolves first-wins from one that resolves last-wins, because the
# difference lives in the engine's loader and never on disk. So this is the one
# borrowed table, and it is quarantined here rather than spread across the
# checks that read it.

# FIOS -- "first in order of sequence". A contested key goes to the FIRST
# filename in ordinal sort. Every directory NOT listed here is LIOS and the last
# filename wins, which is what this file assumed everywhere before decision 29.
# Paths are exact; Irony matches a trailing component, which also catches
# common/inline_scripts/traits and is not what it means.
FIOS_DIRS = {
    "common/component_sets", "common/component_templates", "common/event_chains",
    "common/global_ship_designs", "common/governments/authorities",
    "common/scripted_variables", "common/section_templates",
    "common/ship_behaviors", "common/solar_system_initializers",
    "common/special_projects", "common/start_screen_messages",
    "common/strategic_resources", "common/traits", "events",
}

# Directories where a FILE is the unit and no key-level merge happens: the id is
# the filename, so two differently-named files never resolve against each other
# at all. A contested key here is not "one key loses" -- it is a question about
# two whole files, so findings in these directories carry an extra note rather
# than being suppressed. Suppressing them would have deleted the live
# random_names/star_names finding, which is real.
WHOLE_TEXT_DIRS = {
    "common/component_tags", "common/country_container", "common/diplo_phrases",
    "common/diplomacy_economy", "common/economic_plans",
    "common/gamesetup_settings", "common/inline_scripts", "common/job_tags",
    "common/name_lists", "common/random_names", "common/random_names/base",
    "common/species_classes", "common/species_names",
    "common/start_screen_messages", "common/terraform", "common/trait_tags",
    "gfx/portraits/portraits", "map/galaxy", "map/setup_scenarios",
}

# Databases whose entries carry meaning in the ORDER they are declared, across
# the whole directory rather than within one file. Irony re-emits each of these
# as a single file to preserve that order; we cannot, because we ship the source
# mods' files as they are. See check_order_sensitive_databases.
ORDER_SENSITIVE_DIRS = {
    "common/ethics", "common/governments/authorities", "common/ship_sizes",
    "common/starbase_modules", "common/strategic_resources",
}

RED, YEL, GRN, DIM, OFF = "\033[31m", "\033[33m", "\033[32m", "\033[2m", "\033[0m"

errors: list[str] = []
warnings: list[str] = []


def walk(suffixes: tuple[str, ...], *, under: str | None = None):
    root = REPO / under if under else REPO
    if not root.is_dir():
        return
    for p in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and p.suffix in suffixes:
            yield p


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


def check_localisation() -> int:
    n = 0
    for p in walk((".yml",), under="src/localisation"):
        n += 1
        raw = p.read_bytes()

        if not raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{rel(p)}: missing UTF-8 BOM (game will ignore this file) "
                          f"-- fix with: make fix-bom")
            continue

        text = raw.decode("utf-8-sig")
        lines = text.splitlines()
        if not lines or not re.match(r"^l_[a-z_]+:\s*$", lines[0]):
            errors.append(f"{rel(p)}:1: first line must be a language tag like 'l_english:'")

        expected = p.parent.name
        if lines and expected != "localisation":
            tag = lines[0].rstrip(":").strip()
            if tag != f"l_{expected}":
                warnings.append(f"{rel(p)}:1: '{tag}' in a '{expected}/' folder")

        for i, line in enumerate(lines[1:], start=2):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if not re.match(r'^[A-Za-z0-9_.\-]+:\d*\s+".*"\s*$', s):
                errors.append(f"{rel(p)}:{i}: malformed entry (need  KEY:0 \"value\")  -> {s[:60]}")
    return n


def _bom_convention(folder: str) -> bool | None:
    """Does vanilla BOM this folder's script files? True / False / no opinion.

    DERIVED, NOT ASSERTED. This rule used to read "script files should not have
    a BOM", globally — which is right for 37 of vanilla's 39 common/ databases
    and flatly wrong for common/name_lists/, where vanilla BOMs 76 files out of
    76. The game agrees with vanilla and not with the rule: our five un-BOMed
    name lists logged `File '...' should be in utf8-bom encoding` five times in
    the 2026-08-02 run, and `make validate` was warning against the fix.

    So ask vanilla per folder, the same way check_dangling_shaders takes its
    built-in shader list from what vanilla references. Unanimity either way is a
    convention; anything in between (common/technology/ is 1 of 33) is one
    author's stray byte and gets no opinion at all.
    """
    d = GAME_DIR / folder
    if not d.is_dir():
        return None
    files = list(d.glob("*.txt"))
    if len(files) < 4:
        return None
    bom = sum(1 for f in files if f.read_bytes().startswith(b"\xef\xbb\xbf"))
    if bom == len(files):
        return True
    if bom == 0:
        return False
    return None


def check_script() -> int:
    n = 0
    for p in walk((".txt", ".gui", ".gfx", ".asset"), under="src"):
        if p.name == "descriptor.mod":
            continue
        n += 1
        raw = p.read_bytes()
        has_bom = raw.startswith(b"\xef\xbb\xbf")
        folder = p.parent.relative_to(REPO / "src").as_posix()
        wants = _bom_convention(folder)
        if wants is True and not has_bom:
            errors.append(f"{rel(p)}: missing UTF-8 BOM. Vanilla's {folder}/ BOMs "
                          f"every file and the game logs `should be in utf8-bom "
                          f"encoding` without it -- fix with: make fix-bom")
        elif wants is False and has_bom:
            warnings.append(f"{rel(p)}: has a UTF-8 BOM; vanilla's {folder}/ BOMs "
                            f"none of its files")

        text = raw.decode("utf-8", errors="replace")
        if "�" in text:
            errors.append(f"{rel(p)}: not valid UTF-8")
            continue

        depth, line_no = 0, 1
        opened: list[int] = []
        in_str = in_comment = False
        for ch in text:
            if ch == "\n":
                line_no += 1
                in_comment = False
            elif in_comment:
                continue
            elif ch == '"':
                in_str = not in_str
            elif in_str:
                continue
            # A BRACE INSIDE A COMMENT IS NOT A BRACE, and the scanner used to
            # count it. STNH's ship art comments out whole `state = { ... }`
            # blocks and leaves the opener behind: those files are +2 on a raw
            # count and balanced on a real one. The game reads them fine, and
            # this check only ever saw them once one became an src/ override.
            elif ch == "#":
                in_comment = True
            elif ch == "{":
                depth += 1
                opened.append(line_no)
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    errors.append(f"{rel(p)}:{line_no}: unmatched closing brace")
                    break
                opened.pop()
        else:
            if depth > 0:
                errors.append(f"{rel(p)}: {depth} unclosed brace(s), first opened at line {opened[0]}")
    return n


def digest(path: Path) -> str:
    h = hashlib.sha256()
    normalise = path.suffix.lower() in TEXT_SUFFIXES
    with path.open("rb") as fh:
        while chunk := fh.read(1 << 20):
            h.update(chunk.replace(b"\r\n", b"\n") if normalise else chunk)
    return h.hexdigest()


def check_vendored() -> int:
    """Catch hand-edits to generated files, which `make vendor` would discard.

    Cheap by design: size and mtime come straight from the recorded stat, and
    only files that differ on either are re-hashed. `make vendor` preserves the
    source mtime, so an edit always trips the stat check first.
    """
    if not STATE.is_file():
        warnings.append("no .vendor-manifest.json -- the mod tree has not been "
                        "built. Run: make vendor")
        return 0

    try:
        state = json.loads(STATE.read_text())
    except ValueError as exc:
        errors.append(f".vendor-manifest.json: unreadable ({exc}) -- run: make vendor")
        return 0

    generated = state.get("generated", {})
    missing = edited = 0

    for relpath, rec in generated.items():
        p = BUILD / relpath
        if not p.is_file():
            missing += 1
            if missing <= 5:
                errors.append(f"{relpath}: generated file is missing -- run: make vendor")
            continue
        st = p.stat()
        if st.st_size == rec.get("size") and st.st_mtime == rec.get("mtime"):
            continue
        if digest(p) != rec.get("sha256"):
            edited += 1
            if edited <= 10:
                src = rec.get("source", "?")
                errors.append(
                    f"{relpath}: hand-edited, but this file is GENERATED from "
                    f"'{src}'. `make vendor` will discard the change. Put it in "
                    f"src/{relpath} or declare a patch in vendor.yml instead.")

    if missing > 5:
        errors.append(f"... and {missing - 5} more generated file(s) missing")
    if edited > 10:
        errors.append(f"... and {edited - 10} more hand-edited generated file(s)")

    # Anything in the game tree that no source and no src/ file accounts for.
    # It survives today and vanishes on the next `make clean-vendor`.
    tracked = set(generated)
    stray = 0
    for top in ("common", "events", "flags", "fonts", "gfx", "interface",
                "localisation", "map", "music", "prescripted_countries",
                "sound", "unchecked_defines"):
        root = BUILD / top
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if p.is_file() and str(p.relative_to(BUILD)) not in tracked:
                stray += 1
                if stray <= 5:
                    rp = p.relative_to(BUILD)
                    warnings.append(f"{rp}: in the generated tree but not from any "
                                    f"source -- move it to src/{rp}")
    if stray > 5:
        warnings.append(f"... and {stray - 5} more untracked file(s) in the generated tree")

    return len(generated)


def check_src_shadowing() -> int:
    """A src/ file that replaces a vanilla or vendored file must say why.

    Per .docs/guides/writing-script.md the prefix rule has exactly one exception: compat and override
    files keep the vanilla or source filename so they shadow it. Those are the
    files most likely to silently revert content nobody remembers we wanted, so
    each one needs a header comment.
    """
    src = REPO / "src"
    if not src.is_dir():
        return 0

    vendored: dict[str, str] = {}
    if STATE.is_file():
        try:
            for k, v in json.loads(STATE.read_text()).get("generated", {}).items():
                vendored[k] = v.get("source", "?")
        except ValueError:
            pass

    n = 0
    for p in sorted(src.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        n += 1
        rel = p.relative_to(src).as_posix()

        shadows = None
        if (GAME_DIR / rel).is_file():
            shadows = "a vanilla file"
        else:
            owner = vendored.get(rel)
            if owner and owner != "src/":
                shadows = f"'{owner}'"
        if not shadows:
            continue

        head = p.read_text(encoding="utf-8-sig", errors="replace").lstrip()
        if not head.startswith("#"):
            errors.append(f"src/{rel}: shadows {shadows} but has no header comment. "
                          f"Say what it overrides and why (.docs/guides/writing-script.md).")
    return n


def check_vanilla_regression() -> int:
    """Vendored script that shadows a vanilla file and DROPS definitions.

    .docs/architecture/stnh-art.md's `additive_only` rule stops STNH overwriting paths an earlier
    SOURCE claims. Nothing stopped it overwriting vanilla. STNH is a 3.12-era
    total conversion, so its copy of a vanilla 4.4 file is usually the 3.12 one
    minus whatever 4.4 added -- and the game loads it in place of the real thing
    with no complaint. That is how we shipped a flags/colors.txt missing 47 of
    vanilla's 72 flag colours while vanilla prescripted empires still asked for
    them. See .docs/decisions/08-stnh-art-shadows-vanilla.md.

    Checked: `additive_only` sources, PLUS any source whose descriptor declares
    a supported_version below the target. The original scope was additive_only
    alone, on the premise that "every other mod in the harvest is a live 4.x mod
    that overrides vanilla on purpose -- that is what mods are". The 2026-08-01
    run measured that premise false for part of the harvest: ASB Ironman shadows
    262 vanilla paths from a 3.x codebase and throws parse errors, Starbase
    Extended duplicates vanilla 4.4 definitions, Whiter Stars declares 3.*. A
    mod deliberately overriding the game it was WRITTEN against is not the same
    as one overriding the game we are RUNNING. Only 28 of 23,507 files were
    being examined.
    """
    if not STATE.is_file():
        return 0
    try:
        state = json.loads(STATE.read_text())
    except ValueError:
        return 0

    checkable = _legacy_sources()
    if not checkable:
        return 0

    # Drops that have been looked at and signed off in vendor.yml.
    ack = _ack_list("vanilla_regression_ack")

    return _vanilla_regression_body(state, checkable, ack)


@functools.lru_cache(maxsize=1)
def _legacy_sources() -> frozenset[str]:
    """Sources whose copy of a vanilla file is a copy of an OLDER vanilla file.

    `additive_only` sources, plus any source whose descriptor declares a
    supported_version below the target. The distinction is calibrated and is
    used by two checks: a mod deliberately overriding the game it was WRITTEN
    against is not the same as one overriding the game we are RUNNING.
    """
    manifest = REPO / "vendor.yml"
    if not manifest.is_file():
        return frozenset()
    text = manifest.read_text(encoding="utf-8-sig")

    # Source name -> workshop id, and which declare additive_only. Parsed by
    # hand rather than taking a YAML dependency, as elsewhere in this file.
    additive: set[str] = set()
    ids: dict[str, str] = {}
    name = sid = None
    for line in text.splitlines():
        m = re.match(r'\s*-\s*id:\s*"?(\d+)"?\s*$', line)
        if m:
            sid, name = m.group(1), None
            continue
        m = re.match(r"\s*-?\s*name:\s*(.+?)\s*$", line)
        if m:
            name = m.group(1).strip().strip("\"'")
            if sid:
                ids[name] = sid
        elif re.match(r"\s*additive_only:\s*(yes|true)\s*$", line, re.I) and name:
            additive.add(name)

    # Sources declaring a supported_version older than the target. Their copy of
    # a vanilla path is a copy of an OLDER vanilla path, which is the same
    # hazard additive_only was written for.
    m = re.search(r"^\s*source_root:\s*(\S+)\s*$", text, re.M)
    root = Path(m.group(1).strip("\"'") if m else ".source")
    if not root.is_absolute():
        root = REPO / root

    target = ""
    ls = GAME_DIR / "launcher-settings.json"
    if ls.is_file():
        try:
            target = json.loads(ls.read_text()).get("modsCompatibilityVersion", "")
        except (ValueError, OSError):
            target = ""

    stale: set[str] = set()
    if target:
        want = target.split(".")[:2]
        for nm, wid in ids.items():
            desc = root / wid / "descriptor.mod"
            if not desc.is_file():
                continue
            sv = re.search(r'^\s*supported_version\s*=\s*"([^"]+)"', _read(desc), re.M)
            if not sv:
                continue
            parts = sv.group(1).split(".")
            try:                                    # "3.*" / "4.1" / "v4.*.*"
                major = int(parts[0].lstrip("v"))
            except ValueError:
                continue
            if major < int(want[0]):
                stale.add(nm)
            elif major == int(want[0]) and len(parts) > 1 and parts[1] not in ("*", "**"):
                try:
                    if int(parts[1]) < int(want[1]):
                        stale.add(nm)
                except ValueError:
                    pass

    return frozenset(additive | stale)


def _vanilla_regression_body(state: dict, checkable: frozenset[str],
                             ack: set[str]) -> int:
    # Only depth-0 `key = {` blocks are database definitions. Anything deeper is
    # a trigger or a scope (any_owned_planet, OR, add ...) and comparing those
    # produces nothing but noise.
    tok_re = re.compile(r"([A-Za-z_][\w'.-]*)\s*=\s*\{|\{|\}|#[^\n]*|\"[^\"]*\"")

    def keys(path: Path) -> set[str]:
        """What this file DECLARES, by whatever names identity actually uses.

        For a `.txt` database the depth-0 block key IS the identity. For an
        `.asset` or `.gfx` it is not: every declaration is `entity = { name =
        "..." }`, so ~1,700 declarations collapse to the single token `entity`
        on both sides and the comparison can never fail. That blindness cost
        110 measured errors and 116 latent ones -- STNH dropping
        pre_ftl_chemical_ship_mesh_entity, and Real Space - System Scale
        dropping the 4.4 Dyson sphere and quantum catapult shipsets -- while
        this check counted those very files as examined. See the 2026-08-02
        analysis §7.
        """
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r", "")
        except OSError:
            return set()

        if path.suffix.lower() in {".asset", ".gfx"}:
            return _declared_names(text)

        found: set[str] = set()
        depth = 0
        for m in tok_re.finditer(text):
            tok = m.group(0)
            if tok.startswith(("#", '"')):
                continue
            if tok == "}":
                depth = max(0, depth - 1)
            elif tok == "{":
                depth += 1
            else:
                if depth == 0:
                    found.add(m.group(1))
                depth += 1
        return found

    # Everything the merged tree declares in an .asset/.gfx, and where. A
    # dropped entity is only lost if NOTHING ELSE declares it: a mod that moves
    # its own declarations between files is not a regression. Subsumes the src/
    # rescue below.
    elsewhere: dict[str, set[str]] = {}
    for root in (BUILD, REPO / "src"):
        for suffix in ("*.asset", "*.gfx"):
            for f in root.rglob(suffix):
                if any(part in SKIP_DIRS for part in f.parts):
                    continue
                key = str(f.relative_to(root))
                for nm in _declared_names(_read(f)):
                    elsewhere.setdefault(nm, set()).add(key)

    checked = 0
    for relpath, info in sorted(state.get("generated", {}).items()):
        suffix = Path(relpath).suffix.lower()
        if suffix not in {".txt", ".gui", ".gfx", ".asset"}:
            continue
        # .gui stays scoped to additive_only and stale sources: a live 4.x mod
        # overriding a vanilla layout is what mods ARE.
        #
        # .txt USED TO share that scoping, on the same premise. The 2026-08-07
        # run measured the premise false: Real Space 4.0 is a current 4.x mod,
        # was therefore never examined, and drops twelve vanilla Sol-neighbour
        # initializers that PLANETARY DIVERSITY still references -- four
        # `Invalid initializer` errors a run and three neighbour systems that
        # never generate. Intent is not the discriminator. A mod may replace a
        # vanilla database on purpose and still strand a THIRD mod that calls
        # the old keys. See .docs/decisions/38-real-space-drops-sol-neighbours.md.
        #
        # Widening cost one line and was calibrated first: over every vendored
        # .txt shadowing a vanilla path it yields 31 dropped keys in 11 files,
        # 8 of them already acked, and the `elsewhere` rescue below clears both
        # remaining false positives. 1 finding, 0 false positives.
        #
        # .asset/.gfx get no scoping either. Real Space - System Scale is
        # neither additive_only nor stale and still drops 111 vanilla entities
        # across two files -- shipsets 4.4 added after they were written. Nobody
        # overrides art in order to delete a shipset; they just have not
        # resynced.
        #
        # src/ is exempt from the .txt widening, and only from that. STG is a
        # total conversion: emptying vanilla's prescripted empires out of
        # src/common/prescripted_countries/ is the point, not a regression, and
        # widening without this gate reported 63 such keys across 19 files.
        # src/ has its own two checks -- check_src_shadowing demands every
        # shadow be annotated, and check_src_source_regression (decision 34)
        # catches src/ dropping what a SOURCE declares.
        if suffix == ".gui" and info.get("source") not in checkable:
            continue
        if suffix == ".txt" and info.get("source") == "src/":
            continue
        if relpath in ack:
            continue
        van = GAME_DIR / relpath
        if not van.is_file():
            continue
        checked += 1
        lost = keys(van) - keys(BUILD / relpath)
        if lost and suffix in {".asset", ".gfx"}:
            lost = {n for n in lost if elsewhere.get(n, set()) <= {relpath}}
        elif lost:
            # A mod MOVING its own declarations between files is not a
            # regression, and it is the majority of what widening the .txt
            # scope turned up: Real Space moved `trappist_initializer` into
            # solsector_large_systems.txt, Planetary Diversity moved the nine
            # `trait_pc_*_preference` traits into
            # 04_species_traits_habitability_cold.txt. Both look identical to a
            # drop when only this one path is read.
            #
            # A database key resolves within its own DIRECTORY, so that is where
            # "declared elsewhere" is asked -- siblings only, not the whole
            # tree. Cheaper than a global index and the more correct question:
            # the same key in a different database is a different key.
            for sib in (BUILD / relpath).parent.glob("*" + Path(relpath).suffix):
                if sib.name != Path(relpath).name:
                    lost -= keys(sib)
                if not lost:
                    break
        if lost and suffix not in {".asset", ".gfx"}:
            # src/ may restore the dropped keys under a different filename.
            for s in (REPO / "src").rglob("*" + Path(relpath).suffix):
                if s.is_file():
                    lost -= keys(s)
                if not lost:
                    break
        if lost:
            shown = " ".join(sorted(lost)[:6])
            more = f" (+{len(lost) - 6} more)" if len(lost) > 6 else ""
            warnings.append(
                f"{relpath}: vendored from '{info['source']}' over a vanilla file, "
                f"dropping {len(lost)} definition(s) vanilla still makes: {shown}{more}. "
                f"Exclude it in vendor.yml or restore them in src/.")
    return checked


_SHADER_DECL = re.compile(
    r"^\s*(?:Effect|BlendState|DepthStencilState|RasterizerState)\s+(\w+)\s*$", re.M)


def _declared_keys(path: Path) -> set[str]:
    """What a file DECLARES, by whatever names identity actually uses.

    Three shapes, and picking the wrong one gives a confident wrong answer --
    decision 33. Depth-0 block keys are identity in a `.txt`; in an `.asset`
    every declaration reads `entity = { name = "…" }` so identity is the nested
    name; in a `.shader` it is the `Effect`/state declaration line.
    """
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r", "")
    except OSError:
        return set()
    suffix = path.suffix.lower()
    if suffix in {".asset", ".gfx"}:
        return _declared_names(text)
    if suffix == ".shader":
        return set(_SHADER_DECL.findall(text))
    found: set[str] = set()
    depth = 0
    for m in _DEF_TOK.finditer(text):
        tok = m.group(0)
        if tok.startswith(("#", '"')):
            continue
        if tok == "}":
            depth = max(0, depth - 1)
        elif tok == "{":
            depth += 1
        else:
            if depth == 0:
                found.add(m.group(1))
            depth += 1
    return found


def check_src_source_regression() -> int:
    """An src/ override that drops declarations the SOURCE it shadows makes.

    check_vanilla_regression asks this about vanilla, and that is only half the
    question: `src/` is applied last and beats vendored content too, so an
    override at a path a source also ships silently replaces the source's copy.
    The manifest records exactly which, so this needs no guessing -- the paths
    where src/ overwrote a source (182 on the build of 2026-08-10), and `from`
    names which one.

    That gap shipped a real defect. src/gfx/FX/pdxmesh.shader was written as
    "vanilla 4.4 plus STNH's five effects" and Real Space ships that same path
    with 41 effects of its own appended. The override dropped all 41, and
    gfx/models/planets/rs_rings_entities.asset asks for PdxMeshPlanetRingsRS by
    name: `Failed to create material` at load, gas giant rings drawn with no
    effect in play. Nothing reported it -- check_vanilla_regression compares
    against vanilla, which never declared it, and check_dangling_shaders found
    the name declared in Real Space's own rs_pdxmesh.shader and was satisfied.
    See .docs/decisions/34-src-shadows-drop-source-declarations.md.

    A dropped name is only lost if nothing else declares it, so an override that
    moves a declaration to another filename is not a regression.
    """
    manifest = REPO / ".vendor-manifest.json"
    if not (manifest.is_file() and STATE.is_file()):
        return 0
    try:
        overwrites = json.loads(manifest.read_text()).get("overwrites", [])
    except ValueError:
        return 0

    vy = REPO / "vendor.yml"
    if not vy.is_file():
        return 0
    text = vy.read_text(encoding="utf-8-sig")
    m = re.search(r"^\s*source_root:\s*(\S+)\s*$", text, re.M)
    root = Path(m.group(1).strip("\"'") if m else ".source")
    if not root.is_absolute():
        root = REPO / root

    ids: dict[str, str] = {}
    sid = None
    for line in text.splitlines():
        mm = re.match(r'\s*-\s*id:\s*"?(\d+)"?\s*$', line)
        if mm:
            sid = mm.group(1)
            continue
        mm = re.match(r"\s*-?\s*name:\s*(.+?)\s*$", line)
        if mm and sid:
            ids[mm.group(1).strip().strip("\"'")] = sid

    src = REPO / "src"
    elsewhere: dict[str, set[str]] = {}
    for r in (BUILD, src):
        for suffix in ("*.asset", "*.gfx"):
            for f in r.rglob(suffix):
                if any(part in SKIP_DIRS for part in f.parts):
                    continue
                key = str(f.relative_to(r))
                for nm in _declared_names(_read(f)):
                    elsewhere.setdefault(nm, set()).add(key)

    ack = _ack_list("src_regression_ack")
    checked = 0
    for o in overwrites:
        if o.get("to") not in ("src/", "src"):
            continue
        rel = o["path"]
        if rel in ack or Path(rel).suffix.lower() not in {
                ".txt", ".gui", ".gfx", ".asset", ".shader"}:
            continue
        wid = ids.get(o.get("from", ""))
        if not wid:
            continue
        theirs = root / wid / rel
        ours = src / rel
        if not (theirs.is_file() and ours.is_file()):
            continue
        checked += 1
        lost = _declared_keys(theirs) - _declared_keys(ours)
        # A declaration is only LOST if nothing else in the merged tree makes
        # it. Sources move declarations between their own files all the time --
        # Real Space keeps 11 star classes in realspace_planet_classes.txt
        # rather than 00_planet_classes.txt, and rs_pdxmesh.shader carries the
        # render states its own pdxmesh.shader block repeats. Both looked like
        # regressions until this rescue existed; neither is one.
        if lost:
            suffix = Path(rel).suffix.lower()
            if suffix in {".asset", ".gfx"}:
                # Art resolves across the whole tree, so scope the rescue there.
                lost = {n for n in lost if elsewhere.get(n, set()) <= {rel}}
            else:
                # A database is its directory; a shader effect, gfx/FX.
                sibs = (BUILD / "gfx/FX") if suffix == ".shader" \
                    else (BUILD / rel).parent
                for f in sorted(sibs.glob("*" + suffix)) if sibs.is_dir() else []:
                    if f != BUILD / rel:
                        lost -= _declared_keys(f)
                    if not lost:
                        break
        if lost:
            shown = " ".join(sorted(lost)[:6])
            more = f" (+{len(lost) - 6} more)" if len(lost) > 6 else ""
            warnings.append(
                f"src/{rel}: overrides '{o['from']}''s copy of this path and drops "
                f"{len(lost)} declaration(s) it makes: {shown}{more}. src/ is "
                f"applied last, so the source's version is gone — anything that "
                f"referenced these resolves against nothing. Restore them in the "
                f"override, or ack in vendor.yml under src_regression_ack. "
                f"See .docs/decisions/34-src-shadows-drop-source-declarations.md.")
    return checked


# ---------------------------------------------------------------------------
# Cross-reference checks. Everything above asks "is this file well formed?";
# everything below asks "do its names resolve against the rest of the merge?".
# That is the question the 2026-08-01 live run answered with 8,780 errors while
# this script reported clean.
# ---------------------------------------------------------------------------

# A `key = {` at brace depth 0 is a database definition. Anything deeper is a
# trigger or a scope. Shared with check_vanilla_regression's local version.
_DEF_TOK = re.compile(r"([A-Za-z_][\w'.-]*)\s*=\s*\{|\{|\}|#[^\n]*|\"[^\"]*\"")


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8-sig", errors="replace").replace("\r", "")
    except OSError:
        return ""


def _strip_comments(text: str) -> str:
    return re.sub(r"#[^\n]*", "", text)


def _body_sha(body: str) -> str:
    """Content identity for a declaration body, indifferent to formatting.

    Irony Mod Manager's DefinitionSHA (decision 29): flatten to one line,
    collapse every run of whitespace, then delete the spaces that sit next to
    `=`, `{` and `}` -- the three places Stellaris script is written a dozen
    ways and means one. Two sources shipping `trait = { cost = 2 }` and a
    tab-indented multi-line spelling of the same thing hash the same, which is
    the point: whichever the engine keeps, the game is identical, so it is not
    a conflict and reporting it only teaches us to skim the check.

    Comments are already gone -- callers strip them before the text gets here --
    so a re-worded comment does not make two identical bodies look different.

    Deliberately NOT case-folded. Stellaris keys are matched case-sensitively in
    most databases and `is_species_class = FED` is not `is_species_class = fed`.

    The one way this can mislead: whitespace inside a quoted string is collapsed
    too, so `"a  b"` and `"a b"` hash alike. Nothing in the tree has a
    double-spaced string literal and a texture path with one would be broken
    anyway, but it is the direction the error runs -- toward calling two things
    the same, i.e. toward silence. Weigh that before widening the normalisation.
    """
    one = " ".join(body.split())
    for a, b in ((" =", "="), ("= ", "="), (" {", "{"),
                 ("{ ", "{"), (" }", "}"), ("} ", "}")):
        one = one.replace(a, b)
    return hashlib.sha256(one.encode("utf-8")).hexdigest()


def _top_level_keys(text: str) -> set[str]:
    found: set[str] = set()
    depth = 0
    for m in _DEF_TOK.finditer(text):
        tok = m.group(0)
        if tok.startswith(("#", '"')):
            continue
        if tok == "}":
            depth = max(0, depth - 1)
        elif tok == "{":
            depth += 1
        else:
            if depth == 0:
                found.add(m.group(1))
            depth += 1
    return found


_DECL_BLOCK = re.compile(r"^\s*(entity|mesh|pdxmesh|pdxparticle)\s*=\s*\{", re.M)


def _declared_names(text: str) -> set[str]:
    """Names declared by an `.asset` / `.gfx` file.

    Identity in these files lives in a nested `name = "..."`, not in the block
    key. Only the FIRST name inside each top-level block is the declaration --
    everything after it is a locator, a meshsettings shape or an animation, and
    hoovering those up is what turns a 3-file finding into a 70-file one.
    """
    found: set[str] = set()
    for m in _DECL_BLOCK.finditer(text):
        i, depth = m.end(), 1
        while i < len(text) and depth:
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        nm = re.search(r'name\s*=\s*"([^"]+)"', _strip_comments(text[m.start():i]))
        if nm:
            found.add(nm.group(1))
    return found


@functools.lru_cache(maxsize=1)
def _manifest() -> dict:
    """The build manifest — `.vendor-manifest.json`, which records the source
    every generated file came from."""
    if not STATE.is_file():
        return {}
    try:
        return json.loads(STATE.read_text())
    except ValueError:
        return {}


def _manifest_text() -> str:
    p = REPO / "vendor.yml"
    return p.read_text(encoding="utf-8-sig") if p.is_file() else ""


def check_manifest_parses() -> int:
    """vendor.yml must parse as YAML, because `make vendor` parses it as YAML.

    Everything else in this file reads vendor.yml with regexes, which is
    deliberate -- no YAML dependency for a structural check. The cost is that a
    manifest can be syntactically broken and every check here still passes: on
    2026-08-02 `key_conflict_families` was written as a block sequence nested
    directly under a mapping key, which is not valid YAML, and `make vendor`
    had been unable to run for as long as nobody tried. `make validate` said
    ok -- 6 warnings throughout.

    One import, one parse, and the failure names the line.
    """
    p = REPO / "vendor.yml"
    if not p.is_file():
        errors.append("vendor.yml: missing from repo root")
        return 0
    try:
        import yaml
    except ImportError:                       # same dependency vendor.py needs
        warnings.append("PyYAML not installed -- cannot check that vendor.yml parses")
        return 0
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8-sig"))
    except yaml.YAMLError as exc:
        errors.append(f"vendor.yml: does not parse as YAML, so `make vendor` "
                      f"cannot run -- {str(exc).splitlines()[0]} "
                      f"({getattr(exc, 'problem_mark', '?')})")
        return 0
    if not isinstance(data, dict) or not data.get("sources"):
        errors.append("vendor.yml: parses but declares no 'sources'")
        return 0
    return len(data["sources"])


def _ack_list(name: str) -> set[str]:
    """Entries under a `<name>:` block in vendor.yml.

    The same reviewed-and-signed-off mechanism `vanilla_regression_ack` uses.
    A cross-reference check that cannot be silenced for a known, understood case
    gets ignored wholesale, which is worse than not having it.
    """
    ack: set[str] = set()
    inside = False
    for line in _manifest_text().splitlines():
        if re.match(rf"\s*{re.escape(name)}:\s*$", line):
            inside = True
        elif inside:
            # `  - value` with an optional trailing `# comment`, which these
            # lists use heavily -- an ack entry without a reason is not an ack.
            m = re.match(r"\s+-\s*([^#\s]+)\s*(?:#.*)?$", line)
            if m:
                ack.add(m.group(1).strip("\"'"))
            elif line.strip() and not line.lstrip().startswith("#"):
                inside = False
    return ack


def _database(*dirs: Path) -> set[str]:
    """Every top-level key defined across a game-directory family."""
    keys: set[str] = set()
    for d in dirs:
        if d.is_dir():
            for f in d.rglob("*.txt"):
                keys |= _top_level_keys(_read(f))
    return keys


def check_dangling_identifiers() -> int:
    """Script identifiers in the built art that resolve to nothing.

    This is the check that would have caught the single largest defect class in
    the 2026-08-01 log — 1,462 errors, 17% of the file — every one of them a
    name in a VENDORED file with no definition anywhere in the merged tree:

      is_species_class = FED   660 errors  49 undefined STNH species classes
      has_trait = X            361         leader_trait_starfleet_32 and one more
      <trigger> = yes|no        41         isBajoranReligiousLeader

    Why the art and not the whole tree: STNH's clothing and hair selectors are
    the one place we deliberately ship someone else's script without their
    common/ (.docs/architecture/stnh-art.md), so it is the one place names are systematically
    expected to dangle. Vendored gameplay mods define what they reference.

    The reference side is authoritative, not the definition side. The original
    139-stub harvest read STNH's trigger DEFINITIONS and so missed
    isBajoranReligiousLeader, which STNH references but leaves commented out in
    its own file. Reading references and asking what resolves cannot miss that.

    `X = yes|no` is also ordinary engine vocabulary (`default = yes`), so the
    allowlist is whatever vanilla's own gfx/portraits/ uses the same way. A name
    vanilla never uses and nothing defines is a real dangling reference.
    """
    art = BUILD / "gfx" / "portraits"
    if not art.is_dir():
        return 0

    triggers = _database(GAME_DIR / "common/scripted_triggers",
                         BUILD / "common/scripted_triggers",
                         REPO / "src/common/scripted_triggers")
    traits = _database(GAME_DIR / "common/traits",
                       BUILD / "common/traits",
                       REPO / "src/common/traits")
    classes = _database(GAME_DIR / "common/species_classes",
                        BUILD / "common/species_classes",
                        REPO / "src/common/species_classes")

    bool_ref = re.compile(r"\b([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(?:yes|no)\b")
    # Quoted as well as bare -- see _SPECIES_CLASS_REF.
    named_ref = re.compile(
        r'\b(has_trait|is_species_class)\s*=\s*"?([A-Za-z_][A-Za-z_0-9]*)"?')

    vocab: set[str] = set()
    van_art = GAME_DIR / "gfx" / "portraits"
    if van_art.is_dir():
        for f in van_art.rglob("*.txt"):
            vocab |= {m.group(1) for m in bool_ref.finditer(_strip_comments(_read(f)))}

    ack = _ack_list("dangling_identifier_ack")
    dangling: dict[str, tuple[str, int, str]] = {}   # name -> (kind, count, example file)
    n = 0
    for f in art.rglob("*.txt"):
        n += 1
        text = _strip_comments(_read(f))
        rp = str(f.relative_to(BUILD))
        for m in bool_ref.finditer(text):
            name = m.group(1)
            if name in vocab or name in triggers or name in ack:
                continue
            kind, count, where = dangling.get(name, ("scripted trigger", 0, rp))
            dangling[name] = (kind, count + 1, where)
        for m in named_ref.finditer(text):
            field, name = m.group(1), m.group(2)
            known = traits if field == "has_trait" else classes
            if name in known or name in ack:
                continue
            kind = "trait" if field == "has_trait" else "species class"
            _, count, where = dangling.get(name, (kind, 0, rp))
            dangling[name] = (kind, count + 1, where)

    for name, (kind, count, where) in sorted(dangling.items(), key=lambda kv: -kv[1][1])[:12]:
        errors.append(
            f"{where}: {kind} '{name}' is referenced by vendored art ({count} "
            f"reference(s)) but defined nowhere in vanilla, the vendored tree or "
            f"src/. Every reference is an error.log entry. Stub it in "
            f"src/common/ — see .docs/decisions/10-species-class-keys-unprefixed.md.")
    if len(dangling) > 12:
        errors.append(f"... and {len(dangling) - 12} more dangling identifier(s)")
    return n


def check_dangling_shaders() -> int:
    """Shader effects a mesh or entity names that no .shader file declares.

    399 errors in the 2026-08-01 log — `Failed to create material with shader
    PdxMeshShipTransp` and four siblings. STNH's ship meshes bake in five effect
    names from its own gfx/FX/pdxmesh.shader, and vendor.yml's include list does
    not take gfx/FX. The materials affected are hull stripes, nacelle stripes,
    faction emblems and saucer decals — visible Trek identity on the shipsets,
    not cosmetic.

    Declarations come from the merged tree first and vanilla second — an
    src/gfx/FX/*.shader shadows vanilla's file by path, exactly as the game
    resolves it.
    """
    declared: set[str] = set()
    seen_paths: set[str] = set()
    for root in (BUILD, GAME_DIR):
        fx = root / "gfx" / "FX"
        if not fx.is_dir():
            continue
        for f in fx.rglob("*.shader"):
            key = str(f.relative_to(root))
            if key in seen_paths:
                continue          # our copy already shadowed vanilla's
            seen_paths.add(key)
            declared |= set(re.findall(r"^\s*Effect\s+([A-Za-z_][\w]*)",
                                       _read(f), re.M))
    if not declared:
        return 0

    ref = re.compile(r'\bshader\s*=\s*"([A-Za-z_][\w]*)"')

    # Engine built-ins. Not every shader name resolves to an `Effect` block --
    # "Collision" is used by vanilla's own _add_ons_meshes.gfx and declared in no
    # .shader file at all. Rather than guess at the engine's internal list, take
    # whatever VANILLA references but does not declare: by definition those work.
    builtin: set[str] = set()
    for suffix in ("*.gfx", "*.asset"):
        for f in (GAME_DIR / "gfx").rglob(suffix):
            builtin |= {m.group(1) for m in ref.finditer(_strip_comments(_read(f)))}
    builtin -= declared

    ack = _ack_list("dangling_shader_ack")
    missing: dict[str, tuple[int, str]] = {}
    n = 0
    for suffix in ("*.gfx", "*.asset"):
        for f in (BUILD / "gfx").rglob(suffix):
            n += 1
            rp = str(f.relative_to(BUILD))
            for m in ref.finditer(_strip_comments(_read(f))):
                name = m.group(1)
                if name in declared or name in builtin or name in ack:
                    continue
                count, where = missing.get(name, (0, rp))
                missing[name] = (count + 1, where)

    for name, (count, where) in sorted(missing.items(), key=lambda kv: -kv[1][0])[:10]:
        errors.append(
            f"{where}: shader effect '{name}' is used by {count} mesh/entity "
            f"declaration(s) but no gfx/FX/*.shader declares it. The material "
            f"fails to build and the mesh renders untextured. Add the effect "
            f"block to an src/gfx/FX/ override rather than vendoring a whole "
            f"3.x-era .shader over vanilla's.")
    if len(missing) > 10:
        errors.append(f"... and {len(missing) - 10} more undeclared shader effect(s)")
    return n


def check_dangling_art_references() -> int:
    """Meshes, particles and entities a vendored file names that nothing declares.

    `check_dangling_shaders` already asks this question of one reference kind.
    184 records in the 2026-08-02 run were the same question asked of three
    more, and nothing was asking: STNH's `include:` took gfx/models/ships, whose
    files reference particles in gfx/particles and meshes at the top of
    gfx/models — neither of which was included. The art we took was calling for
    art we had declined to vendor, and the only place that showed up was the
    game's log.

    It is also how ASB's copy of gfx/particles/_ships_particles.gfx was caught
    dropping four vanilla 4.4 particles: the reference side does not care WHY a
    name fails to resolve.

    Declarations come from the merged tree and vanilla together, because the
    game loads both. `entity` references are read from `attach = { x = "y" }`
    and from section templates, which is where the vanilla ones live.
    """
    art = BUILD / "gfx"
    if not art.is_dir():
        return 0

    declared: set[str] = set()
    ours: set[str] = set()
    for suffix in ("*.gfx", "*.asset"):
        for f in art.rglob(suffix):
            ours.add(str(f.relative_to(BUILD)))
            declared |= _declared_names(_read(f))
    van_art = GAME_DIR / "gfx"
    if van_art.is_dir():
        for suffix in ("*.gfx", "*.asset"):
            for f in van_art.rglob(suffix):
                if str(f.relative_to(GAME_DIR)) in ours:
                    continue                  # our copy shadows vanilla's
                declared |= _declared_names(_read(f))

    if not declared:
        return 0

    # `particle = "x"` / `pdxmesh = "x"` / `attach = { root = "x" }`. Textures
    # are deliberately NOT checked here: they resolve by filename against a
    # directory the game searches, not against a declared name, so the question
    # is "does the file exist" and belongs with the vendoring rules.
    ref = re.compile(r'\b(particle|pdxmesh)\s*=\s*"([^"]+)"')

    ack = _ack_list("dangling_art_ack")
    missing: dict[str, tuple[str, int, str]] = {}
    n = 0
    for suffix in ("*.gfx", "*.asset"):
        for f in art.rglob(suffix):
            n += 1
            rp = str(f.relative_to(BUILD))
            for m in ref.finditer(_strip_comments(_read(f))):
                kind, name = m.group(1), m.group(2)
                if name in declared or name in ack:
                    continue
                k = "particle" if kind == "particle" else "mesh"
                _, count, where = missing.get(name, (k, 0, rp))
                missing[name] = (k, count + 1, where)

    for name, (kind, count, where) in sorted(missing.items(),
                                             key=lambda kv: -kv[1][1])[:10]:
        errors.append(
            f"{where}: {kind} '{name}' is referenced {count} time(s) by vendored "
            f"art but declared by no .asset/.gfx in the tree or in vanilla. The "
            f"effect or model does not draw at all. Either the source that "
            f"declares it is not in the harvest, or an include: list took the "
            f"file that USES it without the file that DECLARES it -- check "
            f".source/ before assuming the reference is dead.")
    if len(missing) > 10:
        errors.append(f"... and {len(missing) - 10} more dangling art reference(s)")
    return n


def check_gfx_file_refs() -> int:
    """`file = "…"` in vendored art must point at a file that is actually there.

    The other art checks ask whether a *name* resolves. This asks whether the
    *file behind the declaration* was vendored, which is a different question
    and the one an `include:` list gets wrong. `check_dangling_art_references`
    says so in its own docstring -- "the question is 'does the file exist' and
    belongs with the vendoring rules" -- and nothing implemented it.

    Decision 18 pruned STNH's ship tree from 104 directories to 13, driving the
    include list to closure against the *name* check. It converged: every mesh
    name still resolved, because the .gfx that DECLARES them
    (gfx/models/ships/federation/federation_all_ships.gfx) was kept. Its
    `file =` paths point into federation_01…04/ and borg_01/, which were not.
    The engine falls back to gfx/models/test_object.mesh, which has no
    animation, so every entity built on one loses its animated states.

    Cost: 15 `pdxmeshtype.cpp:139` + 1,453 `pdx_entity.cpp:266` + 167
    `pdxassetutil.cpp:146` + 26 `texturehandler.cpp:66` in one live run,
    against `make validate` reporting ok.

    Only PATH-form references are checked -- ones containing a `/`, which are
    resolved from the mod root and are the form every `pdxmeshtype.cpp:139`
    record in the log names. A bare filename (`foo_idle.anim`, `bar_diffuse.dds`)
    resolves against the declaring file's own directory and against the
    engine's texture search path, so "is it at this path from the root" is the
    wrong question for it -- 330 of them are false positives, and
    `check_dangling_art_references` says so in its own docstring.

    Vanilla counts as present: STNH routinely points at vanilla .mesh files.
    """
    art = BUILD / "gfx"
    if not art.is_dir():
        return 0

    have: set[str] = set()
    for base in (BUILD, GAME_DIR):
        if not base.is_dir():
            continue
        for ext in ("*.mesh", "*.anim", "*.dds"):
            for f in base.rglob(ext):
                have.add(str(f.relative_to(base)).replace("\\", "/"))

    ref = re.compile(r'\bfile\s*=\s*"([^"]+\.(?:mesh|anim|dds))"')
    ack = _ack_list("gfx_file_ref_ack")
    missing: dict[str, tuple[int, str]] = {}
    n = 0
    for suffix in ("*.gfx", "*.asset"):
        for f in art.rglob(suffix):
            n += 1
            rp = str(f.relative_to(BUILD))
            for m in ref.finditer(_strip_comments(_read(f))):
                target = m.group(1).lstrip("/").replace("\\", "/")
                if "/" not in target:
                    continue                  # resolves relative, not from root
                if target in have or target in ack:
                    continue
                count, where = missing.get(target, (0, rp))
                missing[target] = (count + 1, where)

    for target, (count, where) in sorted(missing.items(),
                                         key=lambda kv: -kv[1][0])[:12]:
        errors.append(
            f"{where}: declares art from '{target}', which is in neither the "
            f"built tree nor vanilla ({count} declaration(s)). The engine "
            f"substitutes gfx/models/test_object.mesh, so every entity using "
            f"it loses its mesh and its animated states. Check .source/ -- if "
            f"the file is there, an include: list took the .gfx that DECLARES "
            f"it without the directory that HOLDS it.")
    if len(missing) > 12:
        errors.append(f"... and {len(missing) - 12} more missing art file(s)")
    return n


def check_texture_basenames() -> int:
    """A `meshsettings` texture is a BARE filename, and it still has to exist.

    The sibling check above deliberately skips bare filenames, on the grounds
    that resolving them from the mod root produces 330 false positives. True,
    and it left the whole class unchecked: `texture_diffuse = "foo.dds"` was
    never asked about at all, in any form. The 2026-08-03 run answered with 139
    `pdxassetutil.cpp` "Failed to find texture" records -- and NOT ONE of the
    139 was anywhere in the built tree, while 132 sat in .source/ in ship
    directories decision 18's prune had removed. `make validate` was clean.

    Resolving from the root is the wrong question; resolving by BASENAME
    against everything loaded is the right one, and the engine says so itself:
    `Duplicate texture 'Hull_Main_1_TMP.dds' found (current path
    gfx/models/ships/stnc_shipset_shared/textures/…, previous path
    gfx/models/ships/federation/constitution_refit/…)` is the engine comparing
    two different directories under one basename. So it keeps a global index,
    and "is this basename in it" is answerable here with no false positives --
    where the root-relative form had 330.

    Vanilla counts as present: `nonormal.dds` and `nospec.dds` are vanilla's and
    STNH names them constantly.

    Matching is on the STEM, not the filename, because the engine resolves the
    extension itself and vanilla relies on it: vanilla's own
    gfx/models/ships/other/_other_meshes.gfx asks for `event_ship_07_diffuse.tga`
    and `ancient_destroyer_normal.tga` while vanilla ships only the `.dds`. That
    is all five of vanilla's `.tga` references, so an extension-sensitive check
    would report vanilla itself -- derive the rule from what vanilla does
    (.docs/validation/check-design.md rule 4) rather than acking the five by hand.
    """
    art = BUILD / "gfx"
    if not art.is_dir():
        return 0

    have: set[str] = set()
    for base in (BUILD, GAME_DIR):
        if not base.is_dir():
            continue
        for ext in ("*.dds", "*.tga", "*.png"):
            have.update(f.stem.lower() for f in base.rglob(ext))

    ref = re.compile(r'\btexture_\w+\s*=\s*"([^"]+)"')
    ack = _ack_list("texture_basename_ack")
    missing: dict[str, tuple[int, str]] = {}
    n = 0
    for suffix in ("*.gfx", "*.asset"):
        for f in art.rglob(suffix):
            n += 1
            rp = str(f.relative_to(BUILD))
            for m in ref.finditer(_strip_comments(_read(f))):
                target = m.group(1)
                # A path-form reference is the sibling check's business.
                # A BACKSLASH one is nobody's yet: it is a Windows separator
                # that a Linux build cannot open, and it is reported here rather
                # than normalised away, so it fails instead of silently passing.
                # No .gfx or .asset in the tree currently has one -- the single
                # `planets\nospec.dds` in the 2026-08-03 log is baked into a
                # .mesh binary, which no text check can reach.
                if "/" in target:
                    continue
                if target in ack:
                    continue
                if "\\" not in target and target.rsplit(".", 1)[0].lower() in have:
                    continue
                count, where = missing.get(target, (0, rp))
                missing[target] = (count + 1, where)

    for target, (count, where) in sorted(missing.items(),
                                         key=lambda kv: -kv[1][0])[:12]:
        errors.append(
            f"{where}: names texture '{target}', which is in neither the built "
            f"tree nor vanilla under that filename ({count} reference(s)). The "
            f"mesh draws untextured. Check .source/ -- if the file is there, an "
            f"include: list took the .gfx that NAMES it without the directory "
            f"that HOLDS it; textures live apart from the meshes that use them, "
            f"so a directory-scoped include does not follow the edge.")
    if len(missing) > 12:
        errors.append(f"... and {len(missing) - 12} more missing texture(s)")
    return n


# Define arrays that plausibly describe the same zoom steps from two sides, and
# which vanilla always keeps equal (7 and 7).
#
# THIS IS A COHERENCE HEURISTIC, NOT AN ENGINE REQUIREMENT, and it used to claim
# to be one. The only evidence that the engine coupled these two was the D13
# error of the 2026-08-01 run — and decision 43 showed that error is about
# NCamera.ZOOM_STEPS_SYSTEM, a different array that no script can set and that
# is fixed at 7. With D13 explained, nothing is left that says these two must
# match: Cinematic Camera shipped 13 against System Scale's 8 planet scales and
# the engine's only complaint was the ZOOM_STEPS_SYSTEM one, which is present
# with and without that mod.
#
# So it warns rather than errors, and it says which of the two it is. A rule
# that survives only because nobody re-tested it after its evidence was
# reattributed is exactly what decision 43 is about.
COUPLED_DEFINE_ARRAYS = [
    ("NCamera.ZOOM_STEPS_SYSTEM_PERCENTAGES", "NGraphics.PLANET_SCALE_SYSTEM"),
]

# Arrays the engine couples to an internal array that NO script file can set,
# so the only length that satisfies it is the one vanilla ships. The required
# length is read off vanilla rather than written here, so a game patch that
# re-tunes the camera moves it with them.
#
# `NCamera.ZOOM_STEPS_SYSTEM` is set by no file in vanilla and by none of the 51
# snapshotted workshop mods -- only `..._PERCENTAGES` is scriptable. Which of
# the two the engine actually measures against was settled by refuting the
# alternatives across two live runs, not by reading the binary:
#
#   run        ZOOM%  PLANET_SCALE  ZOOM_GALAXY   engine complained
#   vanilla        7             7            7   no
#   2026-08-01    13             8            8   YES  (Cinematic Camera present)
#   2026-08-07     8             8            6   YES  (Cinematic Camera dropped)
#
#   len == len(ZOOM%)        predicts 2026-08-07 CLEAN   -- refuted
#   len == len(ZOOM_GALAXY)  predicts 2026-08-01 CLEAN   -- refuted
#   len == vanilla's 7       predicts all three          -- the only survivor
#
# So the pairwise COUPLED_DEFINE_ARRAYS rule above is necessary but NOT
# sufficient: it passed 8-against-8 while the engine went on reporting the same
# error, which is the decision-30 trap -- a check calibrated on the near side of
# a repair and never re-run against the far side.
# See .docs/decisions/43-planet-scale-system-length.md.
ENGINE_FIXED_LENGTH_ARRAYS = [
    ("NGraphics.PLANET_SCALE_SYSTEM", "NCamera.ZOOM_STEPS_SYSTEM"),
]



# Every locator the engine can be told to mount a component on. Read out of
# vanilla's section templates rather than listed here -- see _required_locators.
# `is_species_class` takes its value BARE OR QUOTED, and both are live
# references: STNH writes `= "HOLO"` twice and the engine reports the failed
# lookup for both spellings. Three checks read this field with a bare-only
# `(\w+)`, and all three were blind to HOLO -- 2 errors in the 2026-08-07 run,
# the one key of 34 that no ack covered, reported by nothing.
#
# NOT the same as `class = "star"`, where quoting stops a keyword being a keyword
# and the body is silently dropped (decision 27). There, the written form changes
# the meaning and normalising it away deletes the defect; here the form is
# cosmetic and refusing to read one of the two deletes the reference. Ask which
# of those a field is before writing the regex.
_SPECIES_CLASS_REF = re.compile(r'is_species_class\s*=\s*"?([A-Za-z_]\w*)"?')

_LOCATOR_RE = re.compile(r'locator\s*=\s*\{\s*name\s*=\s*"([^"]+)"')
# A locator body carries nested { } for position/rotation, so one level of
# nesting has to be allowed for; a [^{}]* body silently drops every locator that
# has a position, which is exactly the ones this needs to see.
_LOCATOR_BODY_RE = re.compile(
    r'locator\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}')
_LOC_NAME_RE = re.compile(r'\bname\s*=\s*"?([\w.]+)"?')
_LOC_POS_RE = re.compile(
    r'\bposition\s*=\s*\{\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s*\}')


def _placed_locators(body: str) -> dict[str, bool]:
    """Locator name -> whether it carries a position away from the origin.

    A locator declared with no position, or at { 0 0 0 }, puts the gun at the
    model origin — the middle of the ship. See decision 28.
    """
    out: dict[str, bool] = {}
    for m in _LOCATOR_BODY_RE.finditer(body):
        nm = _LOC_NAME_RE.search(m.group(1))
        if not nm:
            continue
        pos = _LOC_POS_RE.search(m.group(1))
        out[nm.group(1)] = bool(
            pos and max(abs(float(v)) for v in pos.groups()) > 1e-6)
    return out
_PDXMESH_RE = re.compile(r'\bpdxmesh\s*=\s*"([^"]+)"')
_CLONE_RE = re.compile(r'\bclone\s*=\s*"([^"]+)"')
_MESHFILE_RE = re.compile(r'\bfile\s*=\s*"([^"]+\.mesh)"')


def _asset_walk(root: Path):
    """`gfx/models/ships/` in the order the engine reads it.

    One alphabetical sequence with files and directories INTERLEAVED. That is
    not a guess: the 2026-08-11 run's own messages name the file and line of
    every failed clone, and four independent slices of them agree on it.
    """
    ships = root / "gfx/models/ships"
    if not ships.is_dir():
        return
    def rec(d: Path):
        for e in sorted(d.iterdir(), key=lambda q: q.name):
            if e.is_dir():
                yield from rec(e)
            elif e.suffix.lower() in (".asset", ".gfx"):
                yield e
    yield from rec(ships)


def _balanced(text: str, start: int) -> str:
    """The `{ … }` beginning at `start`, braces included."""
    depth, j = 0, start
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[start:j + 1]
        j += 1
    return text[start:]


def _entity_blocks(text: str):
    """(name, body) for every `entity = { … }`, comments stripped."""
    text = _strip_comments(text)
    i = 0
    while True:
        m = re.search(r"\bentity\s*=\s*\{", text[i:])
        if not m:
            return
        s = i + m.end() - 1
        depth, j = 0, s
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = text[s + 1:j]
        nm = re.search(r'\bname\s*=\s*"([^"]+)"', body)
        if nm:
            yield nm.group(1), body
        i = j + 1


def _required_locators() -> dict[str, set[str]]:
    """Section entity -> the locators its vanilla section templates mount on."""
    out: dict[str, set[str]] = {}
    src = GAME_DIR / "common/section_templates"
    if not src.is_dir():
        return out
    for f in sorted(src.glob("*.txt")):
        cur = None
        for line in _strip_comments(_read(f)).splitlines():
            m = re.search(r'^\s*entity\s*=\s*"?([A-Za-z0-9_]+)"?', line)
            if m:
                cur = m.group(1)
            m2 = re.search(r'locatorname\s*=\s*"?([A-Za-z0-9_]+)"?', line)
            if m2 and cur:
                out.setdefault(cur, set()).add(m2.group(1))
    return out


def check_asset_load_order() -> int:
    """Two things the asset loader decides while reading, not afterwards.

    Every cross-file reference STG had dealt with before the shipsets --
    scripted triggers, species classes, shader effects, mesh names -- resolves
    after the whole tree is read, and every other check here is built on that.
    `clone` is not: it resolves against entities ALREADY LOADED. A clone whose
    parent sorts later in the walk is a ship that does not render, and
    "declared somewhere" cannot see it.

    That cost a live run. The Vulcan and Tholian shipsets were invisible in game
    because `stg_vulcan_01_….asset` sorted before `vulcan_01_sovereign_frame.asset`
    inside their own directory, while eleven other cultures worked by luck of the
    alphabet -- 537 records, and `make validate` was clean throughout.

    The second half is the same idea for `section.cpp:311`: a section entity has
    to carry the locators its templates name, and a cloned entity inherits them
    from its parent's mesh. 228 records in the same run.

    That half resolves locators across the WHOLE merged tree -- following the
    clone chain into vendored and vanilla art -- but only reports on entities
    STG itself declares. Vanilla ships section entities of its own that fail the
    same test and never appear in error.log, so judging them would be 191
    findings nobody can act on; decision 12's rule is that a source's errors are
    ours to fix, but vanilla's own art is not ours to second-guess.

    CALIBRATION against the 2026-08-03 run, which is the only way to know this
    half works at all -- it previously reported ok against 506 engine records:

        engine `section.cpp:311`                             506
        this check, before gen_shipsets.py placed the mounts 676
        engine found, check missed                             0

    AND THEN IT WENT BACK TO REPORTING 0 WITHOUT FIXING ANYTHING. The repair put
    the mounts in `locator` blocks beside the `clone` they already had; this
    check counted them and fell to 0, and the 2026-08-07 run threw 1,383 records
    -- the same 506, plus 877 from `ship_design_templates.cpp:405` -- because the
    engine drops a locator declared beside a `clone`. All 173 entities it named
    were clone-plus-locator blocks, and every mount it called missing was one
    declared right there. Hence the hard error where `ents` is built, and hence
    `locs` being empty for a cloning entity: a check whose subject was 252 dead
    declarations could not fail, and reported a number anyway.

    It reports a SUPERSET on purpose, and the excess is not noise. The engine
    validates a section entity when something USES it, so one session's log is a
    sample: 36 of the excess are `juggernaut_core_section`, which cannot appear
    at load at all, and others are starbase sections built in game. A longer
    session moves records from this check's excess into the log, not the other
    way round. Never treat the log's total as this check's target.

    It asks about PLACEMENT, not existence. An .asset declaration does satisfy
    the engine -- 0 of 2,780 such mounts were reported in that run -- but a
    declaration with no position leaves the gun at the model origin, which no
    log will ever mention. Decision 28.
    """
    if not (BUILD / "gfx/models/ships").is_dir():
        return 0

    ack = _ack_list("asset_load_order_ack")
    ents: dict[str, dict] = {}
    ours: set[str] = set()
    meshfile: dict[str, Path] = {}
    n = 0

    # Vanilla loads first, then the mod -- the same order the game uses.
    for root in (GAME_DIR, BUILD):
        for f in _asset_walk(root):
            n += 1
            text = _read(f)
            if f.suffix.lower() == ".gfx":
                cur = None
                for line in _strip_comments(text).splitlines():
                    m = re.search(r'\bname\s*=\s*"([^"]+)"', line)
                    if m:
                        cur = m.group(1)
                    m2 = _MESHFILE_RE.search(line)
                    if m2 and cur:
                        meshfile.setdefault(cur, root / m2.group(1))
            for name, body in _entity_blocks(text):
                parent = _CLONE_RE.search(body)
                if parent and parent.group(1) not in ents and name not in ack:
                    errors.append(
                        f"{f.relative_to(root)}: entity '{name}' clones "
                        f"'{parent.group(1)}', which the engine has not loaded yet. "
                        f"`clone` resolves in load order — gfx/models/ships/ is one "
                        f"alphabetical walk with files and directories interleaved — "
                        f"so the parent must sort earlier. The ship will not render.")
                if root is BUILD and (REPO / "src" / f.relative_to(BUILD)).is_file():
                    ours.add(name)
                mesh = _PDXMESH_RE.search(body)
                locs = _placed_locators(body)
                # `clone` is a whole-entity copy applied after the block is read,
                # so ANY locator written beside it is discarded — the entity gets
                # exactly the donor's mounts and none of the ones declared here.
                # Crediting them made this check structurally unable to fail: it
                # reported 0 while the 2026-08-03 run threw 1,383 records (877
                # ship_design_templates.cpp:405 + 506 section.cpp:311) naming
                # mounts declared right beside a `clone`. Vanilla never writes
                # the two together — 0 of 8,429 entity declarations, against 210
                # that clone and 2,160 that declare locators.
                if parent and locs and name not in ack:
                    errors.append(
                        f"{f.relative_to(root)}: entity '{name}' declares "
                        f"{len(locs)} locator(s) beside `clone = "
                        f"\"{parent.group(1)}\"`. The engine applies `clone` as a "
                        f"whole-entity copy and drops them, so those mount points "
                        f"do not exist — the section's guns are reported missing "
                        f"and the ship mounts nothing there. Copy the donor's "
                        f"declaration out instead of cloning it "
                        f"(tools/gen_shipsets.py Emitter.expand), or ack it in "
                        f"vendor.yml under asset_load_order_ack.")
                ents[name] = {
                    "mesh": mesh.group(1) if mesh else None,
                    "clone": parent.group(1) if parent else None,
                    "locs": {} if parent else locs,
                }

    blobs: dict[Path, bytes] = {}

    def in_mesh(mesh: str | None, want: set[str]) -> set[str]:
        p = meshfile.get(mesh or "")
        if p is None or not p.is_file():
            return set()
        if p not in blobs:
            blobs[p] = p.read_bytes()
        blob = blobs[p]
        found = set()
        for c in want:
            b = c.encode()
            i = blob.find(b)
            while i != -1:
                pre, post = blob[i - 1:i], blob[i + len(b):i + len(b) + 1]
                if (not pre or not (pre.isalnum() or pre == b"_")) and \
                   (not post or not (post.isalnum() or post == b"_")):
                    found.add(c)
                    break
                i = blob.find(b, i + 1)
        return found

    def effective(name: str, want: set[str], seen: set[str] | None = None) -> set[str]:
        """Component mount points an entity has A REAL POSITION for, through the
        clone chain: baked into the mesh, or declared in the .asset with a
        position away from the origin.

        BOTH SOURCES COUNT, and that was measured against the 2026-08-03 run.
        Of 2,780 mounts declared in an .asset but absent from the mesh, the
        engine reported exactly 0, while all 506 `section.cpp:311` records named
        a mount declared in neither place. A declaration satisfies the engine.

        What it does NOT do on its own is place the gun. A locator with no
        position, or one at { 0 0 0 }, leaves the gun at the model origin — the
        middle of the ship — which is the defect the 2026-08-03 run showed and
        the reason this counts placement rather than mere existence.

        A locator declared beside a `clone` counts for nothing at all: it is
        dropped before the engine ever sees it, and `locs` is empty for those
        entities. That is enforced where `ents` is built, not here.
        See .docs/decisions/28-weapon-locator-positions.md.
        """
        seen = seen or set()
        if name in seen or name not in ents:
            return set()
        seen.add(name)
        e = ents[name]
        out = in_mesh(e["mesh"], want)
        out |= {ln for ln, placed in e["locs"].items() if placed and ln in want}
        if e["clone"]:
            out |= effective(e["clone"], want, seen)
        return out

    # Only entities a graphical culture can actually reach are checked. The
    # engine looks a section entity up as `<culture>_<name>`, so an STNH entity
    # that merely ends with the same suffix -- deep_space_03's starbase sections
    # -- belongs to no culture and is never asked for. Scoping this by hand
    # would drift; the culture list is read out of the merged tree.
    cultures = {""}
    for d in (BUILD / "common/graphical_culture", GAME_DIR / "common/graphical_culture"):
        if d.is_dir():
            for f in d.glob("*.txt"):
                cultures |= {k + "_" for k in _top_level_keys(_read(f))}

    required = _required_locators()
    unmounted: dict[str, list[str]] = {}
    for section, want in required.items():
        want = want - {"root"}
        if not want:
            continue
        for prefix in cultures:
            name = prefix + section
            if name not in ours or name in ack:
                continue
            for miss in sorted(want - effective(name, want)):
                unmounted.setdefault(prefix.rstrip("_") or "(no culture)",
                                     []).append(f"{name}.{miss}")

    # Reported as a tracked COUNT, not as errors. Each one is a gun that fires
    # from the middle of its ship: the mount is neither baked into the mesh nor
    # declared with a position anywhere up the clone chain.
    #
    # THE NUMBER IS THE SIGNAL, and the baseline is now 0. gen_shipsets.py places
    # every mount it generates from the donor hull's bounding box (decision 28),
    # so anything reported here is either art whose geometry could not be read or
    # a section the generator does not cover. Both are findings.
    if unmounted:
        total = sum(len(v) for v in unmounted.values())
        per = ", ".join(f"{c} {len(v)}" for c, v in sorted(unmounted.items()))
        warnings.append(
            f"gfx/models/ships: {total} weapon mount point(s) have no position "
            f"anywhere — not baked into the section entity's mesh, not declared "
            f"with one in its .asset ({per}). The gun fires from the model "
            f"origin, i.e. the middle of the ship. gen_shipsets.py places the "
            f"mounts it generates from hull geometry, so the baseline is 0; see "
            f".docs/decisions/28-weapon-locator-positions.md. Fix by giving the "
            f"locator a real position, or ack it in vendor.yml under "
            f"asset_load_order_ack once looked at.")
    return n


# The ship-size family this check is calibrated over — see its docstring. Not
# a convenience filter: at wider scope vanilla's own art fails 41 times.
_STATION_SIZE = re.compile(r"^(military_station_\w+|ion_cannon)$")


def check_section_attach_points() -> int:
    """Hull entities missing the attach points their ship size's slots name.

    A DIFFERENT QUESTION FROM check_asset_load_order, and the two are easy to
    confuse because both end in the word "locator". That one reads
    `common/section_templates/` and asks whether a SECTION entity carries the
    gun mounts its template fires from. This one reads `common/ship_sizes/`
    and asks whether the HULL entity carries the `part1`..`partN` attach points
    the size's `section_slots` hang sections on. Different database, different
    entity, different failure: a missing gun mount fires from the model origin,
    a missing attach point means the section never attaches at all.

    `pdxmesh = "X_mesh"` is a DECLARATION NAME, not a filename. Vanilla bakes
    these attach points into the mesh rather than declaring them, so resolving
    the name through the `.gfx` that maps it to a `.mesh` is the whole check --
    a first cut that globbed for `<name>.mesh` found nothing anywhere and
    reported 1,279 findings, most of them vanilla's.

    TWO SCOPES ON PURPOSE, and the second one is gated differently from the
    first. Over the STATION family -- military_station_* and ion_cannon --
    vanilla contributes exactly 1 finding in ~350 entities (synth_queen_01,
    missing part2) against 66 from the vendored shipsets, so that half reports
    on any vendored art. The 66 are all 22 Walshicus shipsets x 3 station
    entities, and the 2026-08-07 log named 2 of them -- one culture's small
    station, the only one a three-minute run drew.

    THE HULL SCOPE WAS OPENED 2026-08-22, and the ratio that closed it is
    stale. This docstring used to record 41 vanilla against 147 mod findings
    over all 317 sizes, "not a signal anyone can act on". Re-measured against
    the build of 2026-08-11, that whole population is 12: 7 vanilla-only and 5
    in vendored files. Decision 82's 230 attach points collapsed the mod side.

    BUT WIDENING ON THAT NUMBER ALONE WOULD HAVE SHIPPED FALSE POSITIVES, and
    what they are is the reason for the gate:

      - `ancient_destroyer_entity [part2]` is vanilla's own body, declaring
        root and part1 and nothing else, carried through unchanged by a shadow.
        `vanilla_only` cannot see it -- that set holds entities vanilla alone
        declares, not entities we shadow without editing.
      - the other four fly THEIR OWN culture's art, and 28 of vanilla's 33
        `*_constructor_entity` declare no part1 in the .asset either. The point
        comes from the animated rig, which is not readable from the container
        (decision 82 records the same caveat for vanilla's titan and colossus
        frames, which name no part locators and work).

    So the hull half is gated on the frame being BORROWED -- `pdxmesh` not
    prefixed by the entity's own culture -- which is exactly how
    tools/fix_ship_locators.py `hull_entities()` scopes the repair. The check
    now guards the population that tool writes, and nothing else. `part1` is
    dropped from the wanted set for the same reason it is there: every borrowed
    frame in this tree is a corvette's, and a corvette always has one.

    Baseline is 0 on both halves. Reverting the vendor.yml patches restores all
    66 stations; stripping fix_ship_locators' output restores 132 hulls.
    See .docs/decisions/35-station-section-attach-points.md and
    .docs/decisions/82-hull-section-attach-points.md.
    """
    if not (BUILD / "gfx/models/ships").is_dir():
        return 0

    # ship size -> the attach points its section slots name.
    required: dict[str, set[str]] = {}
    hull_required: dict[str, set[str]] = {}
    seen_sz: set[str] = set()
    for root in (BUILD, GAME_DIR):
        d = root / "common/ship_sizes"
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.txt")):
            if f.name in seen_sz:
                continue            # BUILD's copy shadows vanilla's by path
            seen_sz.add(f.name)
            text = _strip_comments(_read(f))
            for m in re.finditer(r"^(\w+)\s*=\s*\{", text, re.M):
                body = _balanced(text, text.index("{", m.start()))
                sm = re.search(r"section_slots\s*=\s*\{", body)
                if not sm:
                    continue
                slots = _balanced(body, sm.end() - 1)
                names = set(re.findall(r'locator\s*=\s*"?(\w+)"?', slots))
                size = m.group(1)
                if _STATION_SIZE.match(size):
                    if names - {"root"}:
                        required[size] = names - {"root"}
                # The hull scope. `part1` is dropped, not overlooked: every
                # borrowed frame here is a corvette's, and a corvette's whole
                # job is to have a part1. See the docstring.
                elif names - {"root", "part1"}:
                    hull_required[size] = names - {"root", "part1"}
    if not (required or hull_required):
        return 0

    ents: dict[str, dict] = {}
    meshfile: dict[str, Path] = {}
    vanilla_only: set[str] = set()
    n = 0
    for root in (GAME_DIR, BUILD):
        for f in _asset_walk(root):
            n += 1
            text = _read(f)
            if f.suffix.lower() == ".gfx":
                cur = None
                for line in _strip_comments(text).splitlines():
                    m = re.search(r'\bname\s*=\s*"([^"]+)"', line)
                    if m:
                        cur = m.group(1)
                    m2 = _MESHFILE_RE.search(line)
                    if m2 and cur:
                        meshfile.setdefault(cur, root / m2.group(1))
                continue
            for name, body in _entity_blocks(text):
                parent = _CLONE_RE.search(body)
                mesh = _PDXMESH_RE.search(body)
                if root is GAME_DIR:
                    vanilla_only.add(name)
                else:
                    vanilla_only.discard(name)
                ents[name] = {
                    "mesh": mesh.group(1) if mesh else None,
                    "clone": parent.group(1) if parent else None,
                    # Decision 30: a locator beside a `clone` is discarded.
                    "locs": set() if parent else set(_placed_locators(body)),
                    "file": f.relative_to(root),
                }

    blobs: dict[Path, bytes] = {}

    def in_mesh(mesh: str | None, want: set[str]) -> set[str]:
        p = meshfile.get(mesh or "")
        if p is None or not p.is_file():
            return set()
        if p not in blobs:
            blobs[p] = p.read_bytes()
        blob, found = blobs[p], set()
        for c in want:
            b = c.encode()
            i = blob.find(b)
            while i != -1:
                pre, post = blob[i - 1:i], blob[i + len(b):i + len(b) + 1]
                if (not pre or not (pre.isalnum() or pre == b"_")) and \
                   (not post or not (post.isalnum() or post == b"_")):
                    found.add(c)
                    break
                i = blob.find(b, i + 1)
        return found

    def effective(name: str, want: set[str], seen: set[str] | None = None) -> set[str]:
        seen = seen or set()
        if name in seen or name not in ents:
            return set()
        seen.add(name)
        e = ents[name]
        out = in_mesh(e["mesh"], want) | (e["locs"] & want)
        if e["clone"]:
            out |= effective(e["clone"], want, seen)
        return out

    cultures = {""}
    for d in (BUILD / "common/graphical_culture", GAME_DIR / "common/graphical_culture"):
        if d.is_dir():
            for f in d.glob("*.txt"):
                cultures |= {k + "_" for k in _top_level_keys(_read(f))}

    ack = _ack_list("section_attach_point_ack")
    bad: dict[str, list[str]] = {}
    for size, want in required.items():
        for prefix in cultures:
            name = f"{prefix}{size}_entity"
            if name not in ents or name in ack or name in vanilla_only:
                continue
            miss = sorted(want - effective(name, want))
            if miss:
                bad.setdefault(str(ents[name]["file"]), []).append(
                    f"{name} [{' '.join(miss)}]")

    # The hull scope, gated on the frame being BORROWED -- the discriminator
    # decision 82's own fix tool is scoped by, reused here so the check guards
    # exactly the population that tool repairs.
    for size, want in hull_required.items():
        for prefix in cultures:
            name = f"{prefix}{size}_entity"
            if name not in ents or name in ack or name in vanilla_only:
                continue
            mesh = ents[name]["mesh"]
            if not mesh or mesh.startswith(prefix):
                continue            # its own culture's art: it has its own rig
            miss = sorted(want - effective(name, want))
            if miss:
                bad.setdefault(str(ents[name]["file"]), []).append(
                    f"{name} [{' '.join(miss)}]")
    if bad:
        total = sum(len(v) for v in bad.values())
        head = "; ".join(f"{k}: {', '.join(v)}" for k, v in sorted(bad.items())[:3])
        warnings.append(
            f"gfx/models/ships: {total} hull entity/entities are missing attach "
            f"points their ship size's section_slots name — {head}"
            f"{' …' if len(bad) > 3 else ''}. The section has nowhere to attach, "
            f"so its guns are reported missing and nothing mounts there. Vanilla "
            f"bakes these into the mesh; art that does not must declare them (not "
            f"beside a `clone` — decision 30). Fix, or ack in vendor.yml under "
            f"section_attach_point_ack. "
            f"See .docs/decisions/35-station-section-attach-points.md.")
    return n


_ATTACH_RE = re.compile(r'\battach\s*=\s*\{\s*"?\w+"?\s*=\s*"([^"]+)"\s*\}')


def check_attach_targets() -> int:
    """Entities an `attach = { "slot" = "X" }` names that nothing declares.

    A reference edge no other check here follows, and the one an include list
    scoped by directory is most likely to sever -- the same shape as decision 24,
    one file type further down again. `clone` and `pdxmesh` were already covered;
    `attach` hangs one entity off another's locator and had nobody asking.

    VANILLA IS THE CALIBRATION, and it is unusually clean: 5,672 attach
    references across 2,461 distinct targets and **0 unresolved**. Like the
    8,409 entity names it never repeats (decision 33), that makes any unresolved
    attach in our tree a finding rather than a judgement call.

    THE FORM MATTERS AND ALMOST COST THIS CHECK. The syntax is
    `attach = { "part3" = "some_entity" }` -- an assignment whose KEY is the
    locator and whose VALUE is the entity. A first pass looked for
    `attachment = { entity = "…" }`, which is not a thing Stellaris writes, and
    reported 0 unresolved against 18 that exist. Vanilla writes the locator both
    quoted (2,763) and bare (1,000+), so the key's quoting is cosmetic here and
    both are accepted; the value is always quoted.
    See .docs/decisions/37-attach-edges-into-pruned-art.md.
    """
    if not (BUILD / "gfx").is_dir():
        return 0

    declared: set[str] = set()
    seen: set[str] = set()
    for root in (BUILD, GAME_DIR):
        for suffix in ("*.asset", "*.gfx"):
            for f in (root / "gfx").rglob(suffix):
                if any(part in SKIP_DIRS for part in f.parts):
                    continue
                key = str(f.relative_to(root))
                if key in seen:
                    continue
                seen.add(key)
                declared |= _declared_names(_read(f))
    if not declared:
        return 0

    ack = _ack_list("attach_target_ack")
    n = 0
    unresolved: dict[str, set[str]] = {}
    for f in (BUILD / "gfx").rglob("*.asset"):
        if any(part in SKIP_DIRS for part in f.parts):
            continue
        n += 1
        rel = str(f.relative_to(BUILD))
        if rel in ack:
            continue
        for nm in _ATTACH_RE.findall(_strip_comments(_read(f))):
            if nm not in declared and nm not in ack:
                unresolved.setdefault(rel, set()).add(nm)
    if unresolved:
        total = sum(len(v) for v in unresolved.values())
        head = "; ".join(
            f"{k} → {', '.join(sorted(v)[:3])}{' …' if len(v) > 3 else ''}"
            for k, v in sorted(unresolved.items())[:3])
        warnings.append(
            f"gfx/models: {total} attach target(s) in {len(unresolved)} file(s) "
            f"name an entity nothing declares — {head}"
            f"{' …' if len(unresolved) > 3 else ''}. Vanilla leaves 0 of its "
            f"5,672 attach references unresolved, so each of these is art calling "
            f"for art the tree has not got. Either vendor what declares it, or "
            f"ack the referencing file in vendor.yml under attach_target_ack. "
            f"See .docs/decisions/37-attach-edges-into-pruned-art.md.")
    return n


def _parse_defines(text: str) -> dict[str, str]:
    """<group>.<KEY> -> raw value, for one defines file.

    Deliberately shallow: defines are two levels (`NGraphics = { KEY = ... }`)
    and going deeper would start parsing the array bodies themselves.
    """
    out: dict[str, str] = {}
    text = _strip_comments(text)
    for gm in re.finditer(r"([A-Za-z_]\w*)\s*=\s*\{", text):
        group = gm.group(1)
        if not group.startswith("N"):
            continue
        depth, i = 1, gm.end()
        while i < len(text) and depth:
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        body = text[gm.end():i - 1]
        for km in re.finditer(r"([A-Z][A-Z_0-9]*)\s*=\s*(\{[^{}]*\}|[^\s{}]+)", body):
            out[f"{group}.{km.group(1)}"] = km.group(2)
    return out


def check_defines_conflicts() -> int:
    """Two sources setting the same define, and length-mismatched arrays.

    .docs/architecture/conflict-register.md's conflict register enumerates contested PATHS, so two mods that
    ship differently-named files setting the same key are structurally invisible
    to it. That is not hypothetical: Cinematic Camera's zzzzz_cc_defines.txt set
    ZOOM_STEPS_SYSTEM_PERCENTAGES to 13 entries while Real Space – System Scale's
    systemscale_defines.txt set PLANET_SCALE_SYSTEM to 8, and `zzzzz_` sorts
    last, so Cinematic Camera silently broke the in-system planet scaling that
    System Scale exists to provide.

    Files are read in the order the GAME merges them — alphabetical across the
    union, our copy shadowing vanilla's on an identical filename — so "who wins"
    here is who wins in-game, not who wins in the harvest order.

    Last-wins is correct HERE and is not an oversight left behind by decision 29:
    neither common/defines nor unchecked_defines is in FIOS_DIRS, so this
    database resolves LIOS and the last filename in sort order takes the key.
    """
    files: dict[str, Path] = {}
    for d in ("common/defines", "unchecked_defines"):
        van = GAME_DIR / d
        if van.is_dir():
            for f in van.glob("*.txt"):
                files[f"{d}/{f.name}"] = f
        ours = BUILD / d
        if ours.is_dir():
            for f in ours.glob("*.txt"):
                files[f"{d}/{f.name}"] = f       # shadows vanilla by path

    owner: dict[str, str] = {}
    if STATE.is_file():
        try:
            for k, v in json.loads(STATE.read_text()).get("generated", {}).items():
                owner[k] = v.get("source", "?")
        except ValueError:
            pass

    winner: dict[str, tuple[str, str]] = {}      # key -> (value, who set it)
    setters: dict[str, list[tuple[str, str]]] = {}   # key -> [(who, body sha)]
    for relpath in sorted(files):
        path = files[relpath]
        who = owner.get(relpath, "vanilla" if path.is_relative_to(GAME_DIR) else "src/")
        for key, value in _parse_defines(_read(path)).items():
            winner[key] = (value, f"{who} ({Path(relpath).name})")
            if who != "vanilla":
                setters.setdefault(key, []).append(
                    (f"{who} ({Path(relpath).name})", _body_sha(value)))

    ack = _ack_list("defines_conflict_ack")
    same_value = 0
    for key, entries in sorted(setters.items()):
        if len(entries) < 2 or key in ack:
            continue
        # Set twice to the same value is not a conflict: whichever file the
        # engine reads last, the define ends up identical. Same rule as
        # check_key_conflicts' body hashing (decision 29), and it is what an
        # ack entry used to be spent on -- worse than this, because an ack goes
        # on saying nothing after the two values diverge.
        if len({sha for _, sha in entries}) == 1:
            same_value += 1
            continue
        who = [label for label, _ in entries]
        warnings.append(
            f"define {key} is set by {len(who)} sources to DIFFERENT values: "
            f"{', '.join(who)}. Last alphabetically wins in-game. Confirm that "
            f"is the one you want — .docs/architecture/conflict-register.md's path-based register cannot "
            f"see this.")

    def length(value: str) -> int | None:
        return len(value.strip("{} ").split()) if value.strip().startswith("{") else None

    for a, b in COUPLED_DEFINE_ARRAYS:
        # Acking EITHER member retires the pair: the ack is a statement about a
        # reviewed combination of values, and there is no half of one to keep.
        # This is the weaker, group kind of ack (decision 29) -- it will also
        # sit on a future source that sets the acked key to something new, so
        # every entry says what it is about and when to delete it.
        if a in ack or b in ack:
            continue
        va, vb = winner.get(a), winner.get(b)
        if not va or not vb:
            continue
        la, lb = length(va[0]), length(vb[0])
        if la is None or lb is None or la == lb:
            continue
        warnings.append(
            f"define {a} has {la} entries but {b} has {lb}; vanilla keeps them "
            f"equal. {a} comes from {va[1]}, {b} from {vb[1]}. This is a "
            f"coherence heuristic, NOT a known engine requirement — the error "
            f"that used to be cited as proof of one is about "
            f"NCamera.ZOOM_STEPS_SYSTEM and is reported with or without the mod "
            f"that was blamed for it. Worth a look, not worth a revert on its "
            f"own. See .docs/decisions/43-planet-scale-system-length.md.")

    # Vanilla read alone: the length the engine's own un-scriptable array has.
    vanilla_only: dict[str, str] = {}
    for relpath in sorted(files):
        path = files[relpath]
        if path.is_relative_to(GAME_DIR):
            vanilla_only.update(_parse_defines(_read(path)))

    for key, engine_array in ENGINE_FIXED_LENGTH_ARRAYS:
        got, base = winner.get(key), vanilla_only.get(key)
        if not got or base is None or key in ack:
            continue
        have, want = length(got[0]), length(base)
        if have is None or want is None or have == want:
            continue
        warnings.append(
            f"define {key} has {have} entries where vanilla has {want}, and is "
            f"coupled to {engine_array}, which NO script file can set — so "
            f"vanilla's {want} is the only length that satisfies the engine. It "
            f"reports `PLANET_SCALE_SYSTEM does not match in size with "
            f"ZOOM_STEPS_SYSTEM` once per run. Set by {got[1]}. Matching it to "
            f"ZOOM_STEPS_SYSTEM_PERCENTAGES is NOT enough — that was the "
            f"2026-08-02 repair and the engine went on reporting it. Whether "
            f"the scaling then silently falls back, or the engine rebuilds the "
            f"array and the line is cosmetic, CANNOT be settled from the "
            f"container. Do NOT settle it by counting occurrences — that test "
            f"was run on 2026-08-07 across several systems, and BOTH readings "
            f"predict the one line it found — a per-planet check guarded to log "
            f"once looks identical to a cosmetic one. Settle it "
            f"visually instead: do planets change size across zoom steps, at "
            f"System Scale's sizes rather than vanilla's? Then re-cut it to "
            f"{want} entries or ack it under defines_conflict_ack. "
            f"See .docs/decisions/43-planet-scale-system-length.md.")

    return len(files), same_value


def check_key_conflicts() -> int:
    """Top-level keys claimed by two sources, or silently shrunk against vanilla.

    THE GENERALISATION OF check_defines_conflicts, and it exists because the
    specific version was not enough. .docs/architecture/conflict-register.md's register enumerates contested
    PATHS, so two mods shipping differently-named files that define the same key
    are invisible to it. `common/defines/` was the instance that bit us
    (Cinematic Camera vs Real Space – System Scale); it was never the only place
    the shape occurs.

    It is not. `common/random_names/base/` has FOUR files defining `star_names` —
    vanilla's, two of YAGEM's and one of Real Space's — none of which share a
    filename, so nothing in the build had any idea. Found by hand on 2026-08-02
    while answering "what is still open before Phase 2", which is precisely the
    kind of question a check should answer instead.

    Two reports, and the second is the one worth having:

    1. **Contested key.** Defined by more than one source in differently-named
       files. Same-named files are already an overwrite, recorded in
       provenance.md; this is the case nothing else sees.

    2. **Shrunk pool.** A key that is a flat list in both vanilla and our tree,
       defined in a DIFFERENTLY-NAMED file, with fewer entries than vanilla has.
       That is decision 08's flag-colours defect — 47 of vanilla's 72 colours
       lost to a 3.12-era file — expressed at the key level instead of the path
       level, so check_vanilla_regression cannot reach it.

    Report (1) NAMES THE WINNER, and which file that is depends on the directory.
    This said "last alphabetically wins" for every directory until decision 29,
    which is correct for LIOS and precisely backwards for the FIOS ones — of
    which we vendor into common/traits, common/scripted_variables,
    common/solar_system_initializers and common/component_templates. See
    FIOS_DIRS at the top of this file.
    """
    root = BUILD / "common"
    if not root.is_dir():
        return 0

    owner: dict[str, str] = {}
    if STATE.is_file():
        try:
            for k, v in json.loads(STATE.read_text()).get("generated", {}).items():
                owner[k] = v.get("source", "?")
        except ValueError:
            pass

    ack = _ack_list("key_conflict_ack")

    # Sources that override each other ON PURPOSE. A mod family exists so its
    # extensions can redefine the base's keys, which .docs/architecture/conflict-register.md settles as
    # "extension wins"; reporting them is 75 of 88 findings. Declared in
    # vendor.yml rather than inferred from names -- guessing family membership
    # from strings is how you silently stop reporting a real conflict.
    families: list[set[str]] = []
    fam_block = re.search(r"^key_conflict_families:\s*$(.*?)(?=^\S|\Z)",
                          _manifest_text(), re.M | re.S)
    if fam_block:
        current: set[str] = set()
        for line in fam_block.group(1).splitlines():
            if re.match(r"\s+-\s+name:", line):
                if current:
                    families.append(current)
                current = set()
            m = re.match(r"\s+-\s+([^#\n]+?)\s*(?:#.*)?$", line)
            if m and not m.group(1).startswith("name:"):
                current.add(m.group(1).strip("\"'"))
        if current:
            families.append(current)

    def same_family(sources: set[str]) -> bool:
        return any(sources <= f for f in families) if len(sources) > 1 else True

    list_re = re.compile(r"^([A-Za-z_][\w'.-]*)\s*=\s*\{([^{}]*)\}", re.M)

    # key -> database -> {filename: source}
    claims: dict[tuple[str, str], dict[str, str]] = collections.defaultdict(dict)
    pools: dict[tuple[str, str], dict[str, int]] = collections.defaultdict(dict)
    # Same shape, carrying _body_sha of each declaration. A key declared twice
    # at depth 0 in one file keeps only the last body, which is harmless: that
    # is a type key by definition and type keys never reach the report.
    bodies: dict[tuple[str, str], dict[str, str]] = collections.defaultdict(dict)
    # Keys that are a TYPE, not an identifier: in some databases the depth-0
    # key names the kind of thing declared and repeats within one file
    # (`ambient_object = { }` twenty times). Those collide by design. A key seen
    # more than once inside a single file is a type -- nothing else
    # distinguishes them, and it is what separates the real finding from the 88
    # false positives the first cut produced.
    type_keys: set[tuple[str, str]] = set()
    n = 0

    def scan(path: Path, db: str, fname: str, who: str):
        text = _strip_comments(_read(path))
        seen: collections.Counter = collections.Counter()
        depth = 0
        # The depth-0 block we are currently inside, as (key, offset just past
        # its `{`). Bodies are sliced in THIS pass rather than by a second regex
        # over the same text: a body that disagreed with the key it was filed
        # under would compare two unrelated declarations and call them equal.
        open_at: tuple[str, int] | None = None
        for m in _DEF_TOK.finditer(text):
            tok = m.group(0)
            if tok.startswith(("#", '"')):
                continue
            if tok == "}":
                depth = max(0, depth - 1)
                if depth == 0 and open_at is not None:
                    key, start = open_at
                    bodies[(db, key)][fname] = _body_sha(text[start:m.start()])
                    open_at = None
            elif tok == "{":
                depth += 1
            else:
                if depth == 0:
                    seen[m.group(1)] += 1
                    open_at = (m.group(1), m.end())
                depth += 1
        for key, count in seen.items():
            if count > 1:
                type_keys.add((db, key))
            claims[(db, key)][fname] = who
        for m in list_re.finditer(text):
            body = m.group(2)
            if body.strip() and "=" not in body:      # a flat list, not a block
                pools[(db, m.group(1))][fname] = len(body.split())

    for f in sorted(root.rglob("*.txt")):
        n += 1
        rel = f.relative_to(BUILD).as_posix()
        db = f.parent.relative_to(root).as_posix() or "."
        scan(f, db, f.name, owner.get(rel, "src/"))

    vanilla_db = GAME_DIR / "common"
    for f in sorted(vanilla_db.rglob("*.txt")) if vanilla_db.is_dir() else []:
        db = f.parent.relative_to(vanilla_db).as_posix() or "."
        scan(f, db, f.name, "vanilla")

    contested = shrunk = identical = 0
    for (db, key), who in sorted(claims.items()):
        if (key in ack or f"{db}/{key}" in ack or f"{db}/*" in ack
                or (db, key) in type_keys):
            continue
        # common/defines and unchecked_defines are owned by
        # check_defines_conflicts, which compares the LEAF keys inside NGraphics
        # / NCamera / ... . At this level every defines file trivially "contests"
        # NGraphics with every other, which is true and useless.
        if db.split("/")[0] in ("defines", "unchecked_defines"):
            continue
        mods = {f: s for f, s in who.items() if s != "vanilla"}
        multi = len({s for s in mods.values()}) > 1 and len(mods) > 1

        # Contested by name, identical in content: not a conflict at all.
        # Whichever file the engine keeps, the resulting game is the same, so
        # there is nothing to confirm and nothing to fix. Requires EVERY
        # claimant to have a recorded body -- a key we failed to slice is
        # unknown, not identical, and must still be reported.
        if multi:
            got = [bodies[(db, key)][f] for f in mods if f in bodies[(db, key)]]
            if len(got) == len(mods) and len(set(got)) == 1:
                identical += 1
                multi = False

        if multi and not same_family(set(mods.values())):
            contested += 1
            if contested <= 8:
                # WHICH file wins is a property of the directory, not a constant.
                # This said "last alphabetically" everywhere until decision 29,
                # which is right for LIOS and exactly backwards for the fourteen
                # FIOS directories. TEN of the fourteen have files in the built
                # tree and SEVEN are fed by more than one source (measured
                # 2026-08-22; decision 29 recorded four, before Phase 2 and
                # Phase 4 added to events/ and solar_system_initializers/).
                #
                # Vanilla's own file is in the sort too. It is excluded from
                # `mods` because it is not a source, but it still competes, and
                # under FIOS its `00_` prefix usually means it WINS -- a mod's
                # key never taking effect at all. That case is worth seeing, so
                # the winner is computed over `who`, not `mods`.
                full_db = f"common/{db}"
                fios = full_db in FIOS_DIRS
                win = sorted(who)[0] if fios else sorted(who)[-1]
                note = ""
                if full_db in WHOLE_TEXT_DIRS:
                    note = (f" common/{db} is a whole-file database (decision 29): "
                            f"the engine's unit here is the file, not the key, so "
                            f"the question is which whole file survives, and this "
                            f"key is only the part of it we can see.")
                warnings.append(
                    f"common/{db}: key '{key}' is defined by {len(mods)} sources in "
                    f"differently-named files ({', '.join(f'{f} [{s}]' for f, s in sorted(mods.items()))}). "
                    f"common/{db} is {'FIOS' if fios else 'LIOS'}, so the "
                    f"{'FIRST' if fios else 'LAST'} filename in sort order wins: "
                    f"'{win}' [{who[win]}]. .docs/architecture/conflict-register.md's path register cannot see "
                    f"this, and harvest order does not decide it — confirm that is "
                    f"the winner you want.{note}")

        if f"{db}/*" in ack:
            continue
        sizes = pools.get((db, key), {})
        van = {f: c for f, c in sizes.items() if who.get(f) == "vanilla"}
        ours = {f: c for f, c in sizes.items() if who.get(f) not in (None, "vanilla")}
        if van and ours:
            vmax = max(van.values())
            worst_f, worst = min(ours.items(), key=lambda kv: kv[1])
            if worst < vmax and worst_f not in van:
                shrunk += 1
                if shrunk <= 8:
                    warnings.append(
                        f"common/{db}: '{worst_f}' [{who[worst_f]}] redefines '{key}' "
                        f"with {worst} entries where vanilla's "
                        f"{sorted(van)[0]} has {vmax}. Different filename, so this "
                        f"is not a path overwrite, so check_vanilla_regression "
                        f"cannot see it. IF these pools replace rather than "
                        f"append, {vmax - worst} entries are silently gone. "
                        f"Which of the two it is cannot be settled from the "
                        f"container — check in game, then ack or fix.")

    if contested > 8:
        warnings.append(f"... and {contested - 8} more contested key(s)")
    if shrunk > 8:
        warnings.append(f"... and {shrunk - 8} more shrunk pool(s)")
    return n, identical


def check_order_sensitive_databases() -> int:
    """Order-sensitive databases fed by more than one source.

    A handful of databases carry meaning in the ORDER their entries are declared
    across the whole directory, not just in which entries exist: ethics,
    ship_sizes, starbase_modules, strategic_resources, governments/authorities
    (ORDER_SENSITIVE_DIRS, decision 29). Irony Mod Manager re-emits each of them
    as one file for exactly this reason.

    We cannot do that -- we ship the source mods' files as they stand -- so when
    two sources both contribute, the entries interleave in filename sort order
    and the result is an ordering no source intended and the harvest order did
    not choose. THAT is the whole finding, and it is deliberately stated as a
    fact rather than a defect: whether the interleaving actually breaks anything
    depends on what the database does with order, which cannot be settled from
    the container. Look once, then ack it.

    Explicitly NOT checked: that the database lives in a single file. That was
    the first cut of this check and it was wrong -- vanilla ships 40 files in
    common/ship_sizes and 7 in common/starbase_modules, so "must be one file" is
    Irony's output strategy for writing a patch mod, not a rule of the engine.
    Asserting it would have produced a red check against vanilla's own layout.
    """
    owner: dict[str, str] = {}
    if STATE.is_file():
        try:
            for k, v in json.loads(STATE.read_text()).get("generated", {}).items():
                owner[k] = v.get("source", "?")
        except ValueError:
            pass

    ack = _ack_list("order_sensitive_ack")
    n = 0
    for db in sorted(ORDER_SENSITIVE_DIRS):
        d = BUILD / db
        if not d.is_dir():
            continue
        n += 1
        if db in ack:
            continue
        srcs: dict[str, list[str]] = {}
        for f in sorted(d.glob("*.txt")):
            srcs.setdefault(owner.get(f"{db}/{f.name}", "src/"), []).append(f.name)
        if len(srcs) > 1:
            who = "; ".join(f"{s} ({', '.join(files)})"
                            for s, files in sorted(srcs.items()))
            warnings.append(
                f"{db}: {sum(len(v) for v in srcs.values())} file(s) from "
                f"{len(srcs)} sources — {who}. Entry order across this directory "
                f"is semantic (decision 29), and with two sources contributing "
                f"the entries interleave by filename sort into an order neither "
                f"source chose and the harvest order did not decide. Check what "
                f"this database does with order, then ack it in vendor.yml under "
                f"order_sensitive_ack.")
    return n


def _top_level_blocks(text: str):
    """(key, body) for every depth-0 `key = { ... }`. Body excludes the braces."""
    for m in re.finditer(r"^([A-Za-z_][A-Za-z_0-9]*)\s*=\s*\{", text, re.M):
        i, depth = m.end(), 1
        while i < len(text) and depth:
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        yield m.group(1), text[m.end():i - 1]


def _sub_block(body: str, key: str) -> str | None:
    """The body of the first `key = { ... }` nested anywhere in `body`."""
    m = re.search(rf"\b{re.escape(key)}\s*=\s*\{{", body)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(body) and depth:
        depth += (body[i] == "{") - (body[i] == "}")
        i += 1
    return body[m.end():i - 1]


def _list_field(body: str, key: str) -> set[str]:
    inner = _sub_block(body, key)
    if inner is None:
        # `leader_class = scientist` and `leader_class = { scientist }` are both legal.
        m = re.search(rf"\b{re.escape(key)}\s*=\s*\"?([A-Za-z_][A-Za-z_0-9]*)\"?", body)
        return {m.group(1)} if m else set()
    return set(re.findall(r'"?([A-Za-z_][A-Za-z_0-9]*)"?', inner))


def _defs_and_blocks(*dirs: Path):
    """Top-level blocks across a database family, later dirs overriding earlier.

    Override order is vanilla -> vendored -> src, matching what the game does
    with same-named files and what .docs/architecture/harvest-order.md does with harvest order. A mod
    that redefines a vanilla trait must be the one this check believes.
    """
    out: dict[str, str] = {}
    for d in dirs:
        if not d.is_dir():
            continue
        for f in sorted(d.rglob("*.txt")):
            for k, b in _top_level_blocks(_strip_comments(_read(f))):
                out[k] = b
    return out


def _at_vars(text: str) -> dict[str, int]:
    return {m.group(1): int(m.group(2))
            for m in re.finditer(r"@(\w+)\s*=\s*(-?\d+)", text)}


def check_prescripted_empires() -> int:
    """Every trait, ethic and civic on a prescripted empire, against vanilla's own rules.

    Written against the 2026-08-13 run, which found nine STG empires hidden from
    the empire designer — `select_empire_design_view.cpp:714`, 18 records. Seven
    had no `common/portrait_sets/` entry for their species class; the rest
    carried trait pairs vanilla declares `opposites`, a ruler trait gated to
    Gestalt, and a species over its archetype's trait budget.

    **The log is a sample of this class, not a census.** Sweeping the rule found
    NINE more empires with the identical `trait_communal`/`trait_solitary` pair,
    all AI-only minor powers that never reach the designer and so can never
    produce a record, at any session length. That is the whole reason this check
    exists: `error.log` measures what the engine refused, and the engine refuses
    nothing here — it silently drops one of the two traits at galaxy generation.

    Every rule is read out of vanilla's own databases (trait `cost`, `opposites`,
    `allowed_archetypes`, `allowed_ethics`, `leader_class`; archetype
    `species_trait_points` and `species_max_traits`), never hardcoded, so it
    survives a game patch that rebalances any of them.

    Calibration: reverting the twelve repairs makes this report exactly twelve
    findings and nothing else.
    """
    root = BUILD / "prescripted_countries"
    if not root.is_dir():
        return 0

    traits = _defs_and_blocks(GAME_DIR / "common/traits",
                              BUILD / "common/traits",
                              REPO / "src/common/traits")
    classes = _defs_and_blocks(GAME_DIR / "common/species_classes",
                               BUILD / "common/species_classes",
                               REPO / "src/common/species_classes")

    # Archetype budgets, with vanilla's own @variables resolved.
    arch_src = "".join(_read(f) for d in (GAME_DIR / "common/species_archetypes",
                                          BUILD / "common/species_archetypes")
                       if d.is_dir() for f in sorted(d.rglob("*.txt")))
    at = _at_vars(arch_src)

    def _num(body: str, key: str, default: int) -> int:
        # `-?` is load-bearing: without it `cost = -1` does not match and every
        # malus silently scores 0, which reads as ~130 empires over budget.
        m = re.search(rf"\b{re.escape(key)}\s*=\s*@?(-?\w+)", body)
        if not m:
            return default
        tok = m.group(1)
        return int(tok) if tok.lstrip("-").isdigit() else at.get(tok, default)

    budgets: dict[str, tuple[int, int]] = {}
    for name, body in _top_level_blocks(_strip_comments(arch_src)):
        budgets[name] = (_num(body, "species_trait_points", 2),
                         _num(body, "species_max_traits", 5))

    # species_class -> the portrait GROUPS the empire designer can offer it.
    portraits: dict[str, set[str]] = collections.defaultdict(set)
    for d in (GAME_DIR / "common/portrait_sets", BUILD / "common/portrait_sets"):
        if not d.is_dir():
            continue
        for f in sorted(d.rglob("*.txt")):
            for _, body in _top_level_blocks(_strip_comments(_read(f))):
                m = re.search(r'species_class\s*=\s*"?(\w+)"?', body)
                if m:
                    portraits[m.group(1)] |= _list_field(body, "portraits")

    # An empire the designer never offers cannot be hidden by it. Vanilla marks
    # those `playable = empire_design_never`, a scripted trigger whose body is
    # `always = no`; STG's 79 minor powers use their own `stg_never` the same
    # way. Resolve the trigger rather than matching either name, so the rule is
    # vanilla's idiom and not a list of two spellings.
    triggers = _defs_and_blocks(GAME_DIR / "common/scripted_triggers",
                                BUILD / "common/scripted_triggers",
                                REPO / "src/common/scripted_triggers")

    def _designable(body: str) -> bool:
        m = re.search(r'\bplayable\s*=\s*"?(\w+)"?', body)
        if not m:
            return True
        tok = m.group(1)
        if tok in ("no", "never"):
            return False
        return not re.search(r"\balways\s*=\s*no\b", triggers.get(tok, ""))

    # Civics and origins that GRANT a species trait, written `trait = trait_x`
    # at the top level of the civic body. The engine expects the empire's
    # species to already carry it and reports `Design species was missing trait
    # <t>` when it does not -- deduplicated BY TRAIT NAME, so six broken
    # empires surfaced as three log lines.
    # See .docs/decisions/41-civic-granted-species-traits.md.
    civic_grants: dict[str, set[str]] = {}
    for key, cb in _defs_and_blocks(GAME_DIR / "common/governments/civics",
                                    BUILD / "common/governments/civics",
                                    REPO / "src/common/governments/civics").items():
        g = set(re.findall(r"^\s*trait\s*=\s*(trait_\w+)\s*$", cb, re.M))
        if g:
            civic_grants[key] = g

    ack = _ack_list("prescripted_empire_ack")
    n = 0
    found: list[str] = []

    for f in sorted(root.rglob("*.txt")):
        n += 1
        rp = str(f.relative_to(BUILD))
        for empire, body in _top_level_blocks(_strip_comments(_read(f))):
            if empire in ack:
                continue
            # Two tiers. Trait `opposites` and undefined names corrupt the
            # species wherever it spawns — the engine drops a trait silently and
            # never logs it, which is exactly how nine AI-only minor powers hid
            # from eleven runs of error.log. The designer's own validation rules
            # below only bite on empires it actually offers.
            designable = _designable(body)
            # `ethic_fanatic_x` satisfies an `allowed_ethics = { ethic_x }` gate.
            eth = set(re.findall(r'ethic\s*=\s*"?(\w+)"?', body))
            eth |= {e.replace("_fanatic_", "_") for e in eth}

            for kind in ("species", "secondary_species"):
                sb = _sub_block(body, kind)
                if sb is None:
                    continue
                cm = re.search(r'class\s*=\s*"?(\w+)"?', sb)
                if not cm:
                    continue
                cls = cm.group(1)
                if cls not in classes:
                    found.append(f"{rp}: {empire} {kind} class '{cls}' is defined nowhere")
                    continue
                archetype = (re.search(r'archetype\s*=\s*(\w+)', classes[cls]) or [None, ""])[1] \
                    if re.search(r'archetype\s*=\s*(\w+)', classes[cls]) else ""
                points, maxt = budgets.get(archetype, (2, 5))

                ts = re.findall(r'trait\s*=\s*"?(trait_\w+)"?', sb)
                unknown = [t for t in ts if t not in traits]
                for t in unknown:
                    found.append(f"{rp}: {empire} {kind} has trait '{t}', defined nowhere")
                known = [t for t in ts if t in traits]

                for a in known:
                    for b in _list_field(traits[a], "opposites") & set(known):
                        if a < b:
                            found.append(
                                f"{rp}: {empire} {kind} carries '{a}' and '{b}', which "
                                f"vanilla declares `opposites`. The designer hides the "
                                f"empire; an AI-only empire silently loses one trait.")
                    allowed = _list_field(traits[a], "allowed_archetypes")
                    if allowed and archetype and archetype not in allowed:
                        found.append(f"{rp}: {empire} {kind} trait '{a}' is not allowed on "
                                     f"archetype {archetype} (allowed: {', '.join(sorted(allowed))})")

                if not designable:
                    continue

                spent = sum(_num(traits[t], "cost", 0) for t in known)
                if spent > points:
                    found.append(
                        f"{rp}: {empire} {kind} spends {spent} trait point(s) of "
                        f"{archetype}'s {points}. The designer hides the empire.")
                paid = len([t for t in known if _num(traits[t], "cost", 0) != 0])
                if paid > maxt:
                    found.append(f"{rp}: {empire} {kind} has {paid} costed traits, "
                                 f"over {archetype}'s species_max_traits of {maxt}")

                # 4a: no portrait set for the class means nothing to offer at all.
                pm = re.search(r'portrait\s*=\s*"?(\w+)"?', sb)
                if kind == "species" and not portraits.get(cls):
                    found.append(
                        f"{rp}: {empire} species class '{cls}' has no common/portrait_sets/ "
                        f"entry, so the empire designer has no portrait to offer and hides "
                        f"the empire — 'Must select a portrait'.")
                elif pm and portraits.get(cls) and pm.group(1) not in portraits[cls]:
                    found.append(
                        f"{rp}: {empire} {kind} asks for portrait group '{pm.group(1)}', "
                        f"which is not in {cls}'s portrait set "
                        f"({', '.join(sorted(portraits[cls]))})")

            # A civic that grants a trait needs that trait on the empire's
            # species. Both species blocks count as one pool, NOT the primary
            # alone: the assimilator civics want it on the SECONDARY species,
            # which is where vanilla's Tebrid Homolog and STG's Borg both put
            # trait_cybernetic. Reading only `species` reported the Borg, and
            # the Borg was already correct.
            all_traits = set()
            for kind in ("species", "secondary_species"):
                sb2 = _sub_block(body, kind)
                if sb2 is not None:
                    all_traits |= set(re.findall(r'trait\s*=\s*"?(trait_\w+)"?', sb2))
            used = set(re.findall(r'"(civic_\w+)"', body))
            used |= set(re.findall(r'origin\s*=\s*"?(origin_\w+)"?', body))
            for civ in sorted(used):
                for miss in sorted(civic_grants.get(civ, set()) - all_traits):
                    found.append(
                        f"{rp}: {empire} takes '{civ}', which grants '{miss}', but no "
                        f"species block carries it — `Design species was missing trait "
                        f"{miss}`. Vanilla's own empires never do this in 51 designs. "
                        f"Add the trait, or pick a civic the species can actually hold.")

            for who in ("ruler", "leader"):
                lb = _sub_block(body, who)
                if lb is None or not designable:
                    continue
                lc = (re.search(r'leader_class\s*=\s*"?(\w+)"?', lb) or [None, None])[1] \
                    if re.search(r'leader_class\s*=\s*"?(\w+)"?', lb) else None
                for t in re.findall(r'trait\s*=\s*"?(trait_\w+)"?', lb):
                    if t not in traits:
                        found.append(f"{rp}: {empire} {who} has trait '{t}', defined nowhere")
                        continue
                    gate = _list_field(traits[t], "allowed_ethics")
                    if gate and not (gate & eth):
                        found.append(
                            f"{rp}: {empire} {who} trait '{t}' requires one of "
                            f"{', '.join(sorted(gate))}; the empire is "
                            f"{', '.join(sorted(e for e in eth if 'fanatic' in e or e in gate)) or 'none of them'}. "
                            f"The designer hides the empire.")
                    lcs = _list_field(traits[t], "leader_class")
                    if lc and lcs and lc not in lcs:
                        found.append(f"{rp}: {empire} {who} trait '{t}' is "
                                     f"leader_class = {{ {' '.join(sorted(lcs))} }}, not {lc}")

    for msg in found[:12]:
        errors.append(msg)
    if len(found) > 12:
        errors.append(f"... and {len(found) - 12} more prescripted-empire finding(s). "
                      f"Reviewed cases go in vendor.yml `prescripted_empire_ack:`.")
    return n


def check_name_lists() -> int:
    """Every name-list token must have a localisation key.

    Stellaris looks a name token up as a loc key, always — there is no literal
    mode — so a bare token logs `Failed to localize leader name with key <Name>`
    every time it is drawn. The 2026-08-01 run logged 19 in three minutes, one
    per leader it happened to generate; ship and planet names carry the same
    defect and simply had not been reached yet.

    Also rejects the `%O%` sequential format, which is not a thing: vanilla
    routes fleet and army names through a loc key containing $ORD$, and there is
    no %O% in any vanilla name list.
    """
    nl = REPO / "src" / "common" / "name_lists"
    if not nl.is_dir():
        return 0

    keys: set[str] = set()
    values: dict[str, str] = {}
    for p in walk((".yml",), under="src/localisation"):
        for line in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = re.match(r"\s*([A-Za-z0-9_.\-]+):\d*\s+\"(.*)\"\s*$", line)
            if m:
                keys.add(m.group(1))
                values.setdefault(m.group(1), m.group(2))
                continue
            m = re.match(r"\s*([A-Za-z0-9_.\-]+):\d*\s+\"", line)
            if m:
                keys.add(m.group(1))

    # The ordinal tokens the engine actually substitutes, derived from vanilla's
    # own name-list loc rather than asserted: $ORD$ and $O$, 733 and 768 uses.
    ordinals: set[str] = set()
    for d in (GAME_DIR / "localisation" / "english",):
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*name*.yml")):
            ordinals |= set(re.findall(r"\$O\$|\$ORD\$", _read(f)))
    ordinals = ordinals or {"$ORD$", "$O$"}

    token = re.compile(r"[A-Za-z][A-Za-z_0-9\-]*")
    n = 0
    for p in sorted(nl.glob("*.txt")):
        n += 1
        text = _strip_comments(p.read_text(encoding="utf-8", errors="replace"))
        rp = str(p.relative_to(REPO))

        for m in re.finditer(r"sequential_name\s*=\s*\"([^\"]*)\"", text):
            errors.append(
                f"{rp}: sequential_name = \"{m.group(1)}\" is a literal, and the "
                f"game rejects it (`Malformed sequential format`). Vanilla uses a "
                f"loc key whose value contains $ORD$ — see HUMAN1_FLEET.")

        # The key form is correct; the defect lives in the loc VALUE. The 08-14
        # run logged one `Malformed sequential format in STG_SULIBAN_GROUP`
        # against 1,154 `%O%` values — a fleet format only errors when a fleet is
        # actually named, so the log samples this class one name at a time.
        for m in re.finditer(r"sequential_name\s*=\s*([A-Za-z0-9_.\-]+)\s*$",
                             text, re.M):
            key = m.group(1)
            if key not in values:
                continue
            val = values[key]
            if not any(o in val for o in ordinals):
                errors.append(
                    f"{rp}: sequential_name = {key} resolves to \"{val}\", which "
                    f"contains no ordinal token ({' or '.join(sorted(ordinals))}). "
                    f"The game logs `Malformed sequential format in {key}` the "
                    f"first time it names a fleet or army from this list.")

        missing: list[str] = []
        for m in re.finditer(r"\{([^{}]*)\}", text):
            body = m.group(1)
            if "=" in body:            # not a token list
                continue
            for t in token.findall(body):
                if t not in keys:
                    missing.append(t)
        if missing:
            uniq = sorted(set(missing))
            shown = " ".join(uniq[:8])
            more = f" (+{len(uniq) - 8} more)" if len(uniq) > 8 else ""
            errors.append(
                f"{rp}: {len(uniq)} name token(s) with no localisation key: "
                f"{shown}{more}. Each renders as the raw key and logs "
                f"`Failed to localize`. Add them to "
                f"src/localisation/english/stg_names_l_english.yml.")
    return n


def check_colony_name_collisions() -> int:
    """A `planet_names` pool must not offer a name some empire's CAPITAL uses.

    These pools name colonies. Before decision 25 they also, in effect, named
    the other planets of the home system, and the Federation's pool is a list of
    Federation MEMBER worlds -- so Sol was generated containing Bajor and
    Andoria. Pinning home systems fixed that symptom and not the cause: the pool
    still offered "Vulcan" for any colony the Federation founded, anywhere,
    while the Vulcan Confederacy sat on the real one.

    Two flavours, both wrong and both checked here:
      * another empire's capital -- two Vulcans in one galaxy;
      * the empire's OWN capital -- an Andorian colony called Andoria, which
        only became possible once `planet_name` pinned the capital for real.

    Resolution is through localisation on both sides, because a name list holds
    keys and a prescripted empire holds keys, and the collision is between their
    VALUES: STG_N_Vulcan and STG_planet_name_vulcan are different keys that both
    render "Vulcan".
    """
    names_dir = BUILD / "common/name_lists"
    pre = BUILD / "prescripted_countries"
    if not names_dir.is_dir() or not pre.is_dir():
        return 0

    loc: dict[str, str] = {}
    for p in (BUILD / "localisation").rglob("*.yml"):
        for line in _read(p).splitlines():
            m = re.match(r'\s*([A-Za-z_0-9\-]+):\d*\s*"(.*)"\s*$', line)
            if m:
                loc.setdefault(m.group(1), m.group(2))

    owner: dict[str, str] = {}
    for f in pre.rglob("*.txt"):
        text = _strip_comments(_read(f))
        for key, body in _top_level_blocks(text):
            for field in ("planet_name", "system_name"):
                m = re.search(rf'{field}\s*=\s*"([^"]+)"', body)
                if m and m.group(1) in loc:
                    owner.setdefault(loc[m.group(1)], key)

    ack = _ack_list("colony_name_ack")
    n = 0
    for f in sorted(names_dir.rglob("*.txt")):
        text = _read(f)
        block = re.search(r"planet_names\s*=\s*\{(.*?)\n\t\}", text, re.S)
        if not block:
            continue
        n += 1
        hits = []
        for tok in re.findall(r"\bSTG_N_[A-Za-z_0-9\-]+", block.group(1)):
            val = loc.get(tok)
            if val and val in owner and val not in ack:
                hits.append(f"{val} ({owner[val]})")
        if hits:
            uniq = sorted(set(hits))
            errors.append(
                f"{f.relative_to(BUILD)}: planet_names offers "
                f"{len(uniq)} name(s) an empire already holds as a capital: "
                f"{', '.join(uniq[:6])}"
                f"{f' (+{len(uniq) - 6} more)' if len(uniq) > 6 else ''}. "
                f"A colony would carry a homeworld's name. Drop the token and "
                f"top the pool back up — see .docs/decisions/25-real-home-systems.md.")
    return n


def check_prescripted_initializers() -> int:
    """Every `initializer = "X"` must name a solar system initializer that
    exists in the merged tree, and one the engine will let an empire have.

    The engine reports a bad one -- `prescripted_systems.cpp: Invalid
    initializer "X"` -- but only for empires it actually tries to place, so an
    AI-only minor with a typo can sit undetected for as long as nobody rolls it.
    Sweeping the rule beats reading the log, as with the traits in
    check_prescripted_empires.

    Two conditions, because the engine applies two. The initializer has to be
    declared; and it has to be `usage = custom_empire`, since that is what makes
    it available to an empire rather than to map generation. A system with the
    wrong usage resolves by name and then never spawns.
    """
    pre = BUILD / "prescripted_countries"
    init_dir = BUILD / "common/solar_system_initializers"
    if not pre.is_dir() or not init_dir.is_dir():
        return 0

    declared: dict[str, str] = {}
    for f in init_dir.rglob("*.txt"):
        text = _strip_comments(_read(f))
        for key, body in _top_level_blocks(text):
            declared.setdefault(key, body)

    ack = _ack_list("prescripted_initializer_ack")
    n = 0
    for f in sorted(pre.rglob("*.txt")):
        text = _strip_comments(_read(f))
        if not text.strip():
            continue
        n += 1
        rp = str(f.relative_to(BUILD))
        for key, body in _top_level_blocks(text):
            m = re.search(r'\binitializer\s*=\s*"([^"]*)"', body)
            if not m or not m.group(1) or m.group(1) in ack:
                continue
            target = m.group(1)
            if target not in declared:
                errors.append(
                    f"{rp}: {key} names initializer '{target}', which no file "
                    f"in common/solar_system_initializers/ declares. The engine "
                    f"logs `Invalid initializer` and the empire falls back to a "
                    f"generated home system — the very thing the initializer was "
                    f"added to stop.")
            elif not re.search(r"usage\s*=\s*custom_empire", declared[target]):
                errors.append(
                    f"{rp}: {key} names initializer '{target}', which is "
                    f"declared but is not `usage = custom_empire`. It resolves "
                    f"by name and then never spawns for an empire.")
    return n


def _initializer_class_tokens(text: str) -> set[tuple[str, bool]]:
    """The `class` values in an initializer that name a planet or star class,
    each paired with whether it was written **quoted**.

    Block-aware on purpose. `class` is a heavily overloaded key in these files:
    `create_species = { class = random_non_machine }` is a species class,
    `create_leader = { class = scientist }` a leader class, and
    `ideal_design_class` a ship design. A flat regex over the file collects all
    three and drowns the real finding — it produced 51 false positives against
    14 true ones on the first calibration pass.

    Only two positions name a planet/star class: `class` at the initializer's
    own level (the system's star class) and `class` directly inside a
    `planet`/`moon` block. Anything deeper belongs to some other database.

    The quote flag is carried because it is *semantic* here, which cost a live
    run to learn: a quoted engine keyword parses and then resolves to nothing.
    See .docs/decisions/27-quoted-class-keyword.md.
    """
    refs: set[tuple[str, bool]] = set()
    stack: list[str] = []
    # key = {   |   }   |   class = value   (quoted or bare)
    tok = re.compile(r'([a-z_][a-z0-9_]*)\s*=\s*\{|(\})|'
                     r'\bclass\s*=\s*(?:"([A-Za-z][A-Za-z0-9_]*)"'
                     r'|([A-Za-z][A-Za-z0-9_]*))')
    for m in tok.finditer(text):
        if m.group(1) is not None:
            stack.append(m.group(1))
        elif m.group(2) is not None:
            if stack:
                stack.pop()
        else:
            # The initializer's own level is the system's star class; otherwise
            # the innermost block must be the body itself. `moon` nests inside
            # `planet`, so this tests the innermost key rather than the depth.
            if len(stack) == 1 or stack[-1] in ("planet", "moon"):
                quoted = m.group(3) is not None
                refs.add((m.group(3) if quoted else m.group(4), quoted))
    return refs


def _initializer_class_refs(text: str) -> set[str]:
    """`_initializer_class_tokens` with the quoting discarded — the question of
    whether a name resolves at all, independent of how it is written."""
    return {name for name, _ in _initializer_class_tokens(text)}


def _star_planet_count(body: str) -> int:
    """`class = "star"` planets in one initializer — the ones filled from the
    system's star class. Block-aware for the reason in
    _initializer_class_refs."""
    n, stack = 0, []
    for m in re.finditer(r'([a-z_][a-z0-9_]*)\s*=\s*\{|(\})|class\s*=\s*"?star"?',
                         body):
        if m.group(1) is not None:
            stack.append(m.group(1))
        elif m.group(2) is not None:
            if stack:
                stack.pop()
        elif stack and stack[-1] in ("planet", "moon"):
            n += 1
    return n


def _star_class_counts() -> dict[str, int]:
    """How many stars each star class supplies to `class = "star"` planets."""
    out: dict[str, int] = {}
    for root in (GAME_DIR, BUILD):
        d = root / "common/star_classes"
        if not d.is_dir():
            continue
        for f in d.rglob("*.txt"):
            text = _strip_comments(_read(f))
            for key, body in _top_level_blocks(text):
                if key.startswith("sc_"):
                    out[key] = len(re.findall(r"^\s*planet\s*=", body, re.M))
    return out


def check_initializer_classes() -> int:
    """Every planet/star `class` named by a solar system initializer must
    resolve against the merged tree.

    This crashes the game rather than logging it. On 2026-08-03 Stellaris died
    initialising CSystemInitializerDataBase with an empty time.log and
    *nothing in error.log* — the database resolves these names as it loads, so
    it never reaches the point where a parse error would be reported. Nine
    names had just been introduced: seven STNH planet classes and two STNH star
    classes, written through unchanged by a generator whose remap tables were
    `MAP.get(val, val)`, into a build that does not vendor STNH's common/.
    See .docs/decisions/26-home-system-classes.md.

    Scope is the merged tree, not src/: STNH's classes are perfectly valid in
    STNH, and only the merge decides whether they exist here.

    The vocabulary is derived, never listed, and it took two calibration passes
    to get the derivation honest:

    - Declared classes come from common/planet_classes/ and
      common/star_classes/ — the latter including its randomizers/ subtree,
      because a system's `class` may name an `rl_*` list rather than one class.
    - Everything else legitimate is whatever *vanilla's own initializers* name
      in these same two positions and vanilla never declares: `star`, `none`,
      `random_colonizable`, `random_asteroid`, and the `rl_habitable_normal`
      family of planet randomizers, which the engine holds internally and no
      file on disk defines. Asking vanilla rather than asserting a list is the
      same rule the BOM and shader checks are built on — it survives a patch.
    """
    init_dir = BUILD / "common/solar_system_initializers"
    if not init_dir.is_dir():
        return 0

    def declared(kind: str) -> set[str]:
        found: set[str] = set()
        for root in (GAME_DIR, BUILD):
            d = root / "common" / kind
            if not d.is_dir():
                continue
            for f in d.rglob("*.txt"):
                found |= set(re.findall(r"^\s*([a-z][a-z0-9_]*)\s*=\s*\{",
                                        _strip_comments(_read(f)), re.M))
        return found

    valid = declared("planet_classes") | declared("star_classes")
    belts = declared("asteroid_belts")
    if not valid or not belts:
        return 0

    van_init = GAME_DIR / "common/solar_system_initializers"
    if not van_init.is_dir():
        return 0        # no reference for the engine's own vocabulary
    builtins: set[str] = set()
    van_bare: set[str] = set()      # names vanilla writes without quotes
    van_quoted: set[str] = set()    # names vanilla writes with them
    for f in van_init.rglob("*.txt"):
        # example.txt is the engine's vocabulary reference and it documents by
        # commenting out — `#class = none`, `#class = random_asteroid`. Strip
        # its comments and those keywords vanish, which cost two false
        # positives on the second calibration pass. Read it raw; strip the
        # rest, where a commented-out line is dead script rather than a spec.
        raw = _read(f)
        for name, quoted in _initializer_class_tokens(
                raw if f.name == "example.txt" else _strip_comments(raw)):
            builtins.add(name)
            (van_quoted if quoted else van_bare).add(name)
    builtins -= valid
    if not builtins:
        return 0

    # Which names must be written BARE, asked of vanilla per name rather than
    # asserted as a class. "Not a declared class" is the wrong rule and was
    # tried first: it flags the `rl_*` randomizer lists, which no file declares
    # and which vanilla quotes 14 times. What actually separates them is how
    # vanilla writes each one — `star`, `none`, `random*` and
    # `ideal_planet_class` appear 671 times and never once in quotes, while
    # every `rl_*` and every `pc_*` is quoted somewhere. Same rule as the BOM
    # and shader allowlists: ask vanilla, don't declare the answer.
    # See .docs/decisions/27-quoted-class-keyword.md.
    bare_only = van_bare - van_quoted - valid

    ack = _ack_list("initializer_class_ack")
    star_counts = _star_class_counts()
    n = 0
    for f in sorted(init_dir.rglob("*.txt")):
        text = _strip_comments(_read(f))
        if not text.strip():
            continue
        n += 1
        rp = str(f.relative_to(BUILD))
        for name, quoted in sorted(_initializer_class_tokens(text)):
            if name in valid or name in builtins or name in ack:
                # A declared name may be quoted or bare; vanilla does both.
                # A KEYWORD may only be bare. `class = "star"` parses, then
                # resolves against nothing, and the body is never created —
                # so the system spawns with no star, the empire's home
                # starbase has nothing to anchor to, and its starting fleets
                # fail on `capital_star`. One line in error.log, and only for
                # the system someone actually played.
                # See .docs/decisions/27-quoted-class-keyword.md.
                if quoted and name in bare_only and name not in ack:
                    errors.append(
                        f"{rp}: writes `class = \"{name}\"` quoted. Vanilla "
                        f"writes '{name}' bare every time it uses it and never "
                        f"in quotes, and a quoted keyword resolves to nothing "
                        f"— the body is silently never created, so the system "
                        f"spawns without it. Emit it bare.")
                continue
            errors.append(
                f"{rp}: names planet/star class '{name}', which no file in "
                f"common/planet_classes/ or common/star_classes/ declares and "
                f"which is not vocabulary vanilla's own initializers use. An "
                f"unresolvable class can hard-crash CSystemInitializerDataBase "
                f"at load, with nothing in error.log.")

        # Asteroid belt types resolve in the same database, and were the second
        # half of the 2026-08-03 crash: STNH's STH_asteroid_belts.txt adds
        # `icy_asteroid_belt_dispersed` to vanilla's six, and we do not vendor
        # STNH's common/. Fixing only the classes still crashed.
        for name in sorted(set(re.findall(
                r"asteroid_belt\s*=\s*\{\s*type\s*=\s*(\w+)", text))):
            if name in belts or name in ack:
                continue
            errors.append(
                f"{rp}: names asteroid belt type '{name}', which no file in "
                f"common/asteroid_belts/ declares. Resolved by the same "
                f"database as the classes above, and just as fatal.")

        # A `class = "star"` planet is filled from the system's star class, so
        # more of them than the class supplies leaves one with nothing to draw
        # from. Reported as a warning, not an error: vanilla never does it in
        # 40 files, but Real Space does it three times and the game loads, so
        # it is a defect of the system rather than a certain crash.
        for key, body in _top_level_blocks(text):
            cm = re.search(r'class\s*=\s*"(sc_[a-z0-9_]+)"', body)
            if not cm or key in ack:
                continue
            have = star_counts.get(cm.group(1))
            if have is None:
                continue
            want = _star_planet_count(body)
            if want > have:
                warnings.append(
                    f"{rp}: {key} declares star class {cm.group(1)}, which "
                    f"supplies {have} star(s), but places {want} "
                    f'`class = "star"` planet(s). The surplus has no star to '
                    f"draw from. Vanilla never does this.")
    return n


def check_home_planet_generation() -> int:
    """A `usage = custom_empire` initializer must establish the empire on its
    capital, not merely place the geometry.

    `starting_planet = yes` (or `home_planet = yes`) says *which* body is the
    capital. `generate_empire_home_planet = yes` is what actually puts the
    empire there — capital building, pops, districts, and the home-system
    starbase that makes the empire the system's owner. Ship the first without
    the second and the game starts, the system exists, the planet exists, and
    **the player does not own their own home system**. Nothing is logged: this
    is a gameplay outcome, not a load error, so `error.log` is silent and only
    playing reveals it. That is what the 2026-08-03 evening run reported for
    the Klingon Empire, across all 37 generated systems.

    The rule is vanilla's own, derived rather than asserted: of its nine
    `usage = custom_empire` initializers, eight carry the effect. The single
    exception is `sol_system_initializer`, which five vanilla empires use and
    which scripted content references by name throughout — so it is treated as
    special-cased rather than as licence to omit the effect. `deneb_system` is
    the case that matches a generated STG home system exactly, a prescripted
    empire on fixed geometry, and it pairs `starting_planet = yes` with the
    effect in a second `init_effect` block.

    See .docs/decisions/26-home-system-classes.md.
    """
    init_dir = BUILD / "common/solar_system_initializers"
    if not init_dir.is_dir():
        return 0

    ack = _ack_list("home_planet_generation_ack")
    n = 0
    for f in sorted(init_dir.rglob("*.txt")):
        text = _strip_comments(_read(f))
        if not text.strip():
            continue
        n += 1
        rp = str(f.relative_to(BUILD))
        for key, body in _top_level_blocks(text):
            if key in ack or not re.search(r"usage\s*=\s*custom_empire", body):
                continue
            marks_capital = re.search(r"\bstarting_planet\s*=\s*yes", body) or \
                re.search(r"(?<![_a-z])home_planet\s*=\s*yes", body)
            if not marks_capital:
                continue
            if re.search(r"generate_empire_home_planet\s*=\s*yes", body):
                continue
            errors.append(
                f"{rp}: {key} is `usage = custom_empire` and marks a capital, "
                f"but never runs `generate_empire_home_planet = yes`. The "
                f"system and the planet spawn and the empire is never "
                f"established on them — in play the empire does not own its "
                f"own home system. Nothing is logged; only playing shows it.")
    return n


def check_prescripted_portraits() -> int:
    """Every `portrait = "X"` on a prescripted empire must resolve to a portrait
    or portrait_group declared in the merged tree.

    The engine does not refuse an unresolved one at load — it logs
    `portraitobject.cpp:722 Failed to find portrait selector X` only when a
    player opens the empire designer on that empire, and then draws it blank.
    The 08-14 run surfaced `suliban_male_01` that way; sweeping the rule found
    `hur` (a truncated `hur'q`) on an AI-only minor power that no session length
    would ever have reported.

    Resolution follows the engine: a file in the mod shadows a vanilla file of
    the same name, so index vanilla first and let the build overwrite it.
    """
    root = BUILD / "prescripted_countries"
    if not root.is_dir():
        return 0

    def _depth1_keys(text: str, wanted: str) -> set[str]:
        out: set[str] = set()
        for m in re.finditer(rf"\b{wanted}\s*=\s*{{", text):
            i, depth = m.end(), 1
            while i < len(text) and depth:
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                i += 1
            body, d = text[m.end():i - 1], 0
            for km in re.finditer(r"([A-Za-z_][\w'\-]*)\s*=\s*{|{|}", body):
                if km.group(1) is not None:
                    if d == 0:
                        out.add(km.group(1))
                    d += 1
                elif km.group(0) == "{":
                    d += 1
                else:
                    d -= 1
        return out

    files: dict[str, Path] = {}
    for d in (GAME_DIR / "gfx/portraits/portraits", BUILD / "gfx/portraits/portraits"):
        if d.is_dir():
            for p in sorted(d.glob("*.txt")):
                files[p.name] = p          # build shadows vanilla by filename

    declared: set[str] = set()
    for p in files.values():
        t = _strip_comments(_read(p))
        declared |= _depth1_keys(t, "portraits")
        declared |= _depth1_keys(t, "portrait_groups")

    n = 0
    for f in sorted(root.glob("*.txt")):
        n += 1
        rp = f"prescripted_countries/{f.name}"
        for i, line in enumerate(_read(f).splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            m = re.search(r'portrait\s*=\s*"([^"]+)"', line)
            if m and m.group(1) not in declared:
                errors.append(
                    f"{rp}:{i}: portrait \"{m.group(1)}\" is declared by no "
                    f"portraits or portrait_groups block in the merged tree. "
                    f"The empire designer draws it blank and logs "
                    f"`Failed to find portrait selector {m.group(1)}`.")
    return n


def check_species_class_loc() -> int:
    """Every species class STG declares needs the loc family vanilla derives
    from the class key, and none of those keys may carry an `stg_` prefix.

    The engine builds them off the class key itself — `FED_desc`, `FED_organ` —
    so a class with no localisation shows the raw three-letter key wherever the
    UI names it, and a class whose family is prefixed `STG_` resolves nothing
    below the title. Both fail silently: `error.log` had nothing to say about
    either through the 08-15 run, in which 87 of 101 classes had no loc at all
    and the other 14 had a title and 26 keys the engine never looks up.
    See .docs/decisions/21-species-class-localisation.md.

    The required suffix set is derived from vanilla's own usage — the suffixes
    it defines for *every* one of its species classes — so a game patch that
    adds or drops one moves this check with it rather than stranding a hand
    list.
    """
    classes_dir = REPO / "src" / "common" / "species_classes"
    if not classes_dir.is_dir():
        return 0

    def _class_keys(paths) -> set[str]:
        out: set[str] = set()
        for p in paths:
            for m in re.finditer(r"^([A-Z][A-Z0-9_]*)\s*=\s*{", _strip_comments(_read(p)), re.M):
                out.add(m.group(1))
        return out

    vanilla_classes = _class_keys(sorted((GAME_DIR / "common/species_classes").glob("*.txt")))
    ours = _class_keys(sorted(classes_dir.glob("*.txt")))
    if not (vanilla_classes and ours):
        return 0

    # What vanilla localises, per class, keyed by suffix ("" is the title).
    vloc: dict[str, set[str]] = {c: set() for c in vanilla_classes}
    for p in sorted((GAME_DIR / "localisation" / "english").rglob("*.yml")):
        for line in _read(p).splitlines():
            m = re.match(r"\s*([A-Z][A-Z0-9_]*?)((?:_[a-z0-9_]+)?):\d+\s+\"", line)
            if m and m.group(1) in vloc:
                vloc[m.group(1)].add(m.group(2))
    # Vanilla's own usage is bimodal: 27 classes carry a 27-38 key family and 5
    # carry only a title (EXD, IMPERIAL, SOLARPUNK, SWARM, CYBERNETIC — engine
    # bookkeeping, never a playable species). Intersecting all 32 would demand
    # nothing but the title, so take the intersection over the fully localised
    # half, split at half the largest family rather than at a hand-picked key.
    localised = [s for s in vloc.values() if s]
    if not localised:
        return 0
    cut = max(len(s) for s in localised) / 2
    full = [s for s in localised if len(s) >= cut]
    required = set.intersection(*full)

    have: set[str] = set()
    for p in walk((".yml",), under="src/localisation"):
        for line in _read(p).splitlines():
            m = re.match(r"\s*([A-Za-z0-9_.\-]+):\d*\s+\"", line)
            if m:
                have.add(m.group(1))

    for cls in sorted(ours):
        missing = sorted(s for s in required if f"{cls}{s}" not in have)
        if not missing:
            continue
        prefixed = [s for s in missing if f"STG_{cls}{s}" in have]
        if prefixed:
            errors.append(
                f"common/species_classes: species class '{cls}' localises "
                f"{len(prefixed)} of its keys as STG_{cls}_* . The engine derives "
                f"them from the class key and never looks up a prefixed one — "
                f"drop the prefix (convention exception 2, decision 21).")
        else:
            errors.append(
                f"common/species_classes: species class '{cls}' is missing "
                f"{len(missing)} localisation key(s) vanilla defines for every "
                f"one of its own classes ({', '.join(cls + s if s else cls for s in missing[:4])}"
                f"{', …' if len(missing) > 4 else ''}). The UI shows the raw key.")
    return len(ours)


def _selector_depth() -> dict:
    """clothes selector name -> how many distinct textures it declares.

    Searched RECURSIVELY and across both trees. STNH keeps 530 of its selectors
    in per-species subdirectories of `gfx/portraits/asset_selectors/` where
    vanilla has none, so a top-level glob finds a handful of files and reports
    every selector in the other 520 as undeclared -- which is not a finding
    about the tree, it is a bug in the question.
    """
    out: dict[str, int] = {}
    for d in (GAME_DIR / "gfx/portraits/asset_selectors",
              BUILD / "gfx/portraits/asset_selectors"):
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.txt")):
            t = _strip_comments(_read(p))
            for m in re.finditer(r"^(\w+)\s*=\s*\{", t, re.M):
                i, dep = m.end(), 1
                while i < len(t) and dep:
                    dep += (t[i] == "{") - (t[i] == "}")
                    i += 1
                out[m.group(1)] = len(set(re.findall(r'"([^"]+\.dds)"',
                                                     t[m.end():i])))
    return out


def check_prescripted_appearance() -> int:
    """A prescripted ruler's `texture = N` must index a `character_textures`
    entry the portrait actually declares.

    `texture`, `attachment` and `clothes` pin a leader's appearance to a fixed
    index instead of letting the game choose. Vanilla varies them freely because
    a vanilla portrait carries several body textures; most STNH Trek portraits
    carry exactly one, so `texture = 1` is off the end of the list. STG shipped
    that on **74 of its 101 rulers** through the 08-15 run, and the engine says
    nothing — it falls back rather than refusing.

    `clothes` IS THE SECOND HALF, and what it asks changed on 2026-08-08.
    Decision 68 believed the index enumerates the distinct texture paths of the
    portrait's selector in file order, and this check re-derived that number
    every run. A live run wore six garments the model does not predict, so the
    enumeration is NOT that and nothing readable here says what it is. Asking a
    question whose answer we cannot establish is worse than not asking: it
    reported `ok` on six wrong rulers for a day.

    So the question is now the one that does not need the enumeration: **a
    prescripted ruler must not sit on a `humanoid_master_*` selector at all.**
    That file is shared by 44 species classes and its index 0 is a human
    civilian jacket, so no value of `clothes` dresses a Trek ruler correctly by
    construction. The fix is STNH's own — a dedicated one-texture selector and
    `clothes = 0`, the one index a live run HAS confirmed — and it is generated
    by tools/gen_ruler_clothes.py.
    See .docs/decisions/69-ruler-clothes-dedicated-selectors.md.

    Calibrated by reverting the repair: **7 findings before, 0 after.**

    The in-range half stays and now covers every selector, because a one-texture
    selector makes an out-of-range index cheap to write and invisible to hit —
    STNH ships three of exactly that (`clothes = 109` against a one-entry file).

    94 rulers still pin nothing, and this says nothing about them: on a
    per-species selector index 0 is already that species' own clothing, which
    is decision 57's state and is correct.
    """
    root = REPO / "src" / "prescripted_countries"
    if not root.is_dir():
        return 0

    counts: dict[str, int] = {}
    for d in (GAME_DIR / "gfx/portraits/portraits", BUILD / "gfx/portraits/portraits"):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.txt")):
            t = _strip_comments(_read(p))
            for m in re.finditer(r"([a-z0-9_'\-]+)\s*=\s*{", t):
                i, dep = m.end(), 1
                while i < len(t) and dep:
                    dep += (t[i] == "{") - (t[i] == "}")
                    i += 1
                ct = re.search(r"character_textures\s*=\s*{([^}]*)}", t[m.end():i], re.S)
                if ct:
                    counts[m.group(1)] = len(re.findall(r'"([^"]+)"', ct.group(1)))

    sels: dict[str, str] = {}
    for d in (GAME_DIR / "gfx/portraits/portraits", BUILD / "gfx/portraits/portraits"):
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.txt")):
            for m in re.finditer(
                    r'([\w\'\-]+)\s*=\s*\{[^{}]*clothes_selector\s*=\s*"([^"]+)"',
                    _strip_comments(_read(p))):
                sels[m.group(1)] = m.group(2)
    depth = _selector_depth()

    n = 0
    for f in sorted(root.glob("*.txt")):
        n += 1
        rp = f"src/prescripted_countries/{f.name}"
        for empire, body in _top_level_blocks(_strip_comments(_read(f))):
            rb = _sub_block(body, "ruler")
            if rb is None:
                continue
            pm = re.search(r'portrait\s*=\s*"?([\w\'\-]+)"?', rb)
            tm = re.search(r"texture\s*=\s*(\d+)", rb)
            if pm and tm and pm.group(1) in counts:
                have = counts[pm.group(1)]
                if int(tm.group(1)) >= have:
                    errors.append(
                        f"{rp}: {empire} ruler sets texture = {tm.group(1)} on "
                        f"portrait '{pm.group(1)}', which declares {have} "
                        f"character_texture(s) — valid indices are 0..{have - 1}. "
                        f"The engine falls back silently rather than refusing.")
            if not pm:
                continue
            sel = sels.get(pm.group(1), "")
            if sel.startswith("humanoid_master_"):
                errors.append(
                    f"{rp}: {empire} ruler uses portrait '{pm.group(1)}', whose "
                    f"clothes selector is '{sel}' — shared by 44 species "
                    f"classes, so no `clothes` index addresses this empire's "
                    f"own garment. Give it a dedicated one-texture selector: "
                    f"re-run tools/gen_ruler_clothes.py.")
                continue
            cm = re.search(r"clothes\s*=\s*(\d+)", rb)
            if not cm or sel not in depth:
                continue
            idx, have = int(cm.group(1)), depth[sel]
            if idx >= have:
                errors.append(
                    f"{rp}: {empire} ruler pins clothes = {idx} on selector "
                    f"'{sel}', which declares {have} texture(s) — valid "
                    f"indices are 0..{have - 1}. The engine falls back "
                    f"silently rather than refusing.")
    return n


_SELECTOR_TEXTURE_RE = re.compile(r'"(gfx/models/portraits/[^"]*)"')


def check_selector_texture_paths() -> int:
    """A quoted texture path in an asset selector that is not a `.dds` path.

    THE SYNTAX HALF OF A TWO-HALF QUESTION, landed on its own because it has no
    content call behind it. The other half -- does the path RESOLVE -- is
    check_selector_texture_files below, landed 2026-08-24 once the population
    was measured properly: 117 rows, not the 196 recorded, and 76 of those were
    somebody's typo rather than a content call (decision 85). This half
    is mechanical: the path is malformed, the engine cannot load it, and
    appending `.dds` cannot be the wrong answer.

    A TEXTURE THAT FAILS TO LOAD FALLS BACK RATHER THAN FAILING. That is what
    "the image isn't showing the same as the settings" looks like from the
    empire designer, and it is why this class survived two live runs: the game
    logs `Could not find texture` once per row it actually draws, so the log is
    a sample of the rows somebody scrolled past, never the population.

    VANILLA IS THE CALIBRATION AND IT IS EXACT: 7,845 quoted portrait paths
    across 1,044 distinct files in its own asset_selectors, and every single one
    ends `.dds` -- no other extension appears in that position at all. So the
    floor is 0 and no scope is needed (rule 4, and rule 12: the question is
    asked of the whole directory rather than of the files a log named).

    ROWS THAT NAME ART NO SOURCE SHIPS STILL BELONG HERE. Appending `.dds` to
    `sth_humanoid_08_male_clothes_01` does not conjure the file -- it moves the
    row from "malformed" to "dangling", which is the other half's population and
    the honest place for it. See .docs/analysis/2026-08-16.md finding 1 and
    .docs/planning/ufp-run-remediation.md item 2.
    """
    d = BUILD / "gfx/portraits/asset_selectors"
    if not d.is_dir():
        return 0

    n = 0
    bad: dict[str, set[str]] = {}
    for f in sorted(d.rglob("*.txt")):
        n += 1
        rp = str(f.relative_to(BUILD))
        for path in _SELECTOR_TEXTURE_RE.findall(_strip_comments(_read(f))):
            if not path.lower().endswith(".dds"):
                bad.setdefault(rp, set()).add(path)
    if bad:
        total = sum(len(v) for v in bad.values())
        head = "; ".join(
            f"{k} → {', '.join(sorted(v)[:3])}{' …' if len(v) > 3 else ''}"
            for k, v in sorted(bad.items())[:3])
        warnings.append(
            f"gfx/portraits/asset_selectors: {total} quoted texture path(s) in "
            f"{len(bad)} file(s) do not end in `.dds` — {head}"
            f"{' …' if len(bad) > 3 else ''}. The engine cannot load the "
            f"texture and falls back silently, so the portrait draws in the "
            f"wrong clothes with nothing in error.log unless that exact row is "
            f"drawn. Vanilla writes 7,845 of these and every one ends `.dds`. "
            f"Fix with a `patches:` entry in vendor.yml. "
            f"See .docs/planning/ufp-run-remediation.md, item 2.")
    return n


def check_selector_texture_files() -> int:
    """A quoted texture path in an asset selector that resolves to no file.

    THE RESOLVES HALF of the question decision 83 split in two. The syntax half
    above is pure form -- a path with no `.dds` is malformed whatever is on
    disk. This half asks the harder thing, and it waited two weeks because its
    findings were believed to need a content call each. Most of them did not: of
    the 117 rows measured on 2026-08-24, 76 named art that IS in the tree -- under
    another directory, under one corrected character, or under the name the
    file's own male mirror already draws for that same trigger. The remaining 41
    were the real call and took one policy rather than thirteen decisions:
    repoint at the nearest surviving sibling in the same family, never delete.
    THE FLOOR IS 0 AND THE TREE IS AT IT.

    VANILLA COUNTS AS PRESENT, and getting that wrong is what produced the
    "196" this project carried for two weeks. STG is a total conversion but it
    does not replace vanilla's art: `gfx/models/portraits/` under /stellaris is
    still loaded, and 1,052 selector rows name it. Resolve against the built
    tree ALONE and the finding count is 1,169 rows -- nine in ten of them
    vanilla art that draws correctly. The resolution set is BUILD + GAME_DIR,
    the same pair check_texture_basenames uses for the same reason.

    NO SCOPE AND NO FLOOR IS NEEDED, because the check reads only our own
    directory. Vanilla's own selectors carry 7 unresolved rows / 5 textures --
    two `.dds.dds`, two that differ from the file only in case
    (`reptilian_slender_outfit_Admiral.dds`), and three genuinely absent
    paragon textures -- but those are vanilla's files, which this never opens.

    MATCHING IS EXACT, case included. A case-only difference is reported rather
    than resolved away: it is the one form of this defect whose behaviour the
    container cannot test, since the game runs on the host. Our tree currently
    has none -- the population is identical under either rule -- so the choice
    costs nothing today and fails loudly rather than silently if a copied
    vanilla row ever brings one in.

    A FINDING IS REPOINTED, NEVER DELETED. Deleting an entry from a
    `list = { }` shifts every index after it and changes what other species
    wear, which is why decision 83 accepted a duplicated entry rather than drop
    one. `"path" = { trigger }` rows are index-free, but a deletion there still
    changes what that trigger draws.

    See .docs/decisions/85-selector-textures-that-resolve.md.
    """
    d = BUILD / "gfx/portraits/asset_selectors"
    if not d.is_dir():
        return 0

    ack = _ack_list("selector_texture_ack")
    seen: dict[str, bool] = {}

    def resolves(path: str) -> bool:
        hit = seen.get(path)
        if hit is None:
            hit = (BUILD / path).is_file() or (GAME_DIR / path).is_file()
            seen[path] = hit
        return hit

    n = rows = 0
    missing: dict[str, set[str]] = {}
    for f in sorted(d.rglob("*.txt")):
        n += 1
        rp = str(f.relative_to(BUILD))
        for path in _SELECTOR_TEXTURE_RE.findall(_strip_comments(_read(f))):
            if path in ack or resolves(path):
                continue
            rows += 1
            missing.setdefault(path, set()).add(rp)

    if missing:
        head = "; ".join(
            f"{p} ({len(v)} file(s))"
            for p, v in sorted(missing.items(), key=lambda kv: -len(kv[1]))[:3])
        warnings.append(
            f"gfx/portraits/asset_selectors: {rows} row(s) name "
            f"{len(missing)} texture(s) that exist in neither the built tree "
            f"nor vanilla, across "
            f"{len(set().union(*missing.values()))} file(s) — {head}"
            f"{' …' if len(missing) > 3 else ''}. The engine falls back "
            f"silently, so the portrait draws in the wrong clothes with "
            f"nothing in error.log unless that exact row is drawn. Read the "
            f"row's trigger before pricing this as a content call: two thirds "
            f"of the last population were a directory typo, or had their "
            f"substitute named by the male mirror of the same trigger or by "
            f"the rows beside them. Repoint, never delete — a deletion shifts "
            f"every index after it. "
            f"See .docs/decisions/85-selector-textures-that-resolve.md.")
    return n


def check_portrait_clothes_selectors() -> int:
    """A prescripted empire whose portraits use a class-gated clothes selector
    must have a species class that selector actually names.

    STNH points most Trek portraits at `humanoid_master_male_clothes_01` /
    `..._female_clothes_01`, which choose the clothing texture by
    `is_species_class = X` and end with
    `default = ".../human_civilian/civ_human_male_clothes_01.dds"`. A class the
    selector never names is not a partial match -- it takes the default, and the
    species renders its own head and body above a human civilian jacket.

    That is how eight minor powers shipped with near-miss keys of STG's own
    invention (BENZ for STNH's BEN, DENO for DEN, TELL for TEL, ...) through
    every run to 2026-08-03. See
    .docs/decisions/20-minor-power-species-class-keys.md.

    Two reasons no existing check could see it. `check_prescripted_empires`
    asks about `common/portrait_sets/` and skips `playable = stg_never`, which
    is every minor power. `check_dangling_identifiers` saw the other side of the
    same fact -- BEN referenced and undeclared -- and it was acked as Phase 2
    content STG did not ship, which had stopped being true.

    It is also a SILENCE failure: the engine logs nothing for a selector that
    falls through, so error.log can never report this class at any volume.

    Only selectors that gate on `is_species_class` at all are considered, so a
    species with its own dedicated selector (Ferengi, Borg, Breen) is not a
    finding.
    """
    root = BUILD / "prescripted_countries"
    if not root.is_dir():
        return 0

    def _d1(body: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for m in re.finditer(r"^\t([\w'\-\.]+)\s*=\s*{", body, re.M):
            i, d = m.end() - 1, 0
            for j in range(i, len(body)):
                if body[j] == "{":
                    d += 1
                elif body[j] == "}":
                    d -= 1
                    if d == 0:
                        out[m.group(1)] = body[i:j + 1]
                        break
        return out

    def _d0(text: str, key: str):
        for m in re.finditer(rf"^{key}\s*=\s*{{", text, re.M):
            i, d = m.end() - 1, 0
            for j in range(i, len(text)):
                if text[j] == "{":
                    d += 1
                elif text[j] == "}":
                    d -= 1
                    if d == 0:
                        yield text[i:j + 1]
                        break

    # Vanilla first, so a mod file of the same name shadows it -- the engine's
    # own rule, and the same one check_prescripted_portraits follows.
    pfiles: dict[str, Path] = {}
    for d in (GAME_DIR / "gfx/portraits/portraits", BUILD / "gfx/portraits/portraits"):
        if d.is_dir():
            for p in sorted(d.glob("*.txt")):
                pfiles[p.name] = p

    portrait_sel: dict[str, str] = {}     # portrait -> its clothes_selector
    groups: dict[str, set[str]] = {}      # portrait_group -> member portraits
    for p in pfiles.values():
        t = _strip_comments(_read(p))
        for body in _d0(t, "portraits"):
            for name, b in _d1(body).items():
                m = re.search(r'clothes_selector\s*=\s*"([^"]+)"', b)
                if m:
                    portrait_sel[name] = m.group(1)
        for body in _d0(t, "portrait_groups"):
            for name, b in _d1(body).items():
                # A member is what an `add = { portraits = { ... } }` list names,
                # not every lowercase token in the block. `default = <portrait>`
                # names a fallback borrowed from another people -- STNH points
                # both kriosian and valtese at trill_female_01 -- and scraping it
                # as a member made this check report the master selector against
                # two groups that use a dedicated one for all ten of their own
                # portraits, prescribing decision 20's respelling as the fix for
                # species that already have a full wardrobe.
                mem: set[str] = set()
                for pm in re.finditer(r"portraits\s*=\s*{([^{}]*)}", b):
                    mem |= set(re.findall(r"[\w']+", pm.group(1)))
                if not mem:
                    dm = re.search(r"default\s*=\s*([\w']+)", b)
                    if dm:
                        mem = {dm.group(1)}
                groups[name] = mem

    # selector -> the species classes it gates on. Empty set == not class-gated.
    # `game_setup` is tracked separately: it is a scope of its own, it is the
    # only one the empire designer consults, and a selector can gate every other
    # scope by class while leaving that one a bare default.
    sel_classes: dict[str, set[str]] = {}
    sel_setup: dict[str, set[str]] = {}
    for d in (GAME_DIR / "gfx/portraits/asset_selectors",
              BUILD / "gfx/portraits/asset_selectors"):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.txt")):
            t = _strip_comments(_read(p))
            for m in re.finditer(r"^(\w+)\s*=\s*{", t, re.M):
                i, d2 = m.end() - 1, 0
                for j in range(i, len(t)):
                    if t[j] == "{":
                        d2 += 1
                    elif t[j] == "}":
                        d2 -= 1
                        if d2 == 0:
                            blk = t[i:j + 1]
                            sel_classes[m.group(1)] = set(
                                _SPECIES_CLASS_REF.findall(blk))
                            gs = _sub_block(blk, "game_setup")
                            sel_setup[m.group(1)] = set(
                                _SPECIES_CLASS_REF.findall(gs or ""))
                            break

    ack = _ack_list("portrait_clothes_ack")
    n = 0
    for f in sorted(root.glob("*.txt")):
        n += 1
        rp = f"prescripted_countries/{f.name}"
        for empire, body in _top_level_blocks(_strip_comments(_read(f))):
            if empire in ack:
                continue
            for kind in ("species", "secondary_species"):
                sb = _sub_block(body, kind)
                if sb is None:
                    continue
                cm = re.search(r'class\s*=\s*"?(\w+)"?', sb)
                pm = re.search(r'portrait\s*=\s*"?(\w+)"?', sb)
                if not cm or not pm:
                    continue
                cls, grp = cm.group(1), pm.group(1)
                members = (groups.get(grp) or {grp}) & set(portrait_sel)
                gating = {portrait_sel[m] for m in members
                          if sel_classes.get(portrait_sel[m])}
                missing = sorted(s for s in gating if cls not in sel_classes[s])
                if missing:
                    warnings.append(
                        f"{rp}: {empire} {kind} class '{cls}' is named by none of "
                        f"the class-gated clothes selector(s) its portrait group "
                        f"'{grp}' uses ({', '.join(missing)}), so the species "
                        f"falls through to that selector's `default` — usually "
                        f"human civilian clothes. Either the class should carry "
                        f"the source's own spelling (decision 20) or this people "
                        f"has no vendored clothing yet; ack it in vendor.yml "
                        f"under portrait_clothes_ack once looked at.")

                # The empire designer reads ONLY the `game_setup` scope, so a
                # class-gated selector whose game_setup is a bare default draws
                # every species it serves as that default. Playable empires
                # only — nothing else reaches the designer.
                if re.search(r"playable\s*=\s*stg_never", body):
                    continue
                blind = sorted(s for s in gating if cls not in sel_setup.get(s, set()))
                if blind:
                    warnings.append(
                        f"{rp}: {empire} {kind} class '{cls}' is gated by "
                        f"{', '.join(blind)} in every scope but `game_setup`, "
                        f"which the empire designer is the only thing to read. "
                        f"In the picker this species wears that scope's bare "
                        f"`default` — STNH's master pair defaults to human "
                        f"civilian clothes, which is how the Federation, "
                        f"Vulcan, Andorian, Bajoran and Trill empires were all "
                        f"drawn as humans through the 08-15 run. Gate "
                        f"`game_setup` too (decision 22), or ack it.")
    return n


_ENT_OPEN = re.compile(r"\bentity\s*=\s*\{")
_ENT_NAME = re.compile(r'\bname\s*=\s*"([^"]+)"')


def _norm_body(body: str) -> str:
    """An entity body with whitespace collapsed — two bodies differing only in
    indentation are not in conflict (decision 29)."""
    return re.sub(r"\s+", " ", body).strip()


def _entity_declarations(text: str):
    """(name, body) for each `entity = { … }`, the body BRACE-MATCHED to its end.

    Brace-counted rather than regexed. A nesting-limited regex can find the name
    -- it sits at the top of the block -- but its match ends AT the name, so
    `m.group(0)` is `entity = { name = "X"` and nothing more. Comparing that as
    the body makes every declaration of one name look identical to every other,
    which silently turned the duplicate check into one that could not fail: 0
    reported against a known-differing pair. Getting the name is not the same
    problem as getting the body.
    """
    for m in _ENT_OPEN.finditer(text):
        i, depth = m.end(), 1
        while i < len(text) and depth:
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        body = text[m.end():i - 1]
        n = _ENT_NAME.search(body)
        if n:
            yield n.group(1), body


def check_duplicate_entities() -> int:
    """One entity name declared by two files in the built tree.

    The engine logs `Duplicate of X added to entity system` and keeps one of the
    two. WHICH one is not recorded anywhere and does not show on disk, so a
    duplicate silently decides which art renders -- exactly the failure the
    2026-08-07 run had for `yridian_destroyer_entity`, where STNH's copy in
    gfx/models/ships/other/ points at `federation_01_corvette_frame_mesh` and the
    Walshicus shipset's copy at `yridian_destroyer_mesh`.

    THE RULE IS VANILLA'S OWN: across 8,409 entity declarations vanilla never
    declares one name twice, not once. So a second declaration inside one tree is
    something only the merge produces.

    Only duplicates WITHIN the built tree are visible here, and that is the useful
    scope rather than a limitation: a mod file redeclaring a vanilla name is how
    it overrides vanilla art without shadowing the path, which is deliberate and
    accounts for 558 of the 576 duplicate records in that run. Those never appear
    below, because vanilla's own file is not in the tree.

    EXCEPT when a source FORKS the vanilla file and carries its bodies in with
    it -- that is the same deliberate pair leaking back into scope, not a new
    defect class. A copy whose body is byte-identical to vanilla's own
    declaration of that name is therefore dropped before the comparison. That
    was four of this check's thirteen findings, all against PD - More Arcologies'
    fork of _planetary_entities.asset. Suppressed by CONTENT rather than by ack,
    so it reports again by itself the day either side stops matching vanilla.
    See .docs/decisions/53-duplicate-entity-triage.md.

    Reported as a warning, not an error, and modelled on check_key_conflicts:
    the finding is "confirm this is the winner you want", and only a live run or
    the source's intent settles it. Identical bodies are not a conflict
    (decision 29) and are not reported.

    See .docs/decisions/33-duplicate-entity-declarations.md.
    """
    art = BUILD / "gfx" / "models"
    if not art.is_dir():
        return 0

    ack = _ack_list("duplicate_entity_ack")
    seen: dict[str, list[tuple[str, str]]] = {}   # name -> [(relpath, body-ish)]
    n = 0
    for f in sorted(art.rglob("*.asset")):
        n += 1
        text = _strip_comments(_read(f))
        rp = str(f.relative_to(BUILD))
        for name, body in _entity_declarations(text):
            seen.setdefault(name, []).append((rp, _norm_body(body)))

    # What VANILLA declares, by name and normalised body.
    vanilla_bodies: dict[str, set[str]] = {}
    vart = GAME_DIR / "gfx" / "models"
    if vart.is_dir():
        for f in vart.rglob("*.asset"):
            for name, body in _entity_declarations(_strip_comments(_read(f))):
                vanilla_bodies.setdefault(name, set()).add(_norm_body(body))

    legacy = _legacy_sources()
    src_of = {p: (i or {}).get("source", "")
              for p, i in (_manifest().get("generated") or {}).items()}

    findings = 0
    for name in sorted(seen):
        places = seen[name]
        if name in ack:
            continue
        # A copy carrying vanilla's own body verbatim adds nothing the engine
        # would not have faced with vanilla's own file loaded -- PROVIDED the
        # other copy is a live 4.x mod's deliberate override. From a stale or
        # additive-only source it is a leftover from the game that source was
        # written against, which is the discriminator check_vanilla_regression
        # is already built on.
        vb = vanilla_bodies.get(name, set())
        if vb and not any(src_of.get(p, "") in legacy for p, b in places
                          if b not in vb):
            places = [(p, b) for p, b in places if b not in vb]
        files = sorted({p for p, _ in places})
        if len(files) < 2:
            continue
        # Bodies that differ only in whitespace are not in conflict (decision 29).
        shapes = {b for _, b in places}
        if len(shapes) < 2:
            continue
        findings += 1
        if findings > 12:
            continue
        warnings.append(
            f"{files[0]}: entity '{name}' is declared by {len(files)} files with "
            f"bodies that differ ({', '.join(files)}). The engine keeps one and "
            f"logs the other as a duplicate; which one it keeps is not recorded "
            f"anywhere, so this silently decides which art renders. Vanilla never "
            f"declares an entity name twice in 8,409 declarations. Remove the "
            f"conflict or ack it in vendor.yml under duplicate_entity_ack. "
            f"See .docs/decisions/33-duplicate-entity-declarations.md.")
    if findings > 12:
        warnings.append(f"... and {findings - 12} more duplicated entity name(s)")
    return n


_LOC_KEY_SHAPED = re.compile(r"^(PRESCRIPTED|NAME|EMPIRE_DESIGN|SPEC)_\w+$")


def _pdx_pairs(text: str):
    """(key, value) for the outermost level of every `Name = { … }` in `text`.

    A block-wide `^\\s*name\\s*=` regex finds `species.name` when an empire has
    no top-level `name` of its own, which is how a repair pass briefly renamed
    the Cravic Imperative to "Cravic". Depth has to be tracked, not assumed.
    """
    toks = re.findall(r'"(?:[^"\\]|\\.)*"|[{}=]|[^\s{}=]+',
                      re.sub(r"#[^\n]*", "", text))

    def body(i: int):
        out, n = [], len(toks)
        while i < n:
            t = toks[i]
            if t == "}":
                return out, i + 1
            if i + 1 < n and toks[i + 1] == "=":
                key = t.strip('"')
                if i + 2 < n and toks[i + 2] == "{":
                    sub, i = body(i + 3)
                    out.append((key, sub))
                else:
                    out.append((key, toks[i + 2].strip('"') if i + 2 < n else ""))
                    i += 3
                continue
            i += 1
        return out, i

    i, n = 0, len(toks)
    while i < n:
        if i + 2 < n and toks[i + 1] == "=" and toks[i + 2] == "{":
            name = toks[i].strip('"')
            pairs, i = body(i + 3)
            yield name, pairs
        else:
            i += 1


def check_prescripted_loc() -> int:
    """STG's prescripted loc against the source empire it was converted from.

    Two failure modes, both SILENT — loc that resolves to the wrong string still
    resolves, so no `error.log` line will ever mention either, and every other
    check here passes.

    1. **A value that is still a loc KEY.** `STG_species_adjective_…:0
       "PRESCRIPTED_species_adjective_VulcanHighCommand"` draws that key on
       screen. 16 of these shipped.
    2. **A value that is a TRUNCATION of the source's.** 78 of the 79 minor
       powers had one: `NAME_elaurian_auditorium` "El-Aurian Auditorium" shipped
       as `-Aurian Auditorium`, `NAME_Confederation_of_Earth` as `of Earth`,
       `NAME_hurq_stagnancy` "Hur'Q Stagnancy" as `'Q Stagnancy`. The leading
       token was dropped without separator handling, which is why the survivors
       read as debris.

    Truncation is asked as "ours is a proper substring of the source's, or the
    source's with spaces removed" rather than by re-deriving the name. That is
    deliberately narrow: it cannot fire on a name STG shortened ON PURPOSE
    unless the shortening also happens to be a substring, and it says nothing
    about the six fields where STNH's own wording and ours simply differ
    (`Kessoks` vs `Kessok`) — those are taste, were left alone by the repair,
    and a check that reported them would be reporting a preference.

    THE TWO HALVES HAVE DIFFERENT SCOPES, and that is a calibration result
    rather than an oversight — see .docs/decisions/51-prescripted-loc-scope.md.

    * **Truncation stays on `stg_minor_powers.txt` alone.** It is the only one
      of the four GENERATED from the source, and truncation is a generator
      failure. Asking it of the three hand-authored files needs an STG-empire ->
      STNH-empire mapping that does not exist, because those 22 diverge from
      STNH deliberately (`Bolian Union` vs STNH's `Bolian League`, `Trill
      Symbiosis` vs `Trill Administration`, `Confederacy of Vulcan` vs `Vulcan
      High Command`). Swept once against all 111 STNH empires: **0 real
      findings and 1 false positive** — our canonical `United Federation of
      Planets` reads as a substring of STNH's alt-timeline `United Federation
      of Planets (2300s)`. A permanent ack for a file with no generator behind
      it is the ack-rot .docs/validation/acks.md warns about, so the scope stays put.
    * **The leaked-key half covers ALL FOUR**, because it needs no source
      mapping at all — it asks only whether our own value is still shaped like
      somebody's loc key, which is wrong no matter who wrote the file. It costs
      nothing and currently finds nothing outside the minors.
    """
    pres = REPO / "src" / "prescripted_countries" / "stg_minor_powers.txt"
    locf = (REPO / "src" / "localisation" / "english"
            / "stg_minor_powers_l_english.yml")
    if not pres.is_file() or not locf.is_file():
        return 0

    manifest = REPO / "vendor.yml"
    if not manifest.is_file():
        return 0
    mtext = manifest.read_text(encoding="utf-8-sig")
    m = re.search(r'^\s*-\s*id:\s*"?(\d+)"?\s*\n\s*name:\s*"Star Trek: New Horizons"',
                  mtext, re.M)
    if not m:
        return 0
    m2 = re.search(r"^\s*source_root:\s*(\S+)\s*$", mtext, re.M)
    root = Path((m2.group(1).strip("\"'") if m2 else ".source"))
    if not root.is_absolute():
        root = REPO / root
    stnh = root / m.group(1)
    if not stnh.is_dir():
        return 0

    # Source localisation, first definition wins — the same rule the loader uses.
    sloc: dict[str, str] = {}
    for f in sorted((root).glob("*/localisation/english/*.yml")):
        for mm in re.finditer(r'^\s*([\w\'\.]+):\d*\s*"((?:[^"\\]|\\.)*)"',
                              _read(f), re.M):
            sloc.setdefault(mm.group(1), mm.group(2))

    def clean(s: str) -> str:
        s = re.sub(r"£[^£]*£", "", s)
        s = re.sub(r"§.", "", s)
        return " ".join(s.split())

    def resolve(tok: str | None) -> str | None:
        """Only a loc-KEY-shaped token is a key. `SKR` is a ship prefix that also
        happens to name a species class in loc, and treating it as a key turned
        three prefixes into "Humanoid"."""
        if not tok:
            return None
        if _LOC_KEY_SHAPED.match(tok):
            return clean(sloc[tok]) if tok in sloc else None
        return clean(tok)

    emp: dict[str, list] = {}
    for f in sorted((stnh / "prescripted_countries").glob("*.txt")):
        for name, pairs in _pdx_pairs(_read(f)):
            emp.setdefault(name, pairs)
    flat = {k.lower().replace("_", ""): k for k in emp}

    def get(pairs, key):
        for k, v in pairs:
            if k == key and isinstance(v, str):
                return v
        return None

    ours = dict(re.findall(r'^\s*(STG_\w+):0\s*"([^"]*)"', _read(locf), re.M))
    ack = _ack_list("prescripted_loc_ack")

    n = 0
    for mm in re.finditer(r"^stg_minor_(\w+)", _read(pres), re.M):
        slug = mm.group(1)
        n += 1
        key = f"STG_EMPIRE_minor_{slug}"
        val = ours.get(key)
        if val is None or key in ack:
            continue
        src_key = flat.get(slug.replace("_", ""))
        want = resolve(get(emp[src_key], "name")) if src_key else None
        if want and val != want and (val in want
                                     or val.replace(" ", "") == want.replace(" ", "")):
            warnings.append(
                f"localisation/english/{locf.name}: {key} is \"{val}\", a "
                f"truncation of the source empire's \"{want}\". The leading "
                f"token was dropped when this file was generated. Nothing logs "
                f"this — loc that resolves to the wrong string still resolves. "
                f"Ack in vendor.yml under prescripted_loc_ack if the short form "
                f"is deliberate. See "
                f".docs/decisions/47-minor-power-names-truncated.md.")

    # The leaked-key half asks nothing of the source, so it covers all four
    # prescripted loc files rather than just the generated one — decision 51.
    leaked: list[tuple[str, str, str]] = []
    for stem in ("stg_minor_powers", "stg_major_powers",
                 "stg_frontier_powers", "stg_quadrant_powers"):
        lf = REPO / "src" / "localisation" / "english" / f"{stem}_l_english.yml"
        if not lf.is_file():
            continue
        vals = dict(re.findall(r'^\s*(STG_\w+):0\s*"([^"]*)"', _read(lf), re.M))
        if stem != "stg_minor_powers":  # the minors are already counted above
            n += sum(1 for k in vals if k.startswith("STG_EMPIRE_"))
        leaked += [(lf.name, k, v) for k, v in sorted(vals.items())
                   if _LOC_KEY_SHAPED.match(v) and k not in ack]

    for fn, k, v in leaked[:6]:
        warnings.append(
            f"localisation/english/{fn}: {k} is \"{v}\" — a "
            f"localisation KEY, drawn on screen verbatim. The generator failed "
            f"to resolve it against the source. "
            f"See .docs/decisions/47-minor-power-names-truncated.md.")
    if len(leaked) > 6:
        warnings.append(f"... and {len(leaked) - 6} more unresolved loc key(s)")
    return n


def check_duplicate_textures() -> int:
    """One texture BASENAME carried by two files in the built tree.

    A `.mesh` names its textures by bare filename inside the binary, with no
    directory, so the engine keeps a single global filename -> texture map. Two
    files sharing a basename mean one wins for every mesh that asks, and the
    loser's ship renders wearing the winner's skin. The engine says
    `Duplicate texture 'X' found (current path A, previous path B)` and then
    carries on -- 143 records in the 2026-08-07 run, 137 of them
    stnc_shipset_shared/textures against the per-ship folders it was split out
    of.

    THE RULE IS VANILLA'S OWN, and it is close to absolute: across 7,711
    distinct texture basenames under gfx/models vanilla repeats exactly ONE
    (cybernetics_01/synthetics_01's military_station_normal). The built tree
    repeats 142. That ratio is why this is a warning worth reading rather than
    noise to be filtered.

    Scope is duplicates WITHIN the built tree, for the same reason
    check_duplicate_entities uses it: a mod file reusing a vanilla basename in
    the SAME relative directory is an ordinary path shadow and deliberate (142
    of those here), and one in a different directory is the cross-collision this
    would report -- vanilla's tree is not searched because its own files are not
    in the merge twice.

    Content is compared, not just names (decision 29): byte-identical copies of
    one texture in two folders cost disk and nothing else, and are not reported.
    All 142 in that run differed.

    See .docs/decisions/46-coalition-of-hope-takes-vul.md for the run this came
    from and .docs/decisions/42-event-picture-geometry.md for the sibling failure
    where the path resolves and only the pixels are wrong.
    """
    art = BUILD / "gfx" / "models"
    if not art.is_dir():
        return 0

    # An ack entry is a DIRECTORY, not a basename: the reviewed cases are whole
    # shared-texture libraries meeting each other (.docs/architecture/conflict-register.md), and listing 137
    # basenames would be a list nobody rereads that goes stale the moment a
    # shipset is re-cut. Acking one side silences every pair it is in, so a
    # collision between two folders neither side has reviewed still reports.
    ack = _ack_list("duplicate_texture_ack")
    seen: dict[str, list[Path]] = {}
    n = 0
    for f in sorted(art.rglob("*.dds")):
        n += 1
        seen.setdefault(f.name.lower(), []).append(f)

    pairs: dict[tuple[str, ...], list[str]] = {}
    for base in sorted(seen):
        files = seen[base]
        if len(files) < 2 or base in ack:
            continue
        try:
            if len({hashlib.sha256(p.read_bytes()).digest() for p in files}) < 2:
                continue
        except OSError:
            continue
        dirs = tuple(sorted({str(p.parent.relative_to(BUILD)) for p in files}))
        if any(d in ack for d in dirs):
            continue
        pairs.setdefault(dirs, []).append(base)

    # Grouped by directory pair: 142 findings are ~6 real decisions, and one
    # line per file would bury every other warning in the run.
    for i, dirs in enumerate(sorted(pairs, key=lambda d: (-len(pairs[d]), d))):
        bases = sorted(pairs[dirs])
        tail = (" A mesh names its textures by bare filename, so the engine keeps "
                "one globally and the other folder's ships render with the wrong "
                "skin. Vanilla repeats 1 basename in 7,711. Rename one side, or ack "
                "either directory in vendor.yml under duplicate_texture_ack." if i == 0
                else "")
        warnings.append(
            f"{dirs[0]}: {len(bases)} texture basename(s) also carried, with "
            f"different content, by {', '.join(dirs[1:])} "
            f"(e.g. {', '.join(bases[:3])}).{tail}")
    return n


_AT_DECL = re.compile(r"^[ \t]*@(\w+)\s*=", re.M)
_AT_REF = re.compile(r"@(\w+)")


def check_asset_variables() -> int:
    """`@name` references in built art with no declaration the engine can reach.

    The engine reports `Malformed token: @name` and the property it was the value
    of is lost -- 137 records in the 2026-08-07 live run, one per entity copied
    into zz_stg_shipsets.asset by tools/gen_shipsets.py, every one of them a ship
    with no scale. Nothing was checking this, and the same defect had already been
    hand-patched once in a vendored file (@plasmasmallplasmuzzle in ASB Ironman's
    _ballistics_entities_ap.asset, see .docs/provenance.md).

    THE SCOPE IS NOT FILE-LOCAL, and assuming it was would have reported 96
    references across 18 vanilla files as broken. `@large_trail_L` is referenced
    by 17 vanilla `.asset` files that all leave their own copy commented out,
    because common/scripted_variables/03_scripted_variables_ships.txt declares it
    globally. So the resolvable set is the file's own declarations PLUS
    common/scripted_variables/ -- and vanilla's own 1,788 art files score exactly
    0 under that rule, which is what says the rule is right.

    See .docs/decisions/31-asset-local-variables.md.
    """
    art = BUILD / "gfx"
    if not art.is_dir():
        return 0

    scoped = set()
    for d in (GAME_DIR / "common/scripted_variables",
              BUILD / "common/scripted_variables",
              REPO / "src/common/scripted_variables"):
        if d.is_dir():
            for f in d.rglob("*.txt"):
                scoped |= set(_AT_DECL.findall(_strip_comments(_read(f))))

    ack = _ack_list("asset_variable_ack")
    found: dict[str, tuple[str, int]] = {}   # name -> (example file, file count)
    n = 0
    for f in sorted(art.rglob("*")):
        if f.suffix not in (".asset", ".gfx") or not f.is_file():
            continue
        n += 1
        text = _strip_comments(_read(f))
        local = set(_AT_DECL.findall(text))
        for name in set(_AT_REF.findall(text)) - local - scoped - ack:
            where, count = found.get(name, (str(f.relative_to(BUILD)), 0))
            found[name] = (where, count + 1)

    for name, (where, count) in sorted(found.items(), key=lambda kv: -kv[1][1])[:12]:
        errors.append(
            f"{where}: '@{name}' is referenced but declared neither in that file "
            f"nor in common/scripted_variables/ ({count} file(s)). The engine "
            f"reports `Malformed token` and drops the value it was assigned to. "
            f"See .docs/decisions/31-asset-local-variables.md.")
    if len(found) > 12:
        errors.append(f"... and {len(found) - 12} more unresolved @variable(s)")
    return n


# The two directories where a texture's pixel dimensions are load-bearing AND
# not owned by whoever swaps the art. Each carries its own calibration in
# check_shadowed_texture_geometry(); adding a third means measuring it first.
_GEOMETRY_DIRS = ("gfx/event_pictures", "gfx/portraits/city_sets")

# Per directory, the families vanilla is uniform enough about that a file
# shadowing NO vanilla path can still be checked against one. Patterns are globs
# against the path RELATIVE TO THE DIRECTORY, ordered, first match wins -- which
# is what lets one directory hold two families whose globs overlap.
#
# city_sets qualifies twice: vanilla is 266/271 at 800x400 on city layers and
# 91/91 at 952x340 on rooms. gfx/event_pictures also qualifies twice, and used
# to be listed as qualifying not at all: "580 of its 639 are 450x150 and the
# other 59 are a genuine second size" is what one glob over the whole directory
# measures, and the 59 are the origins/ subdirectory -- 59 of 59 at 220x115.
# Split, both families are 100% uniform.
# See .docs/decisions/74-event-picture-families.md.
#
# Mirrors `target: family` in vendor.yml; the two must name the same families in
# the same order, or the build fixes what the check does not ask about.
_GEOMETRY_FAMILIES = {
    "gfx/event_pictures": ("origins/*.dds", "*.dds"),
    "gfx/portraits/city_sets": ("*_city_l*.dds", "*_room.dds"),
}
_GEOMETRY_UNIFORMITY = 0.90


def _geometry_family_of(rel_in_dir: str, patterns: tuple[str, ...]) -> str | None:
    """The first pattern that claims this path, or None. See _GEOMETRY_FAMILIES."""
    return next((p for p in patterns if _fnmatch(rel_in_dir, p)), None)


def _vanilla_family_sizes(directory: str, patterns: tuple[str, ...]):
    """Per family, (every size vanilla uses for it, its modal size or None).

    Both halves matter. The modal is the target; the full set is what keeps
    vanilla's own vocabulary from reading as a defect -- it ships
    ai_01_city_l01..l05 at 4x4 to mean "this layer is empty", and Planetary
    Diversity uses the same idiom for pd_tree_of_life_01.
    """
    hists = {p: collections.Counter() for p in patterns}
    art = GAME_DIR / directory
    if art.is_dir():
        for f in art.rglob("*.dds"):
            owner = _geometry_family_of(f.relative_to(art).as_posix(), patterns)
            if owner is None:
                continue
            dims = _dds_dimensions(f)
            if dims:
                hists[owner][dims] += 1
    out = {}
    for pattern, hist in hists.items():
        if not hist:
            out[pattern] = (set(), None)
            continue
        (top, count), = hist.most_common(1)
        out[pattern] = (set(hist),
                        top if count / sum(hist.values()) >= _GEOMETRY_UNIFORMITY
                        else None)
    return out


def _dds_dimensions(path: Path) -> tuple[int, int] | None:
    """(width, height) from a DDS header, or None if it isn't a DDS."""
    try:
        with path.open("rb") as fh:
            head = fh.read(20)
    except OSError:
        return None
    if len(head) < 20 or head[:4] != b"DDS ":
        return None
    height, width = struct.unpack("<II", head[12:20])
    return width, height


def check_shadowed_texture_geometry() -> int:
    """Vendored art that shadows a vanilla texture path at different dimensions.

    A whole class of defect that every other check here is blind to, because
    nothing dangles: the file exists, the sprite that declares it resolves, the
    window that draws it resolves. Only the PIXELS changed, and the layout that
    was cut for the old ones is still doing the drawing. STNH replaced 569 of
    vanilla's 639 event pictures with 620x264 art; vanilla's sprites and UIOD's
    eventwindow.gui stayed, and `scale = 1.5` -- which is cut for 450x150 --
    rendered them 930x396 inside a 693x239 frame. `make validate` said ok
    throughout. See .docs/decisions/42-event-picture-geometry.md.

    THE SCOPE IS A CALIBRATION RESULT, NOT A CONVENIENCE FILTER. Over the whole
    tree the same rule reports 865 findings and almost all of them are by
    design: gfx/loadingscreens is 20 for 20 a deliberate 2x HD upscale,
    gfx/models is UV-mapped and resolution-independent, and 92 of the 99 under
    gfx/interface are UIOD resizing vanilla's own UI art while shipping the
    .gui that lays it out -- a texture and its layout changing together is a
    reskin, not a defect. gfx/event_pictures is the one directory where the
    dimensions are load-bearing and NOT owned by whoever swaps the art: vanilla
    pins 220 of those sprites to hardcoded upper_left/lower_right rects in
    450x150 space, and the window applies a fixed scale. 569 true findings
    against 0 vanilla false positives, 0 after the re-cut.

    Widening this to another directory means making that case for it, which is
    why the scope is a constant with the ratio written next to it.

    gfx/portraits/city_sets IS THAT CASE, MADE 2026-08-08 and measured the same
    way. The planet view composites six city layers by exact pixel position on
    a fixed canvas: vanilla ships all 266 of its `*_city_l0N.dds` at 800x400
    with each layer's content at its own offset inside it, and all 91 of its
    `*_room.dds` at 952x340. STNH honours the room canvas -- 316 of 324 -- and
    not the city one, because its own interface/, which STG never vendors, was
    cut for 560x280. 153 findings against 0 vanilla false positives, 0 after
    the re-cut, and the live symptom was the city art sitting low and small on
    every planet with the backdrop behind it correct. The backdrop was right
    because `additive_only` makes STNH lose all 121 environments/ paths to the
    mods that own them, so only the half nobody else claims was ever wrong.
    See .docs/decisions/58-city-set-geometry.md.

    GFX_EVENT_PICTURES BECAME THAT CASE TOO ON 2026-08-09, and it had been read
    as failing the test by a measurement that asked one glob of two families.
    "580 of 639 at 450x150, the other 59 a genuine second size" is true of the
    directory and false of both families in it: the 59 are the origins/
    subdirectory, 59 of 59 at 220x115, and the top level is 580 of 580. So the
    865 STNH pictures that shadow NO vanilla path -- every picture a Trek event
    would want -- had no question asked of them at all, at 620x264 against a
    family of 450x150. Same blindness as the city sets, in the very directory
    decision 42 was written about.
    See .docs/decisions/74-event-picture-families.md.
    """
    ack = _ack_list("texture_geometry_ack")
    found: list[tuple[str, tuple[int, int], tuple[int, int]]] = []
    n = 0
    for d in _GEOMETRY_DIRS:
        art = BUILD / d
        if not art.is_dir():
            continue
        patterns = _GEOMETRY_FAMILIES.get(d, ())
        families = _vanilla_family_sizes(d, patterns)
        for f in sorted(art.rglob("*.dds")):
            rel = f.relative_to(BUILD).as_posix()
            if rel in ack:
                continue
            have = _dds_dimensions(f)
            if not have:
                continue
            vanilla = GAME_DIR / rel
            if vanilla.is_file():
                n += 1
                want = _dds_dimensions(vanilla)
                if want and want != have:
                    found.append((rel, want, have))
                continue
            # SHADOWING NOTHING IS NOT THE SAME AS BEING FINE. A file at a path
            # vanilla does not ship is still drawn into a frame vanilla sized,
            # if it belongs to a family vanilla is uniform about -- which is
            # how STNH's six own Trek city prefixes stayed at 70% through two
            # live runs while this check reported 0. Same question, asked of
            # the family instead of the file. See decision 58.
            pat = _geometry_family_of(f.relative_to(art).as_posix(), patterns)
            if pat is None:
                continue
            sizes, modal = families[pat]
            if modal is None:
                continue
            n += 1
            if have != modal and have not in sizes:
                found.append((rel, modal, have))

    for rel, want, have in found[:8]:
        errors.append(
            f"{rel}: shadows vanilla's texture at {have[0]}x{have[1]} where "
            f"vanilla ships {want[0]}x{want[1]}. Nothing dangles -- the sprite "
            f"and the window still resolve -- but they are cut for vanilla's "
            f"pixels, so the picture draws at the wrong size. Re-cut it with "
            f"`resample_to_vanilla:` in vendor.yml, or ack it under "
            f"texture_geometry_ack. See "
            f".docs/decisions/42-event-picture-geometry.md.")
    if len(found) > 8:
        errors.append(f"... and {len(found) - 8} more re-dimensioned texture(s)")
    return n


def check_music_declarations() -> int:
    """A music track in the tree that nothing declares, and the reverse.

    `music/` holds two halves that must meet: a `.asset` maps a track NAME to an
    `.ogg` FILE, and a `.txt` puts that name in the playlist with `song = { }`.
    Ship the .ogg alone and it is inert -- no loader ever opens it, and nothing
    is logged, because a file nobody asks for is not an error. STNH ships
    Anthem_of_the_United_Federation_of_Planets.ogg and declares it in neither
    half, so it sat unheard through every live run
    (.docs/decisions/55-federation-anthem.md).

    THE RULE IS VANILLA'S OWN AND IT IS EXACT: 30 .ogg files, 30 named by a music
    declaration, and 0 declarations naming a file that is not there. Both
    directions score zero, so both are checked.

    A declaration may name a file vanilla ships rather than one of ours -- STNH's
    songs.asset lists 17 of vanilla's tracks that way -- so the file must resolve
    against the built tree OR /stellaris, not the built tree alone.

    NOT checked: that every music declaration has a `song` entry to play it.
    Four of STNH's spare maintheme aliases have none, and whether the main menu
    picks its theme by song entry or by declaration name is not something the
    files settle -- vanilla's one piece of evidence is `chance = { factor = 0 }`
    on a DLC main theme, which says the two are separable without saying how.
    Asserting a rule there would be guessing at the engine, which is the failure
    decision 27 records.
    """
    d = BUILD / "music"
    if not d.is_dir():
        return 0

    named: set[str] = set()
    for f in sorted(d.glob("*.asset")):
        named |= set(re.findall(r'file\s*=\s*"([^"]+)"', _strip_comments(_read(f))))

    oggs = {p.name for p in d.glob("*.ogg")}
    for orphan in sorted(oggs - named):
        warnings.append(
            f"music/{orphan}: no `music = {{ }}` declaration names this file, so "
            f"nothing can play it and nothing will ever log that. Vanilla names "
            f"all 30 of its own. Declare it in src/music/ (name + file), and a "
            f"`song = {{ }}` beside it to put it in the rotation. "
            f"See .docs/decisions/55-federation-anthem.md.")

    for f in sorted(named):
        if not (d / f).is_file() and not (GAME_DIR / "music" / f).is_file():
            warnings.append(
                f"music/: a declaration names '{f}', which is in neither the "
                f"built tree nor vanilla's music/. The track resolves to nothing "
                f"and the entry is dead. Vanilla has 0 of these.")

    # ── A THIRD DIRECTION: what the music player DRAWS ───────────────────────
    #
    # The player shows the declaration NAME, looked up as a loc key -- vanilla
    # writes `name = "cradleofthegalaxy"` and `cradleofthegalaxy:0 "Cradle of
    # the Galaxy"` beside it. A name with no key is drawn verbatim and logs
    # NOTHING, because a name that resolves to itself still resolves: the same
    # silence decision 47 found in the prescripted loc, in a different database.
    # Decision 61 measured it: 16 of the playlist's 22 entries THEN listed as
    # `newhorizonssong1`, `maintheme7` and `stg_ufp_anthem` through every live
    # run. Both halves of that figure have since moved -- decision 65 deduped
    # the rotation to 27 entries (17 ours + 10 vanilla's) and every one is
    # keyed. Read the live count off this check's own summary line, not here.
    #
    # A NAME CONTAINING A SPACE IS EXEMPT, and that is not a loophole. Extended
    # Soundtrack writes `name = "Battle For Supremacy"` -- the title itself as
    # the key -- and drawing it verbatim is exactly right. The rule separates a
    # name that reads as a key from one that reads as a title, which is the
    # question a player is actually asking.
    #
    # CALIBRATION: 0 findings over our tree after the repair, and vanilla's own
    # music/ scores 6 of 30 -- `towardsutopianovaflare`, `syntheticgod`,
    # `maintheme3` and three more that Paradox never gave a key. We ship none of
    # those files, so vanilla's rate is a floor to know about rather than a
    # false-positive source. See .docs/decisions/61-music-player-track-names.md.
    # Resolve against the MERGED loc -- the built tree plus vanilla's -- because
    # a track's title may come from a vendored mod as easily as from src/.
    loc_keys: set[str] = set()
    for lp in list((BUILD / "localisation").rglob("*.yml")) + \
            list((GAME_DIR / "localisation" / "english").rglob("*.yml")):
        for line in lp.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = re.match(r"\s*([A-Za-z0-9_.\-]+):\d*\s+\"", line)
            if m:
                loc_keys.add(m.group(1))

    for f in sorted(d.glob("*.txt")):
        text = _strip_comments(_read(f))
        for sm in re.finditer(r"(?m)^\s*song\s*=\s*\{", text):
            i, depth = sm.end(), 1
            while depth and i < len(text):
                depth += (text[i] == "{") - (text[i] == "}")
                i += 1
            body = text[sm.end():i - 1]
            m = re.search(r'name\s*=\s*(?:"([^"]*)"|([^\s"}]+))', body)
            if not m:
                continue
            name = m.group(1) if m.group(1) is not None else m.group(2)
            if " " in name or name in loc_keys:
                continue
            warnings.append(
                f"music/{f.name}: the playlist entry '{name}' has no "
                f"localisation key, so the music player draws the key itself. "
                f"Nothing is logged -- a name that resolves to itself still "
                f"resolves. Add it to "
                f"src/localisation/english/stg_music_l_english.yml. "
                f"See .docs/decisions/61-music-player-track-names.md.")

    return len(oggs)


# The one file whose anomaly events are all category outcomes, so an event no
# category names is dead there and only there. See check_anomalies.
_ANOMALY_OWN_EVENTS = "stg_anomaly_events.txt"

# The same shape one database over: the one file whose archaeology events are
# all site stage outcomes. See check_archaeology.
_ARCSITE_OWN_EVENTS = "stg_arcsite_events.txt"

# And a third: the one file whose events are all reached from an on_action, with
# no chains. See check_story_events.
_STORY_OWN_EVENTS = "stg_story_events.txt"


def _is_event_block(kind: str) -> bool:
    """Is this top-level key an event declaration?

    `country_event`, `ship_event`, `planet_event` ... and the BARE `event`,
    which is legal and which vanilla writes in 40-odd of its own files and Real
    Space writes in all of its. Missing the bare form does not make an event
    dangle -- it makes a check believe one does, which is worse: the first run
    of check_story_events reported 26 hooks in Real Space, Planetary Diversity,
    Ariphaos and System Scale as firing events nobody declares, and every one of
    those events was sitting in the tree under `event = {`.
    """
    return kind == "event" or kind.endswith("_event")


@functools.lru_cache(maxsize=4)
def _script_tokens_outside(directory: str) -> frozenset[str]:
    """Every identifier written in script anywhere except one database's own directory.

    The second half of a reachability question. "Nothing places this at random"
    is only half of "nothing places this": the other route is a script that
    names the key outright, and vanilla uses it constantly -- 74 of its 123
    archaeological site types carry no positive `weight` and every one of them
    is created by an initialiser, an event or a parameterised effect instead.
    Ask the weight question alone and the check reports 74 false findings; ask
    it against this sweep and vanilla's floor is 0.

    IT IS A TOKEN SWEEP, NOT A REFERENCE PARSE, and deliberately so. The zroni
    chain is created by `create_archaeological_site = $DIGSITE$` inside an
    inline script, with `DIGSITE = zroni_digsite_2` passed from an event four
    files away -- no parser that follows one effect name finds that, and a mod
    can invent a route vanilla has not used. The sweep over-accepts by
    construction, which is the right direction for a check whose finding is
    "this content can never appear": a key nobody has typed anywhere is a claim
    that holds however the engine reaches it.

    The database's own directory is excluded, since a definition is not a
    reference (check-design rule 3). Localisation is excluded with it -- every
    key has a loc entry by construction, so including .yml would make the
    question vacuous.
    """
    tokens: set[str] = set()
    for root in (BUILD, GAME_DIR):
        for f in root.rglob("*.txt"):
            if f.parent.name == directory:
                continue
            tokens |= set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", _read(f)))
    return frozenset(tokens)


def _no_positive(body: str, field: str) -> bool:
    """Is `field` present-and-zero, or absent, where absent means zero?

    `weight` on a site and `spawn_chance` on an anomaly category are the same
    field twice: a scriptable value that defaults to 0, written either bare
    (`weight = 0`) or as a block whose `base` and `add` entries sum the chance
    up from nothing. A `factor` does NOT count -- it multiplies, and vanilla
    writes `base = 0` with a `factor` under it, which is still zero.

    TRUE ONLY WHEN THE ZERO IS ESTABLISHED. A scripted value, an `@variable` or
    a block shape this does not recognise returns False and is not reported: a
    reachability check that guesses is worse than one that misses, because its
    finding is "delete this or wire it up".
    """
    m = re.search(rf"(?m)^\s*{field}\s*=\s*(\{{|[^\s{{]+)", body)
    if not m:
        return True
    if m.group(1) != "{":
        try:
            return float(m.group(1)) <= 0
        except ValueError:
            return False
    block = _balanced(body, body.index("{", m.start()))
    nums = re.findall(r"(?m)^\s*(?:base|add)\s*=\s*(-?[\d.]+)", block)
    if not nums:
        return False        # a shape this cannot read is not an established zero
    return not any(float(n) > 0 for n in nums)


def _merged_loc_keys() -> set[str]:
    """Every localisation key the game will have loaded: the tree's and vanilla's."""
    keys: set[str] = set()
    for lp in list((BUILD / "localisation").rglob("*.yml")) + \
            list((GAME_DIR / "localisation" / "english").rglob("*.yml")):
        for line in lp.read_text(encoding="utf-8-sig",
                                 errors="replace").splitlines():
            m = re.match(r"\s*([A-Za-z0-9_.\-]+):\d*\s+\"", line)
            if m:
                keys.add(m.group(1))
    return keys


def check_anomalies() -> int:
    """An anomaly whose category, event, picture or loc key does not meet.

    An anomaly is FOUR files that have to agree, and none of them dangles when
    they do not: common/anomalies/ names an event id, events/ declares it,
    interface/*.gfx declares the picture, and localisation/ carries the category
    name, the category description, the event title, the event description and
    every option button. Get any one wrong and the game logs nothing useful --
    a missing outcome event means the anomaly resolves to a blank popup, and a
    missing loc key means the raw key is drawn on screen, which is decision 47's
    silence in a fifth database.

    VANILLA IS THE CALIBRATION AND IT IS NEARLY PERFECT, measured over its 327
    categories and the 310 ship_events in events/anomaly_events_*.txt:

        category picture declared          0 findings
        category name loc key              0
        category desc loc key              0
        event title / desc / option loc    0
        event picture declared             0
        category names an event that exists  1  -- UBUME_BABY_CAT points at
                                                anomaly.6791, which Paradox
                                                does not ship. A floor of one
                                                known instance, not zero.

    So all six questions are asked of every anomaly in the built tree.

    THE SEVENTH IS `spawn_chance`, AND IT IS THE ONE THE SIX ABOVE CANNOT SEE.
    `spawn_chance` defaults to `base = 0`, so a category with none, or with one
    that never adds to it, is complete, correct, validating clean and never
    rolled -- decision 76's `weight = 0` and decision 62's undeclared graphical
    culture in an eighth database, and the defect class this whole family of
    checks exists for. It is asked with the reachability filter
    _script_tokens_outside describes, because a category can also be placed by
    an effect that names it:

        no positive spawn_chance             49 of vanilla's 327
        ... and named nowhere else in script  3 -- ANCREL_MECHANO_CAT,
                                             VULTAUMAR and YUHTAAN, which appear
                                             only in their own file and in
                                             localisation. A floor of three
                                             known instances, not zero.

    See .docs/decisions/79-reachability-checks.md.

    THE SEVENTH QUESTION HAS A SCOPE, because its floor is nothing like zero:
    "an anomaly event no category names" scores 114 of vanilla's 310, since
    vanilla chains events off each other and off on_actions this check does not
    read. Over src/events/stg_anomaly_events.txt the shape is different by
    construction -- every event there is a category outcome and there are no
    chains -- so the question is exact there and meaningless everywhere else.
    A check can want two scopes at once: .docs/validation/check-design.md rule 11
    and .docs/decisions/51-prescripted-loc-scope.md.

    See .docs/decisions/75-trek-anomalies.md.
    """
    cat_dir = BUILD / "common" / "anomalies"
    if not cat_dir.is_dir():
        return 0

    # Event ids resolve against the merged tree AND vanilla: a category may name
    # a vanilla event as easily as one of ours.
    event_ids: set[str] = set()
    events_seen: list[tuple[str, str, str]] = []   # (file, id, body)
    for f in sorted(list((BUILD / "events").glob("*.txt")) +
                    list((GAME_DIR / "events").glob("*.txt"))):
        text = _strip_comments(_read(f))
        for kind, body in _top_level_blocks(text):
            if not _is_event_block(kind):
                continue
            m = re.search(r"(?m)^\s*id\s*=\s*([A-Za-z_0-9]+\.\d+)", body)
            if not m:
                continue
            event_ids.add(m.group(1))
            if f.is_relative_to(BUILD):
                events_seen.append((f.name, m.group(1), body))

    sprites: set[str] = set()
    for f in list((BUILD / "interface").rglob("*.gfx")) + \
            list((GAME_DIR / "interface").rglob("*.gfx")):
        sprites |= set(re.findall(r'name\s*=\s*"(GFX_[^"]+)"', _read(f)))

    loc = _merged_loc_keys()
    referenced = _script_tokens_outside("anomalies")

    def picture_of(body: str) -> str | None:
        m = re.search(r'(?m)^\s*picture\s*=\s*"?(GFX_[A-Za-z_0-9]+)"?', body)
        return m.group(1) if m else None

    n = 0
    reached: set[str] = set()
    for f in sorted(cat_dir.glob("*.txt")):
        text = _strip_comments(_read(f))
        for key, body in _top_level_blocks(text):
            n += 1
            # `on_success = X`, `N = X` and `anomaly_event = X` are all one
            # question: which event does resolving this anomaly fire.
            outcomes = set(re.findall(
                r"(?:anomaly_event|ship_event|on_success)\s*=\s*"
                r"([A-Za-z_0-9]+\.\d+)", body))
            outcomes |= set(re.findall(
                r"(?m)^\s*\d+\s*=\s*([A-Za-z_0-9]+\.\d+)\s*$", body))
            reached |= outcomes
            for eid in sorted(outcomes):
                if eid not in event_ids:
                    errors.append(
                        f"common/anomalies/{f.name}: {key} resolves to event "
                        f"'{eid}', which no events/ file declares. The anomaly "
                        f"completes and shows nothing. Vanilla has exactly one "
                        f"of these.")
            pic = picture_of(body)
            if pic and pic not in sprites:
                errors.append(
                    f"common/anomalies/{f.name}: {key} draws '{pic}', which no "
                    f".gfx declares. Declare it in "
                    f"src/interface/stg_event_pictures.gfx. Vanilla has 0.")
            if key not in loc:
                errors.append(
                    f"common/anomalies/{f.name}: {key} has no localisation key, "
                    f"so the situation log draws the key itself and logs "
                    f"nothing. Vanilla has 0.")
            dm = re.search(r'(?m)^\s*desc\s*=\s*"?([A-Za-z0-9_.\-]+)"?', body)
            dkey = dm.group(1) if dm else f"{key}_desc"
            if dkey not in loc:
                errors.append(
                    f"common/anomalies/{f.name}: {key} describes itself with "
                    f"'{dkey}', which has no localisation key. Vanilla has 0.")
            if _no_positive(body, "spawn_chance") and key not in referenced:
                errors.append(
                    f"common/anomalies/{f.name}: {key} has no positive "
                    f"`spawn_chance` and nothing in script names it, so the "
                    f"survey die can never pick it and no effect places it -- "
                    f"the category, its events, its art and its prose can never "
                    f"appear. `spawn_chance` defaults to `base = 0`. Vanilla's "
                    f"floor is 3 of 327.")

    # The events, from the other end.
    for fname, eid, body in events_seen:
        if eid not in reached and fname == _ANOMALY_OWN_EVENTS:
            errors.append(
                f"events/{fname}: {eid} is declared and no anomaly category "
                f"names it, so it can never fire. Every event in this file is a "
                f"category outcome by construction -- vanilla chains its own, "
                f"and scores 114 of 310 here, which is why the question is "
                f"asked of this file alone.")
        if fname != _ANOMALY_OWN_EVENTS and eid not in reached:
            continue
        pic = picture_of(body)
        if pic and pic not in sprites:
            errors.append(
                f"events/{fname}: {eid} draws '{pic}', which no .gfx declares. "
                f"Vanilla has 0 of these across its 310 anomaly events.")
        for field in ("title", "desc"):
            m = re.search(rf'(?m)^\s*{field}\s*=\s*"?([A-Za-z0-9_.\-]+)"?', body)
            if m and m.group(1) not in loc:
                errors.append(
                    f"events/{fname}: {eid}'s {field} is '{m.group(1)}', which "
                    f"has no localisation key -- the popup draws the key. "
                    f"Vanilla has 0.")
        for om in re.finditer(r'(?m)^\s*name\s*=\s*"?([A-Za-z0-9_.\-]+)"?', body):
            if om.group(1) not in loc:
                errors.append(
                    f"events/{fname}: {eid} has an option named "
                    f"'{om.group(1)}', which has no localisation key -- the "
                    f"button draws the key. Vanilla has 0.")

    return n


def check_archaeology() -> int:
    """An archaeological site whose stages, pictures, modifiers or loc do not meet.

    A dig site is FIVE files that have to agree, and none of them dangles when
    they do not: common/archaeological_site_types/ names a stage event and a
    picture, events/ declares the event, interface/*.gfx declares the picture
    and the stage's rune icon, common/static_modifiers/ declares the reward the
    finale hands out, and localisation/ carries the situation-log entry, the
    stage popup and every option button. Miss one and the game logs nothing
    useful -- a stage naming an event nobody declares completes in silence, and
    a missing loc key draws the raw key on the dig-site panel. Decision 47's
    silence in a sixth database.

    ONE QUESTION HERE HAS NO COUNTERPART IN check_anomalies, and it is the one
    worth having: `stages = N` is written by hand beside N `stage = { }` blocks,
    and vanilla's README says only that it "should match". Nothing enforces it,
    a site that claims more stages than it has cannot be finished, and a site
    that claims fewer never fires its last event.

    VANILLA IS THE CALIBRATION, over its 123 site types and the 475 stage events
    they name:

        site picture declared                0 findings
        site name loc key                    0
        site desc loc key (incl. `desc = { text = }`)  0
        stage names an event that exists     0
        stage rune icon declared             0
        `stages = N` matches the blocks      0
        RANDOM_EVENTS names a scripted effect  0
        stage event picture declared         0
        stage event title / desc loc key     0
        stage event option loc key           1  -- cstorms.1300 offers
                                                NAME_Hold_the_line_habitat,
                                                which no localisation file
                                                defines. A floor of one known
                                                instance, not zero, exactly as
                                                UBUME_BABY_CAT is for
                                                check_anomalies.

    So all ten are asked of every site in the built tree.

    THE ELEVENTH QUESTION HAS A SCOPE, for the reason it does in check_anomalies:
    "an archaeology event no site names" scores 157 of vanilla's 628
    `archaeology = yes` events, because vanilla chains dig-team interruptions
    off scripted effects this check does not read. Over
    src/events/stg_arcsite_events.txt the shape is different by construction --
    every event there is a stage outcome and there are no chains -- so the
    question is exact there and meaningless everywhere else.
    See .docs/validation/check-design.md rule 11.

    THE TWELFTH IS `weight`, WHICH DECISION 76 CALLS "the whole question" AND
    THE FIRST ELEVEN CANNOT SEE. A `weight = 0` site is complete, correct,
    validating clean and never placed, and it is what six of vanilla's ten
    base-game sites look like -- so it is exactly what a site copied from a
    vanilla template inherits. It is asked with the reachability filter
    _script_tokens_outside describes, because `weight` governs only
    `create_archaeological_site = random` and vanilla places most of its sites
    by naming them:

        no positive weight                   74 of vanilla's 123
        ... and named nowhere else in script  0

    Weight alone would be a 74-finding check; the pair is a 0-finding one, so
    the question is asked of the whole built tree rather than scoped to our own
    file -- scope is a calibration result (check-design rule 11), and here the
    calibration says none is needed.

    See .docs/decisions/76-trek-archaeology.md and
    .docs/decisions/79-reachability-checks.md.
    """
    site_dir = BUILD / "common" / "archaeological_site_types"
    if not site_dir.is_dir():
        return 0

    # Events, sprites and scripted effects all resolve against the merged tree
    # AND vanilla: a site may name a vanilla event or a vanilla rune as easily
    # as one of ours, and `no_events` is vanilla's.
    event_ids: set[str] = set()
    events_seen: list[tuple[str, str, str]] = []   # (file, id, body)
    for f in sorted(list((BUILD / "events").glob("*.txt")) +
                    list((GAME_DIR / "events").glob("*.txt"))):
        text = _strip_comments(_read(f))
        for kind, body in _top_level_blocks(text):
            if not _is_event_block(kind):
                continue
            m = re.search(r"(?m)^\s*id\s*=\s*([A-Za-z_0-9]+\.\d+)", body)
            if not m:
                continue
            event_ids.add(m.group(1))
            if f.is_relative_to(BUILD):
                events_seen.append((f.name, m.group(1), body))

    sprites: set[str] = set()
    for f in list((BUILD / "interface").rglob("*.gfx")) + \
            list((GAME_DIR / "interface").rglob("*.gfx")):
        sprites |= set(re.findall(r'name\s*=\s*"(GFX_[^"]+)"', _read(f)))

    effects: set[str] = set()
    for rel in ("common/scripted_effects",):
        for f in list((BUILD / rel).glob("*.txt")) + \
                list((GAME_DIR / rel).glob("*.txt")):
            effects |= {k for k, _ in _top_level_blocks(_strip_comments(_read(f)))}

    # BOTH modifier databases, and the second one is a calibration result rather
    # than thoroughness: `modifier = X` inside an event is written the same way
    # for an empire modifier and for an opinion modifier, and reading only
    # static_modifiers reports vanilla's own strange_worlds.2050 for awarding
    # `opinion_gift_given`. One line, and the floor goes from 1 to 0.
    modifiers: set[str] = set()
    for rel in ("common/static_modifiers", "common/opinion_modifiers"):
        for f in list((BUILD / rel).glob("*.txt")) + \
                list((GAME_DIR / rel).glob("*.txt")):
            modifiers |= {k for k, _ in _top_level_blocks(_strip_comments(_read(f)))}

    loc = _merged_loc_keys()
    referenced = _script_tokens_outside("archaeological_site_types")

    n = 0
    named: set[str] = set()
    for f in sorted(site_dir.glob("*.txt")):
        text = _strip_comments(_read(f))
        for key, body in _top_level_blocks(text):
            # Vanilla's own comment: "empty type for random assignments, handled
            # via code. So do not rename or remove this entry!" It has no name,
            # no picture and no stages on purpose.
            if key == "random":
                continue
            n += 1
            rel = f"common/archaeological_site_types/{f.name}"

            pic = re.search(r'(?m)^\s*picture\s*=\s*"?(GFX_[A-Za-z_0-9]+)"?', body)
            if pic and pic.group(1) not in sprites:
                errors.append(
                    f"{rel}: {key} draws '{pic.group(1)}', which no .gfx "
                    f"declares. Declare it in "
                    f"src/interface/stg_arcsite_pictures.gfx. Vanilla has 0.")
            if key not in loc:
                errors.append(
                    f"{rel}: {key} has no localisation key, so the situation "
                    f"log draws the key itself and logs nothing. Vanilla has 0.")

            # `desc = key` and `desc = { trigger = { } text = key }` are one
            # question. Vanilla writes both, sometimes in the same site.
            dkeys = [m.group(1) for m in re.finditer(
                r'(?m)^\s*desc\s*=\s*"?([A-Za-z0-9_.\-]+)"?\s*$', body)]
            dkeys += re.findall(
                r'(?m)^\s*text\s*=\s*"?([A-Za-z0-9_.\-]+)"?\s*$', body)
            for d in dkeys:
                if d not in loc:
                    errors.append(
                        f"{rel}: {key} describes itself with '{d}', which has "
                        f"no localisation key. Vanilla has 0.")

            if _no_positive(body, "weight") and key not in referenced:
                errors.append(
                    f"{rel}: {key} has no positive `weight` and nothing in "
                    f"script names it, so `create_archaeological_site = random` "
                    f"can never pick it and no initialiser or event places it "
                    f"-- the site, its stages, its art and its prose can never "
                    f"appear. Vanilla writes `weight = 0` in 74 of 123 sites "
                    f"and names every one of them somewhere.")

            stage_blocks = re.findall(r"(?m)^\s*stage\s*=\s*\{", body)
            declared = re.search(r"(?m)^\s*stages\s*=\s*(\d+)", body)
            if declared and int(declared.group(1)) != len(stage_blocks):
                errors.append(
                    f"{rel}: {key} says `stages = {declared.group(1)}` and has "
                    f"{len(stage_blocks)} stage blocks. Claiming more than it "
                    f"has makes the dig unfinishable; claiming fewer drops the "
                    f"last event. Vanilla has 0 mismatches over 123 sites.")

            evs = re.findall(r"(?m)^\s*event\s*=\s*([A-Za-z_0-9]+\.\d+)", body)
            named |= set(evs)
            for eid in evs:
                if eid not in event_ids:
                    errors.append(
                        f"{rel}: {key} has a stage that fires '{eid}', which no "
                        f"events/ file declares. The stage completes and shows "
                        f"nothing. Vanilla has 0.")
            for icon in re.findall(
                    r'(?m)^\s*icon\s*=\s*"?(GFX_[A-Za-z_0-9]+)"?', body):
                if icon not in sprites:
                    errors.append(
                        f"{rel}: {key} marks a stage with '{icon}', which no "
                        f".gfx declares. Vanilla has 0.")
            for rname in re.findall(r"RANDOM_EVENTS\s*=\s*([A-Za-z_0-9]+)", body):
                if rname not in effects:
                    errors.append(
                        f"{rel}: {key}'s on_roll_failed passes "
                        f"RANDOM_EVENTS = {rname}, which no "
                        f"common/scripted_effects/ file declares -- a failed "
                        f"roll then does nothing at all. Vanilla has 0.")

    # The events, from the other end.
    for fname, eid, body in events_seen:
        if fname == _ARCSITE_OWN_EVENTS and eid not in named:
            errors.append(
                f"events/{fname}: {eid} is declared and no site names it, so it "
                f"can never fire. Every event in this file is a stage outcome by "
                f"construction -- vanilla chains its own, and scores 157 of 628 "
                f"here, which is why the question is asked of this file alone.")
        if fname != _ARCSITE_OWN_EVENTS and eid not in named:
            continue
        pic = re.search(r'(?m)^\s*picture\s*=\s*"?(GFX_[A-Za-z_0-9]+)"?', body)
        if pic and pic.group(1) not in sprites:
            errors.append(
                f"events/{fname}: {eid} draws '{pic.group(1)}', which no .gfx "
                f"declares. Vanilla has 0 over its 475 stage events.")
        for field in ("title", "desc"):
            m = re.search(rf'(?m)^\s*{field}\s*=\s*"?([A-Za-z0-9_.\-]+)"?\s*$',
                          body)
            if m and m.group(1) not in loc:
                errors.append(
                    f"events/{fname}: {eid}'s {field} is '{m.group(1)}', which "
                    f"has no localisation key -- the popup draws the key. "
                    f"Vanilla has 0.")
        for om in re.finditer(r'(?m)^\s*name\s*=\s*"?([A-Za-z0-9_.\-]+)"?\s*$',
                              body):
            if om.group(1) not in loc:
                errors.append(
                    f"events/{fname}: {eid} has an option named "
                    f"'{om.group(1)}', which has no localisation key -- the "
                    f"button draws the key. Vanilla has exactly one of these.")
        for mm in re.finditer(
                r'(?m)^\s*modifier\s*=\s*"?([A-Za-z_0-9]+)"?\s*$', body):
            if mm.group(1) not in modifiers:
                errors.append(
                    f"events/{fname}: {eid} awards the modifier "
                    f"'{mm.group(1)}', which no common/static_modifiers/ file "
                    f"declares -- the reward is nothing and the tooltip is "
                    f"blank. Vanilla has 0.")
            elif mm.group(1) not in loc:
                errors.append(
                    f"events/{fname}: {eid} awards '{mm.group(1)}', which is "
                    f"declared but has no localisation key, so the empire's "
                    f"modifier list draws the key itself. Vanilla has 0.")

    return n


def check_story_events() -> int:
    """A story event whose hook, event, picture or loc key does not meet.

    A story event is FOUR files that have to agree, and none of them dangles
    when they do not: common/on_actions/ names an on_action key and an event id
    under it, events/ declares the event, interface/*.gfx declares the picture,
    and localisation/ carries the title, the description and every option
    button. Decision 47's silence in a seventh database.

    THE FIRST QUESTION HAS NO COUNTERPART IN check_anomalies OR
    check_archaeology, and it is the one worth having: an on_action block whose
    KEY nothing declares and nothing fires. The file parses. Every event under
    it exists, draws real art and reads correctly. It simply never runs, because
    Stellaris only fires on_action keys the engine knows or a `fire_on_action`
    names -- a mod that hooks `on_survey` when the engine renamed it
    `on_survey_planet` gets no error and no events. That is decision 76's
    `weight = 0` and decision 62's undeclared graphical culture, one database
    over: everything present, nothing dangling, the content never appears.

    An EMPTY block is not that defect and is not reported. All six findings in
    the built tree before this filter are Planetary Diversity's, and all six are
    `on_x = { events = { } }` -- vestigial stubs left behind by engine renames,
    hooking nothing to nowhere. A hook with nothing in it cannot fail to fire
    anything.

    VANILLA IS THE CALIBRATION, over its 485 on_action keys and the events they
    name -- 396 in 00_on_actions.txt, 33 in 01_planet_destruction.txt and 56 in
    02_component_on_actions.txt. (Decision 77 and this docstring both said 452,
    which is the sum with the planet-destruction file silently dropped. The
    figure is corrected here and recorded in
    .docs/decisions/78-phase-4-count-corrections.md; the decision keeps its
    text, per style guide 7.)

        on_action key declared or fired      0 findings in the built tree
                                             (6 before the empty-block filter,
                                              all six Planetary Diversity's)
        on_action names an event that exists 0 in the built tree, 17 in VANILLA
                                             -- Paradox hooks origin.5094/5104/
                                             5114/5124, anomaly.6793, action.41,
                                             six shroud.103xx and five
                                             grand_archive.70xx that it does not
                                             ship. The floor is a known 17, so
                                             the question is exact over the
                                             built tree and calibrated, not
                                             assumed, over vanilla.
        event picture declared               0
        event title / desc / option loc key  0

    THE FIFTH QUESTION HAS A SCOPE, for the reason it does in the two sibling
    checks: "a story event no on_action names" is meaningless over vanilla,
    which reaches most of its events by chaining them off each other. Over
    src/events/stg_story_events.txt the shape is different by construction --
    every event there is either hung on an on_action or fired by the two-step
    pulse gatekeeper beside it -- so the question is exact there and nowhere
    else. See .docs/validation/check-design.md rule 11.

    THE FIRST QUESTION IS ONE LEVEL DEEP, and saying so is cheaper than deepening
    it. `stg_on_five_year_story_pulse` counts as fired because some event in the
    tree textually contains `fire_on_action = { on_action = ... }` naming it; if
    THAT event were itself unreachable, the hook would still read as fired.
    Today the fifth question closes the gap from the other end -- it catches
    stg_story.2, the event that does the firing, if nothing hangs it on a hook --
    so the pair is closed for our own file and the transitive walk buys nothing
    it does not already have.

    See .docs/decisions/77-trek-story-events.md.
    """
    hook_dir = BUILD / "common" / "on_actions"
    if not hook_dir.is_dir():
        return 0

    # Event ids resolve against the merged tree AND vanilla: a hook may name a
    # vanilla event as easily as one of ours.
    event_ids: set[str] = set()
    events_seen: list[tuple[str, str, str]] = []   # (file, id, body)
    for f in sorted(list((BUILD / "events").glob("*.txt")) +
                    list((GAME_DIR / "events").glob("*.txt"))):
        text = _strip_comments(_read(f))
        for kind, body in _top_level_blocks(text):
            if not _is_event_block(kind):
                continue
            m = re.search(r"(?m)^\s*id\s*=\s*([A-Za-z_0-9]+\.\d+)", body)
            if not m:
                continue
            event_ids.add(m.group(1))
            if f.is_relative_to(BUILD):
                events_seen.append((f.name, m.group(1), body))

    sprites: set[str] = set()
    for f in list((BUILD / "interface").rglob("*.gfx")) + \
            list((GAME_DIR / "interface").rglob("*.gfx")):
        sprites |= set(re.findall(r'name\s*=\s*"(GFX_[^"]+)"', _read(f)))

    # The engine's own on_action keys, plus every custom one somebody fires.
    # BOTH halves are needed: vanilla's 00_on_actions.txt is the engine list, and
    # the README says custom on_actions are legal as long as a `fire_on_action`
    # reaches them -- which is exactly how STG's own pool is reached.
    engine_hooks: set[str] = set()
    van_hook_dir = GAME_DIR / "common" / "on_actions"
    if van_hook_dir.is_dir():
        for f in sorted(van_hook_dir.glob("*.txt")):
            engine_hooks |= {k for k, _ in
                             _top_level_blocks(_strip_comments(_read(f)))}
    fired: set[str] = set()
    for root in (BUILD, GAME_DIR):
        for f in root.rglob("*.txt"):
            fired |= set(re.findall(
                r"fire_on_action\s*=\s*\{[^{}]*on_action\s*=\s*([a-z_0-9]+)",
                _strip_comments(_read(f))))

    # A THIRD source of legitimacy, and it is a calibration result rather than
    # thoroughness. `on_destroy_planet_with_<KEY>` is generated by the ENGINE
    # from a planet-killer component's own key -- vanilla's
    # 01_planet_destruction.txt declares the four for its own components and
    # says nothing about anyone else's, so Planetary Diversity's Necro Ray hook
    # reads as dangling while being perfectly live. The allowlist comes from the
    # component database, not from a hand-written name.
    # .docs/validation/check-design.md rule 4.
    for rel in ("common/component_templates",):
        for f in list((BUILD / rel).glob("*.txt")) + \
                list((GAME_DIR / rel).glob("*.txt")):
            for k in re.findall(r'(?m)^\s*key\s*=\s*"([A-Za-z_0-9]+)"',
                                _strip_comments(_read(f))):
                base = f"on_destroy_planet_with_{k}"
                fired |= {base, f"{base}_queued", f"{base}_unqueued"}

    loc = _merged_loc_keys()

    n = 0
    hooked: set[str] = set()
    for f in sorted(hook_dir.glob("*.txt")):
        if "README" in f.name.upper():
            continue
        rel = f"common/on_actions/{f.name}"
        for key, body in _top_level_blocks(_strip_comments(_read(f))):
            # `events = { X }` and `random_events = { N = X }` are one question:
            # which events does this hook reach.
            evs = set(re.findall(
                r"(?m)^\s*(?:\d+\s*=\s*)?([a-z_0-9]+\.\d+)\s*$", body))
            if not evs:
                continue          # an empty hook reaches nothing to break
            n += 1
            hooked |= evs
            if key not in engine_hooks and key not in fired:
                errors.append(
                    f"{rel}: '{key}' is not an on_action the engine declares "
                    f"and no `fire_on_action` names it, so the {len(evs)} "
                    f"event(s) under it can never run. Nothing dangles and "
                    f"nothing is logged. Vanilla scores 0 here once empty "
                    f"stubs are excluded.")
            for eid in sorted(evs):
                if eid not in event_ids:
                    errors.append(
                        f"{rel}: '{key}' fires '{eid}', which no events/ file "
                        f"declares. Vanilla has 17 of these in its own hooks; "
                        f"the built tree has 0.")

    # An event our own file fires FROM another of its own events is reached too.
    # The pulse gatekeeper hangs on the on_action and calls its sibling back with
    # a random delay, which is vanilla's own action.220 / action.221 shape, and
    # the sibling is named nowhere near an on_action.
    for fname, _eid, body in events_seen:
        if fname == _STORY_OWN_EVENTS:
            hooked |= set(re.findall(
                r"[a-z_]*event\s*=\s*\{[^{}]*?\bid\s*=\s*([A-Za-z_0-9]+\.\d+)",
                body))

    # The events, from the other end.
    for fname, eid, body in events_seen:
        if fname == _STORY_OWN_EVENTS and eid not in hooked:
            errors.append(
                f"events/{fname}: {eid} is declared and no on_action names it, "
                f"so it can never fire. Every event in this file is reached "
                f"from a hook by construction -- vanilla chains its own, which "
                f"is why the question is asked of this file alone.")
        if fname != _STORY_OWN_EVENTS and eid not in hooked:
            continue
        if re.search(r"(?m)^\s*hide_window\s*=\s*yes", body):
            continue          # no window, so no picture and no loc to draw
        pic = re.search(r'(?m)^\s*picture\s*=\s*"?(GFX_[A-Za-z_0-9]+)"?', body)
        if pic and pic.group(1) not in sprites:
            errors.append(
                f"events/{fname}: {eid} draws '{pic.group(1)}', which no .gfx "
                f"declares. Declare it in "
                f"src/interface/stg_story_pictures.gfx. Vanilla has 0.")
        keys = [m.group(1) for m in re.finditer(
            r'(?m)^\s*(?:title|desc|name|text)\s*=\s*"?'
            r'([A-Za-z0-9_.\-]+)"?\s*$', body)]
        for k in keys:
            if k not in loc:
                errors.append(
                    f"events/{fname}: {eid} names the localisation key '{k}', "
                    f"which nothing defines -- the popup draws the key itself. "
                    f"Vanilla has 0 across the events its on_actions reach.")

    return n


def _declared_graphical_cultures() -> set[str]:
    """Every key `common/graphical_culture/` declares, across the merged tree.

    One database holds both shipset cultures and city-set-only cultures —
    vanilla declares `humanoid_01` and `lithoid_01` here beside `mammalian_01`.
    A build file shadows the vanilla file of the same NAME, so vanilla's
    declarations survive only from files the build does not replace; the build
    ships none of vanilla's two filenames today, and modelling it anyway is what
    keeps this correct the day it does.
    """
    rel = "common/graphical_culture"
    build_dir, van_dir = BUILD / rel, GAME_DIR / rel
    build_files = sorted(build_dir.glob("*.txt")) if build_dir.is_dir() else []
    shadowed = {f.name for f in build_files}
    van_files = [f for f in (sorted(van_dir.glob("*.txt")) if van_dir.is_dir()
                             else []) if f.name not in shadowed]

    out: set[str] = set()
    for f in build_files + van_files:
        text = re.sub(r"#.*", "", _read(f))
        depth = 0
        for m in re.finditer(r"([A-Za-z_]\w*)\s*=\s*\{|\{|\}", text):
            tok = m.group(0)
            if tok == "}":
                depth -= 1
            elif tok == "{":
                depth += 1
            else:
                if depth == 0:
                    out.add(m.group(1))
                depth += 1
    return out


def check_room_references() -> int:
    """The room a `room_selector` entry names, and the room an empire asks for.

    A room is the only art in Stellaris addressed by a BARE NAME with no path
    and no declaration anywhere: `room = "klingon_room"` finds
    `gfx/portraits/city_sets/klingon_room.dds` and vanilla's own comment says
    so. So nothing declares a room, which means nothing can dangle, which means
    every other check in this file is structurally blind to the whole database
    — and it was: STNH ships a 3.12 copy of vanilla's room_textures.txt at
    vanilla's path that drops 23 of vanilla's 42 designer rooms and 35 of its
    `ruler` rules, gates all 29 Trek rooms it names on country flags STG never
    sets, and names `futuresf_room`, which is not a texture in either tree.
    None of that produced one `error.log` record or one warning here.
    See .docs/decisions/48-room-selector-merge.md.

    `city_graphical_culture` is the same shape of reference and rides along
    here for that reason: `= "klingon"` finds `klingon_city_l01.dds` in the same
    directory by the same bare-name rule, nothing declares it either, and the
    naming across the Trek sets is irregular enough to invite a typo — STNH
    ships `klingon` beside `vulcan_01`, and `future_starfleet.dds` is a single
    texture that looks like a set prefix and is not one.

    Five questions, each calibrated against vanilla:

    1. **Two files claiming `room_selector`.** Vanilla declares it exactly once
       in 172 asset_selector files. Diverse Rooms ships a second, and which of
       two files wins one selector name is decided by nothing on disk — so the
       finding is that the answer is unknowable, not that either file is wrong.
    2. **A selector entry naming a room with no texture.** 0 of vanilla's 67,
       once entries whose whole body is `always = no` are skipped: vanilla uses
       those to park a room it is not shipping art for (`synth_queen_room`), and
       reading them as live references is what makes the ratio 1 instead of 0.
    3. **A prescripted `room =` with no texture.** 0 of vanilla's 29.
    4. **A PLAYABLE prescripted `room =` the designer does not offer.** A
       `game_setup` entry is what puts a room in the designer's list, so an
       empire in the picker asking for a room outside it has nothing to draw.
       Scoped to playable empires because vanilla's two misses are both pre-FTL
       primitives, which are prescripted countries that never reach the picker:
       0 of the 27 playable against 2 of 29 unscoped.
    5. **A `city_graphical_culture` with no `<name>_city_l01.dds`.** 0 of
       vanilla's 4.
    6. **A `city_graphical_culture` no `common/graphical_culture/` entry
       declares.** 0 of vanilla's 53. Question 5 is NOT this question, and
       passing it is what made this one look answered: a city set needs the art
       AND a declaration, and the five STNH sets that broke shipped complete
       six-layer art under a key nothing declared. Nothing dangles — the bare
       name finds its .dds — so the engine says nothing at load. It refuses at
       the empire designer instead, with EMPIRE_DESIGN_INVALID_GFX_CULTURE, and
       hides the empire from the picker. That is decision 34's rule in a new
       database: "declared somewhere" is not "declared where the engine looks".
       See .docs/decisions/62-city-set-cultures-undeclared.md.

    The reverse — a room texture the selector never names — is asked by
    `check_unreferenced` over `gfx/portraits/city_sets`, which is a closure root.
    """
    sel_dir = BUILD / "gfx/portraits/asset_selectors"
    tex_dirs = [BUILD / "gfx/portraits/city_sets",
                GAME_DIR / "gfx/portraits/city_sets"]
    rooms = {p.stem for d in tex_dirs if d.is_dir() for p in d.glob("*_room.dds")}
    if not rooms:
        return 0

    # Which file the engine reads for room_selector. Same rule as everywhere
    # else: a mod file at vanilla's path shadows it, and among mod files the
    # last filename in sort order takes a contested key (decision 29).
    claimants = sorted(
        f for f in (sel_dir.glob("*.txt") if sel_dir.is_dir() else [])
        if re.search(r"^\s*room_selector\s*=\s*\{", _read(f), re.M))
    if not claimants:
        claimants = [GAME_DIR / "gfx/portraits/asset_selectors/room_textures.txt"]
    if len(claimants) > 1:
        names = ", ".join(f.name for f in claimants)
        warnings.append(
            f"gfx/portraits/asset_selectors: {len(claimants)} files declare "
            f"`room_selector` ({names}). One of them decides every room in the "
            f"game and nothing on disk records which — the last filename in "
            f"sort order is the rule this file assumes, and a selector is not a "
            f"database whose entries merge. Fold the loser into src/'s copy and "
            f"exclude it in vendor.yml. See "
            f".docs/decisions/48-room-selector-merge.md.")
    sel = _read(claimants[-1])
    where = claimants[-1].name

    # `"x_room" = { body }`, brace-matched: a body carrying a nested `weight =
    # { }` ends early under a non-greedy regex and its entry reads as parked.
    entries: list[tuple[str, str]] = []
    for m in re.finditer(r'"([a-z0-9_]+_room)"\s*=\s*\{', sel):
        i, depth = m.end(), 1
        while depth and i < len(sel):
            depth += (sel[i] == "{") - (sel[i] == "}")
            i += 1
        entries.append((m.group(1), " ".join(sel[m.end():i - 1].split())))

    gs = re.search(r"game_setup\s*=\s*\{", sel)
    offered: set[str] = set()
    if gs:
        i, depth = gs.end(), 1
        while depth and i < len(sel):
            depth += (sel[i] == "{") - (sel[i] == "}")
            i += 1
        offered = set(re.findall(r'"([a-z0-9_]+_room)"', sel[gs.end():i]))

    ack = _ack_list("room_reference_ack")
    missing = sorted({name for name, body in entries
                      if body != "always = no" and name not in rooms} - ack)
    for name in missing[:6]:
        warnings.append(
            f"gfx/portraits/asset_selectors/{where}: `{name}` names no "
            f"gfx/portraits/city_sets/{name}.dds in the built tree or vanilla, "
            f"so the entry can only ever draw nothing. A room is addressed by "
            f"bare name, so no declaration dangles and nothing logs it. Ack "
            f"under room_reference_ack if the entry is deliberately parked.")
    if len(missing) > 6:
        warnings.append(f"... and {len(missing) - 6} more unbacked room name(s)")

    cities = {p.name.split("_city_l")[0]
              for d in tex_dirs if d.is_dir() for p in d.glob("*_city_l01.dds")}
    declared_cultures = _declared_graphical_cultures()

    n = 0
    pres = BUILD / "prescripted_countries"
    for f in sorted(pres.glob("*.txt") if pres.is_dir() else []):
        text = _read(f)
        for key, a, b in _pdx_blocks(text):
            city = re.search(r'city_graphical_culture = "?(\w+)"?', text[a:b])
            if city and city.group(1) not in cities and key not in ack:
                warnings.append(
                    f"prescripted_countries/{f.name}: {key} sets "
                    f"city_graphical_culture = {city.group(1)}, which no "
                    f"gfx/portraits/city_sets/{city.group(1)}_city_l01.dds "
                    f"backs. The planet view draws its cities from that bare "
                    f"name and nothing declares it, so a typo is silent.")
            # Question 6. Separate from the art check above: complete art under
            # an undeclared key passes that one and still hides the empire.
            if (city and declared_cultures
                    and city.group(1) not in declared_cultures
                    and key not in ack):
                warnings.append(
                    f"prescripted_countries/{f.name}: {key} sets "
                    f"city_graphical_culture = {city.group(1)}, which no "
                    f"common/graphical_culture/ entry declares. The art can be "
                    f"complete and this still hides the empire from the "
                    f"designer with EMPIRE_DESIGN_INVALID_GFX_CULTURE, and an "
                    f"AI-only empire never reaches the designer, so no log "
                    f"will ever name it. See "
                    f".docs/decisions/62-city-set-cultures-undeclared.md.")
            m = re.search(r'room = "([a-z0-9_]+)"', text[a:b])
            if not m or key in ack:
                continue
            n += 1
            room = m.group(1)
            if room not in rooms:
                warnings.append(
                    f"prescripted_countries/{f.name}: {key} asks for "
                    f"`{room}`, which is no texture in either tree. Nothing "
                    f"logs a room that does not exist.")
            elif room not in offered:
                playable = re.search(r"playable = (\w+)", text[a:b])
                if not playable or playable.group(1) not in ("no", "stg_never"):
                    warnings.append(
                        f"prescripted_countries/{f.name}: {key} asks for "
                        f"`{room}`, which the selector's game_setup does not "
                        f"offer — the empire is in the picker and the picker "
                        f"only draws rooms on that list.")
    return n


def _pdx_blocks(text: str):
    """(key, body_start, body_end) for every depth-0 `key = { ... }`."""
    for m in re.finditer(r"^(\w+) = \{", text, re.M):
        i, depth = m.end(), 1
        while depth and i < len(text):
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        yield m.group(1), m.end(), i - 1


# ── The graphical-culture family ─────────────────────────────────────────────
#
# Three questions share one database and are kept together for that reason:
# which cultures an empire can fly, whether each has art to draw, and whether
# each has prose to show. `check_room_references` asks the CITY half of the same
# database (its questions 5 and 6); these ask the ship half.

def _culture_blocks(root: Path) -> dict[str, str]:
    """Every `common/graphical_culture/` declaration under `root`, keyed by name."""
    out: dict[str, str] = {}
    d = root / "common/graphical_culture"
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.txt")):
        for k, b in _top_level_blocks(_strip_comments(_read(f))):
            out[k] = b
    return out


def _city_set_keys(*roots: Path) -> set[str]:
    """Culture names with a first city layer on disk, across `roots`."""
    out = set()
    for r in roots:
        d = r / "gfx/portraits/city_sets"
        if d.is_dir():
            out |= {p.name[:-len("_city_l01.dds")] for p in d.glob("*_city_l01.dds")}
    return out


def _flown_cultures() -> dict[str, list[str]]:
    """Ship `graphical_culture` -> the prescripted empires flying it.

    `city_graphical_culture` is a DIFFERENT field that ends in the same word, so
    it must be excluded by lookbehind rather than by a substring test -- reading
    them as one turns 30 cultures into 39 and puts `humanoid_01` at the top of
    the list, which is the city answer to a ship question.
    """
    out: dict[str, list[str]] = {}
    d = REPO / "src/prescripted_countries"
    if not d.is_dir():
        return out
    for f in sorted(d.rglob("*.txt")):
        text = _strip_comments(_read(f))
        for key, body in _top_level_blocks(text):
            m = re.search(r'(?<!city_)graphical_culture\s*=\s*"?([A-Za-z_0-9]+)', body)
            if m:
                out.setdefault(m.group(1), []).append(key)
    return out


def check_graphical_culture_art() -> int:
    """An offerable graphical culture whose city art does not resolve, fallback included.

    THE PREMISE THIS CHECK WAS WRITTEN TO TEST WAS FALSE, and recording that is
    most of its value. Analysis 2026-08-16 finding 2 read six STG cultures with
    no `<key>_city_l01.dds` -- bajoran_01, federation_32, andorian_01, bolian_01,
    breen_01, generic_07 -- as six styles the designer offers with nothing to
    draw, and asked for a content call: point them at an orphan city set, or
    accept a blank. Neither is needed.

    VANILLA SETTLES IT IN ITS OWN FILE HEADER: "Setting fallback will allow the
    game to try and use another culture if the asset is missing." Every one of
    those six declares `fallback = mammalian_01`, and mammalian_01 ships city
    art. So the art resolves; it is simply not their own.

    THE NUMBERS THAT MAKE THAT MORE THAN AN ASSERTION. 24 of vanilla's 52
    declared cultures have no city art of their own -- 46%, so "declared implies
    art" cannot be the rule or vanilla would be broken in 24 places. Narrowing
    to the cultures actually offered (those NOT carrying
    `randomized = { always = no }`, which is how vanilla parks a pirate or a
    guardian culture) leaves 22, of which 2 still have no art: mindwarden_01 and
    nemesis_01, and both declare a fallback. Follow the fallback chain and
    vanilla's count is 0 of 22. STG's is 0 of 41. THAT is the invariant with a
    floor, and it is the one asked here (rule 11).

    STG DECLARES NO `randomized = { always = no }` AT ALL, so all 41 of its
    cultures are in scope -- a stricter population than vanilla's 22, and it
    still passes.

    The chain is walked with a `seen` set because a fallback cycle would
    otherwise hang the check rather than report anything.
    """
    cultures = _culture_blocks(BUILD)
    if not cultures:
        return 0
    art = _city_set_keys(BUILD, GAME_DIR)

    broken = {}
    n = 0
    for name, body in cultures.items():
        if re.search(r"randomized\s*=\s*\{[^}]*always\s*=\s*no", body):
            continue          # parked, never offered -- vanilla's pirates and guardians
        n += 1
        seen, cur, chain = set(), name, []
        while cur and cur not in seen:
            if cur in art:
                break
            seen.add(cur)
            chain.append(cur)
            m = re.search(r"\bfallback\s*=\s*(\w+)", cultures.get(cur, ""))
            cur = m.group(1) if m else None
        else:
            cur = None
        if not cur:
            broken[name] = " → ".join(chain)

    if broken:
        head = "; ".join(f"{k} ({v})" for k, v in sorted(broken.items())[:4])
        warnings.append(
            f"common/graphical_culture: {len(broken)} of {n} offerable culture(s) "
            f"have no city art and no fallback chain that reaches any — {head}"
            f"{' …' if len(broken) > 4 else ''}. The empire designer offers the "
            f"style and the planet surface has nothing to draw. Vanilla's floor "
            f"is 0 of 22. Either ship `<key>_city_l01.dds` or declare a "
            f"`fallback` that resolves. "
            f"See .docs/decisions/84-shipset-descs-and-home-system-names.md.")
    return n


def check_shipset_descriptions() -> int:
    """A flown graphical culture with no `_shipset_desc`, and a key naming no culture.

    TWO DIRECTIONS, AND VANILLA'S FLOOR IS EXACTLY 0 IN BOTH. Vanilla declares
    52 graphical cultures and writes only 20 `<culture>_shipset_desc` keys, so
    "every declared culture is described" is emphatically not the rule -- but
    every one of the 19 cultures a vanilla prescripted empire actually FLIES has
    a key, and every one of its 20 keys names a culture that is declared. The
    flown set is the population; the declared set is the sanity bound.

    WHY IT MATTERS MORE THAN A MISSING TOOLTIP. Stellaris renders an unresolved
    localisation key as THE RAW KEY TEXT, not as blank space, so a missing key
    puts the literal string `vulcan_shipset_desc` in the shipset browser. That
    is what the 2026-08-22 Vulcan run reported, and the run plan had predicted
    an empty panel -- worth remembering, because "the box shows the key" reads
    like a different defect and is the normal signature of this one.

    WHAT IT CAUGHT. 7 of STG's 14 keys named a CITY-set culture rather than a
    shipset one (`vulcan_01` where the Vulcans fly `vulcan`, `federation` where
    the Federation flies `starfleet_tng`) and could never render, while 23 flown
    cultures had no key at all -- 30 of 30 wrong in one direction or the other,
    from prose that was written and good. A rename plus sixteen new descriptions
    closed it; this check is what keeps a 31st culture from shipping mute.
    See .docs/decisions/84-shipset-descs-and-home-system-names.md.
    """
    flown = _flown_cultures()
    declared = set(_culture_blocks(BUILD))
    if not flown or not declared:
        return 0

    keys = set()
    d = BUILD / "localisation/english"
    if d.is_dir():
        for f in sorted(d.glob("*.yml")):
            keys |= {m.group(1) for m in
                     re.finditer(r"^\s*([a-z_0-9]+)_shipset_desc\s*:", _read(f), re.M)}

    missing = sorted(set(flown) - keys)
    if missing:
        head = ", ".join(f"{c} ({len(flown[c])} empire(s))" for c in missing[:4])
        warnings.append(
            f"localisation: {len(missing)} of {len(flown)} flown graphical "
            f"culture(s) have no `<culture>_shipset_desc` — {head}"
            f"{' …' if len(missing) > 4 else ''}. Stellaris draws an unresolved "
            f"key as the key text, so the shipset browser shows the raw string. "
            f"Vanilla keys all 19 of its own flown cultures. "
            f"See .docs/decisions/84-shipset-descs-and-home-system-names.md.")

    orphan = sorted(keys - declared)
    if orphan:
        warnings.append(
            f"localisation: {len(orphan)} `_shipset_desc` key(s) name a culture "
            f"no `common/graphical_culture/` entry declares — "
            f"{', '.join(orphan[:6])}{' …' if len(orphan) > 6 else ''}. The prose "
            f"can never render. Vanilla writes 20 such keys and every one names "
            f"a declared culture. "
            f"See .docs/decisions/84-shipset-descs-and-home-system-names.md.")
    return len(flown)


def check_home_system_body_names() -> int:
    """Two bodies in one home system carrying the same name.

    SCOPE IS `usage = custom_empire`, AND THAT IS A CALIBRATION RESULT. Asked of
    every vanilla initializer the question fails 62 times in 357 -- 17%, because
    vanilla repeats a name deliberately for identical decorative objects: four
    `NAME_Ring_Section`s in a shattered ring, three `NAME_Mining_Corps`. Asked of
    the nine initializers a prescripted empire actually starts in, vanilla's
    count is 0. A home system is hand-authored and every body in it is meant to
    be a place, so a repeat there is a paste, not a pattern (rule 11).

    ONLY THE BLOCK'S OWN NAME COUNTS. An early version of this counted the
    initializer's top-level `name` too and reported Sol against itself: vanilla
    names the system NAME_Sol and its primary star NAME_Sol, which is the
    convention rather than a collision. Compare bodies with bodies.

    WHAT IT CAUGHT -- three separate causes behind one symptom, which is why the
    check is worth more than the three fixes:

      * `gen_home_systems.sub_blocks` matched at every nesting depth while its
        docstring promised immediate children, so the moon of a nested planet
        was emitted under that planet AND under its grandparent star. Two
        systems ended up with two "Kerkhov's Moon".
      * the star/capital de-collision rule only recognised a `pc_<x>_star`
        class, and the generator's commonest star is the bare `star` keyword, so
        Qo'noS, Cait, Romulus and Haakon each drew their capital's name twice.
      * STNH's own file names both moons of S'latas "S'latas a".

    Analysis 2026-08-16 finding 4 saw one of the six and read it as a one-line
    content fix. It was three bugs.
    See .docs/decisions/84-shipset-descs-and-home-system-names.md.
    """
    d = REPO / "src/common/solar_system_initializers"
    if not d.is_dir():
        return 0

    n = 0
    bad: dict[str, dict[str, int]] = {}
    for f in sorted(d.glob("*.txt")):
        for key, body in _top_level_blocks(_strip_comments(_read(f))):
            if not re.search(r"\busage\s*=\s*custom_empire\b", body):
                continue
            n += 1
            names: list[str] = []
            for m in re.finditer(r"\b(?:planet|moon)\s*=\s*\{", body):
                i, depth = m.end(), 1
                while i < len(body) and depth:
                    depth += (body[i] == "{") - (body[i] == "}")
                    i += 1
                inner = body[m.end():i - 1]
                # The block's OWN name: everything before its first child block.
                head = re.split(r"\b(?:planet|moon)\s*=\s*\{", inner, maxsplit=1)[0]
                nm = re.search(r'\bname\s*=\s*"([^"]+)"', head)
                if nm:
                    names.append(nm.group(1))
            dup = {k: v for k, v in collections.Counter(names).items() if v > 1}
            if dup:
                bad[key] = dup

    if bad:
        head = "; ".join(f"{k}: {', '.join(sorted(v))}"
                         for k, v in sorted(bad.items())[:3])
        warnings.append(
            f"src/common/solar_system_initializers: {len(bad)} of {n} home "
            f"system(s) name two bodies the same — {head}"
            f"{' …' if len(bad) > 3 else ''}. Both draw on one system map with "
            f"one label. Vanilla's own nine `usage = custom_empire` "
            f"initializers do this 0 times. These files are GENERATED, so the "
            f"fix belongs in tools/gen_home_systems.py, not here. "
            f"See .docs/decisions/84-shipset-descs-and-home-system-names.md.")
    return n


def check_unreferenced() -> tuple[int, int]:
    """The dual of every other check here: is this FILE referenced by anything?

    Twenty-odd checks above ask whether a reference resolves. None has ever
    asked the reverse, and that is why the tree carried a fourth class nobody
    had named: 1,748 files, 1.5 GB, that arrived inside a directory we included
    and that nothing anywhere referred to — 813 STNH event pictures no
    spriteType declares, 107 .wav files no .asset names, two whole directories
    of re-skins for mods not in the harvest. Decision 24's lesson was that an
    include list converges on whatever question the checks ask; this is the
    question that was never asked. See .docs/decisions/45-clutter-pass.md.

    `make vendor` now removes those, so this is the assertion that it did, and
    that nothing has been added since that it would have removed. It GATES on
    the prune scope only. Outside it the count is reported and not failed on,
    because tools/clutter.py's VANILLA_FLOOR says this closure finds 4.9% of
    gfx/models unreferenced in /stellaris itself: at that rate a finding there
    is indistinguishable from Paradox's own leftovers, and gating on it would
    be gating on noise. Scope is a calibration result (.docs/validation/check-design.md rule 11), and widening
    it means moving a tier in clutter.py with a new ratio beside it.

    Calibrated by reverting rather than by reporting a number: blinding the
    closure to one declaration file at a time drops exactly the files it was
    the sole route to — 12 event pictures behind realspace_eventpictures.gfx,
    159 meshes and textures behind federation_all_ships.gfx, 0 behind an
    .asset that only groups names other files map to disk.
    """
    if not BUILD.is_dir():
        return 0, 0
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import clutter

    tree, verdicts = clutter.build_verdicts()
    inside = clutter.prunable(verdicts)
    outside = sum(1 for r, v in verdicts.items()
                  if v == "orphan" and clutter.tier(r) not in clutter.PRUNE_TIERS)

    by_tier: dict[str, int] = collections.Counter(
        clutter.tier(r) for r in inside)
    for name, count in sorted(by_tier.items(), key=lambda kv: -kv[1])[:6]:
        sample = next(r for r in inside if clutter.tier(r) == name)
        errors.append(
            f"{sample}: nothing in the built tree or vanilla names this file, "
            f"and {count - 1} other(s) in {name}. `make vendor` removes "
            f"unreferenced files in that tier, so finding one here means the "
            f"tree was built with --no-prune, hand-edited, or that "
            f"tools/clutter.py's root set changed under it. Run `make clutter "
            f"ARGS='--list {name}'` to read them, and `make clutter-vanilla` "
            f"for the floor before concluding the closure is wrong.")
    return len(tree.files), outside


def check_sources() -> int:
    """Every source vendor.yml declares must be snapshotted in .source/.

    Existence only -- one stat per source. Comparing the snapshot against
    /workshop is `make sources-status`, which walks 40,000 files and is not
    something every validate run should pay for.
    """
    manifest = REPO / "vendor.yml"
    if not manifest.is_file():
        return 0
    text = manifest.read_text(encoding="utf-8-sig")

    m = re.search(r"^\s*source_root:\s*(\S+)\s*$", text, re.M)
    root = Path((m.group(1).strip("\"'") if m else ".source"))
    if not root.is_absolute():
        root = REPO / root

    ids = re.findall(r'^\s*-\s*id:\s*"?(\d+)"?\s*$', text, re.M)
    missing = [i for i in ids if not (root / i).is_dir()]
    for sid in missing[:5]:
        errors.append(f"{root.name}/{sid}: source declared in vendor.yml but not "
                      f"snapshotted -- `make vendor` will fail. "
                      f"Run: make sources-sync ID={sid}")
    if len(missing) > 5:
        errors.append(f"... and {len(missing) - 5} more source(s) not snapshotted")

    if ids and not missing and not (REPO / "sources.lock.yml").is_file():
        warnings.append("sources.lock.yml is missing -- nothing records which "
                        "revision of each source mod is pinned. Run: make sources-sync")
    return len(ids)


def check_descriptor() -> None:
    # src/descriptor.mod is the one we edit; stg-build/descriptor.mod is the copy
    # vendor puts in the mod. Check the source, so this still works before the
    # first build -- the copy is covered by check_vendored like any other.
    p = REPO / "src" / "descriptor.mod"
    if not p.is_file():
        errors.append("src/descriptor.mod: missing -- the mod has no descriptor")
        return

    text = p.read_text(encoding="utf-8-sig")
    for key in ("name", "version", "supported_version"):
        if not re.search(rf'^\s*{key}\s*=\s*"', text, re.M):
            errors.append(f"descriptor.mod: missing required key '{key}'")

    if re.search(r'^\s*path\s*=', text, re.M):
        warnings.append("descriptor.mod: contains 'path=' -- that belongs in the "
                        "deployed .mod file, not the in-mod descriptor")

    pic = re.search(r'^\s*picture\s*=\s*"([^"]+)"', text, re.M)
    if pic and not (REPO / "src" / pic.group(1)).is_file():
        warnings.append(f"descriptor.mod: picture '{pic.group(1)}' not found "
                        f"(the launcher shows a blank thumbnail)")

    sup = re.search(r'^\s*supported_version\s*=\s*"([^"]+)"', text, re.M)
    game_dir = Path(os.environ.get("STELLARIS_GAME_DIR", "/stellaris"))
    ls = game_dir / "launcher-settings.json"
    if sup and ls.is_file():
        import json
        try:
            settings = json.loads(ls.read_text())
        except (ValueError, OSError):
            settings = {}
        # Compare against `rawVersion` ("v4.4.6"), the exact installed build,
        # not `modsCompatibilityVersion` ("4.4"), which is only the launcher's
        # bucket and cannot see a patch -- and a patch is what silently
        # invalidates a vendored copy of a vanilla file (decision 08). Comparing
        # the major against the bucket, as this once did, could not fire short
        # of Stellaris 5: a check that cannot fail.
        installed = settings.get("rawVersion", "").lstrip("v")
        declared = sup.group(1)

        # THE `v` PREFIX IS NOT DECORATION. The launcher stores this string
        # verbatim in launcher-v2.sqlite's `mods.requiredVersion` and a value
        # without the leading `v` fails its version parse, badging the mod
        # "made for a different version of the game" however correct the numbers
        # are. Measured 2026-08-02: 25 of 26 registered mods carry the `v`.
        if not declared.startswith("v"):
            warnings.append(
                f"descriptor.mod: supported_version '{declared}' has no 'v' "
                f"prefix — write 'v{declared}'. The launcher stores this string "
                f"verbatim and badges the mod as made for another game version "
                f"without it, even when the numbers match.")

        # Strip it for the numeric comparison below, on BOTH sides. Comparing
        # 'v4.4.6' against '4.4.6' component-wise would fire drift on the 'v'.
        declared = declared.lstrip("v")

        if installed:
            want, have = declared.split("."), installed.split(".")
            drift = len(want) > len(have) or any(
                w not in ("*", "**") and w != have[i] for i, w in enumerate(want))
            if drift:
                warnings.append(
                    f"descriptor.mod: supported_version '{declared}' vs installed "
                    f"game '{installed}' — the game moved under the build. Re-read "
                    f"the sources that shadow vanilla paths before trusting the "
                    f"next run, then bump src/descriptor.mod.")


def main() -> int:
    loc_n = check_localisation()
    scr_n = check_script()
    shadow_n = check_src_shadowing()
    nl_n = check_name_lists()
    key_n, key_same = check_key_conflicts()
    ose_n = check_order_sensitive_databases()
    gen_n = check_vendored()
    reg_n = check_vanilla_regression()
    srg_n = check_src_source_regression()
    art_n = check_dangling_identifiers()
    mesh_n = check_dangling_shaders()
    ref_n = check_dangling_art_references()
    fil_n = check_gfx_file_refs()
    tex_n = check_texture_basenames()
    ord_n = check_asset_load_order()
    sap_n = check_section_attach_points()
    atk_n = check_attach_targets()
    var_n = check_asset_variables()
    dup_n = check_duplicate_entities()
    dtx_n = check_duplicate_textures()
    ploc_n = check_prescripted_loc()
    geo_n = check_shadowed_texture_geometry()
    def_n, def_same = check_defines_conflicts()
    pre_n = check_prescripted_empires()
    col_n = check_colony_name_collisions()
    ini_n = check_prescripted_initializers()
    icl_n = check_initializer_classes()
    hpg_n = check_home_planet_generation()
    por_n = check_prescripted_portraits()
    clo_n = check_portrait_clothes_selectors()
    selp_n = check_selector_texture_paths()
    selr_n = check_selector_texture_files()
    scl_n = check_species_class_loc()
    app_n = check_prescripted_appearance()
    room_n = check_room_references()
    gca_n = check_graphical_culture_art()
    sdesc_n = check_shipset_descriptions()
    hsbn_n = check_home_system_body_names()
    mus_n = check_music_declarations()
    ano_n = check_anomalies()
    arc_n = check_archaeology()
    sty_n = check_story_events()
    unr_n, unr_out = check_unreferenced()
    src_n = check_sources()
    man_n = check_manifest_parses()
    check_descriptor()

    print(f"{DIM}src/: {scr_n} script file(s), {loc_n} localisation file(s), "
          f"{shadow_n} checked for shadowing, {nl_n} name list(s)  |  "
          f"generated: {gen_n} file(s), {reg_n} checked for vanilla regression, "
          f"{srg_n} src/ override(s) against the source they shadow, "
          f"{art_n} art file(s) for dangling identifiers, {mesh_n} mesh/entity "
          f"file(s) for shaders, {ref_n} for dangling mesh/particle references, "
          f"{fil_n} for art files that must exist on disk, "
          f"{tex_n} for texture filenames that must resolve, "
          f"{ord_n} ship asset(s) for clone load order and section locators, "
          f"{sap_n} for hull section attach points, "
          f"{atk_n} for attach targets, "
          f"{var_n} art file(s) for unresolved @variables, "
          f"{dup_n} for duplicate entity declarations, "
          f"{dtx_n} texture(s) for duplicate basenames, "
          f"{ploc_n} prescripted empire(s) for loc against their source, "
          f"{geo_n} shadowed event picture(s) and city layer(s) for changed "
          f"dimensions, "
          f"{def_n} defines file(s) ({def_same} define(s) set twice to the same "
          f"value, not reported), {key_n} common/ file(s) for key conflicts "
          f"({key_same} contested key(s) identical in content, not reported), "
          f"{ose_n} order-sensitive database(s), "
          f"{pre_n} prescripted-country file(s) for traits and ethics, "
          f"{col_n} name list(s) for colony/capital collisions, "
          f"{ini_n} for home-system initializers, "
          f"{icl_n} initializer file(s) for planet/star class references, "
          f"{hpg_n} for home-planet generation, "
          f"{por_n} for portrait references, "
          f"{clo_n} for clothes-selector species gating, "
          f"{selp_n} asset selector(s) for malformed texture paths, "
          f"{selr_n} for texture paths that must resolve, "
          f"{scl_n} species class(es) for localisation, "
          f"{app_n} for ruler appearance indices, "
          f"{room_n} for the room and city set they ask for, "
          f"{gca_n} offerable graphical culture(s) for city art or a fallback that reaches it, "
          f"{sdesc_n} flown culture(s) for a shipset description, "
          f"{hsbn_n} home system(s) for two bodies sharing a name, "
          f"{mus_n} music track(s) for a declaration that plays them, "
          f"{ano_n} anomaly categor(ies) for their event, picture and loc, "
          f"{arc_n} archaeological site(s) for their stages, pictures, "
          f"modifiers and loc, "
          f"{sty_n} on_action hook(s) for the events, pictures and loc they "
          f"reach, "
          f"{unr_n} for reachability ({unr_out} unreferenced outside the prune "
          f"scope, reported not failed — see `make clutter`)  |  "
          f"{src_n} source snapshot(s), vendor.yml declares {man_n}{OFF}")

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
