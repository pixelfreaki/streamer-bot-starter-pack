# Streamer.bot Sub-Action Type Reference

Discovered by decoding `.import.txt` exports (SBAE + gzip format).
Use this as a lookup when building new actions in `generate_import.py`.

---

## How Exports Work

| Field | Value |
|---|---|
| Format | `base64(SBAE_magic_4_bytes + gzip(json))` |
| Decode | `json.loads(gzip.decompress(base64.b64decode(raw)[4:]))` |
| C# code | Stored in `byteCode` field (base64-encoded UTF-8), **not** `code` or `c` |

---

## Sub-Action Types

### Structure / Flow

| Type | Name | Key Fields | Notes |
|---|---|---|---|
| `1009` | Label | `value` (display text), `color` | Visual separator in the UI |
| `127` | Platform Switch | `input` (`%commandSource%`), `autoType: false` | Routes by platform |
| `99903` | Switch Case | `values` (e.g. `["twitch"]`), `caseSensitive`, `subActions` | Child of type 127 |
| `99904` | Switch Default | `subActions` (usually empty) | Catch-all case of type 127 |
| `120` | If Condition | `input`, `operation` (0=equals), `value`, `autoType`, `subActions` | Contains 99901/99902 branches |
| `99901` | If — True Branch | `random`, `subActions` | Child of type 120 |
| `99902` | If — False Branch | `random`, `subActions` | Child of type 120 |

### Chat Messages

| Type | Platform | Key Fields | Notes |
|---|---|---|---|
| `23` | Twitch | `text`, `color` (see below), `useBot`, `fallback` | Primary Twitch send |
| `35001` | Kick | `text`, `useBot`, `fallback` | |
| `4001` | YouTube | `text`, `useBot`, `fallback`, `broadcast: 0` | |

#### Type 23 — `color` values (Twitch Announcement)

