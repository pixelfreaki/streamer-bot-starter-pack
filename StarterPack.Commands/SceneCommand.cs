using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !scene — native Streamer.bot action (type 34: OBS set scene).
/// No platform switch, no C#, no locale messages needed.
/// This stub exists for local testing and runner registration.
/// </summary>
public class SceneCommand : ICommand
{
    public string Name => "scene";

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string scene = string.IsNullOrWhiteSpace(context.Input) ? "(no scene)" : context.Input.Trim();
        return Task.FromResult(CommandResult.Ok($"[scene] Switching OBS scene to: {scene} (native Streamer.bot action)"));
    }
}
