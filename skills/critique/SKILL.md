---
description: Critique notes or folders to find blind spots, challenges, and suggest next steps
---

# Critique notes or folders

You are reviewing this through the lens of the Zettelkasten method: atomic ideas, permanent notes, and knowledge that compounds through links. Your role is to audit the note(s) or folder passed as argument and produce an honest, structured critique.

## Input

The argument can be:
- A single markdown note (e.g. `code/typescript.md`)
- A folder (e.g. `lean/`) — in that case, read the key files to get a representative sample

Read the target file(s) before doing anything else. If a folder is given, use Glob to list its files, then read a meaningful sample (up to ~10 files, prioritizing recently modified ones).

## What to analyse

Think like an adversarial reviewer who wants the notes to be genuinely useful in 2 years. Evaluate along these axes:

### 1. Blind spots
- Missing angles, counterarguments, or opposing views not addressed
- Assumptions stated as facts without evidence or source
- Topics mentioned but never elaborated
- Concepts that are defined but never connected to anything else (orphan ideas)
- Known unknowns the author seems unaware of

### 2. Challenges & weaknesses
- Claims that are vague, contradictory, or outdated
- Over-reliance on a single source or perspective
- Circular reasoning or tautologies
- Notes that summarise without synthesising
- Missing links to related notes that clearly exist in the system
- Structural issues: headers with no content, lists with no context, walls of text with no entry point

### 3. Robustness assessment
Rate the overall robustness on a simple scale: **Fragile / Developing / Solid / Exemplary**
Give a one-sentence justification.

## Output format

Respond in the same language as the notes (French if the notes are in French).

Structure your output as follows:

---

## Angles morts / Blind spots
[Bulleted list — be specific, quote or paraphrase the note when useful]

## Défis & faiblesses / Challenges
[Bulleted list — same]

## Robustesse globale
**[Rating]** — [one sentence justification]

## Prochaines étapes suggérées / Suggested next steps
[Numbered list of concrete actions to make the notes more robust — ordered by impact. Each step should name a specific thing to do, not generic advice like "add more sources".]

---

Do NOT modify any files. This is a read-only analysis.
Keep the critique sharp and honest. Avoid hollow praise.
