# Hermes Agent Skills

Collection of 79 reusable AI agent skills across 17 categories — the knowledge base that powers [Hermes Agent](https://hermes-agent.nousresearch.com).

## Categories

| Category | Skills | Description |
|---|---|---|
| **apple** | 5 | macOS ecosystem: Notes, Reminders, FindMy, iMessage, Computer Use |
| **autonomous-ai-agents** | 5 | Multi-agent orchestration: Claude Code, Codex, OpenCode, Hermes self-config |
| **creative** | 17 | Design & media: SVG diagrams, ASCII art/video, Canvas 3D/2D, Excalidraw, Manim, p5.js, ComfyUI, infographics, music |
| **data-science** | 1 | Jupyter live kernel for iterative Python |
| **devops** | 3 | Kanban orchestration, macOS proxy diagnostics |
| **email** | 1 | Himalaya CLI for IMAP/SMTP |
| **github** | 6 | Full GitHub workflow: auth, PRs, code review, issues, repos, codebase stats |
| **media** | 4 | YouTube transcripts, GIF search, music generation, audio spectrograms |
| **mlops** | 8 | HuggingFace Hub, vLLM, llama.cpp, AudioCraft, SAM, W&B, lm-eval-harness |
| **note-taking** | 2 | Obsidian vault management & Codex bridge |
| **productivity** | 8 | Airtable, Google Workspace, Notion, PowerPoint, Maps, PDF, OCR, Teams |
| **research** | 5 | arXiv, blog monitoring, LLM Wiki, Polymarket, paper writing |
| **smart-home** | 1 | Philips Hue via OpenHue |
| **social-media** | 1 | X/Twitter via xurl CLI |
| **software-development** | 9 | Plan, spike, TDD, systematic debugging, code review, simplify, debugpy, Node inspect, skill authoring |
| **dogfood** | 1 | Web app exploratory QA |
| **yuanbao** | 1 | 元宝 groups integration |

## Structure

Each skill lives in `skills/<category>/<name>/` with:
- `SKILL.md` — YAML frontmatter + markdown workflow instructions
- `references/` — API docs, cheat sheets
- `scripts/` — Helper scripts (Python/Bash)
- `templates/` — Boilerplate files

## Usage

These skills are loaded by Hermes Agent at runtime. To use one:

```
skill_view(name='category/skill-name')
```

## License

MIT
