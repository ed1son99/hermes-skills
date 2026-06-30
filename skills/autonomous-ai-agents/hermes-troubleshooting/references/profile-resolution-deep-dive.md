# Profile Resolution Deep Dive

How Hermes resolves which profile to use, based on actual code analysis.

## The `_apply_profile_override()` Function

Located in `hermes_cli/main.py`, this function runs BEFORE argparse to set `HERMES_HOME` before imports.

### Resolution Order

1. **`--profile` / `-p` flag** — explicit CLI argument
   ```bash
   hermes -p desktop       # → uses desktop profile
   ```
   Highest priority. Even `HERMES_HOME` env var or `active_profile` file is ignored.

2. **`HERMES_HOME` env var pointing to `profiles/<name>`** — e.g. `HERMES_HOME=/Users/shabi/.hermes/profiles/desktop`
   If set, and the parent directory's name is literally `"profiles"`, the function returns early without checking `active_profile`:
   ```python
   hermes_home_env = os.environ.get("HERMES_HOME", "")
   if profile_name is None and hermes_home_env:
       if Path(hermes_home_env).parent.name == "profiles":
           return
   ```
   This is the mechanism the macOS desktop app should use (via `Info.plist`).

3. **`~/.hermes/active_profile` file** — sticky default set via `hermes profile use <name>`
   ```bash
   hermes profile use pro   # writes "pro" to ~/.hermes/active_profile
   hermes profile use desktop  # writes "desktop"
   ```
   Read by `get_active_profile()` in `hermes_cli/profiles.py`.

### What DOESN'T Work

**`HERMES_PROFILE` env var is completely ignored** by `_apply_profile_override()`. The variable is only read in niche contexts like kanban worker attribution and code execution env passthrough — never for startup profile resolution.

This means setting `HERMES_PROFILE=desktop` in `/Applications/Hermes.app/Contents/Info.plist` has **zero effect** on which profile Hermes loads.

### The Correct Fix for macOS Desktop App

Instead of `HERMES_PROFILE`, set `HERMES_HOME`:

```xml
<key>LSEnvironment</key>
<dict>
    <key>HERMES_HOME</key>
    <string>/Users/<user>/.hermes/profiles/desktop</string>
    <key>MallocNanoZone</key>
    <string>0</string>
</dict>
```

This passes check #2 (parent dir == "profiles") and the desktop app uses the desktop profile with its own config.

### Verification

```bash
# Simulate what the desktop app does
HERMES_HOME=/Users/shabi/.hermes/profiles/desktop hermes profile
# Should show:
#   Active profile: desktop
#   Path:           ~/.hermes/profiles/desktop
#   Model:          <that profile's model>
```
