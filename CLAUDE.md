# Claude-specific config — shared project rules live in AGENTS.md

## RTK
Always prefix commands with `rtk`. Safe to use everywhere — passes through unchanged if no filter exists.

## Skills
Superpowers skills are active. Invoke the relevant skill before any significant task.
Key skills: brainstorming (before features), writing-plans (before implementation),
verification-before-completion (before claiming done), systematic-debugging (before fixes).

## Memory
Project memory lives in ~/.claude/projects/.../memory/. Read it at session start.
