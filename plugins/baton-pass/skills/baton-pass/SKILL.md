---
name: baton-pass
description: Use when the user asks for Baton Pass moves in Codex, including `/new-game`, `/save-state`, `/baton-pass`, `/foresight`, `/dragon-dance`, `/party-check`, or `/hindsight`, or asks to manage handoff continuity for this repo.
---

# Baton Pass

## Purpose

Use this skill to maintain low-token continuity across Codex and other agents. Treat slash-looking user messages such as `/baton-pass` as requests to perform the corresponding Baton Pass move; Codex does not need Claude slash command files to run the workflow.

## Files

Read `baton-pass.config.json` first when present. By default, Baton Pass state lives in:

- `baton-pass.state.json`
- `docs/current-state.md`
- `docs/next-task.md`
- `docs/agent-handoff.md`
- `docs/progress.md`

If `docs/next-task.md` contains a `Turn State` block and it disagrees with `baton-pass.state.json`, treat `docs/next-task.md` as authoritative and repair the JSON when performing a write move.

## Verification Vocabulary

Use these terms exactly:

- `passed`: ran locally and output was confirmed clean.
- `passed outside sandbox`: ran locally outside the normal sandbox or CI environment.
- `not run - [reason]`: skipped, with the reason stated.
- `expected to pass, unverified`: not run, but believed correct.

Never write `passed` for work that was not actually run.

## Moves

### `new-game`

Use once when the repo has no Baton Pass files. Create the config, state, and docs listed above. Do not overwrite existing project-specific handoff files unless the user explicitly asks.

### `save-state`

Use when stopping without changing ownership. Write only the delta needed to resume: current task, stopping point, files touched, next immediate action, blockers, risks, and honest verification status. Update both state JSON and docs.

### `baton-pass`

Use when ownership changes or context is running low. Before handoff, inspect `git status`. Commit first when appropriate and allowed. If the tree remains dirty, name the uncommitted state explicitly.

Record only:

- goal
- done
- task statuses when mid-plan
- files changed
- worktree path and branch
- verified
- deviations from the original plan
- environment prerequisites
- next task
- risks
- next agent

Update `docs/current-state.md`, `docs/next-task.md`, `docs/progress.md`, and `baton-pass.state.json`.

### `foresight`

Use when receiving a baton or resuming after a pause. Before code changes, inspect the user goal, `git status`, recent commits, current state, next task, latest progress entry, and files named in the baton. Report whether the repo is aligned or misaligned. If misaligned, correct the handoff docs before continuing.

### `party-check`

Use for a cheap ownership check. Read `baton-pass.state.json` and the `Turn State` block if present, then report who owns the work, current state, last move, and next expected action.

### `hindsight`

Use for a full audit of the baton chain. Summarize handoffs, claimed milestones, verification gaps, carried risks, drift, open items, and a verdict: `clean`, `gaps found`, `risks unresolved`, or `action required`.

### `dragon-dance`

Use only when a real reusable workflow lesson appeared, such as stale handoff docs, misleading verification, missing environment prerequisites, or repeated re-audit. Append the lesson to the appropriate handoff/progress docs. Skip it when there is no lesson.

## Rules

- Default to deltas, not project recaps.
- Do not rewrite all memory files for small updates.
- Keep repo-specific rules in `AGENTS.md` and handoff docs, not in this plugin.
- Do not hide broken state at handoff; document it as a blocker or risk.
- Do not use `--no-verify` when committing.
