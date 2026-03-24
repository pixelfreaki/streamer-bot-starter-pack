# Streamer.bot Starter Pack

A C#-first command pack for [Streamer.bot](https://streamer.bot). Commands are config-driven, fully localized (English / Brazilian Portuguese), and optionally enhanced by OpenAI or AI_Licia.

---

## Commands

### Standard commands

| Command | Description | AI? |
|---|---|---|
| `!8ball` | Magic 8-ball answer | Optional (OpenAI enhanced) |
| `!joke` | Random joke, supports a topic (`!joke cats`) | Optional (OpenAI generated) |
| `!flipcoin` | Flip a coin — guess HEAD or TAIL | No |
| `!fortune` | Random fortune message | No |
| `!lurk` | Lurk message | No |
| `!translate` | Translates a message | Optional (OpenAI) |
| `!russianroulette` | 1-in-6 chance of dying | No |
| `!sacrifice` | Sacrifice a user | No |
| `!clip` | Create a Twitch clip | No |
| `!shoutout` | Shout out another streamer | No |
| `!settitle` | Set stream title (mod only) | No |
| `!setgame` | Set stream category (mod only) | No |
| `!accountage` | How old is a user's account | No |
| `!followage` | How long a user has been following | No |
| `!uptime` | Stream uptime | No |
| `!time` | Current time for the streamer | No |
| `!scene` | Switch OBS scene (mod only) | No |
| `!pc` | Streamer's PC specs | No |
| `!gear` | Streamer's gear | No |
| `!peripherals` | Streamer's peripherals | No |
| `!commands` | List all available commands | No |

### AI_Licia persona commands

These commands are backed by [AI_Licia](https://www.getailicia.com). AI_Licia sends her response directly to chat — the bot just triggers her. Every command has a local fallback for when AI_Licia is offline.

| Command | Description |
|---|---|
| `!oracle` | The Oracle answers your question |
| `!horoscope` | Dark horoscope reading |
| `!curse` | Cast a curse |
| `!omen` | Reveal an omen |
| `!tarot` | Tarot card reading |
| `!judge` | Judge another viewer |
| `!hex` | One viewer hexes another |

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

AI_Licia commands show `[AI_Licia triggered — response will appear in chat]` in the runner since the response goes directly to Twitch chat.

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

Repeat for each command. You can import all of them or only the ones you need.

---

## OpenAI setup (optional)

OpenAI enhances `!8ball`, `!joke`, and `!translate`. Every command works without it — AI is never required.

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

The exported actions read the key from a Streamer.bot persisted global variable.

1. Open **Streamer.bot**
2. Go to **Settings → Variables**
3. Click **Add** (persisted global variable)
4. Set:
   - **Name:** `openai_api_key`
   - **Value:** your OpenAI API key (`sk-...`)
5. Click **Save**

Once set, `!8ball` and `!joke` will use OpenAI automatically. If the variable is missing or the API call fails, both commands fall back to their local response pool.

---

## AI_Licia setup (optional)

AI_Licia powers the persona commands (`!oracle`, `!horoscope`, `!curse`, `!omen`, `!tarot`, `!judge`, `!hex`). She sends her response directly to Twitch chat — the bot just triggers her.

### Step 1 — Add the global variable in Streamer.bot

1. Open **Streamer.bot**
2. Go to **Settings → Variables**
3. Click **Add** (persisted global variable)
4. Set:
   - **Name:** `ai_licia_key`
   - **Value:** your AI_Licia API key
5. Click **Save**

The exported actions read `ai_licia_key` at runtime. The channel name is read automatically from Streamer.bot's built-in `broadcastUserName` argument — no additional variable needed.

### Step 2 — Set your API key (local runner only)

For local testing with the runner, add to `appsettings.Development.json`:

```json
{
  "AiLicia": {
    "ApiKey": "your-ailicia-key",
    "ChannelName": "your_twitch_channel"
  }
}
```

When `AiLicia.ApiKey` and `AiLicia.ChannelName` are set, the runner triggers AI_Licia on persona commands. When not set, commands fall back to their local response pool.

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
