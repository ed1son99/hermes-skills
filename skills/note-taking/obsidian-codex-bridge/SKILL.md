---
name: obsidian-codex-bridge
description: 连接 Obsidian vault 中 Codex Archive 快照与 Hermes 技能体系的桥接 Skill。告诉我 vault 里有哪些可参考的 Codex 技能，并能按需选择性迁移。
platforms: [macos]
---

# Obsidian ↔ Codex 桥接

## Vault 路径

`/Users/shabi/Documents/Obsidian Vault`

## 结构总览

```
Obsidian Vault/
├── AGENTS.md                          → 指向 Codex/AGENT_CONTEXT.md
├── 阿蒙的记忆库.md                      → 个人记忆
├── 问题库/                             → 3 个具体问题
│   ├── 问题库总览.md
│   ├── 问题页模板.md
│   ├── 大量技能资料找不到使用入口.md
│   ├── 导入快照和实时状态容易混淆.md
│   └── 视频制作信息散在提示词和工具里.md
├── Skills/                            → 技能分类目录（中文）
│   ├── Skill 统一目录.md               → 核心：137 条目，标记 🟣共享/🔵Claude/🟠Hermes
│   ├── Hermes 技能总览.md              → 指向统一目录
│   └── 各分类 MOC (10+ 文件)
└── Codex/
    ├── AGENT_CONTEXT.md                → Agent 入口（用户画像/路由/规则/技能查找）
    ├── Codex 总入口.md
    └── Archive/
        └── 2026-06-22_09-35-25_Codex_Import/
            ├── Memory/Raw/
            │   ├── memory_summary.md    → 用户记忆快照
            │   ├── MEMORY.md
            │   ├── skills/             → 技能相关记忆
            │   └── rollout_summaries/
            └── Skills/
                ├── merged_skill_manifest.json  → 453 技能清单
                ├── skill_manifest.json         → 558 原始记录
                ├── 完整 Skill 档案索引.md       → 按 ID 索引
                └── Merged Skill Notes/         → 每个技能含完整 SKILL.md 内容
                    └── *.md (453 文件)
```

## 互通策略

### 能直接用（双向参考）
- **AGENT_CONTEXT.md 的用户模型** — 你说中文/执行优先等偏好，和我的记忆互为印证
- **工作空间路由** — `~/Documents/乱七八糟` / `New project 3` / `New project 4`
- **问题库** — 可读可分析可处理
- **Skills/ 中文分类** — 你的技能全景图，我能读

### 只读参考（需桥接）
- **Archive 里的 453 个 Codex 技能** — 每个 merged note 包含完整 SKILL.md 内容，我可以读，但不能用 Hermes `skill_view()` 加载或调用
- **Memory 快照** — 是 Codex 侧的，我的记忆系统在 `~/.hermes/memories/`

### 可迁移（Codex → Hermes）
- 选择性地把 Codex 技能转成 `~/.hermes/skills/` 下的 SKILL.md
- 格式差异：Codex SKILL.md 只需 name/description 的 YAML frontmatter；Hermes 格式更丰富（tags/related_skills/linked_files）

## 关键判断

### 两边都有的 8 个技能（无需迁移）
1. `libtv-skill`
2. `code-review-and-quality`
3. `debugging-and-error-recovery`
4. `context-engineering`
5. `performance-optimization`
6. `security-and-hardening`
7. `frontend-ui-engineering`
8. `browser-testing-with-devtools`

### Codex 独有且可能值得迁移的集群
- **编码/工具**: `skill-installer`, `openai-api-troubleshooting`, `chatgpt-apps`, `agents-sdk`
- **前端**: `figma-implement-design`, `frontend-design`, `popular-web-designs` 等更深入的变体
- **研究**: `deep-research`, `paper-search-pro`, `agent-reach`（17 平台搜索）
- **商业**: `marketing-plan`, `ads`, `cold-email`, `seo-audit`, `copywriting` 等 ~20 个
- **安全**: `security-audit`, `vulnerability-scan`, `compliance-check`
- **文档**: `google-docs`, `google-slides` 等 G Suite 集成
- **影视**: `camera-director`, `director-master`, `screenplay-master`
- **测试**: `playwright`, `browser-cdp`, `testing-gen`
- **元技能**: `using-agent-skills`, `idea-refine`, `doubt-driven-development`

### 插件缓存技能（211 个）
- 来自 `~/.codex/plugins/cache`，量大但多数是特定插件的辅助 prompt
- 通常不值得全量迁移，按需提取

## 使用时机

当用户问 "我的 Obsidian 里有什么技能可以用"、"这个 Codex 技能能不能给我装上"、"Archive 里有没有做 X 的 skill" 时，加载本 Skill。
