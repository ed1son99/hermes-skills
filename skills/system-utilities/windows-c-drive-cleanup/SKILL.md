---
name: windows-c-drive-cleanup
description: Windows C 盘清理前的安全只读盘点、目录分类、删除风险等级判断和清理建议表生成。Use when the user asks to clean Windows C drive, free disk space, understand what is taking space, classify C drive files, decide what can or cannot be deleted, or produce a safe cleanup checklist/table for Windows.
triggers: [windows-c-drive-cleanup, 盘清理前, 的安全只, 读盘点, 目录分类, 删除风险, 等级判断, windows, use]
platforms: [claude-code, hermes, codex]
---

# Windows C 盘清理分级

## 核心原则

先盘点，再分类，再分级，最后才执行。默认只读，不删除、不移动、不修改文件。任何清理动作都必须让用户确认具体对象，不能一键全删，不能盲删系统目录。

当用户只是想了解 C 盘结构、哪些能删、哪些不能删、或要求做表格时，只输出分析和建议。只有用户明确要求执行清理，并确认具体项目后，才进入后续执行步骤。

## 只读盘点

优先运行 `scripts/inspect_c_drive.ps1` 获取基础数据。该脚本只统计空间和文件类型，不写入、不删除、不移动。

```powershell
.\scripts\inspect_c_drive.ps1
```

如果无法运行脚本，使用等价的只读 PowerShell 命令检查：

- C 盘总容量、已用空间、剩余空间
- C 盘根目录
- `C:\Windows`、`C:\Program Files`、`C:\Program Files (x86)`、`C:\ProgramData`、`C:\Users`
- 当前用户的 `Desktop`、`Documents`、`Downloads`、`Pictures`、`Videos`、`Music`
- 存在时检查 `C:\Autodesk`、`C:\Drivers`、`C:\Temp`、`C:\Intel`、`C:\CloudMusic`
- 当前用户目录中的常见文档、压缩包、图片、音视频文件类型体积

对访问失败目录静默跳过或说明权限限制。不要为了盘点而提权、修改权限或停止系统服务。

## 内容分类

将观察结果归入这些类别：

| 分类 | 代表位置 | 判断 |
|---|---|---|
| 系统核心 | `C:\Windows`、`C:\Recovery`、`System Volume Information`、`pagefile.sys` | 不手动删除 |
| 软件安装 | `C:\Program Files`、`C:\Program Files (x86)` | 通过系统设置卸载，不直接删目录 |
| 软件公共数据 | `C:\ProgramData`、部分 `AppData` | 谨慎判断，可能含授权、配置或数据库 |
| 用户资料 | `C:\Users\<user>\Desktop`、`Documents`、`Downloads` | 先整理和转移，不盲删 |
| 聊天文件 | `WeChat Files`、`xwechat_files` | 用软件存储管理或先备份 |
| 文献资料 | `Zotero\storage`、论文 PDF、课件 | 不直接破坏文献库结构 |
| 安装/驱动缓存 | `C:\Autodesk`、`C:\Drivers`、`C:\Intel` | 有清理潜力，需确认用途 |
| 临时/回收站 | `Temp`、`$Recycle.Bin`、错误报告、更新缓存 | 优先用系统工具清理 |
| 多媒体/压缩包 | `.mp4`、`.zip`、`.7z`、图片 | 适合删除重复项或转移到非系统盘 |

## 删除风险等级

用 A/B/C/D 四级判断风险，并在表格中明确建议。

| 等级 | 含义 | 操作建议 |
|---|---|---|
| A | 通常可删除 | 关闭相关软件后清理，或用系统清理工具 |
| B | 确认后可删除或转移 | 先看内容，重要文件转移到非系统盘 |
| C | 不建议手动删 | 使用系统工具、软件自带工具或先备份 |
| D | 不要删除 | 保持不动，交给 Windows 或对应软件管理 |

常见判定：

- A：回收站、用户临时文件、错误报告、空目录。
- B：安装包、压缩包、旧视频、重复课件、历史下载、已确认不用的厂商安装缓存。
- C：微信缓存、Zotero 附件、驱动目录、Windows 更新缓存、浏览器/软件缓存。
- D：`C:\Windows`、`C:\Program Files`、`C:\Program Files (x86)`、`C:\Recovery`、`System Volume Information`、`pagefile.sys`、`swapfile.sys`、整个 `C:\Users\<user>`。

## 输出格式

当用户要求分类、判断能不能删、或做表格时，输出这些内容：

1. C 盘几大类说明表。
2. 删除风险等级说明表。
3. 具体目录/文件类型风险表。
4. 当前机器优先处理清单。
5. 明确的“不要手动删除”列表。

默认使用这张明细表：

| 分类 | 位置/示例 | 当前观察 | 等级 | 是否能删除 | 建议 |
|---|---|---:|---|---|---|

优先级按“空间收益大、风险低”排序。通常先建议清理回收站和临时文件，再检查安装缓存和驱动包，再整理微信、桌面、文档、视频和压缩包，最后才考虑卸载软件。

## 执行保护

如果用户要求“直接清理”，先列出待清理项目和风险等级，并要求用户确认具体项目。不得执行以下动作，除非用户对具体路径作出明确确认且风险已说明：

- 删除系统目录或软件安装目录。
- 整体删除用户目录。
- 删除 Zotero、微信、浏览器等应用的数据目录。
- 调整虚拟内存、系统还原、Windows 更新组件。
- 使用递归删除命令清理模糊路径或通配符路径。

优先推荐安全工具：

- Windows “设置 > 系统 > 存储”
- “磁盘清理”
- 微信或其他聊天软件的存储管理
- 软件卸载程序或 “设置 > 应用”

每批清理后重新查看 C 盘剩余空间，并把释放空间和未处理风险反馈给用户。
