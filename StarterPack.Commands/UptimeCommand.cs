using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !uptime — type 1007 (get %uptime% variable), then C# inline that calls CPH.TwitchAnnounce.
/// Only available on Twitch.
/// This stub exists for local testing and runner registration.
/// </summary>
public class UptimeCommand : ICommand
{
    public string Name => "uptime";

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        return Task.FromResult(CommandResult.Ok($"[uptime] Uptime for {context.UserName}'s channel (native Streamer.bot action)"));
    }
}
