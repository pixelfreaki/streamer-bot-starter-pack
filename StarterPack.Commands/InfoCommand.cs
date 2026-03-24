using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// Generic single-message info command (!pc, !gear, !peripherals, etc.)
/// </summary>
public class InfoCommand : ICommand
{
    private readonly string _message;

    public string Name { get; }

    public InfoCommand(string name, string message)
    {
        Name    = name;
        _message = message;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string message = _message.Replace("{user}", context.UserName);
        return Task.FromResult(CommandResult.Ok(message));
    }
}
