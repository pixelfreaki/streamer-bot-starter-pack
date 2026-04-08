# Streamer.bot Starter Pack

A C#-first command pack for [Streamer.bot](https://streamer.bot). Commands are config-driven, fully localized (English / Brazilian Portuguese), and optionally enhanced by OpenAI or AI_Licia.

---

## Commands

### Standard commands

| Command | Description | Access |
|---|---|---|
| `!8ball` | Magic 8-ball answer | Everyone |
| `!joke` | Random joke, supports a topic (`!joke cats`) | Everyone |
| `!flipcoin` | Flip a coin — guess HEAD or TAIL | Everyone |
| `!fortune` | Random fortune message | Everyone |
| `!lurk` | Lurk message | Everyone |
| `!translate` | Translate a message | Everyone |
| `!russianroulette` | 1-in-6 chance of dying | Everyone |
| `!sacrifice` | Sacrifice a user | Everyone |
| `!clip` | Save OBS replay buffer, or fall back to Twitch clip if replay is not running | Everyone |
| `!shoutout` | Shout out another streamer | Everyone |
| `!settitle` | Set stream title | Mod only |
| `!setgame` | Set stream category | Mod only |
| `!accountage` | How old is a user's Twitch account | Everyone |
| `!followage` | How long a user has been following | Everyone |
| `!uptime` | Stream uptime | Everyone |
| `!time` | Current time for the streamer | Everyone |
| `!scene` | Switch OBS scene | Mod only |
| `!pc` | Streamer's PC specs | Everyone |
| `!gear` | Streamer's gear | Everyone |
| `!peripherals` | Streamer's peripherals | Everyone |
| `!commands` | List all available commands | Everyone |

### AI_Licia persona commands

