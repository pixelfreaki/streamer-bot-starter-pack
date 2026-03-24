#!/usr/bin/env python3
"""
Generates a Streamer.bot import file for all commands.

Reads:  appsettings.json          (locale)
        locales/{locale}.json     (responses)

Writes: generated/streamerbot/8ball.import.txt  (paste into Streamer.bot Import dialog)

Usage:
    python tools/generate_import.py
"""

import base64
import gzip
import json
import os
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SBAE_HEADER = b"SBAE"
EXPORTED_FROM = "1.0.4"
MINIMUM_VERSION = "1.0.0-alpha.1"
EXPORT_VERSION = 23

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
- playful "wise but chaotic" energy
- you sometimes tease the user, but in a friendly way
- you feel like a character, not an assistant

Style rules:
- answers must be short (1-2 sentences max)
- always sound creative and unexpected
- avoid generic 8-ball phrases like "Yes" or "No"
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
                    CPH.SetArgument("randomResponse", enhanced);
                    return true;
                }}
            }}
            catch {{ }}
        }}

        CPH.SetArgument("randomResponse", baseResponse);
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


def load_config():
    queues = load_json(os.path.join(ROOT, "config", "queues.json"))
    commands = load_json(os.path.join(ROOT, "config", "commands.json"))
    return queues, commands


def encode_export(export_dict):
    json_bytes = json.dumps(export_dict, ensure_ascii=False).encode("utf-8")
    compressed = gzip.compress(json_bytes)
    return base64.b64encode(SBAE_HEADER + compressed).decode("utf-8")


def make_csharp_subaction(code, parent_id=None, index=0):
    byte_code = base64.b64encode(code.encode("utf-8")).decode("utf-8")
    return {
        "name": "",
        "description": "",
        "references": [
            "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll"
        ],
        "byteCode": byte_code,
        "precompile": False,
        "delayStart": False,
        "saveResultToVariable": False,
        "saveToVariable": "",
        "id": str(uuid.uuid4()),
        "weight": 0.0,
        "type": 99999,
        "parentId": parent_id,
        "enabled": True,
        "index": index,
    }


def make_send_switch(text, parent_id=None, index=0):
    """Platform switch that sends %randomResponse% to Twitch, Kick, and YouTube."""
    switch_id = str(uuid.uuid4())
    twitch_id = str(uuid.uuid4())
    kick_id = str(uuid.uuid4())
    youtube_id = str(uuid.uuid4())
    default_id = str(uuid.uuid4())

    return {
        "input": "%commandSource%",
        "autoType": False,
        "subActions": [
            {
                "caseSensitive": True,
                "values": ["twitch"],
                "random": False,
                "subActions": [{"text": text, "color": 4, "useBot": True, "fallback": True,
                                "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
                                "parentId": twitch_id, "enabled": True, "index": 0}],
                "id": twitch_id, "weight": 0.0, "type": 99903,
                "parentId": switch_id, "enabled": True, "index": 0,
            },
            {
                "caseSensitive": True,
                "values": ["kick"],
                "random": False,
                "subActions": [{"text": text, "useBot": True, "fallback": True,
                                "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
                                "parentId": kick_id, "enabled": True, "index": 0}],
                "id": kick_id, "weight": 0.0, "type": 99903,
                "parentId": switch_id, "enabled": True, "index": 1,
            },
            {
                "caseSensitive": True,
                "values": ["youtube"],
                "random": False,
                "subActions": [{"text": text, "useBot": True, "fallback": True, "broadcast": 0,
                                "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
                                "parentId": youtube_id, "enabled": True, "index": 0}],
                "id": youtube_id, "weight": 0.0, "type": 99903,
                "parentId": switch_id, "enabled": True, "index": 2,
            },
            {
                "random": False, "subActions": [],
                "id": default_id, "weight": 0.0, "type": 99904,
                "parentId": switch_id, "enabled": True, "index": 3,
            },
        ],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": parent_id, "enabled": True, "index": index,
    }


