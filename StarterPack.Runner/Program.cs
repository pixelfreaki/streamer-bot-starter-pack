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
var commandsElement = localeDoc.RootElement.GetProperty("commands");

string[] eightBallResponses = commandsElement
    .GetProperty("8ball")
    .GetProperty("responses")
    .EnumerateArray()
    .Select(x => x.GetString()!)
    .ToArray();

var flipcoinElement     = commandsElement.GetProperty("flipcoin");
string[] flipCoinHeads    = flipcoinElement.GetProperty("heads").EnumerateArray().Select(x => x.GetString()!).ToArray();
string[] flipCoinTails    = flipcoinElement.GetProperty("tails").EnumerateArray().Select(x => x.GetString()!).ToArray();
string[] flipCoinWin      = flipcoinElement.GetProperty("win").EnumerateArray().Select(x => x.GetString()!).ToArray();
string[] flipCoinLoss     = flipcoinElement.GetProperty("loss").EnumerateArray().Select(x => x.GetString()!).ToArray();
string   flipCoinNoChoice = flipcoinElement.GetProperty("noChoice").GetString()!;

var jokeElement = commandsElement.GetProperty("joke");
string[] jokeFallbacks = jokeElement
    .GetProperty("responses")
    .EnumerateArray()
    .Select(x => x.GetString()!)
    .ToArray();
string jokeEmptyPrompt = jokeElement.GetProperty("emptyPrompt").GetString()!;
string jokeTopicPrompt = jokeElement.GetProperty("topicPrompt").GetString()!;

string[] fortuneResponses = commandsElement
    .GetProperty("fortune")
    .GetProperty("responses")
    .EnumerateArray()
    .Select(x => x.GetString()!)
    .ToArray();

string[] lurkMessages = commandsElement
    .GetProperty("lurk")
    .GetProperty("responses")
    .EnumerateArray()
    .Select(x => x.GetString()!)
    .ToArray();

var clipElement   = commandsElement.GetProperty("clip");
string clipSuccess = clipElement.GetProperty("success").GetString()!;
string clipFailure = clipElement.GetProperty("failure").GetString()!;

string commandsFormat     = commandsElement.GetProperty("commands").GetProperty("message").GetString()!;
string pcMessage          = commandsElement.GetProperty("pc").GetProperty("message").GetString()!;
string gearMessage        = commandsElement.GetProperty("gear").GetProperty("message").GetString()!;
string peripheralsMessage = commandsElement.GetProperty("peripherals").GetProperty("message").GetString()!;

// shoutout
var shoutoutElement = commandsElement.GetProperty("shoutout");
// (no runtime messages needed for shoutout stub)

// setgame
var setgameElement    = commandsElement.GetProperty("setgame");
string setgameNotFound     = setgameElement.GetProperty("notFound").GetString()!;
string setgameNotAvailable = setgameElement.GetProperty("notAvailable").GetString()!;

// accountage
var accountageElement    = commandsElement.GetProperty("accountage");
string accountageMessage     = accountageElement.GetProperty("message").GetString()!;
string accountageNotAvailable = accountageElement.GetProperty("notAvailable").GetString()!;

// time
var timeElement    = commandsElement.GetProperty("time");
string timeTwitch  = timeElement.GetProperty("twitch").GetString()!;
string timeKick    = timeElement.GetProperty("kick").GetString()!;
string timeYouTube = timeElement.GetProperty("youtube").GetString()!;

// sacrifice
var sacrificeElement    = commandsElement.GetProperty("sacrifice");
string sacrificeTwitch  = sacrificeElement.GetProperty("twitch").GetString()!;
string sacrificeKick    = sacrificeElement.GetProperty("kick").GetString()!;
string sacrificeYouTube = sacrificeElement.GetProperty("youtube").GetString()!;

// russianroulette
var rrElement    = commandsElement.GetProperty("russianroulette");
string rrDies    = rrElement.GetProperty("dies").GetString()!;
string rrLives   = rrElement.GetProperty("lives").GetString()!;

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
    ["8ball"]    = new EightBallCommand(eightBallResponses, aiProvider, locale),
    ["flipcoin"] = new FlipCoinCommand(flipCoinHeads, flipCoinTails, flipCoinWin, flipCoinLoss, flipCoinNoChoice),
    ["joke"]     = new JokeCommand(jokeFallbacks, aiProvider, locale, jokeEmptyPrompt, jokeTopicPrompt),
    ["fortune"]  = new FortuneCommand(fortuneResponses),
    ["lurk"]     = new LurkCommand(lurkMessages),
    ["clip"]           = new ClipCommand(clipSuccess, clipFailure,
                           createClip: () => "https://clips.twitch.tv/demo-clip"),
    ["pc"]             = new InfoCommand("pc",          pcMessage),
    ["gear"]           = new InfoCommand("gear",        gearMessage),
    ["peripherals"]    = new InfoCommand("peripherals", peripheralsMessage),
    ["shoutout"]       = new ShoutoutCommand(),
    ["settitle"]       = new SetTitleCommand(),
    ["setgame"]        = new SetGameCommand(setgameNotFound, setgameNotAvailable),
    ["accountage"]     = new AccountAgeCommand(accountageMessage, accountageNotAvailable),
    ["followage"]      = new FollowAgeCommand(),
    ["uptime"]         = new UptimeCommand(),
    ["time"]           = new TimeCommand(timeTwitch, timeKick, timeYouTube),
    ["translate"]      = new TranslateCommand(),
    ["sacrifice"]      = new SacrificeCommand(sacrificeTwitch, sacrificeKick, sacrificeYouTube),
    ["russianroulette"] = new RussianRouletteCommand(rrDies, rrLives),
    ["scene"]          = new SceneCommand(),
};

string cmdList = string.Join(" ", commands.Keys.Order().Select(k => $"!{k}"));
commands["commands"] = new InfoCommand("commands", commandsFormat.Replace("{commands}", cmdList));

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
