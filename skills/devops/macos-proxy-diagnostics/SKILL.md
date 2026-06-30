---
name: macos-proxy-diagnostics
description: Systematic diagnosis of macOS proxy/VPN/TUN clients: detect when a proxy process is running but not actually proxying traffic.
triggers: [macos-proxy-diagnostics, macos, proxy, vpn, v2ray, network, troubleshooting, diagnostics, systematic, tun]
platforms: [claude-code, hermes, codex]
---

# macOS Proxy Diagnostics

## Overview

macOS proxy clients (v2rayN, Clash, Surge, Quantumult, Shadowrocket) can appear to be running — process alive in Activity Monitor — while actually doing nothing. The GUI process and even the proxy core can linger as dangling processes that serve only an API port without proxying any traffic.

**Key insight: a running proxy GUI does NOT mean the proxy is working.**

## Diagnostic Checklist

Run these checks in order to locate the failure point.

### 1. Process Status — Is the app + core running?

```bash
# Check proxy app and core processes
ps aux | grep -iE "(clash|v2ray|xray|trojan|sslocal|shadowrocket|surge|quantumult|hiddify|nekoray|nekobox|mihomo|sing-box)" | grep -v grep
```

**Possible states:**
- **Both app + core running** → proceed to check 2
- **App running, no core** → the proxy app never started the core (check logs)
- **Neither running** → app crashed or was never started
- **App running, core running but old PID** → core may be a dangling orphan (check 4)

### 2. System Proxy Settings

```bash
# Check if macOS system proxy is configured
scutil --proxy
# Check specific network interface
networksetup -getwebproxy Wi-Fi
networksetup -getsecurewebproxy Wi-Fi
networksetup -getsocksfirewallproxy Wi-Fi
```

Key fields: `HTTPEnable : 1` means system proxy is active. If `HTTPEnable : 0` but the app is in system-proxy mode, the proxy never started.

### 3. TUN Interface & Routing

```bash
# List all TUN/TAP interfaces
ifconfig | grep -A2 -E "^(utun|tap|tun)"
# Show routing table
netstat -rn -f inet
```

**TUN mode working:** You should see a utun interface (utun30, utun3, etc.) with routes like `1.0.0.0/1` + `128.0.0.0/1` pointing to it — these two routes combined cover all public IPv4.

**TUN mode broken:** No TUN interface exists, default route is the WiFi/LAN gateway.

> **macOS TUN privilege note:** Creating a TUN interface requires root privileges. If the app failed to escalate privileges (no sudo password, macOS denied helper tool), TUN will silently not work.

### 4. Core Listening Ports

```bash
# Check what the proxy core is actually listening on
lsof -i -P | grep -E "(v2ray|xray|clash|mihomo|trojan)"
```

**Healthy:** Should see actual proxy ports (SOCKS :10808, HTTP :7897, mixed :7890, etc.)

**Broken (dangling core):** Only the API/management port (e.g. xray :50713, clash API :9090) is open. This means the core started but isn't doing any proxying.

### 5. Actual Connectivity Test

```bash
# Test foreign vs domestic access
curl -s --connect-timeout 5 -o /dev/null -w "%{http_code}" https://www.google.com
curl -s --connect-timeout 5 -o /dev/null -w "%{http_code}" https://www.baidu.com
```

| Google | Baidu | Meaning |
|--------|-------|---------|
| 200 | 200 | Proxy not working, direct access (only if in China) |
| 000 | 200 | **Proxy broken** — foreign traffic blocked, domestic works direct |
| 200 | △ | Proxy working correctly |

`000` on foreign + `200` on domestic is the classic "proxy dead" signal.

### 6. App Logs

Find and inspect the proxy app's logs for startup errors:

```bash
# v2rayN
cat ~/Library/Application\ Support/v2rayN/guiLogs/$(date +%Y-%m-%d).txt

# Clash/Mihomo
cat ~/.config/clash/logs/*.log

# General macOS console
log show --predicate 'subsystem contains "proxy" OR process contains "v2ray"' --last 10m
```

Look for:
- Missing "Core started" or equivalent message
- Error messages about privilege escalation
- Config file not found errors
- Silent start with no subsequent proxy-related messages

## Common Failure Patterns

### Pattern A: Dangling Core (v2rayN most common)

**Symptoms:** v2rayN GUI + xray process both running, but `utun30` missing, no proxy ports listening, Google returns `000`.

**Root cause:** The xray process is a leftover from a previous session — it only serves the API port and does no proxying. The GUI never successfully launched the core in TUN/system-proxy mode.

**Fix:** 
1. Kill the dangling xray: `kill <xray_pid>`
2. Open v2rayN GUI
3. Click the **system proxy toggle** or **TUN mode button** to re-launch the core
4. Or restart v2rayN entirely

### Pattern B: TUN Privilege Failure

**Symptoms:** App configured for TUN mode, but no TUN interface created.

**Root cause:** macOS requires root/sudo for TUN. The privilege escalation (run_as_sudo.sh, helper tool, or AuthorizationExecuteWithPrivileges) was denied or failed silently.

