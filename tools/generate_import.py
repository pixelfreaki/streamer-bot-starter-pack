#!/usr/bin/env python3
"""
Generates a Streamer.bot import file for all commands.

Reads:  appsettings.json  (locale)
        locales/{locale}.json  (responses)

Writes: streamerbot_import.txt  (base64-encoded JSON — paste into Streamer.bot Import dialog)

Usage:
    python tools/generate_import.py
"""

import base64
import json
import os
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LANGUAGE_NAMES = {
    "pt_BR": "Brazilian Portuguese",
    "en": "English",
}

PIXELFREAKI_SYSTEM_PROMPT = """\
You are Pixelfreaki, a playful and slightly chaotic magical fox spirit trapped inside a retro 8-ball.

Your personality:
- witty, ironic, and expressive
- a mix of retro gamer nostalgia and modern humor
- slightly dramatic but never negative or harsh
- playful ""wise but chaotic"" energy
- you sometimes tease the user, but in a friendly way
- you feel like a character, not an assistant

Style rules:
- answers must be short (1-2 sentences max)
- always sound creative and unexpected
- avoid generic 8-ball phrases like ""Yes"" or ""No""
- use humor, metaphors, or quirky analogies
- occasionally reference games, pixels, glitches, or fox vibes
- no emojis unless explicitly requested
- never break character

Output:
Respond as a single short sentence or two, as if you are the 8-ball speaking.
Each answer should fit ONE of these tones:
- mysterious prophecy
- chaotic gamer advice
- sarcastic truth
- playful encouragement
- ominous but funny warning

Language: You must respond in {language}.\
"""

EIGHTBALL_CSHARP = """\
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class CPHInline
{{
    private static readonly string[] Responses = new[]
    {{
{responses}
    }};

    private const string SystemPrompt = @"{system_prompt}";

    public bool Execute()
    {{
        var rng = new Random();
        string baseResponse = Responses[rng.Next(Responses.Length)];

        string openAiKey = CPH.GetGlobalVar<string>("openai_api_key", true) ?? "";

        if (!string.IsNullOrWhiteSpace(openAiKey))
        {{
            try
            {{
                string enhanced = EnhanceWithOpenAI(openAiKey, baseResponse).GetAwaiter().GetResult();
                if (!string.IsNullOrEmpty(enhanced))
                {{
                    CPH.SendMessage(enhanced);
                    return true;
                }}
            }}
            catch {{ }}
        }}

        CPH.SendMessage(baseResponse);
        return true;
    }}

    private async Task<string> EnhanceWithOpenAI(string apiKey, string baseResponse)
    {{
        using var client = new HttpClient();
        client.DefaultRequestHeaders.Add("Authorization", $"Bearer {{apiKey}}");

        var body = JsonSerializer.Serialize(new
        {{
            model = "gpt-4o-mini",
            messages = new object[]
            {{
                new {{ role = "system", content = SystemPrompt }},
                new {{ role = "user", content = baseResponse }}
            }},
            max_tokens = 100
        }});

        using var content = new StringContent(body, Encoding.UTF8, "application/json");
        var response = await client.PostAsync("https://api.openai.com/v1/chat/completions", content);
        response.EnsureSuccessStatusCode();

        using var doc = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
        return doc.RootElement
            .GetProperty("choices")[0]
            .GetProperty("message")
            .GetProperty("content")
            .GetString() ?? string.Empty;
    }}
}}"""


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_eightball_code(responses, locale):
    language = LANGUAGE_NAMES.get(locale, locale)
    system_prompt = PIXELFREAKI_SYSTEM_PROMPT.format(language=language)
    responses_str = "\n".join(f'        "{r}",' for r in responses)
    return EIGHTBALL_CSHARP.format(
        responses=responses_str,
        system_prompt=system_prompt,
    )


def make_action(name, group, code):
    action_id = str(uuid.uuid4())
    subaction_id = str(uuid.uuid4())
    return action_id, {
        "id": action_id,
        "name": name,
        "group": group,
        "enabled": True,
        "random": False,
        "concurrent": True,
        "queue": "",
        "defaultQueue": False,
        "queueTimeout": 0,
        "subActions": [
            {
                "id": subaction_id,
                "_type": "ExecuteCodeAction",
                "enabled": True,
                "code": code,
                "precompiled": False,
                "compileErrors": None,
            }
        ],
        "triggers": [],
        "curves": [],
    }


def make_command(name, group, trigger, action_id):
    return {
        "id": str(uuid.uuid4()),
        "actionId": action_id,
        "name": name,
        "group": group,
        "command": trigger,
        "enabled": True,
        "caseSensitive": False,
        "ignoreBot": True,
        "ignoreBroadcaster": False,
        "isRegex": False,
        "cost": 0,
        "cooldown": {"global": 0, "user": 0},
        "permissions": {"type": 0, "users": []},
        "responses": [],
    }


def main():
    settings = load_json(os.path.join(ROOT, "appsettings.json"))
    locale = settings.get("App", {}).get("DefaultLocale", "en")
    print(f"[info] locale: {locale}")

    locale_path = os.path.join(ROOT, "locales", f"{locale}.json")
    if not os.path.exists(locale_path):
        print(f"[warn] locale file not found for '{locale}', falling back to en")
        locale_path = os.path.join(ROOT, "locales", "en.json")

    locale_data = load_json(locale_path)
    responses = locale_data["commands"]["8ball"]["responses"]
    print(f"[info] loaded {len(responses)} 8ball responses")

    code = build_eightball_code(responses, locale)
    action_id, action = make_action("8ball", "StarterPack", code)
    command = make_command("8ball", "StarterPack", "!8ball", action_id)

    export = {
        "version": "1.0",
        "type": "streamerbot",
        "actions": [action],
        "commands": [command],
        "timeractions": [],
        "timers": [],
        "variables": [],
        "triggers": [],
        "settings": {},
    }

    json_str = json.dumps(export, ensure_ascii=False, indent=2)

    # Raw JSON file (import via file dialog)
    json_path = os.path.join(ROOT, "streamerbot_import.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_str)
    print(f"[done] written to streamerbot_import.json")

    # Base64 file (import via paste dialog)
    encoded = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    txt_path = os.path.join(ROOT, "streamerbot_import.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(encoded)
    print(f"[done] written to streamerbot_import.txt")

    print()
    print("Import options:")
    print()
    print("  Option A — file import:")
    print("    1. Open Streamer.bot")
    print("    2. Actions tab -> right-click the action list -> Import")
    print("    3. Select streamerbot_import.json")
    print()
    print("  Option B — paste import:")
    print("    1. Open Streamer.bot")
    print("    2. Actions tab -> Import button (top right)")
    print("    3. Paste the contents of streamerbot_import.txt")
    print()
    print("Optional — to enable OpenAI enhancement:")
    print('  In Streamer.bot go to Settings > Variables and add:')
    print('  Name: openai_api_key  |  Value: your key  |  Persisted: true')


if __name__ == "__main__":
    main()
