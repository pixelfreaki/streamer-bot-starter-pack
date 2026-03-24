using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !accountage — fetches account creation age via decapi.me.
/// Self-check: !accountage
/// Target check: !accountage @username
/// </summary>
public class AccountAgeCommand : ICommand
{
    private readonly string _message;
    private readonly string _notAvailable;

    private const string DefaultMessage      = "/me %inputUser% was born %accountAge% ago";
    private const string DefaultNotAvailable = "@%user% !accountage is not available on this platform D:";

    private static readonly HttpClient _http = new();

    public string Name => "accountage";

    public AccountAgeCommand(string? message = null, string? notAvailable = null)
    {
        _message      = message      ?? DefaultMessage;
        _notAvailable = notAvailable ?? DefaultNotAvailable;
    }

    public async Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string target = string.IsNullOrWhiteSpace(context.Input)
            ? context.UserName
            : context.Input.TrimStart('@').Trim();

        string url = $"https://decapi.me/twitch/accountage/{target.ToLower()}?precision=4";
        string accountAge;
        try
        {
            accountAge = (await _http.GetStringAsync(url, cancellationToken)).Trim();
        }
        catch (Exception ex)
        {
            return CommandResult.Fail($"Could not get account age for {target}: {ex.Message}");
        }

        if (string.IsNullOrEmpty(accountAge) || accountAge.StartsWith("Error"))
            return CommandResult.Fail($"Could not get account age for {target}: {accountAge}");

        string msg = _message
            .Replace("%inputUser%", target)
            .Replace("%accountAge%", accountAge);

        return CommandResult.Ok(msg);
    }
}
