using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class CurseCommand : ICommand
{
    private readonly string[] _styles;
    private readonly string[] _fallback;
    private readonly string _noInput;
    private readonly IAiProvider? _aiProvider;
    private readonly Random _random = new();

    public string Name => "curse";

    public CurseCommand(string[] styles, string[] fallback, string noInput, IAiProvider? aiProvider = null)
    {
        _styles = styles.Length > 0 ? styles : DefaultStyles;
        _fallback = fallback.Length > 0 ? fallback : DefaultFallback;
        _noInput = noInput;
        _aiProvider = aiProvider;
    }

    public async Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(context.Input))
            return CommandResult.Ok(_noInput.Replace("{user}", context.UserName));

        if (_aiProvider?.IsAvailable == true)
        {
            string prompt = _styles[_random.Next(_styles.Length)]
                .Replace("{user}", context.UserName)
                .Replace("{text}", context.Input);

            await _aiProvider.EnhanceAsync(prompt, systemPrompt: null, cancellationToken: cancellationToken);
            return CommandResult.Ok(string.Empty);
        }

        string message = _fallback[_random.Next(_fallback.Length)]
            .Replace("{user}", context.UserName);
        return CommandResult.Ok(message);
    }

    private static readonly string[] DefaultStyles =
    [
        "{user} asked for a curse: \"{text}\"\nRespond as a dark entity casting a creative curse on {user}. Be brief and unsettling."
    ];

    private static readonly string[] DefaultFallback =
    [
        "The curse ricochets. No target, no hex.",
        "The Oracle of Ruin waits. Give it something to destroy."
    ];
}
