using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class InMemoryRaffleHistory : IRaffleHistory
{
    private readonly List<RaffleSession> _sessions = new();

    public void Save(RaffleSession session) => _sessions.Add(session);

    public IReadOnlyList<RaffleSession> GetRecent(int count = 3) =>
        _sessions.AsEnumerable().Reverse().Take(count).ToList();
}
