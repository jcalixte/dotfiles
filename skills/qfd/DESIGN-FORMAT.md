# DESIGN.md Format

`DESIGN.md` is the **goal-driven design artifact** produced by the `walk-with-me` skill via a QFD (Quality Function Deployment) cascade. It translates what the system must _be_ (user-facing goals) into what it must _do_ (engineering functions), what we must _build_ (components), and the trade-offs we explicitly took.

Where it lives mirrors `CONTEXT.md`:

- **Single context repo**: `DESIGN.md` at the repo root.
- **Multi-context repo**: one `DESIGN.md` per context, alongside the context's `CONTEXT.md` (e.g. `src/ordering/DESIGN.md`). System-wide design (cross-context) belongs at the root if it exists at all.

Create it **lazily** — only when the first Goal is resolved in a session. Do not pre-populate empty sections.

## Structure

Sections appear in this canonical order. Sections marked _(optional)_ are included only when the session actually resolved them — never as empty placeholders.

```md
# {Context} — Design (QFD)

{One-paragraph scope statement: what this document is about, what it isn't,
and what it relies on (CONTEXT.md, ADRs, product / roadmap docs).}

Strength weights used in matrices: **9** strong, **3** medium, **1** weak, blank none.

---

## 1. Goals — the WHATs

User-facing requirements with importance weights on a 1–10 scale.
Source column points at the doc the requirement comes from.

| ID  | Goal                       | Weight | Source              |
|-----|----------------------------|:------:|---------------------|
| G1  | {user-facing outcome}      |   10   | [link to source]    |
| G2  | …                          |    8   | …                   |

_(optional)_ When several user segments would weight the goals differently,
name the segments first and derive goal weights instead of asserting them:

| ID  | Segment                | Weight (1–5) |
|-----|------------------------|:------------:|
| U1  | {who}                  |      5       |

Goal weight = Σ(segment weight × strength 9/3/1), normalised to 1–10. Skip
this block when one user is in mind — a single asserted weight is enough.

## 2. Functions — the HOWs

Measurable engineering characteristics. Direction shows what "better" means
(↑ higher, ↓ lower, → fixed). Targets may be staged across releases.

| ID  | Function                  | Dir | Target (now) | Target (future) |
|-----|---------------------------|:---:|--------------|-----------------|
| F1  | {verb-form responsibility}|  ↓  | ≤ 200 ms     | ≤ 150 ms        |

## 3. Competitive assessment   _(optional)_

How the alternatives — a competitor, the current system, do-nothing —
perform against what we're designing. Two views; produce only what the
session actually benchmarked.

**Goal ratings** — perception per alternative, 0–5 per goal (this is the
house's perception zone):

| Goal | Us (target) | {Current system} | {Alternative B} |
|------|:-----------:|:----------------:|:---------------:|
| G1   |      4      |        2         |        3        |

**Function benchmarks** — measured values per function where known. A number
beats a rating; a blank beats a guess:

| Function | Us (target) | {Current system} | {Alternative B} |
|----------|-------------|------------------|-----------------|
| F1       | ≤ 200 ms    | 450 ms           | 180 ms          |

**What this tells us:** where the alternatives already beat our targets, and
which goal weights this evidence confirmed or changed.

## 4. Cascade — Goals → Functions → How → Components

The spine of the design. Hierarchical tree, readable top-down.

- **G1** {goal}  _W:10_
  - **F1** {function}  _Dir↓ Target ≤200ms_
    - **How**: {approach A}
      - **Component**: {concrete part}
    - **How**: {approach B — rejected, see T1}

## 5. House — Goals × Functions   _(optional)_

Cells: link strength (9/3/1/blank). Importance row = `Σ(weight × strength)`.

|          | F1 | F2 | F3 |
|----------|:--:|:--:|:--:|
| G1 (10)  |  9 |    |  3 |
| G2 (8)   |    |  9 |    |
| **Σ**    | 90 | 72 | 30 |
| **Rank** |  1 |  2 |  3 |

**Top engineering priorities (from importance):** short commentary on which
functions deserve the most attention and why.

## 6. Roof — Function × Function tradeoffs   _(optional)_

Where pushing one function pushes another the wrong way (or reinforces it).
Symbols (single-character, classical QFD): `◎` strong reinforcement, `○` mild reinforcement, `×` mild conflict, `⊗` strong conflict.

|        | F1 | F2 | F3 |
|--------|:--:|:--:|:--:|
| **F1** | —  | ○  | ×  |
| **F2** |    | —  | ◎  |
| **F3** |    |    | —  |

**Conflicts that actually shape the design:** bullets on the conflicts that matter,
how they're being mitigated, and which ADR (if any) owns the resolution.

## 7. Components & Function → Component map   _(optional)_

Component list with anchoring ADR per row:

| ID  | Component               | ADR     |
|-----|-------------------------|---------|
| C1  | {module / service / lib}| ADR-NNN |

Function-to-component strength matrix (9/3/1/blank). When §5 exists, carry
the cascade down: component Σ = `Σ(function Σ from §5 × strength)` — so
component priorities are derived, not asserted.

|          | C1  | C2  | C3  |
|----------|:---:|:---:|:---:|
| F1       |  9  |  3  |     |
| F2       |     |  9  |  3  |
| **Σ**    | 810 | 918 | 216 |
| **Rank** |  2  |  1  |  3  |

**Where the engineering effort goes:** short commentary on the top-ranked
components — and a flag if the ranking disagrees with where effort is
currently being spent.

## 8. Critical performance budget

Pulled from §5 importance and §6 conflicts, ranked. Each row names the
fallback / kill-switch if the target is missed — a target without a
fallback is a wish, not a budget.

| Rank | Function | Target | Watched on | If we miss it           |
|------|----------|--------|------------|-------------------------|
| 1    | F2       | …      | bench / metric / spike | fallback or kill-switch |

## 9. Tradeoffs — Got / Paid / ADR

Plain-language ledger of what was accepted in exchange for what. Every row
names what was bought *and* what was paid. Link to an ADR when the trade is
hard-to-reverse — the ADR remains the authoritative record of the decision.

| ID  | Tradeoff                | Got                  | Paid                  | ADR     |
|-----|-------------------------|----------------------|-----------------------|---------|
| T1  | Chose A over B          | latency, simplicity  | feature X deferred    | ADR-004 |

### Tensions being watched (unresolved by design)

Live conflicts we are *not* deciding harder yet — documented as deliberate
deferrals, each with the trigger that would force a decision.

- **{conflict}.** {what we're doing instead}. **Trigger to revisit:** {condition}.

## 10. Inconsistencies spotted and fixed

Discrepancies surfaced during the session — between docs, between code and
docs, between code and stated intent — and how they were resolved. This is
the audit trail of what the walk-with-me session actually caught.

- **{discrepancy}.** {resolution}.

---

## How to keep this honest

- When a new ADR lands → add its components to §7 and re-score affected rows.
- When a spike / measurement returns numbers → update §3 benchmarks and §8 `Target` / `Watched on`.
- WHATs change rarely; HOWs change with each release; matrices are recomputed
  when either side changes.
- If a section becomes empty after edits, delete it — empty sections lie.
```

