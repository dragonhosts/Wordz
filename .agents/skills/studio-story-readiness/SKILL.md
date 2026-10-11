---
name: studio-story-readiness
description: "Game Studio / Is a story implementation-ready? Checks clear acceptance criteria, open questions, ADR refs. READY/NEEDS WORK/BLOCKED/NOT ASSESSED."
---

# Game Studio: story-readiness

Read `.agents/game-studio/CODEX.md` and run `python tools/game-studio/studio.py config` from the repository root. Do not execute embedded shell preprocessing or original Claude tool names.

Read `.agents/game-studio/workflows/story-readiness/WORKFLOW.md` on demand and execute its relevant phases using the Codex adapter. Consult `python tools/game-studio/studio.py workflow story-readiness` for project-specific routing. Existing approved plans and paused-task records govern scope. Read only references needed by this request; do not load the whole studio. Keep commits, pushes, merges and PR creation outside implementation until the project's completion and human approval gate.
