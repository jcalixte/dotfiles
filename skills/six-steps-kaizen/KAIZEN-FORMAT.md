# Kaizen document format

One kaizen = one file, `docs/kaizen/<slug>.md`. Fill sections as the steps resolve — never pre-populate empty sections.

```markdown
# Kaizen — <short problem name>

<One-line statement of the problem and the client/user it affects.>

## 1) Improvement potential

**Value model for <client name>**

| Want more of | Do less of |
|---|---|
| + … | – … |
| + … | – … |

**Measurement**: <unit of measurement>

| Current method | Target (new method) |
|---|---|
| <value> | <value> |

## 2) Current method analysis

<Diagram of the situation (mermaid or ASCII art), weak points called out.>

| Factor # | Factor | Hypothesis | Test method | Test result | True or false? |
|---|---|---|---|---|---|
| 1 | … | … | … | … | … |

### Details on hypothesis #X

<Further explanations, data, screenshots.>

**Selected weak point**: <the one weak point this kaizen addresses>

## 3) Ideas

### Bibliography

- <link to state-of-the-art article on the studied problem>

### New ideas

| Name | Estimated gain | Estimated lead time | Cause addressed | Comments |
|---|---|---|---|---|
| … | … | … | … | … |

**Chosen idea**: <name> — <why it won>

## 4) Test plan

**What could go wrong?**

| Lens | Anticipated consequence | Mitigation |
|---|---|---|
| … | … | … |

**Who must we convince?**

- <person / role> — <about what>

<If applicable: rollback procedure, training needed, implementation checklist, measurement protocol.>

## 5) Implementation

**Before**

…

**After**

…

## 6) Evaluation

**Measurement redone** (<unit>): <old value> → <new value> (target was <target>)

**Learnings**: …

**Standard to update**: …

**Share with**: …

**Next steps**

- …
```
