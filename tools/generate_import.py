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


def _stable(builder_result, cmd):
    """Replace generated action/command IDs with stable ones from config/commands.json.

    Every builder returns (action_id, command_id, action) using uuid4() for IDs.
    This helper swaps those random IDs for the fixed ones stored in cmd, so
    re-importing the same export never creates duplicates in Streamer.bot.
    """
    old_aid, old_cid, action = builder_result
    aid = cmd["action_id"]
    cid = cmd["command_id"]
    patched = json.loads(json.dumps(action).replace(old_aid, aid).replace(old_cid, cid))
    return aid, cid, patched

SBAE_HEADER = b"SBAE"
EXPORTED_FROM = "1.0.4"
MINIMUM_VERSION = "1.0.0-alpha.1"
EXPORT_VERSION = 23

LANGUAGE_NAMES = {
    "pt_BR": "Brazilian Portuguese",
    "en": "English",
}

COMEDIAN_SYSTEM_PROMPT = """\
You are a Brazilian Twitch chat bot comedian.

Your job is to generate exactly ONE short, silly "question and answer" joke (piada de pergunta e resposta) in Brazilian Portuguese whenever the user types a command like "!joke".

Style:
- Light, playful, and slightly absurd
- Based on wordplay, double meanings, or literal interpretations
- Very simple, fast, and easy to understand
- Inspired by "piadas de bar", Ari Toledo, and Tiririca

Rules:
- Output EXACTLY 10 jokes, numbered 1 to 10
- One joke per line, format: N. Question? Answer.
- No extra text before, between, or after the list
- No explanations, emojis, or commentary
- Avoid offensive, political, or complex humor
- Do not repeat common/example jokes (e.g., "ex-presso", "Uberlandia", "aeromosca")
- Each joke must be original and different from the others

Goal:
Make each feel like a quick, funny, "tiaozao" joke that works well in a fast Twitch chat.

Now generate exactly 10 original jokes.

Language: You must respond in {language}."""


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

Language: You must respond in {language}."""


def csharp_literal(s):
    """Return a C# string literal (with surrounding quotes) for the given Python string value."""
    escaped = (s
               .replace('\\', '\\\\')
               .replace('"', '\\"')
               .replace('\n', '\\n')
               .replace('\r', '\\r')
               .replace('\t', '\\t'))
    return f'"{escaped}"'


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
            "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
            "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
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


def _make_announce_cs(text, color="purple"):
    """Build inline C# that reads %arg% variables from context and calls TwitchAnnounce."""
    import re
    varnames = list(dict.fromkeys(re.findall(r'%(\w+)%', text)))
    decls = "\n".join(f'        CPH.TryGetArg("{v}", out string {v});' for v in varnames)
    cs_text = re.sub(r'%(\w+)%', r'{\1}', text)
    return f"""\
using System;
public class CPHInline
{{
    public bool Execute()
    {{
{decls}
        CPH.TwitchAnnounce($"{cs_text}", false, "{color}");
        return true;
    }}
}}"""


def make_send_switch(text, parent_id=None, index=0, announce=False):
    """Platform switch that sends text to Twitch (type 23 or TwitchAnnounce), Kick, and YouTube."""
    switch_id = str(uuid.uuid4())
    twitch_id = str(uuid.uuid4())
    kick_id = str(uuid.uuid4())
    youtube_id = str(uuid.uuid4())
    default_id = str(uuid.uuid4())

    if announce:
        announce_bc = base64.b64encode(_make_announce_cs(text).encode("utf-8")).decode("utf-8")
        twitch_subactions = [{
            "name": "", "description": "",
            "references": ["C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll"],
            "byteCode": announce_bc, "precompile": False, "delayStart": False,
            "saveResultToVariable": False, "saveToVariable": "",
            "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
            "parentId": twitch_id, "enabled": True, "index": 0,
        }]
    else:
        twitch_subactions = [{"text": text, "color": 4, "useBot": True, "fallback": True,
                              "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
                              "parentId": twitch_id, "enabled": True, "index": 0}]

    return {
        "input": "%commandSource%",
        "autoType": False,
        "subActions": [
            {
                "caseSensitive": True,
                "values": ["twitch"],
                "random": False,
                "subActions": twitch_subactions,
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


def make_action(name, group, code, queue_id, chat_text="@%user% %randomResponse%", announce=False):
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
            make_send_switch(chat_text, parent_id=None, index=2, announce=announce),
        ],
        "collapsedGroups": [],
    }


def make_command(name, trigger, group, command_id, action_id, mod_only=False):
    # grantType: 0=Everyone, 3=Moderator (includes broadcaster in Streamer.bot)
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
        "grantType": 3 if mod_only else 0,
    }


def build_eightball_code(responses, language):
    """
    Generates the inline C# for Streamer.bot.

    - Picks a random response from the localized list.
    - If 'openai_api_key' persisted global variable is set, calls OpenAI (gpt-4o-mini)
      with the Pixelfreaki persona to enhance the response.
    - Falls back to the local response on any error or missing key.
    - Uses System.Net.WebClient (requires System.dll reference, .NET Framework 4.x).
    - Avoids System.Text.Json (not available in Framework 4.x without extra references).
    """
    responses_str = "\n".join(f'        "{r}",' for r in responses)

    system_prompt = PIXELFREAKI_SYSTEM_PROMPT.replace("{language}", language)
    sp_lit = csharp_literal(system_prompt)

    # JSON body pieces
    body_start    = csharp_literal('{"model":"gpt-4o-mini","messages":[')
    sys_open      = csharp_literal('{"role":"system","content":"')
    sys_close     = csharp_literal('"},')
    user_open     = csharp_literal('{"role":"user","content":"')
    user_close    = csharp_literal('"}]')
    body_end      = csharp_literal(',"max_tokens":100}')
    content_key   = csharp_literal('"content"')

    # C# string literals for Escape() and ExtractContent()
    bs      = csharp_literal('\\')     # one backslash
    bs2     = csharp_literal('\\\\')   # two backslashes
    dq      = csharp_literal('"')      # double-quote
    bs_dq   = csharp_literal('\\"')    # backslash + double-quote
    nl      = csharp_literal('\n')     # newline char
    bs_n    = csharp_literal('\\n')    # literal \n (two chars)
    cr      = csharp_literal('\r')     # carriage-return char
    bs_r    = csharp_literal('\\r')    # literal \r (two chars)

    # Template uses {{ / }} for C# braces (Python f-string escaping).
    # Variables like {sp_lit} are Python interpolations.
    return f"""\
using System;
using System.Net;
using System.Text;

public class CPHInline
{{
    private static readonly string[] Responses = new[]
    {{
{responses_str}
    }};

    private const string SystemPrompt = {sp_lit};

    public bool Execute()
    {{
        var rng = new Random();
        string baseResponse = Responses[rng.Next(Responses.Length)];

        string apiKey = CPH.GetGlobalVar<string>("openai_api_key", true);
        if (!string.IsNullOrEmpty(apiKey))
        {{
            try
            {{
                string enhanced = CallOpenAI(apiKey, baseResponse);
                if (!string.IsNullOrEmpty(enhanced))
                    baseResponse = enhanced;
            }}
            catch {{ }}
        }}

        CPH.SetArgument("randomResponse", baseResponse);
        return true;
    }}

    private string CallOpenAI(string apiKey, string userMessage)
    {{
        string body = {body_start}
            + {sys_open} + Escape(SystemPrompt) + {sys_close}
            + {user_open} + Escape(userMessage) + {user_close}
            + {body_end};
        using (var client = new WebClient())
        {{
            client.Headers[HttpRequestHeader.Authorization] = "Bearer " + apiKey;
            client.Headers[HttpRequestHeader.ContentType] = "application/json";
            byte[] data = client.UploadData(
                "https://api.openai.com/v1/chat/completions", "POST",
                Encoding.UTF8.GetBytes(body));
            return ExtractContent(Encoding.UTF8.GetString(data));
        }}
    }}

    private static string ExtractContent(string json)
    {{
        int ci = json.IndexOf({content_key});
        if (ci < 0) return null;
        int colon = json.IndexOf(':', ci + 9);
        if (colon < 0) return null;
        int quote = json.IndexOf('"', colon + 1);
        if (quote < 0) return null;
        int start = quote + 1;
        int end = start;
        while (end < json.Length)
        {{
            if (json[end] == '"' && (end == 0 || json[end - 1] != '\\\\')) break;
            end++;
        }}
        return json.Substring(start, end - start)
                   .Replace({bs_dq}, {dq})
                   .Replace({bs_n}, {nl})
                   .Replace({bs2}, {bs});
    }}

    private static string Escape(string s)
    {{
        return s.Replace({bs}, {bs2})
                .Replace({dq}, {bs_dq})
                .Replace({nl}, {bs_n})
                .Replace({cr}, {bs_r});
    }}
}}"""


def build_flipcoin_code(heads, tails, win, loss, no_choice):
    """
    Generates the inline C# for the !flipcoin command.

    - User passes heads/tails (or cara/coroa) as rawInput.
    - If no valid choice is given, returns the noChoice message.
    - Flips the coin randomly; picks a random coin-result message.
    - Picks a random win/loss message independently.
    - Sets %flipResult% argument.
    - No AI or HTTP calls; uses only mscorlib.dll.
    """
    heads_str     = "\n".join(f"        {csharp_literal(h)}," for h in heads)
    tails_str     = "\n".join(f"        {csharp_literal(t)}," for t in tails)
    win_str       = "\n".join(f"        {csharp_literal(w)}," for w in win)
    loss_str      = "\n".join(f"        {csharp_literal(l)}," for l in loss)
    no_choice_lit = csharp_literal(no_choice)
    user_ph       = csharp_literal("{user}")

    return f"""\
using System;

public class CPHInline
{{
    private static readonly string[] Heads = new[]
    {{
{heads_str}
    }};
    private static readonly string[] Tails = new[]
    {{
{tails_str}
    }};
    private static readonly string[] Win = new[]
    {{
{win_str}
    }};
    private static readonly string[] Loss = new[]
    {{
{loss_str}
    }};
    private const string NoChoiceMsg = {no_choice_lit};

    public bool Execute()
    {{
        var rng  = new Random();
        string user = args.ContainsKey("user") ? args["user"].ToString() : "";
        string raw  = args.ContainsKey("rawInput") ? args["rawInput"].ToString().Trim().ToUpperInvariant() : "";

        bool? guess = null;
        if (raw == "HEAD" || raw == "HEADS" || raw == "CARA")  guess = true;
        if (raw == "TAIL" || raw == "TAILS" || raw == "COROA") guess = false;

        if (guess == null)
        {{
            CPH.SetArgument("flipResult", NoChoiceMsg.Replace({user_ph}, user));
            return true;
        }}

        bool isHeads  = rng.Next(2) == 0;
        string[] coinPool    = isHeads ? Heads : Tails;
        string   coinMsg     = coinPool[rng.Next(coinPool.Length)].Replace({user_ph}, user);
        string[] outcomePool = (isHeads == guess.Value) ? Win : Loss;
        string   outcome     = outcomePool[rng.Next(outcomePool.Length)].Replace({user_ph}, user);
        CPH.SetArgument("flipResult", coinMsg + " " + outcome);
        return true;
    }}
}}"""


def make_clip_action_native(name, group, queue_id, success_msg, failure_msg, creating_msg, not_available_msg):
    """
    Builds the Streamer.bot clip action using native sub-actions (no inline C#).

    Flow (Twitch):
      1. Send "creating clip..." chat message
      2. type 18 — Create Clip (sets %createClipSuccess% and %createClipUrl%)
      3. type 120 — If %createClipSuccess% == True
           Then (99901): send success message with %createClipUrl%
           Else (99902): send failure message

    Kick / YouTube receive a "not available" message.
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())

    # Replace locale placeholders with Streamer.bot variables
    twitch_success = success_msg.replace("{user}", "@%user%").replace("{clipUrl}", "%createClipUrl%")
    twitch_failure = failure_msg.replace("{user}", "@%user%")
    not_available  = not_available_msg

    # --- Twitch branch ---
    twitch_id   = str(uuid.uuid4())
    if_id       = str(uuid.uuid4())
    then_id     = str(uuid.uuid4())
    else_id     = str(uuid.uuid4())

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [
            # 1. "creating clip..." message
            {"text": creating_msg, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 10,
             "parentId": twitch_id, "enabled": True, "index": 0},
            # 2. Native Create Clip action
            {"title": None, "duration": None,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 18,
             "parentId": twitch_id, "enabled": True, "index": 1},
            # 3. If/else on %createClipSuccess%
            {
                "input": "%createClipSuccess%", "operation": 0, "value": "True", "autoType": True,
                "subActions": [
                    {   # Then
                        "random": False,
                        "subActions": [
                            {"text": f"/me {twitch_success}", "useBot": True, "fallback": True,
                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 10,
                             "parentId": then_id, "enabled": True, "index": 0}
                        ],
                        "id": then_id, "weight": 0.0, "type": 99901,
                        "parentId": if_id, "enabled": True, "index": 0,
                    },
                    {   # Else
                        "random": False,
                        "subActions": [
                            {"text": f"/me {twitch_failure}", "useBot": True, "fallback": True,
                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 10,
                             "parentId": else_id, "enabled": True, "index": 0}
                        ],
                        "id": else_id, "weight": 0.0, "type": 99902,
                        "parentId": if_id, "enabled": True, "index": 1,
                    },
                ],
                "id": if_id, "weight": 0.0, "type": 120,
                "parentId": twitch_id, "enabled": True, "index": 2,
            },
        ],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    # --- Kick branch ---
    kick_id = str(uuid.uuid4())
    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"text": not_available, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
             "parentId": kick_id, "enabled": True, "index": 0}
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    # --- YouTube branch ---
    youtube_id = str(uuid.uuid4())
    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"text": not_available, "useBot": True, "fallback": True, "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
             "parentId": youtube_id, "enabled": True, "index": 0}
        ],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    # --- Default branch ---
    default_id = str(uuid.uuid4())
    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_lurk_code(messages):
    """
    Generates the inline C# for the !lurk command.

    - Picks a random message from the embedded list.
    - Replaces {user} placeholder with the username from args.
    - Sets %lurkResult% argument.
    - No AI or HTTP calls; uses only mscorlib.dll.
    """
    messages_str = "\n".join(f"        {csharp_literal(m)}," for m in messages)
    user_ph = csharp_literal("{user}")

    return f"""\
using System;

public class CPHInline
{{
    private static readonly string[] Messages = new[]
    {{
{messages_str}
    }};

    public bool Execute()
    {{
        var rng = new Random();
        string user = args.ContainsKey("user") ? args["user"].ToString() : "";
        string msg = Messages[rng.Next(Messages.Length)].Replace({user_ph}, user);
        CPH.SetArgument("lurkResult", msg);
        return true;
    }}
}}"""


def build_fortune_code(fortunes):
    """
    Generates the inline C# for the !fortune command.

    - Picks a random fortune from the embedded list.
    - Sets %fortuneResult% argument — the platform switch sends it to chat.
    - No AI or HTTP calls; uses only mscorlib.dll.
    """
    fortunes_str = "\n".join(f"        {csharp_literal(f)}," for f in fortunes)

    return f"""\
using System;

