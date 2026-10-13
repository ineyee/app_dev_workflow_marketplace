---
name: reverse-prd
description: Use when the user explicitly invokes reverse-prd or asks to 反推 PRD、生成 PRD、整理需求文档, or when existing code, screenshots, tests, logs, designs, or documents need to be turned into a Chinese, evidence-driven PRD for product, UI, development, and QA review.
metadata:
  cliHelp: "lark-cli wiki --help;lark-cli docs --help"
---

# 反推 PRD

把可观察的现有产品事实和会话中确认的目标，反向整理成可独立阅读、可评审、可实施、可验收的简体中文 Markdown PRD。PRD 是 UI、开发、测试共享的行为契约，不是代码说明、截图复述、聊天摘要或模块清单。

## 适用范围

适用于：

- 根据现有代码、页面、截图、录屏、测试、日志、旧 PRD 或接口文档反推产品行为；
- 需要将“当前实现是什么”整理成可交付 PRD，并标出目标、差距和未决项；
- 用户明确要求 PRD、产品需求说明、功能规格或跨角色验收文档。

只实现代码、排查 bug、做技术设计、制作 PDF 或只做视觉排版时，不要用本 skill 替代相应任务。

## 触发与输入范围

- 支持显式调用 `$reverse-prd`，也支持用户表达“反推 PRD”“生成 PRD”“整理成需求文档”等同类意图时自动触发；`agents/openai.yaml` 保持 `allow_implicit_invocation: true`。
- 先判断用户是否给出了本次 PRD 的具体主题、功能名、模块名、问题描述或范围词。只写“生成 PRD”“反推一下 PRD”而没有主题时，将当前可见会话中已经落地的全部需求作为同一份 PRD 的需求范围；纳入用户明确提出或确认的目标，排除闲聊、纯状态询问和未形成决策的猜测。
- 用户给出具体主题或提示词时，只围绕该提示词在项目内定向取证：先定位项目根目录，再使用 `rg`/文件清单搜索相关模块、页面、资源、测试、文档和调用链，之后再扩展到必要的关联实现。不得直接把整个仓库无差别写入 PRD。
- 用户提供多份文档、截图、日志或设计资料时，将它们登记为同一份证据集合，去重、按时间和证据类型整合成一份完整 PRD；区分最终用户目标、可验证的实现现状和旧资料中的历史要求，在需求演进账本中保留冲突、被废弃内容和未决项。云端交付时只创建并上传这一份 PRD，不按附件数量拆分多篇。
- 用户明确要求“生成本地文档/保存到本地/导出本地 PRD”时，进入本地交付模式：先将完整 Markdown 写入本地文件（未指定路径时使用当前项目根目录的 `docs/prd/`，文件名使用 PRD 标题生成的安全文件名），完成文件存在性和正文完整性检查后交付；本次不列知识库、不创建或更新飞书文档、不回读飞书、不执行企微通知。用户只要求聊天草稿时仍不创建文件。
- 用户没有明确要求本地文档时，默认进入飞书团队知识库交付模式，并按下方知识库、回读和企微通知流程执行。

## 产物契约

- 正文先按 **Markdown** 编写，默认转换写入用户选择的飞书团队知识库在线 `docx` 文档，不在电脑上保留 `.md` 文件。
- 除非用户另行要求，不生成本地 PDF、Word、PPT、HTML 或其他格式，不调用 PDF 生成/排版流程；飞书知识库在线 `docx` 节点仅作为 Markdown 正文的承载文档。
- 正文使用简体中文；代码路径、类名、接口名、资源 key、错误码可保留原文。
- 用户明确只要聊天中的草稿时，直接输出 Markdown，不调用知识库写入命令。
- 用户要求生成或交付 PRD 时，先在内存中完成 Markdown；只有默认云端交付模式才进入“选择知识库并上传”流程，本地交付模式按“本地文件清理与本地交付例外”执行。

## 飞书知识库交付流程（仅默认云端交付模式）

仅当用户没有明确要求本地文档，且没有选择“只要聊天草稿”时，才执行本节。此时读取并遵循 `lark-shared`、`lark-wiki` 和 `lark-doc`；`lark-cli` 只在云端模式必需。PRD 正文完成并通过本技能的证据审计后，必须按以下顺序交付；不要在用户未选择知识库前创建节点或写入正文。

### 1. 获取并展示知识库

使用用户身份列出当前可访问的全部知识库：

```bash
lark-cli wiki +space-list \
  --page-all \
  --page-limit 0 \
  --as user \
  --format json
```

解析 JSON 中的 `data.spaces[]`，使用可用的用户输入工具弹出选择框，让用户从候选项中选择。每个选项至少展示 `name` 和 `space_id`；可同时展示 `visibility` 和 `description`。若工具限制选项数量，就让用户在输入框填写列出的 `space_id`，然后与返回列表精确匹配。没有候选知识库、列表分页失败或用户取消选择时，停止写入并说明原因。

