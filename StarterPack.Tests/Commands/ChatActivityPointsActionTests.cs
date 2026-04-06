using Moq;
using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;
using static StarterPack.Commands.ChatActivityPointsAction;

namespace StarterPack.Tests.Commands;

public class ChatActivityPointsActionTests
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static ChatActivityPointsAction Build(
        IChatActivityState? state = null,
        IStreamElementsService? se = null,
        int minLength = 3,
        int points = 2) =>
        new(minLength, points, null, null, state ?? new InMemoryChatActivityState(TimeSpan.FromSeconds(30)), se);

    private static ChatMessage Msg(string user, string text, int emoteCount = 0) =>
        new(user, text, emoteCount);

    private static IStreamElementsService AvailableSe(bool addOk = true)
    {
        var mock = new Mock<IStreamElementsService>();
        mock.Setup(s => s.IsAvailable).Returns(true);
        mock.Setup(s => s.AddPointsAsync(It.IsAny<string>(), It.IsAny<int>(), default))
            .ReturnsAsync(addOk);
        return mock.Object;
    }

    // ── Filter: commands ──────────────────────────────────────────────────────

    [Theory]
    [InlineData("!points")]
    [InlineData("!top")]
    [InlineData("!")]
    public void Filter_CommandMessage_ReturnsIsCommand(string text)
    {
        var action = Build();
        Assert.Equal(Rejection.IsCommand, action.Filter(Msg("viewer", text)));
    }

    // ── Filter: short messages ────────────────────────────────────────────────

    [Theory]
    [InlineData("")]
    [InlineData("hi")]
    [InlineData("ok")]
    public void Filter_ShortMessage_ReturnsTooShort(string text)
    {
        var action = Build();
        Assert.Equal(Rejection.TooShort, action.Filter(Msg("viewer", text)));
    }

    [Fact]
    public void Filter_MessageAtMinLength_Passes()
    {
        var action = Build(minLength: 3);
        Assert.Equal(Rejection.None, action.Filter(Msg("viewer", "hey")));
    }

    // ── Filter: bots ──────────────────────────────────────────────────────────

    [Theory]
    [InlineData("nightbot")]
    [InlineData("Nightbot")]
    [InlineData("streamelements")]
    [InlineData("streamlabs")]
    [InlineData("moobot")]
    [InlineData("fossabot")]
    public void Filter_KnownBot_ReturnsIsBot(string username)
    {
        var action = Build();
        Assert.Equal(Rejection.IsBot, action.Filter(Msg(username, "hello chat")));
    }

    // ── Filter: cooldown ──────────────────────────────────────────────────────

    [Fact]
    public void Filter_UserOnCooldown_ReturnsOnCooldown()
    {
        var state = new Mock<IChatActivityState>();
        state.Setup(s => s.IsOnCooldown("viewer")).Returns(true);

        var action = Build(state: state.Object);
        Assert.Equal(Rejection.OnCooldown, action.Filter(Msg("viewer", "hello chat")));
    }

    [Fact]
    public void Filter_UserNotOnCooldown_Passes()
    {
        var state = new Mock<IChatActivityState>();
        state.Setup(s => s.IsOnCooldown("viewer")).Returns(false);
        state.Setup(s => s.IsDuplicate(It.IsAny<string>(), It.IsAny<string>())).Returns(false);

        var action = Build(state: state.Object);
        Assert.Equal(Rejection.None, action.Filter(Msg("viewer", "hello chat")));
    }

    // ── Filter: duplicate messages ────────────────────────────────────────────

    [Fact]
    public void Filter_DuplicateMessage_ReturnsDuplicateMessage()
    {
        var state = new Mock<IChatActivityState>();
        state.Setup(s => s.IsOnCooldown(It.IsAny<string>())).Returns(false);
        state.Setup(s => s.IsDuplicate("viewer", "hello chat")).Returns(true);

        var action = Build(state: state.Object);
        Assert.Equal(Rejection.DuplicateMessage, action.Filter(Msg("viewer", "hello chat")));
    }

    // ── Filter: emote-only ────────────────────────────────────────────────────

    [Fact]
    public void Filter_NativeTwitchEmoteOnly_ReturnsEmoteOnly()
    {
        // 3 words, 3 emotes → all emotes
        var action = Build();
        Assert.Equal(Rejection.EmoteOnly, action.Filter(Msg("viewer", "Kappa PogChamp Kreygasm", emoteCount: 3)));
    }

    [Fact]
    public void Filter_NativeTwitchEmoteMixedWithText_Passes()
    {
        // 4 words, 1 emote → not emote-only
        var action = Build();
        Assert.Equal(Rejection.None, action.Filter(Msg("viewer", "Kappa nice play today", emoteCount: 1)));
    }

    [Theory]
    [InlineData("KEKW KEKW KEKW")]
    [InlineData("LUL LUL")]
    [InlineData("pog pog pog pog")]
    public void Filter_RepeatedSingleWord_ReturnsEmoteOnly(string text)
    {
        var action = Build();
        Assert.Equal(Rejection.EmoteOnly, action.Filter(Msg("viewer", text)));
    }

    [Theory]
    [InlineData("OMEGALUL PogU monkaS")]
    [InlineData("Clap GIGACHAD Pog")]
    [InlineData("COPIUM Sadge FeelsBadMan")]
    public void Filter_AllBttvEmotes_ReturnsEmoteOnly(string text)
    {
        var action = Build();
        Assert.Equal(Rejection.EmoteOnly, action.Filter(Msg("viewer", text)));
    }

    [Fact]
    public void Filter_BttvEmoteMixedWithText_Passes()
    {
        var action = Build();
        Assert.Equal(Rejection.None, action.Filter(Msg("viewer", "OMEGALUL that was funny")));
    }

    // ── ProcessAsync: state and SE ────────────────────────────────────────────

    [Fact]
    public async Task Process_ValidMessage_RecordsStateAndReturnsSuccess()
    {
        var state = new Mock<IChatActivityState>();
        state.Setup(s => s.IsOnCooldown(It.IsAny<string>())).Returns(false);
        state.Setup(s => s.IsDuplicate(It.IsAny<string>(), It.IsAny<string>())).Returns(false);

        var action = Build(state: state.Object);
        var (success, reason) = await action.ProcessAsync(Msg("viewer", "hello chat"));

        Assert.True(success);
        Assert.Equal(Rejection.None, reason);
        state.Verify(s => s.Record("viewer", "hello chat"), Times.Once);
    }

    [Fact]
    public async Task Process_ValidMessage_AddsPointsViaSe()
    {
        var se = new Mock<IStreamElementsService>();
        se.Setup(s => s.IsAvailable).Returns(true);
        se.Setup(s => s.AddPointsAsync("viewer", 2, default)).ReturnsAsync(true);

        var action = Build(se: se.Object);
        var (success, _) = await action.ProcessAsync(Msg("viewer", "hello chat"));

        Assert.True(success);
        se.Verify(s => s.AddPointsAsync("viewer", 2, default), Times.Once);
    }

    [Fact]
    public async Task Process_SeApiFailure_ReturnsFalseDoesNotRecord()
    {
        var state = new Mock<IChatActivityState>();
        state.Setup(s => s.IsOnCooldown(It.IsAny<string>())).Returns(false);
        state.Setup(s => s.IsDuplicate(It.IsAny<string>(), It.IsAny<string>())).Returns(false);

        var action = Build(state: state.Object, se: AvailableSe(addOk: false));
        var (success, _) = await action.ProcessAsync(Msg("viewer", "hello chat"));

        Assert.False(success);
        state.Verify(s => s.Record(It.IsAny<string>(), It.IsAny<string>()), Times.Never);
    }

    [Fact]
    public async Task Process_RejectedMessage_DoesNotCallSe()
    {
        var se = new Mock<IStreamElementsService>();
        se.Setup(s => s.IsAvailable).Returns(true);

        var action = Build(se: se.Object);
        await action.ProcessAsync(Msg("viewer", "!points"));

        se.Verify(s => s.AddPointsAsync(It.IsAny<string>(), It.IsAny<int>(), default), Times.Never);
    }

    // ── InMemoryChatActivityState ─────────────────────────────────────────────

    [Fact]
    public void State_IsOnCooldown_FalseBeforeRecord()
    {
        var state = new InMemoryChatActivityState(TimeSpan.FromSeconds(30));
        Assert.False(state.IsOnCooldown("viewer"));
    }

    [Fact]
    public void State_IsOnCooldown_TrueImmediatelyAfterRecord()
    {
        var state = new InMemoryChatActivityState(TimeSpan.FromSeconds(30));
        state.Record("viewer", "hello");
        Assert.True(state.IsOnCooldown("viewer"));
    }

    [Fact]
    public void State_IsDuplicate_TrueForSameMessageAfterRecord()
    {
        var state = new InMemoryChatActivityState(TimeSpan.FromSeconds(30));
        state.Record("viewer", "hello chat");
        Assert.True(state.IsDuplicate("viewer", "hello chat"));
        Assert.True(state.IsDuplicate("viewer", "HELLO CHAT")); // case-insensitive
    }

    [Fact]
    public void State_IsDuplicate_FalseForDifferentMessage()
    {
        var state = new InMemoryChatActivityState(TimeSpan.FromSeconds(30));
        state.Record("viewer", "hello chat");
        Assert.False(state.IsDuplicate("viewer", "nice stream"));
    }

    [Fact]
    public void State_IsDuplicate_FalseForDifferentUser()
    {
        var state = new InMemoryChatActivityState(TimeSpan.FromSeconds(30));
        state.Record("viewer1", "hello chat");
        Assert.False(state.IsDuplicate("viewer2", "hello chat"));
    }
}
