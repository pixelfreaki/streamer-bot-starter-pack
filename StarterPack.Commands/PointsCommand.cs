using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class PointsCommand : ICommand
{
    private readonly string _message;
    private readonly string _notAvailable;
    private readonly string _notFound;
    private readonly IStreamElementsService? _se;

    public string Name => "points";

    public PointsCommand(
        string message,
        string notAvailable,
        string notFound,
        IStreamElementsService? se = null)
    {
        _message      = message;
        _notAvailable = notAvailable;
        _notFound     = notFound;
        _se           = se;
    }

    public async Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        if (_se is not { IsAvailable: true })
            return CommandResult.Fail(_notAvailable);

        string target = string.IsNullOrWhiteSpace(context.Input) ? context.UserName : context.Input.Trim();

        var result = await _se.GetUserPointsAsync(target, cancellationToken);
        if (result is null)
            return CommandResult.Fail(_notFound.Replace("{target}", target));

        var (points, rank) = result.Value;
        string msg = _message
            .Replace("{target}", target)
            .Replace("{points}", points.ToString())
            .Replace("{rank}", rank.ToString());

        return CommandResult.Ok(msg);
    }
}
