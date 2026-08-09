# 04 — No source-mod archive; the deployed mod is the backup

**Decided 2026-08-01. SUPERSEDED the same day by
[09 — The build reads `.source/`, not `/workshop`](09-source-snapshot.md).**

> **Do not act on this file.** There *is* a source archive now — `.source/`,
> built by `make sources-sync`, and it is what `make vendor` reads. Decision 09
> has the current rules. This one is kept for why it was wrong.

## What it decided

Git tracks `vendor.yml` and `src/` only; no copy of the source mods is kept
outside `/workshop`. The risk accepted knowingly: `/workshop` exists only while
you are subscribed on Steam, so unsubscribing from a source mod would make a
from-scratch rebuild impossible. The mitigation was "the deployed mod is the
backup" — don't wipe it casually.

## Why it was wrong

The copy turned out to be **free**. `/workshop` and this repo are the same btrfs
subvolume, so a reflink snapshot of all 18.7 GB takes 21 s and consumes no
measurable disk. The risk was being carried for nothing.

The mitigation was also unsound. A deployed mod is a 17 GB *output*: you cannot
re-run a merge from it, diff it against an upstream update, or tell which of
23,507 files came from where. It backs up playing, not building.

And the larger risk went unlisted entirely — with `/workshop` as the build input,
any `make vendor` silently picks up whatever Steam last downloaded.

**The lesson:** this file accepted a risk without checking what avoiding it would
cost. The measurement took two minutes and reversed the decision.
