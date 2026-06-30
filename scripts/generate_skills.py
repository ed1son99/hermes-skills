#!/usr/bin/env python3
"""Generate SKILL.md files and mount configs in universal cross-platform format.

Produces the unified structure compatible with Claude Code / Hermes / Codex / Cursor:
  skills/<category>/<name>/
  ├── SKILL.md                  # Universal: name, description, triggers, platforms
  ├── mounts/
  │   ├── claude-code.yaml
  │   ├── hermes.yaml
  │   └── codex.yaml
  ├── references/
  ├── scripts/
  └── templates/

Run from repo root: python scripts/generate_skills.py
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Complete Skill Catalog ─────────────────────────────────────────────
# Format: { "category": [(name, description, trigger_keywords, details), ...] }
# Categories marked with * are new (not yet in hermes-skills)

CATALOG = {
    # ── NEW CATEGORY: film-making ──
    "film-making": [
        (
            "director-master",
            "山音超级导演大师 — 从剧本到九列分镜表的完整导演工作流",
            "分镜, 分镜表, 导演, 镜头语言, 运镜, 构图, 景别, 剪辑节奏, 视听风格, storyboard, 导演方案, 拍摄方案",
            "与 screenplay-master 联动。完成导演定调、节奏规划、剧本微调、分镜拆解，最终生成标准九列分镜表（xlsx）。内置数十种影片类型的导演风格模板库，支持类型交叉组合。覆盖从概念超短片到长片的全格式分镜。",
        ),
        (
            "screenplay-master",
            "剧本创作根编排技能 — 按意图-媒介-阶段-输出-约束进行路由",
            "剧本, 编剧, 叙事, 商业剧本, 交互式剧本, screenplay, script, 故事",
            "加载最小化协议+规范+原子组件。覆盖叙事、商业和交互式剧本。按意图-媒介-阶段-输出-约束进行路由。",
        ),
        (
            "camera-director",
            "生成专业视频运镜提示词，支持单镜头和分镜脚本",
            "video prompt, camera movement, 运镜, storyboard, 分镜, Sora, Runway, Pika, 镜头运动",
            "支持单镜头和分镜脚本。为 AI 视频生成工具（Sora, Runway, Pika 等）生成专业的运镜提示词。",
        ),
        (
            "seedance-20",
            "Seedance 2.0 视频生成 — T2V, I2V, V2V, R2V, audio, safety, API",
            "Seedance, T2V, I2V, V2V, R2V, 视频生成, AI视频, text-to-video",
            "完整的 Seedance 2.0 工作流指导。涵盖文生视频、图生视频、视频生视频、参考生视频、音频、安全和 API 集成。",
        ),
    ],
    # ── NEW CATEGORY: ai-media ──
    "ai-media": [
        (
            "libtv-skill",
            "LibTV AI 图像视频创作 — 通过 liblib.tv AI 能力生成和编辑图片/视频",
            "liblib, libtv, AI图片, AI视频, 文生图, 文生视频, 图生视频, 动画, 风格迁移, MV, 短剧, 海报",
            "覆盖：生成（文生图、文生视频、图生视频、做动画）、编辑修改（局部修改、替换元素、风格转换）、视频续写、复刻视频/TVC、短剧/短漫剧、音乐MV、产品广告、分镜/故事板、教育视频。",
        ),
        (
            "libtv-cli",
            "LibTV 官方 CLI — 命令行操作 LibTV 画布",
            "libtv CLI, 画布, 节点, 模型, 素材, liblib CLI",
            "在命令行里完整操作 LibTV 画布。凡和 LibTV 画布/项目/节点/模型/素材相关的操作，一律通过 libtv CLI 完成。包含完整 CLI 命令操作手册。",
        ),
    ],
    # ── NEW CATEGORY: design-system ──
    "design-system": [
        (
            "impeccable",
            "前端界面设计精修 — 网站、Landing page、Dashboard、组件、表单",
            "design, redesign, 设计, 界面, UI, UX, 美化, 视觉, landing page, dashboard, 组件, 配色, 排版, 动效",
            "覆盖 UX 审核、视觉层级、信息架构、认知负荷、无障碍、性能、响应式、主题化、反模式、排版、字体、间距、布局、对齐、色彩、动效、微交互、UX 文案、错误状态、边缘情况、i18n、设计系统。也适用于从平淡到惊艳、从喧闹到安静的设计调优。",
        ),
        (
            "ui-ux-pro-max",
            "UI/UX 专业级设计系统 — 前端界面工程化",
            "UI, UX, 设计系统, design system, 前端设计, 组件库",
            "专业级 UI/UX 设计系统技能。涵盖完整的设计工程化流程。",
        ),
        (
            "frontend-ui-engineering",
            "生产级前端 UI 工程 — 组件、布局、状态管理",
            "frontend, UI, 组件, component, 布局, layout, 状态管理, 前端工程",
            "构建生产级质量的用户界面。创建组件、实现布局、管理状态，输出专业级而非 AI 生成感的界面。",
        ),
    ],
    # ── ENHANCE: creative ──
    "creative": [
        (
            "agent-reach",
            "全网调研 — 13 平台多后端路由搜索",
            "调研, research, 搜索, 查, 找, look up, 小红书, xiaohongshu, Twitter, 推特, B站, bilibili, Reddit, V2EX, LinkedIn, YouTube, GitHub, 播客, RSS",
            "13 平台覆盖：小红书/推特/B站/V2EX/Reddit/LinkedIn/YouTube/GitHub code search/小宇宙播客/雪球/RSS。多后端路由（OpenCLI / 各平台 CLI / API）。零配置 6 通道。NOT for 写报告/数据分析/翻译等内容加工。路由表及常用命令在 SKILL.md，复杂场景按需阅读 references/。",
        ),
    ],
    # ── NEW CATEGORY: development-methodology ──
    "development-methodology": [
        (
            "test-driven-development",
            "测试驱动开发 — 严格 red-green-refactor 循环",
            "TDD, test-driven, 测试驱动, red-green-refactor, 单元测试, unit test",
            "驱动开发的测试先行方法论。实施严格的 red-green-refactor 循环：先写失败的测试，再写最小实现使其通过，最后重构。",
        ),
        (
            "spec-driven-development",
            "规格驱动开发 — 先写规格再编码",
            "spec, specification, 规格, 需求, PRD, 规范, 设计文档",
            "在编码前创建规格说明。适用于新项目、新功能或重大变更。将模糊需求转化为清晰、可执行的规格。",
        ),
        (
            "source-driven-development",
            "源码驱动开发 — 基于官方文档做决策",
            "source, 官方文档, 源码, RTFM, documentation-driven, 文档驱动",
            "每个实现决策都基于官方文档。适用于任何框架或库的开发。确保代码权威、有据可查、不含过时模式。",
        ),
        (
            "doubt-driven-development",
            "质疑驱动开发 — 每个非平凡决策经受对抗性审查",
            "doubt, 质疑, 审查, 验证, adversarial, 代码审查, correctness",
            "对每个非平凡决策进行全新上下文的对抗性审查。适用于正确性高于速度的场景、陌生代码、高风险操作。验证现在比调试以后更便宜。",
        ),
        (
            "incremental-implementation",
            "增量实现 — 逐步交付变更",
            "incremental, 增量, 逐步, 分批, 迭代, small PRs",
            "将大变更分解为小的、可审查的增量。每次变更只触及最少文件。适用于任何跨文件的功能实现。",
        ),
        (
            "interview-me",
            "访谈式需求澄清 — 一问一答直到 95% 置信度",
            "interview, 访谈, 需求澄清, 理解意图, 提问, clarify",
            "通过一问一答的方式提炼用户真正想要的东西。适用于需求模糊的场景。在计划、规格或代码存在之前发现真正的意图。",
        ),
    ],
    # ── NEW CATEGORY: architecture-planning ──
    "architecture-planning": [
        (
            "planning-and-task-breakdown",
            "工作拆解与任务规划 — 将工作分解为有序任务",
            "plan, 计划, 任务, task, 拆解, breakdown, 估算, estimate",
            "将工作分解为可执行的任务。适用于有规格或清晰需求但需要分解为实施步骤的场景。评估范围、识别并行机会。",
        ),
        (
            "documentation-and-adrs",
            "文档与架构决策记录 — 记录决策和文档",
            "ADR, 架构决策, documentation, 文档, decision record, 设计决策",
            "记录架构决策、API 变更、功能发布。为未来工程师和 AI 代理提供代码库理解所需的上下文。",
        ),
        (
            "context-engineering",
            "上下文工程 — 优化 Agent 上下文配置",
            "context, 上下文, CLAUDE.md, rules, 配置, agent setup",
            "优化 agent 上下文配置。适用于新会话开始、agent 输出质量下降、任务切换、或需要配置规则文件和上下文的场景。",
        ),
        (
            "api-and-interface-design",
            "API 与接口设计 — 稳定的 API 和模块边界设计",
            "API, interface, 接口, REST, GraphQL, 模块边界, contract, 类型契约",
            "设计稳定的 API 和接口。适用于 REST/GraphQL 端点设计、模块间类型契约定义、前后端边界确立。",
        ),
        (
            "deprecation-and-migration",
            "弃用与迁移管理 — 安全地移除旧系统和迁移用户",
            "deprecation, 弃用, migration, 迁移, sunset, 版本升级, 兼容性",
            "管理弃用和迁移。适用于移除旧系统/API/功能、从旧实现迁移用户、决定维护还是淘汰现有代码。",
        ),
    ],
    # ── NEW CATEGORY: code-quality ──
    "code-quality": [
        (
            "code-review-and-quality",
            "多维度代码审查 — correctness, readability, architecture, security, performance",
            "review, 审查, code review, 代码质量, quality, 审查代码",
            "在合并前进行多轴代码审查。评估正确性、可读性、架构、安全性和性能。适用于审查自己、其他 agent 或人类编写的代码。",
        ),
        (
            "code-simplification",
            "代码简化 — 重构使代码更清晰",
            "simplify, 简化, refactor, 重构, clean code, 清晰, 可读性",
            "在不改变行为的前提下重构代码使其更清晰。适用于代码能工作但难以阅读、维护或扩展的场景。",
        ),
        (
            "debugging-and-error-recovery",
            "系统化根因调试 — 从失败到修复的完整流程",
            "debug, 调试, bug, 错误, error, 失败, 根因, root cause, 排查",
            "系统化根因调试指南。适用于测试失败、构建失败、行为不符预期或任何意外错误。使用系统化方法而非猜测。",
        ),
        (
            "security-and-hardening",
            "安全加固 — 防范漏洞",
            "security, 安全, 漏洞, vulnerability, auth, 认证, 输入验证, OWASP",
            "针对漏洞加固代码。适用于处理用户输入、认证、数据存储和外部集成。构建接收不可信数据的功能时必用。",
        ),
        (
            "performance-optimization",
            "性能优化 — 测量驱动的瓶颈消除",
            "performance, 性能, optimization, 优化, bottleneck, 瓶颈, Core Web Vitals, profiling",
            "优化应用性能。适用于存在性能要求的场景、怀疑性能退化的场景、或 Core Web Vitals 需要改进的场景。通过性能分析定位瓶颈并修复。",
        ),
    ],
    # ── NEW CATEGORY: devops-release ──
    "devops-release": [
        (
            "git-workflow-and-versioning",
            "Git 工作流与版本管理 — 结构化 Git 实践",
            "git, commit, branch, PR, 分支, 合并, version, 版本",
            "结构化 Git 工作流实践。适用于任何代码变更的提交、分支、冲突解决、跨并行流的组织。",
        ),
        (
            "shipping-and-launch",
            "发布与上线 — 生产环境部署准备",
            "deploy, 部署, launch, 上线, release, 发布, production, 生产环境, rollout",
            "准备生产环境上线。包含 pre-launch checklist、监控设置、分阶段 rollout 策略、回滚方案。",
        ),
        (
            "ci-cd-and-automation",
            "CI/CD 与自动化 — 构建和部署流水线配置",
            "CI, CD, pipeline, 流水线, 自动化, build, deploy, GitHub Actions",
            "自动化 CI/CD 流水线设置。适用于构建和部署流水线的建立或修改。自动化质量门禁、配置 CI 中的测试运行器、建立部署策略。",
        ),
        (
            "browser-testing-with-devtools",
            "浏览器测试 — 通过 Chrome DevTools MCP 在真实浏览器中测试",
            "browser, 浏览器, Chrome, DevTools, DOM, console, network, 调试, E2E",
            "通过 Chrome DevTools MCP 在真实浏览器中测试。检查 DOM、捕获 console 错误、分析网络请求、性能分析、使用真实运行时数据验证视觉输出。",
        ),
    ],
    # ── NEW CATEGORY: claude-config ──
    "claude-config": [
        (
            "update-config",
            "Claude Code 配置管理 — settings.json 和 hooks 配置",
            "settings, config, 配置, hook, permission, 权限, env, 环境变量, settings.json",
            "通过 settings.json 配置 Claude Code。自动化行为需要 hooks 配置。也适用于权限管理、环境变量设置、hook 故障排除。",
        ),
        (
            "keybindings-help",
            "键盘快捷键自定义 — ~/.claude/keybindings.json 配置",
            "keybinding, 快捷键, 键盘, shortcut, rebind, 绑定",
            "自定义键盘快捷键、重新绑定按键、添加组合键。修改 ~/.claude/keybindings.json。",
        ),
        (
            "claude-api",
            "Claude API 参考 — 模型 ID、定价、参数、流式、工具使用、MCP",
            "Claude API, Anthropic, SDK, model, 模型, pricing, 定价, token, streaming, MCP",
            "Claude API / Anthropic SDK 参考。模型 ID、定价、参数、流式传输、工具使用、MCP、agents、缓存、token 计数、模型迁移。在任何涉及 LLM 选择/定价/限制的问题时必读。",
        ),
        (
            "fewer-permission-prompts",
            "减少权限提示 — 扫描转录记录并添加 allowlist",
            "permission, 权限, allowlist, 允许, 减少提示, 自动允许",
            "扫描转录记录中的常见只读 Bash 和 MCP 工具调用，添加优先 allowlist 以减少权限提示。",
        ),
        (
            "using-agent-skills",
            "Agent Skill 发现与调用 — 元技能，管理所有其他 skill 的发现和调用",
            "skill, agent, 技能, 发现, 调用, meta",
            "发现和调用 agent skills。这是管理所有其他 skills 如何被发现和调用的元技能。会话开始时或需要发现哪个 skill 适用当前任务时使用。",
        ),
    ],
    # ── NEW CATEGORY: cli-commands ──
    "cli-commands": [
        (
            "code-review",
            "CLI 代码审查 — 审查当前 diff 的正确性 bug 和简化机会",
            "/code-review, diff review, PR review, 审查 diff, --comment, --fix",
            "审查当前 diff 中的正确性 bug 和复用/简化/效率改进。支持 --comment（发布为 inline PR 评论）和 --fix（应用修复到工作树）。",
        ),
        (
            "simplify",
            "CLI 代码简化 — 审查变更代码的复用、简化、效率和抽象改进",
            "/simplify, simplify code, 简化代码, 重构, 清理",
            "审查变更代码的复用、简化、效率和抽象改进并应用修复。仅关注质量 — 不查找 bug；用 /code-review 做 bug 查找。",
        ),
        (
            "verify",
            "CLI 验证 — 通过运行应用确认代码变更是否有效",
            "/verify, verify PR, 验证, 确认修复, 测试变更, 手动测试",
            "通过运行应用并观察行为来验证代码变更。适用于验证 PR、确认修复、手动测试变更、验证功能、push 前验证本地变更。",
        ),
        (
            "run",
            "CLI 启动 — 启动并驱动项目应用查看变更效果",
            "/run, run app, 启动, 运行, 截图, 查看效果",
            "启动项目应用以查看变更的实际效果。适用时需要截图或确认变更在真实应用中有效（而非仅测试）。",
        ),
        (
            "loop",
            "CLI 循环 — 按间隔重复执行 prompt 或 slash command",
            "/loop, 循环, 重复, poll, 定时, 监控",
            "按定期间隔运行 prompt 或 slash command。省略间隔让模型自定节奏。适用于设置定期任务或状态轮询。",
        ),
        (
            "init",
            "CLI 初始化 — 创建新的 CLAUDE.md 文件记录代码库文档",
            "/init, CLAUDE.md, 初始化, 文档, 代码库, project docs",
            "用代码库文档初始化新的 CLAUDE.md 文件。分析项目结构并生成标准化的项目上下文文件。",
        ),
        (
            "security-review",
            "CLI 安全审查 — 完成当前分支待处理变更的安全审查",
            "/security-review, security review, 安全审查, 漏洞审查",
            "完成当前分支待处理变更的完整安全审查。检查 OWASP Top 10、认证、授权、数据保护等安全问题。",
        ),
    ],
    # ── NEW CATEGORY: meta-tools ──
    "meta-tools": [
        (
            "graphify",
            "Graphify — 将任何输入转化为持久知识图谱",
            "graphify, 知识图谱, knowledge graph, 代码关系, 文件关系, 项目结构",
            "将任何输入（代码、文档、论文、图片、视频）转化为持久知识图谱，支持 god nodes、社区检测、查询/路径/解释工具。graphify-out/ 目录存在时优先使用图谱查询。",
        ),
        (
            "idea-refine",
            "想法精炼 — 通过结构化发散和收敛思维将原始想法打磨为可执行概念",
            "ideate, refine, 想法, 打磨, 头脑风暴, brainstorm, stress-test",
            "通过结构化发散和收敛思维将原始想法转化为清晰可执行的概念。适用于想法模糊、需要压力测试假设、在收敛前扩展选项的场景。",
        ),
        (
            "deep-research",
            "深度研究 — 扇形网络搜索、获取来源、对抗性验证、综合引用报告",
            "deep research, 深度研究, 调研报告, fact-check, 多源验证, 综合报告",
            "在任意主题上生成深度、多源、事实核验的研究报告。先确认问题是否足够具体，再进行扇形搜索、获取来源、对抗性验证和综合。",
        ),
    ],
    # ── SESSION MANAGEMENT ──
    "session-management": [
        (
            "session-start",
            "创建新的开发会话记录",
            "/session-start, session, 会话, 开始, 记录",
            "通过创建 .claude/sessions/ 下的会话文件开始新的开发会话。格式：YYYY-MM-DD-<name>.md。",
        ),
        (
            "session-end",
            "结束当前开发会话",
            "/session-end, session, 会话结束, 结束",
            "结束当前开发会话，记录完成的工作和后续步骤。",
        ),
        (
            "session-list",
            "列出所有开发会话",
            "/session-list, session, 会话列表, 查看会话",
            "列出所有开发会话及其状态。",
        ),
        (
            "session-current",
            "显示当前会话状态",
            "/session-current, session, 当前会话, 状态",
            "显示当前开发会话的详细信息。",
        ),
        (
            "session-help",
            "会话管理系统帮助",
            "/session-help, session, 会话帮助",
            "显示会话管理系统的完整帮助文档。",
        ),
        (
            "session-update",
            "更新当前开发会话",
            "/session-update, session, 更新会话",
            "更新当前开发会话的状态和内容。",
        ),
    ],
    # ── WORKFLOW COMMANDS ──
    "workflow-automation": [
        (
            "workflow-review",
            "综合代码审查工作流 — 安全、性能、配置安全分析",
            "/review, workflow review, 审查, 综合审查",
            "使用专门的 agents 进行综合代码审查。涵盖安全、性能和配置安全分析。",
        ),
        (
            "workflow-add-to-todos",
            "添加 TODO 到 TO-DOS.md",
            "/add-to-todos, todo, 待办, 任务",
            "从对话上下文中提取并追加 TODO 项到 TO-DOS.md。",
        ),
        (
            "workflow-check-todos",
            "查看并选择待办 TODO",
            "/check-todos, todo, 待办列表, 查看任务",
            "列出未完成的 TODO 并选择一项继续工作。",
        ),
        (
            "workflow-create-prompt",
            "创建优化的 XML 结构化 Prompt",
            "/create-prompt, prompt, 提示词, 优化",
            "专家级 prompt 工程师，创建 XML 结构化的优化 prompt。支持智能深度选择。",
        ),
        (
            "workflow-prompt-run",
            "并行或顺序执行多个 Prompt",
            "/prompt-run, prompt, 执行, 批量",
            "将多个 prompt 委派到新的子任务上下文中并行或顺序执行。",
        ),
        (
            "workflow-handoff-create",
            "创建任务交接文档",
            "/handoff-create, handoff, 交接, 续接",
            "分析当前对话并创建交接文档，用于在新上下文中继续工作。",
        ),
        (
            "workflow-whats-next",
            "分析当前对话并创建后续步骤文档",
            "/whats-next, next, 下一步, 后续",
            "分析当前对话并创建后续步骤指导。",
        ),
    ],
    # ── PLUGIN: development ──
    "plugin-development": [
        (
            "development-scaffold",
            "项目脚手架生成 — 现代化项目结构、组件和样板代码",
            "scaffold, 脚手架, 项目初始化, 模板, boilerplate, 创建项目",
            "生成生产级的项目结构、组件和样板代码。包含现代化最佳实践和全面工具链配置。",
        ),
    ],
    # ── PLUGIN: documentation ──
    "plugin-documentation": [
        (
            "documentation-docs-gen",
            "自动文档生成 — API 文档、用户指南、交互式文档",
            "docs, 文档生成, API docs, 用户指南, documentation",
            "从代码生成综合文档：API 文档、用户指南、交互式文档，支持自动化部署。",
        ),
    ],
    # ── PLUGIN: operations ──
    "plugin-operations": [
        (
            "operations-deploy-validate",
            "部署前验证 — 测试、安全检查、配置安全、环境就绪",
            "deploy, 部署验证, pre-deploy, 上线检查, validation",
            "部署前验证：运行测试、安全检查、配置安全验证、环境就绪检查。",
        ),
        (
            "operations-health-check",
            "系统健康检查 — 生产监控和事件检测",
            "health check, 健康检查, 监控, 生产, incident",
            "全面的系统健康验证。用于生产监控和事件检测。",
        ),
        (
            "operations-incident-response",
            "生产事件响应 — 紧急分诊、RCA、事后分析",
            "incident, 事件, 故障, RCA, 事后分析, postmortem, 紧急",
            "生产事件协调：紧急分诊、根因分析、事后分析生成。",
        ),
    ],
    # ── PLUGIN: performance ──
    "plugin-performance": [
        (
            "performance-benchmark",
            "负载测试与性能基准 — 智能场景生成",
            "benchmark, 负载测试, load test, 性能基准, 压测",
            "负载测试和性能基准测试，支持智能场景生成。",
        ),
        (
            "performance-profile",
            "综合性能分析 — 瓶颈识别和优化建议",
            "profile, 性能分析, 分析, 瓶颈, profiling",
            "全面的性能分析：瓶颈识别和优化建议。",
        ),
    ],
    # ── PLUGIN: quality ──
    "plugin-quality": [
        (
            "quality-code-health",
            "代码健康度评估 — 质量指标、测试覆盖率、文档、可维护性",
            "code health, 代码健康, 质量, 覆盖率, 可维护性",
            "代码库健康度评估：质量指标、测试覆盖率、文档质量、可维护性分析。",
        ),
        (
            "quality-debt-analysis",
            "技术债识别 — 优先级排序、工作量估算、重构路线图",
            "technical debt, 技术债, 重构, 优化, debt analysis",
            "技术债识别：优先级排序、工作量估算、重构路线图。",
        ),
    ],
    # ── PLUGIN: security ──
    "plugin-security": [
        (
            "security-audit",
            "综合安全审计 — 多阶段编排、自动 agent 选择",
            "audit, 安全审计, security audit, 漏洞扫描, CVE",
            "综合安全审计：智能多阶段编排和自动 agent 选择。",
        ),
        (
            "security-compliance-check",
            "合规验证 — GDPR, SOC2, HIPAA, PCI-DSS 等框架",
            "compliance, 合规, GDPR, SOC2, HIPAA, PCI-DSS, 法规",
            "法规合规验证：GDPR、SOC2、HIPAA、PCI-DSS 等框架。",
        ),
        (
            "security-vulnerability-scan",
            "深度漏洞分析 — CVE 扫描、依赖分析、漏洞关联",
            "vulnerability, 漏洞, CVE, 依赖, 扫描",
            "深度漏洞分析：CVE 扫描、依赖分析、漏洞关联。",
        ),
    ],
    # ── PLUGIN: testing ──
    "plugin-testing": [
        (
            "testing-test-gen",
            "测试套件自动生成 — 多框架支持",
            "test, 测试, test-gen, 单元测试, 组件测试, 生成测试",
            "自动生成综合测试套件。支持组件、函数、API 的多框架测试生成。",
        ),
    ],
    # ── TOOLS ──
    "agent-tools": [
        (
            "tools-accessibility-audit",
            "无障碍审计和测试",
            "accessibility, 无障碍, a11y, WCAG, 可访问性",
            "综合无障碍审计和测试工具。",
        ),
        (
            "tools-ai-assistant",
            "AI 助手开发",
            "AI assistant, 助手, chatbot, 对话",
            "AI 助手开发工具和最佳实践。",
        ),
        (
            "tools-ai-review",
            "AI/ML 代码审查",
            "AI review, ML review, AI代码审查, 机器学习",
            "AI/ML 专项代码审查。",
        ),
        (
            "tools-api-mock",
            "API Mock 框架",
            "API mock, mock, 模拟, 接口模拟, stub",
            "API Mock 框架：快速搭建模拟接口。",
        ),
        (
            "tools-api-scaffold",
            "API 脚手架生成器",
            "API scaffold, API生成, 接口脚手架",
            "快速生成 API 脚手架代码。",
        ),
        (
            "tools-code-explain",
            "代码解释与分析",
            "explain code, 解释代码, 代码分析, 理解",
            "深度代码解释和分析。",
        ),
        (
            "tools-code-migrate",
            "代码迁移助手",
            "migrate, 迁移, 升级, 版本迁移, 代码迁移",
            "代码迁移助手：版本升级、框架迁移。",
        ),
        (
            "tools-config-validate",
            "配置验证",
            "config, 配置验证, 配置检查",
            "配置文件验证和检查。",
        ),
        (
            "tools-context-restore",
            "恢复保存的项目上下文",
            "context restore, 恢复上下文, 项目上下文",
            "恢复保存的项目上下文用于 agent 协调。",
        ),
        (
            "tools-context-save",
            "保存当前项目上下文",
            "context save, 保存上下文, 项目上下文",
            "保存当前项目上下文用于未来的 agent 协调。",
        ),
        (
            "tools-cost-optimize",
            "云成本优化",
            "cost, 成本, 云成本, 优化, cloud",
            "云成本优化分析和建议。",
        ),
        (
            "tools-data-pipeline",
            "数据流水线架构",
            "data pipeline, 数据流水线, ETL, 数据架构",
            "数据流水线架构设计和实现。",
        ),
        (
            "tools-data-validation",
            "数据验证流水线",
            "data validation, 数据验证, 数据质量",
            "数据验证流水线：数据质量保证。",
        ),
        (
            "tools-db-migrate",
            "数据库迁移策略与实现",
            "DB migration, 数据库迁移, schema, 迁移策略",
            "数据库迁移策略和实现指导。",
        ),
        (
            "tools-debug-trace",
            "调试和追踪配置",
            "debug trace, 调试追踪, 日志, tracing",
            "调试和追踪配置工具。",
        ),
        (
            "tools-deploy-checklist",
            "部署检查清单和配置",
            "deploy checklist, 部署检查, 上线清单",
            "部署检查清单和配置验证。",
        ),
        (
            "tools-deps-audit",
            "依赖审计和安全分析",
            "deps audit, 依赖审计, 依赖安全, npm audit",
            "依赖审计和安全分析。",
        ),
        (
            "tools-deps-upgrade",
            "依赖升级策略",
            "deps upgrade, 依赖升级, 版本升级",
            "依赖升级策略和最佳实践。",
        ),
        (
            "tools-doc-generate",
            "自动文档生成",
            "doc generate, 文档生成, API文档",
            "自动化文档生成工具。",
        ),
        (
            "tools-docker-optimize",
            "Docker 优化",
            "docker, 容器优化, Dockerfile, 镜像优化",
            "Docker 镜像和容器优化。",
        ),
        (
            "tools-error-analysis",
            "错误分析和解决",
            "error analysis, 错误分析, bug分析",
            "系统化错误分析和解决方案。",
        ),
        (
            "tools-error-trace",
            "错误追踪和监控",
            "error tracking, 错误追踪, 监控, Sentry",
            "错误追踪和监控设置。",
        ),
        (
            "tools-issue",
            "分析和修复 GitHub issue",
            "issue, GitHub issue, bug fix, 修复",
            "分析和修复指定的 GitHub issue。",
        ),
        (
            "tools-k8s-manifest",
            "Kubernetes Manifest 生成",
            "k8s, kubernetes, manifest, 容器编排, 部署",
            "Kubernetes Manifest 文件生成。",
        ),
        (
            "tools-langchain-agent",
            "LangChain/LangGraph Agent 脚手架",
            "langchain, langgraph, agent, LLM agent, RAG",
            "LangChain/LangGraph Agent 脚手架生成。",
        ),
        (
            "tools-monitor-setup",
            "监控和可观测性设置",
            "monitor, 监控, observability, 可观测性, Prometheus, Grafana",
            "监控和可观测性设置。",
        ),
        (
            "tools-multi-agent-optimize",
            "多 Agent 优化应用栈",
            "multi-agent, 多agent, 优化, 应用栈",
            "使用专门的优化 agents 优化应用栈。",
        ),
        (
            "tools-multi-agent-review",
            "多 Agent 综合代码审查",
            "multi-agent review, 多agent审查, 综合审查",
            "使用多个专门的审查 agents 进行综合代码审查。",
        ),
        (
            "tools-onboard",
            "项目入职引导",
            "onboard, 入职, 上手, 新项目, 入门",
            "项目入职引导：帮助新开发者快速上手。",
        ),
        (
            "tools-pr-enhance",
            "PR 增强",
            "PR, pull request, 增强, 完善",
            "Pull Request 增强：自动完善 PR 描述和内容。",
        ),
        (
            "tools-prompt-optimize",
            "AI Prompt 优化",
            "prompt optimize, prompt工程, 提示词优化",
            "AI Prompt 优化工具。",
        ),
        (
            "tools-refactor-clean",
            "重构和清理代码",
            "refactor, 重构, 清理, clean code",
            "重构和清理代码工具。",
        ),
        (
            "tools-security-scan",
            "安全扫描和漏洞评估",
            "security scan, 安全扫描, 漏洞评估",
            "安全扫描和漏洞评估工具。",
        ),
        (
            "tools-slo-implement",
            "SLO 实现指南",
            "SLO, SLA, 服务水平, 可靠性",
            "SLO 实现指南和最佳实践。",
        ),
        (
            "tools-smart-debug",
            "智能调试 — 使用专门的调试 agents",
            "smart debug, 智能调试, 复杂bug",
            "使用专门的调试 agents 调试复杂问题。",
        ),
        (
            "tools-standup-notes",
            "站会记录生成器",
            "standup, 站会, 日报, 进度",
            "自动生成站会记录。",
        ),
        (
            "tools-tdd-green",
            "TDD Green 阶段 — 实现最小代码使测试通过",
            "TDD green, 测试通过, 实现",
            "TDD green 阶段：实现最小代码使失败的测试通过。",
        ),
        (
            "tools-tdd-red",
            "TDD Red 阶段 — 编写全面的失败测试",
            "TDD red, 编写测试, 失败测试",
            "TDD red 阶段：编写全面的失败测试。",
        ),
        (
            "tools-tdd-refactor",
            "TDD Refactor 阶段 — 在测试保护下重构",
            "TDD refactor, 重构, 测试保护",
            "TDD refactor 阶段：在全面测试的安全网下重构代码。",
        ),
        (
            "tools-tech-debt",
            "技术债分析和修复",
            "tech debt, 技术债, 技术债务",
            "技术债分析和修复策略。",
        ),
        (
            "tools-test-harness",
            "综合测试框架生成器",
            "test harness, 测试框架, 测试工具",
            "综合测试框架和工具生成。",
        ),
    ],
    # ── SUPER CLAUDE COMMANDS ──
    "super-claude": [
        (
            "sc-agent",
            "SuperClaude Agent 管理",
            "sc:agent, agent管理",
            "SuperClaude Agent 管理命令。",
        ),
        (
            "sc-analyze",
            "综合代码分析 — 质量、安全、性能、架构",
            "sc:analyze, 分析, 代码分析",
            "跨质量、安全、性能、架构领域的综合代码分析。",
        ),
        (
            "sc-brainstorm",
            "交互式需求发现 — 苏格拉底式对话和系统探索",
            "sc:brainstorm, 头脑风暴, 需求, 苏格拉底",
            "通过苏格拉底式对话和系统化探索进行交互式需求发现。",
        ),
        (
            "sc-build",
            "构建、编译和打包项目",
            "sc:build, 构建, 编译, 打包, build",
            "智能构建、编译和打包项目，支持错误处理和优化。",
        ),
        (
            "sc-business-panel",
            "商业面板分析系统",
            "sc:business-panel, 商业分析, 战略",
            "多专家商业分析面板。",
        ),
        (
            "sc-cleanup",
            "系统化清理代码",
            "sc:cleanup, 清理, 死代码, 优化",
            "系统化清理代码、移除死代码、优化项目结构。",
        ),
        (
            "sc-design",
            "系统架构设计",
            "sc:design, 设计, 架构, API设计",
            "设计系统架构、API 和组件接口。",
        ),
        (
            "sc-document",
            "聚焦文档生成",
            "sc:document, 文档, 注释",
            "为组件、函数、API 和功能生成聚焦文档。",
        ),
        (
            "sc-estimate",
            "开发估算",
            "sc:estimate, 估算, 工作量, 评估",
            "为任务、功能或项目提供智能开发估算。",
        ),
        (
            "sc-explain",
            "代码和概念解释",
            "sc:explain, 解释, 讲解, 理解",
            "提供代码、概念和系统行为的清晰解释。",
        ),
        (
            "sc-git",
            "Git 操作",
            "sc:git, git, commit, 提交",
            "Git 操作：智能提交消息和工作流优化。",
        ),
        (
            "sc-help",
            "SuperClaude 帮助",
            "sc:help, 帮助, 命令列表",
            "列出所有可用的 /sc 命令及其功能。",
        ),
        (
            "sc-implement",
            "功能实现",
            "sc:implement, 实现, 开发, 编码",
            "功能实现：智能 persona 激活和 MCP 集成。",
        ),
        (
            "sc-improve",
            "系统化改进",
            "sc:improve, 改进, 优化",
            "对代码质量、性能和可维护性进行系统化改进。",
        ),
        (
            "sc-index",
            "项目文档和知识库生成",
            "sc:index, 索引, 知识库, 项目文档",
            "生成综合项目文档和知识库，支持智能组织。",
        ),
        (
            "sc-index-repo",
            "仓库索引 — 94% token 减少 (58K → 3K)",
            "sc:index-repo, 索引, repo index",
            "仓库索引：实现 94% token 减少。",
        ),
        (
            "sc-load",
            "会话生命周期管理",
            "sc:load, 加载, 会话, 上下文",
            "会话生命周期管理：Serena MCP 集成。",
        ),
        (
            "sc-pm",
            "项目管理 Agent",
            "sc:pm, 项目管理, 协调",
            "默认的项目管理 orchestrator agent。",
        ),
        (
            "sc-recommend",
            "超智能命令推荐引擎",
            "sc:recommend, 推荐, 命令推荐",
            "为任何用户输入推荐最合适的 SuperClaude 命令。",
        ),
        (
            "sc-reflect",
            "任务反思和验证",
            "sc:reflect, 反思, 验证, 回顾",
            "使用 Serena MCP 分析能力进行任务反思和验证。",
        ),
        (
            "sc-research",
            "深度网络调研",
            "sc:research, 调研, 网络搜索, 深度研究",
            "带自适应规划和智能搜索的深度网络调研。",
        ),
        (
            "sc-save",
            "会话上下文持久化",
            "sc:save, 保存, 持久化, 上下文",
            "会话生命周期管理：Serena MCP 集成用于会话上下文持久化。",
        ),
        (
            "sc-sc",
            "SuperClaude 命令调度器",
            "sc:sc, 调度, 命令",
            "SuperClaude 命令调度器。使用 /sc [command] 访问所有功能。",
        ),
        (
            "sc-select-tool",
            "智能 MCP 工具选择",
            "sc:select-tool, MCP, 工具选择",
            "基于复杂度评分和操作分析的智能 MCP 工具选择。",
        ),
        (
            "sc-spawn",
            "元系统任务编排",
            "sc:spawn, 编排, 任务分解, 委派",
            "元系统任务编排：智能分解和委派。",
        ),
        (
            "sc-spec-panel",
            "多专家规格审查和改进",
            "sc:spec-panel, 规格, 审查, 规范",
            "使用知名规格和软件工程专家进行多专家规格审查和改进。",
        ),
        (
            "sc-task",
            "复杂任务执行",
            "sc:task, 任务, 执行, 工作流",
            "使用智能工作流管理和委派执行复杂任务。",
        ),
        (
            "sc-test",
            "测试执行和分析",
            "sc:test, 测试, 覆盖率, 质量报告",
            "执行测试并附带覆盖率分析和自动质量报告。",
        ),
        (
            "sc-troubleshoot",
            "诊断和解决问题",
            "sc:troubleshoot, 诊断, 排查, 修复",
            "诊断和解决代码、构建、部署和系统行为中的问题。",
        ),
        (
            "sc-workflow",
            "从 PRD 生成结构化实施工作流",
            "sc:workflow, 工作流, PRD, 实施",
            "从 PRD 和功能需求生成结构化实施工作流。",
        ),
    ],
}


def generate_skill_md(name: str, description: str, trigger_str: str, details: str) -> str:
    """Generate universal SKILL.md for a single skill."""
    triggers = [t.strip() for t in trigger_str.split(',') if t.strip()]
    return f"""---
