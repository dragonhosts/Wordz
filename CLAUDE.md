# Wordz 项目协作入口

先读取 `AGENTS.md` 与 `project.yaml`，二者对项目规范和技术栈具有权威性。
工作室迁移自 Claude Code Game Studios 1.1.2，当前可执行入口为 `.agents/skills/studio-*/SKILL.md`。
`.agents/game-studio/upstream/` 保留完整上游参考和许可证，不作为活动 Claude 配置。
在 Claude 宿主运行时，将 Codex 工具映射为实际可用工具；不要执行上游 shell 注入，不假定 Codex Hook 在 Claude 中生效。
禁止实现阶段提交、推送、合并或创建 PR；验证全部任务后展示证据并等待用户批准提交。
