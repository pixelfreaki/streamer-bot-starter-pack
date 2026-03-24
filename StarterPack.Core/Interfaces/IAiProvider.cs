namespace StarterPack.Core.Interfaces;

public interface IAiProvider
{
    bool IsAvailable { get; }
    Task<string?> EnhanceAsync(string prompt, string? systemPrompt = null, CancellationToken cancellationToken = default);
}
