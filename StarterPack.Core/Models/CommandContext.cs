namespace StarterPack.Core.Models;

public class CommandContext
{
    public string UserName { get; init; } = string.Empty;
    public string Input { get; init; } = string.Empty;
    public IReadOnlyDictionary<string, string> Args { get; init; } = new Dictionary<string, string>();
}
