# /foresight — Receive session

Read the current state and claim ownership of this session.

## Steps

1. Read `docs/current-state.md` — understand what's done, what's in progress, any blockers.
2. Read `docs/next-task.md` — understand the single next task and its acceptance criteria.
3. Read `docs/agent-handoff.md` — recall repo-specific rules and forbidden operations.
4. Skim `docs/progress.md` (last 2–3 entries) — pick up any lessons from recent sessions.
5. Verify alignment:
   - Does `baton-pass.state.json` match `current-state.md`? If not, note the discrepancy.
   - Is the next task still valid given the current code state? Do a quick `git log --oneline -5` to confirm.
6. Report back in one paragraph: what phase we're in, what you're about to work on, any concerns.

Do not write any code until foresight is complete and the user has confirmed.
