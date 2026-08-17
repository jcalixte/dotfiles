#!/usr/bin/env python3
"""Report and remove non-essential doc sections. Dry-run by default."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", "target", "vendor", ".venv",
    "venv", "__pycache__", ".next", ".nuxt", ".svelte-kit", "coverage",
    ".nuke-docs-backup", "CHANGELOG.d",
}
DOC_EXT = (".md", ".markdown", ".mdx", ".rst", ".txt", ".adoc")
INSTRUCTION_FILES = {"claude.md", "agents.md", "gemini.md", ".cursorrules",
                     "copilot-instructions.md", "skill.md"}
INSTRUCTION_DIRS = ("/.claude/", "/.cursor/", "/.github/instructions/", "/skills/", "/prompts/")
LEGAL_FILES = {"license", "license.md", "licence.md", "notice.md", "security.md", "code_of_conduct.md"}
DIARY_FILES = re.compile(
    r"(^|/)(notes|worklog|work-log|journal|diary|devlog|session[-_.\w]*|scratch|log|"
    r"progress|status|history|changelog-draft|todo)\.(md|markdown|txt)$", re.I)

ESSENTIAL_TECH = re.compile(
    r"\b(install\w*|setup|set\s?up|getting\s+started|quick\s?start|usage|run\b|running|"
    r"develop\w*|build\w*|deploy\w*|tests?\b|testing|configur\w*|environment|envs?\b|"
    r"architect\w*|design\w*|schema\w*|apis?\b|endpoint\w*|clis?\b|command\w*|option\w*|flag\w*|"
    r"troubleshoot\w*|debug\w*|faqs?\b|requirement\w*|prerequisite\w*|depend\w*|migration|"
    r"upgrad\w*|security|permission\w*|auth\w*|decision\w*|adrs?\b|constraint\w*|invariant\w*|"
    r"contract\w*|glossary|data\s+model|structure|layout|script\w*|hook\w*|workflow\w*)", re.I)
ESSENTIAL_PRODUCT = re.compile(
    r"\b(what\s+(is|it|this)|overview|purpose|feature\w*|capabilit\w*|use\s+case|"
    r"who\s+(is|it|this)|audience|scope|goal\w*|non-goal\w*|principle\w*|vocabulary|"
    r"concept\w*|domain|screen\w*|flow\w*|user\w*)", re.I)
HISTORY_HEAD = re.compile(
    r"\b(history|background|changelog|change\s+log|release\s+notes|previously|legacy|"
    r"timeline|retro\w*|post-?mortem|lessons|migration\s+log|what.s\s+new|origin)\b", re.I)
DIARY_HEAD = re.compile(
    r"\b(journal|worklog|work\s+log|diary|session|log\s+of|day\s+\d|week\s+\d|"
    r"20\d\d-\d\d-\d\d|sprint\s+\d)\b", re.I)
STATUS_HEAD = re.compile(
    r"\b(status|progress|current\s+state|state\s+of|roadmap|next\s+steps|planned|"
    r"upcoming|wip|work\s+in\s+progress|open\s+questions|ideas|backlog|future)\b", re.I)
META_HEAD = re.compile(
    r"\b(table\s+of\s+contents|contents|toc|about\s+this\s+(doc|document|file)|"
    r"how\s+to\s+read|conventions\s+used|document\s+structure|index)\b", re.I)

DATE_STAMP = re.compile(
    r"\b(as\s+of|updated?\s+(on|in)|last\s+updated|since|circa)\s+\w*\s*20\d\d|\b20\d\d-\d\d-\d\d\b", re.I)
PAST_STATE = re.compile(
    r"\b(previously|used\s+to\s+(be|use|live)|we\s+(refactored|renamed|moved|migrated|switched|"
    r"decided|replaced)|has\s+been\s+(moved|replaced|renamed)|no\s+longer|formerly|"
    r"before\s+the\s+\w+\s+(refactor|migration|split)|now\s+lives|used\s+to)\b", re.I)
PADDING = re.compile(
    r"\b(it.s\s+(important|worth)\s+to\s+note|it\s+is\s+important\s+to|in\s+today.s|"
    r"seamless\w*|robust\w*|leverage[sd]?|delve|comprehensive\s+(solution|guide|overview)|"
    r"cutting[\s-]edge|state[\s-]of[\s-]the[\s-]art|best[\s-]in[\s-]class|"
    r"at\s+the\s+end\s+of\s+the\s+day|in\s+conclusion|this\s+document\s+(describes|aims|will)|"
    r"the\s+goal\s+of\s+this\s+(document|section)\s+is|feel\s+free\s+to|"
    r"unlock\w*\s+the\s+(power|potential)|game[\s-]chang\w+|effortless\w*|"
    r"in\s+the\s+ever[\s-]evolving|plays?\s+a\s+(crucial|vital|key)\s+role)\b", re.I)
DATED_FILE = re.compile(r"^(20\d\d-\d\d-\d\d|\d{8})[-_.]")
DEF_LIST = re.compile(r"^\s*[-*+]\s+\*\*[^*]+\*\*\s*[—:-]|^\s*\*\*[^*]+\*\*\s*[—:-]", re.M)
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$", re.M)
NORMATIVE = re.compile(
    r"\b(must|never|always|do not|don.t|required|forbidden|only\s+ever|"
    r"shall|has\s+to|cannot|may\s+not)\b", re.I)
KEEP_MARK = re.compile(r"<!--\s*(keep|nuke-docs:\s*keep)\s*-->", re.I)
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*$")
SETEXT = re.compile(r"^=+\s*$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
RUN_CMD = re.compile(r"\b(?:pnpm|npm|yarn|bun)\s+(?:run\s+)?([a-z][\w:-]*)|\bmake\s+([a-z][\w:-]*)", re.I)
PM_BUILTINS = {"install", "add", "remove", "dlx", "exec", "create", "init", "why", "up", "outdated",
               "test", "start", "publish", "link", "audit", "ci", "i", "x", "run"}


@dataclass
class Section:
    id: int
    path: str
    heading: str
    level: int
    start: int
    end: int
    words: int
    kind: str = "unknown"
    protected: bool = False
    reason: str = ""
    signals: list = field(default_factory=list)
    children: list = field(default_factory=list)


def slug(text):
    return re.sub(r"[^a-z0-9\s-]", "", text.lower()).strip().replace(" ", "-")


def split_sections(path, lines):
    front = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                front = i + 1
                break

    marks, in_fence = [], False
    for i in range(front, len(lines)):
        line = lines[i]
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if m:
            marks.append((i, len(m.group(1)), m.group(2).strip()))
            continue
        # `=` underline only: a `---` line is a thematic break far more often than a setext h2
        if i > front and SETEXT.match(line) and lines[i - 1].strip() and not HEADING.match(lines[i - 1]):
            marks.append((i - 1, 1, lines[i - 1].strip()))

    out = []
    if front:
        out.append(Section(0, path, "(front matter)", 0, 0, front - 1, 0,
                           kind="front-matter", protected=True, reason="parsed metadata"))
    if marks and marks[0][0] > front and any(l.strip() for l in lines[front:marks[0][0]]):
        out.append(Section(0, path, "(preamble)", 1, front, marks[0][0] - 1, 0))
    elif not marks:
        out.append(Section(0, path, "(whole file)", 1, front, len(lines) - 1, 0))

    for n, (start, level, heading) in enumerate(marks):
        end = marks[n + 1][0] - 1 if n + 1 < len(marks) else len(lines) - 1
        out.append(Section(0, path, heading, level, start, end, 0))
    for s in out:
        s.words = sum(len(l.split()) for l in lines[s.start:s.end + 1])
    return out


def body(lines, s):
    return "\n".join(lines[s.start:s.end + 1])


def classify(sec, text, repo_state, is_title=False):
    head, sig = sec.heading, []
    if KEEP_MARK.search(text):
        return "kept-by-marker", True, "`<!-- keep -->` in the section"
    posix = "/" + sec.path.replace(os.sep, "/").lower()
    base = os.path.basename(sec.path).lower()
    if base in INSTRUCTION_FILES or any(d in posix for d in INSTRUCTION_DIRS):
        return "instruction", True, "agent instruction file — needs --include-instructions"
    if base in LEGAL_FILES:
        return "legal", True, "legal or security contact text"
    if DIARY_FILES.search(sec.path.replace(os.sep, "/")):
        return "diary", False, "work log — the repo already records this"
    if DATED_FILE.search(base):
        return "dated-doc", False, "a dated snapshot — true on its date, not today"
    if is_title:
        return "title", True, "document title"

    dates = DATE_STAMP.findall(text)
    past = PAST_STATE.findall(text)
    pad = PADDING.findall(text)
    dead = [t for t in LINK.findall(text) if is_dead_link(sec.path, t)]
    stale = stale_commands(text, repo_state)
    if dates:
        sig.append(f"{len(dates)} date stamp(s)")
    if past:
        sig.append(f"{len(past)} past-state phrase(s)")
    if pad:
        sig.append(f"{len(pad)} padded phrase(s)")
    if dead:
        sig.append(f"dead link: {', '.join(dead[:3])}")
    if stale:
        sig.append(f"stale command: {', '.join(stale[:3])}")
    sec.signals = sig

    if DIARY_HEAD.search(head) or DIARY_FILES.search(sec.path.replace(os.sep, "/")):
        return "diary", False, "work log — the repo already records this"
    if HISTORY_HEAD.search(head):
        return "history", False, "past state, not current truth"
    if STATUS_HEAD.search(head):
        return "status", False, "status rots the day it is written"
    if META_HEAD.search(head):
        return "meta", False, "navigation the reader does not need"
    if not text.strip() or sec.words < 3:
        return "empty", False, "no content"
    if len(past) >= 2 or (past and dates):
        return "history", False, "narrates how it used to be"
    if ESSENTIAL_TECH.search(head):
        return "tech", True, "how to run, build, or reason about the system"
    if ESSENTIAL_PRODUCT.search(head):
        return "product", True, "what this is and what it does"
    if dead and sec.words < 60:
        return "dead-reference", False, "points at files that no longer exist"
    if pad and sec.words < 120 and "```" not in text:
        return "padding", False, "prose with no fact a reader can act on"
    if "```" in text:
        return "tech", True, "carries a runnable example"
    if len(DEF_LIST.findall(text)) >= 3 or len(TABLE_ROW.findall(text)) >= 3:
        return "reference", True, "term or option table a reader looks things up in"
    if len(NORMATIVE.findall(text)) >= 2:
        return "tech", True, "states rules the reader must follow"
    return "unknown", False, "needs a judgment call"


_SLUGS = {}


def heading_slugs(path):
    if path not in _SLUGS:
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            _SLUGS[path] = set()
        else:
            _SLUGS[path] = {slug(m.group(2)) for m in
                            (HEADING.match(l) for l in text.split("\n")) if m}
    return _SLUGS[path]


def is_dead_link(src, target):
    if re.match(r"^(https?:|mailto:|<)", target):
        return False
    rel, _, anchor = target.partition("#")
    dest = os.path.join(os.path.dirname(src) or ".", rel) if rel else src
    if rel and not os.path.exists(dest):
        return True
    if anchor and dest.lower().endswith((".md", ".markdown", ".mdx")):
        return slug(anchor) not in heading_slugs(dest)
    return False


def stale_commands(text, repo_state):
    scripts, makefile = repo_state
    if scripts is None:
        return []
    out = []
    for pm, mk in RUN_CMD.findall(text):
        name = pm or mk
        if mk:
            if makefile is not None and name not in makefile:
                out.append(f"make {name}")
        elif name.lower() not in PM_BUILTINS and name not in scripts:
            out.append(f"run {name}")
    return sorted(set(out))


def repo_scripts(repo):
    scripts, makefile = None, None
    pkg = os.path.join(repo, "package.json")
    if os.path.exists(pkg):
        try:
            scripts = set(json.load(open(pkg, encoding="utf-8")).get("scripts", {}))
        except (ValueError, OSError):
            scripts = set()
    mk = os.path.join(repo, "Makefile")
    if os.path.exists(mk):
        makefile = set(re.findall(r"^([a-zA-Z][\w:-]*):", open(mk, encoding="utf-8").read(), re.M))
    return scripts, makefile


def shingles(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {hashlib.md5(" ".join(words[i:i + 8]).encode()).hexdigest()[:8]
            for i in range(0, max(0, len(words) - 7))}


def mark_duplicates(sections, texts):
    seen = {}
    for sec in sections:
        if sec.protected or sec.words < 40:
            continue
        sh = shingles(texts[sec.id])
        if not sh:
            continue
        for other, osh in seen.items():
            overlap = len(sh & osh) / max(1, len(sh))
            if overlap > 0.6:
                sec.kind, sec.reason = "duplicate", f"~{int(overlap * 100)}% repeats {other}"
                break
        else:
            seen[f"{sec.path}#{slug(sec.heading)}"] = sh


def mark_inbound_anchors(sections, texts, all_paths):
    wanted = set()
    for sec in sections:
        for target in LINK.findall(texts[sec.id]):
            if "#" not in target or target.startswith("http"):
                continue
            rel, anchor = target.split("#", 1)
            base = os.path.normpath(os.path.join(os.path.dirname(sec.path) or ".", rel)) if rel else sec.path
            wanted.add((os.path.normpath(base), anchor.lower()))
    for sec in sections:
        if (os.path.normpath(sec.path), slug(sec.heading)) in wanted and sec.kind not in (
            "diary", "history", "status", "duplicate"
        ):
            sec.protected = True
            sec.reason = "another doc links to this heading"


def collect(files, repo):
    state = repo_scripts(repo)
    sections, texts, lines_by_file = [], {}, {}
    nid = 0
    for path in files:
        try:
            lines = open(path, encoding="utf-8").read().split("\n")
        except (OSError, UnicodeDecodeError):
            continue
        lines_by_file[path] = lines
        secs = split_sections(path, lines)
        titles = [s for s in secs if s.level == 1 and s.heading not in ("(preamble)", "(whole file)")]
        title_id = id(titles[0]) if titles else None
        for sec in secs:
            sec.id = nid
            nid += 1
            text = body(lines, sec)
            texts[sec.id] = text
            if not sec.protected:
                sec.kind, sec.protected, sec.reason = classify(
                    sec, text, state, is_title=id(sec) == title_id and sec.words < 40)
            sections.append(sec)
    mark_duplicates(sections, texts)
    mark_inbound_anchors(sections, texts, files)
    attach_children(sections)
    for sec in sections:
        if sec.children and not sec.protected and sec.kind in ("empty", "unknown", "title"):
            sec.kind, sec.protected, sec.reason = "parent", True, "heading over subsections"
    return sections, texts, lines_by_file


def attach_children(sections):
    by_file = {}
    for sec in sections:
        by_file.setdefault(sec.path, []).append(sec)
    for secs in by_file.values():
        for i, sec in enumerate(secs):
            for other in secs[i + 1:]:
                if other.level <= sec.level or other.level == 0:
                    break
                sec.children.append(other.id)


NUKE_KINDS = {"diary", "history", "status", "meta", "padding", "duplicate", "dead-reference",
              "empty", "dated-doc"}


def select(sections, only, include_instructions):
    if not only:
        return []
    everything = "everything" in only
    files = {o.split(":", 1)[1] for o in only if o.startswith("file:")}
    kinds = {o.split(":", 1)[1] for o in only if o.startswith("kind:")}
    ids = {int(o.split(":", 1)[1]) for o in only if o.startswith("id:")}
    by_id = {s.id: s for s in sections}
    chosen = {}
    for sec in sections:
        if sec.protected and not (include_instructions and sec.kind == "instruction"):
            continue
        hit = (
            sec.id in ids
            or sec.kind in kinds
            or (everything and sec.kind in NUKE_KINDS)
            or (any(os.path.normpath(sec.path) == os.path.normpath(f) for f in files)
                and sec.kind in NUKE_KINDS)
        )
        if hit:
            chosen[sec.id] = sec
            for cid in sec.children:
                child = by_id[cid]
                if not child.protected:
                    chosen[cid] = child
    for sec in sections:
        if sec.kind == "parent" and sec.children and sec.id not in chosen:
            if all(cid in chosen for cid in sec.children):
                chosen[sec.id] = sec
    return [chosen[i] for i in sorted(chosen)]


def dangling_after(all_files, removed_files, removed_anchors):
    out = []
    for path in all_files:
        if path in removed_files or not os.path.exists(path):
            continue
        try:
            text = open(path, encoding="utf-8").read()
        except OSError:
            continue
        for target in LINK.findall(text):
            if target.startswith(("http", "mailto:", "<")):
                continue
            rel, _, anchor = target.partition("#")
            dest = os.path.normpath(os.path.join(os.path.dirname(path) or ".", rel)) if rel else path
            if rel and dest in removed_files:
                out.append(f"{path} → {target} (file removed)")
            elif anchor and (dest, anchor.lower()) in removed_anchors:
                out.append(f"{path} → {target} (heading removed)")
    return out


def apply(chosen, lines_by_file, backup_dir):
    by_file = {}
    for sec in chosen:
        by_file.setdefault(sec.path, []).append(sec)
    removed_files, removed_anchors = set(), set()
    for sec in chosen:
        removed_anchors.add((os.path.normpath(sec.path), slug(sec.heading)))
    os.makedirs(backup_dir, exist_ok=True)
    for path, secs in sorted(by_file.items()):
        lines = lines_by_file[path]
        drop = set()
        for sec in secs:
            drop.update(range(sec.start, sec.end + 1))
        kept = [l for i, l in enumerate(lines) if i not in drop]
        while kept and not kept[0].strip():
            kept.pop(0)
        out, blank = [], False
        for line in kept:
            if not line.strip():
                if blank:
                    continue
                blank = True
            else:
                blank = False
            out.append(line)
        while out and not out[-1].strip():
            out.pop()
        backup = os.path.join(backup_dir, path.replace(os.sep, "__"))
        with open(backup, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        remaining = "\n".join(out).strip()
        if remaining and all(HEADING.match(l) or not l.strip() for l in out):
            remaining = ""
        if not remaining:
            os.remove(path)
            removed_files.add(os.path.normpath(path))
            print(f"{path}: removed entirely ({len(secs)} section(s), nothing essential left)")
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(remaining + "\n")
        print(f"{path}: -{len(secs)} section(s), -{len(lines) - len(out)} line(s)")

    dangling = dangling_after(list(lines_by_file), removed_files, removed_anchors)
    if dangling:
        print(f"\n{len(dangling)} link(s) now dangle — fix or drop them:")
        for d in dangling[:20]:
            print(f"  {d}")
    print(f"\nbackups in {backup_dir}/ — restore with: cp {backup_dir}/<name> <path>")


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
        if set(os.path.normpath(p).split(os.sep)) & SKIP_DIRS:
            continue
        if not p.lower().endswith(DOC_EXT) or not os.path.isfile(p):
            continue
        keep.append(os.path.relpath(p))
    return sorted(set(keep))


def git_files(mode, repo):
    def run(args):
        return subprocess.run(args, cwd=repo, capture_output=True, text=True).stdout.splitlines()

    if mode == "tracked":
        names = run(["git", "ls-files"])
    else:
        names = []
        for line in run(["git", "status", "--porcelain", "--untracked-files=all"]):
            status, name = line[:2].strip(), line[3:].strip()
            if " -> " in name:
                name = name.split(" -> ")[-1]
            if mode == "created" and status not in ("A", "AM", "??"):
                continue
            names.append(name.strip('"'))
    return [os.path.join(repo, n) for n in names]


def report(sections, files):
    by_file = {}
    for sec in sections:
        by_file.setdefault(sec.path, []).append(sec)
    nuke_words = sum(s.words for s in sections if s.kind in NUKE_KINDS and not s.protected)
    unknown_words = sum(s.words for s in sections if s.kind == "unknown" and not s.protected)
    total_words = sum(s.words for s in sections)
    pct = lambda w: w * 100 // max(1, total_words)

    print(f"\nscanned {len(files)} doc(s), {total_words} words in {len(sections)} section(s)")
    print(f"flagged non-essential: {nuke_words} words ({pct(nuke_words)}%)")
    print(f"unclassified, needs judgment: {unknown_words} words ({pct(unknown_words)}%)\n")
    for path in sorted(by_file):
        secs = by_file[path]
        tw = sum(s.words for s in secs)
        nw = sum(s.words for s in secs if s.kind in NUKE_KINDS and not s.protected)
        print(f"{path}  —  {tw} words, {nw} non-essential ({nw * 100 // max(1, tw)}%)")
        for sec in secs:
            tag = "keep " if sec.protected or sec.kind in ("product", "tech") else "NUKE "
            if sec.kind == "unknown":
                tag = "JUDGE"
            head = ("  " * max(0, sec.level - 1)) + (sec.heading or "(untitled)")
            print(f"  [{sec.id:>3}] {tag} {sec.kind:<14} {sec.words:>5}w  {head[:52]}")
            if sec.signals:
                print(f"        signals: {'; '.join(sec.signals)}")
            if sec.reason and tag != "keep ":
                print(f"        {sec.reason}")
        print()
    unknown = [s for s in sections if s.kind == "unknown"]
    if unknown:
        print(f"{len(unknown)} section(s) need a judgment call — read them, then decide:")
        for sec in unknown[:20]:
            print(f"  [{sec.id}] {sec.path}: {sec.heading} ({sec.words}w)")
    print("\nchoices: --only everything | --only file:<path> | --only kind:<kind> | --only id:<n>")
    print("add --apply to write. --include-instructions also touches CLAUDE.md / AGENTS.md.")


def as_json(sections, files):
    return {
        "files": files,
        "sections": [
            {"id": s.id, "path": s.path, "heading": s.heading, "level": s.level,
             "lines": [s.start + 1, s.end + 1], "words": s.words, "kind": s.kind,
             "protected": s.protected, "reason": s.reason, "signals": s.signals,
             "children": s.children}
            for s in sections
        ],
    }


FIXTURES = [
    ("README.md", "# Thing\n\n## Usage\n\nRun `pnpm dev`.\n\n## History\n\nPreviously we used gulp.\n",
     ["title", "tech", "history"]),
    ("README.md", "# Thing\n\n## Status\n\nAs of 2026-08-04 the parser is done.\n", ["title", "status"]),
    ("WORKLOG.md", "# Log\n\n## 2026-08-01\n\nFixed the thing.\n", ["diary", "diary"]),
    ("README.md", "# Thing\n\n## Table of Contents\n\n- [Usage](#usage)\n\n## Usage\n\nRun it.\n",
     ["title", "meta", "tech"]),
    ("CLAUDE.md", "# Rules\n\n## Never\n\nDo not force push.\n", ["instruction", "instruction"]),
    ("0002-modes.md", "---\nstatus: accepted\n---\n\n# Two modes\n\nA reference resolves live or by SHA.\n",
     ["front-matter", "title"]),
    ("guide.md", "Title\n=====\n\n## Usage\n\nRun it.\n\n---\n\n## History\n\nPreviously gulp.\n",
     ["title", "tech", "history"]),
    ("README.md", "# Thing\n\n## Architecture\n\nIt is important to note that this leverages a robust,"
                  " seamless, cutting-edge pipeline.\n", ["title", "tech"]),
    ("README.md", "# Thing\n\n## Philosophy\n\nWe delve into a comprehensive solution that unlocks the"
                  " power of synergy at the end of the day.\n", ["title", "padding"]),
]


def self_test(tmpdir):
    ok = True
    for n, (name, src, want) in enumerate(FIXTURES):
        d = os.path.join(tmpdir, str(n))
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(src)
        sections, _, _ = collect([path], d)
        got = [s.kind for s in sections]
        if got != want:
            ok = False
            print(f"FAIL #{n} {name}\n  expected: {want}\n  got:      {got}")
    print("self-test: " + ("all fixtures pass" if ok else "FAILURES above"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Report, then remove, non-essential doc sections.")
    ap.add_argument("paths", nargs="*", help="docs or directories; default = docs created in the repo")
    ap.add_argument("--created", action="store_true", help="docs added/untracked in git (default)")
    ap.add_argument("--changed", action="store_true")
    ap.add_argument("--tracked", action="store_true", help="every tracked doc")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--only", action="append", default=[], metavar="SEL")
    ap.add_argument("--include-instructions", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backup-dir", default=".nuke-docs-backup")
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
        print("no docs found", file=sys.stderr)
        return 1

    sections, _, lines_by_file = collect(files, args.repo)
    chosen = select(sections, args.only, args.include_instructions)

    if args.json:
        payload = as_json(sections, files)
        payload["selected"] = [s.id for s in chosen]
        print(json.dumps(payload, indent=2))
        if not args.apply:
            return 0
    if not args.apply:
        if not args.json:
            report(sections, files)
        return 0
    if not chosen:
        print("nothing selected — pass --only everything (or a narrower selector)", file=sys.stderr)
        return 1
    apply(chosen, lines_by_file, args.backup_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
