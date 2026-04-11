using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class CurseCommand : ICommand
{
    private readonly string[] _styles;
    private readonly string[] _fallback;
    private readonly IAiProvider? _aiProvider;
    private readonly Random _random = new();

    public string Name => "curse";

    public CurseCommand(string[] styles, string[] fallback, IAiProvider? aiProvider = null)
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
        "{user} has invoked a curse upon this entire stream.\nRespond as a dark entity casting a creative curse over the channel and everyone watching. Be brief and unsettling."
    ];

    private static readonly string[] DefaultFallback =
    [
        "The curse settles over the stream. Something wicked this way stays.",
        "The Oracle of Ruin has spoken. This channel is marked."
    ];
}
