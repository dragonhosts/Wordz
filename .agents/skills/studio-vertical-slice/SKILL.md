---
name: studio-vertical-slice
description: "Game Studio / Pre-production validation — end-to-end build to confirm the full loop is achievable before committing to Production. After GDDs, architecture, UX specs."
---

# Game Studio: vertical-slice

Read `.agents/game-studio/CODEX.md` and run `python tools/game-studio/studio.py config` from the repository root. Do not execute embedded shell preprocessing or original Claude tool names.

Read `.agents/game-studio/workflows/vertical-slice/WORKFLOW.md` on demand and execute its relevant phases using the Codex adapter. Consult `python tools/game-studio/studio.py workflow vertical-slice` for project-specific routing. Existing approved plans and paused-task records govern scope. Read only references needed by this request; do not load the whole studio. Keep commits, pushes, merges and PR creation outside implementation until the project's completion and human approval gate.
