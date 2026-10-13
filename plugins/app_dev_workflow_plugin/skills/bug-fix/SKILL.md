---
name: bug-fix
description: Use when the user expresses intent to fix, resolve, or修复 a bug/缺陷, especially when they provide a Feishu Project issue link; require a valid Feishu bug link before starting the repair workflow.
---

# 修复 BUG

## 触发条件

自动触发本 Skill 的用户意图包括：

- “修复这个 bug”“修复缺陷”“解决这个问题”；
- “fix bug”“resolve issue”“fix defect”；
- “帮我改一下这个飞书缺陷”或同义表达。

用户只是在讨论 Bug、分析原因、查询状态或询问流程时，不触发修复流程。

## 飞书 Bug 链接是入口条件

修复流程必须从飞书项目缺陷链接开始。接受以下形式：

```text
https://project.feishu.cn/<simple_name>/issue/detail/<work_item_id>
```

链接可以带查询参数，也可以作为 Markdown 链接出现，例如：

```markdown
[打开缺陷](https://project.feishu.cn/nbwskj/issue/detail/7133039361?parentUrl=%2Fnbwskj%2Fissue%2Fhomepage)
```

从 Markdown 中取链接目标 URL，而不是把显示文本当作 URL。不要自行从 URL 字符串截取参数；获得链接后使用：

```bash
meegle url decode --url "<飞书缺陷链接>" --format json
```

只有 `url_kind` 为 `workitem_detail` 时，才继续执行缺陷修复流程。

## 缺少链接时的响应

当用户表达了修复 Bug 的意图，但消息中没有可识别的 `project.feishu.cn/.../issue/detail/...` 链接时：

1. 不修改代码；
2. 不执行 Git 提交、推送或其他外部写操作；
3. 不猜测缺陷编号、项目空间或缺陷内容；
4. 优先使用 Codex 的结构化用户输入工具，弹出一个输入框要求用户填写飞书项目缺陷链接；
5. 如果当前运行环境没有可用的结构化输入工具，再使用普通文字提示要求用户提供链接。

结构化输入框的标题和问题建议使用：

```text
标题：飞书 Bug 链接
问题：请粘贴要修复的飞书项目缺陷链接
```

输入框只收集链接，不要在用户填写前执行 `meegle` 查询、修改代码或执行 Git 操作。收到输入后，先校验它是否包含 `https://project.feishu.cn/`，再执行 `meegle url decode`；校验失败时重新请求正确链接。

使用简短提示：

```text
请先发送这个 Bug 在飞书项目中的缺陷链接，例如：
https://project.feishu.cn/nbwskj/issue/detail/7133039361
收到链接后，我再读取缺陷详情并开始修复。
```

如果用户只提供了 Bug 编号、标题、截图或复制的缺陷描述，也仍然先索要飞书缺陷链接。

## 已提供链接时

不要再次索要链接。先按 Meegle Skill 的授权检查和 URL 解析规则处理链接，再进入后续修复步骤。后续步骤包括读取缺陷详情、确认用户允许的代码修改范围，以及在测试通过后执行用户明确授权的 Git 和飞书更新操作。

## 修复期望是必填输入

完成前面的两项检查后：

1. 已确认用户表达了修复 Bug 的意图；
2. 已获得并成功解析飞书项目缺陷链接，且 `url_kind=workitem_detail`；

检查用户原始提示词中是否包含明确的“修复期望”。修复期望是用户希望修复后达到的行为或验收结果，例如：

- “开球选手选择模块需要按设计图展示并可操作”；
- “空响应时页面应显示空状态，不应崩溃”；
- “点击保存后应保留已选择的选手”。

缺陷描述、复现步骤、标题、截图或“请修复这个 Bug”本身不等于修复期望。不要根据这些内容自行推断期望。

### 已包含修复期望

保留用户原话作为 `repair_expectation`，只在必要时做格式整理，不改变其含义。后续分析、修改和测试都必须围绕这个期望进行，并在完成前检查实现是否满足它。

### 未包含修复期望

不要开始修改代码，也不要提交 Git 或写入飞书。优先弹出结构化输入框：

