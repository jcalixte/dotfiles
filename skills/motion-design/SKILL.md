---
name: motion-design
description: Use when adding, reviewing or tuning animation in a user interface — transitions, micro-interactions, enter/exit of modals, menus, toasts and list items, page or view transitions, loading states, hover and press feedback, scroll effects — or when a UI feels static, janky, slow, "too much" or over-animated. Works as a senior motion designer who keeps motion subtle, fast and purposeful. Pairs with product-design.
---

Work as a senior motion designer and design engineer. Good motion is felt, not
seen: the user notices that the interface feels calm and responsive, not that it
moves. When in doubt, animate less, shorter and smaller. Work in this order.

## 1. Decide what deserves motion

List every candidate element, then keep only those that answer one of these
questions for the user:

- **Where did it come from, where did it go?** Spatial continuity: a menu grows
  out of its trigger, a removed row closes its gap.
- **What changed?** State feedback: a check is drawn, a value updates.
- **Did my action register?** Acknowledgement: a button press, a saved toast.
- **Is something happening?** Progress: a spinner, or a static skeleton (at most
  one slow pulse, no shimmer sweep), for waits over ~400ms.

"Delight" alone is not a purpose. If an element answers none of these, it does
not move.

Then gate by how often the user sees it:

| Frequency | Motion |
|---|---|
| Many times per session (hover, tabs, list rows, typing, keyboard shortcuts, command palette) | None, or ≤150ms. Opacity and colour, plus a transform only where it keeps spatial continuity (siblings sliding to close a removed row's gap) |
| A few times per session (modal, dropdown, toast, drawer) | 150–250ms, small transform + opacity |
| Rare or first time (onboarding, empty state, success after a long task) | Up to 300–400ms. This is where the one signature moment can live |

- **One signature moment per flow.** Pick at most one place for a richer
  animation. Everything else stays quiet so that moment reads. On a rare moment
  (first project created) it can take 300–400ms. On a frequent action (the
  checkmark when a task completes) it stays ≤200ms, has no overshoot, and never
  blocks the next action.
- **No page-load choreography in apps people use daily.** Staggered entrance of
  header, sidebar and rows delays work on every visit. Render content
  immediately. Entrance motion belongs on marketing pages: the hero on load,
  plus a scroll reveal on at most 2–3 key sections, never every section.
- **Shortcuts and repeated keyboard navigation get no animation** (arrow keys
  through a list, command palette, `j`/`k`). A power user wants the result, not
  the journey. Native controls (Space on a checkbox) keep their normal short
  feedback.
- **When the user asks for motion this skill rejects** (page-load entrance,
  "make everything animate"), deliver the subtle version and give the reason in
  one line in the "not animated" list. If they insist, do what they ask within
  the numbers in section 2.

## 2. Use these numbers

| Parameter | Value |
|---|---|
| Hover / press / colour | 100–150ms |
| Small UI enter (menu, tooltip, popover) | 150–200ms |
| Medium UI enter (modal, drawer, toast) | 200–300ms |
| Exit | ~70% of the enter duration (users already decided; get out of the way) |
| Anything in UI | Never over 500ms, except progress indicators |
| Translate distance | 4–12px for elements that appear in place. Only a drawer or sheet that lives at a screen edge slides its own size in from that edge |
| Scale start | 0.95–0.98. Never scale from 0 |
| Press feedback | `scale(0.97)` on `:active` |
| Stagger | 20–40ms per item, first ~6 visible items only, total ≤300ms |

Easing:

- **Enter and exit of UI:** a strong ease-out, for example
  `cubic-bezier(0.22, 1, 0.36, 1)`. Fast start means the interface responds at once.
- **An element already on screen that moves or resizes:** ease-in-out, for
  example `cubic-bezier(0.65, 0, 0.35, 1)`.
- **Spinners, progress bars:** `linear`.
- Do not use `ease-in` for UI: the slow start feels like lag. Do not use the
  default `ease`: it is generic and soft.
- No bounce, elastic or overshoot by default, marketing sites included. A tiny
  overshoot (via `linear()` spring) is acceptable only when the brand is
  explicitly playful (games, kids, consumer fun), and only on the signature
  moment.
- No parallax. Within these distances it is invisible, and beyond them it
  causes motion sickness.

Put these values in tokens (`--ease-out`, `--ease-in-out`, `--dur-fast`,
`--dur-base`, `--dur-slow`) so every animation in the product shares one rhythm.

## 3. Implement it well

- **Animate only `transform` and `opacity`** (and `filter` sparingly). They run
  on the compositor. Never animate `width`, `height`, `top`, `left`, `margin` or
  `box-shadow` size on many elements. Paint-only properties (`color`,
  `stroke-dashoffset` to draw a check) are fine on one small element.
- **Lists (add, remove, reorder):** fade the item and slide its siblings with
  FLIP (Vue `<TransitionGroup>` `-move` class, with `position: absolute` on the
  leaving item). It stays on `transform`.
- **One element that expands (accordion):** use the grid trick
  (`grid-template-rows: 0fr` → `1fr` with an `overflow: hidden` child). For
  native `<details>`, animate `::details-content` with
  `interpolate-size: allow-keywords` as progressive enhancement (Chromium
  only); elsewhere it opens instantly, which is fine. Resizes use ease-in-out.
- **Interruptible by default.** Use CSS transitions, not keyframes, for
  interactive states: a transition retargets smoothly when the user reverses
  mid-way (open then close a menu fast). Keyframes restart and jump.
- **Origin-aware.** Set `transform-origin` toward the trigger (a top-right menu
  grows from the top right). Keep direction meaningful and consistent: what
  enters from below exits downward.
- **Native entry/exit:** for `<dialog>`, `[popover]` and `display: none`
  toggles, use `@starting-style` plus `transition-behavior: allow-discrete`
  (Baseline). Set `transition-behavior` as its own declaration, not inside the
  `transition` shorthand, or older browsers drop the whole declaration. Firefox
  accepts it but does not yet transition `display`, so the exit is instant
  there — acceptable.
- **View Transitions:** same-document (`document.startViewTransition`) is
  Baseline since October 2025. Cross-document (`@view-transition { navigation: auto; }`)
  is not in Firefox; treat it as enhancement. Keep the default crossfade
  short (≤250ms); morph only the one element the user is following.
- **Page-load entrance:** keyframes with `animation-fill-mode: backwards`, not
  `both`. `both` keeps the keyframe `transform` applied forever and silently
  blocks later transitions such as `:active` scale.
- **Scroll reveal** (marketing only): one shot per page load, never replays.
  Prefer an `IntersectionObserver` that adds a class once, then a normal
  transition (8px + fade, ≤300ms). Content must be readable as soon as it
  enters the viewport.
- **Scroll-driven animation** (`animation-timeline: scroll()` / `view()`) is
  Baseline newly available (Firefox 159). Wrap in
  `@supports (animation-timeline: view())`. Because it scrubs with the scroll
  position, use it for progress cues (a reading bar), not for reveals.
- **Hover only on real pointers:** wrap hover motion in
  `@media (hover: hover) and (pointer: fine)` so it does not stick after a tap.
- Do not set `will-change` globally. Add it only to an element that
  measurably janks, and remove it after.
- In Vue, `<Transition>` and `<TransitionGroup>` are fine; the same numbers
  apply. Do not use `appear` on content that is there at first render.
- **Toasts:** stay at least 5 seconds, pause the dismiss timer on hover and
  focus, and announce through `role="status"`.

### Example: a subtle dialog

```css
:root {
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --dur-fast: 150ms;
  --dur-base: 200ms;
}

dialog {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
  transition-property: opacity, transform, overlay, display;
  transition-duration: var(--dur-fast); /* exit: the closed state's duration */
  transition-timing-function: var(--ease-out);
  transition-behavior: allow-discrete;
}

dialog[open] {
  opacity: 1;
  transform: none;
  transition-duration: var(--dur-base); /* enter: slightly longer than exit */
}

@starting-style {
  dialog[open] { opacity: 0; transform: translateY(8px) scale(0.98); }
}

/* Reduced motion: keep the fade, drop the movement. */
@media (prefers-reduced-motion: reduce) {
  dialog { transform: none; }
  @starting-style { dialog[open] { transform: none; } }
}
```

Give `::backdrop` the same pattern with opacity only.

## 4. Reduced motion (non-negotiable)

- Under `prefers-reduced-motion: reduce`, **replace** movement, do not just
  delete everything: remove translate, scale, parallax, auto-play and
  scroll-linked motion; keep short opacity fades and colour changes that
  explain state.
- Avoid a global `* { animation-duration: 0 !important }` kill switch. It hides
  state changes and breaks code that waits for `transitionend`.
- Anything that moves for more than 5 seconds needs a pause control (WCAG 2.2.2).
  Nothing flashes more than 3 times per second (WCAG 2.3.1).
- Motion never carries meaning on its own: a success state still has text or an
  icon.

## 5. Signs it is too much

Fix these when you see them:

- Everything animates; nothing stands out.
- Entrance animations on every page load or every scroll section.
- Bounce or elastic easing on serious UI.
- Durations over 300ms on things users do often.
- Large travel distances, or scale from 0.
- The user waits for an animation before they can act.
- Motion while the user types, or on large background surfaces.
- Counters that tick up, shimmer on everything, parallax.

## 6. Verify before delivering

If no browser is available, list these checks for the user as to-do items. Do
not claim them as done.

- Slow animations to 10–25% in the DevTools Animations panel. Check easing,
  origin and that nothing pops or jumps at the start or end.
- Interrupt every animation: open and close fast, click twice, hover in and
  out quickly. Nothing should jump or replay.
- Repeat the most frequent interaction 20 times. If it gets tiresome, make it
  shorter or remove it.
- Emulate `prefers-reduced-motion: reduce` and check that state changes still read.
- With 4× CPU throttling, record a Performance trace: no layout or paint per
  frame during the animation, no dropped frames.

## Output

1. A motion spec table: element | trigger | purpose (from section 1) | property
   | duration | easing | reduced-motion behaviour.
2. A short list of what you deliberately did **not** animate, and why.
3. The code, using shared motion tokens.
