using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !accountage — C# inline that calls TwitchGetUserInfoByLogin, then type 1007 + chat.
/// Only available on Twitch.
/// This stub exists for local testing and runner registration.
/// </summary>
public class AccountAgeCommand : ICommand
{
    private readonly string _message;
    private readonly string _notAvailable;

    private const string DefaultMessage      = "/me %inputUser% was born %accountAge% ago";
    private const string DefaultNotAvailable = "@%user% !accountage is not available on this platform D:";

    public string Name => "accountage";

    public AccountAgeCommand(string? message = null, string? notAvailable = null)
    {
        _message      = message      ?? DefaultMessage;
        _notAvailable = notAvailable ?? DefaultNotAvailable;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string target = string.IsNullOrWhiteSpace(context.Input) ? context.UserName : context.Input.Trim();
        return Task.FromResult(CommandResult.Ok($"[accountage] Account age for {target} (native Streamer.bot action)"));
    }
}
