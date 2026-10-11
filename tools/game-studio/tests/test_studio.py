import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import studio
import import_upstream


class ConverterTests(unittest.TestCase):
    def test_command_conversion_preserves_file_paths(self):
        text = "Run /sprint-status and `/help`; read production/sprint-status.yaml, .claude/skills/help/SKILL.md and /help.md."
        result = import_upstream.adapt_source(text, ["sprint-status", "help"])
        self.assertIn("$studio-sprint-status", result)
        self.assertIn("production/sprint-status.yaml", result)
        self.assertIn("/help.md", result)
        self.assertIn(".agents/game-studio/workflows/help/WORKFLOW.md", result)
        self.assertNotIn("production$studio-", result)

    def test_preprocessing_is_removed_and_rubric_path_is_archived(self):
        result = import_upstream.adapt_source('!`bash "${CLAUDE_SKILL_DIR}/helper.sh"`\nRead CCGS Skill Testing Framework/catalog.yaml', [])
        self.assertNotIn("!`", result)
        self.assertNotIn("CLAUDE_SKILL_DIR", result)
        self.assertIn(".agents/game-studio/upstream/CCGS Skill Testing Framework/catalog.yaml", result)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        studio.write_json(self.root / "project.yaml", {"modes": {"rigor": "standard", "automation": "guided"}, "project": {"stage": "Production"}})

    def tearDown(self):
        self.tmp.cleanup()


class ConfigTests(Fixture):
    def test_rigor_and_explicit_override_do_not_pin_siblings(self):
        studio.set_config(self.root, "docs.density=terse")
        studio.set_config(self.root, "modes.rigor=full")
        cfg = studio.resolve_config(self.root)["effective"]
        self.assertEqual(cfg["docs.density"]["value"], "terse")
        self.assertEqual(cfg["qa.level"]["value"], "full")
        self.assertEqual(cfg["modes.review_mode"]["source"], "rigor:full")

    def test_local_leaf_override_preserves_project_and_siblings(self):
        studio.set_config(self.root, "modes.review_mode=solo", local=True)
        cfg = studio.resolve_config(self.root)["effective"]
        self.assertEqual(cfg["modes.review_mode"]["source"], "project.local.yaml")
        self.assertEqual(cfg["modes.workflow"]["value"], "standard")
        self.assertEqual(cfg["modes.automation"]["value"], "guided")

    def test_shared_settings_cannot_be_personal(self):
        for key in ("engine.name", "modes.rigor", "paths.code_root"):
            with self.subTest(key=key), self.assertRaises(studio.StudioError):
                studio.set_config(self.root, key + "=Unity", local=True)
        studio.write_json(self.root / "project.local.yaml", {"modes": {"rigor": "full"}})
        with self.assertRaises(studio.StudioError):
            studio.resolve_config(self.root)

    def test_invalid_empty_duplicate_and_wrong_shape_fail(self):
        for text in ('', '{"modes":{"rigor":"minimal","rigor":"full"}}', '{"modes":{"rigor":["full"]}}', 'modes:\n  rigor: full', '{"testing":{"strict":{"logic":"false"}}}'):
            with self.subTest(text=text):
                (self.root / "project.yaml").write_text(text, encoding="utf-8")
                with self.assertRaises(studio.StudioError):
                    studio.resolve_config(self.root)

    def test_orphan_local_fails_and_missing_base_reports_defaults(self):
        (self.root / "project.yaml").unlink()
        cfg = studio.resolve_config(self.root)
        self.assertEqual(cfg["effective"]["qa.level"]["value"], "minimal")
        self.assertTrue(cfg["notes"])
        studio.write_json(self.root / "project.local.yaml", {"team": {"size": "small"}})
        with self.assertRaises(studio.StudioError): studio.resolve_config(self.root)

    def test_system_override_and_dry_run(self):
        studio.set_config(self.root, "workflow_overrides.system_overrides.combat=full")
        self.assertEqual(studio.resolve_config(self.root, "combat")["effective"]["modes.workflow"]["value"], "full")
        before = (self.root / "project.yaml").read_bytes()
        studio.set_config(self.root, "modes.rigor=minimal", dry_run=True)
        self.assertEqual(before, (self.root / "project.yaml").read_bytes())

    def test_empty_unknown_and_escape_operands_rejected(self):
        for arg in ("=full", "modes.rigor=", "modes..rigor=full", "madeup.setting=x", "paths.code_root=../escape"):
            with self.subTest(arg=arg), self.assertRaises(studio.StudioError):
                studio.set_config(self.root, arg)
        with self.assertRaises(studio.StudioError): studio.safe_path(self.root, "../escape")

    def test_bom_crlf_and_literal_shell_text_are_data(self):
        studio.write_json(self.root / "project.yaml", {"modes": {"rigor": "minimal"}, "commands": {"run": "$(Get-Content secret)"}})
        text = (self.root / "project.yaml").read_text(encoding="utf-8")
        (self.root / "project.yaml").write_bytes(b'\xef\xbb\xbf' + text.replace("\n", "\r\n").encode())
        self.assertEqual(studio.resolve_config(self.root)["effective"]["commands.run"]["value"], "$(Get-Content secret)")

    def test_path_schema_applies_to_set_and_direct_config_reads(self):
        for key, value in (("paths.code_root", True), ("engine.root", "../outside"), ("paths.code_root", "../outside"), ("madeup.setting", "value")):
            with self.subTest(key=key, value=value):
                with self.assertRaises(studio.StudioError):
                    studio.set_config(self.root, key + "=" + json.dumps(value), dry_run=True)
                data = {}
                head, tail = key.split(".", 1)
                data[head] = {tail: value}
                studio.write_json(self.root / "project.yaml", data)
                with self.assertRaises(studio.StudioError): studio.resolve_config(self.root)
                studio.write_json(self.root / "project.yaml", {"modes": {"rigor": "standard"}})

    def test_wrong_config_container_cannot_silently_fall_back(self):
        for data in ({"modes": "full"}, {"engine": []}, {"paths": True}, {"modes": {"rigor": {}}}, {"paths": {"code_root": {}}}, {"madeup": {}}):
            studio.write_json(self.root / "project.yaml", data)
            with self.assertRaises(studio.StudioError): studio.resolve_config(self.root)


