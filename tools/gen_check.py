#!/usr/bin/env python3
"""Is every generator a fixpoint? Re-run each one and diff `src/` against itself.

WHY THIS EXISTS. `tools/gen_star_names.py` subtracts names already pooled by
reading the BUILT tree -- which `make vendor` fills with the generator's own
previous output. A second run therefore subtracted its own 580 names and wrote a
pool a third the size. That went unnoticed until the 2026-08-10 Federation run
reported unlocalised nebula names and somebody re-ran the tool by hand
(.docs/decisions/78-widen-attach-points-and-two-new-checks.md).

SIX OF THE FOURTEEN GENERATORS READ `stg-build/`, and none of them is invoked by
any `make` target -- so nothing has ever established that the other eight are
fixpoints. A correct generator is one: run it against the tree it already
produced and nothing changes. The floor is therefore 0 by construction, not by
calibration, which is the rare case where a check needs no vanilla ratio beside
it (.docs/validation/check-design.md, rule 11).

TWO LEVELS, BECAUSE THE TWO FAILURES HAVE DIFFERENT SHAPES.

  default  Run each generator once against the current tree and ask whether it
           reproduces `src/` byte for byte. This catches DRIFT: the committed
           output no longer being what today's inputs produce, which is what
           had quietly dropped 22 star names as the tree grew around a tool
           nobody had re-run.

  --deep   gen -> `make vendor` -> gen, for the generators that read the built
           tree. This is the only level that can catch the gen_star_names
           defect itself, because that one needs its own output fed back
           through a build before it bites. It costs a full vendor per
           generator (~70 s each), so it is opt-in.

SAFETY. `src/` is hand-written content and this tool RUNS GENERATORS OVER IT.
Everything under `src/` and `.vendor-cache/` is copied to a scratch directory
first and restored afterwards, including on exception and on Ctrl-C -- the
restore is in a `finally`. Nothing here touches `stg-build/`, `.source/` or
`/stellaris`.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src"
CACHE = REPO / ".vendor-cache"
GUARDED = (SRC, CACHE)

# Every generator, with the arguments a plain run needs. `reads_build` marks the
# ones whose inputs include the tree they themselves feed -- the population
# --deep exists for. Measured 2026-08-22 by grepping each tool for BUILD.
GENERATORS: list[tuple[str, list[str], bool]] = [
    ("gen_borg_vo.py",             [],        True),
    ("gen_empire_flags.py",        [],        False),
    ("gen_first_contact_sounds.py", [],       False),
    ("gen_home_systems.py",        [],        True),
    ("gen_static_galaxy.py",       [],        False),
    ("gen_paragon_backgrounds.py", [],        False),
    ("gen_room_selector.py",       [],        True),
    ("gen_ruler_clothes.py",       [],        True),
    ("gen_ship_class_names.py",    [],        False),
    ("gen_ship_names.py",          [],        False),
    ("gen_shipsets.py",            [],        False),
    ("gen_star_names.py",          [],        True),
    ("fix_prescripted_rooms.py",   [],        False),
    ("fix_ship_locators.py",       ["--all"], True),
]

GREEN, YELLOW, RED, DIM, RESET = (
    "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m")


def snapshot(into: Path) -> None:
    for d in GUARDED:
        if d.is_dir():
            shutil.copytree(d, into / d.name, symlinks=True)


def restore(frm: Path) -> None:
    for d in GUARDED:
        keep = frm / d.name
        if not keep.is_dir():
            continue
        if d.is_dir():
            shutil.rmtree(d)
        shutil.copytree(keep, d, symlinks=True)


def differences(baseline: Path) -> list[str]:
    """Repo-relative paths under the guarded dirs that differ from the snapshot."""
    out: list[str] = []
    for d in GUARDED:
        old, new = baseline / d.name, d
        if not old.is_dir() and not new.is_dir():
            continue
        left = {p.relative_to(old) for p in old.rglob("*") if p.is_file()} \
            if old.is_dir() else set()
        right = {p.relative_to(new) for p in new.rglob("*") if p.is_file()} \
            if new.is_dir() else set()
        for rp in sorted(left | right):
            a, b = old / rp, new / rp
            if not a.is_file():
                out.append(f"+ {d.name}/{rp}")
            elif not b.is_file():
                out.append(f"- {d.name}/{rp}")
            elif not filecmp.cmp(a, b, shallow=False):
                out.append(f"~ {d.name}/{rp}")
    return out


def run(tool: str, args: list[str]) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(REPO / "tools" / tool), *args],
                       cwd=REPO, capture_output=True, text=True)
    return p.returncode, (p.stderr or p.stdout).strip()


def vendor() -> tuple[int, str]:
    p = subprocess.run(["make", "vendor"], cwd=REPO, capture_output=True,
                       text=True)
    return p.returncode, (p.stderr or p.stdout).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--deep", action="store_true",
                    help="gen -> make vendor -> gen, for generators that read "
                         "the built tree (~70 s each)")
    ap.add_argument("only", nargs="*",
                    help="generator filenames to check; default is all")
    a = ap.parse_args()

    todo = [g for g in GENERATORS if not a.only or g[0] in a.only
            or g[0].removesuffix(".py") in a.only]
    if not todo:
        print(f"no generator matches {a.only}; known: "
              f"{', '.join(g[0] for g in GENERATORS)}", file=sys.stderr)
        return 2
    if a.deep:
        todo = [g for g in todo if g[2]]
        if not todo:
            print("--deep only applies to generators that read the built tree; "
                  "none selected.", file=sys.stderr)
            return 2

    print(f"{DIM}checking {len(todo)} generator(s) against src/ — "
          f"{'deep: gen → make vendor → gen' if a.deep else 'single pass'}. "
          f"Assumes a current `make vendor`.{RESET}\n")

    drifted: list[str] = []
    broke: list[str] = []
    with tempfile.TemporaryDirectory(prefix="gen-check-") as tmp:
        base = Path(tmp) / "baseline"
        base.mkdir()
        snapshot(base)
        try:
            for tool, args, reads_build in todo:
                restore(base)
                label = tool.removesuffix(".py")
                rc, msg = run(tool, args)
                if rc != 0:
                    broke.append(tool)
                    print(f"  {RED}err {RESET} {label:26} exit {rc}  "
                          f"{msg.splitlines()[-1] if msg else ''}")
                    continue
                if a.deep and reads_build:
                    rc, msg = vendor()
                    if rc != 0:
                        broke.append(tool)
                        print(f"  {RED}err {RESET} {label:26} make vendor "
                              f"exit {rc}")
                        continue
                    rc, msg = run(tool, args)
                    if rc != 0:
                        broke.append(tool)
                        print(f"  {RED}err {RESET} {label:26} second pass "
                              f"exit {rc}")
                        continue
                diff = differences(base)
                if diff:
                    drifted.append(tool)
                    print(f"  {YELLOW}drift{RESET} {label:26} "
                          f"{len(diff)} file(s) differ")
                    for line in diff[:6]:
                        print(f"        {DIM}{line}{RESET}")
                    if len(diff) > 6:
                        print(f"        {DIM}… and {len(diff) - 6} more{RESET}")
                else:
                    print(f"  {GREEN}ok  {RESET} {label:26} fixpoint")
        finally:
            restore(base)
            if a.deep:
                # The tree was rebuilt from generated src/; put it back.
                vendor()

    print()
    if broke:
        print(f"{RED}fail{RESET} — {len(broke)} generator(s) did not run: "
              f"{', '.join(broke)}")
    if drifted:
        print(f"{YELLOW}warn{RESET} — {len(drifted)} generator(s) are not a "
              f"fixpoint: {', '.join(drifted)}")
        print(f"{DIM}      A generator whose output differs from `src/` has "
              f"either drifted behind its inputs or is feeding on itself. "
              f"Re-run it deliberately and read the diff before committing — "
              f"see .docs/decisions/78-widen-attach-points-and-two-new-checks.md "
              f"for what that looked like the one time it happened.{RESET}")
    if not broke and not drifted:
        print(f"{GREEN}ok{RESET} — every generator checked reproduces src/ "
              f"exactly")
    return 1 if broke else 0


if __name__ == "__main__":
    raise SystemExit(main())
