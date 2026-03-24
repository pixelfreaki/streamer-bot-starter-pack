using System.Text.Json;
using Microsoft.Extensions.Configuration;
using StarterPack.AI.OpenAI;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

string baseDir = AppContext.BaseDirectory;

// Load layered config: appsettings.json < appsettings.Development.json
IConfiguration config = new ConfigurationBuilder()
    .SetBasePath(baseDir)
    .AddJsonFile("appsettings.json", optional: false)
    .AddJsonFile("appsettings.Development.json", optional: true)
    .Build();

string locale = config["App:DefaultLocale"] ?? "en";

// Load locale file
string localePath = Path.Combine(baseDir, "locales", $"{locale}.json");
if (!File.Exists(localePath))
{
    Console.WriteLine($"[warn] Locale file not found: {localePath} — falling back to en");
    localePath = Path.Combine(baseDir, "locales", "en.json");
}

using var localeDoc = JsonDocument.Parse(File.ReadAllText(localePath));
string[] eightBallResponses = localeDoc.RootElement
    .GetProperty("commands")
    .GetProperty("8ball")
    .GetProperty("responses")
    .EnumerateArray()
    .Select(x => x.GetString()!)
    .ToArray();

// Build AI provider (optional)
string? openAiKey = config["OpenAI:ApiKey"];
IAiProvider? aiProvider = !string.IsNullOrWhiteSpace(openAiKey) && openAiKey != "your_key_here"
    ? new OpenAiProvider(openAiKey)
    : null;

if (aiProvider is not null)
    Console.WriteLine("[OpenAI] Connected — responses will be enhanced");

// Register commands
var commands = new Dictionary<string, ICommand>(StringComparer.OrdinalIgnoreCase)
{
    ["8ball"] = new EightBallCommand(eightBallResponses, aiProvider, locale)
};

Console.WriteLine($"Streamer.bot Runner [{locale}] — type !<command> [input] or 'exit' to quit");
Console.WriteLine($"Available commands: {string.Join(", ", commands.Keys.Select(k => $"!{k}"))}");
Console.WriteLine();

while (true)
{
    Console.Write("> ");
    string? line = Console.ReadLine();

    if (line is null || line.Equals("exit", StringComparison.OrdinalIgnoreCase))
        break;

    if (!line.StartsWith('!'))
    {
        Console.WriteLine("Commands must start with !");
        continue;
    }

    string[] parts = line[1..].Split(' ', 2);
    string name = parts[0];
    string input = parts.Length > 1 ? parts[1] : string.Empty;

    if (!commands.TryGetValue(name, out ICommand? command))
    {
        Console.WriteLine($"Unknown command: !{name}");
        continue;
    }

    var context = new CommandContext { UserName = "local", Input = input };
    var result = await command.ExecuteAsync(context);

    Console.WriteLine(result.Success ? result.Message : $"[error] {result.Message}");
}
