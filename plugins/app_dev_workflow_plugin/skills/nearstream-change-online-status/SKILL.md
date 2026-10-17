---
name: nearstream-change-online-status
description: "Use when the Nearstream Strapi online Update entry must be changed to a specified version and published, with Chinese and English release notes inserted before the existing content and a WeCom online-release notification sent after publishing."
user-invocable: true
---

# Nearstream Change Online Status

修改 Nearstream Strapi 后台 Update Collection 中 review 条目的 version 字段。

调用时用户须提供完整目标版本号（如 `999.5.2`）、中文发版内容、英文发版内容，如果检测到用户没有填写，则弹窗向用户收集。

发布成功后，必须调用本 skill 目录中的 `notify_wecom.py` 发送企微通知。通知脚本只提供 `online-status` 命令，通知内容格式为：

```text
【iOS 端】+【Android 端】已上线，上线版本号：{目标版本号}
中文 Release Note：
{本次中文发版内容}
英文 Release Note：
{本次英文发版内容}
```

Release Note 使用本次写入 descriptions 的中英文发版内容原文，保留 Markdown 和换行，不包含历史版本内容，也不包含输入时的分隔提示行或 `-----------`。通知通过原有手机号提及列表 @人员。

通知脚本使用与 review 提审通知相同的 webhook、手机号提及和版本阈值保护；目标版本号低于 `999.999.999` 才发送，达到或超过该值时跳过发送。

## 账号信息

- Email: `developer@auditoryworks.tech`
- Password: `Disc1234`

## 步骤

### 1. 打开登录页

用 `browser` 工具（openclaw 管理模式，不需要 `profile="user"`）打开：

- URL: `http://mosapi.auditoryworks.co:1339/admin/auth/login?redirectTo=%2Fcontent-manager%2FcollectionType%2Fapi%3A%3Aupdate.update%3Fpage%3D1%26pageSize%3D10%26sort%3Dslug%3AASC`
- label: `nearstream-login`

### 2. 登录

snapshot 确认表单加载后：

1. `textbox "Email *"` → type 邮箱
2. `textbox "Password *"` → type 密码
3. 点击 `button "Login"`

### 3. 进入 Update

点击左侧 `link "Content Manager"`，再点击 `link "Update"`。

### 4. 搜索 NearStream-Multicam

1. 点击 `button "Search"` 展开搜索框
2. `textbox "Search for Update"` → type `NearStream-Multicam`
3. 按 Enter 发起搜索

### 5. 复制 ID 值最大的那条搜索记录（必须生成独立新记录）

1. 查询出搜索结果后，读取每一行的数字 ID，按数值比较并选择 **ID 最大的那一行**，同时记下原记录的 ID、version 和 slug。

2. 在已选中的最大 ID 行内部定位双方块复制按钮并点击。先取得该行的可访问性容器（row），再在该 row 的后代元素中查找按钮：按钮名称通常匹配 `Duplicate item line <动态行号>`，或按钮包含双方块复制图标。行号必须从当前 row 动态读取；**禁止写死 `Duplicate item line 3`、禁止按全页面第几个按钮定位、禁止使用屏幕坐标或固定像素点击**。复制按钮必须是该 row 内编辑铅笔右侧的双方块图标，不能点击编辑链接或其他行的按钮。若按钮名称中的行号变化，只要仍位于目标 ID 的 row 内就应点击该按钮。

3. 等待复制后的详情表单加载。此时 URL 可能仍显示原记录 ID，这是复制草稿状态，不代表新记录已经创建。

4. **复制落库步骤（不可跳过）**：不要先修改 version、slug 或 descriptions；直接点击右上角 `Save`，等待保存完成。这个第一次 Save 才会把复制草稿保存为独立的新记录。

5. **复制成功校验（硬门槛）**：第一次 Save 完成后，核对详情页 URL/页面中的记录 ID、slug 或其他唯一标识。新记录的 ID 必须与刚才记下的最大原 ID 不同；原记录仍需保留。

6. 如果第一次 Save 后 URL 仍是原 ID、页面没有显示新记录 ID、保存失败，或无法证明 ID 已变化：立即停止，不得修改任何字段，不得再次 Save/Publish。返回列表确认原记录未被改变，再重新执行 Duplicate 流程。

