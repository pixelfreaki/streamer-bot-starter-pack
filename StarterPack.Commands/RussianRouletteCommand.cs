using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !russianroulette — native Streamer.bot action using type 99900 (random group).
/// 1/6 chance: timeout + announce death. 5/6 chance: announce survival.
/// Available on Twitch, Kick, and YouTube.
/// This stub exists for local testing and runner registration.
/// </summary>
public class RussianRouletteCommand : ICommand
{
    private readonly string _diesMessage;
    private readonly string _livesMessage;

    private const string DefaultDies  = "%user% shot %pronounReflexiveLower% 🪦";
    private const string DefaultLives = "%user% pulled the trigger... but nothing happened";

    private readonly Random _random = new();

    public string Name => "russianroulette";

    public RussianRouletteCommand(string? dies = null, string? lives = null)
    {
        _diesMessage  = dies  ?? DefaultDies;
        _livesMessage = lives ?? DefaultLives;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        bool died = _random.Next(6) == 0;
        string template = died ? _diesMessage : _livesMessage;
        string message = template
            .Replace("%user%", context.UserName)
            .Replace("%pronounReflexiveLower%", "themselves");

        return Task.FromResult(CommandResult.Ok(message));
    }
}
