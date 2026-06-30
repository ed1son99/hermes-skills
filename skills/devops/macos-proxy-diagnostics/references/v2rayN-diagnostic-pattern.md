# v2rayN Diagnostic Pattern (Session Recorded: 2026-06-23)

## Observed Failure

**User symptom:** "为啥这傻逼代理又上不去啊" — proxy not working.

## Diagnostic Sequence

### 1. Process Check
```
ps aux | grep -iE "(clash|v2ray|xray|trojan|sslocal|shadowrocket|surge|quantumult)" | grep -v grep
```
Result: Both `v2rayN` (PID 1636) and `xray` (PID 1698) running.

### 2. System Proxy
```
scutil --proxy
```
Result: `HTTPEnable : 0`, `HTTPSEnable : 0`, `SOCKSEnable : 0` — system proxy not set.

### 3. TUN / Routing
```
ifconfig utun30
netstat -rn -f inet
```
Result: `utun30 NOT found`. Routing table shows default via `172.20.10.1` on `en0` — no TUN routes.

### 4. Core Ports
```
lsof -i -P | grep xray
```
Result: Only `localhost:50713` (TCP+UDP) — this is the API/management port, not a proxy port. No SOCKS (:10808), no HTTP (:7897).

### 5. Connectivity
```
curl google.com → 000 (failed)
curl baidu.com  → 200 (success)
```
Result: Classic "proxy dead" signal — foreign traffic blocked, domestic direct.

### 6. Logs
```
cat ~/Library/Application Support/v2rayN/guiLogs/2026-06-23.txt
```
Result: Only start/close lifecycle logs. **No "Core started" or core-launch entries.** The GUI never triggered the proxy core launch.

## Root Cause (Round 1)

The v2rayN GUI started, registered scheduled tasks, set up helper scripts... but **never launched the xray core in proxy mode**. The running xray process was a dangling leftover from a previous session that only serves the API port (`:50713`) — it doesn't proxy anything.

## Resolution (Round 1 — Incomplete)

Open v2rayN GUI and toggle the proxy on (system proxy button or TUN mode switch), or restart v2rayN completely. The GUI needs to re-launch xray with the full config including TUN/proxy inbounds.

---

## Deep Dive — Why TUN Failed + Additional Fixes

### Finding: v2rayN Configured for TUN Mode

The guiConfig at `~/Library/Application Support/v2rayN/guiConfigs/guiNConfig.json` showed:
```json
"TunModeItem": { "EnableTun": true, "Stack": "gvisor" }
```

TUN mode on macOS needs root privileges. Since the privilege escalation was denied or failed, the core never created the `utun30` interface.

### Fix: Switch to System Proxy Mode

Modified the guiConfig to disable TUN and enable SOCKS system proxy:

1. `TunModeItem.EnableTun: false`
2. `SystemProxyItem.SysProxyType: 2` (SOCKS5 mode)

After restarting v2rayN, the generated config (`binConfigs/config.json`) now had:
- `inbound` SOCKS/mixed on port 10808 ✅
- No TUN protect outbound ✅
- Full DNS section with 119.29.29.29 for direct resolution of proxy domain

### Finding: DNS Poisoning

When xray started, `direct.miyaip.online` was resolved via system DNS → returned `1.1.1.1` (Cloudflare, a GFW poisoned IP). The correct IP was `27.44.141.81` via 8.8.8.8 and 119.29.29.29.

Verification:
```
dig @8.8.8.8 direct.miyaip.online  → 27.44.141.81
dig @119.29.29.29 direct.miyaip.online → 27.44.141.81
host direct.miyaip.online → 1.1.1.1  (poisoned)
```

### Fix: Use Real IP
Replaced `"direct.miyaip.online"` with `"27.44.141.81"` in `binConfigs/config.json`.

### Finding: Missing geoip.dat / geosite.dat

xray crashed on restart with:
```
infra/conf: failed to load geosite: GOOGLE > open geosite.dat: no such file or directory
```

The geo files existed at `.../bin/` but not at `.../bin/xray/` where the xray binary lived.

### Fix: Symlink Geo Files
```bash
ln -sf ~/Library/Application\ Support/v2rayN/bin/geosite.dat \
      ~/Library/Application\ Support/v2rayN/bin/xray/geosite.dat
ln -sf ~/Library/Application\ Support/v2rayN/bin/geoip.dat \
      ~/Library/Application\ Support/v2rayN/bin/xray/geoip.dat
```

### Final: Start Core Manually
Since v2rayN didn't auto-restart the core after killing it:

```bash
"/Users/shabi/Library/Application Support/v2rayN/bin/xray/xray" run \
  -c "/Users/shabi/Library/Application Support/v2rayN/binConfigs/config.json" &
```

### Final: Set System Proxy
```bash
networksetup -setsocksfirewallproxy Wi-Fi 127.0.0.1 10808
networksetup -setsocksfirewallproxystate Wi-Fi on
```

## Final Verification
```
Google:  200 (3.16s)
YouTube: 200 (3.70s)
GitHub:  200 (3.91s)
Twitter: 200 (3.24s)
Baidu:   200 (0.72s, direct)
```

## Key Takeaways

1. **Running process ≠ working proxy.** Check TUN interface, proxy ports, and actual connectivity.
2. **TUN mode on macOS is fragile.** Switch to system proxy mode if privilege escalation fails silently.
3. **DNS poisoning is common in China.** Always verify DNS resolution via multiple resolvers when the proxy connects but foreign sites fail.
4. **geoip.dat/geosite.dat must be in xray's own directory.** v2rayN stores them one level up; symlink them.
5. **Config persistence:** v2rayN overwrites `binConfigs/config.json` when it restarts the core. To make fixes permanent, modify `guiNConfig.json` instead.
