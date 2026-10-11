# Unity MCP

- 桥接包：CoplayDev Unity MCP **10.2.0**，原项目本地固定快照，嵌入 `Wordz-unity/Packages/com.coplaydev.unity-mcp/`。
- 保留 MIT 许可。来源及逐文件哈希：`production/migration/unity-mcp-source.json`。
- 服务端：`uvx --from mcpforunityserver==10.2.0 mcp-for-unity --transport http --http-url http://127.0.0.1:8080 --project-scoped-tools`。
- 地址：`http://127.0.0.1:8080/mcp`。Codex 项目配置 `.codex/config.toml`；Claude HTTP 客户端配置 `.mcp.json`。本机 Codex 已有同地址配置。
- 启动脚本：`powershell -NoProfile -File tools/unity/start-mcp.ps1`；仅绑定本机，不配置系统开机自启。
- 用 Unity 2022.3.56f1c1 打开工程后，菜单 `Wordz/Connect Unity MCP` 连接；`Window/MCP for Unity` 可查看连接状态。
- 多工程同时打开时，先用实例资源确认，再用 `set_active_instance` 明确选择 Wordz，避免操作其他工程。
- 工具安装不等于连接成功：本次通过协议读回项目路径、编辑器 ready 状态、当前 Bootstrap 场景和 Console，并通过 MCP 执行定向启动验收菜单。
- 当前宿主会话是否加载工具由 Codex 客户端负责；项目包和 HTTP 服务已经实测，不声称本聊天已有原生 Unity 工具注入。