name: {name}
description: {description}
triggers: {triggers}
platforms: [claude-code, hermes, codex]
---

# {name}

{description}

## 概述

{details}

## 使用场景

触发关键词: {trigger_str}

## 平台兼容

本 Skill 兼容 Claude Code / Hermes / Codex / Cursor 等多平台。
各平台特定配置见 `mounts/` 目录。
"""


def generate_mounts(category: str, name: str, description: str, trigger_str: str) -> dict:
    """Generate all three mount files for a skill."""
    claude_code = f"""category: {category}
"""

    hermes = f"""version: "1.0.0"
author: Skills Catalog
license: MIT
platforms: [linux, macos, windows]
tags: [{trigger_str}]
"""

    codex = f"""interface:
  display_name: "{name.replace('-', ' ').title()}"
  short_description: "{description}"
  default_prompt: "Use ${name} to help with {name.replace('-', ' ')} tasks."
policy:
  allow_implicit_invocation: true
"""

    return {
        'claude-code.yaml': claude_code,
        'hermes.yaml': hermes,
        'codex.yaml': codex,
    }


def generate_description_md(category: str) -> str:
    """Generate standardized DESCRIPTION.md for a category."""
    return f'---\ndescription: "Skills for {category} category"\n---\n'


def main():
    total = 0
    for category, skills in CATALOG.items():
        cat_dir = REPO_ROOT / "skills" / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        for name, desc, trigger, details in skills:
            skill_dir = cat_dir / name
            skill_dir.mkdir(parents=True, exist_ok=True)

            # Write universal SKILL.md
            skill_path = skill_dir / "SKILL.md"
            content = generate_skill_md(name, desc, trigger, details)
            skill_path.write_text(content)

            # Write mount files
            mounts_dir = skill_dir / "mounts"
            mounts_dir.mkdir(parents=True, exist_ok=True)
            mounts = generate_mounts(category, name, desc, trigger)
            for filename, mount_content in mounts.items():
                (mounts_dir / filename).write_text(mount_content)

            total += 1

        # Write standardized DESCRIPTION.md
        desc_path = cat_dir / "DESCRIPTION.md"
        desc_path.write_text(generate_description_md(category))

    print(f"Generated {total} skills (SKILL.md + 3 mount files each) across {len(CATALOG)} categories.")


if __name__ == "__main__":
    main()
