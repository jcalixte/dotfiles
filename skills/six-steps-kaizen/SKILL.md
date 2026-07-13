---
name: six-steps-kaizen
description: 6-steps Kaizen — a lean problem-solving and continuous-improvement frame. Discover the improvement potential → analyse the current method → generate ideas and choose one → develop a test plan → implement → evaluate. Drives the user through the steps one at a time and lands the result in a kaizen document. Use when the user wants to run a kaizen, improve a process/metric, or do structured continuous improvement on a recurring problem.
---

<what-to-do>

Drive the user through the six kaizen steps, in order, landing each step in a kaizen document as it resolves. Ask questions one at a time and wait for the answer before continuing. For each question, provide your recommended answer when you can derive one.

If a question can be answered by exploring the codebase, metrics, or existing docs, explore instead of asking.

Do not skip steps and do not let the user jump to solutions: if they arrive with an idea already chosen, park it as a step-3 candidate and still run steps 1 and 2 — an idea that doesn't address a verified cause is a solution looking for a problem.

The document lives at `docs/kaizen/<slug>.md` by default (create the directory lazily); confirm the location when creating it. Use the section structure in [KAIZEN-FORMAT.md](./KAIZEN-FORMAT.md). Fill sections lazily — never pre-populate empty ones.

</what-to-do>

<supporting-info>

## The frame in one line

Kaizen brings value to the customer by making the job of the people doing the work (gemba) easier — one small, focused, measured improvement at a time.

## Step 1 — Discover the improvement potential

- Start from the client/user **value model**: "What does <client> want more of?" and "What should we do less of?"
- Within everything that could be improved, what does *this* kaizen relate to?
- Pin down the **measurement**: a unit, the current value, and the target. This becomes the improvement-potential baseline that step 6 re-measures. No measurement, no kaizen — push until one exists, even a rough proxy.
- If you chart the potential (mermaid xychart works well): bar the **current value only**, with the target as a line. The after-kaizen slot stays **empty forever** — it is potential, not result; the measured after-bar belongs in step 6 and nowhere else.

## Step 2 — Analyse the current method

- **Draw the situation** (a mermaid diagram or ASCII art both work — ASCII renders anywhere, mermaid needs a viewer). Mark the weak points — the parts that are slower or break more often.
- An analysis is breaking the problem down into **factors**. For each factor, formulate a hypothesis on what sub-parameter could drive performance, and how to verify it:

| Factor # | Factor | Hypothesis | Test method | Test result | True or false? |
|---|---|---|---|---|---|

  A good test method states exactly which variables are altered and what result is expected under each variation (e.g. brew at 95°C vs 65°C, compare tastes).
- Actually run or help run the tests — a hypothesis column full of "untested" is not an analysis.
- To improve with baby steps, **select one weak point** to address in this kaizen. One.

## Step 3 — Generate original ideas and choose one

1. Diverge first: be quantitative, welcome the craziest ideas, never judge during generation.
2. Then check every idea **addresses an actual cause** (a factor verified true in step 2) — not just a solution someone finds interesting.
3. Evaluate the rational ideas against criteria:

| Name | Estimated gain | Estimated lead time before change is done | Cause addressed | Comments |
|---|---|---|---|---|

   Add columns as needed — cost is a good one.

Don't forget to:
- Look at what the best/other companies do to solve similar problems (keep a short bibliography of sources).
- Prefer ideas that **prevent the issue from ever coming back**.

## Step 4 — Develop a test plan

The goal of kaizen is not making plans — but the bigger the idea, the bigger the plan. This step is **not** about describing how to implement the idea; it's about how to overcome the blockers that will stop the action.

The 2 mandatory questions:

1. **What could possibly go wrong?** Think through consequences of the selected idea. Stress-test it with a prototype (never in production), and learn how to mitigate the risks.
2. **Do you need to convince someone?** Kaizen often needs negotiation and cooperation with people outside the team. This is where to stop going deep and start expressing leadership. List who must be convinced.

Sometimes you need to go further:
- Change outside the common workflow → what is the **rollback procedure** if it causes a regression?
- Not everyone was at the workshop → **who needs training**?
- Idea not "just do it" → what is the **implementation plan** (design + technical checklist)?
- Measuring is hard → prepare a **protocol** for when and how to evaluate results.

Prompts for anticipating consequences — pick whichever lens fits:
- **3S**: Stable, ⚡ Speed, 🛡 Secure (e.g. "regression because of backward compatibility")
- **4M**: Man, Material, Method, Machine (e.g. "the front-end tech lead may not be aware the change breaks our API")
- **Lean indicators**: Safety, Quality, Lead Time, Cost, Environment

## Step 5 — Implement the plan

Show **WHAT** changed in the system — not how well it performs:
- A before/after comparison (drawing, screenshot, code diff — inline the diff, don't just link a PR URL).
- If a diagram was drawn in step 2, redraw it with the change applied.

Do **not** show a measurement here. Evaluation is step 6, and mixing the two hides implementation problems behind good-looking numbers (or vice versa).

## Step 6 — Evaluate the new method

- Redo the **step 1 measurement** after the change has expressed itself — sometimes you must wait for the improvement to reach its potential. Record old vs new value against the target.
- If step 1 had a chart, **redraw it here** with the measured after-bar filled in (before + after bars, target line). Never back-fill the step-1 chart — it stays potential-only.
- Then reflect:
  - What did you learn?
  - What do you want to do next? (next steps list)
  - What **standard** should be updated so the gain sticks?
  - With whom should the findings be shared?

## Common failure modes to catch

- Skipping the measurement in step 1 ("we'll know it when we see it") — then step 6 is impossible.
- Analysis that lists opinions instead of tested hypotheses.
- Ideas that don't map to any verified cause.
- Attacking several weak points at once instead of one.
- Showing a metric in step 5, or a diff in step 6 — the separation is the point.

</supporting-info>
