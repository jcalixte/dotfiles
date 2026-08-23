# LEARNING.md format

One file per language, at the repo root. It is the memory between sessions: read it at the start of the next `/learn-by-shipping` in this language and skip what it already covers.

Append to it; never rewrite history. Each session gets its own block.

```markdown
# Learning <language>

Level at the start of the first session: <verbatim from phase 1>
Transfer languages: <list>

## Session <YYYY-MM-DD> — <feature built>

### Concepts landed

One line each, in the user's own words where possible. Only concepts they
wrote code with — reading about it does not count.

- **<concept>** — <what it does, anchored to a transfer language>

### Errors that cost real time

The compiler and runtime messages that actually blocked progress, what
they meant, and the fix. This is the most valuable section in the file:
the same message will appear again, and next time it should cost seconds.

| Message (trimmed) | What it actually meant | Fix |
|---|---|---|

### Idioms chosen against

Where the working code is not what the language would say, and why the
user kept it. Not a debt list — a record of a decision, so nobody
re-litigates it blind.

### Still fuzzy

Concepts met but not yet understood. Named honestly — this is the
starting point of the next session, so vagueness here costs later.

### Practise next

Two or three, no more. Each small enough to be a single sitting.
```

## Rules

- **Only what was written, not what was mentioned.** A concept explained but never typed goes under *Still fuzzy*, not *Concepts landed*.
- **The user's words beat yours.** If they explained a concept back correctly, use their phrasing — it is the one that will jog their memory.
- **Trim the error messages** to the line that matters, but keep it verbatim enough to be searchable.
- **No praise, no progress narrative.** This is a reference, not a report card.
- **Absolute dates.** "Last session" means nothing in three months.
