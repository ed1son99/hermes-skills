# Session 20260622_090539_dce686 — Diagnosing Frozen Hermes

## Symptoms
- User reported Hermes "died" in terminal
- "最近怎么总卡死" — general slowness/freezing

## Root Causes Found

### 1. Config version outdated (v0 → v30)
`hermes config migrate` upgraded it. After migration, 7 empty dict sections and 2 null values triggered repeated warnings.

### 2. Auxiliary provider thrash
All 13 auxiliary tasks (`vision`, `compression`, `title_generation`, etc.) used `provider: auto`. The auto-detection tried OpenRouter then Nous, both failed with "payment/credit error", and the system retried every ~60s. This added startup delay every session.

**Fix:** Set all to `provider: deepseek`.

### 3. MCP server node_repl failed (default profile only)
Path `/Applications/Codex.app/Contents/Resources/node_repl` doesn't exist. Hermes retried 3 times (1s/2s/4s backoff) before giving up. ~7s startup overhead.

**Fix:** `hermes mcp remove node_repl` in default profile.

### 4. Per-profile .env empty
`pro` profile had a header-only `.env` with no actual keys. `DEEPSEEK_API_KEY` was only in the default profile's `~/.hermes/.env`.

**Fix:** Append key line from default to pro: `grep '^DEEPSEEK_API_KEY=' ~/.hermes/.env >> ~/.hermes/profiles/pro/.env`

## Outcome
After fixes, `hermes doctor` showed green on all critical checks. No more unhealthy-auxiliary spam in logs.
