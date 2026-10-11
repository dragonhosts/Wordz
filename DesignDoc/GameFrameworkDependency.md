# GameFramework 依赖与构建记录

## 固定版本

- 上游：`https://github.com/EllanJiang/UnityGameFramework`，提交 `e7eb3ef11393df0ac504204c480cdb839752b05f`。
- 获取地址：`https://codeload.github.com/EllanJiang/UnityGameFramework/zip/e7eb3ef11393df0ac504204c480cdb839752b05f`。
- 上游 ZIP SHA-256：`F3D620AA96CE1DFC9113AA6D4377C6A925FBEA40AB5278B6D3A9392D89A7081C`。
- 随附 `GameFramework.dll` SHA-256：`765C0E15EDE1ADBDB6892133F60E5095168EF5BD121B37D062F3DC7EAD18AFE9`。
- 随附 `ICSharpCode.SharpZipLib.dll` SHA-256：`40B3D590F95191F3E33E5D00E534FA40F823D9B1BB2A9AFE05F139C4E0A3AF8D`；程序集版本 `0.86.0.518`。

从同一 ZIP 导入 `Libraries`、`Scripts`、`GameFramework.prefab`、`LICENSE.md` 及其原始 `.meta`。没有混入独立 GameFramework 仓库的其他 DLL。上游 `package.json` 的版本号 `2021.05.31` 不符合 UPM SemVer；本项目使用固定快照，不以浮动 Git 包安装。

## 许可证

- UnityGameFramework：MIT；许可证原文保留在 `Assets/ThirdParty/GameFramework/LICENSE.md`。随附 GameFramework 核心 DLL 对应项目也采用 [MIT](https://github.com/EllanJiang/GameFramework/blob/master/LICENSE.md)。
- SharpZipLib `0.86.0`：此**旧版**采用 GPL 加链接例外，见[旧版官方许可说明](https://icsharpcode.github.io/SharpZipLib/legacy.html)。目前仓库的 MIT 许可证不适用于这个旧 DLL；分发 Player 时需保留该旧版许可与来源说明。项目没有修改这个 DLL。

## 本地适配

上游源码和 DLL 内容未修改。为 Unity 2022.3 增加本地 `UnityGameFramework.Runtime` 与 `UnityGameFramework.Editor` 程序集定义，并让项目 Runtime、Editor、测试程序集按需求显式引用所需程序集。PlayModeTests 对预编译 `GameFramework.dll` 使用 `overrideReferences` / `precompiledReferences`；原有 `TestAssemblies` 自动引用保留，未手动添加 TestRunner 重复引用。


## Wordz 迁移

本地固定快照逐文件 SHA-256 校验，文件清单见 `production/migration/gameframework-files.json`。本工程尚无资源打包业务；不继承 EchoChronicle 的资源构建脚本或历史验证结论。
GameFramework MIT 原文保留；随附旧 SharpZipLib 的许可与来源说明保留在本文件，Player 分发时继续携带相应声明。