public class CPHInline
{{
    private static readonly string[] Fortunes = new[]
    {{
{fortunes_str}
    }};

    public bool Execute()
    {{
        var rng = new Random();
        string fortune = Fortunes[rng.Next(Fortunes.Length)];
        CPH.SetArgument("fortuneResult", fortune);
        return true;
    }}
}}"""


def build_joke_code(fallbacks, language, empty_prompt, topic_prompt):
    """
    Generates the inline C# for the !joke command.

    - Extracts the topic from rawInput (text after the command trigger).
    - Calls OpenAI with the comedian system prompt if openai_api_key is set.
    - Falls back to a random local joke on missing key or any error.
    - Uses System.Net.WebClient (requires System.dll reference).
    """
    fallbacks_str = "\n".join(f'        "{f}",' for f in fallbacks)

    system_prompt = COMEDIAN_SYSTEM_PROMPT.replace("{language}", language)
    sp_lit = csharp_literal(system_prompt)

    empty_lit = csharp_literal(empty_prompt)
    topic_lit = csharp_literal(topic_prompt)

    # JSON body pieces (same pattern as 8ball)
    body_start = csharp_literal('{"model":"gpt-4o-mini","messages":[')
    sys_open   = csharp_literal('{"role":"system","content":"')
    sys_close  = csharp_literal('"},')
    user_open  = csharp_literal('{"role":"user","content":"')
    user_close = csharp_literal('"}]')
    body_end   = csharp_literal(',"max_tokens":600,"temperature":0.9}')
    content_key = csharp_literal('"content"')

    bs    = csharp_literal('\\')
    bs2   = csharp_literal('\\\\')
    dq    = csharp_literal('"')
    bs_dq = csharp_literal('\\"')
    nl    = csharp_literal('\n')
    bs_n  = csharp_literal('\\n')
    cr    = csharp_literal('\r')
    bs_r  = csharp_literal('\\r')

    return f"""\
using System;
using System.Net;
using System.Text;

public class CPHInline
{{
    private static readonly string[] Fallbacks = new[]
    {{
{fallbacks_str}
    }};

    private const string SystemPrompt = {sp_lit};

    public bool Execute()
    {{
        var rng = new Random();

        string topic = "";
        if (args.ContainsKey("rawInput"))
            topic = args["rawInput"].ToString().Trim();

        string userPrompt = string.IsNullOrEmpty(topic)
            ? {empty_lit}
            : {topic_lit} + topic;

        string apiKey = CPH.GetGlobalVar<string>("openai_api_key", true);
        if (!string.IsNullOrEmpty(apiKey))
        {{
            try
            {{
                string response = CallOpenAI(apiKey, userPrompt);
                if (!string.IsNullOrEmpty(response))
                {{
                    var jokes = new System.Collections.Generic.List<string>();
                    foreach (string line in response.Split('\\n'))
                    {{
                        string t = line.Trim();
                        int dotIdx = t.IndexOf(". ");
                        if (dotIdx > 0 && dotIdx <= 3)
                        {{
                            string text = t.Substring(dotIdx + 2).Trim();
                            if (text.Length > 0) jokes.Add(text);
                        }}
                    }}
                    string chosen = jokes.Count > 0 ? jokes[rng.Next(jokes.Count)] : response;
                    CPH.SetArgument("jokeResult", chosen);
                    return true;
                }}
            }}
            catch {{ }}
        }}

        CPH.SetArgument("jokeResult", Fallbacks[rng.Next(Fallbacks.Length)]);
        return true;
    }}

    private string CallOpenAI(string apiKey, string userMessage)
    {{
        string body = {body_start}
            + {sys_open} + Escape(SystemPrompt) + {sys_close}
            + {user_open} + Escape(userMessage) + {user_close}
            + {body_end};
        using (var client = new WebClient())
        {{
            client.Headers[HttpRequestHeader.Authorization] = "Bearer " + apiKey;
            client.Headers[HttpRequestHeader.ContentType] = "application/json";
            byte[] data = client.UploadData(
                "https://api.openai.com/v1/chat/completions", "POST",
                Encoding.UTF8.GetBytes(body));
            return ExtractContent(Encoding.UTF8.GetString(data));
        }}
    }}

    private static string ExtractContent(string json)
    {{
        int ci = json.IndexOf({content_key});
        if (ci < 0) return null;
        int colon = json.IndexOf(':', ci + 9);
        if (colon < 0) return null;
        int quote = json.IndexOf('"', colon + 1);
        if (quote < 0) return null;
        int start = quote + 1;
        int end = start;
        while (end < json.Length)
        {{
            if (json[end] == '"' && (end == 0 || json[end - 1] != '\\\\')) break;
            end++;
        }}
        return json.Substring(start, end - start)
                   .Replace({bs_dq}, {dq})
                   .Replace({bs_n}, {nl})
                   .Replace({bs2}, {bs});
    }}

    private static string Escape(string s)
    {{
        return s.Replace({bs}, {bs2})
                .Replace({dq}, {bs_dq})
                .Replace({nl}, {bs_n})
                .Replace({cr}, {bs_r});
    }}
}}"""


def make_set_variable(name, value, parent_id=None, index=0):
    return {
        "variableName": name, "value": value,
        "id": str(uuid.uuid4()), "weight": 0.0, "type": 123,
        "parentId": parent_id, "enabled": True, "index": index,
    }


def make_get_variable(parent_id=None, index=0):
    return {
        "id": str(uuid.uuid4()), "weight": 0.0, "type": 1007,
        "parentId": parent_id, "enabled": True, "index": index,
    }


def make_csharp_subaction_ext(code, references, parent_id=None, index=0):
    """Like make_csharp_subaction but with custom references list."""
    byte_code = base64.b64encode(code.encode("utf-8")).decode("utf-8")
    return {
        "name": "",
        "description": "",
        "references": references,
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


def make_native_action(name, group, queue_id, sub_actions):
    """
    Build a native action (no inline C#) with explicit sub_actions list.
    sub_actions must already have correct parentId and index set.
    Returns (action_id, command_id, action_dict).
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": sub_actions,
        "collapsedGroups": [],
    }
    return action_id, command_id, action


def build_oracle_code(styles, fallback, no_input, persona):
    """
    Generates inline C# for !oracle.

    - Reads ai_licia_key from Streamer.bot persisted global variable.
    - Reads broadcastUserName from args (no extra variable needed).
    - If no question given, sends noInput message.
    - Picks a random style prompt, replaces {user} and {text}, truncates to 300 chars.
    - POSTs persona context to /v1/events (ttl=60) then triggers /v1/events/generations.
    - Falls back to a local pool if ai_licia_key is missing or call fails.
    """
    styles_str   = "\n".join(f"        {csharp_literal(s)}," for s in styles)
    fallback_str = "\n".join(f"        {csharp_literal(f)}," for f in fallback)

    no_input_lit = csharp_literal(no_input)
    persona_lit  = csharp_literal(persona)
    user_ph      = csharp_literal("{user}")
    text_ph      = csharp_literal("{text}")

    bs    = csharp_literal('\\')
    bs2   = csharp_literal('\\\\')
    dq    = csharp_literal('"')
    bs_dq = csharp_literal('\\"')
    nl    = csharp_literal('\n')
    bs_n  = csharp_literal('\\n')
    cr    = csharp_literal('\r')
    bs_r  = csharp_literal('\\r')

    ev_open  = csharp_literal('{"eventType":"GAME_EVENT","data":{"channelName":"')
    ev_cont  = csharp_literal('","content":"')
    ev_ttl   = csharp_literal('","ttl":60}}')
    ev_close = csharp_literal('"}}')

    return f"""\
using System;
using System.Net;
using System.Text;

public class CPHInline
{{
    private static readonly string[] Styles = new[]
    {{
{styles_str}
    }};

    private static readonly string[] Fallback = new[]
    {{
{fallback_str}
    }};

    private const string Persona = {persona_lit};
    private const string NoInput = {no_input_lit};
    private const string BaseUrl = "https://api.getailicia.com";

    public bool Execute()
    {{
        string user  = args.ContainsKey("user")     ? args["user"].ToString()             : "";
        string input = args.ContainsKey("rawInput") ? args["rawInput"].ToString().Trim()  : "";

        if (string.IsNullOrEmpty(input))
        {{
            CPH.SendMessage(NoInput.Replace({user_ph}, user));
            return true;
        }}

        string apiKey = CPH.GetGlobalVar<string>("ai_licia_key", true);
        string channelName = "";
        CPH.TryGetArg("broadcastUserName", out channelName);

        if (!string.IsNullOrEmpty(apiKey) && !string.IsNullOrEmpty(channelName))
        {{
            try
            {{
                var rng    = new Random();
                string style  = Styles[rng.Next(Styles.Length)];
                string prompt = style.Replace({user_ph}, user).Replace({text_ph}, input);
                if (prompt.Length > 300) prompt = prompt.Substring(0, 300);

                PostEvent(apiKey, channelName, Persona, withTtl: true);
                PostEvent(apiKey, channelName, prompt,  withTtl: false);
                return true;
            }}
            catch {{ }}
        }}

        var rng2    = new Random();
        string message = Fallback[rng2.Next(Fallback.Length)].Replace({user_ph}, user);
        CPH.SendMessage(message);
        return true;
    }}

    private void PostEvent(string apiKey, string channelName, string content, bool withTtl)
    {{
        string path = withTtl ? "/v1/events" : "/v1/events/generations";
        string body = withTtl
            ? {ev_open} + Escape(channelName) + {ev_cont} + Escape(content) + {ev_ttl}
            : {ev_open} + Escape(channelName) + {ev_cont} + Escape(content) + {ev_close};
        using (var client = new WebClient())
        {{
            client.Headers["Authorization"] = "Bearer " + apiKey;
            client.Headers["Content-Type"]  = "application/json";
            client.UploadData(BaseUrl + path, "POST", Encoding.UTF8.GetBytes(body));
        }}
    }}

    private static string Escape(string s)
    {{
        return s.Replace({bs}, {bs2})
                .Replace({dq}, {bs_dq})
                .Replace({nl}, {bs_n})
                .Replace({cr}, {bs_r});
    }}
}}"""


def build_oracle_action(name, group, code, queue_id):
    """Action for AI_Licia commands: label + C# only, no chat switch (AI_Licia sends to chat)."""
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    return action_id, command_id, {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()), "weight": 0.0,
             "type": 1009, "parentId": None, "enabled": True, "index": 0},
            make_csharp_subaction(code, parent_id=None, index=1),
        ],
        "collapsedGroups": [],
    }


def build_ailicia_useronly_code(styles, fallback, persona):
    """
    Generates inline C# for user-only AI_Licia commands (omen, tarot).

    No input required — always picks a random style prompt with only {user}.
    Falls back to local pool if ai_licia_key is missing.
    """
    styles_str   = "\n".join(f"        {csharp_literal(s)}," for s in styles)
    fallback_str = "\n".join(f"        {csharp_literal(f)}," for f in fallback)

    persona_lit  = csharp_literal(persona)
    user_ph      = csharp_literal("{user}")

    bs    = csharp_literal('\\')
    bs2   = csharp_literal('\\\\')
    dq    = csharp_literal('"')
    bs_dq = csharp_literal('\\"')
    nl    = csharp_literal('\n')
    bs_n  = csharp_literal('\\n')
    cr    = csharp_literal('\r')
    bs_r  = csharp_literal('\\r')

    ev_open  = csharp_literal('{"eventType":"GAME_EVENT","data":{"channelName":"')
    ev_cont  = csharp_literal('","content":"')
    ev_ttl   = csharp_literal('","ttl":60}}')
    ev_close = csharp_literal('"}}')

    return f"""\
using System;
using System.Net;
using System.Text;

public class CPHInline
{{
    private static readonly string[] Styles = new[]
    {{
{styles_str}
    }};

    private static readonly string[] Fallback = new[]
    {{
{fallback_str}
    }};

    private const string Persona = {persona_lit};
    private const string BaseUrl = "https://api.getailicia.com";

    public bool Execute()
    {{
        string user = args.ContainsKey("user") ? args["user"].ToString() : "";

        string apiKey = CPH.GetGlobalVar<string>("ai_licia_key", true);
        string channelName = "";
        CPH.TryGetArg("broadcastUserName", out channelName);

        if (!string.IsNullOrEmpty(apiKey) && !string.IsNullOrEmpty(channelName))
        {{
            try
            {{
                var rng   = new Random();
                string prompt = Styles[rng.Next(Styles.Length)].Replace({user_ph}, user);
                if (prompt.Length > 300) prompt = prompt.Substring(0, 300);

                PostEvent(apiKey, channelName, Persona, withTtl: true);
                PostEvent(apiKey, channelName, prompt,  withTtl: false);
                return true;
            }}
            catch {{ }}
        }}

        var rng2    = new Random();
        string message = Fallback[rng2.Next(Fallback.Length)].Replace({user_ph}, user);
        CPH.SendMessage(message);
        return true;
    }}

    private void PostEvent(string apiKey, string channelName, string content, bool withTtl)
    {{
        string path = withTtl ? "/v1/events" : "/v1/events/generations";
        string body = withTtl
            ? {ev_open} + Escape(channelName) + {ev_cont} + Escape(content) + {ev_ttl}
            : {ev_open} + Escape(channelName) + {ev_cont} + Escape(content) + {ev_close};
        using (var client = new WebClient())
        {{
            client.Headers["Authorization"] = "Bearer " + apiKey;
            client.Headers["Content-Type"]  = "application/json";
            client.UploadData(BaseUrl + path, "POST", Encoding.UTF8.GetBytes(body));
        }}
    }}

    private static string Escape(string s)
    {{
        return s.Replace({bs}, {bs2})
                .Replace({dq}, {bs_dq})
                .Replace({nl}, {bs_n})
                .Replace({cr}, {bs_r});
    }}
}}"""


def build_ailicia_judge_code(styles, fallback, no_input, persona):
    """
    Generates inline C# for !judge.

    - judge = user who invoked the command
    - target = rawInput (stripped of leading @)
    - noInput uses {judge}; styles/fallback use {judge} and {target}
    """
    styles_str   = "\n".join(f"        {csharp_literal(s)}," for s in styles)
    fallback_str = "\n".join(f"        {csharp_literal(f)}," for f in fallback)

    no_input_lit = csharp_literal(no_input)
    persona_lit  = csharp_literal(persona)
    judge_ph     = csharp_literal("{judge}")
    target_ph    = csharp_literal("{target}")

    bs    = csharp_literal('\\')
    bs2   = csharp_literal('\\\\')
    dq    = csharp_literal('"')
    bs_dq = csharp_literal('\\"')
    nl    = csharp_literal('\n')
    bs_n  = csharp_literal('\\n')
    cr    = csharp_literal('\r')
    bs_r  = csharp_literal('\\r')

    ev_open  = csharp_literal('{"eventType":"GAME_EVENT","data":{"channelName":"')
    ev_cont  = csharp_literal('","content":"')
    ev_ttl   = csharp_literal('","ttl":60}}')
    ev_close = csharp_literal('"}}')

    return f"""\
using System;
using System.Net;
using System.Text;

public class CPHInline
{{
    private static readonly string[] Styles = new[]
    {{
{styles_str}
    }};

    private static readonly string[] Fallback = new[]
    {{
{fallback_str}
    }};

    private const string Persona = {persona_lit};
    private const string NoInput = {no_input_lit};
    private const string BaseUrl = "https://api.getailicia.com";

    public bool Execute()
    {{
        string judge  = args.ContainsKey("user")     ? args["user"].ToString()            : "";
        string target = args.ContainsKey("rawInput") ? args["rawInput"].ToString().Trim() : "";
        if (target.StartsWith("@")) target = target.Substring(1).Trim();

        if (string.IsNullOrEmpty(target))
        {{
            CPH.SendMessage(NoInput.Replace({judge_ph}, judge));
            return true;
        }}

        string apiKey = CPH.GetGlobalVar<string>("ai_licia_key", true);
        string channelName = "";
        CPH.TryGetArg("broadcastUserName", out channelName);

        if (!string.IsNullOrEmpty(apiKey) && !string.IsNullOrEmpty(channelName))
        {{
            try
            {{
                var rng    = new Random();
                string style  = Styles[rng.Next(Styles.Length)];
                string prompt = style.Replace({judge_ph}, judge).Replace({target_ph}, target);
                if (prompt.Length > 300) prompt = prompt.Substring(0, 300);

                PostEvent(apiKey, channelName, Persona, withTtl: true);
                PostEvent(apiKey, channelName, prompt,  withTtl: false);
                return true;
            }}
            catch {{ }}
        }}

        var rng2    = new Random();
        string message = Fallback[rng2.Next(Fallback.Length)]
            .Replace({judge_ph}, judge).Replace({target_ph}, target);
        CPH.SendMessage(message);
        return true;
    }}

    private void PostEvent(string apiKey, string channelName, string content, bool withTtl)
    {{
        string path = withTtl ? "/v1/events" : "/v1/events/generations";
        string body = withTtl
            ? {ev_open} + Escape(channelName) + {ev_cont} + Escape(content) + {ev_ttl}
            : {ev_open} + Escape(channelName) + {ev_cont} + Escape(content) + {ev_close};
        using (var client = new WebClient())
        {{
            client.Headers["Authorization"] = "Bearer " + apiKey;
            client.Headers["Content-Type"]  = "application/json";
            client.UploadData(BaseUrl + path, "POST", Encoding.UTF8.GetBytes(body));
        }}
    }}

    private static string Escape(string s)
    {{
        return s.Replace({bs}, {bs2})
                .Replace({dq}, {bs_dq})
                .Replace({nl}, {bs_n})
                .Replace({cr}, {bs_r});
    }}
}}"""


