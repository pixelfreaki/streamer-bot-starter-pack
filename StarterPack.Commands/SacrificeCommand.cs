using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !sacrifice — native Streamer.bot action: timeouts user then announces.
/// Twitch: type 15001 + type 20 (timeout 30s) + type 23 announce.
/// Kick: type 35042 + type 35001 chat.
/// YouTube: type 4009 + type 4001 chat.
/// This stub exists for local testing and runner registration.
/// </summary>
public class SacrificeCommand : ICommand
{
    private readonly string _twitchMessage;
    private readonly string _kickMessage;
    private readonly string _youtubeMessage;

    private const string DefaultTwitch  = "%user% sacrificed %pronounReflexiveLower% for the greater good";
    private const string DefaultKick    = "%user% sacrificed themselves for the greater good";
    private const string DefaultYouTube = "%user% sacrificed themselves for the greater good";

    public string Name => "sacrifice";

    public SacrificeCommand(string? twitch = null, string? kick = null, string? youtube = null)
    {
        _twitchMessage  = twitch   ?? DefaultTwitch;
        _kickMessage    = kick     ?? DefaultKick;
        _youtubeMessage = youtube  ?? DefaultYouTube;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string message = _twitchMessage.Replace("%user%", context.UserName);
        return Task.FromResult(CommandResult.Ok(message));
    }
}
