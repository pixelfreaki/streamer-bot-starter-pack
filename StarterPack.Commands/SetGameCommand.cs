using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !setgame — native Streamer.bot action (type 16 for Twitch, type 35031 for Kick)
/// with IGDB C# fallback search when the direct set fails.
/// Not available on YouTube.
/// This stub exists for local testing and runner registration.
/// </summary>
public class SetGameCommand : ICommand
{
    private readonly string _notFound;
    private readonly string _notAvailable;

    private const string DefaultNotFound     = "Could not set game to %rawInput%";
    private const string DefaultNotAvailable = "@%user% !setgame is not available on this platform D:";

    public string Name => "setgame";

    public SetGameCommand(string? notFound = null, string? notAvailable = null)
    {
        _notFound     = notFound     ?? DefaultNotFound;
        _notAvailable = notAvailable ?? DefaultNotAvailable;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string game = string.IsNullOrWhiteSpace(context.Input) ? "(no game)" : context.Input.Trim();
        return Task.FromResult(CommandResult.Ok($"[setgame] Game set to: {game} (native Streamer.bot action)"));
    }
}
