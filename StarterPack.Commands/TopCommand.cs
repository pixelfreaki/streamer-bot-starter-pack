using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class TopCommand : ICommand
{
    private readonly string _header;
    private readonly string _entry;
    private readonly string _notAvailable;
    private readonly int _limit;
    private readonly IStreamElementsService? _se;

    public string Name { get; }

    public TopCommand(
        string name,
        string header,
        string entry,
        string notAvailable,
        int limit = 5,
        IStreamElementsService? se = null)
    {
        Name          = name;
        _header       = header;
        _entry        = entry;
        _notAvailable = notAvailable;
        _limit        = limit;
        _se           = se;
    }

    public async Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        if (_se is not { IsAvailable: true })
            return CommandResult.Fail(_notAvailable);

        var top = await _se.GetTopAsync(_limit, cancellationToken);
        if (top.Count == 0)
            return CommandResult.Fail(_notAvailable);

        var entries = top.Select((u, i) => _entry
            .Replace("{rank}", (i + 1).ToString())
            .Replace("{username}", u.Username)
            .Replace("{points}", u.Points.ToString()));

        return CommandResult.Ok($"{_header} {string.Join(" | ", entries)}");
    }
}
