# /save-state — Checkpoint without transfer

Pause mid-session: commit work in progress and update state docs without handing off.

## Steps

1. Stage and commit work in progress with a `wip:` prefix on the commit message.
2. Update `docs/current-state.md` — move completed subtasks under "What's done", note what's still in progress.
3. Append a short entry to `docs/progress.md` with what's done so far and where you stopped.
4. Update `baton-pass.state.json`: set `state` to `in_progress`, update `updatedAt` and `summary`.
5. Report: "State saved. Resuming at: [description of next step]."

Use this when you need to stop mid-task but want to preserve context for continuation.
