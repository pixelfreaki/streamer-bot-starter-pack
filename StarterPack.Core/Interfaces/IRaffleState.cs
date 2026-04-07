namespace StarterPack.Core.Interfaces;

public interface IRaffleState
{
    bool IsOpen { get; }
    string Title { get; }
    DateTime OpenedAt { get; }
    IReadOnlyList<string> JoinedUsers { get; }

    void Open(string title);
    void Close();

    /// <summary>Returns false if raffle is closed or user already joined.</summary>
    bool AddUser(string username);
}
