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

**Standard references (include all three in every action):**
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
| `System.Core.dll` | `HashSet<T>`, LINQ (`Where`, `Take`, `Select`) |

> Always include all three. Missing `System.Core.dll` causes a silent compile failure — Streamer.bot will accept the import but the action produces no output.

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

### OBS Studio

All OBS sub-actions require a `connectionId` (the UUID of your configured OBS WebSocket connection in Streamer.bot).

| Type | Name | Key Fields | Notes |
|---|---|---|---|
| `43` | Start Recording | `connectionId` | Starts OBS recording |
| `321` | Set Recording State | `connectionId`, `state` (2 = stop) | Controls recording state |
| `328` | Stop Recording | `connectionId` | Stops OBS recording |
| `329` | Add Chapter Marker | `connectionId`, `chapterName` | Adds a chapter marker; supports `%variable%` substitution |

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
| `401` | Command Trigger | `commandId` | Links action to a `!command`. Paired with `commands[]` entry. |
| `701` | Timer Trigger | `timerId` | Links action to a named timer. Paired with `timers[]` entry. |
| `133` | Twitch Chat Message | — | Fires on every chat message. Passes `user`, `message`, `emoteCount`. Add manually after import. |
| `101` | Twitch Follow | — | |
| `102` | Twitch Cheer | `min`, `max` (-1 = any) | |
| `103` | Twitch New Subscriber | `tiers` (16 = all tiers) | |
| `104` | Twitch Resubscriber | `tiers`, `min`, `max` | |
| `105` | Twitch Gifted Subscription | `tiers`, `min`, `max`, `subType`, `monthsGifted` | |
| `106` | Twitch Gift Bomb | `tiers`, `min`, `max`, `subType` | |
| `107` | Twitch Raid | `min`, `max` (-1 = any) | Passes `%user%`, `%viewers%` |
| `108` | Twitch Hype Train Start | — | |
| `110` | Twitch Hype Train Level Up | `min`, `max` | Passes `%level%` |
| `111` | Twitch Hype Train End | — | Passes `%level%`, `%percent%`, `%percentDecimal%` |
| `118` | Twitch Stream Update | `gameOnly`, `gameId`, `gameName` | Passes `%statusUpdate%`, `%gameUpdate%`, `%status%`, `%gameName%` |
| `125` | Twitch Poll Start | — | Passes `%poll.Title%` |
| `127` | Twitch Poll Results | — | Passes `%poll.winningChoice.title%`, `%poll.winningChoice.totalVotes%`, `%poll.votes%` |
| `128` | Twitch Prediction Start | — | Passes `%prediction.Title%` |
| `130` | Twitch Prediction Results | — | Passes `%prediction.winningOutcome.title%`, `%prediction.winningOutcome.users%` |
| `132` | Twitch Prediction Locked | — | |
| `139` | Twitch Ad Run | — | Passes `%adLength%` |
| `186` | Twitch Upcoming Ads | `minutes` (array, e.g. `[1]`) | Passes `%minutes%`, `%broadcastUser%` |
| `4006` | YouTube Super Chat | `min`, `max` | Passes `%user%`, `%amount%`, `%message%` |
| `4007` | YouTube Super Sticker | `min`, `max` | Passes `%user%`, `%amount%` |
| `4008` | YouTube New Member | — | Passes `%user%`, `%levelName%` |
| `4015` | YouTube New Gifted Membership | — | Passes `%gifterUser%`, `%user%`, `%tier%` |
| `35011` | Kick New Follow | — | |
| `35014` | Kick New Subscriber | — | |
| `35015` | Kick New Resubscriber | — | Passes `%monthsSubscribed%` |
| `35016` | Kick New Gifted Subscription | — | Passes `%user%`, `%recipient.userName%` |
| `35017` | Kick Mass Gifted Subscriptions | — | Recipients in args as `recipient.{n}.userId` |
| `35020` | Kick Stream Update | `gameOnly`, `gameId`, `gameName` | Passes `%titleUpdate%`, `%gameUpdate%`, `%status%`, `%categoryName%` |
| `18002` | Kick Custom Event (Kick.bot) | `name`, `eventName` | Used for Kick polls/predictions/raid. See table below. |

#### Type 18002 — Kick.bot Event Names

| `eventName` | `name` | Event |
|---|---|---|
| `kickIncomingRaid` | `[Kick.bot] Raid` | Incoming raid. Passes `%user%`, `%viewers%` |
| `kickPollCreated` | `[Kick.bot] Poll Created` | Poll started |
| `kickPollCompleted` | `[Kick.bot] Poll Completed` | Poll ended |
| `kickPredictionCreated` | `[Kick.bot] Prediction Created` | Prediction started |
| `kickPredictionLocked` | `[Kick.bot] Prediction Locked` | Prediction locked |
| `kickPredictionResolved` | `[Kick.bot] Prediction Resolved` | Prediction resolved |

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

### Chat Message event action (e.g. chatactivitypoints)
```
Label (1009)
Inline C# (99999)    → reads %user%, %message%, %emoteCount%; awards SE points via WebClient PUT
```
Trigger: **none in the import** — add manually via Triggers → Twitch → Chat → Message after importing.
The 30-second per-user cooldown is enforced in C# using `CPH.GetGlobalVar<string>` / `CPH.SetGlobalVar`
with ISO-8601 timestamps keyed per user (`chatpoints_last_{user}`).

> **Do not use type 701 (Timer) for chat-message actions.** Timer triggers fire on a schedule and do
> not populate `user`, `message`, or `emoteCount` args. Those args only appear in Twitch Chat Message event triggers.

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
