using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class HoroscopeCommand : ICommand
{
    private readonly string[] _styles;
    private readonly string[] _fallback;
    private readonly string _noInput;
    private readonly IAiProvider? _aiProvider;
    private readonly Random _random = new();

    public string Name => "horoscope";

    public HoroscopeCommand(string[] styles, string[] fallback, string noInput, IAiProvider? aiProvider = null)
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
        "{user} asked for their horoscope: \"{text}\"\nRespond as a dark horoscope for {user}. Be brief and unsettling."
    ];

    private static readonly string[] DefaultFallback =
    [
        "The stars refuse to align for you today.",
        "The Astral Oracle sees turbulence. Try again when the cosmos is less hostile."
    ];
}