def make_action(name, group, code, queue_id):
    action_id = str(uuid.uuid4())
    command_id = str(uuid.uuid4())

    return action_id, command_id, {
        "id": action_id,
        "queue": queue_id,
        "enabled": True,
        "excludeFromHistory": False,
        "excludeFromPending": False,
        "name": name,
        "group": group,
        "alwaysRun": False,
        "randomAction": False,
        "concurrent": False,
        "triggers": [
            {
                "commandId": command_id,
                "id": str(uuid.uuid4()),
                "type": 401,
                "enabled": True,
                "exclusions": [],
            }
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()), "weight": 0.0,
             "type": 1009, "parentId": None, "enabled": True, "index": 0},
            make_csharp_subaction(code, parent_id=None, index=1),
            make_send_switch("@%user% %randomResponse%", parent_id=None, index=2),
        ],
        "collapsedGroups": [],
    }


def make_command(name, trigger, group, command_id, action_id):
    return {
        "permittedUsers": [],
        "permittedGroups": [],
        "id": command_id,
        "name": name,
        "enabled": True,
        "include": False,
        "mode": 0,
        "command": trigger,
        "regexExplicitCapture": False,
        "location": 0,
        "ignoreBotAccount": True,
        "ignoreInternal": True,
        "sources": 2098177,
        "persistCounter": False,
        "persistUserCounter": False,
        "caseSensitive": False,
        "globalCooldown": 0,
        "userCooldown": 0,
        "group": group,
        "grantType": 0,
    }


def build_eightball_code(responses, locale):
    language = LANGUAGE_NAMES.get(locale, locale)
    system_prompt = PIXELFREAKI_SYSTEM_PROMPT.format(language=language)
    system_prompt_escaped = system_prompt.replace('"', '""')
    responses_str = "\n".join(f'        "{r}",' for r in responses)
    return EIGHTBALL_CSHARP.format(
        responses=responses_str,
        system_prompt=system_prompt_escaped,
    )


def main():
    settings = load_json(os.path.join(ROOT, "appsettings.json"))
    locale = settings.get("App", {}).get("DefaultLocale", "en")
    print(f"[info] locale: {locale}")

    locale_path = os.path.join(ROOT, "locales", f"{locale}.json")
    if not os.path.exists(locale_path):
        print(f"[warn] locale '{locale}' not found, falling back to en")
        locale_path = os.path.join(ROOT, "locales", "en.json")

    locale_data = load_json(locale_path)
    responses = locale_data["commands"]["8ball"]["responses"]
    print(f"[info] loaded {len(responses)} 8ball responses")

    queues_config, commands_config = load_config()

    # Build 8ball
    cmd_meta = commands_config["8ball"]
    queue_key = cmd_meta["queue"]
    group = cmd_meta["group"]
    trigger = cmd_meta["trigger"]

    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")

    queue_def = queues_config[queue_key]
    queue_id = str(uuid.uuid4())

    code = build_eightball_code(responses, locale)
    action_id, command_id, action = make_action(trigger, group, code, queue_id)
    command = make_command(trigger, trigger, group, command_id, action_id)

    print(f"[info] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {group}")

    export = {
        "meta": {
            "name": "Streamer.bot Starter Pack",
            "author": "",
            "version": "1.0.0",
            "description": "Generated by tools/generate_import.py",
            "autoRunAction": None,
            "minimumVersion": None,
        },
        "data": {
            "actions": [action],
            "queues": [
                {
                    "id": queue_id,
                    "blocking": queue_def["blocking"],
                    "name": queue_def["name"],
                }
            ],
            "commands": [command],
            "websocketServers": [],
            "websocketClients": [],
            "timers": [],
        },
        "version": EXPORT_VERSION,
        "exportedFrom": EXPORTED_FROM,
        "minimumVersion": MINIMUM_VERSION,
    }

    out_dir = os.path.join(ROOT, "generated", "streamerbot")
    os.makedirs(out_dir, exist_ok=True)

    encoded = encode_export(export)
    txt_path = os.path.join(out_dir, "8ball.import.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(encoded)
    print(f"[done] written to generated/streamerbot/8ball.import.txt")

    print()
    print("To import:")
    print("  1. Open Streamer.bot")
    print("  2. Actions tab -> Import button (top right)")
    print("  3. Paste the contents of generated/streamerbot/8ball.import.txt")
    print("  4. Click Import")
    print()
    print("Optional - to enable OpenAI enhancement:")
    print('  Settings -> Variables -> add "openai_api_key" (persisted)')


if __name__ == "__main__":
    main()
