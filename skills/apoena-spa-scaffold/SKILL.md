---
name: apoena-spa-scaffold
description: Use when scaffolding the frontend of an apoena app — a Vite + Vue 3 + TypeScript SPA with Tailwind v4, DaisyUI, oxc lint/format, a Tabler favicon recoloured to the brand hex, and a Dockerfile + nginx.conf ready for Coolify. Builds a real first screen, not a placeholder card. Called by apoena-new, or on its own to add this stack to an existing directory.
---

<what-to-do>

## Inputs

Needed before starting (the caller supplies them; ask the user for anything missing):

- **App name** (kebab-case) — used for `package.json` `"name"` and the `<title>`.
- **Project dir** — where the SPA lands. May already exist and hold design docs.
- **Primary color** (hex, e.g. `#570DF8`) — Tailwind v4 `--color-primary` and the favicon stroke.
- **Favicon icon name** from Tabler (`https://tabler.io/icons`), outline variant, exact slug (e.g. `bolt`, `paw`, `qrcode`). Pre-verify it resolves (HTTP 200) before scaffolding so you don't discover a 404 late.
- **What the app is** — its purpose and core features, enough to build the genuine first screen.
- **Backend?** — only affects whether `vite.config.ts` gets the `/api` dev proxy.

## Scaffold

```bash
cd <local-path-parent>
npm create vite@latest <app-name> -- --template vue-ts
cd <app-name>
pnpm install
pnpm add -D tailwindcss @tailwindcss/vite
pnpm add daisyui@latest
pnpm add -D oxlint oxfmt    # oxc linter + formatter (https://oxc.rs)
```

**If the target directory already exists and is non-empty** (e.g. it already holds design docs, or the chosen path equals the current folder), `npm create vite` becomes interactive and would clobber files. Instead scaffold into a scratch dir and copy in, preserving everything that already exists:

```bash
npm create vite@latest /tmp/<app-name>-scaffold -- --template vue-ts
rm -f /tmp/<app-name>-scaffold/README.md      # never clobber an existing README
cp -R /tmp/<app-name>-scaffold/. <project-dir>/   # trailing /. includes dotfiles; only README would collide
cd <project-dir> && pnpm install && pnpm add -D tailwindcss @tailwindcss/vite && pnpm add daisyui@latest && pnpm add -D oxlint oxfmt
```
Set `"name"` in `package.json` to `<app-name>` (the scaffold names it after the temp dir). If an informative `README.md` already exists, keep it and tell the caller so it skips its README step.

Then write/patch these files (templates in `templates/`):

