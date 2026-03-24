using System.Text;
using System.Text.Json;
using StarterPack.Core.Interfaces;

namespace StarterPack.AI.OpenAI;

public class OpenAiProvider : IAiProvider
{
    private const string ChatCompletionsUrl = "https://api.openai.com/v1/chat/completions";
    private const string Model = "gpt-4o-mini";

    private readonly string _apiKey;
    private readonly HttpClient _httpClient;

    public bool IsAvailable => !string.IsNullOrWhiteSpace(_apiKey);

    public OpenAiProvider(string apiKey, HttpClient? httpClient = null)
    {
        _apiKey = apiKey;
        _httpClient = httpClient ?? new HttpClient();
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiKey}");
    }

    public async Task<string?> EnhanceAsync(string prompt, CancellationToken cancellationToken = default)
    {
        if (!IsAvailable)
            return null;

        var body = JsonSerializer.Serialize(new
        {
            model = Model,
            messages = new[] { new { role = "user", content = prompt } },
            max_tokens = 100
        });

        using var content = new StringContent(body, Encoding.UTF8, "application/json");
        var response = await _httpClient.PostAsync(ChatCompletionsUrl, content, cancellationToken);
        response.EnsureSuccessStatusCode();

        using var doc = JsonDocument.Parse(await response.Content.ReadAsStringAsync(cancellationToken));
        return doc.RootElement
            .GetProperty("choices")[0]
            .GetProperty("message")
            .GetProperty("content")
            .GetString();
    }
}
