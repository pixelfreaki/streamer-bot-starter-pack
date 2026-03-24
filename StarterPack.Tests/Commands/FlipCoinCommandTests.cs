using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class FlipCoinCommandTests
{
    private static CommandContext ContextFor(string user, string input = "") =>
        new() { UserName = user, Input = input };

    [Fact]
    public void Name_IsFlipCoin()
    {
        Assert.Equal("flipcoin", new FlipCoinCommand().Name);
    }

    [Fact]
    public async Task Execute_WithNoInput_ReturnsNoChoiceMessage()
    {
        var command = new FlipCoinCommand(noChoice: "choose {user}!");

        var result = await command.ExecuteAsync(ContextFor("alice"));

        Assert.True(result.Success);
        Assert.Equal("choose alice!", result.Message);
    }

    [Fact]
    public async Task Execute_WithUnrecognizedInput_ReturnsNoChoiceMessage()
    {
        var command = new FlipCoinCommand(noChoice: "invalid");

        var result = await command.ExecuteAsync(ContextFor("alice", "foo"));

        Assert.Equal("invalid", result.Message);
    }

    [Theory]
    [InlineData("heads")]
    [InlineData("HEADS")]
    [InlineData("head")]
    [InlineData("HEAD")]
    [InlineData("cara")]
    [InlineData("CARA")]
    public async Task Execute_HeadsVariants_AreRecognized(string input)
    {
        var command = new FlipCoinCommand(
            heads: ["COIN_HEADS VoteYea"],
            tails: ["COIN_TAILS VoteNay"],
            win: ["W"], loss: ["L"]);

        // Over 200 runs we must see at least one HEADS result to confirm the input was parsed
        bool sawHeads = false;
        for (int i = 0; i < 200 && !sawHeads; i++)
        {
            var r = await command.ExecuteAsync(ContextFor("u", input));
            sawHeads = r.Message.Contains("COIN_HEADS");
        }

        Assert.True(sawHeads, $"Input '{input}' was never treated as heads guess");
    }

    [Theory]
    [InlineData("tails")]
    [InlineData("TAILS")]
    [InlineData("tail")]
    [InlineData("TAIL")]
    [InlineData("coroa")]
    [InlineData("COROA")]
    public async Task Execute_TailsVariants_AreRecognized(string input)
    {
        var command = new FlipCoinCommand(
            heads: ["COIN_HEADS VoteYea"],
            tails: ["COIN_TAILS VoteNay"],
            win: ["W"], loss: ["L"]);

        bool sawTails = false;
        for (int i = 0; i < 200 && !sawTails; i++)
        {
            var r = await command.ExecuteAsync(ContextFor("u", input));
            sawTails = r.Message.Contains("COIN_TAILS");
        }

        Assert.True(sawTails, $"Input '{input}' was never treated as tails guess");
    }

    [Fact]
    public async Task Execute_WhenCoinMatchesGuess_ContainsWin()
    {
        var command = new FlipCoinCommand(
            heads: ["HEADS VoteYea"], tails: ["TAILS VoteNay"],
            win: ["WIN"], loss: ["LOSE"]);

        bool sawWin = false;
        for (int i = 0; i < 200 && !sawWin; i++)
        {
            var r = await command.ExecuteAsync(ContextFor("u", "heads"));
            if (r.Message.Contains("HEADS")) sawWin = r.Message.Contains("WIN");
        }

        Assert.True(sawWin, "A correct heads guess should produce WIN");
    }

    [Fact]
    public async Task Execute_WhenCoinDiffersFromGuess_ContainsLoss()
    {
        var command = new FlipCoinCommand(
            heads: ["HEADS VoteYea"], tails: ["TAILS VoteNay"],
            win: ["WIN"], loss: ["LOSE"]);

        bool sawLoss = false;
        for (int i = 0; i < 200 && !sawLoss; i++)
        {
            var r = await command.ExecuteAsync(ContextFor("u", "heads"));
            if (r.Message.Contains("TAILS")) sawLoss = r.Message.Contains("LOSE");
        }

        Assert.True(sawLoss, "A wrong heads guess (landed tails) should produce LOSE");
    }

    [Fact]
    public async Task Execute_ReplacesUserPlaceholderInCoinMessage()
    {
        var command = new FlipCoinCommand(
            heads: ["{user} HEADS VoteYea"],
            tails: ["{user} TAILS VoteNay"],
            win: ["W"], loss: ["L"]);

        bool sawReplaced = false;
        for (int i = 0; i < 200 && !sawReplaced; i++)
        {
            var r = await command.ExecuteAsync(ContextFor("pixelfreaki", "heads"));
            if (r.Message.Contains("HEADS"))
            {
                Assert.Contains("pixelfreaki", r.Message);
                Assert.DoesNotContain("{user}", r.Message);
                sawReplaced = true;
            }
        }
    }

    [Fact]
    public async Task Execute_ReplacesUserPlaceholderInNoChoice()
    {
        var command = new FlipCoinCommand(noChoice: "Hey {user}, pick one!");

        var result = await command.ExecuteAsync(ContextFor("bob"));

        Assert.Equal("Hey bob, pick one!", result.Message);
    }

    [Fact]
    public async Task Execute_WithDefaults_ReturnsValidMessage()
    {
        var command = new FlipCoinCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer", "heads"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
        Assert.DoesNotContain("{user}", result.Message);
    }

    [Fact]
    public async Task Execute_OverTime_ShowsBothHeadsAndTails()
    {
        var command = new FlipCoinCommand(
            heads: ["HEADS VoteYea"],
            tails: ["TAILS VoteNay"],
            win: ["W"], loss: ["L"]);
        var seen = new HashSet<string>();

        for (int i = 0; i < 200; i++)
        {
            var r = await command.ExecuteAsync(ContextFor("u", "heads"));
            if (r.Message.Contains("HEADS")) seen.Add("heads");
            if (r.Message.Contains("TAILS")) seen.Add("tails");
        }

        Assert.Contains("heads", seen);
        Assert.Contains("tails", seen);
    }
}
