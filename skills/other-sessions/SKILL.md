---
name: other-sessions
description: Warn the current session that other Claude sessions are modifying the same codebase concurrently. Use when the user invokes /other-sessions, or mentions that parallel sessions/agents are working in the repo. Ignore unrelated changes as much as possible, and be conservative with commits — ask the user before committing files that mix this session's edits with someone else's.
---

# Other Sessions

## Context

Other Claude sessions (or the user) are modifying this codebase at the same time as you. Files, git status, and branches can change under you at any moment, and that is expected — not a bug, not corruption, not something to fix.

## Rules

### 1. Ignore changes that aren't yours

- If a file you didn't touch appears modified, added, or deleted in `git status`, ignore it. Don't investigate it, don't revert it, don't "clean it up", don't mention it unless it directly blocks your task.
- If a file you read earlier has changed when you come back to it, re-read it and continue. Don't treat the drift as an anomaly worth reporting.
- Never run destructive git commands that could wipe other sessions' work: no `git checkout .`, `git restore`, `git reset --hard`, `git stash`, or `git clean` on files you didn't modify.

### 2. Track what you actually changed

Keep a mental list of the files YOU modified in this session. That list — not `git status` — defines the scope of what you're allowed to stage, commit, or revert.

### 3. Commits: conservative, file-by-file

When committing:

- Stage only the specific files you modified in this session, by explicit path. Never use `git add -A`, `git add .`, or `git commit -a`.
- Before staging, diff each file (`git diff <file>`). If the diff contains ONLY your changes, it's safe to stage.
- **If a file contains both your changes and changes you don't recognize (another session edited the same file): STOP.** Do not stage it, do not try to partially stage hunks, do not guess which changes are whose. Show the user the mixed diff and ask how to proceed. Wait for their answer.
- If `git status` changes between your diff check and your commit, re-check before committing.

### 4. Branches and pulls

- Don't switch branches, rebase, or pull unless the user asks — another session may be mid-work on the current branch.
- If a commit fails because HEAD moved (another session committed), re-diff your files against the new HEAD and re-verify before retrying.

## Summary

Work as if you have a narrow lease on exactly the files you edit. Everything else in the repo belongs to someone else: read it if you need to, never write to it, never revert it, and when ownership of a file is ambiguous at commit time, ask the user instead of deciding.
