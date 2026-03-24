using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class LurkCommand : ICommand
{
    private static readonly string[] DefaultMessages =
    [
        "⚠️ {user} launched LURK.exe… reality corrupted… user not found",
        "👁️ {user} entered lurk mode… watching… always watching…",
        "{user} disappeared from chat… but not from the system",
        "error 404: {user} not found… just digital echo",
        "⚡ activity detected: {user}… but not in this dimension",
        "███ USER TRANSITION: {user} → SHADOW STATE",
        "lurk mode: {user} watching everything, saying nothing 🧘‍♀️",
        "{user} went stealth… even the chat lost sight of them",
        "🦊 PixelFreaki detected {user} in lurk mode... fading in 3… 2… glitch 👾",
        "{user} lurking like a hidden boss waiting for the right moment",
    ];

    private readonly string[] _messages;
    private readonly Random _random = new();

    public string Name => "lurk";

    public LurkCommand(string[]? messages = null)
    {
        _messages = messages is { Length: > 0 } ? messages : DefaultMessages;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string message = _messages[_random.Next(_messages.Length)]
            .Replace("{user}", context.UserName);
        return Task.FromResult(CommandResult.Ok(message));
    }
}
