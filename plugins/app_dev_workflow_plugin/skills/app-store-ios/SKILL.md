---
name: app-store-ios
description: Use when the user explicitly invokes $app-store-ios or asks to publish, release, submit for review, or upload an iOS build to App Store Connect through the project's Fastlane release lane.
---

# iOS 发版到 AppStore

## 目的

使用项目已有的 Fastlane `ios release` lane 完成 iOS App Store Connect 发版，创建版本时默认选择“审核通过后自动发布此版本”。这个 skill 负责收集双语 Release Note、解析输入、检查发布方式并调用现有 lane；除下述发布方式配置外，不修改 `Fastfile`，不改写文案，也不自动提交审核。

## 触发

在以下任一情况使用：

- 用户显式调用 `$app-store-ios`。
- 用户表达“发布”“发版”“提审”“上传 App Store”“发到 App Store Connect”等意图。

蒲公英提测使用项目已有的 beta lane 或对应的蒲公英 skill，不使用本 skill。

## 执行前检查

从当前项目根目录检查：

1. `fastlane/Fastfile` 存在。
2. 存在 `lane :release`。
3. `release` 接收并传递以下两个 snake_case 参数：
   - `chinese_release_note`
   - `english_release_note`

如果检查失败，报告缺少项并停止，不自行修改 Fastfile 或猜测其它 lane 名称。

## 默认发布方式

- 除非用户本次明确要求手动发布或定时发布，创建版本时必须使用“自动发布此版本”，即审核通过后自动发布，不设置最早发布日期。
- 检查 `release` 实际调用的 `upload_to_app_store` / `deliver` 及其配置，确保生效参数为 `automatic_release: true`，且没有生效的 `auto_release_date`。不能只把 `automatic_release:true` 追加为 lane 参数；现有 lane 未接收并传递时，该参数不会配置上传 action。
- 如果项目尚未配置自动发布，或现有配置为手动／定时发布，允许仅为本次发布方式对现有上传 action 或其配置作最小修改：显式设置 `automatic_release: true`，移除冲突的 `auto_release_date`。不要重写 lane 或修改其它构建、签名、上传逻辑；若无法确定实际生效配置，报告原因并停止。
- 发布方式需要随版本 metadata 写入 App Store Connect；如果现有流程跳过 metadata 或无法写入发布方式，报告阻碍并停止，不把本地配置当作远端已生效。
- 保持 `submit_for_review: false`：自动发布控制审核通过后的行为，不代表自动提交审核。不要为设置自动发布而开启自动提审。
- 上传后通过可用的 App Store Connect API 或页面回读目标版本，核对 `releaseType` 为 `AFTER_APPROVAL`（页面显示“自动发布此版本”）。无法回读时，在结果中明确说明发布方式尚未验证；若仍为手动或定时发布，报告未完成，不宣称设置成功。

参数说明见 [Fastlane upload_to_app_store 文档](https://docs.fastlane.tools/actions/upload_to_app_store/)。

## 收集 Release Note

每次发版都必须要求用户提供中文和英文两段 Release Note。如果当前用户消息没有同时包含两段内容，必须先使用 Codex 的输入提示工具请求输入并等待回复；如果该工具不可用，直接在输入框中提示用户按下面格式回复：

```text
中文 Realease Note：
新功能
* 支持手动打点功能
* 支持 VM33Pro 自动打点功能
漏洞修复
* 修复一些已知问题

英文 Realease Note：
New Features
* Support manual point marking  
* Support automatic point marking with VM33 Pro  
Bug Fixes
* Fix some known issues
```

规则：

- `中文 Realease Note：` 和 `英文 Realease Note：` 是分隔提示行，不属于上传内容；也识别拼写正确的 `中文 Release Note` 和 `英文 Release Note`。
- 两个分隔提示行都必须存在，且两段内容都不能为空；缺少任一段时要求用户重新输入。
- 标题匹配不区分英文字母大小写，同时识别全角或半角冒号；分隔行允许有首尾空格。
- 从中文分隔行之后开始读取中文内容，直到英文分隔行之前；英文内容从英文分隔行之后开始读取到输入结束。
- 保留内容中的换行、空行、缩进、连续空格、标点、星号和其它字符。不要翻译、润色、排序、合并或 Markdown 格式化。
- 只移除分隔提示行本身及解析它们所必需的结构性边界换行；不要对正文调用整体 `strip`、`trim` 或其它会改变正文的清理。
- 如果用户只给出一段、只给出标题、或把标题文字当成正文，要求重新输入，不使用默认文案。

## 调用 Fastlane

解析成功后，从项目根目录调用现有 lane：

```bash
bundle exec fastlane ios release \
  chinese_release_note:"<中文 Release Note 原文>" \
  english_release_note:"<英文 Release Note 原文>"
```

调用要求：

- 参数名必须是 `chinese_release_note` 和 `english_release_note`，不要改成 camelCase。
- 使用能保留多行文本、空格、标点和引号的安全参数传递方式；不要把用户文案拼成 Ruby 代码，也不要让 shell 对正文进行命令替换或再次展开。
- 不把正文写入 Fastfile、仓库中的固定 metadata 文件或日志。
- 不自动重跑失败的 lane。构建、上传或 Release Note 同步失败时，报告 Fastlane 的错误并停止。

## 结果报告

完成后简要报告：

- `fastlane ios release` 是否成功；
- 构建和 App Store Connect 上传是否成功；
- 双语 Release Note 是否已传递；
- 审核通过后的发布方式及远端核验结果；默认应为“审核通过后自动发布此版本”；
- 明确说明该 lane 默认 `submit_for_review: false`，因此不会自动提交审核，用户仍需在 App Store Connect 检查版本、选择构建并手动提交审核。
