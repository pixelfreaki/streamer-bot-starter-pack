namespace StarterPack.Core.Interfaces;

public interface IStreamElementsService
{
    bool IsAvailable { get; }
    Task<(long Points, long Rank)?> GetUserPointsAsync(string username, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<(string Username, long Points)>> GetTopAsync(int limit = 5, CancellationToken cancellationToken = default);
}
