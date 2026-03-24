using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !shoutout — native Streamer.bot action (Twitch shoutout + Kick chat).
/// The actual logic runs via native sub-actions in Streamer.bot.
/// This stub exists for local testing and runner registration.
/// </summary>
public class ShoutoutCommand : ICommand
{
    public string Name => "shoutout";

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string target = string.IsNullOrWhiteSpace(context.Input) ? context.UserName : context.Input.Trim();
        return Task.FromResult(CommandResult.Ok($"[shoutout] Shouting out {target}! (native Streamer.bot action)"));
    }
}