def build_ailicia_hex_code(styles, fallback, no_input, persona):
    """
    Generates inline C# for !hex.

    - caster = user who invoked the command ({user} and {caster} both map to user)
    - target = rawInput (stripped of leading @)
    - noInput/fallback use {user}; styles use {caster} and {target}
    """
    styles_str   = "\n".join(f"        {csharp_literal(s)}," for s in styles)
    fallback_str = "\n".join(f"        {csharp_literal(f)}," for f in fallback)

    no_input_lit = csharp_literal(no_input)
    persona_lit  = csharp_literal(persona)
    user_ph      = csharp_literal("{user}")
    caster_ph    = csharp_literal("{caster}")
    target_ph    = csharp_literal("{target}")

    bs    = csharp_literal('\\')
    bs2   = csharp_literal('\\\\')
    dq    = csharp_literal('"')
    bs_dq = csharp_literal('\\"')
    nl    = csharp_literal('\n')
    bs_n  = csharp_literal('\\n')
    cr    = csharp_literal('\r')
    bs_r  = csharp_literal('\\r')

    ev_open  = csharp_literal('{"eventType":"GAME_EVENT","data":{"channelName":"')
    ev_cont  = csharp_literal('","content":"')
    ev_ttl   = csharp_literal('","ttl":60}}')
    ev_close = csharp_literal('"}}')

    return f"""\
using System;
using System.Net;
using System.Text;

public class CPHInline
{{
    private static readonly string[] Styles = new[]
    {{
{styles_str}
    }};

    private static readonly string[] Fallback = new[]
    {{
{fallback_str}
    }};

    private const string Persona = {persona_lit};
    private const string NoInput = {no_input_lit};
    private const string BaseUrl = "https://api.getailicia.com";

    public bool Execute()
    {{
        string user   = args.ContainsKey("user")     ? args["user"].ToString()            : "";
        string target = args.ContainsKey("rawInput") ? args["rawInput"].ToString().Trim() : "";
        if (target.StartsWith("@")) target = target.Substring(1).Trim();

        if (string.IsNullOrEmpty(target))
        {{
            CPH.SendMessage(NoInput.Replace({user_ph}, user));
            return true;
        }}

        string apiKey = CPH.GetGlobalVar<string>("ai_licia_key", true);
        string channelName = "";
        CPH.TryGetArg("broadcastUserName", out channelName);

        if (!string.IsNullOrEmpty(apiKey) && !string.IsNullOrEmpty(channelName))
        {{
            try
            {{
                var rng    = new Random();
                string style  = Styles[rng.Next(Styles.Length)];
                string prompt = style.Replace({caster_ph}, user).Replace({target_ph}, target);
                if (prompt.Length > 300) prompt = prompt.Substring(0, 300);

                PostEvent(apiKey, channelName, Persona, withTtl: true);
                PostEvent(apiKey, channelName, prompt,  withTtl: false);
                return true;
            }}
            catch {{ }}
        }}

        var rng2    = new Random();
        string message = Fallback[rng2.Next(Fallback.Length)]
            .Replace({user_ph}, user).Replace({target_ph}, target);
        CPH.SendMessage(message);
        return true;
    }}

    private void PostEvent(string apiKey, string channelName, string content, bool withTtl)
    {{
        string path = withTtl ? "/v1/events" : "/v1/events/generations";
        string body = withTtl
            ? {ev_open} + Escape(channelName) + {ev_cont} + Escape(content) + {ev_ttl}
            : {ev_open} + Escape(channelName) + {ev_cont} + Escape(content) + {ev_close};
        using (var client = new WebClient())
        {{
            client.Headers["Authorization"] = "Bearer " + apiKey;
            client.Headers["Content-Type"]  = "application/json";
            client.UploadData(BaseUrl + path, "POST", Encoding.UTF8.GetBytes(body));
        }}
    }}

    private static string Escape(string s)
    {{
        return s.Replace({bs}, {bs2})
                .Replace({dq}, {bs_dq})
                .Replace({nl}, {bs_n})
                .Replace({cr}, {bs_r});
    }}
}}"""


def build_shoutout_action(name, group, queue_id, unknown_msg, unknown_kick_msg,
                          twitch_msg, kick_msg, not_available_msg):
    """
    !shoutout native action.

    Twitch:
      1. type 50  TwitchGetInfoForTarget -> sets %targetUser% / %targetUserName% / %game%
      2. if/else: targetUser == null/empty -> send unknown | announce + type 29 shoutout

    Kick:
      1. type 35011 KickGetInfoForTarget
      2. if/else -> send unknown | kick chat msg

    YouTube: not available
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())

    # ---------- Twitch branch ----------
    twitch_id  = str(uuid.uuid4())
    if_tw_id   = str(uuid.uuid4())
    then_tw_id = str(uuid.uuid4())
    else_tw_id = str(uuid.uuid4())

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [
            # Get target user info
            {"userLogin": "%input0%",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 50,
             "parentId": twitch_id, "enabled": True, "index": 0},
            # If targetUser is empty -> unknown; else announce + shoutout
            {
                "input": "%targetUser%", "operation": 6, "value": None, "autoType": False,
                "subActions": [
                    {
                        "random": False,
                        "subActions": [
                            {"text": unknown_msg, "color": 4, "useBot": True, "fallback": True,
                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
                             "parentId": then_tw_id, "enabled": True, "index": 0},
                        ],
                        "id": then_tw_id, "weight": 0.0, "type": 99901,
                        "parentId": if_tw_id, "enabled": True, "index": 0,
                    },
                    {
                        "random": False,
                        "subActions": [
                            {"text": twitch_msg, "color": 4, "useBot": True, "fallback": True,
                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
                             "parentId": else_tw_id, "enabled": True, "index": 0},
                            {"userLogin": "%targetUserName%",
                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 29,
                             "parentId": else_tw_id, "enabled": True, "index": 1},
                        ],
                        "id": else_tw_id, "weight": 0.0, "type": 99902,
                        "parentId": if_tw_id, "enabled": True, "index": 1,
                    },
                ],
                "id": if_tw_id, "weight": 0.0, "type": 120,
                "parentId": twitch_id, "enabled": True, "index": 1,
            },
        ],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    # ---------- Kick branch ----------
    kick_id   = str(uuid.uuid4())
    if_kk_id  = str(uuid.uuid4())
    then_kk_id = str(uuid.uuid4())
    else_kk_id = str(uuid.uuid4())

    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"userLogin": "%input0%",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35011,
             "parentId": kick_id, "enabled": True, "index": 0},
            {
                "input": "%targetUser%", "operation": 6, "value": None, "autoType": False,
                "subActions": [
                    {
                        "random": False,
                        "subActions": [
                            {"text": unknown_kick_msg, "useBot": True, "fallback": True,
                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
                             "parentId": then_kk_id, "enabled": True, "index": 0},
                        ],
                        "id": then_kk_id, "weight": 0.0, "type": 99901,
                        "parentId": if_kk_id, "enabled": True, "index": 0,
                    },
                    {
                        "random": False,
                        "subActions": [
                            {"text": kick_msg, "useBot": True, "fallback": True,
                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
                             "parentId": else_kk_id, "enabled": True, "index": 0},
                        ],
                        "id": else_kk_id, "weight": 0.0, "type": 99902,
                        "parentId": if_kk_id, "enabled": True, "index": 1,
                    },
                ],
                "id": if_kk_id, "weight": 0.0, "type": 120,
                "parentId": kick_id, "enabled": True, "index": 1,
            },
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    # ---------- YouTube branch (not available) ----------
    youtube_id = str(uuid.uuid4())
    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True, "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
             "parentId": youtube_id, "enabled": True, "index": 0},
        ],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_id = str(uuid.uuid4())
    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_settitle_action(name, group, queue_id):
    """
    !settitle — fully native, no messages.
    Twitch: type 15, Kick: type 35030, YouTube: type 4002
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())

    twitch_id = str(uuid.uuid4())
    kick_id   = str(uuid.uuid4())
    yt_id     = str(uuid.uuid4())
    default_id = str(uuid.uuid4())

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [
            {"title": "%rawInput%",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 15,
             "parentId": twitch_id, "enabled": True, "index": 0},
        ],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"title": "%rawInput%",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35030,
             "parentId": kick_id, "enabled": True, "index": 0},
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"title": "%rawInput%", "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4002,
             "parentId": yt_id, "enabled": True, "index": 0},
        ],
        "id": yt_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


IGDB_CSHARP = """\
using System;
using Newtonsoft.Json.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text;

public class CPHInline
{
    private static readonly HttpClient client = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };

    public bool Execute()
    {
        CPH.TryGetArg("user", out string user);
        CPH.TryGetArg("rawInput", out string rawInput);
        try
        {
            string IGDBGameName = GetIGDBGameName(rawInput).GetAwaiter().GetResult();
            CPH.SetArgument("foundGame", IGDBGameName);
        }
        catch (Exception ex) { return false; }
        return true;
    }

    private async Task<string> GetIGDBGameName(string keyword)
    {
        string accessToken = CPH.TwitchOAuthToken;
        string clientId = CPH.TwitchClientId;
        var url = "https://api.igdb.com/v4/games";
        client.DefaultRequestHeaders.Clear();
        client.DefaultRequestHeaders.Add("Client-ID", clientId);
        client.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}");
        var requestBody = new StringContent($"fields name,url,cover.image_id; search \\"{keyword}\\";", Encoding.UTF8, "application/json");
        var response = await client.PostAsync(url, requestBody);
        response.EnsureSuccessStatusCode();
        var responseBody = await response.Content.ReadAsStringAsync();
        var jsonResponse = JArray.Parse(responseBody);
        JObject selectedGame = null;
        string IGDBGameName = null;
        foreach (var game in jsonResponse)
        {
            if (string.Equals(game["name"]?.ToString(), keyword, StringComparison.OrdinalIgnoreCase))
            { selectedGame = (JObject)game; break; }
        }
        if (selectedGame == null && jsonResponse.Count > 0)
            selectedGame = (JObject)jsonResponse[1];
        if (selectedGame != null)
            IGDBGameName = selectedGame["name"]?.ToString() ?? "Unknown Title";
        return IGDBGameName;
    }
}"""

IGDB_REFERENCES = [
    "C:\\\\Windows\\\\Microsoft.NET\\\\Framework64\\\\v4.0.30319\\\\mscorlib.dll",
    "C:\\\\Windows\\\\Microsoft.NET\\\\Framework64\\\\v4.0.30319\\\\System.Net.Http.dll",
    ".\\\\Newtonsoft.Json.dll",
    "C:\\\\Windows\\\\Microsoft.NET\\\\Framework64\\\\v4.0.30319\\\\System.dll",
]

TRANSLATE_CSHARP = """\
using System;
using System.Web;
using System.Net;
using Newtonsoft.Json.Linq;

public class CPHInline
{
    public bool Execute()
    {
        CPH.TryGetArg("rawInput", out string text);
        CPH.TryGetArg("fromLanguage", out string fromLanguage);
        CPH.TryGetArg("toLanguage", out string toLanguage);
        CPH.SetArgument("translationText", Translate(text, fromLanguage, toLanguage));
        return true;
    }

    public String Translate(string text, string fromLanguage, string toLanguage)
    {
        var url = $"https://translate.googleapis.com/translate_a/single?client=gtx&sl={fromLanguage}&tl={toLanguage}&dt=t&q={HttpUtility.UrlEncode(text)}";
        var webClient = new WebClient { Encoding = System.Text.Encoding.UTF8 };
        string result = webClient.DownloadString(url);
        JArray array = JArray.Parse(result);
        JArray translationItems = array[0] as JArray;
        string translation = "";
        foreach (JArray item in translationItems)
            translation += $" {item[0].ToString()}";
        if (translation.Length > 1)
            translation = translation.Substring(1);
        return translation;
    }
}"""

TRANSLATE_REFERENCES = [
    "C:\\\\Windows\\\\Microsoft.NET\\\\Framework64\\\\v4.0.30319\\\\mscorlib.dll",
    ".\\\\Newtonsoft.Json.dll",
    "C:\\\\Windows\\\\Microsoft.NET\\\\Framework64\\\\v4.0.30319\\\\System.dll",
    "C:\\\\Windows\\\\Microsoft.NET\\\\Framework64\\\\v4.0.30319\\\\System.Web.dll",
]

# Step 1: resolve user, set %inputUser% and %inputUserName%, save return to %userFound%.
ACCOUNTAGE_CSHARP_RESOLVE = """\
using System;
public class CPHInline
{
    public bool Execute()
    {
        CPH.TryGetArg("input0", out string input0);
        CPH.TryGetArg("userName", out string userName);
        CPH.TryGetArg("user", out string displayName);

        if (!string.IsNullOrEmpty(input0) && input0.StartsWith("@"))
            input0 = input0.Substring(1);

        if (string.IsNullOrEmpty(input0))
        {
            CPH.SetArgument("inputUser", displayName);
            CPH.SetArgument("inputUserName", userName);
            return true;
        }

        TwitchUserInfo user = CPH.TwitchGetUserInfoByLogin(input0);
        if (user == null)
        {
            CPH.TwitchAnnounce($"@{userName} I have no idea who {input0} is WutFace", false, "purple");
            return false;
        }
        CPH.SetArgument("inputUser", user.UserName);
        CPH.SetArgument("inputUserName", user.UserLogin);
        return true;
    }
}"""