## Rules

- **Goals are user-facing outcomes**, never implementation. Weight (1–10) and `Source` link are required.
- **Functions are verbs with measurable targets and a direction.** Multi-stage targets are encouraged so the doc shows trajectory.
- **The cascade tree (§4) is the spine.** It's the only required structural section beyond §1 and §2. Matrices (§§5–7) and the competitive assessment (§3) are produced only when the session resolved them.
- **§3 records evidence, not guesses.** Measured benchmark values beat 0–5 ratings; a blank cell beats a made-up number.
- **Don't pre-populate empty sections.** Sections appear when content exists. If a section becomes empty after edits, delete it.
- **Group long levels.** When Goals or Functions grow past ~7 rows, group them under short theme headings (a bold full-width row in the table, a sub-bullet level in the tree). Matrices stay flat.
- **§8 must include `If we miss it`** — the fallback / kill-switch column is mandatory for every row.
- **§9 uses `Got / Paid / ADR`** — lean framing. Both sides of every trade are named.
- **§10 (inconsistencies) is the audit trail.** Every discrepancy surfaced during the session lands here with its resolution, even if small.
- **Maintenance footer is required** (not optional). The doc decays silently without it.
- **Lazy creation.** Create `DESIGN.md` only when the first Goal resolves. Same rule applies recursively to its sections.

## When to produce matrices vs tree only

Matrices (§§5–7) have real upkeep cost in markdown. Produce them when:

- There are ≥2 goals and ≥3 functions (the matrix actually reveals priorities the tree hides).
- Inter-function conflicts are likely to shape the design (the roof is the point).
- Multiple components share responsibility for the same function (the function→component map prevents drift).

Otherwise the cascade tree (§4) + critical performance budget (§8) + tradeoffs (§9) is enough. The skill should call out the upkeep cost before producing matrices and offer a tree-only variant when scope is small.

## Relationship to other artifacts

- **`CONTEXT.md`** owns the glossary. Goals, Functions, Components are *named* in `DESIGN.md`; their _terms_ (when they introduce new vocabulary) are defined in `CONTEXT.md`. Never duplicate definitions across the two.
- **ADRs** own hard-to-reverse decisions. `DESIGN.md` references ADRs from §7 (component anchors) and §9 (tradeoff rows). The ADR is the authoritative record; `DESIGN.md` is the index that shows how the decision fits into the cascade.
- **`CONTEXT-MAP.md`** (multi-context repos) lists where each `CONTEXT.md` / `DESIGN.md` pair lives.
