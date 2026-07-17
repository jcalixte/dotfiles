# Condition-Based Waiting

## Overview

`sleep(2000)` is a guess about how long something takes. Guesses are wrong in both
directions: too short and the test flakes, too long and every run wastes the
slack. Arbitrary timeouts are the single most common source of flaky tests and
sluggish suites.

**Core principle:** wait for the CONDITION you actually care about, not for a
duration you hope is long enough.

**If you're typing a number of milliseconds to `sleep`, stop and name the
condition instead.**

## The Anti-Pattern

```js
await doAsyncThing()
await sleep(2000)          // "should be done by now" — hope, not logic
expect(result).toBe(...)   // flakes when the machine is slow / loaded
```

Two failure modes, both bad:
- **Too short** → intermittent failures under load, in CI, on slow machines. The
  test that passes locally and fails in CI is almost always this.
- **Too long** → every run pays the full timeout even when the work finished in
  50ms. Multiply across a suite and minutes evaporate.

## The Pattern

Poll for the condition, with a generous *ceiling* timeout that only trips on real
failure:

```js
async function waitFor(condition, { timeout = 5000, interval = 50 } = {}) {
  const deadline = Date.now() + timeout
  while (Date.now() < deadline) {
    if (await condition()) return
    await sleep(interval)
  }
  throw new Error('waitFor: condition not met within ' + timeout + 'ms')
}

await doAsyncThing()
await waitFor(() => result.isReady)   // returns the instant it's true
expect(result).toBe(...)
```

The timeout here is a *failure ceiling*, not an *expected duration* — set it well
above the worst realistic case (the test finishes as soon as the condition holds,
so a high ceiling costs nothing on the happy path).

## Prefer Built-In Waiters

Most frameworks already provide condition-based waiting — reach for it before
hand-rolling:

- **Playwright / Cypress:** auto-waiting locators, `expect(locator).toBeVisible()`,
  `page.waitForResponse()`, `waitForSelector()`
- **Testing Library:** `await waitFor(() => ...)`, `findBy*` queries
- **Jest/Vitest:** `await expect(...).resolves`, fake timers for time-dependent
  logic (`vi.useFakeTimers()` / `vi.advanceTimersByTime()`)
- **Backend/integration:** poll a health endpoint, tail for a readiness log line,
  await an event/promise, or block on the actual signal (a queue message, a file
  appearing)

## Pick the Right Signal

Wait on the thing that is *causally* what you need, not a proxy for it:

| Waiting for | Wait on |
|---|---|
| Server ready | health endpoint returns 200 (not `sleep` after spawn) |
| Element interactive | element visible + enabled (not `sleep` after navigation) |
| Async job done | job status flips / completion event (not "jobs usually take 3s") |
| File written | file exists AND is non-empty / has trailing marker |
| DB write visible | read-back returns the row (not `sleep` after insert) |

## When A Fixed Delay Is Actually Correct

Rare, but real — be honest about which case you're in:

- **Debounce/throttle windows:** the behavior under test IS "wait 300ms of
  silence." Use fake timers to advance virtual time; don't wall-clock sleep.
- **Rate-limit backoff:** waiting is the intended behavior. Even then, prefer the
  API's own retry/`Retry-After` signal over a hard-coded pause.
- **Polling an external system you don't control** with no event/webhook. Poll on
  an interval with a ceiling — that's still condition-based, not a blind sleep.

If you can't name a condition after genuinely trying, document *why* the fixed
delay is correct in a comment. An unexplained `sleep` is a bug waiting to happen.

## Red Flags

- Any literal millisecond value passed to `sleep`/`setTimeout` in a test
- "Increase the timeout" as the fix for a flaky test (treats the symptom — the
  test flakes because it waits on time, not on the condition)
- `sleep` immediately after a spawn/navigate/insert "to let it settle"
- A comment like `// wait for it to finish` above a bare delay
