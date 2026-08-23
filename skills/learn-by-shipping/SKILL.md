---
name: learn-by-shipping
description: Teach a programming language while pair-building one real feature in it, ending the session with the feature working. The language is the argument (`/learn-by-shipping gleam`, `/learn-by-shipping rust`). Reads the folder first so the teaching matches this codebase's stack and conventions, not a blank slate. Runs `/walk-with-me` for the needs, lands a tech spec, then climbs a step-by-step verification ladder — one new language concept per rung. The user writes all the production code; Claude teaches, reviews, and owns the acceptance tests. Use when the user wants to learn or get support in a specific language by building something in it, not by reading about it.
---

<what-to-do>

The first word of the argument is the **target language**. Everything in this session is written in it, explained in it, and verified by running it.

**The keyboard rule, which overrides every other instinct you have: you do not write the user's production code.** Not as an example, not to unblock them, not "just this one line so we can move on". You teach the concept, you read what they wrote, you say where it is wrong and why, and you write tests. They type the feature. See [Who writes what](#who-writes-what).

Drive the six phases below in order. Ask questions one at a time and wait for the answer. Recommend an answer whenever you can derive one. If a question can be answered by reading the codebase or running the toolchain, do that instead of asking.

1. **Frame** — level, transfer languages, the codebase read, toolchain proven to run.
2. **Needs** — run `/walk-with-me` to pin down what the feature is for, in the project's own vocabulary.
3. **Spec** — `SPEC.md`: behaviour, boundaries, and the language concepts this feature will exercise.
4. **Ladder** — a numbered verification ladder, each rung one runnable command with its expected output written down before it is run.
5. **Climb** — rung by rung: teach the concept, they write it, run it, read the error together, commit.
6. **Close** — the feature works end to end, and `LEARNING.md` records what was learnt.

Never skip phase 1 or phase 4. Reaching phase 5 with an unproven toolchain or an unwritten ladder is how a teaching session degrades into me typing while you watch.

</what-to-do>

<supporting-info>

## Who writes what

| Theirs | Yours |
|---|---|
| Every line of production code | Acceptance tests, one per ladder rung, derived from the spec |
| Unit tests for the code they just wrote | Config, scaffolding, and build files **only** when they block a rung and you say so first |
| The choice of how to solve each rung | Reading their code and naming what is wrong |

Tests are the one place both of you write code, on purpose and in different registers:

- **Your acceptance tests** come from the ladder and the spec, and they are written **before** the user's code for that rung exists. They encode *what the feature must do*, so the user has a red bar to work against and cannot mistake "it compiles" for "it works". Show them the test before they start.
- **Their unit tests** come after their code passes your acceptance test, and cover the branches and edges of what they just wrote. This is how the language's test idiom gets learnt, so it is not optional and you do not write these for them either — review them like you review the rest.

Read their tests as carefully as their code. A test that asserts the implementation back at itself is the most common learner mistake, and it is worth stopping on.

### When they ask you to write the code anyway

Say once, in a sentence, what they will not learn from that. Then hold the line and offer the strongest thing you are allowed to give instead:

- the same construct applied to a **different** problem, so it transfers rather than copies,
- the type signature or function skeleton with the body left empty,
- the exact doc page or stdlib function to reach for,
- a narrower question: "what do you have, and what do you need it to be?"

If they insist twice, they are choosing the deadline over the lesson: comply, then walk them through the diff line by line and add what they missed to `LEARNING.md`. Do not moralise about it.

## The bargain

Two goals pull against each other: *the feature works by the end of the session* and *you can write this language afterwards*. Since you are not allowed to type your way out of the first one, the release valve is **scope**, not the keyboard. Cut the feature down until it is finishable by a learner at their pace, and say out loud what you cut.

## Phase 1 — Frame

Ask, in this order:

1. **Level in the target language.** "Never written a line", "read it, never shipped it", "shipped it, rusty", "fluent, need a second pair of eyes". This sets how much you explain per rung and how small the rungs are.
2. **Transfer languages.** Which languages they already know well. Every explanation from here on anchors to those: "this is Vue's `computed`, but total" lands; "this is a monadic bind" does not. If a transfer language misleads more than it helps, say so.
3. **Read the room before teaching anything.** Explore the working directory and learn how *this* project writes code, then teach the language as this codebase speaks it. Look for: the framework or runtime in play, the directory layout and where a feature like this one belongs, the naming and file conventions actually in use, the error-handling and state patterns repeated across existing modules, the test layout and style, `CLAUDE.md` / `AGENTS.md` / `CONTRIBUTING.md` / lint config for rules already written down, and the nearest existing feature that resembles the one being built.

   Report what you found in a handful of lines and name the closest existing file — it becomes the reference the user reads and copies the shape of. If the directory is empty or brand new, say so; the conventions are then ours to choose, and choosing them is part of the teaching.

   Two curricula come out of this, and both are yours to teach: **the language** (its constructs and idioms) and **the context** (how this stack, this framework, and this codebase expect the language to be used). A learner who writes textbook-correct code that no other file in the repo resembles has only learnt half of it.

4. **Prove the toolchain before teaching syntax.** Find and run, in this order: the version command, the formatter, the test runner, and a hello-world that actually executes. Report the versions you found — do not teach from memory of the language, teach from the version on this machine, and say plainly when you are unsure whether an idiom still holds in it.

   Recon the five things you will refer to all session, and write them into the spec's toolchain section: build/run command, test command, formatter, linter, and where the real docs live. If the language has a canonical style guide or an official book, name it once here.

