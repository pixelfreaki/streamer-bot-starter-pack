using StarterPack.Core.Interfaces;

namespace StarterPack.AI.AiLicia;

public class AiLiciaProvider : IAiProvider
{
    private readonly string _apiKey;
    private readonly HttpClient _httpClient;

    public bool IsAvailable => !string.IsNullOrWhiteSpace(_apiKey);

    public AiLiciaProvider(string apiKey, string baseUrl, HttpClient? httpClient = null)
    {
        _apiKey = apiKey;
        _httpClient = httpClient ?? new HttpClient();
        _httpClient.BaseAddress = new Uri(baseUrl);
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiKey}");
    }

    public Task<string?> EnhanceAsync(string prompt, string? systemPrompt = null, CancellationToken cancellationToken = default)
    {
        if (!IsAvailable)
            return Task.FromResult<string?>(null);

        // TODO: implement AI_Licia generation call via /v1/events/generations
        throw new NotImplementedException();
    }
}
