---
name: studio-qa-plan
description: "Game Studio / QA test plan for a sprint — classifies stories by Logic/Integration/Visual/UI, covers automated tests, manual cases, smoke scope."
---

# Game Studio: qa-plan

Read `.agents/game-studio/CODEX.md` and run `python tools/game-studio/studio.py config` from the repository root. Do not execute embedded shell preprocessing or original Claude tool names.

Read `.agents/game-studio/workflows/qa-plan/WORKFLOW.md` on demand and execute its relevant phases using the Codex adapter. Consult `python tools/game-studio/studio.py workflow qa-plan` for project-specific routing. Existing approved plans and paused-task records govern scope. Read only references needed by this request; do not load the whole studio. Keep commits, pushes, merges and PR creation outside implementation until the project's completion and human approval gate.
