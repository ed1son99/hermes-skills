---
name: ai-pipeline-orchestrator
description: Orchestrate multi-AI pipelines: Hermes coordinates Claude (brain/reviewer) and Codex (executor/writer) in a chained workflow
triggers: [ai-pipeline-orchestrator, multi-agent, pipeline, orchestration, claude, codex, coordination, workflow, orchestrate, ai, hermes]
platforms: [claude-code, hermes, codex]
---

# AI Pipeline Orchestrator

Orchestrate multiple AI agent CLIs in a coordinated pipeline, with Hermes as the central conductor. The standard pipeline:

```
User → Hermes → [Claude = Brain] → [Codex = Hands] → [Claude = Reviewer] → Hermes → User
```

## When to Use

- Complex tasks that benefit from **multiple AI perspectives**
- Tasks wanting Claude's strategic thinking + Codex's execution
- Any workflow requiring: **plan → execute → review → deliver**
- When you want Hermes to **coordinate**, not just execute on its own

## Prerequisites

### Required CLIs

| Agent | Role | Install |
|-------|------|---------|
| **Claude Code CLI** | Strategic advisor + reviewer | `npm install -g @anthropic-ai/claude-code` |
| **Codex CLI** | Execution/writer | `npm install -g @openai/codex` |

### Verify Installation

```bash
claude --version && claude auth status
codex --version && codex login status
```

### macOS Desktop App Paths

If Codex was installed via the macOS desktop app, the binary is at:
```
/Applications/Codex.app/Contents/Resources/codex
```
Add a shell alias to make it accessible:
```bash
alias codex=/Applications/Codex.app/Contents/Resources/codex
```

**Important distinction:** `Claude.app` (macOS desktop GUI) does NOT include `claude` (Claude Code CLI). They are separate products. Claude.app cannot be called from the command line.

## Pipeline Architecture

### Standard 4-Step Pipeline

```
Step 1: Claude as Brain (advise)
  → Hermes asks Claude for strategic advice on the task
  → Returns: high-level plan, approach, considerations, edge cases

Step 2: Codex as Hands (execute)
  → Hermes feeds Claude's advice to Codex as context
  → Codex writes files, code, plans, documentation
  → Returns: concrete artifacts

Step 3: Claude as Reviewer (verify)
  → Hermes feeds Codex's output to Claude for review
  → Claude checks: correctness, completeness, edge cases, soundness
  → Returns: approval, revisions needed, or concerns

Step 4: Hermes Delivers
  → Hermes synthesizes: problem → Claude's advice → Codex's work → Claude's review
  → Deliver complete package to user
```

### Pipeline Diagram

```
                      ┌─────────────────┐
                      │   User (Task)    │
                      └────────┬────────┘
                               │
                      ┌────────▼────────┐
                      │  Hermes (Orch)  │
                      └────────┬────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                                   ▼
   ┌─────────────────┐                 ┌─────────────────┐
   │  Claude = Brain  │                 │ Codex = Hands   │
   │  (plan / advise)  │                 │ (write / exec)  │
   └────────┬─────────┘                 └────────┬────────┘
            │                                     │
            └──────────────┬──────────────────────┘
                           ▼
                  ┌─────────────────┐
                  │ Claude = Review  │
                  │ (verify sound)   │
                  └────────┬────────┘
                           │
                  ┌────────▼────────┐
                  │  Hermes → User  │
                  └─────────────────┘
```

### Variants

| Variant | Description | When |
|---------|-------------|------|
| **Quick pipeline** | Skip review step (brain → exec → deliver) | When speed matters more than verification |
| **Iterative loop** | If review fails, loop steps 2-3 | When quality is critical |
| **Double brain** | Ask both Claude and Codex for plans, then compare | When exploring multiple approaches |
| **Multi-executor** | Run multiple executors in parallel on subtasks | Large projects with independent modules |
| **Hermes-only** | Hermes does all steps itself | When the task doesn't need external AI perspectives |
| **Swap roles** | Codex plans, Claude executes | When you want Codex's approach with Claude's implementation |

## How to Call Each Agent from Hermes

### Claude Code (Print Mode — Preferred)

One-shot, non-interactive, exits when done:

```bash
claude -p "Your strategic question" --max-turns 5 --output-format text
```

For structured output:
```bash
claude -p "Analyze this and list risks" --max-turns 3 --output-format json
```

### Claude Code (Full Task with Context)

Pipe context in, get analysis out:

```bash
echo "$CONTEXT" | claude -p "Review this plan. Is it sound?" --max-turns 3
```

### Codex CLI

```bash
codex exec "Write implementation based on this plan" --full-auto
```

### Codex via Direct Binary (macOS Desktop App)

When installed via Codex.app (not npm):

```bash
/Applications/Codex.app/Contents/Resources/codex exec "Task description" --full-auto
```

## Hermes Implementation Pattern

When Hermes runs this pipeline, the pattern is:

```python
# Inside Hermes execute_code or terminal:

# Step 1: Ask Claude for advice
step1 = terminal("claude -p '...' --max-turns 5", timeout=120)
claude_advice = step1["output"]

# Step 2: Feed advice to Codex for execution
step2 = terminal("echo $PLAN | codex exec 'Implement this plan' --full-auto", timeout=300)
codex_output = step2["output"]

# Step 3: Claude reviews the result
step3 = terminal("echo $WORK | claude -p 'Review this. Issues?' --max-turns 3", timeout=120)
claude_review = step3["output"]

# Step 4: Hermes synthesizes and delivers
# Combine all outputs and present final result to user
```

## Pitfalls & Gotchas

1. **Claude.app ≠ Claude Code CLI** — The macOS Claude desktop app (`/Applications/Claude.app`) cannot be scripted from the command line. For CLI access you need `npm install -g @anthropic-ai/claude-code`.

2. **Separate auth per agent** — Each CLI has its own authentication. `claude auth login` (browser OAuth) and `codex login` are independent. A user logged into one may not be logged into the other.

3. **Timeouts compound** — Each pipeline step is sequential, and each can take significant time. A 3-step pipeline may need 300-600+ seconds total. Set generous per-step timeouts.

4. **Context loss between steps** — Agent output doesn't automatically feed into the next agent. Hermes must explicitly pass context via files, pipes, or summaries. Save step outputs to /tmp/ as you go.

5. **Cost accumulation** — Each Claude Code call burns tokens (system prompt + conversation). Set `--max-turns` conservatively. The review step usually needs fewer turns than the planning step.

6. **Git state discipline** — Codex may modify workspace files. Always ensure clean `git status` before running the pipeline, and use `git diff` to review changes before committing.

7. **Sequential by design** — Steps depend on previous outputs. Don't run steps 2 and 3 concurrently unless the task structure allows independent subtasks.

8. **Codex workspace sandbox** — When invoked from a Hermes gateway/service context, Codex's `workspace-write` sandboxing may fail with user-namespace errors. Prefer `codex exec --sandbox danger-full-access "..."` in that case.

## Quick Reference

```bash
# Step 1: Claude advises
claude -p "What's the best approach to [TASK]?" --max-turns 5 > /tmp/step1-advice.md

# Step 2: Codex writes (using advice as context)
cat /tmp/step1-advice.md | codex exec "Based on this plan, implement it" --full-auto

# Step 3: Claude reviews
git diff | claude -p "Review these changes. Issues?" --max-turns 3 > /tmp/step3-review.md

# Step 4: Hermes delivers — synthesize all three outputs
cat /tmp/step1-advice.md /tmp/step3-review.md
```