```text
标题：修复期望
问题：修复这个 Bug 后，期望达到什么结果？请描述正确行为或验收标准。
```

输入框只收集修复期望。用户提交后，将答案保存为 `repair_expectation`，并把它作为后续修复和验证的必需条件。

如果当前环境没有结构化输入工具，再使用普通文字询问：

```text
请补充这个 Bug 的修复期望：修复后应该表现为什么正确行为？
```

如果用户的回答仍然只有“修复一下”“按正常逻辑处理”等无法验收的表述，继续要求具体的正确行为或验收标准，不要猜测。

## 获取并展示缺陷上下文

当 `repair_expectation` 已收集且具体可验收后，才执行 Meegle 查询。只获取以下两项业务内容：

1. 缺陷名称（工作项名称）；
2. 缺陷详细描述字段（当前空间中名称为“缺陷详细描述”的字段）。

查询时仍需执行 Meegle 的授权检查、URL 解析和空间 key 校验。不要自行从 URL 截取参数。先通过工作项类型元数据找到“缺陷详细描述”的真实 field key，再用 `workitem get` 读取该字段；不要假设所有空间都使用同一个 field key。

可以使用以下命令模式，具体参数以 `meegle inspect` 返回的当前 schema 为准：

```bash
meegle url decode --url "<飞书缺陷链接>" --format json
meegle project search --project-key "<simple_name>" --format json
meegle workitem meta-fields \
  --project-key "<project_key>" \
  --work-item-type "<work_item_type>" \
  --field-query "缺陷详细描述" \
  --format json
meegle workitem get \
  --project-key "<project_key>" \
  --work-item-id "<work_item_id>" \
  --fields "<description_field_key>" \
  --format json
```

如果 CLI 的 `workitem get` 默认已经返回缺陷名称，则从 `work_item_attribute.work_item_name` 读取；缺陷详细描述从对应字段的 `value` 读取。只保留这两项内容用于后续分析。

### 必须向用户展示

读取成功后，先向用户展示，不要直接进入代码修改或 Git 操作。展示格式：

```markdown
## 已读取的飞书缺陷

**缺陷名称**

<work_item_name>

**缺陷详细描述**

<description_value>

**修复期望**

<repair_expectation>
```

如果名称或缺陷详细描述为空、字段未找到、查询结果无法确认，停止并告诉用户缺失项；不要用附件、标题或自行推断内容补齐。

### 附件处理边界

不要下载、解析或自动查看飞书缺陷附件。用户会自行查看附件并在修复期望中描述相关要求。附件 URL、file token 和其他未请求字段不进入修复上下文。

### 修复上下文

后续分析和代码修改只能基于以下三项已确认信息：

- 缺陷名称；
- 缺陷详细描述；
- 用户提供的修复期望。

将三项信息一起用于定位原因、制定修改方案和设计验证步骤；不得把缺陷描述中的“应该如何修复”替换为用户明确提供的修复期望，也不得在缺少修复期望时自行补全。

## 代码修改后的人工验证门禁

在完成代码修改和必要的本地测试后，**不得立即执行 Git commit、push、状态流转或评论**。先向用户展示修改摘要和测试结果，并弹出人工验证交互。

交互内容：

```text
标题：修复完成，请人工验证
问题：请验证当前修复是否符合修复期望。若未通过，请输入具体问题或下一步修复要求。
选项：继续修复、验证通过
```

如果当前界面提供可同时提交文本和选择结果、并支持条件禁用按钮的表单，就将文本输入绑定为 `validation_feedback`：

- 选择“继续修复”时，`validation_feedback` 必须是非空、具体的反馈；用它指导下一轮修改；
- 选择“验证通过”时，允许反馈为空，但必须保留当前修复期望和测试结果；
- 用户未填写 `validation_feedback` 时禁用“继续修复”；
- 当前 Codex 的结构化提问工具若只能在“选择选项”和“输入自由文本”之间二选一，则先展示“继续修复 / 验证通过”选项；用户选择“继续修复”后，再弹出输入框收集 `validation_feedback`。反馈为空时保持等待并重新询问，不进入下一轮修改；
- 用户只输入“继续”“不通过”等无法指导修改的内容时，不得继续盲改，应要求具体失败现象、期望行为或复现步骤。

