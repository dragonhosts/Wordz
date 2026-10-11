"""Import an explicit CCGS archive into Codex entrypoints; never touch game files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        raise ValueError("Missing source frontmatter")
    fields = {}
    for line in match[1].splitlines():
        key, sep, value = line.partition(":")
        if sep:
            value = value.strip()
            if value.startswith('"'):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    value = value.strip('"')
            fields[key] = value
    return fields, text[match.end():]


NOTICE = """> Codex adaptation: read `.agents/game-studio/CODEX.md` first. It supersedes
> source-runtime tool names, approvals, models, paths, helpers and engine defaults
> below. Treat upstream shell examples as reference, not executable bootstrap.

"""


def adapt_source(text: str, skill_names: list[str]) -> str:
    for name in sorted(skill_names, key=len, reverse=True):
        # A slash command is a standalone token, never a slash inside a path.
        text = re.sub(r"(?<![\w./-])/" + re.escape(name) + r"(?![\w/.-])", "$studio-" + name, text)
    text = text.replace(".claude/skills/", ".agents/game-studio/workflows/")
    text = re.sub(r"(\.agents/game-studio/workflows/[^\s`\"']+/)SKILL\.md", r"\1WORKFLOW.md", text)
    text = text.replace(".claude/agents/", ".agents/game-studio/roles/")
    text = text.replace(".claude/docs/", ".agents/game-studio/docs/")
    text = text.replace(".claude/rules/", ".agents/game-studio/rules/")
    text = text.replace(".claude/scripts/", ".agents/game-studio/upstream/.claude/scripts/")
    text = text.replace(".claude/hooks/", ".agents/game-studio/upstream/.claude/hooks/")
    text = text.replace("docs/engine-reference/", ".agents/game-studio/upstream/docs/engine-reference/")
    text = text.replace("CCGS Skill Testing Framework/", ".agents/game-studio/upstream/CCGS Skill Testing Framework/")
    for name in ("COLLABORATIVE-DESIGN-PRINCIPLE.md", "WORKFLOW-GUIDE.md", "skill-flow-diagrams.md", "migration-guide-v1.1.md"):
        text = text.replace("docs/" + name, ".agents/game-studio/upstream/docs/" + name)
    text = re.sub(r"^!`.*?`\s*$", "Run `python tools/game-studio/studio.py config` explicitly before this workflow; no shell preprocessing is used.", text, flags=re.M)
    return text


def regenerate_references(root: Path) -> None:
    shared = root / ".agents/game-studio"
    upstream = shared / "upstream"
    names = sorted(p.parent.name for p in (upstream / ".claude/skills").glob("*/SKILL.md"))
    for category in ("docs", "rules", "skills", "agents"):
        base = upstream / ".claude" / category
        for src in base.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(base)
            if category == "skills":
                dest = shared / "workflows" / rel
                if src.name == "SKILL.md": dest = dest.with_name("WORKFLOW.md")
            else:
                dest = shared / {"agents": "roles"}.get(category, category) / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            text = src.read_text(encoding="utf-8-sig")
            if category in ("skills", "agents") and (src.name == "SKILL.md" or category == "agents"):
                _, text = frontmatter(text)
            dest.write_text((NOTICE if src.suffix == ".md" else "") + adapt_source(text, names), encoding="utf-8")


def import_archive(root: Path, archive: Path) -> dict:
    shared = root / ".agents/game-studio"
    if (shared / "source.json").exists():
        raise ValueError("Already imported; use a reviewed migration for upgrades")
    baseline = {}
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], cwd=root
    ).decode("utf-8").split("\0")
    for row in status:
        if not row:
            continue
        name = row[3:]
        if name.startswith((".studio-upstream", "production/migration/", "docs/superpowers/specs/2026-10-06-", "docs/superpowers/plans/2026-10-06-", "tools/game-studio/")):
            continue
        path = root / name
        if path.is_file():
            baseline[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    # Root files that migration is allowed to extend are recorded separately.
    for name in ("AGENTS.md", "README.md", ".gitignore"):
        path = root / name
        baseline[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    for name in (".superpowers/sdd/2026-09-28-inventory-hotbar-keybindings/progress.md", ".agents/skills/superpowers-plan-execution/SKILL.md"):
        path = root / name
        if path.is_file():
            baseline[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    baseline_path = root / "production/migration/baseline.json"
    if not baseline_path.exists():
        dump(baseline_path, baseline)

    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        prefix = names[0].split("/")[0] + "/"
        for name in names:
            rel = name.removeprefix(prefix)
            if not rel or name.endswith("/"):
                continue
            if not (rel.startswith((".claude/", "docs/", "CCGS Skill Testing Framework/")) or rel in ("LICENSE", "README.md", "CHANGELOG.md", "project.yaml", "CLAUDE.md")):
                continue
            dest = (shared / "upstream" / rel).resolve()
            if not dest.is_relative_to((shared / "upstream").resolve()):
                raise ValueError("Unsafe archive member")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(name))

    upstream = shared / "upstream"
    source_skills = sorted((upstream / ".claude/skills").glob("*/SKILL.md"))
    source_agents = sorted((upstream / ".claude/agents").glob("*.md"))
    skill_names = [p.parent.name for p in source_skills]

    def adapt(text: str) -> str:
        return adapt_source(text, skill_names)

    notice = """> Codex adaptation: read `.agents/game-studio/CODEX.md` first. It supersedes
