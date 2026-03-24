namespace StarterPack.Core.Models;

public class CommandResult
{
    public bool Success { get; init; }
    public string Message { get; init; } = string.Empty;

    public static CommandResult Ok(string message) => new() { Success = true, Message = message };
    public static CommandResult Fail(string message) => new() { Success = false, Message = message };
}
