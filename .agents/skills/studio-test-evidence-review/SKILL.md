---
name: studio-test-evidence-review
description: "Game Studio / Quality review of test files and evidence — goes beyond existence, evaluates assertion coverage. ADEQUATE/INCOMPLETE/MISSING/NOT ASSESSED per story."
---

# Game Studio: test-evidence-review

Read `.agents/game-studio/CODEX.md` and run `python tools/game-studio/studio.py config` from the repository root. Do not execute embedded shell preprocessing or original Claude tool names.

Read `.agents/game-studio/workflows/test-evidence-review/WORKFLOW.md` on demand and execute its relevant phases using the Codex adapter. Consult `python tools/game-studio/studio.py workflow test-evidence-review` for project-specific routing. Existing approved plans and paused-task records govern scope. Read only references needed by this request; do not load the whole studio. Keep commits, pushes, merges and PR creation outside implementation until the project's completion and human approval gate.
