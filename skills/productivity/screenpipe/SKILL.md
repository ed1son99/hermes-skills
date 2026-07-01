---
name: screenpipe
description: Local-first screen and audio capture for AI agent long-term memory. Records what you've seen, said, and heard — searchable via MCP. Use when the user needs to recall past screen content, find something they saw earlier, or give the agent persistent visual/audio memory.
version: "1.0.0"
metadata:
  author: screenpipe (https://screenpi.pe)
  tags: screen-capture, memory, mcp, audio, productivity
compatibility: macOS, Windows, Linux. Requires screenpipe app installed.
---

# Screenpipe

Local-first screen and audio recording that gives your AI agent persistent memory of everything you've seen, said, and heard. Fully on-device, no cloud upload.

## Setup

1. Install screenpipe: `curl -fsSL https://screenpi.pe/install.sh | bash`
2. Add MCP config:

```yaml
mcp_servers:
  screenpipe:
    command: npx
    args: ["-y", "screenpipe-mcp"]
```

## Available Tools

- **search** — Search past screen content by text query
- **get_activity_summary** — Summary of what you worked on in a time range
- **get_meeting_detection** — Detect when you were in meetings
- **get_screenshots** — Retrieve screenshots from a time range

## Usage Examples

- "What was I looking at yesterday around 3pm?"
- "Search for that article about React hooks I saw last week"
- "Summarize what I worked on this morning"
- "Find the meeting notes from Tuesday's standup"
