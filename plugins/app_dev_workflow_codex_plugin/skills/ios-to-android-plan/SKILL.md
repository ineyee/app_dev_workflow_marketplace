---
name: ios-to-android-plan
description: Use when the current conversation contains an iOS feature change and the user needs a Chinese, file-level implementation plan for the equivalent Android native work, with existing Flutter code treated as a read-only integration contract.
---

# iOS → Android 原生实施计划

## 适用范围

当当前会话已经讨论、实现或确认过 iOS 功能变更，且用户要把最终行为迁移/对接到 Android、输出计划而不是直接改 Android 代码时使用。本 skill 支持自动发现，也支持 `$ios-to-android-plan` 显式调用。

## 不可违反的边界

- 生成的计划只描述未来需要实施的 Android 原生改动；本次 skill 执行不得修改 Android 业务代码、测试代码、Gradle 配置或 `PROJECT_OVERVIEW.md`。
- Flutter/Dart 只读核验：不得修改构建脚本实际选中的 Flutter 工作树中的 `near_stream_flutter_module/**`，不得更新 Android submodule 指针，不得自行创造新的 route、MethodChannel、EventChannel 或参数。
- 计划必须以实际 Android 文件、类、方法和可验证命令为依据；不能把 iOS 文件名机械映射成 Android 类名。
- 保留 Android 与 iOS 工作树已有未提交修改；不要 reset、checkout、覆盖或把现有改动误判为本需求已完成。
- 找不到可靠的 Android 根目录时，停止生成文件级计划并向用户询问路径；不得猜路径、伪造文件名或写入 iOS/Flutter 仓库。
- 默认只写 Android 根目录 `docs/features/<功能名>-Android实施计划.md`。若同名文件存在，先读取，并用 `git status --short -- <target>`、`git diff -- <target>` 检查其状态；保留仍有效事实并以当前会话最终行为替换过期要求。若无法确认目标文件现有未提交/未跟踪内容的归属，先询问用户，不得覆盖。

## 工作流程

### 1. 定位仓库并读取规范

先检查当前工作区和用户明确路径；若当前仓库是 `multistream-cam-ios`，优先检查同级 `multistream-cam-android`，但必须通过目录内容确认。Android 根目录候选必须逐项核验：`AGENTS.md`、`PROJECT_OVERVIEW.md` 是文件，`app/`、`docs/` 是预期目录，并确认它们属于同一 Android 仓库；Android 根目录不要求必须包含 `near_stream_flutter_module/`，因为 Flutter 工作树可能位于其同级目录。随后读取 Android `AGENTS.md`、项目总览、文档索引、相关 `docs/modules/`、`docs/guides/文档维护规范.md`、相关 feature/history 文档，并查看当前分支 `git status` 与必要的最近提交。

解析 Flutter 事实源时，必须先读取 Android 根目录的 `settings.gradle`/`settings.gradle.kts`、`.gitmodules`（若存在）和相关构建配置，按构建脚本实际路径选择 Flutter 工作树。在 macOS/Linux 上，如果脚本通过 `settingsDir.parentFile`、`../near_stream_flutter_module` 或等价路径解析 Android 同级目录，则使用 `multistream-cam-android` 同级的 `near_stream_flutter_module` 作为事实源。不要因为 Android 仓库内部存在同名目录就把它当作事实源；内部同名目录只能作为明确标注的备用副本。计划必须记录实际 Flutter 路径及 commit；若存在内部副本，也记录其路径/commit 和未被构建脚本选中的状态。只有构建脚本明确选择内部目录，或脚本确实在同级目录不存在时回退到内部目录，才读取内部副本作为事实源。

### 2. 合并会话中的最终需求

完整回看当前会话，按时间顺序区分初始需求、变更、废弃行为、图片可观察状态、已在 iOS 实现的行为和明确不改动部分。计划只描述最终有效行为；可用“历史变更摘要”解释冲突，但不得要求实现者同时支持已废弃逻辑。

### 3. 建立 iOS 行为基线

读取 iOS 实际 diff、相关控制器/服务/通知/回调、测试脚本和本地化资源。把 iOS 行为翻译成 Android 可执行规格：入口来源标记、状态机、Wi‑Fi 成功后设备连接判断、断开和视频/音频/MediaEngine 清理、Done/Connect 导航、返回首页后 Add Asset → Connect Devices、资源 key 及兼容约束。Flutter 调用只记录为契约来源。

### 4. 盘点 Android 现状并做差距分析

先搜索真实 Android 类、方法、导航、连接服务、预览/音频源、资源、Channel 和测试。每项放入“已实现、部分实现、未实现、与 iOS 不同但可接受、需要确认”之一，并绑定真实相对路径、类名和方法。文档/代码冲突以当前代码和命令输出为准并记录冲突。

### 5. 写入计划并验证

使用 [android-plan-template.md](references/android-plan-template.md) 的固定结构和任务格式，使用 [evidence-and-boundaries.md](references/evidence-and-boundaries.md) 的证据等级、差距和 Flutter 边界规则。生成中文 Markdown，front matter 为 `document_type: feature`、`status: active`、`verification: design-only`、当前日期。任务按“失败测试/契约 → 状态模型与入口 → 页面导航 → 断开和媒体清理 → 资源多语言 → Flutter Channel → 集成验证”排序。

完成后检查：输出位于 Android `docs/features/`；没有业务代码或 Flutter 文件改动；所有文件/类/方法均有证据或明确标成 `需要确认`；测试命令来自 Android 实际 Gradle task；计划包含状态、生命周期、线程、去重、页面销毁回调和验收矩阵。

## 关键产品约束的表达方式

不要只写“仿照 iOS”。对类似 Connect Devices/Wi‑Fi 的需求，明确写出三个入口、入口 1 原 Setup 流程不变、入口 2/3 的来源记录、设备和手机网络状态、App 是否仍连接设备、断开时的视频/音频/MediaEngine 清理、Done/Connect/To connect device 的导航，以及四语资源。具体行为以当前会话和代码证据为准，不把本段示例当成额外产品需求。

## 输出

计划正文必须包含以下 12 个章节：Goal、Final Behavior、Android Current Baseline、Gap Analysis、Architecture and Data Flow、Public Interfaces and Models、File-Level Implementation Tasks、Flutter Boundary、Localization and Resources、Test and Acceptance Matrix、Explicit Non-Goals、Assumptions and Blockers。章节标题可保留英文以便检索，正文使用简体中文。不得把计划执行成代码变更。
