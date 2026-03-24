using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !followage — C# inline (get user info), then type 51 (get follow info), then C# inline (send message).
/// Only available on Twitch.
/// This stub exists for local testing and runner registration.
/// </summary>
public class FollowAgeCommand : ICommand
{
    public string Name => "followage";

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string target = string.IsNullOrWhiteSpace(context.Input) ? context.UserName : context.Input.Trim();
        return Task.FromResult(CommandResult.Ok($"[followage] Follow age for {target} (native Streamer.bot action)"));
    }
}
