# Defense in Depth

## Overview

Once you've found and fixed a bug at its source (`root-cause-tracing.md`), ask a
second question: *could this class of bad value get in through another door?*
Defense in depth adds validation at multiple layers so a single missed check
doesn't become a production incident.

**Core principle:** fix the root cause first, THEN add layered guards. Guards are
insurance, not the fix.

**A guard is not a substitute for fixing the source — it's a backstop for the
sources you haven't found yet.**

## The Ordering Rule

```
1. Fix the source (root-cause-tracing.md)
2. THEN add validation at the layers that should have caught it
```

Never reverse this. A guard added *instead* of a source fix silently swallows the
bug — the value is still wrong, you just stopped seeing the crash. That's the
symptom fix this whole skill exists to prevent.

## Where to Add Layers

Add validation at each boundary the bad value crossed on its way to the crash.
Each layer answers "is this input valid for what I'm about to do with it?"

- **Ingestion boundary** — parse/validate external input (request body, file,
  env var, DB row, third-party response) into a known-good shape. Reject or
  normalize at the door.
- **Trust boundary** — where data crosses from untrusted to trusted (API → domain
  logic, user → privileged operation). Assert invariants here.
- **Contract boundary** — public function / module entry points assert their
  preconditions instead of assuming callers behaved.
- **Persistence boundary** — validate before writing; a bad value in the DB
  becomes tomorrow's mystery bug.

You rarely need all four. Add the ones the bad value actually passed through, and
prefer the layer closest to the source.

## Fail Loud, Not Silent

The point of a guard is to surface the problem sooner and clearer, not to hide it.

| Bad guard (hides) | Good guard (surfaces) |
|---|---|
| `plan ?? 'free'` (masks missing plan) | `if (plan == null) throw new Error('plan missing for user ' + id)` |
| `catch { return [] }` | `catch (e) { log.error(...); throw }` |
| silently clamp out-of-range value | reject with a message naming the value and expected range |

Defaults are appropriate when the default is genuinely correct domain behavior —
not as a way to avoid dealing with an unexpected value. If you don't know why the
value is bad, don't paper over it with a default.

## How Much Is Too Much

Layered validation has a cost: redundant checks, noise, and the false comfort of
"we validate everywhere." Guard against:

- Re-validating the same invariant five times in one call chain — validate once
  at the boundary, then trust internally.
- Guards that duplicate the type system — if the type already guarantees it,
  don't re-check at runtime (unless it's a real trust boundary).
- Guards so defensive they hide legitimate bugs during development.

Rule of thumb: validate at boundaries you don't control, trust within boundaries
you do.

## Checklist

- [ ] Source fixed first (not replaced by a guard)
- [ ] Identified which boundaries the bad value crossed
- [ ] Added validation at the boundary closest to the source
- [ ] Guards fail loud (throw/log), not silent (default/swallow)
- [ ] No redundant re-validation of already-guaranteed invariants
- [ ] A regression test proves the guard fires (see `agent-skills:test-driven-development`)
