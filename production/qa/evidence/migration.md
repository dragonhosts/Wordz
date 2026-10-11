# Wordz 迁移验收证据

## 已完成

- 工作室结构：74 技能、49 角色、470 上游文件；结构和出处检查 PASS。
- 工作室工具定向测试：29/29，无失败；未运行 EchoChronicle 历史玩法测试。
- GameFramework：627 文件逐一哈希一致；框架、Wordz Runtime/Editor 定向源码编译 0 错误，第三方代码保留 1 条过时 API 警告。
- 实际 Unity 2022.3.56f1c1 导入与编译完成；Bootstrap 场景、GameFramework 项目预制体生成。
- 实际进入 Play Mode，ProcedureBootstrap 被框架调用；正交相机就绪，1280×720 实际相机渲染留档 `bootstrap.png`。本次为空工程基础场景，不代表完成了游戏玩法或试玩。
- Unity MCP 10.2.0 本地固定包已迁入，逐文件一致并补保留 MIT 许可；同版本 Python 服务已缓存并启动。
- MCP 握手成功，发现 48 个工具；读回 `E:/Wordz/Wordz-unity`、正确版本、Bootstrap 场景及 ready 状态。
- MCP 实际调用场景读取、Console 查询，并触发 `Wordz/Validate Framework Startup`；生成新的 PASS 记录及截图，返回 Edit Mode；Console 错误 0。
- 无旧玩法、旧任务、旧验收记录、Git 历史或远程配置；迁移验收时新仓库提交数 0；随后用户授权提交并推送指定仓库。

## 证据

`verification.json`、`studio-check.log`、`studio-tools-tests.log`、`compile-*.log`、`unity-import-smoke.log`、`framework-smoke.txt`、`module-install.log`、`unity-mcp.log`、`mcp-protocol.json`、`mcp-menu-verify.json`、`bootstrap.png`。

## 已解决的过程问题

初次编辑器许可缺失，用户已修复；随后发现打开项目的编辑器占用，用户关闭后完成验收。官方模板未声明框架所需内置模块，通过独立 Unity 工程中的 PackageManager.Client API 添加31个固定模块后，同步 API 生成的配置，实际编译通过；未手写包清单补依赖。

## 边界

未产出 Player，未预设玩法/目标平台；后续按批准需求执行游戏设计、定向测试、构建与试玩。Hook 的宿主信任仍需单独确认，本次显式运行检查，不声称自动门禁生效。迁移验收完成时保持未提交；随后用户已明确授权提交与推送。

原始机器诊断 `.log` 保留在本地并被 Git 忽略；发布内容保留本文、结构化验收记录、启动结果与截图。
