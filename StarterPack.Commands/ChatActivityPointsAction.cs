using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class ChatActivityPointsAction
{
    public enum Rejection
    {
        None,
        IsCommand,
        TooShort,
        IsBot,
        OnCooldown,
        DuplicateMessage,
        EmoteOnly
    }

    // ── Defaults ──────────────────────────────────────────────────────────────

    public static readonly IReadOnlySet<string> DefaultBots =
        new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "nightbot", "streamelements", "streamlabs", "moobot",
            "fossabot", "wizebot", "botisimo", "commanderroot",
            "stay_hydrated_bot", "restreambot", "pokemoncommunitygame",
            "kofistreambot", "streamholics"
        };

    public static readonly IReadOnlySet<string> DefaultBttvEmotes =
        new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            // Globais comuns BTTV / FFZ / 7TV
            "OMEGALUL", "PogU", "PauseChamp", "monkaS", "monkaW",
            "LULW", "Clap", "GIGACHAD", "Pog", "FeelsBadMan",
            "FeelsGoodMan", "HYPERS", "widepeepoHappy", "PepeLaugh",
            "catJAM", "NODDERS", "COPIUM", "Sadge", "EZ", "PeepoClap",
            "peepoHappy", "NOTED", "Aware", "forsenCD", "TriHard",
            "WeirdChamp", "BASED", "OMEGADANCE", "peepoLeave", "peepoArrive"
        };

    // ── Fields ────────────────────────────────────────────────────────────────

    private readonly int _minLength;
    private readonly int _points;
    private readonly IReadOnlySet<string> _bots;
    private readonly IReadOnlySet<string> _bttvEmotes;
    private readonly IChatActivityState _state;
    private readonly IStreamElementsService? _se;

    // ── Constructor ───────────────────────────────────────────────────────────

    public ChatActivityPointsAction(
        int minLength,
        int points,
        IReadOnlySet<string>? bots,
        IReadOnlySet<string>? bttvEmotes,
        IChatActivityState state,
        IStreamElementsService? se = null)
    {
        _minLength  = minLength;
        _points     = points;
        _bots       = bots       ?? DefaultBots;
        _bttvEmotes = bttvEmotes ?? DefaultBttvEmotes;
        _state      = state;
        _se         = se;
    }

    // ── Public API ────────────────────────────────────────────────────────────

    public async Task<(bool Success, Rejection Reason)> ProcessAsync(
        ChatMessage message,
        CancellationToken cancellationToken = default)
    {
        var rejection = Filter(message);
        if (rejection != Rejection.None)
            return (false, rejection);

        if (_se is { IsAvailable: true })
        {
            bool ok = await _se.AddPointsAsync(message.Username, _points, cancellationToken);
            if (!ok) return (false, Rejection.None);
        }

        _state.Record(message.Username, message.Text);
        return (true, Rejection.None);
    }

    // ── Filter (pure — no side effects, fully testable) ───────────────────────

    public Rejection Filter(ChatMessage message)
    {
        if (message.Text.StartsWith('!'))                    return Rejection.IsCommand;
        if (message.Text.Trim().Length < _minLength)         return Rejection.TooShort;
        if (_bots.Contains(message.Username))                return Rejection.IsBot;
        if (_state.IsOnCooldown(message.Username))           return Rejection.OnCooldown;
        if (_state.IsDuplicate(message.Username, message.Text)) return Rejection.DuplicateMessage;
        if (IsEmoteOnly(message))                            return Rejection.EmoteOnly;
        return Rejection.None;
    }

    // ── Emote-only detection ──────────────────────────────────────────────────

    private bool IsEmoteOnly(ChatMessage message)
    {
        var words = message.Text.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (words.Length == 0) return false;

        // Native Twitch emotes: Streamer.bot provides emoteCount
        if (message.EmoteCount > 0 && message.EmoteCount >= words.Length) return true;

        // Same word repeated: "KEKW KEKW KEKW", "LUL LUL"
        var unique = new HashSet<string>(words, StringComparer.OrdinalIgnoreCase);
        if (unique.Count == 1 && words.Length >= 2) return true;

        // All words are known BTTV / FFZ / 7TV emotes
        if (words.All(w => _bttvEmotes.Contains(w))) return true;

        return false;
    }
}