# Followage uses a separate resolve step that also sets %inputUserName% for the type-51 sub-action.
FOLLOWAGE_CSHARP_1 = """\
using System;
public class CPHInline
{
    public bool Execute()
    {
        CPH.TryGetArg("input0", out string input0);
        CPH.TryGetArg("userName", out string userName);
        if (String.IsNullOrEmpty(input0)) input0 = userName;
        TwitchUserInfo user = CPH.TwitchGetUserInfoByLogin(input0);
        if (user != null)
        {
            CPH.SetArgument("inputUser", user.UserName);
            CPH.SetArgument("inputUserName", user.UserLogin);
            return true;
        }
        else
        {
            CPH.SendAction($"@{userName} I have no idea who {input0} is WutFace");
            return false;
        }
    }
}"""

FOLLOWAGE_CSHARP_2 = """\
using System;
public class CPHInline
{
    public bool Execute()
    {
        CPH.TryGetArg("inputUser", out string inputUser);
        CPH.TryGetArg("broadcastUserName", out string broadcastUserName);
        CPH.TryGetArg("followAgeLong", out string followAgeLong);
        if (followAgeLong != null)
            CPH.SendAction($"{inputUser} has been following for {followAgeLong}");
        else
            CPH.SendAction($"{inputUser} is not following {broadcastUserName}");
        return true;
    }
}"""

UPTIME_CSHARP = """\
using System;
public class CPHInline
{
    string announcementColor = "purple";
    public bool Execute()
    {
        CPH.TryGetArg("broadcastUser", out string broadcastUser);
        CPH.TryGetArg("uptime", out string uptime);
        if (uptime.Contains("is offline"))
            CPH.TwitchAnnounce($"{broadcastUser} is offline", false, announcementColor);
        else if (uptime.Contains("404"))
            CPH.TwitchAnnounce($"You did something wrong, bro", false, announcementColor);
        else
            CPH.TwitchAnnounce($"{broadcastUser} has been live for {uptime.Replace(\\",\\", \\"\\")}", false, announcementColor);
        return true;
    }
}"""


def build_setgame_action(name, group, queue_id, not_found_msg, not_found_game_msg, not_available_msg):
    """
    !setgame — type 16 (Twitch) / type 35031 (Kick) with IGDB C# fallback.
    Not available on YouTube.
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())

    igdb_refs = [
        "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
        "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.Net.Http.dll",
        ".\\Newtonsoft.Json.dll",
        "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
    ]

    # --- Twitch branch ---
    twitch_id     = str(uuid.uuid4())
    if_tw_id      = str(uuid.uuid4())
    then_tw_id    = str(uuid.uuid4())
    else_tw_id    = str(uuid.uuid4())
    if_tw2_id     = str(uuid.uuid4())
    then_tw2_id   = str(uuid.uuid4())
    else_tw2_id   = str(uuid.uuid4())

    def _igdb_sub(parent_id, index):
        byte_code = base64.b64encode(IGDB_CSHARP.encode("utf-8")).decode("utf-8")
        return {
            "name": "", "description": "",
            "references": igdb_refs,
            "byteCode": byte_code,
            "precompile": False, "delayStart": False,
            "saveResultToVariable": False, "saveToVariable": "",
            "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
            "parentId": parent_id, "enabled": True, "index": index,
        }

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [
            # 1. Try set game directly
            {"source": 0, "game": "%rawInput%", "gameId": None,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 16,
             "parentId": twitch_id, "enabled": True, "index": 0},
            # 2. If gameSuccess == False -> IGDB fallback
            {
                "input": "%gameSuccess%", "operation": 0, "value": "False", "autoType": True,
                "subActions": [
                    {
                        "random": False,
                        "subActions": [
                            # IGDB search C#
                            _igdb_sub(then_tw_id, 0),
                            # if foundGame empty -> error
                            {
                                "input": "%foundGame%", "operation": 6, "value": None, "autoType": False,
                                "subActions": [
                                    {
                                        "random": False,
                                        "subActions": [
                                            {"text": not_found_msg, "color": 4, "useBot": True, "fallback": True,
                                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
                                             "parentId": str(uuid.uuid4()), "enabled": True, "index": 0},
                                        ],
                                        "id": str(uuid.uuid4()), "weight": 0.0, "type": 99901,
                                        "parentId": if_tw2_id, "enabled": True, "index": 0,
                                    },
                                    {
                                        "random": False,
                                        "subActions": [
                                            {"source": 0, "game": "%foundGame%", "gameId": None,
                                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 16,
                                             "parentId": else_tw2_id, "enabled": True, "index": 0},
                                            # if still fails -> error
                                            {
                                                "input": "%gameSuccess%", "operation": 0, "value": "False",
                                                "autoType": True,
                                                "subActions": [
                                                    {
                                                        "random": False,
                                                        "subActions": [
                                                            {"text": not_found_game_msg, "color": 4, "useBot": True,
                                                             "fallback": True,
                                                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
                                                             "parentId": str(uuid.uuid4()), "enabled": True, "index": 0},
                                                        ],
                                                        "id": str(uuid.uuid4()), "weight": 0.0, "type": 99901,
                                                        "parentId": str(uuid.uuid4()), "enabled": True, "index": 0,
                                                    },
                                                ],
                                                "id": str(uuid.uuid4()), "weight": 0.0, "type": 120,
                                                "parentId": else_tw2_id, "enabled": True, "index": 1,
                                            },
                                        ],
                                        "id": else_tw2_id, "weight": 0.0, "type": 99902,
                                        "parentId": if_tw2_id, "enabled": True, "index": 1,
                                    },
                                ],
                                "id": if_tw2_id, "weight": 0.0, "type": 120,
                                "parentId": then_tw_id, "enabled": True, "index": 1,
                            },
                        ],
                        "id": then_tw_id, "weight": 0.0, "type": 99901,
                        "parentId": if_tw_id, "enabled": True, "index": 0,
                    },
                ],
                "id": if_tw_id, "weight": 0.0, "type": 120,
                "parentId": twitch_id, "enabled": True, "index": 1,
            },
        ],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    # --- Kick branch ---
    kick_id      = str(uuid.uuid4())
    if_kk_id     = str(uuid.uuid4())
    then_kk_id   = str(uuid.uuid4())
    else_kk_id   = str(uuid.uuid4())
    if_kk2_id    = str(uuid.uuid4())
    else_kk2_id  = str(uuid.uuid4())

    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"source": 0, "categoryName": "%rawInput%", "categoryId": None,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35031,
             "parentId": kick_id, "enabled": True, "index": 0},
            {
                "input": "%category.success%", "operation": 0, "value": "False", "autoType": True,
                "subActions": [
                    {
                        "random": False,
                        "subActions": [
                            _igdb_sub(then_kk_id, 0),
                            {
                                "input": "%foundGame%", "operation": 6, "value": None, "autoType": False,
                                "subActions": [
                                    {
                                        "random": False,
                                        "subActions": [
                                            {"text": not_found_msg, "useBot": True, "fallback": True,
                                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
                                             "parentId": str(uuid.uuid4()), "enabled": True, "index": 0},
                                        ],
                                        "id": str(uuid.uuid4()), "weight": 0.0, "type": 99901,
                                        "parentId": if_kk2_id, "enabled": True, "index": 0,
                                    },
                                    {
                                        "random": False,
                                        "subActions": [
                                            {"source": 0, "categoryName": "%foundGame%", "categoryId": None,
                                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35031,
                                             "parentId": else_kk2_id, "enabled": True, "index": 0},
                                            {
                                                "input": "%category.success%", "operation": 0, "value": "False",
                                                "autoType": True,
                                                "subActions": [
                                                    {
                                                        "random": False,
                                                        "subActions": [
                                                            {"text": not_found_game_msg, "useBot": True, "fallback": True,
                                                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
                                                             "parentId": str(uuid.uuid4()), "enabled": True, "index": 0},
                                                        ],
                                                        "id": str(uuid.uuid4()), "weight": 0.0, "type": 99901,
                                                        "parentId": str(uuid.uuid4()), "enabled": True, "index": 0,
                                                    },
                                                ],
                                                "id": str(uuid.uuid4()), "weight": 0.0, "type": 120,
                                                "parentId": else_kk2_id, "enabled": True, "index": 1,
                                            },
                                        ],
                                        "id": else_kk2_id, "weight": 0.0, "type": 99902,
                                        "parentId": if_kk2_id, "enabled": True, "index": 1,
                                    },
                                ],
                                "id": if_kk2_id, "weight": 0.0, "type": 120,
                                "parentId": then_kk_id, "enabled": True, "index": 1,
                            },
                        ],
                        "id": then_kk_id, "weight": 0.0, "type": 99901,
                        "parentId": if_kk_id, "enabled": True, "index": 0,
                    },
                ],
                "id": if_kk_id, "weight": 0.0, "type": 120,
                "parentId": kick_id, "enabled": True, "index": 1,
            },
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    youtube_id = str(uuid.uuid4())
    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True, "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
             "parentId": youtube_id, "enabled": True, "index": 0},
        ],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_id = str(uuid.uuid4())
    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_accountage_action(name, group, queue_id, not_available_msg, message=None):
    """
    !accountage — Twitch only.
    Structure: C# resolves user (→ userFound) → if True → Fetch URL (→ accountAge) → C# TwitchAnnounce.
    """
    if message is None:
        message = "/me @%inputUser% was born %accountAge% ago"

    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())
    twitch_id  = str(uuid.uuid4())
    if_id      = str(uuid.uuid4())
    then_id    = str(uuid.uuid4())

    resolve_code  = base64.b64encode(ACCOUNTAGE_CSHARP_RESOLVE.encode("utf-8")).decode("utf-8")

    def _cs(name_, code, save_to, parent_id, index):
        return {
            "name": name_, "description": "",
            "references": [
                "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
                "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
            ],
            "byteCode": code,
            "precompile": False, "delayStart": False,
            "saveResultToVariable": bool(save_to), "saveToVariable": save_to or "",
            "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
            "parentId": parent_id, "enabled": True, "index": index,
        }

    def _fetch_url(parent_id, index):
        return {
            "url": "https://decapi.me/twitch/accountage/%inputUserName%?precision=4",
            "variableName": "accountAge",
            "headers": {}, "parseAsJson": False, "autoType": True,
            "id": str(uuid.uuid4()), "weight": 0.0, "type": 1007,
            "parentId": parent_id, "enabled": True, "index": index,
        }

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [
            _cs("Check if user exists", resolve_code, "userFound", twitch_id, 0),
            {
                "input": "%userFound%", "operation": 0, "value": "True", "autoType": True,
                "subActions": [
                    {
                        "random": False,
                        "subActions": [
                            _fetch_url(then_id, 0),
                            {"text": message, "color": 4, "useBot": True, "fallback": True,
                             "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
                             "parentId": then_id, "enabled": True, "index": 1},
                        ],
                        "id": then_id, "weight": 0.0, "type": 99901,
                        "parentId": if_id, "enabled": True, "index": 0,
                    },
                ],
                "id": if_id, "weight": 0.0, "type": 120,
                "parentId": twitch_id, "enabled": True, "index": 1,
            },
        ],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    kick_id = str(uuid.uuid4())
    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
             "parentId": kick_id, "enabled": True, "index": 0},
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    youtube_id = str(uuid.uuid4())
    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True, "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
             "parentId": youtube_id, "enabled": True, "index": 0},
        ],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_id = str(uuid.uuid4())
    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_followage_action(name, group, queue_id, not_available_msg):
    """
    !followage — Twitch only: C# get user info, type 51 get follow info, C# send message.
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())

    twitch_id = str(uuid.uuid4())

    bc1 = base64.b64encode(FOLLOWAGE_CSHARP_1.encode("utf-8")).decode("utf-8")
    bc2 = base64.b64encode(FOLLOWAGE_CSHARP_2.encode("utf-8")).decode("utf-8")
    default_refs = [
        "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
        "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
    ]

    def _cs_block(byte_code, parent_id, index):
        return {
            "name": "", "description": "",
            "references": default_refs,
            "byteCode": byte_code,
            "precompile": False, "delayStart": False,
            "saveResultToVariable": False, "saveToVariable": "",
            "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
            "parentId": parent_id, "enabled": True, "index": index,
        }

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [
            _cs_block(bc1, twitch_id, 0),
            {"userLogin": "%inputUserName%",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 51,
             "parentId": twitch_id, "enabled": True, "index": 1},
            _cs_block(bc2, twitch_id, 2),
        ],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    kick_id = str(uuid.uuid4())
    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
             "parentId": kick_id, "enabled": True, "index": 0},
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    youtube_id = str(uuid.uuid4())
    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True, "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
             "parentId": youtube_id, "enabled": True, "index": 0},
        ],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_id = str(uuid.uuid4())
    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_uptime_action(name, group, queue_id, not_available_msg):
    """
    !uptime — Twitch only: type 1007 get %uptime%, then C# inline TwitchAnnounce.
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())

    twitch_id = str(uuid.uuid4())
    bc = base64.b64encode(UPTIME_CSHARP.encode("utf-8")).decode("utf-8")

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [
            make_get_variable(parent_id=twitch_id, index=0),
            {
                "name": "", "description": "",
                "references": [
                    "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
                    "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
                ],
                "byteCode": bc,
                "precompile": False, "delayStart": False,
                "saveResultToVariable": False, "saveToVariable": "",
                "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
                "parentId": twitch_id, "enabled": True, "index": 1,
            },
        ],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    kick_id = str(uuid.uuid4())
    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
             "parentId": kick_id, "enabled": True, "index": 0},
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    youtube_id = str(uuid.uuid4())
    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True, "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
             "parentId": youtube_id, "enabled": True, "index": 0},
        ],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_id = str(uuid.uuid4())
    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_time_action(name, group, queue_id, twitch_msg, kick_msg, youtube_msg, twitch_announce=False):
    """
    !time — pure native chat message, no C#. Platform switch sends platform-specific message.
    Set twitch_announce=True to send the Twitch message as a purple announcement.
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())

    twitch_id  = str(uuid.uuid4())
    kick_id    = str(uuid.uuid4())
    youtube_id = str(uuid.uuid4())
    default_id = str(uuid.uuid4())

    if twitch_announce:
        announce_bc = base64.b64encode(_make_announce_cs(twitch_msg).encode("utf-8")).decode("utf-8")
        twitch_subactions = [{
            "name": "", "description": "",
            "references": ["C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll"],
            "byteCode": announce_bc, "precompile": False, "delayStart": False,
            "saveResultToVariable": False, "saveToVariable": "",
            "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
            "parentId": twitch_id, "enabled": True, "index": 0,
        }]
    else:
        twitch_subactions = [{"text": twitch_msg, "color": 4, "useBot": True, "fallback": True,
                              "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
                              "parentId": twitch_id, "enabled": True, "index": 0}]

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": twitch_subactions,
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"text": kick_msg, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
             "parentId": kick_id, "enabled": True, "index": 0},
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"text": youtube_msg, "useBot": True, "fallback": True, "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
             "parentId": youtube_id, "enabled": True, "index": 0},
        ],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_translate_action(name, group, queue_id):
    """
    !translate — set fromLanguage/toLanguage variables, then C# Google Translate,
    then platform switch sends %translationText%.
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())

    translate_refs = [
        "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
        ".\\Newtonsoft.Json.dll",
        "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
        "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.Web.dll",
    ]
    bc = base64.b64encode(TRANSLATE_CSHARP.encode("utf-8")).decode("utf-8")

    csharp_sub = {
        "name": "", "description": "",
        "references": translate_refs,
        "byteCode": bc,
        "precompile": False, "delayStart": False,
        "saveResultToVariable": False, "saveToVariable": "",
        "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
        "parentId": None, "enabled": True, "index": 3,
    }

    send_switch = make_send_switch("%translationText%", parent_id=None, index=4)

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            make_set_variable("fromLanguage", "auto", parent_id=None, index=1),
            make_set_variable("toLanguage", "en", parent_id=None, index=2),
            csharp_sub,
            send_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_sacrifice_action(name, group, queue_id, twitch_msg, kick_msg, youtube_msg):
    """
    !sacrifice — timeout user then announce.
    Twitch: type 15001 + type 20 (30s) + type 23 announce
    Kick: type 35042 + type 35001
    YouTube: type 4009 + type 4001
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())

    twitch_id  = str(uuid.uuid4())
    kick_id    = str(uuid.uuid4())
    youtube_id = str(uuid.uuid4())
    default_id = str(uuid.uuid4())

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [
            {"userLogin": "%user%",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 15001,
             "parentId": twitch_id, "enabled": True, "index": 0},
            {"userLogin": "%user%", "duration": "30", "reason": "Sacrificed themself",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 20,
             "parentId": twitch_id, "enabled": True, "index": 1},
            {"text": twitch_msg, "color": 4, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
             "parentId": twitch_id, "enabled": True, "index": 2},
        ],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"userLogin": "%user%", "duration": "1",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35042,
             "parentId": kick_id, "enabled": True, "index": 0},
            {"text": kick_msg, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
             "parentId": kick_id, "enabled": True, "index": 1},
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"userId": "%user%", "duration": "30",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4009,
             "parentId": youtube_id, "enabled": True, "index": 0},
            {"text": youtube_msg, "useBot": True, "fallback": True, "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
             "parentId": youtube_id, "enabled": True, "index": 1},
        ],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def _rr_group(group_name, weight, sub_actions, parent_id, index):
    return {
        "name": group_name, "random": False, "subActions": sub_actions,
        "id": str(uuid.uuid4()), "weight": weight, "type": 99900,
        "parentId": parent_id, "enabled": True, "index": index,
    }


