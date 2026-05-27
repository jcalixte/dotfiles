---
name: walk-with-me
description: Deep thinking session that builds the project's ubiquitous language, challenges your plan against the existing domain model, and sharpens terminology. Updates CONTEXT.md (and ADRs when warranted) inline as decisions crystallise. Use when stress-testing terminology against the existing glossary. For goal-driven design decomposition (Goal → Function → How → Component, with critical performance budget and explicit tradeoffs), run `/qfd` instead.
---

<what-to-do>

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead.

</what-to-do>

<supporting-info>

## Domain awareness

During codebase exploration, also look for existing documentation:

### File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── DESIGN.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   ├── DESIGN.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       ├── DESIGN.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## When to escalate to `/qfd`

This skill stops at language and decisions. When the session moves into goal-driven design — a new feature, an architectural shift, a cross-cutting concern, or any non-trivial change whose goals haven't been explicitly decomposed — run `/qfd`. It shares this skill's language discipline, then drives a Goal → Function → How → Component decomposition into `DESIGN.md`.

## During the session

### Ubiquitous language

`CONTEXT.md` is the project's **ubiquitous language** — the shared vocabulary that should appear verbatim in conversation, code, tests, commit messages, and docs. The behaviours below all serve this principle: surfacing gaps between how the team speaks and how the code is named, then closing them by renaming the code, renaming the term, or recording the discarded word as an alias-to-avoid.

A useful smell: if you find yourself "translating" between what was said and what the code calls it, the language has drifted. Stop and resolve it.

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

</supporting-info>