class NavigationTests(Fixture):
    def test_paused_task_is_not_next_and_cannot_be_implemented(self):
        studio.write_json(self.root / "production/tasks.json", {"tasks": [{"id": "inventory", "status": "paused", "plan": "old.md"}]})
        (self.root / "old.md").write_text("approved inventory", encoding="utf-8")
        studio.write_json(self.root / ".agents/game-studio/catalog.json", {"skills": [{"name": "studio-dev-story", "workflow": "flow.md"}]})
        self.assertIn("No runnable task", studio.task_status(self.root)["next_action"])
        with self.assertRaisesRegex(studio.StudioError, "Paused task"):
            studio.workflow(self.root, "dev-story", "old.md")

    def test_checkpoint_is_bounded_and_does_not_include_narrative(self):
        path = self.root / "production/session-state/active.md"
        path.parent.mkdir(parents=True)
        path.write_text("<!-- CHECKPOINT -->\n" + "\n".join(str(n) for n in range(50)) + "\n<!-- /CHECKPOINT -->\nSECRET_NARRATIVE", encoding="utf-8")
        output = studio.checkpoint(self.root)
        self.assertEqual(len(output.splitlines()), 25)
        self.assertNotIn("SECRET_NARRATIVE", output)

    def test_paused_spec_ledger_and_owned_directory_are_protected(self):
        studio.write_json(self.root / "production/tasks.json", {"tasks": [{"id": "inventory", "status": "paused", "plan": "plan.md", "related_paths": ["spec.md", "ledger.md", "Inventory"]}]})
        studio.write_json(self.root / ".agents/game-studio/catalog.json", {"skills": [{"name": "studio-dev-story", "workflow": "flow.md"}]})
        (self.root / "Inventory").mkdir()
        for name in ("plan.md", "spec.md", "ledger.md", "Inventory/story.md"):
            (self.root / name).write_text("inventory", encoding="utf-8")
            with self.subTest(name=name), self.assertRaisesRegex(studio.StudioError, "Paused task"):
                studio.workflow(self.root, "dev-story", name)

    def test_nested_cli_uses_explicit_project_root(self):
        nested = self.root / "unity/Assets"
        nested.mkdir(parents=True)
        run = subprocess.run([sys.executable, str(TOOLS / "studio.py"), "--root", str(self.root), "config"], cwd=nested, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["root"], str(self.root))

    def test_checklist_progress_is_read_from_plan(self):
        (self.root / "plan.md").write_text("- [x] Task 1：done\n- [ ] Task 2：next\n", encoding="utf-8")
        studio.write_json(self.root / "production/tasks.json", {"tasks": [{"id": "work", "status": "in_progress", "plan": "plan.md"}]})
        self.assertEqual(studio.task_status(self.root)["tasks"][0]["checklist"], {"done": 1, "total": 2})