| Value | Appearance |
|---|---|
| `0` | Regular chat (no announcement) |
| `1` | Blue announcement |
| `2` | Green announcement |
| `3` | Orange announcement |
| `4` | **Purple announcement** ← used throughout this project |
| `5` | Primary (broadcaster's accent colour) |

> Set `color: 4` on any type-23 sub-action to send as a purple Twitch Announcement.
> No C# needed — this is fully native.

### Inline C#

| Type | Name | Key Fields | Notes |
|---|---|---|---|
| `99999` | Execute Code (Inline C#) | `byteCode` (base64 UTF-8), `references` (dll paths), `saveResultToVariable`, `saveToVariable`, `precompile`, `delayStart` | `saveResultToVariable: true` + `saveToVariable: "varName"` stores the `bool` return as `"True"`/`"False"` in `%varName%` |

**Typical references:**
```json
[
  "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
  "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
  "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.Core.dll"
]
```

| DLL | Required when |
|---|---|
| `mscorlib.dll` | Always |
| `System.dll` | `System.Net.WebClient`, `HttpRequestHeader` |
| `System.Core.dll` | `HashSet<T>`, `LINQ` (`Where`, `Take`, `Select`) |

### HTTP / URL

| Type | Name | Key Fields | Notes |
|---|---|---|---|
| `1007` | Fetch URL | `url` (supports `%arg%` substitution), `variableName`, `headers: {}`, `parseAsJson`, `autoType` | Response stored in `%variableName%` |

### Twitch-Specific

| Type | Name | Key Fields | Notes |
|---|---|---|---|
| `50` | Get User Info by Login | — | Populates `%targetCreatedAt%`, `%targetFollowCount%`, etc. |
| `51` | Get Follow Age | — | Populates `%followAgeLong%`, `%broadcastUserName%` |
| `123` | Create Clip | — | |
| `15001` | Timeout User | — | |
| `20` | Wait / Delay | `waitTime` (ms) | |

### Kick-Specific

| Type | Name | Key Fields |
|---|---|---|
| `35001` | Send Chat Message | `text`, `useBot`, `fallback` |
| `35031` | Get Category | `source`, `categoryName`, `categoryId` |

### YouTube-Specific

| Type | Name | Key Fields |
|---|---|---|
| `4001` | Send Chat Message | `text`, `useBot`, `fallback`, `broadcast` |

### Triggers

| Type | Name | Key Fields | Notes |
|---|---|---|---|
| `401` | Command Trigger | `commandId` — links an action to a `!command` | Paired with a `commands[]` entry in the export |
| `701` | Timer Trigger | `timerId` — links an action to a named timer | Paired with a `timers[]` entry in the export |

#### Type 701 — Timer Trigger

The timer object lives in `data.timers[]` and is referenced by `timerId` in the trigger:

```json
{
  "timers": [{
    "id": "0d681571-951e-4c5b-aa80-6c11160df843",
    "name": "Twitch Chat Message Cooldown",
    "enabled": false,
    "repeat": true,
    "interval": 30,
    "randomInterval": false,
    "upperInterval": 0,
    "lines": 0,
    "counter": 0
  }]
}
```

```json
{
  "triggers": [{
    "timerId": "0d681571-951e-4c5b-aa80-6c11160df843",
    "id": "fc878ca9-27c7-4de9-9efa-6dc3dc12713e",
    "type": 701,
    "enabled": true,
    "exclusions": []
  }]
}
```

> `enabled: false` on the timer itself is intentional for per-user cooldown use — Streamer.bot uses it as a cooldown gate, not a repeating scheduler.
> Use stable UUIDs in `config/commands.json` for both `timer_id` and `trigger_id` to prevent duplicates on re-import.

---

## Patterns Used in This Project

### Standard text command (all platforms)
```
Label (1009)
Platform Switch (127)
  case twitch (99903)  → type 23, color=4  (purple announcement)
  case kick   (99903)  → type 35001
  case youtube(99903)  → type 4001
  default     (99904)
```

### C# compute → announce (e.g. !joke, !8ball)
```
Label (1009)
Inline C# (99999)      → sets %jokeResult% via CPH.SetArgument, returns true
Platform Switch (127)
  case twitch → type 23, color=4, text="@%user% %jokeResult%"
  case kick   → type 35001
  case youtube→ type 4001
```

### Resolve user → Fetch URL → announce (e.g. !accountage)
```
Label (1009)
Platform Switch (127)
  case twitch (99903)
    Inline C# (99999, saveToVariable="userFound")
      → sets %inputUser%, %inputUserName%, returns true/false
    If %userFound% == True (120)
      Then (99901)
        Fetch URL (1007, variableName="accountAge")
          url: https://decapi.me/twitch/accountage/%inputUserName%?precision=4
        type 23, color=4, text="/me @%inputUser% nasceu há %accountAge%"
  case kick   → type 35001 (not available)
  case youtube→ type 4001  (not available)
```

### Resolve user → platform sub-action → C# format → announce (e.g. !followage)
```
Label (1009)
Platform Switch (127)
  case twitch (99903)
    Inline C# (99999) → sets %inputUser%, %inputUserName%
    Get Follow Age (51) → sets %followAgeLong%
    Inline C# (99999) → formats message, calls CPH.TwitchAnnounce or sets arg
    type 23, color=4
```

### Timer-triggered event action (e.g. chatactivitypoints)
```
Label (1009)
Inline C# (99999)    → reads %user%, %message%, %emoteCount%; awards SE points via WebClient PUT
```
Trigger: type 701, `timerId` → timer with `interval: 30`, `enabled: false` (acts as per-user cooldown gate).
No command trigger — fires on Twitch Chat Message event.

---

## CPH Methods (Inline C# API)

| Method | Purpose |
|---|---|
| `CPH.TryGetArg(key, out string val)` | Read a Streamer.bot argument |
| `CPH.SetArgument(key, value)` | Set an argument for downstream sub-actions |
| `CPH.SendMessage(text, bot=true)` | Send to current platform chat |
| `CPH.TwitchAnnounce(text, bot, color)` | Send Twitch announcement (`color`: `"purple"`, `"blue"`, `"green"`, `"orange"`, `"primary"`) |
| `CPH.TwitchGetUserInfoByLogin(login)` | Returns `TwitchUserInfo` or `null` |
| `CPH.GetGlobalVar<T>(key, persisted)` | Read a global variable |
| `CPH.LogInfo(text)` | Log at INFO level to the Streamer.bot log |

> Prefer native sub-actions (type 23 color=4) over `CPH.TwitchAnnounce` in C# when the message
> is a simple template with `%arg%` substitutions — it's cleaner and visible in the UI.
