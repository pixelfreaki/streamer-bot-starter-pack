# AI Strategy

This project uses a layered AI architecture designed for reliability and clear separation of concerns. Every command must work without AI — AI enhances responses, never replaces the fallback.

---

## Layers

| Layer | Technology | Purpose |
|---|---|---|
| Local | C# / config | Deterministic fallback — always runs |
| OpenAI | OpenAI API | Utility AI (translation, rewrite, enhance) |
| AI_Licia | AI_Licia API | Persona-driven responses (character tone) |

---

## Local Layer

The baseline. Every command implements this.

- Responses are deterministic and fast
- Loaded from `locales/{locale}.json` at startup
- No external calls, no latency

**Examples:** `!flipcoin`, `!fortune`, `!russianroulette`, base `!8ball` / `!joke` pool

---

## OpenAI Layer

Used for utility tasks where tone and persona are not important.

- Enhances a base local response
- Always wrapped in try/catch — failure falls back to local
- Must not apply persona tone

**Used by:** `!8ball` (enhance answer), `!joke` (generate topic joke), `!translate`

**Setup:** add `openai_api_key` as a persisted global variable in Streamer.bot (see README).

### Flow

```
1. Pick local base response
2. Call OpenAI to enhance it
3. If OpenAI fails → return local response unchanged
```

---

## AI_Licia Layer

Used for persona-driven interactions where character identity matters more than precision.

- AI_Licia sends her response directly to Twitch chat — the bot just triggers her
- Local fallback is shown in the runner; in Streamer.bot, AI_Licia handles the reply
- Do not mix AI_Licia logic into utility commands

**Used by:** `!oracle`, `!horoscope`, `!curse`, `!omen`, `!tarot`, `!judge`, `!hex`

**Setup:** add `ai_licia_key` as a persisted global variable in Streamer.bot (see README).

---

## Rules

- `Core` must not depend on OpenAI or AI_Licia
- `Commands` depend only on `IAiProvider` — never on concrete implementations
- AI implementations live in `StarterPack.AI.OpenAI` and `StarterPack.AI.AiLicia`
- Do not mix persona tone into utility commands
- Do not mix utility logic into persona commands