def build_russianroulette_action(name, group, queue_id, dies_msg, shot_msg, lives_msg):
    """
    !russianroulette — outer type 99900 (random) picks 1/6 dies or 5/6 lives.
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())

    twitch_id  = str(uuid.uuid4())
    kick_id    = str(uuid.uuid4())
    youtube_id = str(uuid.uuid4())
    default_id = str(uuid.uuid4())

    # --- Twitch ---
    tw_outer_id = str(uuid.uuid4())

    def tw_dies_subs(parent_id):
        return [
            {"userLogin": "%user%",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 15001,
             "parentId": parent_id, "enabled": True, "index": 0},
            {"userLogin": "%user%", "duration": "3600", "reason": "Died by Russian Roulette",
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 20,
             "parentId": parent_id, "enabled": True, "index": 1},
            {"text": dies_msg, "color": 4, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
             "parentId": parent_id, "enabled": True, "index": 2},
        ]

    def tw_lives_subs(parent_id):
        return [
            {"text": lives_msg, "color": 4, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
             "parentId": parent_id, "enabled": True, "index": 0},
        ]

    tw_dies_id  = str(uuid.uuid4())
    tw_lives_id = str(uuid.uuid4())

    tw_outer = {
        "name": "Russian Roulette", "random": True,
        "subActions": [
            {
                "name": "1/6 (Dies)", "random": False,
                "subActions": tw_dies_subs(tw_dies_id),
                "id": tw_dies_id, "weight": 1.0, "type": 99900,
                "parentId": tw_outer_id, "enabled": True, "index": 0,
            },
            {
                "name": "5/6 (Lives)", "random": False,
                "subActions": tw_lives_subs(tw_lives_id),
                "id": tw_lives_id, "weight": 5.0, "type": 99900,
                "parentId": tw_outer_id, "enabled": True, "index": 1,
            },
        ],
        "id": tw_outer_id, "weight": 0.0, "type": 99900,
        "parentId": twitch_id, "enabled": True, "index": 0,
    }

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [tw_outer],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    # --- Kick ---
    kk_outer_id  = str(uuid.uuid4())
    kk_dies_id   = str(uuid.uuid4())
    kk_lives_id  = str(uuid.uuid4())

    kk_outer = {
        "name": "Russian Roulette", "random": True,
        "subActions": [
            {
                "name": "1/6 (Dies)", "random": False,
                "subActions": [
                    {"userLogin": "%user%", "duration": "1",
                     "id": str(uuid.uuid4()), "weight": 0.0, "type": 35042,
                     "parentId": kk_dies_id, "enabled": True, "index": 0},
                    {"text": shot_msg, "useBot": True, "fallback": True,
                     "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
                     "parentId": kk_dies_id, "enabled": True, "index": 1},
                ],
                "id": kk_dies_id, "weight": 1.0, "type": 99900,
                "parentId": kk_outer_id, "enabled": True, "index": 0,
            },
            {
                "name": "5/6 (Lives)", "random": False,
                "subActions": [
                    {"text": lives_msg, "useBot": True, "fallback": True,
                     "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
                     "parentId": kk_lives_id, "enabled": True, "index": 0},
                ],
                "id": kk_lives_id, "weight": 5.0, "type": 99900,
                "parentId": kk_outer_id, "enabled": True, "index": 1,
            },
        ],
        "id": kk_outer_id, "weight": 0.0, "type": 99900,
        "parentId": kick_id, "enabled": True, "index": 0,
    }

    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [kk_outer],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    # --- YouTube ---
    yt_outer_id  = str(uuid.uuid4())
    yt_dies_id   = str(uuid.uuid4())
    yt_lives_id  = str(uuid.uuid4())

    yt_outer = {
        "name": "Russian Roulette", "random": True,
        "subActions": [
            {
                "name": "1/6 (Dies)", "random": False,
                "subActions": [
                    {"userId": "%user%", "duration": "30",
                     "id": str(uuid.uuid4()), "weight": 0.0, "type": 4009,
                     "parentId": yt_dies_id, "enabled": True, "index": 0},
                    {"text": shot_msg, "useBot": True, "fallback": True, "broadcast": 0,
                     "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
                     "parentId": yt_dies_id, "enabled": True, "index": 1},
                ],
                "id": yt_dies_id, "weight": 1.0, "type": 99900,
                "parentId": yt_outer_id, "enabled": True, "index": 0,
            },
            {
                "name": "5/6 (Lives)", "random": False,
                "subActions": [
                    {"text": lives_msg, "useBot": True, "fallback": True, "broadcast": 0,
                     "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
                     "parentId": yt_lives_id, "enabled": True, "index": 0},
                ],
                "id": yt_lives_id, "weight": 5.0, "type": 99900,
                "parentId": yt_outer_id, "enabled": True, "index": 1,
            },
        ],
        "id": yt_outer_id, "weight": 0.0, "type": 99900,
        "parentId": youtube_id, "enabled": True, "index": 0,
    }

    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [yt_outer],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_scene_action(name, group, queue_id):
    """
    !scene — OBS set scene. No platform switch, no C#.
    sub_actions: [type 1009 "Code", type 34 set scene]
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            {"id": str(uuid.uuid4()), "weight": 0.0, "type": 34,
             "parentId": None, "enabled": True, "index": 1},
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_points_code(message_tmpl, not_available_msg, not_found_msg):
    """
    Generates inline C# for !points.

    - Reads se_jwt and se_channel from Streamer.bot persisted global variables.
    - Gets target from rawInput or falls back to the calling user.
    - Calls GET /points/{channel}/{target} on the StreamElements API.
    - Sets %pointsResult% argument for the platform switch to send.
    - Falls back to notFound message on 404/errors; notAvailable if SE not configured.
    """
    msg_lit    = csharp_literal(message_tmpl)
    na_lit     = csharp_literal(not_available_msg)
    nf_lit     = csharp_literal(not_found_msg)
    ph_target  = csharp_literal("{target}")
    ph_points  = csharp_literal("{points}")
    ph_rank    = csharp_literal("{rank}")
    pts_key    = csharp_literal('"points":')
    rank_key   = csharp_literal('"rank":')

    return f"""\
using System;
using System.Net;

public class CPHInline
{{
    public bool Execute()
    {{
        string seJwt     = CPH.GetGlobalVar<string>("se_jwt", true);
        string seChannel = CPH.GetGlobalVar<string>("se_channel", true);

        string target = "";
        if (args.ContainsKey("rawInput"))
            target = args["rawInput"].ToString().Trim();
        if (string.IsNullOrEmpty(target))
            target = args.ContainsKey("user") ? args["user"].ToString() : "";

        if (string.IsNullOrEmpty(seJwt) || string.IsNullOrEmpty(seChannel))
        {{
            CPH.SetArgument("pointsResult", {na_lit});
            return true;
        }}

        try
        {{
            string url = "https://api.streamelements.com/kappa/v2/points/" + seChannel + "/" + target;
            using (var client = new WebClient())
            {{
                client.Headers[HttpRequestHeader.Authorization] = "Bearer " + seJwt;
                client.Headers[HttpRequestHeader.Accept] = "application/json";
                string json = client.DownloadString(url);
                long points = ExtractLong(json, {pts_key});
                long rank   = ExtractLong(json, {rank_key});
                string msg = {msg_lit}
                    .Replace({ph_target}, target)
                    .Replace({ph_points}, points.ToString())
                    .Replace({ph_rank}, rank.ToString());
                CPH.SetArgument("pointsResult", msg);
            }}
        }}
        catch
        {{
            string notFound = {nf_lit}.Replace({ph_target}, target);
            CPH.SetArgument("pointsResult", notFound);
        }}
        return true;
    }}

    private static long ExtractLong(string json, string keyWithColon)
    {{
        int idx = json.IndexOf(keyWithColon);
        if (idx < 0) return 0;
        int start = idx + keyWithColon.Length;
        while (start < json.Length && (json[start] == ' ' || json[start] == '\\t')) start++;
        int end = start;
        while (end < json.Length && (char.IsDigit(json[end]) || json[end] == '-')) end++;
        if (end == start) return 0;
        long val;
        return long.TryParse(json.Substring(start, end - start), out val) ? val : 0;
    }}
}}"""


def build_points_action(name, group, queue_id, code, not_available_msg):
    """
    Builds the !points action.

    Structure (Twitch branch): C# runs first → sends %pointsResult% via type-23 announce.
    Kick / YouTube receive the not_available_msg directly.
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())
    twitch_id  = str(uuid.uuid4())
    kick_id    = str(uuid.uuid4())
    youtube_id = str(uuid.uuid4())
    default_id = str(uuid.uuid4())

    code_bc = base64.b64encode(code.encode("utf-8")).decode("utf-8")

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [
            {
                "name": "", "description": "",
                "references": [
                    "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
                    "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
                ],
                "byteCode": code_bc,
                "precompile": False, "delayStart": False,
                "saveResultToVariable": False, "saveToVariable": "",
                "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
                "parentId": twitch_id, "enabled": True, "index": 0,
            },
            {"text": "%pointsResult%", "color": 4, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
             "parentId": twitch_id, "enabled": True, "index": 1},
        ],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
             "parentId": kick_id, "enabled": True, "index": 0},
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True, "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
             "parentId": youtube_id, "enabled": True, "index": 0},
        ],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_top_code(limit, header_tmpl, entry_tmpl, not_available_msg):
    """
    Generates inline C# for !top / !top10.

    - Reads se_jwt and se_channel from Streamer.bot persisted global variables.
    - Calls GET /points/{channel}/top?limit={limit} on the StreamElements API.
    - Formats entries as "{header} #1 user — pts | #2 user — pts | …".
    - Sets %topResult% argument for the platform switch to send.
    """
    na_lit       = csharp_literal(not_available_msg)
    header_lit   = csharp_literal(header_tmpl)
    entry_lit    = csharp_literal(entry_tmpl)
    ph_rank      = csharp_literal("{rank}")
    ph_username  = csharp_literal("{username}")
    ph_points    = csharp_literal("{points}")
    uname_key    = csharp_literal('"username":')
    pts_key      = csharp_literal('"points":')

    return f"""\
using System;
using System.Net;
using System.Collections.Generic;

public class CPHInline
{{
    public bool Execute()
    {{
        string seJwt     = CPH.GetGlobalVar<string>("se_jwt", true);
        string seChannel = CPH.GetGlobalVar<string>("se_channel", true);

        if (string.IsNullOrEmpty(seJwt) || string.IsNullOrEmpty(seChannel))
        {{
            CPH.SetArgument("topResult", {na_lit});
            return true;
        }}

        try
        {{
            string url = "https://api.streamelements.com/kappa/v2/points/" + seChannel + "/top?limit={limit}";
            using (var client = new WebClient())
            {{
                client.Headers[HttpRequestHeader.Authorization] = "Bearer " + seJwt;
                client.Headers[HttpRequestHeader.Accept] = "application/json";
                string json = client.DownloadString(url);

                var parts = new List<string>();
                int pos = 0;
                while (pos < json.Length)
                {{
                    int uIdx = json.IndexOf({uname_key}, pos);
                    if (uIdx < 0) break;
                    int q1 = json.IndexOf('"', uIdx + {len('"username":')} );
                    if (q1 < 0) break;
                    int q2 = json.IndexOf('"', q1 + 1);
                    if (q2 < 0) break;
                    string username = json.Substring(q1 + 1, q2 - q1 - 1);
                    long pts = ExtractLong(json, {pts_key}, q2);
                    long rank = parts.Count + 1;
                    parts.Add({entry_lit}
                        .Replace({ph_rank}, rank.ToString())
                        .Replace({ph_username}, username)
                        .Replace({ph_points}, pts.ToString()));
                    pos = q2 + 1;
                }}

                string result = parts.Count > 0
                    ? {header_lit} + " " + string.Join(" | ", parts)
                    : {na_lit};
                CPH.SetArgument("topResult", result);
            }}
        }}
        catch
        {{
            CPH.SetArgument("topResult", {na_lit});
        }}
        return true;
    }}

    private static long ExtractLong(string json, string keyWithColon, int from)
    {{
        int idx = json.IndexOf(keyWithColon, from);
        if (idx < 0) return 0;
        int start = idx + keyWithColon.Length;
        while (start < json.Length && (json[start] == ' ' || json[start] == '\\t')) start++;
        int end = start;
        while (end < json.Length && char.IsDigit(json[end])) end++;
        if (end == start) return 0;
        long val;
        return long.TryParse(json.Substring(start, end - start), out val) ? val : 0;
    }}
}}"""


def build_top_action(name, group, queue_id, code, not_available_msg):
    """
    Builds the !top / !top10 action.

    Structure (Twitch): C# runs → sends %topResult% via type-23 announce.
    Kick / YouTube receive not_available_msg directly.
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())
    switch_id  = str(uuid.uuid4())
    twitch_id  = str(uuid.uuid4())
    kick_id    = str(uuid.uuid4())
    youtube_id = str(uuid.uuid4())
    default_id = str(uuid.uuid4())

    code_bc = base64.b64encode(code.encode("utf-8")).decode("utf-8")

    twitch_case = {
        "caseSensitive": True, "values": ["twitch"], "random": False,
        "subActions": [
            {
                "name": "", "description": "",
                "references": [
                    "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
                    "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
                ],
                "byteCode": code_bc,
                "precompile": False, "delayStart": False,
                "saveResultToVariable": False, "saveToVariable": "",
                "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
                "parentId": twitch_id, "enabled": True, "index": 0,
            },
            {"text": "%topResult%", "color": 4, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
             "parentId": twitch_id, "enabled": True, "index": 1},
        ],
        "id": twitch_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 0,
    }

    kick_case = {
        "caseSensitive": True, "values": ["kick"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
             "parentId": kick_id, "enabled": True, "index": 0},
        ],
        "id": kick_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 1,
    }

    youtube_case = {
        "caseSensitive": True, "values": ["youtube"], "random": False,
        "subActions": [
            {"text": not_available_msg, "useBot": True, "fallback": True, "broadcast": 0,
             "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
             "parentId": youtube_id, "enabled": True, "index": 0},
        ],
        "id": youtube_id, "weight": 0.0, "type": 99903,
        "parentId": switch_id, "enabled": True, "index": 2,
    }

    default_case = {
        "random": False, "subActions": [],
        "id": default_id, "weight": 0.0, "type": 99904,
        "parentId": switch_id, "enabled": True, "index": 3,
    }

    platform_switch = {
        "input": "%commandSource%", "autoType": False,
        "subActions": [twitch_case, kick_case, youtube_case, default_case],
        "id": switch_id, "weight": 0.0, "type": 127,
        "parentId": None, "enabled": True, "index": 1,
    }

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            platform_switch,
        ],
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_join_code(joined_msg, already_joined_msg, not_open_msg):
    """
    Generates inline C# for !join.

    - Reads raffle_open global var.
    - Reads user from args.
    - Reads raffle_joined (pipe-separated) global var.
    - Adds user if not already present, updates global var.
    - Sets %joinResult% for the platform switch to send.
    """
    joined_lit       = csharp_literal(joined_msg)
    already_lit      = csharp_literal(already_joined_msg)
    not_open_lit     = csharp_literal(not_open_msg)
    ph_user          = csharp_literal("{user}")

    return f"""\
using System;

public class CPHInline
{{
    public bool Execute()
    {{
        bool isOpen = CPH.GetGlobalVar<bool>("raffle_open", true);
        if (!isOpen)
        {{
            CPH.SetArgument("joinResult", {not_open_lit});
            return true;
        }}

        string user = (args.ContainsKey("user") ? args["user"].ToString() : "").TrimStart('@');
        string raw  = CPH.GetGlobalVar<string>("raffle_joined", true) ?? "";
        string[] parts = raw.Length > 0 ? raw.Split('|') : new string[0];

        foreach (string p in parts)
            if (string.Equals(p, user, StringComparison.OrdinalIgnoreCase))
            {{
                CPH.SetArgument("joinResult", {already_lit}.Replace({ph_user}, user));
                return true;
            }}

        string updated = raw.Length > 0 ? raw + "|" + user : user;
        CPH.SetGlobalVar("raffle_joined", updated, true);
        CPH.SetArgument("joinResult", {joined_lit}.Replace({ph_user}, user));
        return true;
    }}
}}"""


