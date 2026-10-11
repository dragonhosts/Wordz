"""Codex Game Studio: dependency-free configuration, observations and checks.

Configuration is JSON-shaped YAML intentionally: no shell injection or YAML parser
dependency. All paths are resolved against the project root, never a skill folder.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
TIERS = {
    "minimal": {"modes.workflow": "minimal", "docs.density": "terse", "qa.level": "minimal", "modes.story_granularity": "coarse", "modes.review_mode": "solo", "team.size": "individual"},
    "standard": {"modes.workflow": "standard", "docs.density": "balanced", "qa.level": "standard", "modes.story_granularity": "balanced", "modes.review_mode": "lean", "team.size": "individual"},
    "full": {"modes.workflow": "full", "docs.density": "thorough", "qa.level": "full", "modes.story_granularity": "fine", "modes.review_mode": "full", "team.size": "studio"},
}
ENUMS = {
    "modes.rigor": tuple(TIERS), "modes.workflow": tuple(TIERS),
    "modes.automation": ("collaborative", "guided", "autonomous"),
    "modes.review_mode": ("solo", "lean", "full"),
    "modes.story_granularity": ("coarse", "balanced", "fine"),
    "docs.density": ("terse", "balanced", "thorough"), "qa.level": tuple(TIERS),
    "team.size": ("individual", "small", "studio"),
    "project.stage": ("Concept", "Systems Design", "Technical Setup", "Pre-Production", "Production", "Polish", "Release"),
}
LOCAL_KEYS = {"modes.automation", "modes.review_mode", "modes.automation_always_ask", "team.size", "performance.enforce"} | {"testing.strict." + k for k in ("logic", "integration", "visual", "ui", "config")}
DEFAULTS = {"modes.rigor": "minimal", "modes.automation": "guided", "modes.automation_always_ask": ["scope_changes", "file_deletions", "schema_changes"], "project.stage": "Production"}
CONTAINER_KEYS = {"framework", "project", "engine", "paths", "specialists", "modes", "commands", "features", "workflow_overrides", "workflow_overrides.system_overrides", "testing", "testing.strict", "docs", "qa", "team", "performance", "naming"}


class StudioError(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise StudioError(f"Duplicate configuration key: {key}")
        result[key] = value
    return result


def read_json(path: Path, optional=False):
    if not path.exists():
        if optional:
            return {}
        raise StudioError(f"Required file absent: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise StudioError(f"Invalid JSON-shaped YAML/JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise StudioError(f"Expected an object at {path}")
    return value


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Same-directory replacement prevents an interrupted write truncating config.
    tmp = path.with_name(path.name + ".studio-tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def flatten(data, prefix=""):
    result = {}
    for key, value in data.items():
        if not isinstance(key, str) or "." in key:
            raise StudioError(f"Invalid configuration key: {key!r}")
        dotted = prefix + key
        if isinstance(value, dict):
            if dotted not in CONTAINER_KEYS:
                raise StudioError(f"Expected a scalar setting or known container: {dotted}")
            result.update(flatten(value, dotted + "."))
        else:
            result[dotted] = value
    return result


def locally_allowed(key):
    return key in LOCAL_KEYS or key.startswith("features.") or key in ("schema_version",) or key.startswith("framework.")


PATH_KEYS = {"engine.root"} | {"paths." + k for k in ("code_root", "test_root", "design_root", "plans_root", "specs_root", "evidence_root")}
STRING_KEYS = {"framework.version", "framework.adapter", "framework.last_upgraded", "project.name", "engine.name", "engine.version", "engine.render_pipeline", "engine.input"}


def validate_values(values, local=False, root=None):
    for key, value in values.items():
        known = key in ENUMS or key in LOCAL_KEYS or key in PATH_KEYS or key in STRING_KEYS or key == "schema_version" or key.startswith(("features.", "specialists.", "naming.", "workflow_overrides.system_overrides.")) or key in ("commands.smoke", "commands.test", "commands.run", "performance.frame_budget_ms", "performance.memory_mb")
        if not known:
            raise StudioError(f"Unknown setting: {key}")
        if local and not locally_allowed(key):
            raise StudioError(f"Not locally overridable: {key}; use project.yaml")
        if key in ENUMS and value not in ENUMS[key]:
            raise StudioError(f"Invalid {key}: {value!r}; expected {ENUMS[key]}")
        if key.startswith(("testing.strict.", "features.")) or key == "performance.enforce":
            if type(value) is not bool:
                raise StudioError(f"{key} must be a boolean")
        if key == "modes.automation_always_ask" and (not isinstance(value, list) or not all(isinstance(v, str) for v in value)):
            raise StudioError(f"{key} must be an array of strings")
        if key.startswith("workflow_overrides.system_overrides.") and value not in TIERS:
            raise StudioError(f"Invalid system workflow tier: {key}={value!r}")
        if key in PATH_KEYS or key in STRING_KEYS or key.startswith(("specialists.", "naming.")):
            if not isinstance(value, str) or not value.strip():
                raise StudioError(f"{key} must be a nonempty string")
        if key in PATH_KEYS and root is not None:
            safe_path(root, value)
        if key == "schema_version" and (type(value) is not int or value != 1):
            raise StudioError("schema_version must be 1")
        if key.startswith("commands.") and value is not None and not isinstance(value, str):
            raise StudioError(f"{key} must be a string or null")
        if key in ("performance.frame_budget_ms", "performance.memory_mb") and (type(value) not in (int, float) or value <= 0):
            raise StudioError(f"{key} must be a positive number")


def resolve_config(root: Path, system=None):
    base = flatten(read_json(root / "project.yaml", optional=True))
    local_path = root / "project.local.yaml"
    if local_path.exists() and not (root / "project.yaml").exists():
        raise StudioError("project.local.yaml requires project.yaml")
    local = flatten(read_json(local_path, optional=True))
    validate_values(base, root=root)
    validate_values(local, local=True, root=root)
    effective = {k: {"value": v, "source": "default"} for k, v in DEFAULTS.items()}
    merged = {**base, **local}
    rigor = merged.get("modes.rigor", DEFAULTS["modes.rigor"])
    for key, value in TIERS[rigor].items():
        effective[key] = {"value": value, "source": "rigor:" + rigor}
    for key, value in base.items():
        effective[key] = {"value": value, "source": "project.yaml"}
    for key, value in local.items():
        effective[key] = {"value": value, "source": "project.local.yaml"}
    for key in ("logic", "integration", "visual", "ui", "config"):
        effective.setdefault("testing.strict." + key, {"value": None, "source": "unset; apply story requirements"})
    if system:
        key = "workflow_overrides.system_overrides." + system
        if key in merged:
            effective["modes.workflow"] = {"value": merged[key], "source": key}
    return {"root": str(root), "effective": effective, "notes": [] if base else ["project.yaml absent/empty; defaults used"]}


def set_config(root, operand, local=False, dry_run=False):
    key, sep, raw = operand.partition("=")
    if not sep or not key or not raw or any(not part for part in key.split(".")):
        raise StudioError("Expected nonempty key=value")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = raw
    candidate = {key: value}
    validate_values(candidate, local=local, root=root)
    base_path = root / "project.yaml"
    if local and not base_path.exists():
        raise StudioError("project.local.yaml requires project.yaml")
    path = root / ("project.local.yaml" if local else "project.yaml")
    data = deepcopy(read_json(path, optional=True))
    node = data
    parts = key.split(".")
    for part in parts[:-1]:
        child = node.setdefault(part, {})
        if not isinstance(child, dict):
            raise StudioError(f"Cannot descend into scalar: {part}")
        node = child
    node[parts[-1]] = value
    validate_values(flatten(data), local=local, root=root)
    if not dry_run:
        write_json(path, data)
    return {"file": path.name, "key": key, "value": value, "dry_run": dry_run}


def safe_path(root: Path, relative: str):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise StudioError(f"Path escapes project: {relative}")
    return path


def tasks(root):
    result = read_json(root / "production/tasks.json", optional=True).get("tasks", [])
    if not isinstance(result, list):
        raise StudioError("tasks must be an array")
    for task in result:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str):
            raise StudioError("Each task requires an id")
        if task.get("status") not in ("ready", "in_progress", "paused", "complete", "blocked"):
            raise StudioError(f"Invalid task status: {task}")
        for key in ("plan", "checkpoint"):
            if task.get(key):
                safe_path(root, task[key])
        related = task.get("related_paths", [])
        if not isinstance(related, list) or not all(isinstance(p, str) and p for p in related):
            raise StudioError("related_paths must be an array of nonempty paths")
        for path in related:
            safe_path(root, path)
    return result


def checkpoint(root):
    path = root / "production/session-state/active.md"
    if not path.exists():
        return "No checkpoint. Inspect the existing task plans; do not assume greenfield."
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(r"<!-- CHECKPOINT -->\s*(.*?)\s*<!-- /CHECKPOINT -->", text, re.S)
    return "\n".join((match[1] if match else text).splitlines()[:25])[:4000]


def task_status(root):
    config = resolve_config(root)
    rows = []
    for task in tasks(root):
        row = dict(task)
        plan = safe_path(root, task.get("plan", ""))
        if plan.is_file():
            text = plan.read_text(encoding="utf-8-sig")
            marks = re.findall(r"^- \[([ xX])\] Task \d+", text, re.M)
            if marks:
                row["checklist"] = {"done": sum(m.lower() == "x" for m in marks), "total": len(marks)}
        rows.append(row)
    return {
        "stage": config["effective"]["project.stage"]["value"], "checkpoint": checkpoint(root),
        "tasks": rows, "next_action": next((t["plan"] for t in rows if t["status"] in ("in_progress", "ready")), "No runnable task; ask for the next objective. Paused tasks require explicit user resumption."),
        "design_sources": [p for p in ("DesignDoc/GameBrief.md", "DesignDoc/UnityProjectContext.md", "DesignDoc/GameFrameworkDependency.md") if (root / p).exists()],
    }


def workflow(root, name, story=None):
    name = name.removeprefix("studio-")
    catalog = read_json(root / ".agents/game-studio/catalog.json")
    item = next((s for s in catalog["skills"] if s["name"] == "studio-" + name), None)
    if not item:
        raise StudioError(f"Unknown workflow: {name}")
    config = resolve_config(root)["effective"]
    result = {"skill": item["name"], "reference": item["workflow"], "mode": config["modes.automation"]["value"], "constraints": ["Preserve existing Unity/GameFramework architecture", "No implementation-stage Git mutations", "Paused inventory requires explicit user resume", "Actual editor/build/test evidence is required; do not fabricate"]}
    if name in ("start", "help", "adopt", "project-stage-detect", "sprint-status"):
        result["project"] = task_status(root)
        result["route"] = "Existing project: read authoritative DesignDoc and plan; do not re-onboard or reset config/stage."
    elif name == "settings":
        result["route"] = "Use config, get and set commands; project.yaml is JSON-shaped YAML. Explicit requested setting changes are authorized; show effective value and source."
    elif name == "setup-engine":
        result["route"] = "Engine is already pinned in the nested Unity project; do not change packages, input or rendering without a specific request. Inspect ProjectVersion.txt."
    elif name in ("dev-story", "story-readiness", "story-done"):
        if story:
            story_path = safe_path(root, story)
            for task in tasks(root):
                protected = [task[k] for k in ("plan", "checkpoint") if task.get(k)] + task.get("related_paths", [])
                if task["status"] == "paused" and any(story_path.is_relative_to(safe_path(root, p)) for p in protected):
                    raise StudioError(f"Paused task: {task['id']}; explicit user resumption required")
            if not story_path.is_file():
                raise StudioError(f"Story/plan absent: {story}")
        result["route"] = "Use the approved Superpowers plan as story input when no production/epics story exists. Its tests and checklist govern even at minimal. Never create a duplicate plan. Run check --scope assets and required engine checks, retain screenshots for visible changes."
    elif name.startswith("team-"):
        result["route"] = "Declare active roles and scoped files; use available Codex subagents only for independent work. Read role references explicitly. Team task state is file-backed; no assumption of Claude Agent Teams API. Obey runtime concurrency and avoid overlapping writers."
    elif name in ("skill-test", "skill-improve"):
        result["route"] = "Use check --scope migration for structural checks; use the upstream testing framework only as behavioral scenarios/rubrics. A static check is not behavior evidence."
    elif name in ("gate-check", "release-checklist", "launch-checklist", "team-release", "hotfix", "day-one-patch"):
        result["route"] = "Prepare checks and reviewable changes only. Publishing, Git mutations and release approval remain separate human actions. Phase navigation must not resume paused tasks."
    else:
        result["route"] = "Apply relevant workflow phases using project paths and native tools; use shared CODEX adapter for helper mappings and existing-document precedence."
    return result


def check_baseline(root):
    original = read_json(root / "production/migration/baseline.json")
    changed = []
    for name, expected in original.items():
        if name in ("AGENTS.md", "README.md", ".gitignore"):
            continue
        path = safe_path(root, name)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            changed.append(name)
    return {"protected_files": sum(n not in ("AGENTS.md", "README.md", ".gitignore") for n in original), "changed": changed, "ok": not changed}


def check_migration(root):
    catalog = read_json(root / ".agents/game-studio/catalog.json")
    source = read_json(root / ".agents/game-studio/source.json")
    errors = []
    for kind in ("skills", "agents"):
        if len(catalog[kind]) != source["counts"][kind]:
            errors.append(f"{kind} count mismatch")
        if len({s["name"] for s in catalog[kind]}) != len(catalog[kind]):
            errors.append(f"Duplicate {kind} names")
    for entry in catalog["skills"]:
        for key in ("entry", "workflow"):
            if not safe_path(root, entry[key]).is_file():
                errors.append(f"Missing {entry[key]}")
        text = safe_path(root, entry["entry"]).read_text(encoding="utf-8")
        if not re.search(r"^name: " + re.escape(entry["name"]) + "$", text, re.M):
            errors.append(f"Skill name mismatch: {entry['name']}")
        if re.search(r"^!`|CLAUDE_SKILL_DIR|^model:|^allowed-tools:", text, re.M):
            errors.append(f"Claude runtime declaration in {entry['entry']}")
        body = safe_path(root, entry["workflow"]).read_text(encoding="utf-8")
        if re.search(r"^!`", body, re.M):
            errors.append(f"Unconverted preprocessing: {entry['workflow']}")
        if re.search(r"\w\$studio-[\w-]+\.(yaml|md|json)", body):
            errors.append(f"Command conversion corrupted a file path: {entry['workflow']}")
        if re.search(r"\.agents/game-studio/workflows/[^\s`]+/SKILL\.md", body):
            errors.append(f"Old skill filename in workflow reference: {entry['workflow']}")
    for entry in catalog["agents"]:
        path = safe_path(root, entry["config"])
        try:
            agent = tomllib.loads(path.read_text(encoding="utf-8"))
            for field in ("name", "description", "developer_instructions"):
                if not agent.get(field):
                    errors.append(f"Missing {field}: {path.name}")
            if agent.get("name") != entry["name"] or agent.get("model") in ("opus", "sonnet", "haiku"):
                errors.append(f"Invalid agent: {path.name}")
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(str(exc))
        if not safe_path(root, entry["role"]).is_file():
            errors.append(f"Missing role: {entry['role']}")
    for name, expected in source["files"].items():
        path = safe_path(root, ".agents/game-studio/upstream/" + name)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"Upstream provenance mismatch: {name}")
    for name in (".agents/game-studio/CODEX.md", ".agents/game-studio/HELPERS.md", "production/session-state/active.md", ".codex/hooks.json", "tools/game-studio/hook.py"):
        if not (root / name).is_file():
            errors.append(f"Missing runtime dependency: {name}")
    hooks = read_json(root / ".codex/hooks.json")
    for event, groups in hooks.get("hooks", {}).items():
        for group in groups:
            for handler in group.get("hooks", []):
                if handler.get("type") != "command" or "hook.py" not in handler.get("command", "") or "hook.py" not in handler.get("commandWindows", ""):
                    errors.append(f"Invalid native Hook handler: {event}")
    resolve_config(root)
    tasks(root)
    return {"skills": len(catalog["skills"]), "agents": len(catalog["agents"]), "upstream_files": len(source["files"]), "errors": errors, "ok": not errors}


def check_assets(root, staged=False):
    if staged:
        names = subprocess.check_output(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], cwd=root).decode("utf-8").split("\0")
    else:
        folder = root / "Wordz-unity/Assets/Wordz"
        names = [p.relative_to(root).as_posix() for p in folder.rglob("*.json")] if folder.exists() else []
    errors, checked = [], 0
    for name in names:
        if not name.endswith(".json") or not name.startswith("Wordz-unity/Assets/"):
            continue
        checked += 1
        try:
            data = subprocess.check_output(["git", "show", ":" + name], cwd=root) if staged else safe_path(root, name).read_bytes()
            json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique_object)
        except (UnicodeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
            errors.append(f"{name}: {exc}")
    return {"checked_json": checked, "staged": staged, "errors": errors, "ok": not errors}


def validate_commit_message(message):
    title, sep, detail = message.strip().partition("\n\n")
    if not re.fullmatch(r"[a-z]+：[\u3400-\u9fff][^\n]*", title) or re.search(r"[A-Za-z]", title.split("：", 1)[-1]):
        raise StudioError("Commit title must use an English word prefix, full-width colon and Chinese title")
    if not sep or not re.search(r"[\u3400-\u9fff]", detail):
        raise StudioError("Commit message requires a blank line and Chinese detail")
    return True


def unfinished_tasks(root):
    unfinished = []
    for task in tasks(root):
        if task["status"] in ("in_progress", "ready", "blocked"):
            unfinished.append(task["id"])
        elif task["status"] == "complete" and task.get("plan"):
            text = safe_path(root, task["plan"]).read_text(encoding="utf-8-sig")
            if re.search(r"^- \[ \] Task \d+", text, re.M):
                unfinished.append(task["id"])
    return unfinished


def check_commit(root, message=None):
    unfinished = unfinished_tasks(root)
    result = check_assets(root, staged=True)
    result["unfinished_tasks"] = unfinished
    result["ok"] = result["ok"] and not unfinished
    if message is not None:
        validate_commit_message(message)
        result["message_valid"] = True
    result["approval"] = "Human approval is required even when checks pass; this tool does not grant it."
    return result


def inspect(root, kind, path=None):
    if kind == "changes":
        unstaged = subprocess.check_output(["git", "diff", "--name-only", "-z"], cwd=root).decode("utf-8").split("\0")
        staged = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"], cwd=root).decode("utf-8").split("\0")
        return {"unstaged": [p for p in unstaged if p], "staged": [p for p in staged if p], "observation_only": True}
    if not path:
        raise StudioError("inspect gdd/adrs requires a project-relative path")
    target = safe_path(root, path)
    if kind == "gdd":
        text = target.read_text(encoding="utf-8-sig")
        sections = re.findall(r"^##\s+(.+)$", text, re.M)
        return {"path": path, "sections": sections, "observation_only": True}
    if not target.is_dir():
        raise StudioError(f"ADR directory absent: {path}")
    rows = []
    for file in sorted(target.glob("adr-*.md")):
        text = file.read_text(encoding="utf-8-sig")
        rows.append({"file": file.relative_to(root).as_posix(), "references": sorted(set(re.findall(r"adr-[\w-]+\.md", text)))})
    return {"adrs": rows, "observation_only": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("config"); p.add_argument("--system")
    p = sub.add_parser("get"); p.add_argument("key")
    p = sub.add_parser("set"); p.add_argument("operand"); p.add_argument("--local", action="store_true"); p.add_argument("--dry-run", action="store_true")
    sub.add_parser("status")
    p = sub.add_parser("workflow"); p.add_argument("name"); p.add_argument("story", nargs="?")
    p = sub.add_parser("inspect"); p.add_argument("kind", choices=("gdd", "adrs", "changes")); p.add_argument("path", nargs="?")
    p = sub.add_parser("check"); p.add_argument("--scope", choices=("migration", "baseline", "assets", "commit", "all"), default="migration"); p.add_argument("--message-file", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "config": result = resolve_config(root, args.system)
        elif args.command == "get":
            cfg = resolve_config(root)["effective"]
            if args.key not in cfg: raise StudioError(f"Unknown/unset setting: {args.key}")
            result = {args.key: cfg[args.key]}
        elif args.command == "set": result = set_config(root, args.operand, args.local, args.dry_run)
        elif args.command == "status": result = task_status(root)
        elif args.command == "workflow": result = workflow(root, args.name, args.story)
        elif args.command == "inspect": result = inspect(root, args.kind, args.path)
        else:
            checks = {"migration": check_migration, "baseline": check_baseline, "assets": check_assets, "commit": check_commit}
            if args.scope == "all":
                result = {k: checks[k](root) for k in ("migration", "baseline", "assets")}
                result["ok"] = all(v["ok"] for v in result.values())
            elif args.scope == "commit": result = check_commit(root, args.message_file.read_text(encoding="utf-8-sig") if args.message_file else None)
            else: result = checks[args.scope](root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok", True) else 1
    except (StudioError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
