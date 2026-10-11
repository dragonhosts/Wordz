# Codex Game Studio navigation

Read `.agents/game-studio/CODEX.md` first. This is an existing Unity project,
not an unconfigured studio template. No script output is pre-injected.

1. Explicitly run `python tools/game-studio/studio.py config` and `status` from
   the repository root. Read the current bounded checkpoint and referenced plan.
   Registry statuses determine eligibility; checkboxes determine progress.
2. Read `.agents/game-studio/catalog.json` or discover
   `.agents/skills/studio-*/SKILL.md` for installed skills. Actual frontmatter
   names are `studio-<name>`, user invocation is `$studio-<name>`; strip the `$`
   when comparing names. Do not enumerate workflow references as skills.
3. Explain current stage, active objective, paused tasks, actual checklist
   progress and the next eligible action. Never resume a paused plan or choose
   it merely because it contains unfinished checkboxes or code modifications.
   If nothing is eligible, ask what objective the user wants to pursue.
4. Use existing `DesignDoc/` and `docs/superpowers/{specs,plans}/` instead of
   flagging missing upstream directory names. Do not reset config or stage,
   restart onboarding, create a duplicate Story, or waive approved-plan tests.
5. Recommend the specific skill or installed Unity/Superpowers capability that
   serves the user's next action. Minimal is brief → stories → implement/verify
   for *new* work; the existing approved plan already supplies those artifacts.
   Wider lifecycle steps are documented in
   `.agents/game-studio/docs/workflow-catalog.yaml`; read only the relevant
   phase when the user needs that guidance. Its `$studio-*` commands refer to
   the actual names in catalog.json. Stage gates guide a decision; they are not
   a reason to invent missing design work in an adopted project.

The status command replaces upstream story-status preprocessing. It lists the
registered task lifecycle and current plan progress; for an epic with individual
Story files, inspect those requested files and dependency statuses explicitly.
Do not wait for nonexistent automatic queue injection.

For a specific workflow, run `python tools/game-studio/studio.py workflow <name>`
and read its live skill/reference. Help is navigation, not authorization to
implement, publish or commit a new objective.
