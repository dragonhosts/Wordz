"""Install reviewed native overlays without replacing existing project settings."""
import json
from pathlib import Path
import shutil
from import_upstream import regenerate_references

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).parent / "runtime"
TARGET = ROOT / ".agents/game-studio"
regenerate_references(ROOT)
for name in ("CODEX.md", "HELPERS.md"):
    shutil.copyfile(SOURCE / name, TARGET / name)

# Native documents take precedence over upstream configuration/runtime guides.
overlays = {
    "config-resolution.md": "# Native configuration\n\nRead ../CODEX.md and ../HELPERS.md. Run `python tools/game-studio/studio.py config`. The native adapter uses JSON-shaped YAML, strict errors and whitelisted personal overrides; no injected shell, legacy mirrors or source defaults. Full original spec is archived under ../upstream/.claude/docs/config-resolution.md.\n",
    "code-root-resolution.md": "# Project code roots\n\nRead project.yaml through the native config command. Unity root: Wordz-unity; code: Wordz-unity/Assets/Wordz; tests: Wordz-unity/Assets/Wordz/Tests. Existing DesignDoc and Superpowers specs/plans remain authoritative. Root Assets/src is not this project's code root.\n",
    "technical-preferences.md": "# Wordz technical preferences\n\nUnity 2022.3.56f1c1, Built-in Render Pipeline, Legacy Input Manager and GameFramework. Read DesignDoc/UnityProjectContext.md and GameFrameworkDependency.md. Do not automatically install packages, replace rendering/input, move gameplay state into scene/UI scripts, or modify third-party assets.\n",
    "model-tiers.md": "# Native model policy\n\nInherit the actual Codex session model/effort unless the user or a valid custom-agent setting explicitly selects another. Opus/Sonnet/Haiku pins from the original framework are provenance only; no model is hardcoded by this adapter. Role tier is seniority, not a model/cost guarantee.\n",
    "agent-teams.md": "# Codex collaboration\n\nUse native subagent spawn/message/followup/wait tools with scoped file-backed task lists. Read ../CODEX.md. No dependency on Claude Agent Teams independent-session/shared-task APIs. Native custom roles may be loaded by host configuration or explicitly supplied to subagent prompts.\n",
    "automation-modes.md": "# Native automation\n\nRead ../CODEX.md. Guided mode continues approved reversible work, asks for missing consequential decisions and respects root AGENTS commit gates. Collaborative/autonomous modes adjust interaction frequency but do not override user authorization, paused tasks, host permissions or explicit publication approval. No repeated write approvals inside approved scope.\n",
    "directory-structure.md": "# Existing project layout\n\nRead ../CODEX.md and project.yaml. Authoritative design: DesignDoc/. Specs/plans: docs/superpowers/. Unity: Wordz-unity/. Runtime/test code: Assets/Wordz under that project. Studio task state: production/. New template artifacts may use design/ or docs/architecture/ only when requested and not duplicates.\n",
    "coordination-rules.md": "# Native coordination\n\nRead ../CODEX.md Roles and collaboration. Parent agent controls scope and decisions, domain experts work within delegated files, peers consult via messages, cross-domain conflicts escalate. Collect independent results before dependent work. Native tool grants do not follow original Claude Markdown frontmatter.\n",
}
for name, body in overlays.items():
    (TARGET / "docs" / name).write_text(body, encoding="utf-8")

# Discovery and skill-authoring inspect actual Codex skills, not reference bodies.
help_path = TARGET / "workflows/help/WORKFLOW.md"
help_path.write_text(help_path.read_text(encoding="utf-8").replace(".agents/game-studio/workflows/*/WORKFLOW.md", ".agents/skills/studio-*/SKILL.md"), encoding="utf-8")
for name in ("help", "skill-test", "skill-improve"):
    path = TARGET / "workflows" / name / "WORKFLOW.md"
    path.write_text((SOURCE / (name + ".md")).read_text(encoding="utf-8"), encoding="utf-8")

command = "python3 \"$(git rev-parse --show-toplevel)/tools/game-studio/hook.py\""
windows = "powershell -NoProfile -NonInteractive -Command \"$studioRoot = git rev-parse --show-toplevel; if ($LASTEXITCODE -ne 0) { exit 1 }; python (Join-Path $studioRoot 'tools/game-studio/hook.py')\""
events = {}
for event in ("SessionStart", "PreToolUse", "PostToolUse", "PreCompact", "PostCompact", "Stop", "SubagentStart", "SubagentStop", "Interrupt", "SessionEnd"):
    handler = {"type": "command", "command": command, "commandWindows": windows, "timeout": 3 if event in ("Interrupt", "SessionEnd") else 10}
    if event in ("SessionStart", "PostCompact"):
        handler["additionalContextLimit"] = 1500
    group = {"hooks": [handler]}
    if event == "PreToolUse": group["matcher"] = "Bash|exec_command|PowerShell"
    if event == "PostToolUse": group["matcher"] = "apply_patch|Edit|Write"
    events[event] = [group]
hooks = ROOT / ".codex/hooks.json"
hooks.parent.mkdir(parents=True, exist_ok=True)
if hooks.exists():
    existing = json.loads(hooks.read_text(encoding="utf-8-sig"))
    if existing.get("description") != "Wordz Game Studio native hooks; review/trust required":
        raise SystemExit("Existing hooks require a reviewed merge; not overwritten")
hooks.write_text(json.dumps({"description": "Wordz Game Studio native hooks; review/trust required", "hooks": events}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
config = ROOT / ".codex/config.toml"
if not config.exists():
    config.write_text("# Studio roles inherit the parent model and runtime permissions.\n[agents]\nenabled = true\n", encoding="utf-8")
print("Installed shared runtime, eight native guides, lifecycle hooks and project agent configuration")
