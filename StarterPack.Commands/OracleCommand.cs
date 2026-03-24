using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class OracleCommand : ICommand
{
    private readonly string[] _styles;
    private readonly string[] _fallback;
    private readonly string _noInput;
    private readonly IAiProvider? _aiProvider;
    private readonly Random _random = new();

    public string Name => "oracle";

    public OracleCommand(string[] styles, string[] fallback, string noInput, IAiProvider? aiProvider = null)
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
        "{user} asked the Oracle: \"{text}\"\nRespond as a dark and mysterious oracle. Be brief and unsettling."
    ];

    private static readonly string[] DefaultFallback =
    [
        "The Oracle sees only darkness where your question should be.",
        "The visions are obscured. Try again when the stars align."
    ];
}
