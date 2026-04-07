using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class ShowPreviousRaffleCommand : ICommand
{
    private readonly IRaffleHistory _history;
    private readonly string _template;
    private readonly string _noHistory;

    public string Name => "showPreviousRaffle";

    public ShowPreviousRaffleCommand(
        string template,
        string noHistory,
        IRaffleHistory history)
    {
        _template  = template;
        _noHistory = noHistory;
        _history   = history;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        var recent = _history.GetRecent(1);
        if (recent.Count == 0)
            return Task.FromResult(CommandResult.Fail(_noHistory));

        var s = recent[0];
        string msg = _template
            .Replace("{title}",  s.Title)
            .Replace("{date}",   s.Date.ToString("yyyy-MM-dd"))
            .Replace("{top5}",   s.Top5Winner  ?? "-")
            .Replace("{top10}",  s.Top10Winner ?? "-")
            .Replace("{bonus}",  s.BonusWinner ?? "-");

        return Task.FromResult(CommandResult.Ok(msg));
    }
}
