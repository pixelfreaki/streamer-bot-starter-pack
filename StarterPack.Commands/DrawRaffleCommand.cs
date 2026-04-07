using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

public class DrawRaffleCommand : ICommand
{
    private readonly IRaffleState _state;
    private readonly IRaffleHistory _history;
    private readonly IStreamElementsService? _se;
    private readonly string _starting;
    private readonly string _top5Winner;
    private readonly string _top10Winner;
    private readonly string _bonusWinner;
    private readonly string _noJoined;
    private readonly string _top5NoLeaderboard;
    private readonly string _top10NoWinner;
    private readonly string _top10NotEnough;
    private readonly string _notOpen;
    private readonly string _leaderboardError;

    public string Name => "drawRaffle";

    public DrawRaffleCommand(
        string starting,
        string top5Winner,
        string top10Winner,
        string bonusWinner,
        string noJoined,
        string top5NoLeaderboard,
        string top10NoWinner,
        string top10NotEnough,
        string notOpen,
        string leaderboardError,
        IRaffleState state,
        IRaffleHistory history,
        IStreamElementsService? se = null)
    {
        _starting          = starting;
        _top5Winner        = top5Winner;
        _top10Winner       = top10Winner;
        _bonusWinner       = bonusWinner;
        _noJoined          = noJoined;
        _top5NoLeaderboard = top5NoLeaderboard;
        _top10NoWinner     = top10NoWinner;
        _top10NotEnough    = top10NotEnough;
        _notOpen           = notOpen;
        _leaderboardError  = leaderboardError;
        _state             = state;
        _history           = history;
        _se                = se;
    }

    public async Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        if (!_state.IsOpen)
            return CommandResult.Fail(_notOpen);

        string title      = _state.Title;
        DateTime openedAt = _state.OpenedAt;
        var joined        = _state.JoinedUsers.ToList();
        _state.Close();

        IReadOnlyList<(string Username, long Points)> leaderboard =
            Array.Empty<(string, long)>();

        if (_se is { IsAvailable: true })
        {
            try { leaderboard = await _se.GetTopAsync(50, cancellationToken); }
            catch { /* fall through to draws with empty leaderboard */ }
        }

        var rng       = new Random();
        var joinedSet = new HashSet<string>(joined, StringComparer.OrdinalIgnoreCase);

        // ── Top 5 draw: random from positions 1–5 in leaderboard ──────────────
        // Does not require !join — always runs when leaderboard is available.
        string? top5 = null;
        if (leaderboard.Count > 0)
        {
            var pool = leaderboard.Take(5).Select(e => e.Username).ToList();
            top5 = pool[rng.Next(pool.Count)];
        }

        // ── Top 10 draw: walk leaderboard, collect up to 10 joined users ──────
        string? top10 = null;
        int top10PoolSize = 0;
        if (joined.Count > 0 && leaderboard.Count > 0)
        {
            var eligible = leaderboard
                .Where(e => joinedSet.Contains(e.Username))
                .Take(10)
                .Select(e => e.Username)
                .ToList();
            top10PoolSize = eligible.Count;
            if (eligible.Count > 0)
                top10 = eligible[rng.Next(eligible.Count)];
        }

        // ── Bonus draw: random from all joined users ───────────────────────────
        string? bonus = joined.Count > 0 ? joined[rng.Next(joined.Count)] : null;

        // ── Persist session to history ─────────────────────────────────────────
        _history.Save(new RaffleSession(
            Title:       title,
            Date:        openedAt,
            JoinedCount: joined.Count,
            Top5Winner:  top5,
            Top10Winner: top10,
            BonusWinner: bonus
        ));

        var lines = new List<string> { _starting };

        // Top 5 — always report outcome
        if (top5 is not null)
            lines.Add(_top5Winner.Replace("{user}", top5));
        else
            lines.Add(_top5NoLeaderboard);

        if (joined.Count == 0)
        {
            lines.Add(_noJoined);
        }
        else
        {
            // Top 10 — report winner, partial-pool warning, or no-qualifier message
            if (top10PoolSize > 0 && top10PoolSize < 10)
                lines.Add(_top10NotEnough.Replace("{count}", top10PoolSize.ToString()));
            if (top10 is not null)
                lines.Add(_top10Winner.Replace("{user}", top10));
            else if (leaderboard.Count > 0)
                lines.Add(_top10NoWinner);

            // Bonus — always has a winner when anyone joined
            lines.Add(_bonusWinner.Replace("{user}", bonus!));
        }

        return CommandResult.Ok(string.Join("\n", lines));
    }
}