Backed by [AI_Licia](https://www.getailicia.com). AI_Licia sends her response directly to Twitch chat — the bot just triggers her. Every command has a local fallback.

| Command | Description |
|---|---|
| `!oracle` | The Oracle answers your question |
| `!horoscope` | Dark horoscope reading |
| `!curse` | Cast a curse on a viewer |
| `!omen` | Reveal an omen |
| `!tarot` | Tarot card reading |
| `!judge` | Judge another viewer |
| `!hex` | One viewer hexes another |

### StreamElements points commands

Require a StreamElements account. See [StreamElements setup](#streamelements-setup-optional) below.

| Command | Description | Access |
|---|---|---|
| `!points` | Show your current point balance | Everyone |
| `!top` | Show the top 5 on the leaderboard | Everyone |
| `!top10` | Show the full top 10 leaderboard | Everyone |

There is also a `chatactivitypoints` event action that awards points when a user sends a chat message. After importing, add its trigger manually: **Triggers → Add → Twitch → Chat → Message**. The 30-second per-user cooldown is enforced in the C# code — no extra settings needed on the trigger.

### Raffle bot

A full raffle system that integrates with the StreamElements leaderboard. StreamElements is optional — all three draws degrade gracefully when unavailable.

| Command | Description | Access |
|---|---|---|
| `!openRaffle <title>` | Open a new raffle | Mod only |
| `!join` | Join the current raffle | Everyone |
| `!closeRaffle` | Close entries (draw is not triggered yet) | Mod only |
| `!drawRaffle` | Close entries and draw all three winners | Mod only |
| `!showPreviousRaffle` | Show the result of the last raffle | Mod only |

#### How the draws work

`!drawRaffle` announces three winners in sequence (10-second delay before draws start):

| Draw | Pool | Requires `!join`? |
|---|---|---|
| **Top 5** | Random pick from StreamElements leaderboard positions 1–5 | No |
| **Top 10** | Walk the full leaderboard top-to-bottom; collect up to 10 users who joined; pick 1 at random | Yes |
| **Bonus** | Random pick from all users who joined | Yes |

**Top 10 example:** If the leaderboard has 19 users and only positions 16 and 17 joined, the Top 10 pool is `[position 16, position 17]` — higher-ranked users who didn't join are skipped. The winner is drawn from whoever showed up.

Each draw reports its outcome to chat even when no winner is available (e.g. "StreamElements not configured — draw skipped", "None of the participants appear on the leaderboard — draw skipped").

Raffle history is persisted to `%APPDATA%\Streamer.bot\raffle_history.json`.

### Event notifications

36 pre-built event notification actions, fully localized. Each fires on its platform event and sends an announcement to chat.

**Twitch**

| Action | Trigger event |
|---|---|
| Title Changed | Stream updated (title) |
| Game Changed | Stream updated (category) |
| Poll Start / Results | Poll created / completed |
| Prediction Start / Locked / Results | Prediction lifecycle |
| Ad Run / Upcoming Ads | Ad break start / upcoming |
| Hype Train Start / Level Up / End | Hype train lifecycle |
| Raid | Incoming raid |
| New Subscriber / Resubscriber | Subscription |
| Gifted Subscription / Gift Bomb | Gift sub events |

**YouTube**

| Action | Trigger event |
|---|---|
| Super Chat / Super Sticker | Super Chat / Sticker |
| New Member / New Gifted Membership | Membership events |

**Kick** (requires [Kick.bot](https://kick.bot))

| Action | Trigger event |
|---|---|
| New Follow / Subscriber / Resubscriber | Follow / sub events |
| Gifted Subscription / Mass Gifted | Gift sub events |
| Host | Incoming raid |
| Title Changed / Category Changed | Stream updated |
| Poll Start / Results | Poll lifecycle |
| Prediction Start / Locked / Results | Prediction lifecycle |

Import files are at `generated/streamerbot/notif_*.import.txt`. All messages are in `locales/{locale}.json` under the `notifications` key.

---

## Requirements

- [.NET 10 SDK](https://dotnet.microsoft.com/download)
- [Python 3.10+](https://www.python.org/downloads/) — only needed to regenerate exports
- [Streamer.bot 0.2+](https://streamer.bot)

---

## Install

```bash
git clone https://github.com/your-user/streamer-bot-starter-pack
cd streamer-bot-starter-pack
dotnet restore
```

### Configure locale

Edit `appsettings.json` and set your preferred locale:

```json
{
  "App": {
    "DefaultLocale": "pt_BR"
  }
}
```

Supported values: `en`, `pt_BR`.

---

## Run tests

```bash
dotnet test
```

---

## Run locally (optional)

The runner lets you test commands in a terminal before importing to Streamer.bot.

```bash
dotnet run --project StarterPack.Runner
```

Then type commands like `!8ball will it rain?`, `!flipcoin head`, or `!oracle will I survive?`.

Raffle commands work in the runner: `!openRaffle Test`, `!join`, `!drawRaffle`.

AI_Licia commands show `[AI_Licia triggered — response will appear in chat]` since responses go directly to Twitch.

---

## Export to Streamer.bot

### 1. Generate the import files

```bash
python tools/generate_import.py
```

This reads `appsettings.json` (for locale) and `locales/{locale}.json` (for messages), then writes one `.import.txt` file per command into `generated/streamerbot/`.

### 2. Import into Streamer.bot

For each command you want to add:

1. Open **Streamer.bot**
2. Go to the **Actions** tab
3. Click **Import** (top-right corner)
4. Open or paste the contents of `generated/streamerbot/<command>.import.txt`
5. Click **Import**

Repeat for each command. You can import all of them or only the ones you need. Re-importing an existing command is safe — each action has a stable UUID so duplicates are never created.

---

## OpenAI setup (optional)

OpenAI enhances `!8ball`, `!joke`, and `!translate`. Every command works without it.

### Step 1 — Set your API key (local runner)

Create `appsettings.Development.json` in the project root (gitignored):

```json
{
  "OpenAI": {
    "ApiKey": "sk-..."
  }
}
```

### Step 2 — Add the global variable in Streamer.bot

1. Open **Streamer.bot**
2. Go to **Settings → Variables**
3. Click **Add** (persisted global variable)
4. Set **Name:** `openai_api_key`, **Value:** your OpenAI API key
5. Click **Save**

When set, `!8ball` and `!joke` use OpenAI automatically. If the variable is missing or the call fails, both commands fall back to their local response pool.

---

## AI_Licia setup (optional)

AI_Licia powers the persona commands. She sends responses directly to Twitch chat — the bot just triggers her.

### Step 1 — Add the global variable in Streamer.bot

1. Open **Streamer.bot**
2. Go to **Settings → Variables**
3. Click **Add** (persisted global variable)
4. Set **Name:** `ai_licia_key`, **Value:** your AI_Licia API key
5. Click **Save**

The channel name is read automatically from Streamer.bot's `broadcastUserName` — no extra variable needed.

### Step 2 — Set your API key (local runner only)

Add to `appsettings.Development.json`:

```json
{
  "AiLicia": {
    "ApiKey": "your-ailicia-key",
    "ChannelName": "your_twitch_channel"
  }
}
```

---

## StreamElements setup (optional)

Required for `!points`, `!top`, `!top10`, `chatactivitypoints`, and the **Top 5** / **Top 10** raffle draws.

### Step 1 — Get your JWT token and channel ID

1. Log in to [StreamElements](https://streamelements.com)
2. Go to **Account → Show secrets** to find your JWT token
3. Your channel ID is in the URL of your StreamElements dashboard

### Step 2 — Add the global variables in Streamer.bot

1. Open **Streamer.bot**
2. Go to **Settings → Variables**
3. Add two persisted global variables:

| Name | Value |
|---|---|
| `se_jwt` | Your StreamElements JWT token |
| `se_channel` | Your StreamElements channel ID |

When both variables are set, all StreamElements commands and the raffle leaderboard draws activate automatically. When missing, those commands gracefully report that the service is unavailable.

---

## Customise messages

All messages live in `locales/en.json` and `locales/pt_BR.json`. Edit those files, then regenerate:

```bash
python tools/generate_import.py
```

Re-import any updated `.import.txt` files into Streamer.bot.

---

## Project structure

```
StarterPack.Commands/     — bot command implementations
StarterPack.Core/         — interfaces and models
StarterPack.AI.OpenAI/    — OpenAI provider
StarterPack.AI.AiLicia/   — AI_Licia persona provider
StarterPack.Runner/       — local CLI test runner
StarterPack.Tests/        — unit tests
config/                   — command metadata (queues, groups)
locales/                  — message strings (source of truth)
tools/                    — export generator
generated/                — build output (not checked in)
```

---

## AI architecture

See [docs/ai-strategy.md](docs/ai-strategy.md) for the full breakdown of the three-layer AI design (Local → OpenAI → AI_Licia).
