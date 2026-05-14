# /hindsight — Full session audit

Review the full baton chain for gaps, verification failures, and open risks.

## Steps

1. Read all of `docs/progress.md`.
2. Read `docs/current-state.md` and `docs/next-task.md`.
3. Run `git log --oneline -20` and compare to progress entries — are there commits with no corresponding progress note?
4. Check for verification gaps: sessions that modified frontend/Rust/backend without recording a type-check or lint result.
5. Identify open risks: tasks described as "done" that weren't verified, deviations from spec that weren't documented.
6. Report a numbered list:
   - **Baton chain:** sessions in order, agent, what was handed off
   - **Verification gaps:** sessions that skipped checks
   - **Open risks:** anything that could break or was left incomplete
   - **Recommended next action:** one specific thing to address first

Keep the report factual. Don't speculate — if something isn't recorded, say so.
