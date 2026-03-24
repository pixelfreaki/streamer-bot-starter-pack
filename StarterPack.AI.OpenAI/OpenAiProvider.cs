using StarterPack.Core.Interfaces;

namespace StarterPack.AI.OpenAI;

public class OpenAiProvider : IAiProvider
{
    private readonly string _apiKey;
    private readonly HttpClient _httpClient;

    public bool IsAvailable => !string.IsNullOrWhiteSpace(_apiKey);

    public OpenAiProvider(string apiKey, HttpClient? httpClient = null)
    {
        _apiKey = apiKey;
        _httpClient = httpClient ?? new HttpClient();
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiKey}");
    }

    public Task<string?> EnhanceAsync(string prompt, CancellationToken cancellationToken = default)
    {
        if (!IsAvailable)
            return Task.FromResult<string?>(null);

        // TODO: implement OpenAI chat completion
        throw new NotImplementedException();
    }
}