知识库选择是一次性确认：选择结果必须映射到返回的真实 `space_id`，不能把名称、URL、node token 或 `my_library` 当作团队知识库 ID，也不能自动替用户猜选。

### 2. 在一级目录创建文档节点

用户选择后，使用所选 `space_id` 在知识库根目录创建一个 `docx` 节点：

```bash
lark-cli wiki +node-create \
  --space-id <selected_space_id> \
  --title "<PRD 标题>" \
  --obj-type docx \
  --as user \
  --format json
```

不要传 `--parent-node-token`，这样文档直接创建在该知识库的一级目录。标题应来自 PRD 的功能名称；创建失败时停止，不创建第二个替代节点。

### 3. 写入 Markdown 正文

从 `+node-create` 的返回值读取 `obj_token`（也可使用返回的 Wiki URL），然后使用 `lark-doc` 的文档更新命令追加正文：

```bash
lark-cli docs +update \
  --doc <obj_token> \
  --command append \
  --doc-format markdown \
  --content - \
  --as user \
  --format json
```

将内存中的完整 PRD Markdown 通过 stdin 传给 `--content -`。优先使用不展开 Markdown 中 shell 特殊字符的传输方式，避免为了上传而生成本地 `.md` 文件。Markdown 中的特殊字符必须遵循 `lark-doc` 的转义规则。

### 4. 回读验证并报告结果

写入返回成功后，回读同一个文档并确认标题、关键章节和正文存在：

```bash
lark-cli docs +fetch \
  --doc <obj_token> \
  --detail with-ids \
  --as user \
  --format json
```

只有 `+update` 成功且 `+fetch` 能核对出正文时，才向用户报告上传成功，并提供知识库 Wiki URL、文档标题和所选知识库名称。若返回 `partial_success`、警告、回读失败或正文不完整，明确报告失败点，不声称上传完成。

### 4a. 飞书 PRD 验证成功后的企微通知

回读同一文档并确认标题、关键章节和正文存在后，调用**本次反推所针对的项目仓库根目录**中的通知脚本。先用 `git -C <项目路径> rev-parse --show-toplevel` 确认根目录；脚本必须位于该目录的 `notify_wecom.py`，不能调用 skill 安装目录、另一个项目或当前目录之外的副本：

```bash
PROJECT_ROOT="$(git -C "/本次反推项目的绝对路径" rev-parse --show-toplevel)"
python3 "$PROJECT_ROOT/notify_wecom.py" \
  feishu-prd \
  --title "<PRD 标题>" \
  --url "<飞书文档链接>"
```

脚本入口为项目根目录的 `notify_wecom.py`，通知方法按用途扩展；当前方法为 `feishu-prd`。iOS 与 Android 使用相同的纯 Python 标准库脚本，各项目根目录各放一份，并分别配置各自要通知的企微群。Webhook 和手机号 @ 列表配置在脚本顶部，也可用 `WECOM_WEBHOOK`、`WECOM_MENTIONED_MOBILES` 环境变量覆盖。不要把真实 webhook 写入公开仓库或输出到日志。

若项目根目录没有 `notify_wecom.py`、脚本不是当前项目的副本或 webhook 未配置，停止企微发送并明确报告“飞书文档已上传并验证，企微通知未执行/失败”；不要回退到 skill 目录或其他仓库中的脚本。

企微消息必须是文本消息，正文格式为 `《<飞书 PRD 标题>》：<飞书文档链接>`。手机号只放入企微接口的 `mentioned_mobile_list`，不要把手机号或姓名 @ 文本拼到正文中。

通知脚本失败时，不得撤销或重复创建已验证的飞书文档；应报告“飞书文档已上传并验证，企微通知失败”，保留文档链接，并允许用户单独重试通知脚本。没有用户授权或 webhook 未配置时，不得自行发送或猜测目标群。

### 5. 本地文件清理与本地交付例外

- 默认云端交付不创建本地 PRD 文件，Markdown 只存在于内存和飞书文档中。
- 进入“本地交付模式”时，用户明确要求保留的 PRD 文件不是临时文件：按用户指定路径保存；未指定路径时保存到当前项目根目录的 `docs/prd/`，并在最终回复中提供文件路径。此模式不执行任何飞书上传或企微通知。
- 如果因命令行长度、工具限制或其他必要原因创建了临时 `.md` 文件，使用后删除并确认删除结果；上传失败时也不留下本地 PRD 文件，应保留内存中的正文供本轮重试，并报告失败点。
- 云端交付的临时文件不得写入主仓库的 `docs/prd/`；只有用户明确要求本地副本时才保留本地文件。

### 常见错误处理

- `lark-cli` 未安装、未登录或缺少 scope：停止写入，提示用户先完成对应的 CLI 安装/登录/授权，不改用未验证的原生 API。
- 知识库列表有多页：必须使用 `--page-all`（必要时 `--page-limit 0`）完整收集后再让用户选择。
- `+node-create` 成功但 `docs +update` 失败：保留已创建节点，报告节点 URL，允许用户重试正文写入，不重复创建节点。
- `docs +update` 成功但 `+fetch` 失败：不要报告“已验证”，保留文档 URL 并说明需要重新回读确认。

