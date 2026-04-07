using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class JoinCommand : ICommand
{
    private readonly IRaffleState _state;
    private readonly string _joined;
    private readonly string _alreadyJoined;
    private readonly string _notOpen;

    public string Name => "join";

    public JoinCommand(
        string joined,
        string alreadyJoined,
        string notOpen,
        IRaffleState state)
    {
        _joined        = joined;
        _alreadyJoined = alreadyJoined;
        _notOpen       = notOpen;
        _state         = state;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        if (!_state.IsOpen)
            return Task.FromResult(CommandResult.Fail(_notOpen));

        bool added = _state.AddUser(context.UserName);
        string msg = added
            ? _joined.Replace("{user}", context.UserName)
            : _alreadyJoined.Replace("{user}", context.UserName);

        return Task.FromResult(CommandResult.Ok(msg));
    }
}