### 继续修复循环

用户选择“继续修复”后：

1. 读取 `validation_feedback`；
2. 根据缺陷名称、缺陷详细描述、原始修复期望和本轮人工反馈修改代码；
3. 重新运行相关测试；
4. 再次弹出同一个“修复完成，请人工验证”交互；
5. 在用户选择“验证通过”之前，禁止执行 Git commit、push、飞书状态更新和评论。

这个循环可以重复多次。用户选择“验证通过”后，才进入提交确认阶段。

## 提交与飞书更新确认

用户选择“验证通过”后，弹出第二个确认交互：

```text
标题：是否自动提交代码 + 切换 BUG 状态 + 评论 BUG
问题：验证已通过，是否执行 Git commit、将飞书 Bug 流转到 Resolved，并添加版本评论？
选项：暂不、确定
```

### 选择“暂不”

立即结束当前自动化流程：

- 不执行 Git commit 或 push；
- 不修改飞书 Bug 状态；
- 不添加飞书评论；
- 向用户报告代码仍保留在当前工作区，等待用户后续自行处理。

### 选择“确定”

按以下顺序执行：

1. 读取当前 Git 状态，识别并暂不暂存与本次 Bug 无关的现有修改。确认项目版本来源唯一、版本为 `major.minor.patch`，并计算 patch 加 1 后的评论版本；如果当前项目有多个版本来源且无法确定目标，先向用户询问，暂不提交或更新飞书；
2. 生成唯一 commit message，格式必须为：

   ```text
   fix: <缺陷名称>
   ```

   `<缺陷名称>` 必须使用前面从飞书读取并展示的原始工作项名称，不得自行改写成其他标题；
3. 仅暂存本次 Bug 修复涉及的文件，执行 `git commit -m "fix: <缺陷名称>"`；
4. commit 成功后，将当前分支 push 到对应远程仓库。优先执行 `git push`；如果当前分支尚无上游分支，在确认远程仓库和当前分支后执行 `git push -u origin <当前分支名>`。不创建新分支或 Pull Request；
5. push 成功后，查询当前 Bug 的可用状态流转。当前已知的合法路线是：

   ```text
   New bug → Affirm → IN PROGRESS → RESOLVED
   Reopened → IN PROGRESS → RESOLVED
   ```

   `New bug` 和 `Reopened` 都可能是起始状态。每一步必须以 Meegle 实时返回的 transition 为准，不能直接硬编码 transition ID；
6. 如果当前状态不能直接到 `RESOLVED`，按照匹配的已知路线逐步查询并执行合法 transition。每一步流转后回读确认状态；如果实时可选状态与路线不符，或需要额外业务选择，停止并询问用户，不得盲目流转；
7. 直到状态实际变为名称为 `RESOLVED` 的状态后停止。若没有可用 transition、目标名称不明确或流转失败，停止后报告原因，不得伪造已解决；
8. 项目版本优先从代码仓库实际使用的版本配置读取（例如 `pubspec.yaml`、`package.json`、`build.gradle`、`gradle.properties`、`Info.plist` 或项目既有版本脚本），不要从飞书截图、附件或猜测得到版本。将 patch 位加 1，例如当前版本 `2.9.8`，评论版本为 `v2.9.9`；不要为评论而修改项目版本文件；
9. 添加唯一评论，格式为：

   ```text
   已修复，见 v<major.minor.patch>
   ```

10. 向用户报告 commit hash、push 结果、实际状态流转结果和评论版本。

飞书状态更新和评论只有在用户选择“确定”、Git commit 成功、push 成功、版本号确认成功后才能执行。commit 成功但 push 失败时，必须停止，不得更新飞书状态或添加“已修复”评论；明确报告 commit hash、push 错误和未执行的飞书步骤。状态流转或评论失败时，也必须明确报告已完成和未完成的步骤，不能声称全流程完成。
