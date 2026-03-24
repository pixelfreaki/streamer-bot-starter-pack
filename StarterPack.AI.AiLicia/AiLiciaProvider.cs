using System.Text;
using System.Text.Json;
using StarterPack.Core.Interfaces;

namespace StarterPack.AI.AiLicia;

public class AiLiciaProvider : IAiProvider
{
    private readonly string _apiKey;
    private readonly string _channelName;
    private readonly HttpClient _httpClient;

    public bool IsAvailable => !string.IsNullOrWhiteSpace(_apiKey) && !string.IsNullOrWhiteSpace(_channelName);

    public AiLiciaProvider(string apiKey, string channelName, string baseUrl, HttpClient? httpClient = null)
    {
        _apiKey = apiKey;
        _channelName = channelName;
        _httpClient = httpClient ?? new HttpClient();
        _httpClient.BaseAddress = new Uri(baseUrl);
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiKey}");
    }

    public async Task<string?> EnhanceAsync(string prompt, string? systemPrompt = null, int maxTokens = 300, double temperature = 0.7, CancellationToken cancellationToken = default)
    {
        if (!IsAvailable)
            return null;

        if (systemPrompt != null)
        {
            var contextPayload = new
            {
                eventType = "GAME_EVENT",
                data = new { channelName = _channelName, content = systemPrompt, ttl = 60 }
            };
            var contextJson = JsonSerializer.Serialize(contextPayload);
            await _httpClient.PostAsync("/v1/events",
                new StringContent(contextJson, Encoding.UTF8, "application/json"),
                cancellationToken);
        }

        var genContent = prompt.Length > 300 ? prompt[..300] : prompt;
        var genPayload = new
        {
            eventType = "GAME_EVENT",
            data = new { channelName = _channelName, content = genContent }
        };
        var genJson = JsonSerializer.Serialize(genPayload);
        await _httpClient.PostAsync("/v1/events/generations",
            new StringContent(genJson, Encoding.UTF8, "application/json"),
            cancellationToken);

        // AI_Licia sends the response to chat directly — no text to return
        return null;
    }
}
