namespace StarterPack.Core.Interfaces;

public interface IAiProvider
{
    bool IsAvailable { get; }
    Task<string?> EnhanceAsync(string prompt, string? systemPrompt = null, int maxTokens = 300, double temperature = 0.7, CancellationToken cancellationToken = default);
}
