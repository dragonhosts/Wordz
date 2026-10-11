---
name: superpowers-plan-execution
description: Use when executing a multi-task implementation plan where progress tracking, task ordering, or commit timing must be explicit.
---

# Superpowers 计划执行规则

## 计划阶段

在修改代码前列出计划中的全部 Task，使用可勾选清单，并为每个 Task 列出主要子任务、验证方式和依赖关系。清单是本次执行的唯一进度来源；不得只展示当前 Task 而隐藏后续任务。

## 执行阶段

按清单顺序执行。每完成一个 Task，先运行该 Task 规定的验证，再将对应项改为 `[x]`，记录验证结果和未解决风险，然后立即开始下一个未完成 Task。不得等待用户再次确认，也不得把一个 Task 的代码误标为整个计划完成。

执行过程中禁止执行任何 Git 提交、推送、合并或创建 PR。可以查看状态、生成 diff、暂存文件以检查范围，但不得创建提交对象。所有代码和资源任务及其验证全部完成后，才向用户报告最终清单、验证证据和待处理风险，并询问是否提交；在用户明确同意前保持工作树未提交。

## 完成阶段

只有当全部 Task 都已勾选且验证完成，才可以声明计划完成。若有失败或阻塞，保留未勾选状态，说明证据和下一步，不得用“基本完成”替代清单状态。
