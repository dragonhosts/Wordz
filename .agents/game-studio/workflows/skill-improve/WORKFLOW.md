# Codex studio skill improvement

Read `.agents/game-studio/CODEX.md`. Accept one studio skill name. Locate its
live `.agents/skills/studio-<name>/SKILL.md`, workflow and linked resources through
`.agents/game-studio/catalog.json`. Do not change the immutable source snapshot.

1. Define the observed failure or requested improvement; run a baseline scenario
   and structural check, retaining evidence and a local snapshot of affected
   files. Use the relevant source quality rubric only when it adds a real check.
2. Change the smallest live entry/workflow/shared resource that addresses it.
   Update `tools/game-studio/runtime/` overlays or the converter as appropriate,
   so a future reviewed regeneration retains the correction. Shared changes
   require checking affected callers; do not broaden unrelated scope.
3. Repeat the same scenario and structural checks. Keep improvements supported
   by evidence; restore only your own test change from its local snapshot when
   it regresses behavior. No git reset, source catalog edits or stage commits.
4. Record the request, affected files, before/after evidence and limitations in
   `production/qa/skill-evaluations/` when a saved report is requested. Finish the
   project's checklist and Git approval protocol.

The archived upstream `skill-improve` workflow remains available as reference
for its score-comparison method, but its original tools, writable catalog and
frontmatter assumptions are not active.