7. 只有确认第一次 Save 已生成新 ID 后，才可以修改 version、slug、descriptions，并进行第二次 Save。

### 6. 替换 version

仅在第 5 步确认第一次 Save 已生成新 ID 后执行。

1. 点击 `textbox "version *"`
2. 全选（Cmd+A）
3. type 用户提供的完整版本号，比如“999.5.2”

### 7. 替换 slug

仅在第 5 步确认第一次 Save 已生成新 ID 后执行。

1. 点击 `textbox "slug *"`

2. 全选（Cmd+A）

3. type "NearStream-Multicam-用户提供的完整版本号"，比如“NearStream-Multicam-999.5.2”

### 8. 修改英文发版内容

1. 选中 descriptions 里 locale 为 en-us 的 entry
2. 把我发你的“英文发版内容”插入到当前 entry 的 content 的最前面，注意是最前面

### 9. 修改中文发版内容

1. 选中 descriptions 里 locale 为 zh-cn 的 entry

2. 把我发你的“中文发版内容”插入到当前 entry 的 content 的最前面，注意是最前面。发版内容是“-----------”中间的所有 markdown 内容，包括 “***” 以及 “\*\*\*” 后面的空行

   ```
   中文发版内容：
   -----------
   ## v3.5.2
   
   #### 新功能
   * 支持 UAC/UVC 设备接入（如 USB 摄像头、麦克风）。支持范围：
   机型 : iPhone 15 及后续机型。
   系统 : iOS 13 / iPadOS 13 及以上。
   
   ***
   
   -----------
   
   英文发版内容：
   -----------
   ## v3.4.0
   
   #### New Features
   * Support UAC/UVC device access​ (e.g., USB cameras, microphones). Support Scope：
   Model: iPhone 15 and later
   OS: iOS 13 / iPadOS 13 and aboveio tracking
   
   ***
   
   -----------
   ```

### 10. 保存

点击右上角 `button "Save"`，等 Save 按钮变回 disabled 表示保存成功。

第二次 Save 后回到列表再次确认：原记录的 ID 和 version 仍未改变，并且新记录使用新的 ID 和目标 version。若原记录被改成目标 version，立即停止发布并报告复制校验失败。

### 11. 发布

点击右上角 `button "Publish"`，等待发布成功。

### 12. 发布成功后发送企微通知

仅在确认页面显示发布成功后执行。将本次写入 descriptions 的中英文发版内容分别原样保存为两个 UTF-8 临时文件，使用文件写入工具或 Python 文件 API，避免通过 shell 插值写入 Markdown。两段内容均不能为空。

将当前工作目录切换到本 skill 目录，也就是同时包含本 `SKILL.md` 和 `notify_wecom.py` 的目录，再执行（文件参数替换为实际临时文件路径）：

```bash
python3 ./notify_wecom.py online-status --version "{目标版本号}" \
  --chinese-release-note-file "{中文发版内容临时文件路径}" \
  --english-release-note-file "{英文发版内容临时文件路径}"
```

- 目标版本号 `< 999.999.999`：确认脚本输出包含 `sent online-status`，再继续后续步骤。
- 目标版本号 `>= 999.999.999`（包括 `999.999.999`）：脚本输出应包含 `skipped online-status`，不要把它报告为发送成功。
- 如果脚本返回非零退出码或输出 `notify_wecom: ...` 错误：记录错误原因，并明确告知用户线上发布已成功但企微通知失败。

脚本执行结束后清理本次创建的临时文件。

不要假设 skill 安装在固定绝对路径；始终从当前加载的 skill 目录执行脚本。

### 13. 退出

退出你打开的这个浏览器，千万不要退出其它浏览器。

### 14. 回复我

都执行完毕后回复我时，要体现出版本号原来是什么、修改后是什么。中英文发版内里各自最新两个版本的发版内容也发给我，从 content 里截取出来原样发给我就行。

## 注意事项

- Save 按钮在未修改时为 disabled，填入新值后才可点击
- Publish 按钮在未修改时为 disabled，Save 后才可点击
