namespace StarterPack.Core.Interfaces;

public interface IAiProvider
{
    bool IsAvailable { get; }
    Task<string?> EnhanceAsync(string prompt, CancellationToken cancellationToken = default);
}
