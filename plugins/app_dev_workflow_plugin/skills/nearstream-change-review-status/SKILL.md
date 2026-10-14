---
name: nearstream-change-review-status
description: "登录 Nearstream Strapi 后台，搜索 review 条目并将 version 字段替换为用户指定的版本号。触发示例：把 nearstream review 版本改成 x.x.x"
user-invocable: true
---

# Nearstream Change Review Status

修改 Nearstream Strapi 后台 Update Collection 中 review 条目的 version 字段。

保存成功后，根据版本号决定是否发送企微通知。通知脚本位于本 skill 目录的
`notify_wecom.py`，消息内容固定为：
`【iOS 端】+【Android 端】已提审，提审版本号：{目标版本号}`。

调用时用户须提供完整目标版本号（如 `999.5.2`），如果检测到用户没有填写，则弹窗向用户收集。

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

### 4. 搜索 review

1. 点击 `button "Search"` 展开搜索框
2. `textbox "Search for Update"` → type `review`
3. 按 Enter 发起搜索

### 5. 打开第一条记录

点击 `link "Edit item line 1"`。

### 6. 替换 version

1. 点击 `textbox "version *"`
2. 全选（Cmd+A）
3. type 用户提供的完整版本号

### 7. 保存

点击右上角 `button "Save"`，等 Save 按钮变回 disabled 表示保存成功。

### 8. 发送企微通知

仅在确认 Save 已成功后执行判断。将版本号按点分隔的数字逐段比较：

- 目标版本号 `< 999.999.999`：调用通知脚本：
  先将当前工作目录切换到本 skill 目录，也就是同时包含本 `SKILL.md` 和 `notify_wecom.py` 的目录，再执行：
  `python3 ./notify_wecom.py review-submitted --version "{目标版本号}"`
- 目标版本号 `>= 999.999.999`（包括 `999.999.999`）：不要调用脚本，也不要发送企微消息。

脚本自身也会执行同一阈值保护。不要假设 skill 安装在固定绝对路径；分享或安装到其他电脑后，始终以当前加载的 skill 目录为准。脚本返回成功后，确认输出包含 `sent review-submitted`；若跳过，确认输出包含 `skipped review-submitted`。通知失败时说明失败原因，不要把它报告为发送成功。

### 9. 退出

退出你打开的这个浏览器，千万不要退出其它浏览器。

### 10. 回复我
都执行完毕后回复我时，要体现出版本号原来是什么、修改后是什么。

## 注意事项

- 搜索结果预期只有 1 条；如有多条，停下来让用户确认操作哪一条
- Save 按钮在未修改时为 disabled，填入新值后才可点击
