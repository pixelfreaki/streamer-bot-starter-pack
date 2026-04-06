using StarterPack.Core.Interfaces;

namespace StarterPack.Commands;

public class InMemoryChatActivityState : IChatActivityState
{
    private readonly TimeSpan _cooldown;
    private readonly Dictionary<string, DateTime> _lastTime = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, string> _lastMsg   = new(StringComparer.OrdinalIgnoreCase);

    public InMemoryChatActivityState(TimeSpan cooldown) => _cooldown = cooldown;

    public bool IsOnCooldown(string username) =>
        _lastTime.TryGetValue(username, out var t) && DateTime.UtcNow - t < _cooldown;

    public bool IsDuplicate(string username, string message) =>
        _lastMsg.TryGetValue(username, out var m) &&
        string.Equals(m, message, StringComparison.OrdinalIgnoreCase);

    public void Record(string username, string message)
    {
        _lastTime[username] = DateTime.UtcNow;
        _lastMsg[username]  = message;
    }
}
