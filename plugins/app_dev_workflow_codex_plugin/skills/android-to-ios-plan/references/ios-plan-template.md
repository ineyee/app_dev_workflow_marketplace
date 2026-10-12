# iOS Feature 计划模板

生成文件必须放在 iOS 根仓库 `docs/features/`，使用如下 front matter（日期为实际验证日期）：

```yaml
---
document_type: feature
status: active
verification: design-only
last_verified: YYYY-MM-DD
---
```

标题使用业务功能名，例如 `# VM33 Wi‑Fi 切换与设备连接流程 iOS 原生实施计划`。正文固定使用以下章节；不能用泛化模块清单替代证据、状态或任务。

## 1. Goal

写清用户最终看到的行为、iOS 原生实施目标、需要对齐的入口/页面/状态/导航，并明确只改 iOS 原生、Flutter 已完成且不改、目标与 Android 最终行为一致。

## 2. Final Behavior

用入口和状态表描述：入口/状态、用户操作、预期行为、保持不变的行为。状态机至少覆盖入口标识、初始、Wi‑Fi 成功/失败/取消/返回、手机未连接或已连接 Wi‑Fi、App 已连接或未连接设备、Done、Connect/To connect device。注明旧行为已废弃的地方。入口 1 的 Setup/AP 流程若被声明兼容，必须单独列出。

## 3. iOS Current Baseline

按真实相对路径、类名和方法列出 UIViewController/SwiftUI View、ViewModel/Coordinator、设备连接与网络服务、BLE/HTTP、设备列表、视频/音频预览与 MediaEngine、首页导航、通知/回调、资源、本地化、Flutter bridge、测试和构建命令。每个结论说明证据来源；未确认的不要猜。

## 4. Gap Analysis

至少使用下表字段：

| 状态 | iOS 当前代码/证据 | Android 最终目标 | iOS 需要增加或调整 | 不能修改/Flutter 影响 | 验证 |
|---|---|---|---|---|---|
| 已实现/部分实现/未实现/与 Android 不同但可接受/需要确认 | 真实路径、类、方法 | 可执行行为 | 文件级动作 | 兼容边界 | 命令或真机步骤 |

## 5. Architecture and Data Flow

画出 iOS 数据流，并说明状态所有权、生命周期、线程切换、重复回调去重和页面销毁后的回调处理。例如：入口页面 → entryPoint/source → Wi‑Fi 页面 → 成功状态 → 设备连接管理 → 媒体清理 → 首页导航 → Add Asset → Connect Devices。需要 Flutter 时写出现有 bridge/channel/route/event 的方向和适配点。

## 6. Public Interfaces and Models

列出要新增/修改的 Swift enum、struct/class、Objective‑C enum/model、UIViewController/SwiftUI 参数、ViewModel、Coordinator、Service 回调、Notification、delegate、closure、Combine/async sequence、Flutter bridge 方法参数、resource key 和测试辅助接口。每项写输入、输出、生命周期、调用方；没有证据的接口标为“实现前核对”，不得自创。

## 7. File-Level Implementation Tasks

每个任务严格采用：

```markdown
### Task N：任务名称

Files:
- Create: ...
- Modify: ...
- Do not modify: ...

Current code:
- 真实当前行为、路径、类和方法。

Required change:
- 最终行为与差距。

Implementation details:
- 状态、参数、线程、生命周期、错误/超时/重试、兼容约束。

Acceptance:
- 可观察的通过条件。

Verification:
- 实际测试/构建/真机命令或步骤。
```

任务顺序：先失败测试或行为契约；再状态模型和入口标识；再页面/导航；再设备断开及视频、音频、MediaEngine 清理；再资源多语言；再 Flutter bridge；最后集成验证。每个任务都要包含真实文件或明确的确认阻塞点。

## 8. Flutter Boundary

单独写明不修改构建脚本实际选中的 Flutter 工作树中的 `near_stream_flutter_module/**`，不更新 Android/Flutter submodule 指针；只读实际 Flutter 工作树的当前 commit、route、Dart 方法、MethodChannel/EventChannel 名称和参数/返回值。macOS/Linux 若构建脚本解析到 Android 同级 `near_stream_flutter_module`，必须记录该路径和 commit；内部同名副本若未被选中，只能作为标明状态的备用证据。iOS 只调用既有接口并适配原生状态。若 iOS bridge 与 Android 目标不一致，列出 iOS 当前 bridge、Android 目标、Flutter 现有接口、iOS 适配位置和不改 Flutter 的理由。证据不足标为 `external-unverified`，要求实现者先核对。

## 9. Localization and Resources

列出实际 iOS `.lproj` 目录、`Localizable.strings`/String Catalog、key、旧 key 清理策略、Storyboard/XIB/SwiftUI accessibility 文案和图片资源。覆盖中文、英文、日文、西班牙文；用户给出的文案保持语义，不擅自改写。说明 iOS 资源命名、Dynamic Type、RTL 和无障碍验证。

## 10. Test and Acceptance Matrix

至少覆盖：入口 1 原流程；入口 2/3 记录；Wi‑Fi 成功/失败；手机未/已连 Wi‑Fi；App 已/未连设备；断开后视频预览、音频源、MediaEngine、设备列表清理；Done；Connect/To connect device；AP 流程；bridge 参数；四语；旋转/尺寸变化、后台恢复、重复点击、页面销毁；空设备、非法状态、超时、重试。命令必须来自当前工程实际 scheme、脚本或 harness，不写死不存在的 target。区分本地单测、XCTest/UI test、xcodebuild build/test、Flutter 只读验证、真机和外部网络验证。

## 11. Explicit Non-Goals

至少写：不改 Flutter/Dart、不更新 submodule、不重写无关设备协议、不重构整个导航、不改入口 1 Setup、不删除已有等价实现、不用 Android 类名代替 iOS 类名、不修改 iOS 业务/测试/Xcode/CocoaPods/项目总览。

## 12. Assumptions and Blockers

记录 iOS 路径/分支、两端工作树未提交状态、由 Android 构建脚本解析出的实际 Flutter 工作树路径及 commit；macOS/Linux 常为 Android 同级 `near_stream_flutter_module`，不要默认写 iOS 内部副本。若存在内部同名副本，记录其路径/commit 为备用并说明未被构建脚本选中。另记录资源来源、已由代码确认的行为和需要实现者开始前核对的点。不能用猜测填充阻塞项。

## 历史变更摘要（按需）

只有当会话存在相互冲突的旧需求时才加入；简述旧行为、何时废弃、当前最终行为，避免实现者误实现历史逻辑。
