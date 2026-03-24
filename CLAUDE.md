# CLAUDE.md

## Project Architecture

This project is a C#-first Streamer.bot starter pack.

### Core Rules

- All bot commands must be implemented in C#
- Python is only used for build/generation tooling (not runtime commands)
- Do not introduce Python-based command execution
- Do not call external scripts from C# unless explicitly required

---

## Structure

- `StarterPack.Core` → interfaces, models, shared logic
- `StarterPack.Commands` → bot commands
- `StarterPack.AI.OpenAI` → utility AI (translation, rewrite, enhancement)
- `StarterPack.AI.AiLicia` → persona-based AI (character-driven responses)

- `config/` → source of truth for queues, groups, and command metadata
- `locales/` → source of truth for messages
- `generated/` → build output (not source of truth)

---

## Streamer.bot Queue & Group Architecture

Queues and groups are defined in `config/queues.json` and assigned per command in `config/commands.json`.

### Queues

| Key | Display Name | Blocking | Purpose |
|---|---|---|---|
| `ai` | AI Commands | No | Commands that call OpenAI or AI_Licia. Non-blocking — HTTP calls are async. |
| `moderation` | Moderation | Yes | Mod actions (ban, timeout, etc.). Must complete in order. |
| `info` | Info | No | Informational commands (!setup, !mic, !discord, etc.). |
| `fun` | Fun | No | Fun commands without AI (!flipcoin, !fortune, etc.). |
| `obs` | OBS | Yes | OBS scene/source control. Scene changes must be sequential. |
| `stream` | Stream | No | Stream management (clips, markers, etc.). |

### Groups

Groups are for visual organization in the Streamer.bot UI. A command's group does not have to match its queue.

| Group | Commands |
|---|---|
| Fun | !8ball, !flipcoin, !fortune, !rps, ... |
| Info | !setup, !mic, !discord, !social, ... |
| Moderation | !ban, !timeout, !clear, ... |
| OBS | !scene, !source, ... |
| Stream | !clip, !marker, ... |

### Rules

- Queue assignment is defined in `config/commands.json` — never hardcoded in the generator
- Any command using an AI provider must use the `ai` queue
- OBS and Moderation queues must be blocking
- Add new queues to `config/queues.json` before referencing them in commands

---

## AI Architecture

This project uses a layered AI approach:

- Local → deterministic fallback (required)
- OpenAI → utility AI (translation, rewrite, enhancement)
- AI_Licia → persona-driven AI

### Rules

- AI is optional, not required
- Every command must work without AI
- Always implement fallback behavior
- Do not mix persona tone into utility commands

### Integration

- All AI interactions must go through `IAiProvider`
- Do NOT call OpenAI or AI_Licia directly inside commands
- Commands must depend on abstractions, not implementations

---

## Localization

- Localization is resolved at build time
- Do NOT implement runtime language detection
- Commands should assume pre-localized input

---

## Command Guidelines

- Keep commands small and focused
- Avoid duplication
- Prefer reusable services over inline logic
- Do not hardcode messages (use config/locales instead)
- Do not read from generated files as source of truth

---

## What to Avoid

- No runtime locale switching
- No mixing Python logic into commands
- No direct OpenAI calls inside commands
- No mixing AI_Licia logic into core
- No reliance on Streamer.bot UI for logic

---

## Dependency Rules

- `Core` must not depend on OpenAI or AI_Licia
- `Commands` depend only on abstractions (`IAiProvider`)
- AI implementations live in separate modules

---

## Goal

This project is configuration-driven.

Commands should be generated, scalable, and maintainable — not manually maintained.