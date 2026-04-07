using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class OpenRaffleCommand : ICommand
{
    private readonly IRaffleState _state;
    private readonly string _opened;
    private readonly string _noTitle;
    private readonly string _alreadyOpen;

    public string Name => "openRaffle";

    public OpenRaffleCommand(
        string opened,
        string noTitle,
        string alreadyOpen,
        IRaffleState state)
    {
        _opened      = opened;
        _noTitle     = noTitle;
        _alreadyOpen = alreadyOpen;
        _state       = state;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(context.Input))
            return Task.FromResult(CommandResult.Fail(_noTitle));

        if (_state.IsOpen)
            return Task.FromResult(CommandResult.Fail(_alreadyOpen.Replace("{title}", _state.Title)));

        string title = context.Input.Trim();
        _state.Open(title);

        return Task.FromResult(CommandResult.Ok(_opened.Replace("{title}", title)));
    }
}