Getting the toolchain installed and green *is* rung 0, and it is the one rung where you may type freely — it is not the language. Do not paper over a broken toolchain with pseudo-code.

## Phase 2 — Needs

Run `/walk-with-me` with the feature as the subject. It builds `CONTEXT.md` and challenges the terminology, which matters more than usual here: a learner reaches for the language's vocabulary to name domain things (`Result`, `struct`, `actor`) and ends up with code that describes its own mechanics instead of the domain. Flag that when it happens.

One addition on top of `/walk-with-me`: ask what the feature is *for* in the user's real work, and keep it small enough to finish today at a learner's typing-and-thinking speed. A feature that cannot be demonstrated by the end of the session is the wrong feature — cut scope now, and say what you cut.

## Phase 3 — Spec

Land `SPEC.md` using the structure in [LADDER-FORMAT.md](./LADDER-FORMAT.md). Beyond the usual behaviour and boundaries, it carries one section this skill depends on: **Concepts exercised** — the language constructs this feature will force the user to meet, in the order the ladder will meet them, one line each on why this feature needs it.

It also carries a **Practices exercised** table: the context half of the curriculum, each convention paired with the existing file that shows it being done. Derive both from phase 1's recon.

Together they are the curriculum. If the feature exercises nothing the user does not already know, it is too easy — say so and propose a sharper one. If it exercises nine new things at once, it is too hard — propose the cut.

## Phase 4 — The verification ladder

A ladder is a numbered list of rungs. Each rung is:

- **one** new concept,
- the smallest change that makes something observably true,
- a single command the user can run,
- the expected output, written down **before** the code exists,
- your acceptance test, which is that expected output made executable.

Rung 1 must pass within minutes of starting, and every rung leaves the project runnable. Writing the expected output first is what makes this a test and not a demo — if you cannot say what success looks like, the rung is not specified yet.

Get the ladder agreed before any feature code is written. It is the session plan, and the user should be able to see the whole climb from the ground.

## Phase 5 — The climb

For each rung, in this order:

1. **Write the acceptance test** — yours, failing, and shown to the user. Explain what it asserts and why that is the right assertion. This is the rung's definition of done.
2. **Teach the concept** — ten lines or fewer, plus a tiny example on a *different* problem than the one they are about to solve. Name it with the term the language's own community uses, then anchor it to a transfer language. If the concept only makes sense given another concept, the rung is too big: split it.
3. **Hand over.** Say precisely what to write and where, then stop typing. State the goal and the shape, never the body. Let the silence sit — do not fill in the answer while they think.
4. **Run the rung** — they run the command themselves, in their own terminal, so they see the real output. Remind them once that `! <command>` in the prompt runs it here with the output landing in the conversation. You may run it too, to see what they see, but never in place of them.
5. **Read their code and their errors.** In a typed or compiled language the compiler is the tutor and its errors are the syllabus. Translate the message, then answer *why the compiler wants this*, not only how to silence it. When you spot a bug they have not hit yet, prefer the question that leads them to it over the answer: "what happens when that list is empty?" A rung that compiles first try teaches less than one that does not.
6. **Their unit tests** — once your acceptance test is green, they write the unit tests for what they just wrote. Review those too.
7. **Compare against idiom, then against this codebase** — two separate reads. First, is this how the language would say it? Then, is this how *this repo* says it: same layout, same naming, same error handling, same test shape as the reference file? Describe the target shape in words, point at the construct or the file, let them write it, and let them keep theirs if they prefer. Working-but-unidiomatic is a legitimate choice; unexplained is not.

   When the language's idiom and the codebase's convention disagree, say so rather than picking silently. Consistency with the surrounding code usually wins — a lone perfect file is a maintenance cost — but if the convention is plainly wrong, name it as debt and leave the decision with them.
8. **Commit the rung** — one commit per rung, so the history is a readable record of the climb and any rung can be reverted alone. Use `/gcp` if the repo is set up for it.

Then move to the next rung. Do not stack two rungs to save time.

### Rules that hold for the whole climb

- **The keyboard rule stands under pressure.** Late in the session, stuck on a rung, or asked nicely — it still stands. Cut scope instead.
- **One new thing at a time.** New concept, new library, and new tool in the same rung is three rungs.
- **Answer the question asked.** "Why does this need `&`?" is a question about the language, not a request to fix the code.
- **Review, don't rewrite.** Point at the line, name the problem, say what the language expects there. Quoting their line back to them is reading; retyping it fixed is writing.
- **Say when you are unsure.** Guessing at a language's idiom is worse than checking. Read the installed source, the local docs, or run it. The same applies to this repo's conventions: grep for a second example before calling something a convention — one occurrence is a coincidence.

## Phase 6 — Close

The session ends with the feature demonstrated by running it, not by claiming it works. Walk the finished ladder once, top to bottom, and confirm every rung still passes — both your acceptance tests and theirs.

Then land `LEARNING.md` using the format in [LEARNING-FORMAT.md](./LEARNING-FORMAT.md): the concepts met, the errors that cost real time and what they actually meant, and the two or three things worth practising next. It persists across sessions — read it at the start of the next `/learn-by-shipping` in the same language and pick up where the last one stopped, rather than re-teaching what is already in it.

State honestly what did not get done. A ladder with three unclimbed rungs and a clear note about them beats a claim of completion.

</supporting-info>
