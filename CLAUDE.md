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

- `locales/` → source of truth for messages
- `generated/` → build output (not source of truth)

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