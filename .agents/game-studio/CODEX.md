# Codex Game Studio adapter — Wordz

This is the runtime adaptation policy for the migrated CCGS workflows and roles.
Read root `AGENTS.md` first. Source material under `upstream/` is an immutable
reference snapshot, not active Claude configuration. Migrated workflow bodies
retain domain detail; the rules here replace their source-host assumptions.

## Project and authority

- Root means the Git repository, not the Unity project or the skill directory.
  Resolve it before shell calls. `studio.py` locates its own repository root even
  when launched from `Wordz-unity/`; `--root` is for isolated fixtures.
- Run `python tools/game-studio/studio.py config` and `status`. JSON-shaped YAML
  is the supported `project.yaml`/`project.local.yaml` format; use the native `set`
  command rather than a source YAML helper. No automatic shell interpolation.
- Existing `DesignDoc/UnityProjectContext.md`, `GameFrameworkDependency.md`,
  game design, and approved `docs/superpowers/{specs,plans}/` are authoritative.
  Recognize these when workflows expect `design/gdd`, `production/epics`, ADRs
  or stories. An approved plan is a valid story input. Read requested sections,
  not every design file. New studio work may use `production/` and the templates.
- Unity root is `Wordz-unity/`; code/test roots come from config. Do not
  scan root `Assets/` and conclude no code exists. Third-party code is not owned
  by studio programmers.
- Preserve Unity 2022.3.56f1c1, Built-in, Legacy Input Manager and GameFramework.
  Source-role preferences for SRP, new Input System, Addressables, DOTS or UI
  Toolkit are proposals only; they do not authorize changing the existing stack.
  Source engine-reference versions are historical and not this project's pin.
  Inspect ProjectVersion.txt, existing code/packages and applicable Unity skills
  before API work; verify version-specific APIs against official sources.
- `commands.smoke/test/run` are deliberately unset. Use existing Unity
  Workbench/Unity connection tools when available, or discover the editor and
  configure commands for the actual environment. Never treat an unset command,
  parse-only success or historical test result as current validation.

## Workflow execution and consent

- Original `/name` commands are `$studio-name` skills or equivalent natural
  language requests. Read the short skill then its relevant `WORKFLOW.md`.
  `WORKFLOW.md` is an on-demand instruction reference, not a discoverable skill.
- Guided is the default. Continue ordinary reversible edits inside approved
  scope. Source "May I write" and phase approvals do not require re-approval of
  work the user already requested. Ask for material missing decisions, scope
  changes, deletions or schema changes when not already authorized. Sandbox,
  network and Hook trust approvals are still controlled by the host.
- Rigor controls new process artifacts and review depth. It does not waive an
  existing approved plan's tests, checklists or build requirements. Explicit
  testing.strict values apply to new stories. Visible changes still need a real
  run, retained screenshot, and separate feel/playtest evidence when applicable.
- Root AGENTS rules override source steps about Git/release operations. No
  commit, push, merge or PR during multi-task implementation. Finish and verify
  the whole checklist, show evidence, then ask whether to commit. Release
  workflows prepare reviewable results; they do not authorize publication.
  Commit messages use the existing English prefix, full-width colon, Chinese
  title, blank line and Chinese detail format.
- `production/tasks.json` is the task lifecycle registry; plan checkboxes are
  the sole implementation-progress ledger. Do not invent a second progress list.
  Checkpoints reference that ledger. Paused tasks are excluded from navigation
  and automatic implementation, including old active stories and unfinished
  code. Only explicit user resumption permits changing paused to in_progress.
  New projects have no inherited paused tasks; consult their own task registry.

## Native tool adaptation

Use the actual available tool schemas, not literal names from the source body.

| Source concept | Codex execution |
| --- | --- |
| Read / Glob / Grep | Native file tools or PowerShell, `rg`/`rg --files`; images via view_image |
| Write / Edit | apply_patch or available file tools, inside authorized scope |
| Bash / PowerShell | exec_command with this session's shell; rewrite shell syntax appropriately |
| AskUserQuestion | request_user_input_async for meaningful missing preferences; normal text if unavailable |
| Agent / Task delegation | Available collaboration spawn/message/followup/wait tools; never shell-spawn Codex as a substitute |
| TaskCreate/Get/List/Update | File-backed scoped tasks/checklist; no nonexistent task API calls |
| Skill tool / slash command | Read/invoke the installed studio skill using the current host mechanism |
| WebSearch / WebFetch | Available web tools, citing sources; official docs for technical APIs |
| Claude model/frontmatter settings | Removed from active entries; inherit actual session settings unless explicitly configured |
| yaml-helper and deterministic helpers | Native commands in HELPERS.md; do not execute original helper scripts |

## Roles and collaboration

Role definitions live in `roles/<name>.md`; native custom agent declarations are
`.codex/agents/studio-<name>.toml`. Native loading depends on the host version and
project trust. If the current spawn tool has no named-role argument, read the
role first and put its responsibilities, delegated scope, input paths, expected
evidence, and this adapter in the subagent prompt. Do not pretend Markdown tool
grants enforce permissions: they are delegation boundaries, while the host
sandbox is the security boundary. Source maxTurns is not a Codex tool argument.

Studio team workflows request delegation when independent work benefits from it.
Respect actual concurrency (this migration session: four active agents including
the parent), and do not hardcode it in future sessions. Core roles execute in
individual mode; widen deliberately for cross-domain work. Keep one writer per
file set, gather prerequisites before dependent work, use message/followup for
corrections, and surface partial or blocked results. Same-tier agents may consult
each other; cross-domain decisions escalate to the parent. No assumption of
Claude Agent Teams shared-task APIs or permanently running teammates.

Reuse installed Superpowers for design/plans/implementation/review and Unity
Workbench for editor integration and validation. Do not duplicate those systems
or import source habits that conflict with user authorization.

## Context and verification

Read `production/session-state/active.md` after interruption/compaction. Keep its
CHECKPOINT under 25 lines, overwrite the summary, and store longer evidence in
`production/migration/` or `production/qa/evidence/`. Subagents return summaries
and exact evidence, not their entire context. No automatic resume of paused work.

Run `python tools/game-studio/studio.py check --scope all` for the studio itself.
This checks migration structure, provenance, protected baseline and JSON data;
it does not build the game or prove all workflow behavior. Native Hooks require
host review/trust and a new/resumed session; until confirmed, call checks
explicitly. No Hook or role bypasses permissions or independently approves Git.
