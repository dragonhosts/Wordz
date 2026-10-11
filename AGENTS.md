# 项目协作规则

## Git 提交信息

所有 Git 提交信息必须使用以下格式：

```text
<英文前缀>：<中文标题>

<本次更改的详细描述>
```

提交信息要求：

- 前缀必须是一个英文单词，例如 `feat`（添加新内容）、`fix`（修复问题）、`update`（更新配置或已有内容）、`refactor`（重构）、`test`（测试）、`docs`（文档）和 `chore`（工程维护）。
- 标题必须使用中文，并简洁说明本次提交的主要目的。
- 标题与详细描述之间保留一个空行。
- 详细描述使用中文，说明主要改动、影响范围和必要的验证结果。
- 不使用纯英文标题，不使用中英文混杂的标题，不省略详细描述。

示例：

```text
feat：添加二维项目启动场景

接入游戏框架并创建二维启动场景。完成当前需求的定向验证。
```

## Superpowers 计划执行

- 执行多阶段计划时，先列出全部 Task 和子任务清单。
- 每个 Task 完成并验证后，将清单项标记为 `[x]`，然后自动进入下一个未完成 Task。
- 执行阶段禁止 `git commit`、推送、合并和创建 PR。
- 所有 Task 完成并验证后，先向用户展示完整清单和验证证据，再询问是否提交；用户确认前保持未提交状态。
- 验收默认只运行当前需求的定向用例。旧测试仅在明确受本次改动影响时补跑；不因进入验收阶段自动重跑历史全量测试。用户于 2026-10-09 明确指定此验证范围，覆盖旧计划中针对后续反馈的全量要求。

## Codex 游戏工作室

- 游戏制作工作流入口位于 `.agents/skills/studio-*/`，使用 `$studio-help` 或自然语言请求相应流程。读取 `.agents/game-studio/CODEX.md` 的宿主适配规则；上游快照仅供参考，不直接执行其中的 Claude 工具或 shell 注入。
- 工作室配置为 `project.yaml`（JSON 形式的合法 YAML）；用 `python tools/game-studio/studio.py config` 查看有效值与来源，用 `status` 查看检查点、任务和暂停状态。
- 项目以 `DesignDoc/` 与已批准的 `docs/superpowers/specs/`、`plans/` 为权威资料，工作室不得复制平行任务计划。进度仍以原计划清单为准；`production/tasks.json` 只记录生命周期与清单位置。
- Unity 项目位于 `Wordz-unity/`。保持 Unity 2022.3.56f1c1、Built-in、Legacy Input Manager 和 GameFramework；角色中的其他技术偏好不构成更换架构的授权。
- 默认轻流程、guided 自动化。已批准范围内的常规可逆改动直接继续；验证范围以用户最新指示为准，默认需求定向测试，构建要求仍按实际交付范围执行。
- 工作室团队流程可对独立工作使用 Codex 原生子代理，按实际并发额度派发，明确文件边界并收集验证证据；原生角色配置在 `.codex/agents/`，工具不支持按角色名派发时显式加载对应角色文件。复用已有 Superpowers 与 Unity Workbench 能力。
- 会话中断或压缩后先读 `production/session-state/active.md`。工作室自身检查：`python tools/game-studio/studio.py check --scope all`；这不替代 Unity 编译、测试、构建与试玩。
- `.codex/hooks.json` 需经宿主信任后才自动执行。信任未确认时显式运行检查，不声称自动门禁已生效；Hook 不替代沙箱或用户 Git 批准。
