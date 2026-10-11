"""Codex lifecycle adapter. No game writes, task resumption or transcript reads."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys
import uuid

import studio


def git_operations(command):
    """Recognize ordinary git invocations; this is a guardrail, not a shell parser."""
    operations = []
    for segment in re.split(r"[\r\n;&|]+", command):
        try:
            tokens = shlex.split(segment, posix=True)
        except ValueError:
            tokens = segment.split()
        for index, token in enumerate(tokens):
            executable = token.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if executable not in ("git", "git.exe"):
                continue
            cursor = index + 1
            while cursor < len(tokens):
                token = tokens[cursor]
                if token in ("-C", "-c", "--git-dir", "--work-tree", "--namespace"):
                    cursor += 2
                elif token.startswith("-"):
                    cursor += 1
                else:
                    operations.append(token.lower())
                    break
            break
    return operations


def audit(root, event):
    # Each event gets its own file: concurrent subagents never append to one log.
    folder = root / "production/session-logs"
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    label = hashlib.sha256(str(event.get("session_id", "unknown")).encode()).hexdigest()[:12]
    data = {"at_utc": now.isoformat(), "event": event.get("hook_event_name"), "session_hash": label}
    if event.get("agent_type"):
        data["agent_type"] = str(event["agent_type"])[:100]
    path = folder / (now.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex + ".json")
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


def deny(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}, 0


def handle(event, root=None):
    root = (root or studio.DEFAULT_ROOT).resolve()
    name = event.get("hook_event_name", "")
    if name in ("SessionStart", "PostCompact"):
        state = studio.task_status(root)
        paused = [t["id"] for t in state["tasks"] if t["status"] == "paused"]
        context = "Wordz Game Studio. Read AGENTS.md and .agents/game-studio/CODEX.md.\n" + state["checkpoint"]
        context += "\nPaused tasks (do not resume automatically): " + (", ".join(paused) or "none")
        return {"hookSpecificOutput": {"hookEventName": name, "additionalContext": context[:5000]}}, 0
    if name == "PreToolUse":
        data = event.get("tool_input", {})
        command = str(data.get("command", data.get("cmd", "")))
        operations = git_operations(command)
        if not set(operations) & {"commit", "push", "merge"}:
            return {}, 0
        unfinished = studio.unfinished_tasks(root)
        if unfinished:
            return deny("Project AGENTS.md forbids implementation-stage commit/push/merge. Unfinished tasks: " + ", ".join(unfinished))
        if "commit" in operations:
            result = studio.check_commit(root)
            if not result["ok"]:
                return deny("Pre-commit checks failed: " + json.dumps(result, ensure_ascii=False))
        # Human approval is enforced by instructions/host. Never return 'allow'.
        return {}, 0
    if name == "PostToolUse":
        data = event.get("tool_input", {})
        path = str(data.get("file_path", data.get("path", ""))).replace("\\", "/")
        patch = str(data.get("patch", data.get("input", "")))
        relevant = (path.endswith(".json") and "Assets/" in path) or ("Assets/" in patch and ".json" in patch)
        if relevant:
            result = studio.check_assets(root)
            if not result["ok"]:
                return {"systemMessage": "Asset JSON check failed: " + json.dumps(result, ensure_ascii=False)}, 0
        return {}, 0
    if name in ("PreCompact", "Stop", "SubagentStart", "SubagentStop", "Interrupt", "SessionEnd"):
        audit(root, event)
        return {}, 0
    return {}, 0


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise studio.StudioError("Hook input must be an object")
        output, code = handle(data)
    except (ValueError, OSError) as exc:
        # Surface hook failure rather than claiming a successful validation.
        output = {"systemMessage": "Game Studio hook NOT VERIFIED: " + str(exc)}
        code = 1
    if output:
        print(json.dumps(output, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