> source-runtime tool names, approvals, models, paths, helpers and engine defaults
> below. Treat upstream shell examples as reference, not executable bootstrap.

"""
    for category in ("docs", "rules"):
        for src in (upstream / ".claude" / category).rglob("*"):
            if src.is_file():
                dest = shared / category / src.relative_to(upstream / ".claude" / category)
                dest.parent.mkdir(parents=True, exist_ok=True)
                body = adapt(src.read_text(encoding="utf-8-sig"))
                dest.write_text((notice if src.suffix == ".md" else "") + body, encoding="utf-8")

    manifest = {"skills": [], "agents": []}
    for src in source_skills:
        name = src.parent.name
        meta, body = frontmatter(src.read_text(encoding="utf-8-sig"))
        desc = meta["description"]
        dest = shared / "workflows" / name / "WORKFLOW.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(notice + adapt(body), encoding="utf-8")
        for extra in src.parent.rglob("*"):
            if extra.is_file() and extra != src:
                other = dest.parent / extra.relative_to(src.parent)
                other.parent.mkdir(parents=True, exist_ok=True)
                other.write_text(notice + adapt(extra.read_text(encoding="utf-8-sig")), encoding="utf-8")
        entry = root / ".agents/skills" / ("studio-" + name) / "SKILL.md"
        if entry.exists():
            raise ValueError(f"Skill collision: {entry}")
        entry.parent.mkdir(parents=True, exist_ok=True)
        entry.write_text(
            "---\nname: studio-" + name + "\ndescription: "
            + json.dumps("Game Studio / " + desc, ensure_ascii=False) + "\n---\n\n"
            + "# Game Studio: " + name + "\n\n"
            + "Read `.agents/game-studio/CODEX.md` and run `python tools/game-studio/studio.py config` from the repository root. "
            + "Do not execute embedded shell preprocessing or original Claude tool names.\n\n"
            + "Read `.agents/game-studio/workflows/" + name + "/WORKFLOW.md` on demand and execute its relevant phases using the Codex adapter. "
            + "Consult `python tools/game-studio/studio.py workflow " + name + "` for project-specific routing. "
            + "Existing approved plans and paused-task records govern scope. Read only references needed by this request; do not load the whole studio. "
            + "Keep commits, pushes, merges and PR creation outside implementation until the project's completion and human approval gate.\n",
            encoding="utf-8",
        )
        manifest["skills"].append({"name": "studio-" + name, "description": desc, "workflow": dest.relative_to(root).as_posix(), "entry": entry.relative_to(root).as_posix()})

    for src in source_agents:
        name = src.stem
        meta, body = frontmatter(src.read_text(encoding="utf-8-sig"))
        dest = shared / "roles" / (name + ".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(notice + adapt(body), encoding="utf-8")
        instructions = (
            f"You serve the {name} role in Wordz. Read .agents/game-studio/CODEX.md "
            f"and .agents/game-studio/roles/{name}.md from the repository root before work. "
            "Follow only the delegated scope; report files, evidence and blockers. "
            "Do not resume paused tasks. Preserve Unity 2022.3 Built-in, Legacy Input Manager and GameFramework. "
            "Use available Codex tools; explicit delegation prompts may carry this role when named-agent selection is unavailable. "
            "Never commit, push, merge, publish or create a PR during implementation. "
            "Approved scope is sufficient for ordinary edits; do not repeat source-runtime file-write approvals."
        )
        agent = root / ".codex/agents" / ("studio-" + name + ".toml")
        agent.parent.mkdir(parents=True, exist_ok=True)
        # JSON basic strings are also legal TOML basic strings for these fields.
        agent.write_text(
            'name = ' + json.dumps("studio-" + name) + '\ndescription = '
            + json.dumps(meta["description"], ensure_ascii=False)
            + '\ndeveloper_instructions = ' + json.dumps(instructions, ensure_ascii=False) + '\n',
            encoding="utf-8",
        )
        manifest["agents"].append({"name": "studio-" + name, "role": dest.relative_to(root).as_posix(), "config": agent.relative_to(root).as_posix(), "source_model": meta.get("model", "inherit")})

    framework = (upstream / "project.yaml").read_text(encoding="utf-8-sig")
    version = re.search(r"^  version:\s*(.*)$", framework, re.M)
    provenance = {
        "repository": "https://github.com/Donchitos/Claude-Code-Game-Studios",
        "download_url": "https://codeload.github.com/Donchitos/Claude-Code-Game-Studios/zip/refs/heads/main",
        "retrieved": "2026-10-06", "framework_version": version[1] if version else "unknown",
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "commit": "Not determined; exact snapshot identified by archive and file SHA-256",
        "license": "upstream/LICENSE", "counts": {"skills": len(source_skills), "agents": len(source_agents)},
        "files": {p.relative_to(upstream).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(upstream.rglob("*")) if p.is_file()},
    }
    dump(shared / "catalog.json", manifest)
    dump(shared / "source.json", provenance)
    return provenance


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = import_archive(args.root.resolve(), args.archive.resolve())
    print(json.dumps({k: result[k] for k in ("framework_version", "archive_sha256", "counts")}, indent=2))
