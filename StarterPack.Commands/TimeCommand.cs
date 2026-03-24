using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !time — pure native chat message on all three platforms using %time:hh:mm tt% variable.
/// No C# inline needed.
/// This stub exists for local testing and runner registration.
/// </summary>
public class TimeCommand : ICommand
{
    private readonly string _twitchMessage;
    private readonly string _kickMessage;
    private readonly string _youtubeMessage;

    private const string DefaultTwitch  = "/me @%user% The time for %broadcastUser% is %time:hh:mm tt%";
    private const string DefaultKick    = "@%user% The time for %broadcastUser% is %time:hh:mm tt%";
    private const string DefaultYouTube = "@%user% The time for %broadcastUser% is %time:hh:mm tt%";

    public string Name => "time";

    public TimeCommand(string? twitch = null, string? kick = null, string? youtube = null)
    {
        _twitchMessage  = twitch   ?? DefaultTwitch;
        _kickMessage    = kick     ?? DefaultKick;
        _youtubeMessage = youtube  ?? DefaultYouTube;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        // Local stub: use the Twitch-style message as a placeholder
        string message = _twitchMessage
            .Replace("%user%", context.UserName)
            .Replace("%broadcastUser%", context.UserName)
            .Replace("%time:hh:mm tt%", DateTime.Now.ToString("hh:mm tt"));

        return Task.FromResult(CommandResult.Ok(message));
    }
}
