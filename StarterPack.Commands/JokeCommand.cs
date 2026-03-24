using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class JokeCommand : ICommand
{
    private const string BaseSystemPrompt =
        """
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
        - Do not repeat common/example jokes (e.g., "ex-presso", "Uberlândia", "aeromosca")
        - Each joke must be original and different from the others

        Goal:
        Make each feel like a quick, funny, "tiozão" joke that works well in a fast Twitch chat.

        Now generate exactly 10 original jokes.
        """;

    private static readonly string[] DefaultFallbacks =
    [
        "I analyzed this. Results: 1. Bad idea | 2. Still a bad idea | 3. Somehow worse with confidence.",
        "This has the same energy as refactoring code at 2am. Technically possible. Emotionally questionable.",
        "I like this plan. Simple, bold, and completely ignores consequences. My favorite combination.",
        "Error 404: Common sense not found. Bug or feature? Data suggests: feature.",
        "I looked at the facts. Calculated the risks. Decided to ignore both. That's called determination. Or sleep deprivation.",
    ];

    private readonly string[] _fallbacks;
    private readonly IAiProvider? _aiProvider;
    private readonly string _systemPrompt;
    private readonly string _emptyPrompt;
    private readonly string _topicPrompt;
    private readonly Random _random = new();

    public string Name => "joke";

    public JokeCommand(
        string[]? fallbacks = null,
        IAiProvider? aiProvider = null,
        string? locale = null,
        string? emptyPrompt = null,
        string? topicPrompt = null)
    {
        _fallbacks = fallbacks is { Length: > 0 } ? fallbacks : DefaultFallbacks;
        _aiProvider = aiProvider;
        _systemPrompt = BuildSystemPrompt(locale);
        (_emptyPrompt, _topicPrompt) = GetPrompts(locale, emptyPrompt, topicPrompt);
    }

    public async Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string userPrompt = string.IsNullOrWhiteSpace(context.Input)
            ? _emptyPrompt
            : _topicPrompt + context.Input;

        if (_aiProvider is { IsAvailable: true })
        {
            string? response = await _aiProvider.EnhanceAsync(userPrompt, _systemPrompt, maxTokens: 600, temperature: 0.9, cancellationToken);
            if (response is not null)
            {
                var jokes = ParseJokeList(response);
                return CommandResult.Ok(jokes.Count > 0
                    ? jokes[_random.Next(jokes.Count)]
                    : response);
            }
        }

        return CommandResult.Ok(_fallbacks[_random.Next(_fallbacks.Length)]);
    }

    private static string BuildSystemPrompt(string? locale)
    {
        string languageInstruction = locale switch
        {
            "pt_BR" => "You must respond in Brazilian Portuguese.",
            "en"    => "You must respond in English.",
            null    => string.Empty,
            _       => $"You must respond in the language matching locale '{locale}'.",
        };

        return string.IsNullOrEmpty(languageInstruction)
            ? BaseSystemPrompt
            : BaseSystemPrompt + $"\nLanguage: {languageInstruction}";
    }

    private static List<string> ParseJokeList(string response)
    {
        var jokes = new List<string>();
        foreach (var line in response.Split('\n'))
        {
            var t = line.Trim();
            int dotIdx = t.IndexOf(". ");
            if (dotIdx > 0 && dotIdx <= 3)
            {
                var text = t[(dotIdx + 2)..].Trim();
                if (text.Length > 0)
                    jokes.Add(text);
            }
        }
        return jokes;
    }

    private static (string empty, string topic) GetPrompts(string? locale, string? empty, string? topic)
    {
        var (defaultEmpty, defaultTopic) = locale switch
        {
            "pt_BR" => ("Me conte uma piada.", "Me conte uma piada sobre: "),
            _       => ("Tell me a joke.", "Tell me a joke about: "),
        };
        return (empty ?? defaultEmpty, topic ?? defaultTopic);
    }
}
