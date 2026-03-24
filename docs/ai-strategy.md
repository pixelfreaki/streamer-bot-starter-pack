# AI Strategy

This project uses a **multi-layer AI architecture** designed for reliability, performance, and clear separation of responsibilities.

## Overview

There are three distinct layers:

| Layer | Purpose | Technology |
|------|--------|-----------|
| 🧠 AI_Licia | Persona-driven interactions | Python + AI |
| ⚙️ OpenAI | Utility AI (translation, rewriting, etc.) | OpenAI API |
| 🧱 Local | Deterministic fallback | C# / config |

---
## 🔗 AI_Licia Integration

AI_Licia is a separate project responsible for persona-driven interactions.

Repository:
https://github.com/pixelfreaki/streamerbot-ai-licia

This starter pack integrates with AI_Licia as an optional component.

### Responsibilities

- AI_Licia → persona, tone, character-driven responses
- Starter Pack → command system, orchestration, fallback logic

### Important

- AI_Licia is NOT required for the starter pack to function
- Commands must always have a local fallback
- Integration should follow the rules defined in this document
---
## Core Principle

> Every command must work **without AI**.

AI enhances responses — it should never be required for core functionality.

---

## 🧠 AI_Licia (Persona Layer)

AI_Licia is responsible for **character-driven interactions**.

Use AI_Licia when:
- The response must follow a persona
- Tone and personality matter
- The interaction is immersive or roleplay-driven

### Examples

- `!oracle`
- `!judge`
- `!omen`
- `!tarot`
- `!curse`
- `!hex`

### Rules

- Always preserve persona identity
- Never return generic chatbot responses
- Responses must feel authored by a character
- Personality is more important than precision

---

## ⚙️ OpenAI (Utility Layer)

OpenAI is used for **non-persona utility tasks**.

Use OpenAI when:
- You need translation
- You need paraphrasing or rewriting
- You want to enhance a base response
- The command is not tied to a persona

### Examples

- Translating dynamic text
- Rewriting bot responses
- Enhancing `!8ball` responses
- Formatting user-generated input

### Rules

- Do NOT apply persona tone
- Keep responses neutral unless specified
- Use OpenAI as an enhancement, not a dependency

---

## 🧱 Local Layer (Fallback)

The local layer guarantees reliability.

Use local logic when:
- The command must always work
- The response is deterministic
- Low latency is important

### Examples

- `!flipcoin`
- Base `!8ball` responses
- Static command messages
- Predefined text responses

---

## 🔁 Fallback Strategy

All commands using OpenAI must implement fallback behavior.

### Standard Flow

1. Generate a local/base response
2. Attempt OpenAI enhancement
3. If OpenAI fails → return local response

### Example (`!8ball`)

```csharp
string baseAnswer = GetRandomEightBallResponse();

try
{
    string enhanced = CallOpenAI(baseAnswer);
    return enhanced;
}
catch
{
    return baseAnswer;
}