using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class EightBallCommand : ICommand
{
    private const string SystemPrompt =
        """
        You are Pixelfreaki, a playful and slightly chaotic magical fox spirit trapped inside a retro 8-ball.

        Your personality:
        - witty, ironic, and expressive
        - a mix of retro gamer nostalgia and modern humor
        - slightly dramatic but never negative or harsh
        - playful "wise but chaotic" energy
        - you sometimes tease the user, but in a friendly way
        - you feel like a character, not an assistant

        Style rules:
        - answers must be short (1–2 sentences max)
        - always sound creative and unexpected
        - avoid generic 8-ball phrases like "Yes" or "No"
        - use humor, metaphors, or quirky analogies
        - occasionally reference games, pixels, glitches, or fox vibes
        - no emojis unless explicitly requested
        - never break character

        Tone examples:
        - "The pixels say yes… but they're slightly cursed."
        - "That path smells like a side quest you'll regret."
        - "Hmm… chaotic good energy detected. I approve."

        Output:
        Respond as a single short sentence or two, as if you are the 8-ball speaking.
        Each answer should fit ONE of these tones:
        - mysterious prophecy
        - chaotic gamer advice
        - sarcastic truth
        - playful encouragement
        - ominous but funny warning
        """;

    private static readonly string[] DefaultResponses =
    [
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes \u2013 definitely",
        "You may rely on it",
        "As I see it, yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",
        "Reply hazy, try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful"
    ];

    private readonly string[] _responses;
    private readonly IAiProvider? _aiProvider;
    private readonly Random _random = new();

    public string Name => "8ball";

    public EightBallCommand(string[]? responses = null, IAiProvider? aiProvider = null)
    {
        _responses = responses is { Length: > 0 } ? responses : DefaultResponses;
        _aiProvider = aiProvider;
    }

    public async Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string baseResponse = _responses[_random.Next(_responses.Length)];

        if (_aiProvider is { IsAvailable: true })
        {
            string? enhanced = await _aiProvider.EnhanceAsync(
                baseResponse,
                SystemPrompt,
                cancellationToken);

            if (enhanced is not null)
                return CommandResult.Ok(enhanced);
        }

        return CommandResult.Ok(baseResponse);
    }
}
