---
name: studio-architecture-decision
description: "Game Studio / Create an ADR documenting a technical decision: context, alternatives considered, consequences."
---

# Game Studio: architecture-decision

Read `.agents/game-studio/CODEX.md` and run `python tools/game-studio/studio.py config` from the repository root. Do not execute embedded shell preprocessing or original Claude tool names.

Read `.agents/game-studio/workflows/architecture-decision/WORKFLOW.md` on demand and execute its relevant phases using the Codex adapter. Consult `python tools/game-studio/studio.py workflow architecture-decision` for project-specific routing. Existing approved plans and paused-task records govern scope. Read only references needed by this request; do not load the whole studio. Keep commits, pushes, merges and PR creation outside implementation until the project's completion and human approval gate.
