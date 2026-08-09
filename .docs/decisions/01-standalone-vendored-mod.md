# 01 — Standalone, self-contained mod

**Decided:** 2026-08-01

STG is a single standalone mod with no dependencies. Enabling it is the only
thing in the playset. Subscribing to or unsubscribing from anything on the
Workshop must not change how STG behaves.

**Why:** it is a personal mod for one machine, and a playset that depends on
dozens of Workshop subscriptions (48 today) is a playset that breaks whenever an
author updates, delists, or abandons something.

**Consequence:** everything STG uses is vendored into the tree. There is no load
order to lean on — whatever we don't ship, we don't have. That merge is driven by
`vendor.yml` and `make vendor` rather than by hand, so it stays reproducible and
auditable across Stellaris patches. See plan.md §2.

Superseded an earlier draft that proposed a thin layer over a curated playset.
That draft was written before the standalone requirement was known.
