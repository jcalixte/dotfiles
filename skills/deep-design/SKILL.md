---
name: deep-design
description: Deep thinking session that builds the project's ubiquitous language, challenges your plan against the existing domain model, sharpens terminology, and — when scope warrants — runs a goal-driven QFD cascade (Goal → Function → How → Component, with critical performances and explicit tradeoffs). Updates documentation (CONTEXT.md, DESIGN.md, ADRs) inline as decisions crystallise. Use when user wants to stress-test a plan against their project's language, design tree, and documented decisions.
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

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `DESIGN.md` exists, create one when the first Goal is resolved during a QFD cascade. If no `docs/adr/` exists, create it when the first ADR is needed.

## Goal-driven cascade (QFD)

When the session is non-trivial in scope, run the QFD cascade. This translates what the system must _be_ (user-facing goals) into what it must _do_ (functions), what we must _build_ (components), and the trade-offs we explicitly took. Output goes into `DESIGN.md` — see [DESIGN-FORMAT.md](./DESIGN-FORMAT.md).

**Trigger the cascade when:**

- A new feature or capability is being designed
- An architectural shift is on the table
- A cross-cutting concern spans multiple components
- The user explicitly says "start from the goal" / "design from scratch"

**Skip the cascade when:**

- The session is terminology cleanup only
- A single isolated decision (one ADR worth)
- A localised refactor with no user-visible behaviour change

**Interview flow** — one question at a time, codebase-first when the answer is derivable from code. Interleave with the language-sharpening behaviour below; the cascade does not replace it.

1. **Goals (WHATs).** "From the user's POV, what outcome are we delivering? How important is it (1–10)? Where is it specified?"
2. **Functions (HOWs).** "What must the system *do* to deliver G1? Each as a verb with a measurable target and a direction (↑↓→)." Probe for completeness — missing functions are the common failure mode.
3. **How.** "For F1, what are the candidate approaches? List them before picking."
4. **Components.** "Which How are we choosing? What concrete components realise it?"
5. **Importance** (when ≥2 goals and ≥3 functions). "Which functions strongly/weakly advance which goals? Score 9 / 3 / 1." Call out the upkeep cost of the matrix before producing it; offer a tree-only variant when scope is small.
6. **Conflicts.** "Does pushing F1 push another function the wrong way? Where?" Captures the roof — function-vs-function tensions.
7. **Critical performance budget.** "Rank what we just produced. For each top item, where do we watch it, and what's the fallback if we miss it?" A target without a fallback is a wish.
8. **Tradeoffs.** Every time a How is chosen over another, record `Got / Paid`. If the trade is hard-to-reverse, also offer an ADR.
9. **Tensions.** "Which conflicts are we *not* resolving now? Under what condition would we?"
10. **Inconsistencies.** Surface and record any discrepancies noticed between current claims and the code / existing docs. This is where the cascade earns its keep.

Update `DESIGN.md` inline as each level resolves. Sections are produced lazily — do not pre-populate empty sections.

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

