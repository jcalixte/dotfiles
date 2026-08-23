# SPEC.md format

One file at the repo root (or beside the feature in a multi-context repo). Fill sections as they resolve; never pre-populate empty ones.

```markdown
# <Feature name>

One paragraph: what this does and who it is for. Use the terms from CONTEXT.md verbatim.

## Behaviour

Numbered, so acceptance tests can cite them (`SPEC §3`). One observable
statement each — what is true from outside, not how it is built.

1. ...
2. ...

## Boundaries

What this feature does **not** do, and what it assumes already exists.

## Toolchain

Verified on this machine, with the versions actually found:

| | Command |
|---|---|
| Language version | |
| Build / run | |
| Test | |
| Format | |
| Lint | |

Docs: <link to the real reference, not a tutorial>

## Concepts exercised

The curriculum, in the order the ladder meets them. One line each on why
this feature needs it — a concept with no line is a concept to cut.

| # | Concept | Why this feature needs it |
|---|---|---|
| 1 | | |

## Ladder

See below.
```

# The ladder

A numbered table in `SPEC.md`, agreed before any feature code exists:

| Rung | Concept | Observable change | Command | Expected output |
|---|---|---|---|---|
| 0 | toolchain | hello-world runs | `<run cmd>` | prints `hello` |
| 1 | | | | |

Rules:

- **One** new concept per rung. New concept + new library + new tool is three rungs.
- Rung 1 passes within minutes of starting.
- Every rung leaves the project runnable.
- The expected output is written before the code. If you cannot state it, the rung is not specified yet.
- The signature or entry point each rung introduces is **the user's choice**, agreed here — the acceptance test is then written against the name they picked.

# Acceptance tests

One per rung, owned by Claude, in a directory of their own (`acceptance/`, `test/acceptance/`, or whatever the language's convention makes obvious) so ownership is visible in the diff.

```
// acceptance/rung_03_test.*   — Claude's file; the user does not edit it
// SPEC §2: a rate of 0 leaves the total untouched
test "zero rate is identity"
  assert apply_rate(total: 100, rate: 0) == 100

// SPEC §2: rates are rejected, not clamped
test "negative rate is an error"
  assert apply_rate(total: 100, rate: -1) is Error
```

Properties:

- **Derived from `SPEC.md`, never from the user's code.** They state what must be true, not how — so they cannot drift into asserting the implementation back at itself, and they do not leak the answer.
- **Red first, with a readable failure message.** That message is the spec restated at the moment it is needed. Show the failing test to the user before they start the rung.
- **Cumulative.** Rung 3's test stays green through rung 9. The regression net it builds is most of the value: it is what makes refactoring safe for someone who does not yet trust the language.
- **Behaviour only.** No private helpers, no intermediate shapes, no call counts.
- **Cite the spec clause** each assertion comes from, in a comment.
- **Not editable by the user.** If a test is wrong, they argue it and Claude changes it. Editing the test to make it pass is the one move that empties the exercise.

## When there is nothing to assert against

For a rung with no testable surface — a screen, a deploy, a manual smoke — replace the test with a scripted verification, still written before the code:

```markdown
### Rung 5 — acceptance (manual)

1. Run: `<exact command>`
2. Open: `<exact URL>`
3. Expect: <exact observable state, specific enough to be wrong>
```

## The user's unit tests

Written after the acceptance test goes green, covering the branches and edges of what they just wrote, in their own test directory. Claude reviews them and does not write them. The failure to watch for: a test that asserts the implementation back at itself. Stop on it — it is the most common learner mistake and the most expensive one to keep.
