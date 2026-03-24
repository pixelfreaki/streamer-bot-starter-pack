using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class FlipCoinCommand : ICommand
{
    private static readonly string[] DefaultHeads =
    [
        "🪙 {user} flipped a coin and it landed on... HEADS!",
        "🪙 The universe answered. It's HEADS for {user}!",
        "🪙 RNG activated — result: HEADS!",
        "🪙 The coin spun, thought about it… and chose HEADS!",
        "🪙 Fate confirmed: HEADS!",
        "🪙 Chaos approved. HEADS for {user}!",
        "🪙 {user}, this roll came with main quest energy. HEADS!",
        "🪙 Destiny spoiler: HEADS it is!",
        "🪙 The coin didn't glitch… landed on HEADS!",
        "🪙 Mystical signals detected — HEADS confirmed!",
    ];

    private static readonly string[] DefaultTails =
    [
        "🪙 {user} flipped a coin and it landed on... TAILS!",
        "🪙 The universe chose TAILS for {user}!",
        "🪙 RNG trolled a little — TAILS!",
        "🪙 The coin spun dramatically… and landed on TAILS!",
        "🪙 The pixels decided: TAILS!",
        "🪙 Hmm… weird side quest energy. TAILS for {user}!",
        "🪙 {user}, this smells like a plot twist. TAILS!",
        "🪙 Alternative destiny unlocked: TAILS!",
        "🪙 Minor chaos detected… result is TAILS!",
        "🪙 The coin took the most suspicious path: TAILS!",
    ];

    private static readonly string[] DefaultWin =
    [
        "✅ {user} called it! RNG approved.",
        "✅ Correct! The pixels align in your favor.",
        "✅ {user} read the timeline perfectly. Well played.",
        "✅ The universe agrees — you nailed it.",
        "✅ Chaos factor: zero. You got this right.",
        "✅ Main quest instincts confirmed. Nice one, {user}!",
        "✅ Fate validated. You got it!",
        "✅ The coin didn't betray you. Good call!",
        "✅ Mystical accuracy confirmed. You won!",
        "✅ Prediction locked in. Correct!",
    ];

    private static readonly string[] DefaultLoss =
    [
        "❌ {user} trusted fate… fate disagreed.",
        "❌ Wrong! The RNG showed no mercy.",
        "❌ The pixels say nope. Missed!",
        "❌ Side quest failed. Better luck next time, {user}.",
        "❌ Plot twist: you were wrong.",
        "❌ Chaos wins this round. You missed.",
        "❌ Alternative timeline unlocked — the one where you lose.",
        "❌ The universe had other plans. Missed!",
        "❌ Not this time, {user}. The coin had other ideas.",
        "❌ Unlucky roll. The RNG was not on your side.",
    ];

    private const string DefaultNoChoice = "⚠️ {user}, choose first: !flipcoin heads or !flipcoin tails";

    private readonly string[] _heads;
    private readonly string[] _tails;
    private readonly string[] _win;
    private readonly string[] _loss;
    private readonly string _noChoice;
    private readonly Random _random = new();

    public string Name => "flipcoin";

    public FlipCoinCommand(
        string[]? heads    = null,
        string[]? tails    = null,
        string[]? win      = null,
        string[]? loss     = null,
        string?   noChoice = null)
    {
        _heads    = heads    is { Length: > 0 } ? heads    : DefaultHeads;
        _tails    = tails    is { Length: > 0 } ? tails    : DefaultTails;
        _win      = win      is { Length: > 0 } ? win      : DefaultWin;
        _loss     = loss     is { Length: > 0 } ? loss     : DefaultLoss;
        _noChoice = noChoice ?? DefaultNoChoice;
    }

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string input = (context.Input ?? "").Trim().ToUpperInvariant();

        bool? userGuess = input switch
        {
            "HEAD"  or "HEADS" or "CARA"  => true,
            "TAIL"  or "TAILS" or "COROA" => false,
            _ => null,
        };

        if (userGuess is null)
            return Task.FromResult(CommandResult.Ok(_noChoice.Replace("{user}", context.UserName)));

        bool isHeads   = _random.Next(2) == 0;
        string[] pool  = isHeads ? _heads : _tails;
        string coinMsg = pool[_random.Next(pool.Length)].Replace("{user}", context.UserName);

        string[] outcomePool = (isHeads == userGuess) ? _win : _loss;
        string outcome = outcomePool[_random.Next(outcomePool.Length)].Replace("{user}", context.UserName);

        return Task.FromResult(CommandResult.Ok($"{coinMsg} {outcome}"));
    }
}