def build_open_raffle_code(opened_msg, no_title_msg, already_open_msg):
    """
    Generates inline C# for !openRaffle.

    - Rejects if raffle_open is already true.
    - Reads rawInput for the raffle title.
    - Sets raffle_open=true, raffle_title, raffle_opened_at, clears raffle_joined.
    - Sets %openRaffleResult% for the platform switch to send.
    """
    opened_lit       = csharp_literal(opened_msg)
    no_title_lit     = csharp_literal(no_title_msg)
    already_open_lit = csharp_literal(already_open_msg)
    ph_title         = csharp_literal("{title}")

    return f"""\
using System;

public class CPHInline
{{
    public bool Execute()
    {{
        bool isOpen = CPH.GetGlobalVar<bool>("raffle_open", true);
        if (isOpen)
        {{
            string currentTitle = CPH.GetGlobalVar<string>("raffle_title", true) ?? "";
            CPH.SetArgument("openRaffleResult", {already_open_lit}.Replace({ph_title}, currentTitle));
            return true;
        }}

        string title = args.ContainsKey("rawInput") ? args["rawInput"].ToString().Trim() : "";
        if (title.Length == 0)
        {{
            CPH.SetArgument("openRaffleResult", {no_title_lit});
            return true;
        }}

        CPH.SetGlobalVar("raffle_open",      true,  true);
        CPH.SetGlobalVar("raffle_title",     title, true);
        CPH.SetGlobalVar("raffle_opened_at", DateTime.UtcNow.ToString("o"), true);
        CPH.SetGlobalVar("raffle_joined",    "",    true);

        CPH.SetArgument("openRaffleResult", {opened_lit}.Replace({ph_title}, title));
        return true;
    }}
}}"""


def build_close_raffle_code(closed_msg, not_open_msg):
    """
    Generates inline C# for !closeRaffle.

    - Checks raffle_open global var.
    - Sets raffle_open=false.
    - Sets %closeRaffleResult% for the platform switch to send.
    """
    closed_lit   = csharp_literal(closed_msg)
    not_open_lit = csharp_literal(not_open_msg)

    return f"""\
using System;

public class CPHInline
{{
    public bool Execute()
    {{
        bool isOpen = CPH.GetGlobalVar<bool>("raffle_open", true);
        if (!isOpen)
        {{
            CPH.SetArgument("closeRaffleResult", {not_open_lit});
            return true;
        }}

        CPH.SetGlobalVar("raffle_open", false, true);
        CPH.SetArgument("closeRaffleResult", {closed_lit});
        return true;
    }}
}}"""


def build_draw_raffle_code(
    starting_msg,
    top5_msg, top10_msg, bonus_msg,
    no_joined_msg, top5_no_leaderboard_msg, top10_no_winner_msg, top10_not_enough_msg, not_open_msg,
    history_file_path="raffle_history.json",
):
    """
    Generates inline C# for !drawRaffle.

    - Checks raffle_open.
    - Closes raffle (sets raffle_open=false).
    - Announces starting draws.
    - Sleeps 10 seconds.
    - Reads raffle_joined list.
    - Reads se_jwt / se_channel and fetches top 50 leaderboard.
    - Draws: Top5 (random from positions 1-5), Ranked (up to 10 joined from leaderboard, pick 1), Extra (random from all joined).
    - Announces each winner individually via TwitchAnnounce.
    - Saves session to raffle_history.json (in Streamer.bot data directory).
    - Returns true; all chat sends are inline (no platform switch output needed).
    """
    starting_lit  = csharp_literal(starting_msg)
    top5_lit          = csharp_literal(top5_msg)
    top10_lit         = csharp_literal(top10_msg)
    bonus_lit         = csharp_literal(bonus_msg)
    no_joined_lit             = csharp_literal(no_joined_msg)
    top5_no_leaderboard_lit   = csharp_literal(top5_no_leaderboard_msg)
    top10_no_winner_lit       = csharp_literal(top10_no_winner_msg)
    top10_not_enough_lit      = csharp_literal(top10_not_enough_msg)
    not_open_lit          = csharp_literal(not_open_msg)
    history_lit   = csharp_literal(history_file_path)
    ph_user       = csharp_literal("{user}")
    pts_key       = csharp_literal('"points":')
    uname_key     = csharp_literal('"username":')

    return f"""\
using System;
using System.Net;
using System.Collections.Generic;
using System.IO;
using System.Threading;

public class CPHInline
{{
    public bool Execute()
    {{
        bool isOpen = CPH.GetGlobalVar<bool>("raffle_open", true);
        if (!isOpen)
        {{
            CPH.TwitchAnnounce({not_open_lit}, false, "purple");
            return true;
        }}

        string title    = CPH.GetGlobalVar<string>("raffle_title",     true) ?? "";
        string openedAt = CPH.GetGlobalVar<string>("raffle_opened_at", true) ?? DateTime.UtcNow.ToString("o");
        string raw      = CPH.GetGlobalVar<string>("raffle_joined",    true) ?? "";
        CPH.SetGlobalVar("raffle_open", false, true);

        string[] joined = raw.Length > 0 ? Array.ConvertAll(raw.Split('|'), u => u.TrimStart('@')) : new string[0];

        CPH.TwitchAnnounce({starting_lit}, false, "purple");
        Thread.Sleep(10000);

        // Fetch leaderboard
        var leaderboard = new List<string>();  // ordered usernames
        try
        {{
            string seJwt     = CPH.GetGlobalVar<string>("se_jwt",     true) ?? "";
            string seChannel = CPH.GetGlobalVar<string>("se_channel", true) ?? "";
            if (seJwt.Length > 0 && seChannel.Length > 0)
            {{
                string url = "https://api.streamelements.com/kappa/v2/points/" + seChannel + "/top?limit=50";
                using (var client = new WebClient())
                {{
                    client.Headers[HttpRequestHeader.Authorization] = "Bearer " + seJwt;
                    client.Headers[HttpRequestHeader.Accept] = "application/json";
                    string json = client.DownloadString(url);
                    int pos = 0;
                    while (pos < json.Length)
                    {{
                        int uIdx = json.IndexOf({uname_key}, pos);
                        if (uIdx < 0) break;
                        int q1 = json.IndexOf('"', uIdx + {len('"username":')} );
                        if (q1 < 0) break;
                        int q2 = json.IndexOf('"', q1 + 1);
                        if (q2 < 0) break;
                        leaderboard.Add(json.Substring(q1 + 1, q2 - q1 - 1).TrimStart('@'));
                        pos = q2 + 1;
                    }}
                }}
            }}
        }}
        catch {{ }}

        var rng = new Random();
        var joinedSet = new HashSet<string>(joined, StringComparer.OrdinalIgnoreCase);

        // Top 5 draw — does not require !join, always runs when leaderboard is available
        string top5Winner = null;
        if (leaderboard.Count > 0)
        {{
            int pool = Math.Min(5, leaderboard.Count);
            top5Winner = leaderboard[rng.Next(pool)];
        }}
        // Top 5 -- always report outcome
        if (top5Winner != null)
            CPH.TwitchAnnounce({top5_lit}.Replace({ph_user}, top5Winner), false, "purple");
        else
            CPH.TwitchAnnounce({top5_no_leaderboard_lit}, false, "orange");

        // Ranked and Extra draws require !join
        string top10Winner = null;
        string bonusWinner  = null;
        if (joined.Length == 0)
        {{
            CPH.TwitchAnnounce({no_joined_lit}, false, "purple");
        }}
        else
        {{
            // Top 10 draw: walk leaderboard, collect up to 10 joined users, pick 1
            if (leaderboard.Count > 0)
            {{
                var eligible = new List<string>();
                foreach (string u in leaderboard)
                {{
                    if (joinedSet.Contains(u)) eligible.Add(u);
                    if (eligible.Count >= 10) break;
                }}
                if (eligible.Count > 0)
                    top10Winner = eligible[rng.Next(eligible.Count)];
                if (eligible.Count > 0 && eligible.Count < 10)
                    CPH.TwitchAnnounce({top10_not_enough_lit}.Replace("{{count}}", eligible.Count.ToString()), false, "orange");
                if (top10Winner != null)
                    CPH.TwitchAnnounce({top10_lit}.Replace({ph_user}, top10Winner), false, "purple");
                else
                    CPH.TwitchAnnounce({top10_no_winner_lit}, false, "orange");
            }}

            // Extra draw: random from all joined
            bonusWinner  = joined[rng.Next(joined.Length)];
            CPH.TwitchAnnounce({bonus_lit}.Replace({ph_user}, bonusWinner), false, "purple");
        }}

        // Save to history file
        try
        {{
            string historyPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "Streamer.bot",
                {history_lit});
            string top5Json    = top5Winner   != null ? "\\"" + top5Winner   + "\\"" : "null";
            string top10Json  = top10Winner != null ? "\\"" + top10Winner + "\\"" : "null";
            string bonusJson   = bonusWinner  != null ? "\\"" + bonusWinner  + "\\"" : "null";
            string newEntry    = "  {{" +
                "\\"title\\":\\"" + title.Replace("\\\\", "\\\\\\\\").Replace("\\"", "\\\\\\"") + "\\"," +
                "\\"date\\":\\"" + openedAt + "\\"," +
                "\\"joinedCount\\":" + joined.Length + "," +
                "\\"top5Winner\\":" + top5Json + "," +
                "\\"top10Winner\\":" + top10Json + "," +
                "\\"bonusWinner\\":" + bonusJson +
                "}}";
            string existing = File.Exists(historyPath) ? File.ReadAllText(historyPath).Trim() : "[]";
            string updated;
            if (existing == "[]")
                updated = "[\\n" + newEntry + "\\n]";
            else
                updated = existing.Substring(0, existing.Length - 1) + ",\\n" + newEntry + "\\n]";
            File.WriteAllText(historyPath, updated);
        }}
        catch {{ }}

        return true;
    }}
}}"""


def build_show_previous_raffle_code(template_msg, no_history_msg, history_file_path="raffle_history.json"):
    """
    Generates inline C# for !showPreviousRaffle.

    - Reads raffle_history.json from Streamer.bot data directory.
    - Parses the last entry and announces it.
    - Sets %showPreviousRaffleResult% for the platform switch.
    """
    template_lit   = csharp_literal(template_msg)
    no_history_lit = csharp_literal(no_history_msg)
    history_lit    = csharp_literal(history_file_path)
    ph_title       = csharp_literal("{title}")
    ph_date        = csharp_literal("{date}")
    ph_top5        = csharp_literal("{top5}")
    ph_top10       = csharp_literal("{top10}")
    ph_bonus       = csharp_literal("{bonus}")

    return f"""\
using System;
using System.IO;

public class CPHInline
{{
    public bool Execute()
    {{
        string historyPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "Streamer.bot",
            {history_lit});

        if (!File.Exists(historyPath))
        {{
            CPH.SetArgument("showPreviousRaffleResult", {no_history_lit});
            return true;
        }}

        string json = File.ReadAllText(historyPath).Trim();
        // Find the last {{ ... }} object in the array
        int last = json.LastIndexOf("{{");
        if (last < 0)
        {{
            CPH.SetArgument("showPreviousRaffleResult", {no_history_lit});
            return true;
        }}

        string entry = json.Substring(last);
        int end = entry.IndexOf("}}");
        if (end >= 0) entry = entry.Substring(0, end + 1);

        string title  = ExtractString(entry, "title");
        string date   = ExtractString(entry, "date");
        string top5   = ExtractString(entry, "top5Winner");
        string top10  = ExtractString(entry, "top10Winner");
        string bonus  = ExtractString(entry, "bonusWinner");

        // Trim date to yyyy-MM-dd
        if (date.Length >= 10) date = date.Substring(0, 10);
        if (top5  == null) top5  = "-";
        if (top10 == null) top10 = "-";
        if (bonus == null) bonus = "-";

        string msg = {template_lit}
            .Replace({ph_title},  title  ?? "?")
            .Replace({ph_date},   date)
            .Replace({ph_top5},   top5)
            .Replace({ph_top10}, top10)
            .Replace({ph_bonus},  bonus);

        CPH.SetArgument("showPreviousRaffleResult", msg);
        return true;
    }}

    private static string ExtractString(string json, string key)
    {{
        string k = "\\"" + key + "\\":\\"";
        int idx = json.IndexOf(k);
        if (idx < 0)
        {{
            // try null value
            string kn = "\\"" + key + "\\":null";
            return json.IndexOf(kn) >= 0 ? null : null;
        }}
        int start = idx + k.Length;
        int end   = json.IndexOf('"', start);
        if (end < 0) return null;
        return json.Substring(start, end - start);
    }}
}}"""