class CheckTests(Fixture):
    def test_baseline_detects_modified_or_missing_protected_file(self):
        import hashlib
        (self.root / "game.cs").write_bytes(b"original")
        data = {"game.cs": hashlib.sha256(b"original").hexdigest()}
        studio.write_json(self.root / "production/migration/baseline.json", data)
        self.assertTrue(studio.check_baseline(self.root)["ok"])
        (self.root / "game.cs").write_bytes(b"changed")
        self.assertEqual(studio.check_baseline(self.root)["changed"], ["game.cs"])
        (self.root / "game.cs").unlink()
        self.assertFalse(studio.check_baseline(self.root)["ok"])

    def test_assets_reports_all_invalid_json(self):
        folder = self.root / "Wordz-unity/Assets/Wordz/Data"
        folder.mkdir(parents=True)
        (folder / "good.json").write_text('{"a":1}', encoding="utf-8")
        (folder / "bad.json").write_text('{', encoding="utf-8")
        (folder / "duplicate.json").write_text('{"a":1,"a":2}', encoding="utf-8")
        result = studio.check_assets(self.root)
        self.assertEqual(result["checked_json"], 3)
        self.assertEqual(len(result["errors"]), 2)

    def test_staged_asset_check_reads_index_not_worktree(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        folder = self.root / "Wordz-unity/Assets/Wordz/Data"
        folder.mkdir(parents=True)
        file = folder / "data.json"
        file.write_text('{', encoding="utf-8")
        subprocess.run(["git", "add", "--", file.relative_to(self.root).as_posix()], cwd=self.root, check=True)
        file.write_text('{}', encoding="utf-8")
        self.assertFalse(studio.check_assets(self.root, staged=True)["ok"])

    def test_commit_message_format(self):
        self.assertTrue(studio.validate_commit_message("feat：迁移游戏工作室\n\n迁移技能并完成验证。"))
        for message in ("feat: English\n\nDetails", "feat：迁移\n无空行", "feat：迁移Codex\n\n中文详情", "feat：迁移\n\nEnglish"):
            with self.subTest(message=message), self.assertRaises(studio.StudioError): studio.validate_commit_message(message)


class HookTests(Fixture):
    def hook_module(self):
        spec = importlib.util.spec_from_file_location("studio_hook", TOOLS / "hook.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_start_from_nested_directory_restores_paused_notice(self):
        hook = self.hook_module()
        studio.write_json(self.root / "production/tasks.json", {"tasks": [{"id": "inventory", "status": "paused", "plan": "old.md"}]})
        output, code = hook.handle({"hook_event_name": "SessionStart", "cwd": str(self.root / "unity/Assets")}, self.root)
        self.assertEqual(code, 0)
        self.assertIn("inventory", output["hookSpecificOutput"]["additionalContext"])
        self.assertIn("paused", output["hookSpecificOutput"]["additionalContext"].lower())

    def test_pretool_blocks_git_during_active_plan_but_allows_status(self):
        hook = self.hook_module()
        studio.write_json(self.root / "production/tasks.json", {"tasks": [{"id": "migration", "status": "in_progress", "plan": "plan.md"}]})
        for command in ('git commit -m "feat：迁移"', 'git -C . commit -F message.txt', 'git push origin main', 'git merge branch'):
            output, code = hook.handle({"hook_event_name": "PreToolUse", "tool_input": {"command": command}}, self.root)
            self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny", command)
        output, code = hook.handle({"hook_event_name": "PreToolUse", "tool_input": {"command": "git status --short"}}, self.root)
        self.assertEqual(output, {})

    def test_stop_does_not_resume_or_mutate_task_state(self):
        hook = self.hook_module()
        path = self.root / "production/tasks.json"
        studio.write_json(path, {"tasks": [{"id": "inventory", "status": "paused", "plan": "old.md"}]})
        before = path.read_bytes()
        output, code = hook.handle({"hook_event_name": "Stop", "session_id": "../../unsafe"}, self.root)
        self.assertEqual(code, 0)
        self.assertEqual(path.read_bytes(), before)
        self.assertNotIn("decision", output)
        self.assertTrue(list((self.root / "production/session-logs").glob("*.json")))

    def test_event_audit_does_not_log_tools_or_transcript(self):
        hook = self.hook_module()
        hook.handle({"hook_event_name": "SubagentStart", "session_id": "s", "agent_type": "qa", "tool_input": {"command": "SECRET"}, "transcript_path": "SECRET"}, self.root)
        logs = list((self.root / "production/session-logs").glob("*.json"))
        self.assertEqual(len(logs), 1)
        self.assertNotIn("SECRET", logs[0].read_text())

    def test_all_registered_lifecycle_events_have_native_behavior(self):
        hook = self.hook_module()
        for event in ("PreCompact", "PostCompact", "SubagentStart", "SubagentStop", "Interrupt", "SessionEnd"):
            with self.subTest(event=event):
                output, code = hook.handle({"hook_event_name": event, "session_id": "test"}, self.root)
                self.assertEqual(code, 0)
                if event == "PostCompact": self.assertEqual(output["hookSpecificOutput"]["hookEventName"], event)

    def test_posttool_asset_warning_is_advisory_and_real(self):
        hook = self.hook_module()
        path = self.root / "Wordz-unity/Assets/Wordz/Data/bad.json"
        path.parent.mkdir(parents=True)
        path.write_text('{', encoding="utf-8")
        output, code = hook.handle({"hook_event_name": "PostToolUse", "tool_input": {"patch": "*** Update File: Wordz-unity/Assets/Wordz/Data/bad.json"}}, self.root)
        self.assertEqual(code, 0)
        self.assertIn("bad.json", output["systemMessage"])

    def test_git_read_command_with_commit_word_is_not_a_mutation(self):
        hook = self.hook_module()
        self.assertEqual(hook.git_operations('git log --grep="commit push merge"'), ["log"])

    def test_completed_registry_with_unfinished_checklist_blocks_all_mutations(self):
        hook = self.hook_module()
        (self.root / "plan.md").write_text("- [ ] Task 1：unfinished\n", encoding="utf-8")
        studio.write_json(self.root / "production/tasks.json", {"tasks": [{"id": "migration", "status": "complete", "plan": "plan.md"}]})
        for operation in ("commit", "push", "merge"):
            output, code = hook.handle({"hook_event_name": "PreToolUse", "tool_input": {"command": "git " + operation}}, self.root)
            self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
