---
name: daisyui-contrast
description: Use when picking or overriding colours in a Tailwind v4 + DaisyUI app — setting `--color-primary`, writing a gradient or brand-coloured surface, or reviewing UI that may be unreadable in dark mode. Measures WCAG contrast instead of eyeballing it, and states the `--color-*-content` pair DaisyUI does not derive for you.
---

<what-to-do>

## The failure this prevents

DaisyUI ships a light **and** a dark theme, and the dark one applies from `prefers-color-scheme`
whether or not anyone designed for it. Two traps follow, and both have shipped unreadable text:

1. **Overriding `--color-primary` does not recompute `--color-primary-content`.** DaisyUI keeps the
   near-white label that belonged to *its* dark-purple primary. Give it a light brand colour and
   every `btn-primary` reads at ~1.9:1. Always state the pair, in both theme blocks.
2. **A fixed-colour surface must carry fixed-colour text.** A hero with a hand-written gradient, a
   brand panel, a coloured banner — the background is the same under both themes, so text on it
   that inherits `base-content` flips to near-white in dark mode and lands on a pale background at
   ~1:1. Set `color` on the surface itself. DaisyUI resolves a button's label from `base-content`
   rather than inheriting, so a `btn-ghost` on that surface needs `--btn-rest-fg` too.

## Measure, never eyeball

Pick the label colour by measuring — a mid-tone primary can fail against black *and*
white, which is the signal to darken the primary itself:

```bash
python3 - <<'PY'
def lum(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    c=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c]
    return .2126*c[0]+.7152*c[1]+.0722*c[2]
def ratio(a,b):
    x,y=sorted((lum(a),lum(b))); return (y+.05)/(x+.05)
PRIMARY="{{PRIMARY_COLOR}}"
for ink in ("#0d1117","#ffffff"):
    print(ink, round(ratio(ink,PRIMARY),2), "PASS" if ratio(ink,PRIMARY)>=4.5 else "FAIL")
PY
```

Take the passing ink as `{{PRIMARY_CONTENT_COLOR}}`. Run the same check for every colour pair you
hand-write, against **both** ends of a gradient. Anything under 4.5:1 (3:1 for text at 24px+) is a
bug, not a taste call. A brand ink used as *text* on the page background needs to move with the
theme — `light-dark(<on-light>, <on-dark>)` in the `@theme` block, not one fixed hex.

## Verify in both schemes

Load the page in a browser (the **browser-testing-with-devtools** skill) and toggle DevTools'
"Emulate prefers-color-scheme: dark", then re-read the two traps above for anything that vanished.
Without a browser, grep the built CSS for the colour pairs you wrote and run them through the ratio
snippet; the numbers are the evidence, a passing build is not.

</what-to-do>

<supporting-info>

## Where the pair is declared

Primary color is wired into `src/style.css` via `@plugin "daisyui/theme" { name: "light"; default: true; --color-primary: <hex>; --color-primary-content: <ink>; }`. The override propagates to both Tailwind utilities (`bg-primary`, `text-primary`) and DaisyUI components (`btn-primary`, `badge-primary`, etc.). Setting it in `@theme` alone would only cover Tailwind utilities, not DaisyUI components. **`--color-primary-content` is not derived from `--color-primary`** — omit it and DaisyUI keeps the label colour of its own default primary, so a light brand colour ships a `btn-primary` nobody can read. The same two lines go in a `dark` theme block, since DaisyUI's dark theme applies from `prefers-color-scheme` unasked.

</supporting-info>
