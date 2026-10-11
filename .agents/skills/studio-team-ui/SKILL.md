---
name: studio-team-ui
description: "Game Studio / Orchestrate the UI team through the UX pipeline — authoring, visual design, implementation, review, polish. Uses /ux-design, /ux-review, studio templates."
---

# Game Studio: team-ui

Read `.agents/game-studio/CODEX.md` and run `python tools/game-studio/studio.py config` from the repository root. Do not execute embedded shell preprocessing or original Claude tool names.

Read `.agents/game-studio/workflows/team-ui/WORKFLOW.md` on demand and execute its relevant phases using the Codex adapter. Consult `python tools/game-studio/studio.py workflow team-ui` for project-specific routing. Existing approved plans and paused-task records govern scope. Read only references needed by this request; do not load the whole studio. Keep commits, pushes, merges and PR creation outside implementation until the project's completion and human approval gate.
