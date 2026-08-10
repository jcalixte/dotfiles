# Load-bearing comments

Comments a compiler, bundler, linter, type checker, test runner, or doc generator actually reads. Deleting one changes behavior or breaks the build. **Never remove these during a comment prune** — they are not comments, they are syntax that happens to start with `//` or `#`.

Match on the marker, not on whether the text "looks useful".

## Any language

- Shebang: `#!/usr/bin/env node`
- License / SPDX headers: `// SPDX-License-Identifier: MIT`, copyright blocks
- Formatter and coverage pragmas: `// prettier-ignore`, `// istanbul ignore next`, `// c8 ignore`, `# fmt: off` / `# fmt: on`, `// biome-ignore`, `# ruff: noqa`
- Region markers a tool consumes (`// #region` when the docs tool or snippet extractor uses them)

## JavaScript / TypeScript

- `// @ts-ignore`, `// @ts-expect-error`, `// @ts-nocheck`, `/// <reference types="..." />`
- `/** @type {...} */`, `/** @satisfies */`, and every JSDoc annotation in a `checkJs`/JSDoc-typed project — these ARE the types
- JSX/pragma comments: `/** @jsx h */`, `/** @jsxImportSource react */`
- Bundler magic comments: `/* webpackChunkName: "x" */`, `/* webpackPreload: true */`, `/* @vite-ignore */`
- Minifier hints: `/*#__PURE__*/`, `/** @preserve */`, `/*! ... */` (banner-preserved)
- Lint control: `// eslint-disable`, `// eslint-disable-next-line rule`, `/* global foo */`, `/* eslint-env node */`
- `"use client"` / `"use server"` are directives, not comments — obviously untouchable
- Vue SFC: `<!-- eslint-disable -->`, and HTML conditional comments in templates

## Python

- Encoding line: `# -*- coding: utf-8 -*-`
- `# type: ignore`, `# type: (int) -> str` (legacy type comments — removing them removes the types)
- `# noqa`, `# noqa: E501`, `# pylint: disable=...`, `# mypy: disable-error-code=...`, `# pragma: no cover`
- Docstrings: runtime-visible via `__doc__`, consumed by Sphinx, and may contain **doctests** (`>>>` lines are executed tests)

## Go

- Build constraints: `//go:build linux`, `// +build linux` (must stay above the package clause with its blank line)
- Toolchain directives: `//go:generate`, `//go:embed`, `//go:noinline`, `//go:linkname`
- Doc comments preceding exported identifiers — `go vet`/lint enforce them, `go doc` publishes them
- `// Deprecated:` markers (tooling reads these)

## Rust

- `///` and `//!` doc comments — rustdoc output, and fenced code blocks in them are **compiled and run as doctests**
- Anything after `#[...]` is an attribute, not a comment

## C / C++ / Objective-C

- `#pragma once`, `#pragma pack`, `#pragma omp`, `// NOLINT`, `// NOLINTNEXTLINE` (clang-tidy)
- Doxygen `/** */` blocks that generate the published API docs

## Java / Kotlin

- Javadoc on public API (published, and `-Werror` doclint fails without it)
- `// $NON-NLS-1$` and similar i18n tooling markers

## Config, markup, infra

- YAML/JSON5 comments that a schema or templating layer reads (`# yamllint disable`, `# noqa` in Ansible)
- Dockerfile `# syntax=docker/dockerfile:1` — must be the first line
- Nginx/Apache configs where commented blocks are toggled by deploy scripts (ask before touching)
- SQL hints in comments: `/*+ INDEX(...) */` (Oracle), `-- noqa: L016` (sqlfluff)
- Terraform/HCL `# tflint-ignore:`
- CI YAML anchors and `# renovate:` / `# dependabot` datasource comments — dependency bots parse these

## Rule of thumb

If the text after the comment marker contains `@`, `:`, `!`, `#`, `+`, or a tool name — stop and check what reads it before deleting.
