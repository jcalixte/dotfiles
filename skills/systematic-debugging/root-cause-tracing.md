# Root Cause Tracing

## Overview

Bugs surface where they crash, not where they originate. A `null` blows up three
layers deep, but the `null` was created five layers up. Fixing the crash site
(add a guard, default the value) hides the symptom and leaves the source intact —
the bad value will reappear somewhere else.

**Core principle:** trace the bad value BACKWARD to where it was first created,
and fix it there.

**Fix at the source, not at the symptom.**

## When to Use

- Error is deep in a call stack and the immediate cause is "a value is wrong"
- A `null`/`undefined`/`NaN`/empty/negative value shows up where it shouldn't
- You're tempted to add a defensive guard at the crash site
- The same class of bug keeps reappearing in different places

## The Technique

Trace one question repeatedly until you reach the origin:

```
"This value is wrong HERE. Where did it come from?"
```

1. **Anchor on the exact bad value.** Not "something's off" — name it:
   "`user.plan` is `undefined` at `billing.ts:88`."

2. **Find who supplied it.** Read the frame above. What passed this argument,
   returned this value, or set this field? Go up one level, not ten.

3. **Ask: is the value already wrong here, or does it become wrong later?**
   - Already wrong on arrival → keep tracing up.
   - Correct here, wrong below → the corruption is between here and the symptom;
     narrow into that span.

4. **Repeat until the value is BORN.** You've found the source when you reach the
   line that first constructs it — a parse, a DB read, a default, a computation,
   an external input. That line is where the fix belongs.

5. **Fix at the source.** Correct the construction, the parse, the query, the
   default. Then decide, deliberately, whether guards downstream are still
   warranted (see `defense-in-depth.md`).

## Instrument, Don't Guess

If reading the code doesn't reveal where the value goes bad, make it observable.
Log the value at each boundary between the source and the symptom:

```
[parse]   plan = "pro"        <- correct
[service] plan = "pro"        <- correct
[cache]   plan = undefined    <- WRONG: corrupted here
[billing] plan = undefined    -> crash
```

The first frame that shows the wrong value is your source. Binary-search the
boundaries if the chain is long: check the midpoint first, then the half that
contains the transition.

## Worked Example

```
TypeError: cannot read 'length' of undefined   at render.ts:42
```

- `render.ts:42` — `items.length`; `items` is `undefined`. Who passed `items`?
- `Page` renders `<List items={data.rows} />`. Is `data.rows` undefined? Yes.
- `data` came from `useQuery('/report')`. The query returned `{ total: 0 }` — no
  `rows` key at all. Who built that response?
- `/report` handler: `return { total: count }` when `count === 0` — it early-returns
  **before** attaching `rows`.

**Symptom fix (wrong):** `items?.length ?? 0` at `render.ts:42`. Empty report now
renders, but every other consumer of `/report` still gets a response missing `rows`.

**Root fix (right):** the handler always returns `{ total, rows }`, with `rows: []`
when empty. One fix, every consumer correct.

## Red Flags

- Adding `?.`, `|| []`, `?? default`, or a try/catch at the crash site before you
  know where the bad value was born
- "I'll just guard against undefined here" — guarding *is* fine, but only after
  you've found and fixed the source
- Fixing the same shape of bug in a third location — the real source was never
  addressed

## Relationship to Other Techniques

- Found the source → decide if downstream validation is warranted:
  `defense-in-depth.md`
- Can't reproduce the bad value reliably → return to Phase 1 of `SKILL.md`
  (reproduce consistently, gather evidence)
