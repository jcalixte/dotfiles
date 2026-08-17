#!/usr/bin/env python3
"""Report and remove comments from code files. Dry-run by default."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", "target", "vendor",
    ".venv", "venv", "__pycache__", ".next", ".nuxt", ".svelte-kit",
    "coverage", ".turbo", "bower_components", "build-dev", ".nuke-comments-backup",
}
SKIP_FILE = re.compile(r"(\.min\.(js|css)|\.generated\.|_pb2?\.py|\.lock)$", re.I)

PROTECTED = re.compile(
    r"""(
    eslint-(disable|enable)|prettier-ignore|biome-ignore|oxlint-disable|deno-lint-ignore
    |@ts-(ignore|expect-error|nocheck|check)|type:\s*ignore|noqa|pylint:|mypy:|ruff:|flake8:
    |istanbul\s+ignore|[cv]8\s+ignore|coverage:\s*ignore|NOLINT|clang-format\s+(on|off)
    |go:(build|generate|embed|linkname|noinline)|\+build\s|\#\s*pragma|shellcheck\s+disable
    |hadolint\s+ignore|swiftlint:|SPDX-License-Identifier|@license|@preserve
    |webpack[A-Za-z]+|@vite-ignore|vite-ignore|@jsx|-\*-\s*coding|frozen_string_literal
    |(?-i:Code\s+generated\s+by|DO\s+NOT\s+EDIT|Copyright)|@vue-(ignore|expect-error|generic)
    |<reference\s|grcov-excl|tarpaulin::skip
    )""",
    re.X | re.I,
)
JSDOC_TYPE = re.compile(r"@(type|typedef|param\s*\{|returns?\s*\{|template|satisfies|callback|this)\b")
WORK_MARKER = re.compile(r"\b(TODO|FIXME|HACK|XXX|BUG|WIP)\b")
BANNER = re.compile(r"^[\s/*#<!->=~_+*.]+$")
CODEISH = re.compile(
    r"^\s*(if|for|while|switch|return|const|let|var|def|class|function|func|import|export"
    r"|from|print|console\.|await|async|public|private|try|catch|else|elif|end|fn|pub|use)\b"
    r"|[;{}]\s*$|^\s*[\w.\[\]\"']+\s*[:=]\s*\S"
)


@dataclass
class Lang:
    name: str
    line: tuple = ()
    block: tuple = ()
    strings: tuple = (('"', '"', "\\", False), ("'", "'", "\\", False))
    template: str = ""
    regex: bool = False
    hash_guard: bool = False
    mixed: bool = False
    nested_block: bool = False
    rust_tokens: bool = False
    doc_line: tuple = ()
    template_escape: bool = True


C_STR = (('"', '"', "\\", False), ("'", "'", "\\", False))
PY_STR = (
    ('"""', '"""', "\\", True), ("'''", "'''", "\\", True),
    ('"', '"', "\\", False), ("'", "'", "\\", False),
)

JS = Lang("js", line=("//",), block=(("/*", "*/"),), strings=C_STR, template="`", regex=True)
CLIKE = Lang("c-like", line=("//",), block=(("/*", "*/"),), strings=C_STR, template="`")
GO = Lang("go", line=("//",), block=(("/*", "*/"),), strings=C_STR, template="`",
          template_escape=False)
GLEAM = Lang("gleam", line=("//",), strings=(('"', '"', "\\", True),), doc_line=("////", "///"))
RUST = Lang(
    "rust", line=("//",), block=(("/*", "*/"),), strings=(('"', '"', "\\", True),),
    nested_block=True, rust_tokens=True, doc_line=("//!", "///"),
)
CSS = Lang("css", line=("//",), block=(("/*", "*/"),), strings=C_STR)
CSS_PLAIN = Lang("css", block=(("/*", "*/"),), strings=C_STR)
HTML = Lang("html", block=(("<!--", "-->"),), strings=())
PY = Lang("python", line=("#",), strings=PY_STR, hash_guard=True)
HASH = Lang("hash", line=("#",), strings=C_STR, hash_guard=True)
SQL = Lang("sql", line=("--",), block=(("/*", "*/"),), strings=C_STR, hash_guard=True)
LUA = Lang("lua", line=("--",), block=(("--[[", "]]"),), strings=C_STR, hash_guard=True)
HASKELL = Lang("haskell", line=("--",), block=(("{-", "-}"),), strings=C_STR, hash_guard=True)
MIXED = Lang("vue/svelte", mixed=True)

BY_EXT = {}
for exts, lang in (
    ("js jsx mjs cjs ts tsx mts cts", JS),
    ("java kt kts swift c h cc cpp cxx hpp cs scala dart php zig m mm groovy proto", CLIKE),
    ("go", GO),
    ("rs", RUST),
    ("gleam", GLEAM),
    ("scss less sass", CSS),
    ("css", CSS_PLAIN),
    ("html htm xml svg vtl", HTML),
    ("vue svelte astro", MIXED),
    ("py pyi", PY),
    ("sh bash zsh fish rb ex exs yaml yml toml tf nix pl r jl dockerfile makefile mk env", HASH),
    ("sql", SQL),
    ("lua", LUA),
    ("hs", HASKELL),
):
    for ext in exts.split():
        BY_EXT[ext] = lang

BY_NAME = {
    "Dockerfile": HASH, "Makefile": HASH, ".gitignore": HASH, ".dockerignore": HASH,
    ".env": HASH, ".env.example": HASH,
}

RUST_RAW = re.compile(r'(?:b|c)?r(?P<hashes>#*)"')
RUST_CHAR = re.compile(r"'(?:\\.|[^'\\\n])'")
DOCTEST = re.compile(r"```|~~~")
SAFETY = re.compile(r"\b(SAFETY|Safety|INVARIANT|PANICS|Panics)\b\s*:?")

REGEX_PREV = set("(,=:[!&|?{};+-*%~^<>\n\t ")
REGEX_WORDS = {"return", "typeof", "case", "in", "of", "new", "delete", "void", "do",
               "else", "yield", "await", "instanceof"}


def lang_for(path):
    base = os.path.basename(path)
    if base in BY_NAME:
        return BY_NAME[base]
    ext = base.rsplit(".", 1)[-1].lower() if "." in base else ""
    return BY_EXT.get(ext)


def _hash_ok(text, i):
    """Comment only at line start or after whitespace: keeps `$#`, `${#var}`, `a--b` intact."""
    return i == 0 or text[i - 1] in " \t\n"


def scan_code(text, i, lang, region_end, stop_brace=False):
    spans, depth, prev, word = [], 0, "\n", ""
    while i < region_end:
        c = text[i]
        if stop_brace:
            if c == "{":
                depth += 1
            elif c == "}":
                if depth == 0:
                    return spans, i + 1
                depth -= 1

        if lang.regex and c == "/" and text[i + 1:i + 2] not in ("/", "*") and (
            prev in REGEX_PREV or word in REGEX_WORDS
        ):
            j, in_class, closed = i + 1, False, False
            while j < region_end:
                ch = text[j]
                if ch == "\\":
                    j += 2
                    continue
                if ch == "\n":
                    break
                if ch == "[":
                    in_class = True
                elif ch == "]":
                    in_class = False
                elif ch == "/" and not in_class:
                    j, closed = j + 1, True
                    break
                j += 1
            if closed:
                i, prev, word = j, "/", ""
                continue

        if lang.rust_tokens:
            m = RUST_RAW.match(text, i)
            if m and not (i and (text[i - 1].isalnum() or text[i - 1] == "_")):
                close = '"' + "#" * len(m.group("hashes"))
                j = text.find(close, m.end())
                i = region_end if j == -1 else min(j + len(close), region_end)
                prev, word = '"', ""
                continue
            if c == "'":
                m = RUST_CHAR.match(text, i)
                i = min(m.end(), region_end) if m else i + 1
                prev, word = "'" if m else "a", ""
                continue

        hit = False
        for tok in lang.line:
            if text.startswith(tok, i) and not (lang.hash_guard and not _hash_ok(text, i)):
                j = text.find("\n", i)
                j = region_end if j == -1 else min(j, region_end)
                spans.append((i, j))
                i, hit = j, True
                break
        if hit:
            prev, word = "\n", ""
            continue

        for op, cl in lang.block:
            if text.startswith(op, i):
                j, level = i + len(op), 1
                while j < region_end and level:
                    if lang.nested_block and text.startswith(op, j):
                        level, j = level + 1, j + len(op)
                    elif text.startswith(cl, j):
                        level, j = level - 1, j + len(cl)
                    else:
                        j += 1
                spans.append((i, min(j, region_end)))
                i, hit = min(j, region_end), True
                break
        if hit:
            prev, word = " ", ""
            continue

        if lang.template and c == lang.template:
            i += 1
            while i < region_end:
                if lang.template_escape and text[i] == "\\":
                    i += 2
                    continue
                if text[i] == lang.template:
                    i += 1
                    break
                if text.startswith("${", i):
                    inner, i = scan_code(text, i + 2, lang, region_end, stop_brace=True)
                    spans.extend(inner)
                    continue
                i += 1
            prev, word = lang.template, ""
            continue

        for op, cl, esc, multi in lang.strings:
            if text.startswith(op, i):
                j = i + len(op)
                while j < region_end:
                    if esc and text[j] == esc:
                        j += 2
                        continue
                    if not multi and text[j] == "\n":
                        break
                    if text.startswith(cl, j):
                        j += len(cl)
                        break
                    j += 1
                i, hit = min(j, region_end), True
                break
        if hit:
            prev, word = '"', ""
            continue

        if c.isalnum() or c == "_":
            word += c
        else:
            word = ""
        if not c.isspace():
            prev = c
        elif c == "\n":
            prev = "\n"
        i += 1
    return (spans, i) if stop_brace else (spans, i)


TAG = re.compile(r"<(script|style|template)\b[^>]*>", re.I)


def scan_mixed(text):
    spans, pos = [], 0
    for m in TAG.finditer(text):
        if m.start() < pos:
            continue
        spans += scan_code(text, pos, HTML, m.start())[0]
        tag = m.group(1).lower()
        close = re.search(rf"</{tag}\s*>", text[m.end():], re.I)
        rend = m.end() + close.start() if close else len(text)
        sub = {"script": JS, "style": CSS, "template": HTML}[tag]
        spans += scan_code(text, m.end(), sub, rend)[0]
        pos = rend
    spans += scan_code(text, pos, HTML, len(text))[0]
    return sorted(spans)


def merge_doc_runs(text, spans, lang):
    """Consecutive `///` / `//!` lines are one doc comment — and one doctest."""
    starts = line_starts_of(text)
    out = []
    for span in spans:
        s, e = span
        idx = line_index(starts, s)
        own_line = not text[starts[idx]:s].strip()
        tok = next((t for t in lang.doc_line if text.startswith(t, s)), None)
        if out and tok and own_line:
            ps, pe = out[-1]
            prev_idx = line_index(starts, ps)
            prev_tok = next((t for t in lang.doc_line if text.startswith(t, ps)), None)
            if prev_tok == tok and line_index(starts, pe - 1) == idx - 1:
                out[-1] = (ps, e)
                continue
        out.append(span)
    return out


def find_comments(text, lang):
    if lang.mixed:
        return scan_mixed(text)
    spans = sorted(scan_code(text, 0, lang, len(text))[0])
    if lang.doc_line:
        spans = merge_doc_runs(text, spans, lang)
    return spans


@dataclass
class Comment:
    id: int
    path: str
    line: int
    end_line: int
    start: int
    end: int
    text: str
    kind: str
    protected: bool
    reason: str = ""


def classify(path, text, span, line_starts):
    s, e = span
    raw = text[s:e]
    line = line_index(line_starts, s) + 1
    end_line = line_index(line_starts, max(s, e - 1)) + 1
    body = "\n".join(
        re.sub(r"^\s*(//!|//+|#+|--+|/\*+|\*+/?|<!--|-->)", "", l).strip()
        for l in raw.splitlines()
    ).strip()

    prefix = text[line_starts[line - 1]:s]
    trailing = bool(prefix.strip())

    if raw.startswith("#!") and line == 1:
        return line, end_line, body, "shebang", True, "interpreter line"
    if PROTECTED.search(raw):
        return line, end_line, body, "directive", True, "toolchain reads it"
    if raw.startswith("/**") and JSDOC_TYPE.search(raw) and not path.endswith((".ts", ".tsx", ".mts", ".cts")):
        return line, end_line, body, "jsdoc-types", True, "types live in the comment"
    if WORK_MARKER.search(raw):
        return line, end_line, body, "work-marker", True, "tracked work, not narration"
    doc = raw.startswith(("///", "////", "//!", "/**"))
    if doc and DOCTEST.search(raw):
        return line, end_line, body, "doctest", True, "fenced example compiles and runs as a test"
    if SAFETY.search(body[:80]):
        return line, end_line, body, "safety", True, "states an unsafe/panic invariant"

    if not body:
        kind = "empty"
    elif BANNER.match(raw.strip()) or re.match(r"^[=\-*#~_]{3,}", body):
        kind = "banner"
    elif CODEISH.search(body):
        kind = "commented-code"
    elif doc:
        kind = "doc-block"
    elif trailing:
        kind = "trailing"
    elif end_line > line:
        kind = "block"
    else:
        kind = "line"
    return line, end_line, body, kind, False, ""


def line_index(line_starts, pos):
    lo, hi = 0, len(line_starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if line_starts[mid] <= pos:
            lo = mid
        else:
            hi = mid - 1
    return lo


def line_starts_of(text):
    starts = [0]
    for m in re.finditer("\n", text):
        starts.append(m.end())
    return starts


def collect(paths, next_id=0):
    out, skipped = [], []
    for path in paths:
        lang = lang_for(path)
        if lang is None:
            skipped.append((path, "unsupported file type"))
            continue
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError) as exc:
            skipped.append((path, str(exc)))
            continue
        starts = line_starts_of(text)
        for span in find_comments(text, lang):
            if span[1] <= span[0]:
                continue
            line, end_line, body, kind, prot, reason = classify(path, text, span, starts)
            next_id += 1
            out.append(Comment(next_id, path, line, end_line, span[0], span[1], body, kind, prot, reason))
    return out, skipped


def strip_line(line, ranges):
    out = line
    for a, b in sorted(ranges, reverse=True):
        left, right = out[:a], out[b:]
        if not right.strip():
            out = (left + right).rstrip()
        elif not left.strip():
            out = left + right.lstrip()
        else:
            l2, r2 = left.rstrip(), right.lstrip()
            glue = "" if l2[-1] in "([{" or r2[0] in ")]},;" else " "
            out = l2 + glue + r2
    return out


def remove(path, comments):
    text = open(path, encoding="utf-8").read()
    had_newline = text.endswith("\n")
    lines = text.split("\n")
    starts = line_starts_of(text)
    marks = {}
    for c in comments:
        for idx in range(c.line - 1, c.end_line):
            ls = starts[idx]
            le = ls + len(lines[idx])
            marks.setdefault(idx, []).append((max(c.start, ls) - ls, min(c.end, le) - ls))

    new = list(lines)
    dropped = set()
    for idx, ranges in marks.items():
        rebuilt = strip_line(lines[idx], ranges)
        if rebuilt.strip() == "":
            dropped.add(idx)
        else:
            new[idx] = rebuilt

    final, skip_blank, emitted = [], False, False
    for idx, line in enumerate(new):
        if idx in dropped:
            prev_blank = (not emitted) or (final and final[-1].strip() == "")
            j = idx + 1
            while j < len(new) and j in dropped:
                j += 1
            next_blank = j < len(new) and new[j].strip() == ""
            if prev_blank and next_blank:
                skip_blank = True
            continue
        if skip_blank and line.strip() == "":
            skip_blank = False
            continue
        final.append(line)
        if line.strip():
            emitted = True

    out = "\n".join(final)
    if had_newline and not out.endswith("\n"):
        out += "\n"
    while out.startswith("\n"):
        out = out[1:]
    return text, out


def git_files(mode, repo):
    def run(args):
        return subprocess.run(args, cwd=repo, capture_output=True, text=True).stdout.splitlines()

    if mode == "tracked":
        names = run(["git", "ls-files"])
    else:
        names = []
        for line in run(["git", "status", "--porcelain", "--untracked-files=all"]):
            status, name = line[:2], line[3:].strip()
            if " -> " in name:
                name = name.split(" -> ")[-1]
            is_new = status.strip() in ("A", "AM", "??")
            if mode == "created" and not is_new:
                continue
            names.append(name.strip('"'))
    return [os.path.join(repo, n) for n in names]


def expand(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                out += [os.path.join(root, f) for f in files]
        else:
            out.append(p)
    keep = []
    for p in out:
        parts = set(os.path.normpath(p).split(os.sep))
        if parts & SKIP_DIRS or SKIP_FILE.search(p) or not os.path.isfile(p):
            continue
        if lang_for(p) is None:
            continue
        keep.append(os.path.relpath(p))
    return sorted(set(keep))


def select(comments, only, include_protected):
    if not only:
        return []
    chosen = []
    everything = any(o == "everything" for o in only)
    files = {o.split(":", 1)[1] for o in only if o.startswith("file:")}
    kinds = {o.split(":", 1)[1] for o in only if o.startswith("kind:")}
    ids = {int(o.split(":", 1)[1]) for o in only if o.startswith("id:")}
    for c in comments:
        if c.protected and not include_protected:
            continue
        if everything or c.kind in kinds or c.id in ids or any(
            os.path.normpath(c.path) == os.path.normpath(f) for f in files
        ):
            chosen.append(c)
    return chosen


def report(comments, skipped, files):
    by_file = {}
    for c in comments:
        by_file.setdefault(c.path, []).append(c)
    kinds, prot = {}, []
    total_lines = 0
    for c in comments:
        kinds[c.kind] = kinds.get(c.kind, 0) + 1
        if c.protected:
            prot.append(c)
        else:
            total_lines += c.end_line - c.line + 1

    print(f"\nscanned {len(files)} file(s), found {len(comments)} comment(s)\n")
    if by_file:
        print(f"{'file':<48} {'nuke':>5} {'lines':>6} {'kept':>5}  kinds")
        for path in sorted(by_file):
            cs = by_file[path]
            nuke = [c for c in cs if not c.protected]
            lines = sum(c.end_line - c.line + 1 for c in nuke)
            src = len(open(path, encoding="utf-8").read().splitlines()) or 1
            ks = {}
            for c in nuke:
                ks[c.kind] = ks.get(c.kind, 0) + 1
            summary = ", ".join(f"{k} {v}" for k, v in sorted(ks.items(), key=lambda x: -x[1]))
            print(f"{path[-48:]:<48} {len(nuke):>5} {lines:>6} {len(cs) - len(nuke):>5}  "
                  f"{summary}  ({lines * 100 // src}% of {src} lines)")
    print(f"\ntotal to nuke: {len(comments) - len(prot)} comment(s), {total_lines} line(s)")
    if kinds:
        print("by kind: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    if prot:
        print(f"\nprotected ({len(prot)}) — kept unless --include-protected:")
        for c in prot:
            print(f"  [{c.id}] {c.path}:{c.line} {c.kind} — {c.text[:60]!r} ({c.reason})")
    if skipped:
        print(f"\nskipped ({len(skipped)}):")
        for path, why in skipped[:20]:
            print(f"  {path}: {why}")
    print("\nchoices: --only everything | --only file:<path> | --only kind:<kind> | --only id:<n>")
    print("add --apply to write. --include-protected also strips the protected list.")


def as_json(comments, skipped, files):
    return {
        "files": files,
        "skipped": [{"path": p, "reason": r} for p, r in skipped],
        "comments": [
            {
                "id": c.id, "path": c.path, "line": c.line, "end_line": c.end_line,
                "kind": c.kind, "protected": c.protected, "reason": c.reason,
                "text": c.text[:200],
            }
            for c in comments
        ],
    }


FIXTURES = [
    ("t.js", "const re = /https:\\/\\//; // gone\nlet a = 1 / 2; // gone\n",
     "const re = /https:\\/\\//;\nlet a = 1 / 2;\n"),
    ("t.js", "const s = `a ${/* gone */ b} // not a comment`;\n",
     "const s = `a ${b} // not a comment`;\n"),
    ("t.js", "const u = 'http://x'; // gone\n", "const u = 'http://x';\n"),
    ("t.py", 'x = "# not a comment"  # gone\ny = 1\n', 'x = "# not a comment"\ny = 1\n'),
    ("t.py", 'def f():\n    """kept docstring"""\n    return 1  # gone\n',
     'def f():\n    """kept docstring"""\n    return 1\n'),
    ("t.sh", 'n=$#\nfoo ${#bar}  # gone\n', 'n=$#\nfoo ${#bar}\n'),
    ("t.sh", "#!/bin/sh\n# gone\necho hi\n", "#!/bin/sh\necho hi\n"),
    ("t.vue", "<template>\n  <!-- gone -->\n  <p>hi</p>\n</template>\n<script setup>\n// gone\nlet a = 1\n</script>\n<style>\n/* gone */\n.a { color: red }\n</style>\n",
     "<template>\n  <p>hi</p>\n</template>\n<script setup>\nlet a = 1\n</script>\n<style>\n.a { color: red }\n</style>\n"),
    ("t.ts", "a()\n\n// gone\n\nb()\n", "a()\n\nb()\n"),
    ("t.ts", "/* eslint-disable no-console */\n// gone\nconsole.log(1)\n",
     "/* eslint-disable no-console */\nconsole.log(1)\n"),
    ("t.ts", "const a = 1 /* gone */ + 2\n", "const a = 1 + 2\n"),
    ("t.ts", "// TODO: kept\nlet x = 1\n", "// TODO: kept\nlet x = 1\n"),
    ("t.css", "/* gone */\n.a { color: red } /* gone */\n", ".a { color: red }\n"),
    ("t.sql", "select 1 -- gone\nfrom t\n", "select 1\nfrom t\n"),
    ("t.gleam", "// gone\npub fn main() { io.println(\"// not a comment\") }\n",
     "pub fn main() { io.println(\"// not a comment\") }\n"),
    ("t.go", "s := `http://x`\t// gone\n", "s := `http://x`\n"),
    ("t.go", "s := `a \\` // gone\n", "s := `a \\`\n"),
    ("t.rs", "// gone\nfn f<'a>(s: &'a str) -> &'a str { s } // gone\n",
     "fn f<'a>(s: &'a str) -> &'a str { s }\n"),
    ("t.rs", "let c = '\\''; // gone\nlet d = '/';  // gone\n", "let c = '\\'';\nlet d = '/';\n"),
    ("t.rs", 'let p = r"C:\\"; // gone\nlet q = r#"a "//" b"#; // gone\n',
     'let p = r"C:\\";\nlet q = r#"a "//" b"#;\n'),
    ("t.rs", "/* outer /* inner */ still comment */\nlet a = 1;\n", "let a = 1;\n"),
    ("t.rs", "/// Adds.\n///\n/// ```\n/// assert_eq!(add(1, 1), 2);\n/// ```\npub fn add(a: u8, b: u8) -> u8 { a + b }\n",
     "/// Adds.\n///\n/// ```\n/// assert_eq!(add(1, 1), 2);\n/// ```\npub fn add(a: u8, b: u8) -> u8 { a + b }\n"),
    ("t.rs", "/// Adds two numbers.\n/// Nothing else to say.\npub fn add(a: u8, b: u8) -> u8 { a + b }\n",
     "pub fn add(a: u8, b: u8) -> u8 { a + b }\n"),
    ("t.rs", "// SAFETY: ptr is non-null and aligned\nunsafe { *p }\n",
     "// SAFETY: ptr is non-null and aligned\nunsafe { *p }\n"),
    ("t.rs", "//! Module docs, gone.\nuse std::fmt;\n", "use std::fmt;\n"),
    ("t.rs", 'let s = "// not a comment"; // gone\n', 'let s = "// not a comment";\n'),
    ("t.gleam", "//// Module docs, gone.\n\n/// Doc, gone.\npub fn f() { 1 }\n", "pub fn f() { 1 }\n"),
    ("t.gleam", "pub fn f() { \"a // b\" } // gone\n", "pub fn f() { \"a // b\" }\n"),
    ("t.gleam", "/// Doc with a doctest kept:\n/// ```gleam\n/// f()\n/// ```\npub fn f() { 1 }\n",
     "/// Doc with a doctest kept:\n/// ```gleam\n/// f()\n/// ```\npub fn f() { 1 }\n"),
    ("t.ts", '/// <reference types="vite/client" />\nlet a = 1\n',
     '/// <reference types="vite/client" />\nlet a = 1\n'),
    ("t.js", "const p = s.split(/\\*/) // gone\n", "const p = s.split(/\\*/)\n"),
    ("t.js", "/**\n * @type {number}\n */\nlet n = 1\n", "/**\n * @type {number}\n */\nlet n = 1\n"),
    ("t.ts", "/**\n * @type {number} gone in ts\n */\nlet n = 1\n", "let n = 1\n"),
    ("t.ts", "let a = 1\n/*\n multi\n line\n*/\nlet b = 2\n", "let a = 1\nlet b = 2\n"),
    ("t.ts", "// gone\n\nlet a = 1\n", "let a = 1\n"),
    ("t.ts", "let a = 1 // no trailing newline", "let a = 1"),
    ("t.py", "def f():\n    # gone\n    return 1\n", "def f():\n    return 1\n"),
    ("t.html", "<p>a</p>\n<!-- gone\n     still gone -->\n<p>b</p>\n", "<p>a</p>\n<p>b</p>\n"),
]


def self_test(tmpdir):
    ok = True
    for i, (name, src, want) in enumerate(FIXTURES):
        path = os.path.join(tmpdir, f"{i}_{name}")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(src)
        comments, _ = collect([path])
        chosen = select(comments, ["everything"], False)
        _, got = remove(path, chosen)
        if got != want:
            ok = False
            print(f"FAIL {name} #{i}\n  input:    {src!r}\n  expected: {want!r}\n  got:      {got!r}")
    print("self-test: " + ("all fixtures pass" if ok else "FAILURES above"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Report, then remove, comments from code files.")
    ap.add_argument("paths", nargs="*", help="files or directories; default = files created in the repo")
    ap.add_argument("--created", action="store_true", help="files added/untracked in git (default)")
    ap.add_argument("--changed", action="store_true", help="all files git reports as dirty")
    ap.add_argument("--tracked", action="store_true", help="every tracked code file")
    ap.add_argument("--repo", default=".", help="repo root for git modes")
    ap.add_argument("--only", action="append", default=[],
                    metavar="SEL", help="everything | file:<path> | kind:<kind> | id:<n>")
    ap.add_argument("--include-protected", action="store_true")
    ap.add_argument("--apply", action="store_true", help="write the changes")
    ap.add_argument("--backup-dir", default=".nuke-comments-backup")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            return self_test(tmp)

    if args.paths:
        files = expand(args.paths)
    else:
        mode = "tracked" if args.tracked else "changed" if args.changed else "created"
        files = expand(git_files(mode, args.repo))
    if not files:
        print("no supported code files found", file=sys.stderr)
        return 1

    comments, skipped = collect(files)
    chosen = select(comments, args.only, args.include_protected)

    if args.json:
        payload = as_json(comments, skipped, files)
        payload["selected"] = [c.id for c in chosen]
        print(json.dumps(payload, indent=2))
        if not args.apply:
            return 0

    if not args.apply:
        if not args.json:
            report(comments, skipped, files)
        return 0

    if not chosen:
        print("nothing selected — pass --only everything (or a narrower selector)", file=sys.stderr)
        return 1

    by_file = {}
    for c in chosen:
        by_file.setdefault(c.path, []).append(c)

    os.makedirs(args.backup_dir, exist_ok=True)
    for path, cs in sorted(by_file.items()):
        before, after = remove(path, cs)
        if before == after:
            continue
        backup = os.path.join(args.backup_dir, path.replace(os.sep, "__"))
        with open(backup, "w", encoding="utf-8") as fh:
            fh.write(before)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(after)
        removed_lines = len(before.splitlines()) - len(after.splitlines())
        print(f"{path}: -{len(cs)} comment(s), -{removed_lines} line(s)")
    print(f"\nbackups in {args.backup_dir}/ — restore with: cp {args.backup_dir}/<name> <path>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
