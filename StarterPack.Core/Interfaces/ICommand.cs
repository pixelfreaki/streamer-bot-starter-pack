using StarterPack.Core.Models;

namespace StarterPack.Core.Interfaces;

public interface ICommand
{
    string Name { get; }
    Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default);
}
