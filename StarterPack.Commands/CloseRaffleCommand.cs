using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class CloseRaffleCommand : ICommand
{
    private readonly IRaffleState _state;
    private readonly string _closed;
    private readonly string _notOpen;

    public string Name => "closeRaffle";

    public CloseRaffleCommand(
        string closed,
        string notOpen,
        IRaffleState state)
    {
        _closed  = closed;
        _notOpen = notOpen;
        _state   = state;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        if (!_state.IsOpen)
            return Task.FromResult(CommandResult.Fail(_notOpen));

        _state.Close();
        return Task.FromResult(CommandResult.Ok(_closed));
    }
}
