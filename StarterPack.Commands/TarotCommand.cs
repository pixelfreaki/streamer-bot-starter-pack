using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class TarotCommand : ICommand
{
    private readonly string[] _styles;
    private readonly string[] _fallback;
    private readonly IAiProvider? _aiProvider;
    private readonly Random _random = new();

    public string Name => "tarot";

    public TarotCommand(string[] styles, string[] fallback, IAiProvider? aiProvider = null)
    {
        _styles = styles.Length > 0 ? styles : DefaultStyles;
        _fallback = fallback.Length > 0 ? fallback : DefaultFallback;
        _aiProvider = aiProvider;
    }

    public async Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        if (_aiProvider?.IsAvailable == true)
        {
            string prompt = _styles[_random.Next(_styles.Length)]
                .Replace("{user}", context.UserName);

            await _aiProvider.EnhanceAsync(prompt, systemPrompt: null, cancellationToken: cancellationToken);
            return CommandResult.Ok(string.Empty);
        }

        string message = _fallback[_random.Next(_fallback.Length)]
            .Replace("{user}", context.UserName);
        return CommandResult.Ok(message);
    }

    private static readonly string[] DefaultStyles =
    [
        "{user} asked for a tarot reading.\nRespond as a dark cartomancer drawing a card for {user}. Be brief and unsettling."
    ];

    private static readonly string[] DefaultFallback =
    [
        "The cards refuse to be drawn for {user} today.",
        "The Veil is thick. The Cartomancer cannot read what lies ahead."
    ];
}
