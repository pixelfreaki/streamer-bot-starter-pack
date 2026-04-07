using System.Text.Json;
using Microsoft.Extensions.Configuration;
using StarterPack.AI.AiLicia;
using StarterPack.AI.OpenAI;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;
using StarterPack.StreamElements;

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

// Build AI_Licia provider (optional)
string? aiLiciaKey     = config["AiLicia:ApiKey"];
string? aiLiciaChannel = config["AiLicia:ChannelName"];
string  aiLiciaUrl     = config["AiLicia:BaseUrl"] ?? "https://api.getailicia.com";
using AiLiciaProvider aiLicia =
    !string.IsNullOrWhiteSpace(aiLiciaKey)     && aiLiciaKey     != "your_key_here" &&
    !string.IsNullOrWhiteSpace(aiLiciaChannel) && aiLiciaChannel != "your_channel_here"
        ? new AiLiciaProvider(aiLiciaKey, aiLiciaChannel, aiLiciaUrl)
        : new AiLiciaProvider(string.Empty, string.Empty, aiLiciaUrl);

if (aiLicia.IsAvailable)
    Console.WriteLine("[AI_Licia] Connected — persona commands enabled");

// Build chat activity action
var chatState  = new InMemoryChatActivityState(TimeSpan.FromSeconds(30));
// seService wired below after it is created

// Build StreamElements service (optional)
string? seJwt     = config["StreamElements:JwtToken"];
string? seChannel = config["StreamElements:Channel"];
StreamElementsService? seService =
    !string.IsNullOrWhiteSpace(seJwt)     && seJwt     != "your_jwt_token_here" &&
    !string.IsNullOrWhiteSpace(seChannel) && seChannel != "your_channel_name_here"
        ? new StreamElementsService(seJwt, seChannel)
        : null;

if (seService?.IsAvailable == true)
    Console.WriteLine("[StreamElements] Connected — !points and !top enabled");

var chatAction = new ChatActivityPointsAction(
    minLength:  3,
    points:     2,
    bots:       null,   // uses DefaultBots
    bttvEmotes: null,   // uses DefaultBttvEmotes
    state:      chatState,
    se:         seService);

// Load AI_Licia command locale strings
var oracleElement   = commandsElement.GetProperty("oracle");
string[] oracleStyles   = oracleElement.GetProperty("styles").EnumerateArray().Select(x => x.GetString()!).ToArray();
string[] oracleFallback = oracleElement.GetProperty("fallback").EnumerateArray().Select(x => x.GetString()!).ToArray();
string   oracleNoInput  = oracleElement.GetProperty("noInput").GetString()!;

var horoscopeElement     = commandsElement.GetProperty("horoscope");
string[] horoscopeStyles   = horoscopeElement.GetProperty("styles").EnumerateArray().Select(x => x.GetString()!).ToArray();
string[] horoscopeFallback = horoscopeElement.GetProperty("fallback").EnumerateArray().Select(x => x.GetString()!).ToArray();
string   horoscopeNoInput  = horoscopeElement.GetProperty("noInput").GetString()!;

var curseElement     = commandsElement.GetProperty("curse");
string[] curseStyles   = curseElement.GetProperty("styles").EnumerateArray().Select(x => x.GetString()!).ToArray();
string[] curseFallback = curseElement.GetProperty("fallback").EnumerateArray().Select(x => x.GetString()!).ToArray();
string   curseNoInput  = curseElement.GetProperty("noInput").GetString()!;

var omenElement     = commandsElement.GetProperty("omen");
string[] omenStyles   = omenElement.GetProperty("styles").EnumerateArray().Select(x => x.GetString()!).ToArray();
string[] omenFallback = omenElement.GetProperty("fallback").EnumerateArray().Select(x => x.GetString()!).ToArray();