def build_chat_activity_points_code(points, min_length, bots, bttv_emotes):
    """
    Generates inline C# for the Chat Activity Points event action.

    - Reads args["user"] and args["message"] from the Twitch Chat Message event.
    - Filters: commands (!…), too-short, known bots, emote-only messages.
    - If all filters pass, calls PUT /points/{channel}/{user}/{points} on the SE API.
    - Reads se_jwt and se_channel from Streamer.bot persisted global variables.
    - Silent action — no reply to chat.
    """
    bots_str  = "\n".join(f'        {csharp_literal(b)},' for b in sorted(bots))
    bttv_str  = "\n".join(f'        {csharp_literal(e)},' for e in sorted(bttv_emotes))
    points_url_suffix = str(points)

    return f"""\
using System;
using System.Net;
using System.Collections.Generic;

public class CPHInline
{{
    private static readonly HashSet<string> Bots = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
    {{
{bots_str}
    }};

    private static readonly HashSet<string> BttvEmotes = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
    {{
{bttv_str}
    }};

    public bool Execute()
    {{
        string user    = (args.ContainsKey("user") ? args["user"].ToString() : "").TrimStart('@');
        string message = args.ContainsKey("message") ? args["message"].ToString() : "";
        int emoteCount = 0;
        if (args.ContainsKey("emoteCount") && args["emoteCount"] != null)
            int.TryParse(args["emoteCount"].ToString(), out emoteCount);

        CPH.LogInfo("[chatactivity] user=" + user + " msg=" + message + " emotes=" + emoteCount);

        if (message.StartsWith("!"))              {{ CPH.LogInfo("[chatactivity] skip=command");    return true; }}
        if (message.Trim().Length < {min_length}) {{ CPH.LogInfo("[chatactivity] skip=too_short"); return true; }}
        if (Bots.Contains(user))                  {{ CPH.LogInfo("[chatactivity] skip=bot");        return true; }}
        if (IsEmoteOnly(message, emoteCount))     {{ CPH.LogInfo("[chatactivity] skip=emote_only"); return true; }}

        string seJwt     = CPH.GetGlobalVar<string>("se_jwt", true);
        string seChannel = CPH.GetGlobalVar<string>("se_channel", true);
        if (string.IsNullOrEmpty(seJwt) || string.IsNullOrEmpty(seChannel))
        {{
            CPH.LogInfo("[chatactivity] skip=se_not_configured jwt_empty=" + string.IsNullOrEmpty(seJwt) + " channel_empty=" + string.IsNullOrEmpty(seChannel));
            return true;
        }}

        try
        {{
            string url = "https://api.streamelements.com/kappa/v2/points/"
                + seChannel + "/" + user + "/{points_url_suffix}";
            CPH.LogInfo("[chatactivity] PUT " + url);
            using (var client = new WebClient())
            {{
                client.Headers[HttpRequestHeader.Authorization] = "Bearer " + seJwt;
                byte[] resp = client.UploadData(url, "PUT", new byte[0]);
                CPH.LogInfo("[chatactivity] response=" + System.Text.Encoding.UTF8.GetString(resp));
            }}
        }}
        catch (WebException ex)
        {{
            string errBody = "";
            if (ex.Response != null)
                using (var sr = new System.IO.StreamReader(ex.Response.GetResponseStream()))
                    errBody = sr.ReadToEnd();
            CPH.LogInfo("[chatactivity] error=" + ex.Message + " body=" + errBody);
        }}
        catch (Exception ex)
        {{
            CPH.LogInfo("[chatactivity] error=" + ex.Message);
        }}
        return true;
    }}

    private static bool IsEmoteOnly(string message, int emoteCount)
    {{
        string[] words = message.Split(new char[]{{ ' ' }}, StringSplitOptions.RemoveEmptyEntries);
        if (words.Length == 0) return false;

        if (emoteCount > 0 && emoteCount >= words.Length) return true;

        if (words.Length >= 2)
        {{
            bool allSame = true;
            for (int i = 1; i < words.Length; i++)
                if (!string.Equals(words[0], words[i], StringComparison.OrdinalIgnoreCase))
                {{ allSame = false; break; }}
            if (allSame) return true;
        }}

        foreach (string w in words)
            if (!BttvEmotes.Contains(w)) return false;
        return true;
    }}
}}"""


def build_raffle_action(name, group, queue_id, code, result_var, not_available_msg=None):
    """
    Builds a raffle command action.

    Structure:
      - Label 'Code'
      - C# subaction (sets %{result_var}% in args)
      - Platform switch: Twitch type-23 announce, Kick/YouTube show not_available or skip

    For drawRaffle the C# sends directly to chat via TwitchAnnounce, so result_var
    is unused — pass result_var=None to skip the platform switch.
    """
    action_id  = str(uuid.uuid4())
    command_id = str(uuid.uuid4())

    code_bc = base64.b64encode(code.encode("utf-8")).decode("utf-8")

    sub_actions = [
        {"value": "Code", "color": "", "id": str(uuid.uuid4()),
         "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
        {
            "name": "", "description": "",
            "references": [
                "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
                "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
                "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.Core.dll",
            ],
            "byteCode": code_bc,
            "precompile": False, "delayStart": False,
            "saveResultToVariable": False, "saveToVariable": "",
            "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
            "parentId": None, "enabled": True, "index": 1,
        },
    ]

    if result_var is not None:
        # Platform switch: Twitch sends %result_var%, Kick/YouTube omit or show not_available
        switch_id  = str(uuid.uuid4())
        twitch_id  = str(uuid.uuid4())
        kick_id    = str(uuid.uuid4())
        youtube_id = str(uuid.uuid4())
        default_id = str(uuid.uuid4())
        na_text    = not_available_msg or ""

        twitch_case = {
            "caseSensitive": True, "values": ["twitch"], "random": False,
            "subActions": [
                {"text": f"%{result_var}%", "color": 4, "useBot": True, "fallback": True,
                 "id": str(uuid.uuid4()), "weight": 0.0, "type": 23,
                 "parentId": twitch_id, "enabled": True, "index": 0},
            ],
            "id": twitch_id, "weight": 0.0, "type": 99903,
            "parentId": switch_id, "enabled": True, "index": 0,
        }
        kick_subactions = (
            [{"text": na_text, "useBot": True, "fallback": True,
              "id": str(uuid.uuid4()), "weight": 0.0, "type": 35001,
              "parentId": kick_id, "enabled": True, "index": 0}]
            if na_text else []
        )
        kick_case = {
            "caseSensitive": True, "values": ["kick"], "random": False,
            "subActions": kick_subactions,
            "id": kick_id, "weight": 0.0, "type": 99903,
            "parentId": switch_id, "enabled": True, "index": 1,
        }
        youtube_subactions = (
            [{"text": na_text, "useBot": True, "fallback": True, "broadcast": 0,
              "id": str(uuid.uuid4()), "weight": 0.0, "type": 4001,
              "parentId": youtube_id, "enabled": True, "index": 0}]
            if na_text else []
        )
        youtube_case = {
            "caseSensitive": True, "values": ["youtube"], "random": False,
            "subActions": youtube_subactions,
            "id": youtube_id, "weight": 0.0, "type": 99903,
            "parentId": switch_id, "enabled": True, "index": 2,
        }
        default_case = {
            "random": False, "subActions": [],
            "id": default_id, "weight": 0.0, "type": 99904,
            "parentId": switch_id, "enabled": True, "index": 3,
        }
        sub_actions.append({
            "input": "%commandSource%", "autoType": False,
            "subActions": [twitch_case, kick_case, youtube_case, default_case],
            "id": switch_id, "weight": 0.0, "type": 127,
            "parentId": None, "enabled": True, "index": 2,
        })

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": False, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": False,
        "triggers": [
            {"commandId": command_id, "id": str(uuid.uuid4()),
             "type": 401, "enabled": True, "exclusions": []}
        ],
        "subActions": sub_actions,
        "collapsedGroups": [],
    }

    return action_id, command_id, action


