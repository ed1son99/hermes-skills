# Skills Catalog

通用跨平台 Agent Skill 目录 — 222 个可复用的 AI Agent 技能，覆盖 39 个分类。  
兼容 **Claude Code** / **Hermes** / **Codex (OpenAI)** / **Cursor** 等多平台。

## 通用架构

每个 Skill 采用统一跨平台格式，一次维护，多 Agent 通用：

```
skills/<category>/<name>/
├── SKILL.md                  # 通用核心（所有平台共享）
├── mounts/                   # 各平台挂载配置
│   ├── claude-code.yaml      # Claude Code: category
│   ├── hermes.yaml           # Hermes: version, author, license, tags, ...
│   └── codex.yaml            # Codex: interface, policy
├── scripts/                  # 辅助脚本 (Python/Bash/PS1)
├── references/               # API 文档、备忘单
└── templates/                # 模板文件
```

### SKILL.md 统一格式

```yaml
---
name: <skill-name>
description: <universal description>
triggers: [keyword1, keyword2, ...]       # 通用触发词
platforms: [claude-code, hermes, codex]   # 可用平台
---

# <skill-name>

<通用 Markdown 工作流指令 — 所有平台共享>
```

## 分类总览

| 分类 | 数量 | 说明 |
|---|---|---|
| **film-making** | 4 | 影视制作：分镜导演、剧本创作、运镜设计、Seedance 视频生成 |
| **ai-media** | 2 | AI 媒体生成：LibTV 图片/视频生成与编辑 |
| **design-system** | 3 | 设计系统：前端 UI 精修、设计系统工程化 |
| **creative** | 19 | 创意设计：ASCII 艺术/视频、Canvas 3D/2D、Manim、p5.js、ComfyUI、信息图、音乐等 |
| **development-methodology** | 6 | 开发方法论：TDD、规格驱动、源码驱动、质疑驱动、增量实现、需求访谈 |
| **architecture-planning** | 5 | 架构规划：任务拆解、ADR、上下文工程、API 设计、弃用迁移 |
| **code-quality** | 5 | 代码质量：多维度审查、简化、调试、安全加固、性能优化 |
| **devops-release** | 4 | DevOps 与发布：Git 工作流、上线部署、CI/CD、浏览器测试 |
| **cli-commands** | 7 | CLI 命令：代码审查、简化、验证、启动、循环、初始化、安全审查 |
| **claude-config** | 5 | Claude 配置：设置管理、快捷键、API 参考、权限优化、Skill 发现 |
| **meta-tools** | 3 | 元工具：知识图谱、想法精炼、深度研究 |
| **session-management** | 6 | 会话管理：开始、结束、列表、状态、帮助、更新 |
| **workflow-automation** | 7 | 工作流自动化：代码审查、TODO 管理、Prompt 工程、交接文档 |
| **plugin-development** | 1 | 开发插件：项目脚手架 |
| **plugin-documentation** | 1 | 文档插件：自动文档生成 |
| **plugin-operations** | 3 | 运维插件：部署验证、健康检查、事件响应 |
| **plugin-performance** | 2 | 性能插件：负载测试、性能分析 |
| **plugin-quality** | 2 | 质量插件：代码健康、技术债分析 |
| **plugin-security** | 3 | 安全插件：安全审计、合规检查、漏洞扫描 |
| **plugin-testing** | 1 | 测试插件：测试套件自动生成 |
| **agent-tools** | 41 | Agent 工具集：无障碍、AI开发、API Mock、调试、Docker、K8s 等 |
| **super-claude** | 30 | SuperClaude 命令：分析、构建、设计、文档、Git、实现、测试等 |
| **apple** | 5 | Apple 生态：Notes、Reminders、FindMy、iMessage、Computer Use |
| **autonomous-ai-agents** | 6 | 自主 AI Agent：Claude Code、Codex、OpenCode、Hermes 配置 |
| **data-science** | 1 | 数据科学：Jupyter 实时内核 |
| **devops** | 3 | DevOps：Kanban 编排、macOS 代理诊断 |
| **email** | 1 | 邮件：Himalaya CLI |
| **github** | 6 | GitHub 工作流：认证、PR、代码审查、Issues、仓库管理 |
| **media** | 4 | 媒体：YouTube 字幕、GIF 搜索、音乐生成、音频频谱 |
| **mlops** | 7 | MLOps：HuggingFace、vLLM、llama.cpp、AudioCraft、SAM、W&B |
| **note-taking** | 2 | 笔记：Obsidian 仓库管理、Codex 桥接 |
| **productivity** | 8 | 生产力：Airtable、Google Workspace、Notion、PowerPoint、Maps、PDF、OCR、Teams |
| **research** | 5 | 学术研究：arXiv、博客监控、LLM Wiki、Polymarket、论文写作 |
| **smart-home** | 1 | 智能家居：Philips Hue |
| **social-media** | 1 | 社交媒体：X/Twitter |
| **software-development** | 9 | 软件开发：Plan、Spike、TDD、调试、代码审查、简化、Skill 创作 |
| **dogfood** | 1 | 内部测试：Web App QA |
| **yuanbao** | 1 | 元宝集成 |
| **system-utilities** | 1 | 系统工具：Windows C 盘安全清理 |

## 统计

- **总 Skill 数**: 222
- **总分类数**: 39
- **平台兼容**: Claude Code / Hermes / Codex / Cursor
- **每个 Skill**: 1 通用核心 + 3 平台挂载配置

## 使用方式

SKILL.md 是通用核心，所有平台都能读取。平台特定配置在 `mounts/` 目录下：

| 平台 | 加载文件 | 关键字段 |
|------|---------|---------|
| **Claude Code** | `SKILL.md` + `mounts/claude-code.yaml` | `triggers`, `category` |
| **Hermes Agent** | `SKILL.md` + `mounts/hermes.yaml` | `version`, `tags`, `platforms` |
| **Codex** | `SKILL.md` + `mounts/codex.yaml` | `interface.display_name`, `policy.allow_implicit_invocation` |

## License

MIT
