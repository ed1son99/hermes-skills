# Hermes Upgrade Pitfalls

## `hermes update` npm timeout is harmless

When running `hermes update`, the npm install step for the desktop app sidecar may time out (120s+). The core agent upgrade (Python venv) completes first and is NOT blocked by the npm step. After the timeout:

```bash
hermes version   # Will show the new version even if npm timed out
```

The desktop app will pick up the new frontend on next launch — the npm timeout only delays desktop UI availability, not the agent core.

## Photon iMessage setup is interactive-only

`hermes photon setup` requires:
1. Browser OAuth (device code flow) — opens a URL, waits for user to approve
2. TTY input (phone number prompt)
3. NPM sidecar install

It **cannot** be run non-interactively from within the agent's own terminal/bin. The agent should tell the user to run it themselves in their own terminal.

## Gateway restart required after Photon setup

After `hermes photon setup` completes, the gateway **must be restarted** to pick up the new Photon credentials and start the gRPC sidecar. If the gateway was already running during setup, it won't see the new config and inbound iMessages will be silently dropped.

```bash
hermes photon setup          # Complete setup first
hermes gateway restart       # Then restart
```

Verify with `hermes photon status` — all four fields (device token, project id, project secret, sidecar deps) should show ✓. Then check gateway logs for `✓ photon connected`.

## Release notes CLI names may not match actual CLI

Example: v0.17.0 release notes mention `hermes photon login`, but the actual CLI uses `hermes photon setup`. Always verify with:

```bash
hermes photon --help        # List available subcommands
hermes photon setup --help  # See options for a specific subcommand
```

The `--help` flag is the source of truth, not release notes.
