using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !settitle — native Streamer.bot action (Twitch type 15, Kick type 35030, YouTube type 4002).
/// Fully silent; no locale messages needed.
/// This stub exists for local testing and runner registration.
/// </summary>
public class SetTitleCommand : ICommand
{
    public string Name => "settitle";

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string title = string.IsNullOrWhiteSpace(context.Input) ? "(no title)" : context.Input.Trim();
        return Task.FromResult(CommandResult.Ok($"[settitle] Title set to: {title} (native Streamer.bot action)"));
    }
}