**Fix:** 
- Manually approve the privilege prompt when it appears
- Or switch to system proxy mode (doesn't need root)
- Or run the proxy core with sudo manually

### Pattern C: System Proxy Not Set

**Symptoms:** App in system proxy mode, but `scutil --proxy` shows all disabled.

**Root cause:** The app failed to set macOS system proxy settings, possibly due to macOS permission changes.

**Fix:** Toggle the proxy mode off and on again in the app GUI, or set manually via System Settings → Network → Proxies.

### Pattern D: Core Process Died Silently

**Symptoms:** GUI running, core process absent.

**Root cause:** Core crashed on startup — bad config, incompatible core version, or resource issue.

**Fix:** Check logs for crash reason, validate config file, update core binary.

### Pattern E: TUN Privilege Failure → Fall Back to System Proxy (v2rayN)

**Symptoms:** v2rayN in TUN mode, no TUN interface, core API port only — user sees "proxy dead" despite process running.

**Root cause:** TUN mode on macOS requires root. If privilege escalation fails silently, the core never creates the TUN interface and may not listen on any proxy port.

**Fix — switch to system proxy mode (no root needed):**

1. **Kill dangling core** — `pkill -f "xray.*config.json"`
2. **Modify v2rayN guiConfig** — edit `~/Library/Application Support/v2rayN/guiConfigs/guiNConfig.json`:
   - Set `TunModeItem.EnableTun: false`
   - Set `SystemProxyItem.SysProxyType: 2` (SOCKS5 proxy mode)
3. **Restart v2rayN** — `open /Applications/v2rayN.app` (or kill+reopen)
4. **Verify** — SOCKS port should now be listening on the configured port (usually 10808)

Alternatively, manually set the SOCKS proxy after the core starts:
```bash
networksetup -setsocksfirewallproxy Wi-Fi 127.0.0.1 10808
networksetup -setsocksfirewallproxystate Wi-Fi on
```
Verify with `scutil --proxy` — should show `SOCKSEnable : 1`.

### Pattern F: DNS Poisoning (GFW Interception)

**Symptoms:** Proxy connects but all foreign sites time out. Rapid `000` or timeouts on Google, but `nc -zv` shows TCP to the proxy server IP succeeds.

**Root cause:** The proxy server domain (e.g. `direct.miyaip.online`) is resolved by the system DNS to a poisoned IP (e.g. 1.1.1.1) instead of the real server IP. The proxy then connects to a decoy that doesn't respond.

**Detection:**
```bash
# Compare DNS results
dig @8.8.8.8 <proxy-domain> A +short     # real IP
dig @119.29.29.29 <proxy-domain> A +short # real IP (China DNS)
host <proxy-domain>                         # system DNS — may show different/poisoned IP
```

**Fix — use the real IP directly:**
1. Find the real IP: `dig @8.8.8.8 proxy.example.com A +short`
2. Replace the domain with the IP in the proxy core's config file:
   ```bash
   # e.g. for xray config
   patch ... "address": "27.44.141.81", "address": "proxy.example.com",
   ```
3. Restart the proxy core

**Prevention:** Configure the proxy app to use a trusted DNS (e.g. 8.8.8.8, 119.29.29.29) for outbound resolution, or hardcode the server IP instead of the domain.

### Pattern G: Missing Geo Routing Files (xray)

**Symptoms:** xray fails to start with:
```
Failed to start: main: failed to load config files: ... > infra/conf: failed to load geosite: GOOGLE > open geosite.dat: no such file or directory
```

**Root cause:** xray expects `geosite.dat` and `geoip.dat` in its own binary directory (`bin/xray/`), but v2rayN stores them in the parent `bin/` directory.

**Fix:**
```bash
ln -sf "/Users/shabi/Library/Application Support/v2rayN/bin/geosite.dat" \
      "/Users/shabi/Library/Application Support/v2rayN/bin/xray/geosite.dat"
ln -sf "/Users/shabi/Library/Application Support/v2rayN/bin/geoip.dat" \
      "/Users/shabi/Library/Application Support/v2rayN/bin/xray/geoip.dat"
```

### Running xray Directly (Without v2rayN GUI)

When the v2rayN GUI won't auto-restart the core after a config change, run xray manually:

```bash
# Kill old core
pkill -f "xray.*config.json"

# Start with modified config in background
"/Users/shabi/Library/Application Support/v2rayN/bin/xray/xray" run \
  -c "/Users/shabi/Library/Application Support/v2rayN/binConfigs/config.json" &

# Verify
lsof -i :10808 -P
curl -s --connect-timeout 10 -x socks5://127.0.0.1:10808 \
  -o /dev/null -w "%{http_code}" https://www.google.com
```

> **Note:** This is a temporary fix — v2rayN may overwrite config.json if it restarts the core. For persistence, modify the guiNConfig.json (Pattern E) so v2rayN generates correct configs on its own.

## Pitfalls

- **"Process alive = proxy working" is a trap.** Always check routing table and listening ports.
- **macOS TUN mode is fragile.** It needs escalated privileges that can be denied silently.
- **v2rayN app restart cycles** (OnClosing → start again) without a "Core started" log entry means the core was never launched.
- **Don't confuse the v2rayN GUI process with the xray core** — they're separate processes.
- **System proxy exceptions** can mask problems: if DNS or local addresses are excepted, domestic sites may work while proxy appears broken for foreign traffic.
- **WiFi vs Ethernet:** Proxy settings are per-interface. If you switch networks, the proxy config might not carry over.

## Related Skills

- `systematic-debugging` — general 4-phase debugging methodology
