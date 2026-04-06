namespace StarterPack.Core.Interfaces;

public interface IChatActivityState
{
    bool IsOnCooldown(string username);
    bool IsDuplicate(string username, string message);
    void Record(string username, string message);
}
