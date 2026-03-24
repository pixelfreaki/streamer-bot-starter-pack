using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class EightBallCommand : ICommand
{
    private static readonly string[] Responses =
    [
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes – definitely",
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

    private readonly IAiProvider? _aiProvider;
    private readonly Random _random = new();

    public string Name => "8ball";

    public EightBallCommand(IAiProvider? aiProvider = null)
    {
        _aiProvider = aiProvider;
    }

    public async Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string baseResponse = Responses[_random.Next(Responses.Length)];

        if (_aiProvider is { IsAvailable: true })
        {
            string? enhanced = await _aiProvider.EnhanceAsync(
                $"Rephrase this magic 8-ball response creatively: {baseResponse}",
                cancellationToken);

            if (enhanced is not null)
                return CommandResult.Ok(enhanced);
        }

        return CommandResult.Ok(baseResponse);
    }
}