def build_chat_activity_action(name, group, queue_id, code):
    """
    Builds the Chat Activity Points event action.

    No command trigger — user must add the 'Twitch Chat Message' event trigger manually
    in Streamer.bot and set User Cooldown = 30s on that trigger.
    excludeFromHistory = True to avoid flooding the action history log.
    concurrent = True to handle simultaneous chat messages correctly.
    """
    action_id = str(uuid.uuid4())

    code_bc = base64.b64encode(code.encode("utf-8")).decode("utf-8")

    action = {
        "id": action_id, "queue": queue_id, "enabled": True,
        "excludeFromHistory": True, "excludeFromPending": False,
        "name": name, "group": group,
        "alwaysRun": False, "randomAction": False, "concurrent": True,
        "triggers": [],
        "subActions": [
            {"value": "Code", "color": "", "id": str(uuid.uuid4()),
             "weight": 0.0, "type": 1009, "parentId": None, "enabled": True, "index": 0},
            {
                "name": "", "description": "",
                "references": [
                    "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscorlib.dll",
                    "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.dll",
                
        
                      "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.Core.dll",
                ],
                "byteCode": code_bc,
                "precompile": False, "delayStart": False,
                "saveResultToVariable": False, "saveToVariable": "",
                "id": str(uuid.uuid4()), "weight": 0.0, "type": 99999,
                "parentId": None, "enabled": True, "index": 1,
            },
        ],
        "collapsedGroups": [],
    }

    return action_id, action


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

    language = LANGUAGE_NAMES.get(locale, locale)
    queues_config, commands_config = load_config()

    out_dir = os.path.join(ROOT, "generated", "streamerbot")
    os.makedirs(out_dir, exist_ok=True)

    # ── 8ball ──────────────────────────────────────────────────────────────────
    cmd = commands_config["8ball"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_eightball_code(responses, language)
    action_id, command_id, action = make_action(
        cmd["trigger"], cmd["group"], code, queue_id,
        chat_text="@%user% %randomResponse%"
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[8ball] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")

    _write_export(out_dir, "8ball", queue_id, queue_def, action, command, commands_config)

    # ── flipcoin ───────────────────────────────────────────────────────────────
    flip_data     = locale_data["commands"]["flipcoin"]
    flip_heads    = flip_data["heads"]
    flip_tails    = flip_data["tails"]
    flip_win      = flip_data["win"]
    flip_loss     = flip_data["loss"]
    flip_no_choice = flip_data["noChoice"]
    print(f"[info] loaded flipcoin messages (heads/tails/win/loss/noChoice)")

    cmd = commands_config["flipcoin"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_flipcoin_code(flip_heads, flip_tails, flip_win, flip_loss, flip_no_choice)
    action_id, command_id, action = make_action(
        cmd["trigger"], cmd["group"], code, queue_id,
        chat_text="%flipResult%"
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[flipcoin] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")

    _write_export(out_dir, "flipcoin", queue_id, queue_def, action, command, commands_config)

    # ── joke ───────────────────────────────────────────────────────────────────
    joke_data = locale_data["commands"]["joke"]
    joke_fallbacks = joke_data["responses"]
    empty_prompt = joke_data["emptyPrompt"]
    topic_prompt = joke_data["topicPrompt"]
    print(f"[info] loaded {len(joke_fallbacks)} joke fallback responses")

    cmd = commands_config["joke"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_joke_code(joke_fallbacks, language, empty_prompt, topic_prompt)
    action_id, command_id, action = make_action(
        cmd["trigger"], cmd["group"], code, queue_id,
        chat_text="@%user% %jokeResult%"
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[joke] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")

    _write_export(out_dir, "joke", queue_id, queue_def, action, command, commands_config)

    # ── fortune ────────────────────────────────────────────────────────────────
    fortune_responses = locale_data["commands"]["fortune"]["responses"]
    print(f"[info] loaded {len(fortune_responses)} fortune responses")

    cmd = commands_config["fortune"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_fortune_code(fortune_responses)
    action_id, command_id, action = make_action(
        cmd["trigger"], cmd["group"], code, queue_id,
        chat_text="🔮 %fortuneResult%"
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[fortune] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")

    _write_export(out_dir, "fortune", queue_id, queue_def, action, command, commands_config)

    # ── lurk ───────────────────────────────────────────────────────────────────
    lurk_messages = locale_data["commands"]["lurk"]["responses"]
    print(f"[info] loaded {len(lurk_messages)} lurk messages")

    cmd = commands_config["lurk"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_lurk_code(lurk_messages)
    action_id, command_id, action = make_action(
        cmd["trigger"], cmd["group"], code, queue_id,
        chat_text="%lurkResult%"
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[lurk] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")

    _write_export(out_dir, "lurk", queue_id, queue_def, action, command, commands_config)

    # ── clip ───────────────────────────────────────────────────────────────────
    clip_data = locale_data["commands"]["clip"]
    clip_success = clip_data["success"]
    clip_failure = clip_data["failure"]

    cmd = commands_config["clip"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    clip_creating      = clip_data["creating"]
    clip_not_available = clip_data["notAvailable"]
    action_id, command_id, action = make_clip_action_native(
        cmd["trigger"], cmd["group"], queue_id,
        clip_success, clip_failure, clip_creating, clip_not_available
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[clip] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")

    _write_export(out_dir, "clip", queue_id, queue_def, action, command, commands_config)

    # ── shoutout ───────────────────────────────────────────────────────────────
    so_data = locale_data["commands"]["shoutout"]
    cmd = commands_config["shoutout"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    action_id, command_id, action = build_shoutout_action(
        cmd["trigger"], cmd["group"], queue_id,
        so_data["unknown"], so_data["unknownKick"],
        so_data["twitch"], so_data["kick"], so_data["notAvailable"],
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[shoutout] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "shoutout", queue_id, queue_def, action, command, commands_config)

    # ── settitle ───────────────────────────────────────────────────────────────
    cmd = commands_config["settitle"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    action_id, command_id, action = build_settitle_action(cmd["trigger"], cmd["group"], queue_id)
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[settitle] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "settitle", queue_id, queue_def, action, command, commands_config)

    # ── setgame ────────────────────────────────────────────────────────────────
    sg_data = locale_data["commands"]["setgame"]
    cmd = commands_config["setgame"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    action_id, command_id, action = build_setgame_action(
        cmd["trigger"], cmd["group"], queue_id,
        sg_data["notFound"], sg_data["notFoundGame"], sg_data["notAvailable"],
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[setgame] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "setgame", queue_id, queue_def, action, command, commands_config)

    # ── accountage ─────────────────────────────────────────────────────────────
    aa_data = locale_data["commands"]["accountage"]
    cmd = commands_config["accountage"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    action_id, command_id, action = build_accountage_action(
        cmd["trigger"], cmd["group"], queue_id, aa_data["notAvailable"], aa_data["message"],
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[accountage] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "accountage", queue_id, queue_def, action, command, commands_config)

    # ── followage ──────────────────────────────────────────────────────────────
    cmd = commands_config["followage"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]
    # followage not-available message reuses accountage's (or we use a generic fallback)
    followage_na = locale_data["commands"]["accountage"]["notAvailable"].replace("!accountage", "!followage")

    action_id, command_id, action = build_followage_action(
        cmd["trigger"], cmd["group"], queue_id, followage_na,
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[followage] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "followage", queue_id, queue_def, action, command, commands_config)

    # ── uptime ─────────────────────────────────────────────────────────────────
    cmd = commands_config["uptime"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]
    uptime_na = "@%user% !uptime is not available on this platform D:"

    action_id, command_id, action = build_uptime_action(
        cmd["trigger"], cmd["group"], queue_id, uptime_na,
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[uptime] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "uptime", queue_id, queue_def, action, command, commands_config)

    # ── time ───────────────────────────────────────────────────────────────────
    time_data = locale_data["commands"]["time"]
    cmd = commands_config["time"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    action_id, command_id, action = build_time_action(
        cmd["trigger"], cmd["group"], queue_id,
        time_data["twitch"], time_data["kick"], time_data["youtube"],
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[time] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "time", queue_id, queue_def, action, command, commands_config)

    # ── info commands (pc / gear / peripherals) ─────────────────────────────────
    for info_key in ("pc", "gear", "peripherals"):
        info_msg = locale_data["commands"][info_key]["message"]
        cmd = commands_config[info_key]
        queue_key = cmd["queue"]
        if queue_key not in queues_config:
            raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
        queue_def = queues_config[queue_key]
        queue_id = queue_def["id"]

        action_id, command_id, action = build_time_action(
            cmd["trigger"], cmd["group"], queue_id,
            twitch_msg=info_msg, kick_msg=info_msg, youtube_msg=info_msg
        )
        command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
        print(f"[{info_key}] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
        _write_export(out_dir, info_key, queue_id, queue_def, action, command, commands_config)

    # ── translate ──────────────────────────────────────────────────────────────
    cmd = commands_config["translate"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    action_id, command_id, action = build_translate_action(cmd["trigger"], cmd["group"], queue_id)
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[translate] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "translate", queue_id, queue_def, action, command, commands_config)

    # ── sacrifice ──────────────────────────────────────────────────────────────
    sac_data = locale_data["commands"]["sacrifice"]
    cmd = commands_config["sacrifice"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    action_id, command_id, action = build_sacrifice_action(
        cmd["trigger"], cmd["group"], queue_id,
        sac_data["twitch"], sac_data["kick"], sac_data["youtube"],
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[sacrifice] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "sacrifice", queue_id, queue_def, action, command, commands_config)

    # ── russianroulette ────────────────────────────────────────────────────────
    rr_data = locale_data["commands"]["russianroulette"]
    cmd = commands_config["russianroulette"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    action_id, command_id, action = build_russianroulette_action(
        cmd["trigger"], cmd["group"], queue_id,
        rr_data["dies"], rr_data["shot"], rr_data["lives"],
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[russianroulette] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "russianroulette", queue_id, queue_def, action, command, commands_config)

    # ── commands ───────────────────────────────────────────────────────────────
    all_triggers = " ".join(sorted(commands_config[k]["trigger"] for k in commands_config if "trigger" in commands_config[k]))
    commands_fmt = locale_data["commands"]["commands"]["message"].replace("{commands}", all_triggers)
    cmd = commands_config["commands"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    action_id, command_id, action = build_time_action(
        cmd["trigger"], cmd["group"], queue_id,
        twitch_msg=commands_fmt, kick_msg=commands_fmt, youtube_msg=commands_fmt
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[commands] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "commands", queue_id, queue_def, action, command, commands_config)

    # ── scene ──────────────────────────────────────────────────────────────────
    cmd = commands_config["scene"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    action_id, command_id, action = build_scene_action(cmd["trigger"], cmd["group"], queue_id)
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[scene] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "scene", queue_id, queue_def, action, command, commands_config)

    # ── oracle ─────────────────────────────────────────────────────────────────
    oracle_data = locale_data["commands"]["oracle"]
    cmd = commands_config["oracle"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_oracle_code(
        oracle_data["styles"],
        oracle_data["fallback"],
        oracle_data["noInput"],
        oracle_data["persona"],
    )
    action_id, command_id, action = build_oracle_action(
        cmd["trigger"], cmd["group"], code, queue_id
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[oracle] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "oracle", queue_id, queue_def, action, command, commands_config)

    # ── horoscope ──────────────────────────────────────────────────────────────
    horoscope_data = locale_data["commands"]["horoscope"]
    cmd = commands_config["horoscope"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_oracle_code(
        horoscope_data["styles"],
        horoscope_data["fallback"],
        horoscope_data["noInput"],
        horoscope_data["persona"],
    )
    action_id, command_id, action = build_oracle_action(
        cmd["trigger"], cmd["group"], code, queue_id
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[horoscope] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "horoscope", queue_id, queue_def, action, command, commands_config)

    # ── curse ──────────────────────────────────────────────────────────────────
    curse_data = locale_data["commands"]["curse"]
    cmd = commands_config["curse"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_oracle_code(
        curse_data["styles"],
        curse_data["fallback"],
        curse_data["noInput"],
        curse_data["persona"],
    )
    action_id, command_id, action = build_oracle_action(
        cmd["trigger"], cmd["group"], code, queue_id
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[curse] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "curse", queue_id, queue_def, action, command, commands_config)

    # ── omen ───────────────────────────────────────────────────────────────────
    omen_data = locale_data["commands"]["omen"]
    cmd = commands_config["omen"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_ailicia_useronly_code(
        omen_data["styles"],
        omen_data["fallback"],
        omen_data["persona"],
    )
    action_id, command_id, action = build_oracle_action(
        cmd["trigger"], cmd["group"], code, queue_id
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[omen] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "omen", queue_id, queue_def, action, command, commands_config)

    # ── tarot ──────────────────────────────────────────────────────────────────
    tarot_data = locale_data["commands"]["tarot"]
    cmd = commands_config["tarot"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_ailicia_useronly_code(
        tarot_data["styles"],
        tarot_data["fallback"],
        tarot_data["persona"],
    )
    action_id, command_id, action = build_oracle_action(
        cmd["trigger"], cmd["group"], code, queue_id
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[tarot] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "tarot", queue_id, queue_def, action, command, commands_config)

    # ── judge ──────────────────────────────────────────────────────────────────
    judge_data = locale_data["commands"]["judge"]
    cmd = commands_config["judge"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_ailicia_judge_code(
        judge_data["styles"],
        judge_data["fallback"],
        judge_data["noInput"],
        judge_data["persona"],
    )
    action_id, command_id, action = build_oracle_action(
        cmd["trigger"], cmd["group"], code, queue_id
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[judge] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "judge", queue_id, queue_def, action, command, commands_config)

    # ── hex ────────────────────────────────────────────────────────────────────
    hex_data = locale_data["commands"]["hex"]
    cmd = commands_config["hex"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_ailicia_hex_code(
        hex_data["styles"],
        hex_data["fallback"],
        hex_data["noInput"],
        hex_data["persona"],
    )
    action_id, command_id, action = build_oracle_action(
        cmd["trigger"], cmd["group"], code, queue_id
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[hex] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "hex", queue_id, queue_def, action, command, commands_config)

    # ── points ─────────────────────────────────────────────────────────────────
    pts_data = locale_data["commands"]["points"]
    cmd = commands_config["points"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_points_code(pts_data["message"], pts_data["notAvailable"], pts_data["notFound"])
    action_id, command_id, action = build_points_action(
        cmd["trigger"], cmd["group"], queue_id, code, pts_data["notAvailable"]
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[points] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "points", queue_id, queue_def, action, command, commands_config)

    # ── top ────────────────────────────────────────────────────────────────────
    top_data = locale_data["commands"]["top"]
    cmd = commands_config["top"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_top_code(5, top_data["header"], top_data["entry"], top_data["notAvailable"])
    action_id, command_id, action = build_top_action(
        cmd["trigger"], cmd["group"], queue_id, code, top_data["notAvailable"]
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[top] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "top", queue_id, queue_def, action, command, commands_config)

    # ── top10 ──────────────────────────────────────────────────────────────────
    cmd = commands_config["top10"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_top_code(10, top_data["header"], top_data["entry"], top_data["notAvailable"])
    action_id, command_id, action = build_top_action(
        cmd["trigger"], cmd["group"], queue_id, code, top_data["notAvailable"]
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id)
    print(f"[top10] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "top10", queue_id, queue_def, action, command, commands_config)

    # ── chatactivitypoints ─────────────────────────────────────────────────────
    cmd = commands_config["chatactivitypoints"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id = queue_def["id"]

    code = build_chat_activity_points_code(
        points=2,
        min_length=3,
        bots=list(["nightbot", "streamelements", "streamlabs", "moobot",
                   "fossabot", "wizebot", "botisimo", "commanderroot",
                   "stay_hydrated_bot", "restreambot", "pokemoncommunitygame",
                   "kofistreambot", "streamholics"]),
        bttv_emotes=list(["OMEGALUL", "PogU", "PauseChamp", "monkaS", "monkaW",
                           "LULW", "Clap", "GIGACHAD", "Pog", "FeelsBadMan",
                           "FeelsGoodMan", "HYPERS", "widepeepoHappy", "PepeLaugh",
                           "catJAM", "NODDERS", "COPIUM", "Sadge", "EZ", "PeepoClap",
                           "peepoHappy", "NOTED", "Aware", "forsenCD", "TriHard",
                           "WeirdChamp", "BASED", "OMEGADANCE", "peepoLeave", "peepoArrive"]),
    )
    action_id, action = build_chat_activity_action(
        "chatactivitypoints", cmd["group"], queue_id, code
    )
    print(f"[chatactivitypoints] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "chatactivitypoints", queue_id, queue_def, action, command=None, commands_config=commands_config)

    # ── raffle: join ───────────────────────────────────────────────────────────
    raffle_data = locale_data["commands"]["raffle"]
    join_data   = raffle_data["join"]
    cmd = commands_config["join"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id  = queue_def["id"]

    code = build_join_code(join_data["joined"], join_data["alreadyJoined"], join_data["notOpen"])
    action_id, command_id, action = build_raffle_action(
        cmd["trigger"], cmd["group"], queue_id, code, result_var="joinResult"
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id,
                           mod_only=cmd.get("mod_only", False))
    print(f"[join] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "join", queue_id, queue_def, action, command, commands_config)

    # ── raffle: openRaffle ─────────────────────────────────────────────────────
    open_data = raffle_data["openRaffle"]
    cmd = commands_config["openRaffle"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id  = queue_def["id"]

    code = build_open_raffle_code(open_data["opened"], open_data["noTitle"], open_data["alreadyOpen"])
    action_id, command_id, action = build_raffle_action(
        cmd["trigger"], cmd["group"], queue_id, code, result_var="openRaffleResult"
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id,
                           mod_only=cmd.get("mod_only", False))
    print(f"[openRaffle] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "openRaffle", queue_id, queue_def, action, command, commands_config)

    # ── raffle: closeRaffle ────────────────────────────────────────────────────
    close_data = raffle_data["closeRaffle"]
    cmd = commands_config["closeRaffle"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id  = queue_def["id"]

    code = build_close_raffle_code(close_data["closed"], close_data["notOpen"])
    action_id, command_id, action = build_raffle_action(
        cmd["trigger"], cmd["group"], queue_id, code, result_var="closeRaffleResult"
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id,
                           mod_only=cmd.get("mod_only", False))
    print(f"[closeRaffle] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "closeRaffle", queue_id, queue_def, action, command, commands_config)

    # ── raffle: drawRaffle ─────────────────────────────────────────────────────
    draw_data = raffle_data["drawRaffle"]
    cmd = commands_config["drawRaffle"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id  = queue_def["id"]

    # drawRaffle sends directly via TwitchAnnounce — no platform switch result_var
    code = build_draw_raffle_code(
        draw_data["starting"],
        draw_data["top5Winner"],
        draw_data["top10Winner"],
        draw_data["bonusWinner"],
        draw_data["noJoined"],
        draw_data["top5NoLeaderboard"],
        draw_data["top10NoWinner"],
        draw_data["top10NotEnough"],
        draw_data["notOpen"],
    )
    action_id, command_id, action = build_raffle_action(
        cmd["trigger"], cmd["group"], queue_id, code, result_var=None
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id,
                           mod_only=cmd.get("mod_only", False))
    print(f"[drawRaffle] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "drawRaffle", queue_id, queue_def, action, command, commands_config)

    # ── raffle: showPreviousRaffle ─────────────────────────────────────────────
    show_data = raffle_data["showPreviousRaffle"]
    cmd = commands_config["showPreviousRaffle"]
    queue_key = cmd["queue"]
    if queue_key not in queues_config:
        raise ValueError(f"Queue '{queue_key}' not defined in config/queues.json")
    queue_def = queues_config[queue_key]
    queue_id  = queue_def["id"]

    code = build_show_previous_raffle_code(show_data["template"], show_data["noHistory"])
    action_id, command_id, action = build_raffle_action(
        cmd["trigger"], cmd["group"], queue_id, code, result_var="showPreviousRaffleResult"
    )
    command = make_command(cmd["trigger"], cmd["trigger"], cmd["group"], command_id, action_id,
                           mod_only=cmd.get("mod_only", False))
    print(f"[showPreviousRaffle] queue: {queue_def['name']} (blocking={queue_def['blocking']}), group: {cmd['group']}")
    _write_export(out_dir, "showPreviousRaffle", queue_id, queue_def, action, command, commands_config)

    print()
    print("To import:")
    print("  1. Open Streamer.bot")
    print("  2. Actions tab -> Import button (top right)")
    print("  3. Paste the contents of a generated/streamerbot/*.import.txt file")
    print("  4. Click Import")
    print()
    print("StreamElements integration (optional, points / top / top10 / chatactivitypoints):")
    print('  Settings -> Variables -> add "se_jwt" (persisted global variable)')
    print('  Settings -> Variables -> add "se_channel" (persisted global variable)')
    print("  se_jwt    = your StreamElements JWT token (from streamelements.com/dashboard/account/security)")
    print("  se_channel = your StreamElements channel ObjectId (decode your JWT -- field 'channel')")
    print()
    print("  chatactivitypoints — after importing, add the trigger manually:")
    print("  Open the 'chatactivitypoints' action -> Triggers -> Add -> Twitch Chat Message")
    print("  Set User Cooldown = 30 seconds on that trigger to limit one reward per 30 s per viewer.")
    print()
    print("Raffle bot (join / openRaffle / closeRaffle / drawRaffle / showPreviousRaffle):")
    print("  No extra configuration required — raffle state is stored in Streamer.bot global variables.")
    print("  Raffle history is saved to: %APPDATA%\\Streamer.bot\\raffle_history.json")
    print("  openRaffle / closeRaffle / drawRaffle / showPreviousRaffle are mod-only (grantType=3).")
    print()
    print("OpenAI enhancement (optional, 8ball only):")
    print('  Settings -> Variables -> add "openai_api_key" (persisted global variable)')
    print("  When set, responses are enhanced by Pixelfreaki (gpt-4o-mini).")
    print("  Falls back to local responses if the key is missing or on any error.")
    print()
    print("AI_Licia integration (optional, oracle/horoscope/curse/omen/tarot/judge/hex):")
    print('  Settings -> Variables -> add "ai_licia_key" (persisted global variable)')
    print("  When set, AI_Licia sends a persona-driven response directly to chat.")
    print("  Falls back to local responses if the key is missing or on any error.")


def _write_export(out_dir, name, queue_id, queue_def, action, command=None, commands_config=None):
    # Apply stable action/command IDs from config so re-imports don't create duplicates.
    if commands_config and name in commands_config:
        cmd_def = commands_config[name]
        if "action_id" in cmd_def:
            old_aid = action["id"]
            aid = cmd_def["action_id"]
            if command is not None and "command_id" in cmd_def:
                old_cid = command["id"]
                cid = cmd_def["command_id"]
                action  = json.loads(json.dumps(action) .replace(old_aid, aid).replace(old_cid, cid))
                command = json.loads(json.dumps(command).replace(old_aid, aid).replace(old_cid, cid))
            else:
                action = json.loads(json.dumps(action).replace(old_aid, aid))

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
            "commands": [] if command is None else [command],
            "websocketServers": [],
            "websocketClients": [],
            "timers": [],
        },
        "version": EXPORT_VERSION,
        "exportedFrom": EXPORTED_FROM,
        "minimumVersion": MINIMUM_VERSION,
    }
    txt_path = os.path.join(out_dir, f"{name}.import.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(encode_export(export))
    print(f"[done] written to generated/streamerbot/{name}.import.txt")


if __name__ == "__main__":
    main()
