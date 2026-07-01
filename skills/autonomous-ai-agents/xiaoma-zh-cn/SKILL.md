---
name: xiaoma-zh-cn
description: Chinese localization and onboarding for Hermes Agent. One-command installer applies zh-CN UI text patches, gateway prompts, and pairing messages for Hermes 0.14.x/0.13.x. Use when setting up Hermes in Chinese or localizing an existing Hermes installation.
version: "1.0.0"
metadata:
  author: fresh-claw (xiaoma)
  tags: chinese, localization, hermes, zh-cn, i18n
compatibility: Hermes Agent 0.13.x/0.14.x, Linux/macOS/WSL
---

# Xiaoma — Hermes 中文本地化

Hermes Agent 的一键中文本地化包。安装后自动应用简体中文 UI 文本、网关提示语和配对消息。

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/fresh-claw/hermes-zh-cn/main/install.sh | bash
```

## 功能

- Hermes CLI 中文提示
- 网关消息中文配对
- 中文会话开场白
- 中文本地化帮助文档

## 使用

安装后重启 Hermes，界面自动变为简体中文。
如需还原英文，运行安装目录下的 `uninstall.sh`。
