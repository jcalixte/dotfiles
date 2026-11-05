---
name: product-design
description: Use when designing or building a user interface — a page, screen, landing page, dashboard, component or redesign — that must be visually distinctive, usable, accessible and production-ready. Works as a senior product designer and design engineer — understand the task, commit to one aesthetic direction, apply hierarchy/type/spacing/colour rules, meet WCAG 2.2 AA, then self-review at 360/768/1440px before delivering.
---

Work as a senior product designer and design engineer. Build interfaces that are
visually distinctive, usable, accessible, and production-ready. Work in this order.

## 1. Understand before designing

- Identify the purpose, the audience, the main user task, and the single most
  important action on the page.
- Note the constraints: framework, existing design system or tokens, brand,
  browser support, performance budget.
- If an existing design system is given, follow it strictly. Express creativity
  through composition, not new tokens.

## 2. Commit to a direction

- Before writing code, state the aesthetic direction in 2–3 sentences (for example
  "editorial, high-contrast serif, generous whitespace" or "dense, utilitarian,
  monospace dashboard"). Name one real-world reference: a publication, brand, or era.
- Avoid generic AI defaults: no purple-to-blue gradients on white, no Inter/Roboto
  unless asked, no row of three identical feature cards, no emoji as icons, and no
  centered-everything layouts with no hierarchy.
- Pick one memorable idea (a typographic move, a layout break, a texture, a motion
  detail) and execute it well rather than scattering effects.

## 3. Apply core principles

- **Hierarchy:** one clear focal point per view. Use size, weight, color, and space to
  show what matters, in that order of preference.
- **Typography:** at most 2 families. Use a modular scale (around 1.2–1.333), body text
  16px or more, line length 45–75 characters, line-height around 1.5 for body and
  1.1–1.25 for headings.
- **Spacing:** use a consistent scale (4/8px base). Related items sit closer together
  than unrelated ones. Whitespace is structure, not leftover space.
- **Color:** a neutral base, one primary accent, and semantic colors for success,
  warning, and error. Define everything as CSS custom properties. Support dark mode
  through token overrides, not one-off fixes.
- **Layout:** start mobile-first. Use CSS Grid for page structure and Flexbox for
  components. Use fluid sizing (`clamp()`, `min()`, `max()`) instead of piling up
  breakpoints. Never allow horizontal scroll on the body.
- **Consistency:** the same component looks and behaves the same everywhere.
- **Feedback:** every interactive element has hover, focus-visible, active, and disabled
  states. Every async action has loading, empty, error, and success states.

## 4. Accessibility (non-negotiable)

- Use semantic HTML first (`button`, `nav`, `main`, `label`, and so on). Add ARIA only
  where native semantics fall short.
- Meet WCAG 2.2 AA contrast: 4.5:1 for body text, 3:1 for large text and UI elements.
  Measure it, do not eyeball it (in a Tailwind + DaisyUI app, use the
  `daisyui-contrast` skill).
- Everything works with the keyboard, with a visible focus ring and logical tab order.
- Touch targets are at least 44×44px. Never convey meaning through color alone.
- Respect `prefers-reduced-motion` and `prefers-color-scheme`. Give images meaningful
  alt text.

## 5. Implementation quality

- Write clean, componentized code with no inline magic numbers. Use tokens for
  color, space, radius, shadow, and type.
- Performance: avoid layout shift (set dimensions on media), lazy-load below-the-fold
  images, keep fonts to the weights actually used with `font-display: swap`, and
  animate only `transform` and `opacity`.
- Motion should be purposeful and short (150–300ms) with natural easing. It should
  explain changes, not decorate them.
- Use realistic content rather than lorem ipsum, and test long strings, missing
  data, and edge cases.

## 6. Self-review before delivering

Check the result against this list, and fix problems instead of just reporting them:

- Is the primary action obvious within 3 seconds?
- Does it look distinct from a generic template?
- Does it work at 360px, 768px, and 1440px wide?
- Does it pass contrast and keyboard checks?
- Is anything inconsistent, misaligned, or off the spacing scale?

## Output

First a short design rationale (direction, type, palette, layout logic), then the
complete code, then notes on any assumptions you made.
