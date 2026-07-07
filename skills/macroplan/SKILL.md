---
name: macroplan
description: Generate valid Macroplan TOML — the source file the macroplan app parses into a week-by-week delivery plan (features with an Original Estimate baseline, re-estimate slips, deliveries, learnings, statuses, and milestones). Use when the user wants to author, draft, or scaffold a macroplan plan file, or invokes /macroplan with a description of what to plan.
---

# Generate Macroplan TOML

Turn a plan description into valid Macroplan TOML the app can parse. **Output only a single ```macroplan code block** (macroplan-fenced, TOML syntax inside) ready to paste into the app's editor or save as a `.toml` file — no surrounding prose unless the user asks for an explanation.

If the user hasn't given you a feature's `start` or `original` date, ask for it (or restate a sensible assumption and proceed). Never invent a `delivered` date — a feature is delivered only if the user says so.

## Schema (authoritative)

A machine-readable JSON Schema ships next to this skill as `macroplan.schema.json` (kept in sync with `public/macroplan.schema.json` in the macroplan repo) — read it when you need the exact validation rules beyond the summary below.

Top-level keys:

- `title` — string. Always include one; defaults to `"Untitled Macroplan"` if omitted.
- `start` — optional date. The plan's left edge. Must be **≤ every feature's `start`**.
- `end` — optional date. The plan's right edge. Must be **≥ every feature's last week** (last re-estimate, delivery, or original — whichever is latest). Omit both `start`/`end` to auto-fit columns to the features and milestones.

`[[feature]]` blocks (one per feature, in author order — usually earliest `start` first):

| Key | Type | Required | Meaning |
| --- | --- | --- | --- |
| `name` | string, non-empty | yes | Feature name. Milestones reference this exact string. |
| `start` | date | yes | First week of the feature's bar. |
| `original` | date | yes | Original Estimate — the immovable baseline on-time/late is judged against. |
| `reestimates` | array of dates | no | Later revised delivery weeks (slips), chronological. Each later than `original`. |
| `delivered` | date | no | The week it actually shipped. Omit while in-flight. |
| `learning` | string | no | Takeaway captured after delivery. |
| `status` | `"on-track"` \| `"at-risk"` \| `"off-track"` | no | In-flight confidence. Omit once `delivered` is set. |
| `note` | string | no | Short comment, typically paired with `status`. |

`[[milestone]]` blocks:

| Key | Type | Required | Meaning |
| --- | --- | --- | --- |
| `name` | string, non-empty | yes | Milestone label. |
| `week` | date | yes | The week the milestone falls on. |
| `requires` | array of strings | no | Exact `name`s of features that must be delivered by `week`. |

### Dates

- Write dates as **unquoted TOML date literals**: `2026-06-15`. Arrays too: `reestimates = [2026-06-29, 2026-07-13]`.
- Any day snaps to that week's **Monday**, so the exact weekday doesn't matter — but prefer Mondays for readability.

## Authoring rules (don't get these wrong)

- **Never move `original`.** To show a plan slipping, append to `reestimates`; the baseline stays put.
- **Never author on-time vs. late.** The app derives it by comparing `delivered` against `original` (on/before → on-time, after → late). You only supply the dates.
- **`status` is in-flight only.** Once a feature has `delivered`, drop `status`/`note` and use `learning` instead — a delivered feature carries no status.
- **`reestimates` are for real slips**, each strictly later than `original` and in chronological order.
- **No "now" field.** The current-week line is derived from today's date, not authored.
- **`requires` must match feature `name`s exactly** (case-sensitive), or the milestone silently requires nothing.
- An **overdue** feature (past its latest estimate, undelivered) isn't a special field — express it with `status = "at-risk"` or `"off-track"` and a `note`.

## Minimal template

```macroplan
title = "My plan"

[[feature]]
name = "First feature"
start = 2026-06-01
original = 2026-06-15
```

## Worked example (covers every state)

```macroplan
title = "Q3 — Checkout revamp"

# Optional span: start ≤ every feature start, end ≥ every feature's last week.
start = 2026-05-25
end = 2026-08-03

[[feature]]
name = "Auth"
start = 2026-06-01
original = 2026-06-15
delivered = 2026-06-15          # on/before original → on-time
learning = "Discovery spike first paid off — do them earlier."

[[feature]]
name = "Payments"
start = 2026-06-01
original = 2026-06-15
reestimates = [2026-06-29, 2026-07-13]   # two slips
delivered = 2026-07-20          # after original → late
learning = "Vendor lead time was the constraint — derisk vendors up front."

[[feature]]
name = "Dashboard"
start = 2026-06-01
original = 2026-06-08           # past 'now', undelivered → overdue
status = "off-track"
note = "No recovery plan yet — needs an owner."

[[feature]]
name = "Search"
start = 2026-06-08
original = 2026-06-22
reestimates = [2026-07-06]      # slipped once, still in flight
status = "at-risk"
note = "Third-party search API is flaky; spike a fallback."

[[feature]]
name = "Notifications"
start = 2026-06-22
original = 2026-07-06
status = "on-track"

[[milestone]]
name = "MVP go-live"
week = 2026-07-06
requires = ["Auth", "Payments", "Dashboard"]
```

## Before returning, check

1. Every `[[feature]]` has `name`, `start`, `original`.
2. Dates are unquoted literals; `reestimates` (if any) are chronological and later than `original`.
3. No feature has both `delivered` and `status`.
4. If `start`/`end` are set, they enclose every feature's span; otherwise omit them.
5. Every `requires` entry matches a feature `name` exactly.
6. Output is a single ```` ```macroplan ````-fenced block of valid TOML and nothing the parser would reject.