- `vite.config.ts` — add `@tailwindcss/vite` plugin, and (if backend) the `/api` dev proxy to `http://localhost:8000`.
- `src/style.css` — copy `templates/tailwind-style.css`, substitute `{{PRIMARY_COLOR}}` with the user's hex, and substitute `{{PRIMARY_CONTENT_COLOR}}` with the label colour you compute for it (use the **daisyui-contrast** skill — do not skip this, and do not eyeball it). **Keep the font `@import url(...)` as the first line** (the template already orders it correctly — do not move it below `@import "tailwindcss"` or the font silently won't load in the build).
- `src/App.vue` + supporting files — build the **real first screen of the app**, not a generic landing card. This is the genuine entry point the user would land on, themed with DaisyUI: for a data-driven app that means the primary screen actually wired up (fetching and rendering real data), not a mockup. Keep it to that one screen — secondary screens and the full feature set come later — but it must be recognizably *this* app. Add only the components / composables / types that this one screen needs. Delete `src/components/HelloWorld.vue` (and the now-empty `src/components/` if nothing replaces it).
- `src/assets/icons/` — create the folder and copy `templates/icons-readme.md` to `src/assets/icons/README.md`. This is the reusable in-app icon folder; the user drops Tabler SVGs here as needed.
- `public/favicon.svg` — fetch `https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/outline/<favicon-icon>.svg`, then `sed` replace `currentColor` with the primary-color hex, and **overwrite** `public/favicon.svg` (the modern `vue-ts` template already ships one). If the curl 404s, ask the user for a different icon name and retry.
- **Remove the modern template's demo cruft** — recent `vue-ts` ships `src/assets/{vite.svg,vue.svg,hero.png}` and `public/icons.svg` (there is no longer a `public/vite.svg`). `rm -f` them since the new `App.vue` doesn't reference them.
- `index.html` — the modern template **already** has `<link rel="icon" type="image/svg+xml" href="/favicon.svg" />`, so usually only the `<title>` needs updating to the app name (fix the icon link only if it differs).
- `Dockerfile` — copy `templates/Dockerfile.spa`.
- `nginx.conf` — copy `templates/nginx.conf`.
- `.dockerignore` — at minimum `node_modules`, `dist`, `.git`.
- **oxc linter + formatter** ([oxc.rs](https://oxc.rs)) — run `pnpm exec oxlint --init` to generate `.oxlintrc.json` (a valid starter for the installed version; don't hand-write it). For oxfmt, write `.oxfmtrc.json` with `semi: false` (no trailing semicolons) and `singleQuote: false` (double quotes — also oxfmt's default, set explicitly):
  ```json
  {
    "$schema": "./node_modules/oxfmt/configuration_schema.json",
    "semi": false,
    "singleQuote": false
  }
  ```
  Add four scripts to `package.json`: `"lint": "oxlint"`, `"lint:fix": "oxlint --fix"`, `"fmt": "oxfmt"`, `"fmt:check": "oxfmt --check"`. **Coverage caveat:** oxlint lints the `<script>` blocks of `.vue` files but not `<template>`, and oxfmt's `.vue` support is partial — so the Vue markup layer isn't checked. oxfmt does **not** touch `src/style.css` (it formats JS/TS/Vue, not CSS), so the font `@import` ordering there is unaffected.
- **Zed format-on-save** — copy `templates/zed-settings.json` to `.zed/settings.json`. Without it, Zed formats `.ts`/`.vue` on save with its built-in (Prettier-style) formatter, which **adds semicolons** and fights the `semi: false` in `.oxfmtrc.json`. The config points Zed's on-save formatter at the project-local `./node_modules/.bin/oxfmt` (via `--stdin-filepath`, so it honours `.oxfmtrc.json`), for TypeScript/JavaScript/Vue only — CSS/JSON/Markdown keep Zed's defaults. Use the direct binary path, not `pnpm exec oxfmt`: both need cwd at the project root, but the wrapper adds ~300ms on every save. `.zed/` is committed (not git-ignored) so any Zed user on the repo gets consistent saves.

## Contrast

Run the **daisyui-contrast** skill to pick `{{PRIMARY_CONTENT_COLOR}}` and to check every colour pair you hand-write. Overriding `--color-primary` without stating `--color-primary-content` ships a `btn-primary` nobody can read, and DaisyUI's dark theme applies from `prefers-color-scheme` whether or not anyone designed for it. Measure, don't eyeball.

## Verify

Verify it builds, lints, and is formatted:

1. `pnpm dev` boots — start it, curl `http://localhost:5173` (use `curl --retry … --retry-connrefused` instead of a foreground `sleep` to wait for boot), then kill it.
2. **`pnpm build` succeeds with no warnings** — this is exactly what Coolify runs (`vue-tsc -b && vite build`) and catches type errors the dev server won't. A `@import must precede all rules` warning means the font import in `src/style.css` is misordered.
3. Run `pnpm fmt` to format the generated code, then `pnpm lint` — both should pass clean on a fresh scaffold (fix anything oxlint flags before committing).
4. Since the scaffold is a real screen, not a static card, sanity-check that it actually renders — load it in a browser (the **browser-testing-with-devtools** skill) and confirm the first screen shows real content, not an error or empty state.
5. **Look at it in both colour schemes** — DevTools' "Emulate prefers-color-scheme: dark" — and re-check with **daisyui-contrast** for anything that vanished.

</what-to-do>

<supporting-info>

## Stack rationale

- **Vite + Vue 3 + TypeScript** — matches `skills/web-dev/SKILL.md` ("Always use the most modern HTML, CSS, and JS"). `--template vue-ts` is the official Vite scaffold. Note: the modern `vue-ts` template ships demo assets (`src/assets/{vite.svg,vue.svg,hero.png}`, `public/icons.svg`, and its own `public/favicon.svg`) — clear the unused ones during scaffold.
- **Tailwind v4 via `@tailwindcss/vite`** — v4 dropped the `postcss` + `tailwind.config.js` ceremony; everything is configured in CSS via `@import "tailwindcss"` and `@plugin "daisyui"`.
- **DaisyUI** — Tailwind component library, registered as a Tailwind v4 plugin in the stylesheet (no JS import).
- **Fonts via `api.fonts.coollabs.io`** — privacy-friendly Google Fonts mirror (run by the Coolify team). The CSS `@import`s the font from `https://api.fonts.coollabs.io/css2?...` and sets it as `--font-sans` in the Tailwind v4 `@theme` block. **Note the `api.` subdomain** — the bare `fonts.coollabs.io` host serves the marketing homepage (HTML), not CSS, so the `@font-face` rules never load and the font silently falls back to system fonts. **The font `@import url(...)` MUST be the first line, before `@import "tailwindcss"`** — Tailwind inlines its own import into real rules, and per the CSS spec `@import` must precede all other rules, so a font import placed second is dropped by the build (with a warning) and never loads. To swap fonts, edit `src/style.css` — change the `@import url(...)` family and the `--font-sans` value (and `--font-mono` if you want a mono font like Fira Code applied app-wide).
- **oxc for lint + format** ([oxc.rs](https://oxc.rs)) — `oxlint` (Rust, ESLint-compatible, stable) and `oxfmt` (Prettier-compatible, Beta) replace the ESLint + Prettier stack with one fast toolchain and near-zero config. Chosen over ESLint/Prettier for speed and simplicity. **Limitation to be aware of:** as of mid-2026 oxlint lints only the `<script>` of `.vue` files (no `<template>` linting) and oxfmt's `.vue` support is partial — so the Vue markup layer is unchecked. Acceptable here because the type-checked `pnpm build` (`vue-tsc`) already catches template type errors, and most logic lives in `<script setup lang="ts">`. `.oxlintrc.json` is generated by `oxlint --init`; `.oxfmtrc.json` pins `semi: false` + `singleQuote: false` (no semicolons, double quotes).
- **Nginx-alpine for SPA serving** — tiny image, SPA fallback via `try_files`. Coolify expects port 80 by default for SPAs.

## Tabler icons + favicon

- The favicon is fetched from `https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/outline/<name>.svg` at scaffold time, recoloured to the user's primary hex (Tabler outline icons use `stroke="currentColor"` → `sed` replace), and written to `public/favicon.svg` (overwriting the template's default).
- In-app icons live in `src/assets/icons/` — the user drops more Tabler SVGs there as needed. Pattern in Vue: `<img src="@/assets/icons/foo.svg" alt="" class="size-5" />` for static colour, or paste the SVG inline as a Vue component if it needs to follow `currentColor`.

## When the user wants a different stack

This skill is opinionated for Vite/Vue/DaisyUI. If the user says "actually I want Svelte": stop, name what's different, and ask whether to (a) adapt manually after the Gitea + Coolify parts run, or (b) skip this skill entirely and scaffold by hand.

## Files in this skill

- `templates/Dockerfile.spa` — Vite build → nginx serve, port 80.
- `templates/nginx.conf` — SPA fallback.
- `templates/tailwind-style.css` — Tailwind v4 + DaisyUI import (font import ordered first), with `{{PRIMARY_COLOR}}` placeholder.
- `templates/icons-readme.md` — README dropped into `src/assets/icons/` to document the icon folder.
- `templates/zed-settings.json` — copied verbatim to `.zed/settings.json`; points Zed's format-on-save at project-local oxfmt for TS/JS/Vue so editor saves match `.oxfmtrc.json` (no semicolons).

</supporting-info>