var tarotElement     = commandsElement.GetProperty("tarot");
string[] tarotStyles   = tarotElement.GetProperty("styles").EnumerateArray().Select(x => x.GetString()!).ToArray();
string[] tarotFallback = tarotElement.GetProperty("fallback").EnumerateArray().Select(x => x.GetString()!).ToArray();

var judgeElement     = commandsElement.GetProperty("judge");
string[] judgeStyles   = judgeElement.GetProperty("styles").EnumerateArray().Select(x => x.GetString()!).ToArray();
string[] judgeFallback = judgeElement.GetProperty("fallback").EnumerateArray().Select(x => x.GetString()!).ToArray();
string   judgeNoInput  = judgeElement.GetProperty("noInput").GetString()!;

var hexElement     = commandsElement.GetProperty("hex");
string[] hexStyles   = hexElement.GetProperty("styles").EnumerateArray().Select(x => x.GetString()!).ToArray();
string[] hexFallback = hexElement.GetProperty("fallback").EnumerateArray().Select(x => x.GetString()!).ToArray();
string   hexNoInput  = hexElement.GetProperty("noInput").GetString()!;

// points
var pointsElement      = commandsElement.GetProperty("points");
string pointsMessage      = pointsElement.GetProperty("message").GetString()!;
string pointsNotAvailable = pointsElement.GetProperty("notAvailable").GetString()!;
string pointsNotFound     = pointsElement.GetProperty("notFound").GetString()!;

// top
var topElement      = commandsElement.GetProperty("top");
string topHeader      = topElement.GetProperty("header").GetString()!;
string topEntry       = topElement.GetProperty("entry").GetString()!;
string topNotAvailable = topElement.GetProperty("notAvailable").GetString()!;

// raffle
var raffleElement       = commandsElement.GetProperty("raffle");
var joinEl              = raffleElement.GetProperty("join");
string joinJoined           = joinEl.GetProperty("joined").GetString()!;
string joinAlreadyJoined    = joinEl.GetProperty("alreadyJoined").GetString()!;
string joinNotOpen          = joinEl.GetProperty("notOpen").GetString()!;
var openEl              = raffleElement.GetProperty("openRaffle");
string openOpened           = openEl.GetProperty("opened").GetString()!;
string openNoTitle          = openEl.GetProperty("noTitle").GetString()!;
var closeEl             = raffleElement.GetProperty("closeRaffle");
string closeClosed          = closeEl.GetProperty("closed").GetString()!;
string closeNotOpen         = closeEl.GetProperty("notOpen").GetString()!;
var drawEl              = raffleElement.GetProperty("drawRaffle");
string drawStarting         = drawEl.GetProperty("starting").GetString()!;
string drawTop5Winner       = drawEl.GetProperty("top5Winner").GetString()!;
string drawRankedWinner     = drawEl.GetProperty("rankedWinner").GetString()!;
string drawExtraWinner      = drawEl.GetProperty("extraWinner").GetString()!;
string drawNoJoined         = drawEl.GetProperty("noJoined").GetString()!;
string drawNotOpen          = drawEl.GetProperty("notOpen").GetString()!;
string drawLeaderboardError = drawEl.GetProperty("leaderboardError").GetString()!;
var showEl              = raffleElement.GetProperty("showPreviousRaffle");
string showTemplate         = showEl.GetProperty("template").GetString()!;
string showNoHistory        = showEl.GetProperty("noHistory").GetString()!;

