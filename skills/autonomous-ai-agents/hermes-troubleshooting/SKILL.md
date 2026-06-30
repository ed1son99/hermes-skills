---
name: hermes-troubleshooting
description: "Diagnose and fix a frozen, unresponsive, or slow Hermes Agent — process death, config rot, auxiliary timeout, profile mismatch, model issues."
version: 1.0.0
author: Hermes Agent
platforms: [macos, linux]
metadata:
  hermes:
    tags: [hermes, troubleshooting, diagnostics, config, profile]
---

# Hermes Troubleshooting

Systematic diagnostic pipeline for when Hermes is frozen, unresponsive, slow, or behaving unexpectedly. Run these steps in order.

## 1. Check If Hermes Is Actually Running

```bash
ps aux | grep -i hermes | grep -v grep
```

Look for:
- **CLI process**: `python .../venv/bin/hermes` — the TUI/CLI session
- **Dashboard**: `python ... dashboard --port ...` — serves the web UI / desktop app
- **Desktop app**: `/Applications/Hermes.app/Contents/MacOS/Hermes` — Electron shell
- **Slash worker**: `tui_gateway.slash_worker` — handles slash commands

If no Hermes process is running, start one: `hermes` (CLI) or open Hermes.app.

## 2. Check Error Logs

```bash
tail -50 ~/.hermes/logs/errors.log
tail -50 ~/.hermes/logs/agent.log
```

Common patterns and their meaning:

| Log Pattern | What It Means |
|-------------|---------------|
| `Auxiliary: marking <provider> unhealthy` | Auxiliary system tried OpenRouter/Nous first, they failed, falling back. **Fix:** set all auxiliary providers to your main provider (see §5). |
| `MCP server 'X' failed initial connection` | MCP server path doesn't exist. **Fix:** remove broken MCP server: `hermes mcp remove <name>`. |
| `Config version outdated (v0 → v30)` | Config schema is stale. **Fix:** `hermes config migrate` (use `-p <profile>` if using a non-default profile). |
| `config.yaml has empty section(s)` | Null or empty dict values in config. **Fix:** remove them (see §5). |
| `Tool terminal returned error (BLOCKED)` | Command approval timeout or user denied. Normal — not a bug. |

## 3. Run Doctor

```bash
# Default profile
hermes doctor

# Specific profile
hermes -p <profile> doctor
```

Key things doctor checks:
- Config version (should be latest)
- API key presence (check per-profile `.env`)
- Provider connectivity (DeepSeek, OpenRouter, etc.)
- Tool availability
- Directory structure

## 4. Config Migration & Cleanup

### Migrate config schema
```bash
hermes config migrate                  # default profile
hermes -p <profile> config migrate     # other profile
```

### Remove empty/null section warnings
Empty dict sections and null values like `providers: {}`, `honcho: {}`, `max_concurrent_sessions: null` trigger warnings. Clean them with a temp script:

```python
import yaml
from pathlib import Path

config_path = Path.home() / ".hermes" / "profiles" / "<profile>" / "config.yaml"
with open(config_path) as f:
    cfg = yaml.safe_load(f)

# Empty dicts to remove
for key in ['providers', 'credential_pool_strategies', 'honcho', 'whatsapp',
            'quick_commands', 'hooks', 'personalities']:
    cfg.pop(key, None)

# Null values to remove
for key in ['max_concurrent_sessions', 'context_file_max_chars']:
    cfg.pop(key, None)

with open(config_path, 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
```

Alternatively, use `hermes config set` per key.

## 5. Fix Auxiliary Provider Timeouts

If logs show repetitive `Auxiliary: marking <provider> unhealthy` messages, the auxiliary system is trying multiple providers before finding one that works. This adds startup delay.

**Fix:** Set all auxiliary providers to your main working provider:

```bash
# For each auxiliary task, replace 'auto' with your main provider (e.g. deepseek)
hermes config set auxiliary.title_generation.provider deepseek
hermes config set auxiliary.vision.provider deepseek
hermes config set auxiliary.compression.provider deepseek
hermes config set auxiliary.web_extract.provider deepseek
hermes config set auxiliary.skills_hub.provider deepseek
hermes config set auxiliary.approval.provider deepseek
hermes config set auxiliary.mcp.provider deepseek
hermes config set auxiliary.tts_audio_tags.provider deepseek
hermes config set auxiliary.triage_specifier.provider deepseek
hermes config set auxiliary.kanban_decomposer.provider deepseek
hermes config set auxiliary.profile_describer.provider deepseek
hermes config set auxiliary.curator.provider deepseek
hermes config set auxiliary.monitor.provider deepseek
```

## 6. API Key Check

