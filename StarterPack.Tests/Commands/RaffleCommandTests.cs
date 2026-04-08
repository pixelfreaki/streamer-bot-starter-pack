using Moq;
using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class RaffleCommandTests
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static InMemoryRaffleState State() => new();
    private static InMemoryRaffleHistory History() => new();
    private static CommandContext Ctx(string user, string input = "") =>
        new() { UserName = user, Input = input };

    private static JoinCommand Join(IRaffleState state) =>
        new("@{user} joined!", "@{user} already in.", "No raffle open.", state);

    private static OpenRaffleCommand Open(IRaffleState state) =>
        new("Raffle open: {title}!", "Usage: !openRaffle <title>", "Already open: {title}.", state);

    private static CloseRaffleCommand Close(IRaffleState state) =>
        new("Raffle closed.", "No raffle to close.", state);

    private static DrawRaffleCommand Draw(IRaffleState state, IRaffleHistory history,
        IStreamElementsService? se = null) =>
        new("Starting...", "Top5: @{user}", "Top10: @{user}", "Bonus: @{user}",
            "No joined.", "No leaderboard.", "No top10 winner.", "Only {count} joined.",
            "Not open.", "Leaderboard error.", state, history, se);

    private static ShowPreviousRaffleCommand Show(IRaffleHistory history) =>
        new("Last: {title} | {date} | Top5: {top5} | Top10: {top10} | Bonus: {bonus}",
            "No history.", history);

    // ── InMemoryRaffleState ───────────────────────────────────────────────────

    [Fact]
    public void State_Open_SetsPropertiesAndClearsUsers()
    {
        var state = State();
        state.Open("My Raffle");
        state.AddUser("user1");

        state.Open("New Raffle"); // re-open resets joined
        Assert.True(state.IsOpen);
        Assert.Equal("New Raffle", state.Title);
        Assert.Empty(state.JoinedUsers);
    }

    [Fact]
    public void State_AddUser_ReturnsFalseWhenClosed()
    {
        var state = State();
        Assert.False(state.AddUser("user1"));
    }

    [Fact]
    public void State_AddUser_ReturnsFalseForDuplicate()
    {
        var state = State();
        state.Open("Raffle");
        Assert.True(state.AddUser("user1"));
        Assert.False(state.AddUser("user1"));
        Assert.False(state.AddUser("USER1")); // case-insensitive
    }

    [Fact]
    public void State_AddUser_IsCaseInsensitive()
    {
        var state = State();
        state.Open("Raffle");
        state.AddUser("ViewerA");
        Assert.Single(state.JoinedUsers);
        Assert.False(state.AddUser("viewera"));
    }

    [Fact]
    public void State_Close_SetsIsOpenFalse()
    {
        var state = State();
        state.Open("Raffle");
        state.Close();
        Assert.False(state.IsOpen);
    }

    // ── JoinCommand ───────────────────────────────────────────────────────────

    [Fact]
    public async Task Join_UserNameStoredWithoutAtPrefix()
    {
        // Streamer.bot sometimes provides usernames with a leading @.
        // The command must store the bare username so SE leaderboard comparisons work.
        var state = State();
        state.Open("Test");
        await Join(state).ExecuteAsync(Ctx("@viewer1"));
        Assert.Contains("viewer1", state.JoinedUsers);
        Assert.DoesNotContain("@viewer1", state.JoinedUsers);
    }

    [Fact]
    public async Task Join_WhenClosed_ReturnsFail()
    {
        var result = await Join(State()).ExecuteAsync(Ctx("viewer1"));
        Assert.False(result.Success);
        Assert.Contains("No raffle open", result.Message);
    }

    [Fact]
    public async Task Join_WhenOpen_ReturnsSuccess()
    {
        var state = State();
        state.Open("Test");
        var result = await Join(state).ExecuteAsync(Ctx("viewer1"));
        Assert.True(result.Success);
        Assert.Contains("viewer1", result.Message);
        Assert.Contains("joined", result.Message);
    }

    [Fact]
    public async Task Join_DuplicateUser_ReturnsAlreadyJoined()
    {
        var state = State();
        state.Open("Test");
        await Join(state).ExecuteAsync(Ctx("viewer1"));
        var result = await Join(state).ExecuteAsync(Ctx("viewer1"));
        Assert.True(result.Success); // not a failure — just informational
        Assert.Contains("already", result.Message);
    }

    // ── OpenRaffleCommand ─────────────────────────────────────────────────────

    [Fact]
    public async Task OpenRaffle_NoTitle_ReturnsFail()
    {
        var result = await Open(State()).ExecuteAsync(Ctx("mod", ""));
        Assert.False(result.Success);
        Assert.Contains("!openRaffle", result.Message);
    }

    [Fact]
    public async Task OpenRaffle_WithTitle_OpensStateAndReturnsMessage()
    {
        var state = State();
        var result = await Open(state).ExecuteAsync(Ctx("mod", "Campanha dos 500"));
        Assert.True(result.Success);
        Assert.Contains("Campanha dos 500", result.Message);
        Assert.True(state.IsOpen);
        Assert.Equal("Campanha dos 500", state.Title);
    }

    [Fact]
    public async Task OpenRaffle_WhenAlreadyOpen_ReturnsFail()
    {
        var state = State();
        state.Open("Existing Raffle");
        var result = await Open(state).ExecuteAsync(Ctx("mod", "New Raffle"));
        Assert.False(result.Success);
        Assert.Contains("Existing Raffle", result.Message);
        Assert.True(state.IsOpen);
        Assert.Equal("Existing Raffle", state.Title); // unchanged
    }

    // ── CloseRaffleCommand ────────────────────────────────────────────────────

    [Fact]
    public async Task CloseRaffle_WhenClosed_ReturnsFail()
    {
        var result = await Close(State()).ExecuteAsync(Ctx("mod"));
        Assert.False(result.Success);
    }

    [Fact]
    public async Task CloseRaffle_WhenOpen_ClosesAndReturnsMessage()
    {
        var state = State();
        state.Open("Test");
        var result = await Close(state).ExecuteAsync(Ctx("mod"));
        Assert.True(result.Success);
        Assert.Contains("closed", result.Message, StringComparison.OrdinalIgnoreCase);
        Assert.False(state.IsOpen);
    }

    // ── DrawRaffleCommand ─────────────────────────────────────────────────────

    [Fact]
    public async Task DrawRaffle_WhenClosed_ReturnsFail()
    {
        var result = await Draw(State(), History()).ExecuteAsync(Ctx("mod"));
        Assert.False(result.Success);
    }

    [Fact]
    public async Task DrawRaffle_NoJoined_NoLeaderboard_ShowsNoJoinedMessage()
    {
        var state = State();
        state.Open("Test");
        var result = await Draw(state, History()).ExecuteAsync(Ctx("mod"));
        Assert.True(result.Success);
        Assert.False(state.IsOpen);
        Assert.Contains("No joined", result.Message);
    }

    [Fact]
    public async Task DrawRaffle_NoJoined_StillDrawsTop5FromLeaderboard()
    {
        var seMock = new Mock<IStreamElementsService>();
        seMock.Setup(s => s.IsAvailable).Returns(true);
        seMock.Setup(s => s.GetTopAsync(50, default)).ReturnsAsync(
            (IReadOnlyList<(string Username, long Points)>)new[]
            {
                ("ranked1", 1000L), ("ranked2", 900L), ("ranked3", 800L),
            });

        var state = State();
        state.Open("Test");

        var history = History();
        var result = await Draw(state, history, seMock.Object).ExecuteAsync(Ctx("mod"));

        Assert.True(result.Success);
        var session = history.GetRecent(1)[0];
        Assert.NotNull(session.Top5Winner);
        Assert.Null(session.Top10Winner);
        Assert.Null(session.BonusWinner);
        Assert.Contains("No joined", result.Message);
        Assert.True(
            result.Message.Contains("ranked1") ||
            result.Message.Contains("ranked2") ||
            result.Message.Contains("ranked3"));
    }

    [Fact]
    public async Task DrawRaffle_WithJoined_ClosesStateAndReturnsWinners()
    {
        var state = State();
        state.Open("Test");
        state.AddUser("viewer1");
        state.AddUser("viewer2");
        state.AddUser("viewer3");

        var history = History();
        var result = await Draw(state, history).ExecuteAsync(Ctx("mod"));

        Assert.True(result.Success);
        Assert.False(state.IsOpen); // raffle closed
        Assert.Single(history.GetRecent(1));
    }

    [Fact]
    public async Task DrawRaffle_BonusWinnerIsOneOfJoined()
    {
        var state = State();
        state.Open("Test");
        state.AddUser("alpha");
        state.AddUser("beta");

        var result = await Draw(state, History()).ExecuteAsync(Ctx("mod"));

        Assert.True(result.Success);
        Assert.True(result.Message.Contains("alpha") || result.Message.Contains("beta"));
    }

    [Fact]
    public async Task DrawRaffle_SavesSessionToHistory()
    {
        var state = State();
        state.Open("Campanha dos 500");
        state.AddUser("viewer1");

        var history = History();
        await Draw(state, history).ExecuteAsync(Ctx("mod"));

        var recent = history.GetRecent(1);
        Assert.Single(recent);
        Assert.Equal("Campanha dos 500", recent[0].Title);
        Assert.Equal(1, recent[0].JoinedCount);
        Assert.NotNull(recent[0].BonusWinner);
    }

    [Fact]
    public async Task DrawRaffle_WithLeaderboard_PicksTop5Winner()
    {
        var seMock = new Mock<IStreamElementsService>();
        seMock.Setup(s => s.IsAvailable).Returns(true);
        seMock.Setup(s => s.GetTopAsync(50, default)).ReturnsAsync(
            (IReadOnlyList<(string Username, long Points)>)new[]
            {
                ("ranked1", 1000L),
                ("ranked2",  900L),
                ("ranked3",  800L),
            });

        var state = State();
        state.Open("Test");
        state.AddUser("ranked2"); // ranked2 joins

        var history = History();
        var result = await Draw(state, history, seMock.Object).ExecuteAsync(Ctx("mod"));

        Assert.True(result.Success);
        var session = history.GetRecent(1)[0];
        // Top5 winner must be ranked1, ranked2, or ranked3
        Assert.NotNull(session.Top5Winner);
        Assert.Contains(session.Top5Winner, new[] { "ranked1", "ranked2", "ranked3" });
        // Top10 winner must be ranked2 (only joined user in leaderboard)
        Assert.Equal("ranked2", session.Top10Winner);
    }

    [Fact]
    public async Task DrawRaffle_Top10Draw_CollectsUpTo10JoinedFromLeaderboard()
    {
        // Leaderboard has 15 users, only positions 11-13 joined
        var leaderboard = Enumerable.Range(1, 15)
            .Select(i => ($"user{i}", (long)(1000 - i * 10)))
            .ToArray();

        var joinedInLeaderboard = new[] { "user11", "user12", "user13" };

        var seMock = new Mock<IStreamElementsService>();
        seMock.Setup(s => s.IsAvailable).Returns(true);
        seMock.Setup(s => s.GetTopAsync(50, default))
              .ReturnsAsync((IReadOnlyList<(string Username, long Points)>)leaderboard);

        var state = State();
        state.Open("Test");
        foreach (var u in joinedInLeaderboard) state.AddUser(u);
        state.AddUser("viewer_outside"); // not in leaderboard

        var history = History();
        await Draw(state, history, seMock.Object).ExecuteAsync(Ctx("mod"));

        var session = history.GetRecent(1)[0];
        // Top10 winner must be one of user11/user12/user13
        Assert.NotNull(session.Top10Winner);
        Assert.Contains(session.Top10Winner, joinedInLeaderboard);
    }

    [Fact]
    public async Task DrawRaffle_Top10_SkipsNonJoinedLeaderboardEntries_PicksFromJoinedOnly()
    {
        // Leaderboard positions 1-15 don't join; only positions 16 and 17 join.
        // The draw must skip positions 1-15 and pick from [viewer116, viewer117].
        var leaderboard = new[]
        {
            ("viewer1",   200L), ("viewer12",  200L), ("viewer13",  190L),
            ("viewer14",  180L), ("viewer15",  170L), ("viewer16",  160L),
            ("viewer17",  150L), ("viewer18",  140L), ("viewer19",  130L),
            ("viewer10",  120L), ("viewer111", 110L), ("viewer112", 100L),
            ("viewer113",  90L), ("viewer114",  80L), ("viewer115",  70L),
            ("viewer116",  60L), ("viewer117",  50L), ("viewer118",  40L),
            ("viewer119",  30L),
        };

        var seMock = new Mock<IStreamElementsService>();
        seMock.Setup(s => s.IsAvailable).Returns(true);
        seMock.Setup(s => s.GetTopAsync(50, default))
              .ReturnsAsync((IReadOnlyList<(string Username, long Points)>)leaderboard);

        var state = State();
        state.Open("Test");
        state.AddUser("viewer116"); // position 16
        state.AddUser("viewer117"); // position 17
        state.AddUser("viewer417"); // not in leaderboard
        state.AddUser("viewer318"); // not in leaderboard

        var history = History();
        await Draw(state, history, seMock.Object).ExecuteAsync(Ctx("mod"));

        var session = history.GetRecent(1)[0];
        // Top 10 winner must be viewer116 or viewer117 — positions 1-15 didn't join
        Assert.NotNull(session.Top10Winner);
        Assert.True(session.Top10Winner == "viewer116" || session.Top10Winner == "viewer117");
        // Bonus can be any of the four joined users
        Assert.NotNull(session.BonusWinner);
    }

    [Fact]
    public async Task DrawRaffle_NoLeaderboard_ShowsTop5NoLeaderboardMessage()
    {
        // SE not configured — top5 draw skipped, message shown instead
        var state = State();
        state.Open("Test");
        state.AddUser("viewer1");

        var result = await Draw(state, History()).ExecuteAsync(Ctx("mod"));

        Assert.True(result.Success);
        Assert.Contains("No leaderboard", result.Message);
        Assert.DoesNotContain("Top5:", result.Message);
    }

    [Fact]
    public async Task DrawRaffle_JoinedButNoneOnLeaderboard_ShowsTop10NoWinnerMessage()
    {
        // Leaderboard available, but no joined user appears in it
        var seMock = new Mock<IStreamElementsService>();
        seMock.Setup(s => s.IsAvailable).Returns(true);
        seMock.Setup(s => s.GetTopAsync(50, default)).ReturnsAsync(
            (IReadOnlyList<(string Username, long Points)>)new[]
            {
                ("topuser1", 1000L), ("topuser2", 900L),
            });

        var state = State();
        state.Open("Test");
        state.AddUser("outsider1"); // not on leaderboard
        state.AddUser("outsider2"); // not on leaderboard

        var history = History();
        var result = await Draw(state, history, seMock.Object).ExecuteAsync(Ctx("mod"));

        Assert.True(result.Success);
        Assert.Contains("No top10 winner", result.Message);
        Assert.Null(history.GetRecent(1)[0].Top10Winner);
        // Bonus draw still happens
        Assert.True(result.Message.Contains("outsider1") || result.Message.Contains("outsider2"));
    }

    // ── ShowPreviousRaffleCommand ─────────────────────────────────────────────

    [Fact]
    public async Task ShowPreviousRaffle_NoHistory_ReturnsFail()
    {
        var result = await Show(History()).ExecuteAsync(Ctx("mod"));
        Assert.False(result.Success);
        Assert.Contains("No history", result.Message);
    }

    [Fact]
    public async Task ShowPreviousRaffle_WithHistory_FormatsLastSession()
    {
        var history = History();
        history.Save(new RaffleSession(
            Title:        "Campanha 500",
            Date:         new DateTime(2026, 4, 7, 12, 0, 0, DateTimeKind.Utc),
            JoinedCount:  42,
            Top5Winner:  "winner1",
            Top10Winner: "winner2",
            BonusWinner: "winner3"
        ));

        var result = await Show(history).ExecuteAsync(Ctx("mod"));
        Assert.True(result.Success);
        Assert.Contains("Campanha 500", result.Message);
        Assert.Contains("2026-04-07", result.Message);
        Assert.Contains("winner1", result.Message);
        Assert.Contains("winner2", result.Message);
        Assert.Contains("winner3", result.Message);
    }

    [Fact]
    public async Task ShowPreviousRaffle_ReturnsLastSavedSession()
    {
        var history = History();
        history.Save(new RaffleSession("Old", DateTime.UtcNow, 5, null, null, "bonus1"));
        history.Save(new RaffleSession("New", DateTime.UtcNow, 10, "t5", "t10", "b1"));

        var result = await Show(history).ExecuteAsync(Ctx("mod"));
        Assert.Contains("New", result.Message);
        Assert.DoesNotContain("Old", result.Message);
    }

    [Fact]
    public async Task ShowPreviousRaffle_NullWinnersRenderedAsDash()
    {
        // All three draws can be null (e.g. no leaderboard, nobody joined).
        var history = History();
        history.Save(new RaffleSession("Test", DateTime.UtcNow, 0, null, null, null));

        var result = await Show(history).ExecuteAsync(Ctx("mod"));
        Assert.True(result.Success);
        // Each null winner slot must render as "-", not empty or literal "null"
        Assert.DoesNotContain("null", result.Message);
        Assert.Contains("Top5: -",  result.Message);
        Assert.Contains("Top10: -", result.Message);
        Assert.Contains("Bonus: -", result.Message);
    }

    // ── @ prefix handling ─────────────────────────────────────────────────────

    [Fact]
    public async Task DrawRaffle_LeaderboardMatchesJoinedUserWithAtPrefix()
    {
        // If a user joined as "@viewer1" the @ must be stripped so the leaderboard
        // comparison ("viewer1") still finds a match.
        var seMock = new Mock<IStreamElementsService>();
        seMock.Setup(s => s.IsAvailable).Returns(true);
        seMock.Setup(s => s.GetTopAsync(50, default)).ReturnsAsync(
            (IReadOnlyList<(string Username, long Points)>)new[]
            {
                ("viewer1", 1000L), ("viewer2", 900L),
            });

        var state = State();
        state.Open("Test");
        state.AddUser("@viewer1"); // stored with @ — must be stripped before comparison

        var history = History();
        await Draw(state, history, seMock.Object).ExecuteAsync(Ctx("mod"));

        var session = history.GetRecent(1)[0];
        // viewer1 is in the leaderboard and joined — must be the Top10 winner
        Assert.Equal("viewer1", session.Top10Winner);
    }
}