// Build shared raffle state and history
IRaffleState raffleState     = new InMemoryRaffleState();
string raffleHistoryPath     = Path.Combine(baseDir, "raffle_history.json");
IRaffleHistory raffleHistory = new JsonFileRaffleHistory(raffleHistoryPath);

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
    ["oracle"]         = new OracleCommand(oracleStyles, oracleFallback, oracleNoInput, aiLicia.IsAvailable ? aiLicia : null),
    ["horoscope"]      = new HoroscopeCommand(horoscopeStyles, horoscopeFallback, horoscopeNoInput, aiLicia.IsAvailable ? aiLicia : null),
    ["curse"]          = new CurseCommand(curseStyles, curseFallback, curseNoInput, aiLicia.IsAvailable ? aiLicia : null),
    ["omen"]           = new OmenCommand(omenStyles, omenFallback, aiLicia.IsAvailable ? aiLicia : null),
    ["tarot"]          = new TarotCommand(tarotStyles, tarotFallback, aiLicia.IsAvailable ? aiLicia : null),
    ["judge"]          = new JudgeCommand(judgeStyles, judgeFallback, judgeNoInput, aiLicia.IsAvailable ? aiLicia : null),
    ["hex"]            = new HexCommand(hexStyles, hexFallback, hexNoInput, aiLicia.IsAvailable ? aiLicia : null),
    ["points"]         = new PointsCommand(pointsMessage, pointsNotAvailable, pointsNotFound, seService),
    ["top"]            = new TopCommand("top",   topHeader, topEntry, topNotAvailable, 5,  seService),
    ["top10"]          = new TopCommand("top10", topHeader, topEntry, topNotAvailable, 10, seService),
    ["join"]           = new JoinCommand(joinJoined, joinAlreadyJoined, joinNotOpen, raffleState),
    ["openraffle"]     = new OpenRaffleCommand(openOpened, openNoTitle, raffleState),
    ["closeraffle"]    = new CloseRaffleCommand(closeClosed, closeNotOpen, raffleState),
    ["drawraffle"]     = new DrawRaffleCommand(
                             drawStarting, drawTop5Winner, drawRankedWinner, drawExtraWinner,
                             drawNoJoined, drawNotOpen, drawLeaderboardError,
                             raffleState, raffleHistory, seService),
    ["showpreviousraffle"] = new ShowPreviousRaffleCommand(showTemplate, showNoHistory, raffleHistory),
};

string cmdList = string.Join(" ", commands.Keys.Order().Select(k => $"!{k}"));
commands["commands"] = new InfoCommand("commands", commandsFormat.Replace("{commands}", cmdList));

Console.WriteLine($"Streamer.bot Runner [{locale}] — type !<command> [input] or 'exit' to quit");
Console.WriteLine($"Available commands: {string.Join(", ", commands.Keys.Select(k => $"!{k}"))}");
Console.WriteLine("Chat simulation: type  chat [username] message  to test activity points");
Console.WriteLine("Raffle simulation: !openRaffle <title>  |  !join  |  !drawRaffle  |  !showPreviousRaffle");
Console.WriteLine();

while (true)
{
    Console.Write("> ");
    string? line = Console.ReadLine();

    if (line is null || line.Equals("exit", StringComparison.OrdinalIgnoreCase))
        break;

    // ── Chat simulation: "chat [username] message" ─────────────────────
    if (line.StartsWith("chat ", StringComparison.OrdinalIgnoreCase))
    {
        var chatParts = line[5..].Trim().Split(' ', 2);
        string chatUser, chatText;

        if (chatParts.Length == 2 && !chatParts[0].Contains(' '))
        {
            chatUser = chatParts[0];
            chatText = chatParts[1];
        }
        else
        {
            chatUser = "local";
            chatText = line[5..].Trim();
        }

        var chatMsg = new ChatMessage(chatUser, chatText);
        var (success, reason) = await chatAction.ProcessAsync(chatMsg);

        string status = success
            ? $"✅ +2 pts"
            : $"❌ {reason}";

        Console.WriteLine($"[chat] {chatUser}: \"{chatText}\" → {status}");
        continue;
    }

    if (!line.StartsWith('!'))
    {
        Console.WriteLine("Commands must start with !   |   Chat sim: chat [user] message");
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

    if (!result.Success)
        Console.WriteLine($"[error] {result.Message}");
    else if (result.Message == string.Empty)
        Console.WriteLine("[AI_Licia triggered — response will appear in chat]");
    else
        Console.WriteLine(result.Message);
}
