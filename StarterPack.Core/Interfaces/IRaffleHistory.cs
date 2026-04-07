using StarterPack.Core.Models;

namespace StarterPack.Core.Interfaces;

public interface IRaffleHistory
{
    void Save(RaffleSession session);
    IReadOnlyList<RaffleSession> GetRecent(int count = 3);
}