## 反推原则

1. **先取证，后下结论。** 代码、截图、测试和旧文档只证明它们直接支持的事实。
2. **区分现状、目标和差距。** 当前实现不是自动目标；用户最终确认的目标优先于旧实现。
3. **可观察行为优先。** 描述用户看到的页面、状态、按钮、提示、导航、数据变化和失败结果，不用“按设计实现”替代细节。
4. **未知就标记。** 会改变 UI、开发或测试结果的缺口写成 `unresolved` 并生成 `B-*`，不能用常识补全。
5. **证据可追溯。** 每条关键结论使用 `E-*`；每条功能、UI、异常、文案和非功能要求都要能追溯到证据或明确的会话决策。
6. **最终行为可验收。** 每个 `AC-*` 必须引用需求编号、测试 CASE 和证据；不写只有“支持”“正常”“适当”“尽快”的空泛要求。

## 工作流（必须按顺序）

### 1. 建立证据清单

读取完整可见会话和可用附件，按以下类型登记：

- `session-confirmed`：用户明确提出或确认的目标；
- `attachment-observed`：截图、录屏或页面直接观察到的 UI；不能据此推断底层协议；
- `verified-code`：代码、Git diff、构建、测试或命令直接证实的现状；
- `verified-doc`：文档记录且没有被更新证据反驳；
- `platform-equivalent`：不同平台均有证据证明用户可观察结果等价；
- `assumption`：不改变交付结果、且写明依据和风险的临时假设；
- `unresolved`：证据不足、冲突未裁决或外部契约未验证。

每条证据使用 `E-编号`，记录来源、相对路径或附件名、类/方法/截图区域、日期、命令及结果摘要。上下文或附件不完整时登记缺失范围并生成 `B-*`，不能声称已完整读取。

### 2. 反推现状并建立需求演进账本

按时间顺序记录：

`L-编号 | 轮次/日期 | 原始要求或观察 | 证据 E-* | 对 UI/开发/测试的影响 | 状态 | 当前决策`

状态只能是 `final`、`deprecated`、`assumption`、`unresolved`。后续用户说“改成/现在期望/不再/继续”时，旧条目标记 `deprecated`，并把新行为写入最终决策。代码现状只作为兼容约束或差距证据，不覆盖用户目标。

### 3. 还原入口、状态和异常

为每个入口、角色和页面回答：前置条件、触发操作、可观察 UI、系统状态、下一步、成功、失败、取消、返回、重试、超时、权限拒绝、后台恢复、重复点击和页面销毁结果。

网络、设备或系统设置功能还要核对设备热点/手机热点/普通 Wi-Fi、SSID 与安全类型、蜂窝路径、无互联网但局域网可用、权限弹窗、设置回跳、设备连接生命周期和媒体清理；无证据的项写“未确认”。

### 4. 盘点实现边界

只读取有助于解释兼容约束或行为差距的页面、状态、资源、通知、导航、网络 API、连接生命周期、测试和构建命令。不要把类名、文件名、接口、超时、埋点或平台能力写成未经证据支持的产品契约。

### 5. 编写并审计 Markdown PRD

读取并遵循：

- [references/prd-template.md](references/prd-template.md)：可按复杂度裁剪的内容结构、编号和追踪矩阵；
- [references/evidence-and-ambiguity-rules.md](references/evidence-and-ambiguity-rules.md)：证据、阻塞和网络检查规则。

使用稳定且不可复用的 `FR/UI/ERR/LOC/NFR/AC-*` 编号。交付前检查：文档基本信息、背景与目标、用户与场景、范围与优先级、业务流程、功能和数据规则、页面交互、非功能、验收、上线安排，以及最终行为、废弃行为、差距和阻塞项。

## 输出状态

默认 front matter：

```yaml
---
document_type: prd
status: draft
verification: product-review-required
last_updated: YYYY-MM-DD
---
```

无阻塞时使用 `status: ready-for-cross-functional-review`；有影响交付的 `unresolved` 时使用 `status: blocked`、`verification: clarification-required`，并在正文最前列出 `B-*` 的影响、决策人、解除条件和临时假设（如有）。

## 不可越过的边界

- 不把截图当协议证据，不把旧文档当当前事实。
- 不把“按 iOS/Android/设计稿实现”当作需求；写跨平台可观察行为和已证实集成契约。
- 不用“支持多语言”替代每种语言的文案、资源 key、占位符和验收。
- 不遗漏入口来源、状态互斥、失败重试、权限、前后台、重复操作、数据保留和日志脱敏。
- 不修改业务代码、测试代码、设计稿、项目总览、Flutter/Dart、submodule 指针或其他仓库文件。
- 不为了显得详细而虚构数据库、API、错误码、协议、埋点或性能指标；未知写 `unresolved` 和核对动作。
