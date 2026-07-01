---
name: meigen-design
description: Multi-model AI image and video generation via MeiGen — supports GPT Image 2, Nanobanana 2, Seedream 5.0, Midjourney V8.1, Flux 2 Klein, Seedance 2.0, Happyhorse 1.0, Veo 3.1, and local ComfyUI. Use when the user wants to generate, edit, or transform images and videos using state-of-the-art AI models.
version: "1.0.0"
metadata:
  author: Community (MeiGen)
  tags: image-generation, video-generation, midjourney, flux, comfyui, ai-art
compatibility: Requires MCP server running (meigen-mcp) or MeiGen cloud API key
---

# MeiGen AI Design

Generate images and videos using 9 leading AI models through a single MCP server.

## Setup

Add to your `mcp_servers` config:

```yaml
mcp_servers:
  meigen:
    command: npx
    args: ["-y", "@jau/meigen-mcp"]
    env:
      MEIGEN_API_KEY: "${MEIGEN_API_KEY}"
    timeout: 300 # video gen can take minutes
```

Get a key at [MeiGen cloud](https://meigen.ai) or use your own OpenAI-compatible API endpoint.

## Supported Models

| Model | Type | Best For |
|-------|------|----------|
| GPT Image 2 | Image | General purpose, photorealistic |
| Midjourney V8.1 | Image | Artistic, stylized |
| Flux 2 Klein | Image | Fast, high quality |
| Seedream 5.0 | Image | Cinematic, dreamlike |
| Nanobanana 2 | Image | Anime, illustrations |
| Seedance 2.0 | Video | Short video clips |
| Happyhorse 1.0 | Video | Fast video gen |
| Veo 3.1 | Video | High quality video |
| ComfyUI (local) | Both | Fully offline, custom workflows |

## Usage

```bash
# Generate image
meigen generate --model "midjourney-v8-1" --prompt "a serene mountain lake at sunset"

# Generate video
meigen generate --model "veo-3-1" --prompt "a dog running on a beach"

# Edit image
meigen edit --image path/to/image.jpg --prompt "add a rainbow in the sky"
```
