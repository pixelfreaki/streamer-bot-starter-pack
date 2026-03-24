using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class FortuneCommand : ICommand
{
    private static readonly string[] DefaultFortunes =
    [
        "A journey of a thousand miles begins with a single step.",
        "The best time to plant a tree was 20 years ago. The second best time is now.",
        "Wherever you go, go with all your heart.",
        "In the middle of difficulty lies opportunity.",
        "Your talents will be recognized and suitably rewarded.",
    ];

    private readonly string[] _fortunes;
    private readonly Random _random = new();

    public string Name => "fortune";

    public FortuneCommand(string[]? fortunes = null)
    {
        _fortunes = fortunes is { Length: > 0 } ? fortunes : DefaultFortunes;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string fortune = _fortunes[_random.Next(_fortunes.Length)];
        return Task.FromResult(CommandResult.Ok(fortune));
    }
}