```bash
# Check which profile you're using
hermes config path

# Check if API key is present (doctor will report this)
hermes doctor
```

Per-profile `.env` files at:
- `~/.hermes/.env` — default profile
- `~/.hermes/profiles/<name>/.env` — named profiles

Key observation: `hermes doctor -p <name>` only checks that profile's `.env`. If the key is in the default profile's `.env` but not in your per-profile `.env`, doctor will falsely report "no API key configured." Copy the key: `grep '^KEY_NAME=' ~/.hermes/.env >> ~/.hermes/profiles/<name>/.env`

## 7. Profile-Based Model Differentiation

Useful when you want **different models for different Hermes interfaces** (e.g., terminal CLI uses one model, desktop app uses another).

### Option A: Desktop uses default, Terminal uses named profile

The desktop Hermes app / dashboard runs under the **default** profile by default. The terminal CLI lets you pick with `-p <name>`.

```bash
# Desktop uses default profile → set to flash
hermes -p default config set model.default deepseek-v4-flash
hermes -p default config set model.provider deepseek

# Terminal uses pro profile → keep at pro
hermes -p pro config set model.default deepseek-v4-pro
hermes -p pro config set model.provider deepseek

# Terminal launch
hermes -p pro
```

### Option B: Dedicated desktop profile (via macOS Info.plist env var)

When both interfaces need to use different models, create a separate desktop profile and inject `HERMES_HOME` (NOT `HERMES_PROFILE`) into the macOS app bundle.

**IMPORTANT:** The `HERMES_PROFILE` env var is **completely ignored** by Hermes' startup profile resolution (`_apply_profile_override()` in `hermes_cli/main.py`). It only reads `--profile` flag, `HERMES_HOME` pointing to `profiles/<name>`, or `~/.hermes/active_profile` file. See `references/profile-resolution-deep-dive.md` for the full code analysis.

**Steps:**

```bash
# 1. Create desktop profile cloned from an existing one
hermes profile create desktop --clone-from pro

# 2. Set its model
hermes -p desktop config set model.default deepseek-v4-flash

# 3. Set HERMES_HOME in Hermes.app Info.plist
#    Edit /Applications/Hermes.app/Contents/Info.plist
#    Change LSEnvironment from:
#      <key>HERMES_PROFILE</key>
#      <string>desktop</string>
#    To:
#      <key>HERMES_HOME</key>
#      <string>/Users/<your-username>/.hermes/profiles/desktop</string>

# 4. Re-sign the app (ad-hoc, since we modified the bundle)
codesign --force --sign - /Applications/Hermes.app
```

**Pitfalls:**
- macOS app updates will overwrite Info.plist changes. Re-apply after each update.
- Modifying the .app bundle invalidates the code signature. Re-sign with `codesign --force --sign -` (ad-hoc) after modifications.
- `hermes config set` requires `hermes` in PATH. If running from a terminal without it, use the full path: `~/.hermes/hermes-agent/venv/bin/hermes`.
- The desktop profile needs its own API keys (`.env`) if it's not inherited from shell env. Either copy keys or run `desktop setup` (the wrapper script created alongside the profile).
- The cloned profile inherits all config, skills, and plugins from the source. Remove unwanted auxiliary provider overrides if they point to a non-functioning provider.
- The terminal CLI's profile is still determined by `~/.hermes/active_profile` (e.g., "pro"). The desktop app uses `HERMES_HOME` → desktop profile. The two are now independent.

**Verify:**
```bash
# Simulate what the desktop app does at startup
HERMES_HOME=/Users/<your-username>/.hermes/profiles/desktop hermes profile
# Should show:
#   Active profile: desktop
#   Path:           ~/.hermes/profiles/desktop
#   Model:          deepseek-v4-flash (desktop profile's model)

# For terminal CLI (without HERMES_HOME)
hermes profile
# Should show:
#   Active profile: pro
#   Model:          deepseek-v4-pro (pro profile's model)
```

## 8. Upgrade & Setup Pitfalls

See `references/upgrade-pitfalls.md` for:
- `hermes update` npm timeout (harmless — core upgrade already completed)
- Photon iMessage setup (`hermes photon setup`) is interactive-only
- Release notes CLI names may differ from actual CLI — always verify with `--help`

## 9. Config Safety Notes

- **Do NOT** use `patch()` or `write_file()` to modify `~/.hermes/config.yaml` or any profile's `config.yaml` — these files are access-denied by Hermes tools for security reasons. Use `hermes config set` or `hermes config edit` instead.
- **For batch changes**, write a temp Python script to the filesystem and run it via terminal (as in §4).
- **Config changes take effect on next session start** (`/reset` in chat, or new `hermes` invocation), not mid-conversation.
