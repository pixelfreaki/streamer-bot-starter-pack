using System.Text.Json;
using StarterPack.Core.Interfaces;

namespace StarterPack.StreamElements;

public class StreamElementsService : IStreamElementsService, IDisposable
{
    private const string BaseUrl = "https://api.streamelements.com/kappa/v2";

    private readonly string _channel;
    private readonly HttpClient _httpClient;

    public bool IsAvailable => !string.IsNullOrWhiteSpace(_channel);

    public StreamElementsService(string jwtToken, string channel, HttpClient? httpClient = null)
    {
        _channel = channel;
        _httpClient = httpClient ?? new HttpClient();

        if (!string.IsNullOrWhiteSpace(jwtToken))
            _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {jwtToken}");
    }

    public async Task<(long Points, long Rank)?> GetUserPointsAsync(string username, CancellationToken cancellationToken = default)
    {
        if (!IsAvailable) return null;

        var url = $"{BaseUrl}/points/{_channel}/{Uri.EscapeDataString(username)}";
        var response = await _httpClient.GetAsync(url, cancellationToken);

        if (!response.IsSuccessStatusCode) return null;

        using var doc = JsonDocument.Parse(await response.Content.ReadAsStringAsync(cancellationToken));
        var root = doc.RootElement;

        long points = root.TryGetProperty("points", out var p) ? p.GetInt64() : 0;
        long rank   = root.TryGetProperty("rank",   out var r) ? r.GetInt64() : 0;

        return (points, rank);
    }

    public async Task<IReadOnlyList<(string Username, long Points)>> GetTopAsync(int limit = 5, CancellationToken cancellationToken = default)
    {
        if (!IsAvailable) return [];

        var url = $"{BaseUrl}/points/{_channel}/top?limit={limit}";
        var response = await _httpClient.GetAsync(url, cancellationToken);
        var body = await response.Content.ReadAsStringAsync(cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            Console.Error.WriteLine($"[SE] GET {url} → {(int)response.StatusCode} {body}");
            return [];
        }

        Console.Error.WriteLine($"[SE] GET {url} → {body}");

        using var doc = JsonDocument.Parse(body);

        if (!doc.RootElement.TryGetProperty("users", out var users))
            return [];

        return users.EnumerateArray()
            .Select(u => (
                Username: u.TryGetProperty("username", out var un) ? un.GetString() ?? string.Empty : string.Empty,
                Points:   u.TryGetProperty("points",   out var pts) ? pts.GetInt64() : 0L
            ))
            .Where(u => !string.IsNullOrEmpty(u.Username))
            .ToList();
    }

    public void Dispose() => _httpClient.Dispose();
}
