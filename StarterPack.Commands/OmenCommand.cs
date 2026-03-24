using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class OmenCommand : ICommand
{
    private readonly string[] _styles;
    private readonly string[] _fallback;
    private readonly IAiProvider? _aiProvider;
    private readonly Random _random = new();

    public string Name => "omen";

    public OmenCommand(string[] styles, string[] fallback, IAiProvider? aiProvider = null)
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
        "{user} asked for an omen.\nRespond as a dark entity revealing an omen about {user}. Be brief and unsettling."
    ];

    private static readonly string[] DefaultFallback =
    [
        "The omens are silent today. That is itself a warning.",
        "Something stirs around {user}. The Herald cannot speak it aloud."
    ];
}
