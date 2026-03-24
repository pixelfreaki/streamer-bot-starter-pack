using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class HexCommand : ICommand
{
    private readonly string[] _styles;
    private readonly string[] _fallback;
    private readonly string _noInput;
    private readonly IAiProvider? _aiProvider;
    private readonly Random _random = new();

    public string Name => "hex";

    public HexCommand(string[] styles, string[] fallback, string noInput, IAiProvider? aiProvider = null)
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

        string target = context.Input.TrimStart('@').Trim();

        if (_aiProvider?.IsAvailable == true)
        {
            string prompt = _styles[_random.Next(_styles.Length)]
                .Replace("{caster}", context.UserName)
                .Replace("{target}", target);

            await _aiProvider.EnhanceAsync(prompt, systemPrompt: null, cancellationToken: cancellationToken);
            return CommandResult.Ok(string.Empty);
        }

        string message = _fallback[_random.Next(_fallback.Length)]
            .Replace("{user}", context.UserName)
            .Replace("{target}", target);
        return CommandResult.Ok(message);
    }

    private static readonly string[] DefaultStyles =
    [
        "{caster} curses {target}.\nStart with \"{caster} curses {target}\" and narrate the curse. Be dark and brief."
    ];

    private static readonly string[] DefaultFallback =
    [
        "A hex without a target dissolves into the void. Name someone, {user}.",
        "The ritual is incomplete. {user} must name a target."
    ];
}
