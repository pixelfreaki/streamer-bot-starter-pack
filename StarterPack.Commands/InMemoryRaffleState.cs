using StarterPack.Core.Interfaces;

namespace StarterPack.Commands;

public class InMemoryRaffleState : IRaffleState
{
    private readonly HashSet<string> _joined = new(StringComparer.OrdinalIgnoreCase);
    private bool _isOpen;
    private string _title = string.Empty;
    private DateTime _openedAt;

    public bool IsOpen => _isOpen;
    public string Title => _title;
    public DateTime OpenedAt => _openedAt;
    public IReadOnlyList<string> JoinedUsers => _joined.ToList();

    public void Open(string title)
    {
        _title    = title;
        _openedAt = DateTime.UtcNow;
        _isOpen   = true;
        _joined.Clear();
    }

    public void Close() => _isOpen = false;

    public bool AddUser(string username)
    {
        if (!_isOpen) return false;
        return _joined.Add(username);
    }
}
