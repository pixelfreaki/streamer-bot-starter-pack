using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class ClipCommand : ICommand
{
    private const string DefaultSuccess = "🎬 {user} created a clip! {clipUrl}";
    private const string DefaultFailure = "❌ Couldn't create a clip right now. Try again, {user}!";

    private readonly string _success;
    private readonly string _failure;
    private readonly Func<string?> _createClip;

    public string Name => "clip";

    /// <param name="success">Message on success. Supports {user} and {clipUrl} placeholders.</param>
    /// <param name="failure">Message on failure. Supports {user} placeholder.</param>
    /// <param name="createClip">Delegate that creates a clip and returns its URL, or null/empty on failure.
    /// In Streamer.bot this is fulfilled by CPH.TwitchCreateClip(); inject a fake for tests.</param>
    public ClipCommand(string? success = null, string? failure = null, Func<string?>? createClip = null)
    {
        _success   = success    ?? DefaultSuccess;
        _failure   = failure    ?? DefaultFailure;
        _createClip = createClip ?? (() => null);
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string? clipUrl = _createClip();
        string message  = string.IsNullOrEmpty(clipUrl)
            ? _failure.Replace("{user}", context.UserName)
            : _success.Replace("{user}", context.UserName).Replace("{clipUrl}", clipUrl);

        return Task.FromResult(CommandResult.Ok(message));
    }
}
