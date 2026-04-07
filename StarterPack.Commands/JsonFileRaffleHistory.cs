using System.Text.Json;
using System.Text.Json.Serialization;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class JsonFileRaffleHistory : IRaffleHistory
{
    private readonly string _filePath;
    private static readonly JsonSerializerOptions _opts = new()
    {
        WriteIndented = true,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    };

    public JsonFileRaffleHistory(string filePath) => _filePath = filePath;

    public void Save(RaffleSession session)
    {
        var sessions = Load();
        sessions.Add(session);
        string dir = Path.GetDirectoryName(_filePath)!;
        if (!string.IsNullOrEmpty(dir))
            Directory.CreateDirectory(dir);
        File.WriteAllText(_filePath, JsonSerializer.Serialize(sessions, _opts));
    }

    public IReadOnlyList<RaffleSession> GetRecent(int count = 3)
    {
        var sessions = Load();
        return sessions.AsEnumerable().Reverse().Take(count).ToList();
    }

    private List<RaffleSession> Load()
    {
        if (!File.Exists(_filePath)) return new List<RaffleSession>();
        try
        {
            var text = File.ReadAllText(_filePath);
            return JsonSerializer.Deserialize<List<RaffleSession>>(text, _opts) ?? new List<RaffleSession>();
        }
        catch
        {
            return new List<RaffleSession>();
        }
    }
}
