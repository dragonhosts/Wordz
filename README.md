# Wordz

独立 2D 小游戏项目，迁移自 EchoChronicle 的开发流程、规范及固定版本 GameFramework。

## 工程

使用 Unity **2022.3.56f1c1** 打开 `Wordz-unity/`。Built-in、Legacy Input Manager；官方 2D 模板 7.0.3。
启动场景与项目预制体已生成；需要重新配置新工程时执行菜单 **Wordz / Configure 2D Project**，生成正交相机、GameFramework 项目预制体和 `Assets/Wordz/Scenes/Bootstrap.unity`。
启动流程为 `Wordz.Framework.ProcedureBootstrap`，进入时输出 `Wordz GameFramework ready`。无预设玩法。

## 开发流程

读取 `AGENTS.md` → `$studio-help` / 自然语言 → 明确玩法并编写简要设计 → 原批准计划 → 实现 → 定向验证及试玩 → 展示证据 → 用户批准提交。
沿用轻流程与 guided 自动化、中文提交规范和多阶段清单。设计在 `DesignDoc/`；设计/计划在 `docs/superpowers/specs/`、`plans/`。
工作室有 74 个技能与 49 个角色；Claude 上游原文和许可证在 `.agents/game-studio/upstream/`；Codex 适配在 `.agents/game-studio/CODEX.md`。`CLAUDE.md` 提供跨宿主入口，不声称已经安装 Claude 插件或 Hook。
个人安装的 Superpowers、Unity Workbench 等技能仍由宿主提供；本仓库不复制宿主插件缓存或凭据。

```powershell
python tools/game-studio/studio.py config
python tools/game-studio/studio.py status
python tools/game-studio/studio.py check --scope all
```

Hook 需宿主审查与信任，未确认前显式运行检查。工作室检查不能替代 Unity 编译、构建或试玩。
迁移清单见 `docs/superpowers/plans/2026-10-11-project-migration.md`，证据见 `production/qa/evidence/migration.md`。
独立 Git 仓库：`https://github.com/dragonhosts/Wordz`；保留远程初始历史。原项目的未提交玩法内容和旧任务不进入本项目。

## Unity MCP

已安装并实测 CoplayDev Unity MCP 10.2.0，地址 `http://127.0.0.1:8080/mcp`。重启服务可运行 `tools/unity/start-mcp.ps1`，Unity 中用 `Wordz/Connect Unity MCP` 连接。详见 `DesignDoc/UnityMcpSetup.md`。
