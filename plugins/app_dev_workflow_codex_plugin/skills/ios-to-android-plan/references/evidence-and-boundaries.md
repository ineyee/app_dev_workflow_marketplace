# 证据等级、差距分析与边界规则

## 证据等级

按强度使用并在计划中标注：

1. `verified-code`：当前分支代码、Git diff、构建/测试命令直接证明。
2. `verified-doc`：仓库文档明确记录，且未被代码反驳。
3. `session-confirmed`：当前会话或用户附图明确确认，但代码尚未证实。
4. `platform-equivalent`：Android 实现方式不同，但用户可观察行为等价；必须同时给出 Android 证据。
5. `external-unverified`：Flutter/外部设备/网络协议等只能由当前代码或运行时进一步核对。

代码与文档冲突时，以当前代码和可复现命令为准，在“Assumptions and Blockers”记录冲突；不要把旧文档升级为事实。

## 差距判定

- **已实现**：Android 当前行为已经满足最终要求，不要重复安排修改。
- **部分实现**：入口/页面/回调存在，但缺少最终状态分支、来源标记、媒体清理、导航或资源。
- **未实现**：经搜索没有对应实现，需要新增文件或方法。
- **与 iOS 不同但可接受**：实现机制不同且已有证据证明用户行为等价。
- **需要确认**：代码、文档和会话证据不足；写出核对动作和阻塞，不创造类名、Channel 或协议。

每行差距都要绑定真实 Android 相对路径、类和方法。只有 iOS 文件名不构成 Android 证据。

## Flutter 只读边界

允许读取 Android 构建脚本实际解析出的 Flutter 工作树当前 commit、路由、Dart 方法、MethodChannel/EventChannel 名称、参数和返回/事件结构，用来确定 Android 调用契约。macOS/Linux 上若 `settings.gradle`/`settings.gradle.kts` 解析到 Android 同级的 `near_stream_flutter_module`，必须以该同级工作树为事实源。Android 仓库内部同名目录只有在构建脚本明确选中，或脚本在同级目录不存在时确实回退到它，才可作为事实源；否则只能作为标明路径、commit 和“未被构建脚本选中”的备用副本。禁止：

- 修改任何 Dart/Flutter 文件；
- 更新 submodule 指针、生成 Flutter 代码或修改 Flutter 文档；
- 增加未被现有 Flutter 代码证明的 key、route、Channel、参数或事件；
- 因 Android 缺少适配而把 Flutter 改动写进计划的 `Modify` 列。

若接口未知，使用 `external-unverified`，安排“实现前读取指定 Flutter 文件并确认”，而不是猜 API。若 Android 现有桥接与 iOS 目标不一致，只计划 Android 侧桥接适配。

## 工作树与写入边界

先读取 Android `settings.gradle`/`settings.gradle.kts`、`.gitmodules`（若存在）和相关构建配置，解析实际 Flutter 工作树，再记录 iOS、Android、实际 Flutter 工作树三处 `git status` 及 commit；若 Android 仓库内部存在未被选中的同名副本，也记录其 status/commit 并明确标为备用副本，不得冒充实际构建源。把已有未提交改动视为用户资产，不覆盖、不重置、不归因于本需求。skill 的唯一默认写入是 Android 根仓库 `docs/features/<功能名>-Android实施计划.md`；写入前对该目标运行 `git status --short -- <target>` 和 `git diff -- <target>`。若无法确认目标文件已有内容的归属，必须先询问用户。不要自动更新项目总览、模块文档、业务代码、测试或 Gradle。

## 计划质量检查

交付前逐项检查：

- 是否合并了会话最终需求并标记废弃旧行为；
- 是否保留入口 1 的兼容约束；
- 是否有入口标记和完整状态机；
- 是否写出断开、预览/音频/MediaEngine 清理和导航回首页链路；
- 是否每个待办绑定真实文件/类/方法；
- 是否给出生命周期、线程、去重、错误/超时/重试；
- 是否明确 Flutter 不改但需要读取现有契约；
- 是否有四语资源和实际 Gradle/test 命令；
- 是否没有 Android、iOS、Flutter 业务文件改动。
