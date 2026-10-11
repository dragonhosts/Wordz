# Codex studio skill validation

Read `.agents/game-studio/CODEX.md` first. Accept `static [name|all]`,
`category [name]`, `spec [name]`, or `audit` as in the upstream workflow.

## Structural / audit

Run `python tools/game-studio/studio.py check --scope migration`. Discover live
skills at `.agents/skills/studio-*/SKILL.md`, and native agents in
`.codex/agents/studio-*.toml`; workflow bodies are separate references under
`.agents/game-studio/workflows/<name>/WORKFLOW.md` without frontmatter. Count and
cross-check `.agents/game-studio/catalog.json`; check the native adapter and
referenced dependencies. Source model/tool/frontmatter criteria do not apply.
Report structure and coverage separately from behavior. For named checks,
inspect that entry, role, workflow and its linked references.

## Behavioral / category

Read only the relevant specs/rubrics from
`.agents/game-studio/upstream/CCGS Skill Testing Framework/`. Treat their Claude
tool and directory assumptions through the adapter. Use realistic requests in
isolated permitted fixtures or read-only subagent evaluation; no game or paused
task mutation unless the user requested it. Record actual observations and
failures, not the intended outcome. Static success does not prove all behaviors.

Write requested evaluation records to `production/qa/skill-evaluations/`, not
the immutable upstream snapshot. Keep native coverage records separate from
the source catalog. Scope test cost deliberately; do not launch 74 agent runs
for an ordinary structural request.

The complete original assertions, category rubrics and reporting examples are
archived in `upstream/.claude/skills/skill-test/SKILL.md` relative to the shared
studio root; consult relevant sections only.
