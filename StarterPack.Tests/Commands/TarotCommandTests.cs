using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class TarotCommandTests
{
    private static TarotCommand MakeCommand(IAiProvider? ai = null) =>
        new(
            styles: ["{user} asked for a tarot reading."],
            fallback: ["The cards refuse to be drawn for {user}.", "The Veil is thick."],
            aiProvider: ai
        );

    [Fact]
    public void Name_IsTarot() =>
        Assert.Equal("tarot", MakeCommand().Name);

    [Fact]
    public async Task NoAi_ReturnsFallback()
    {
        var result = await MakeCommand(ai: null).ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "" });
        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task NoAi_WithOrWithoutInput_ReturnsFallback()
    {
        var cmd = MakeCommand(ai: null);
        var r1 = await cmd.ExecuteAsync(new CommandContext { UserName = "u", Input = "" });
        var r2 = await cmd.ExecuteAsync(new CommandContext { UserName = "u", Input = "anything" });
        Assert.True(r1.Success);
        Assert.True(r2.Success);
    }

    [Fact]
    public async Task WithAi_TriggersAiAndReturnsEmpty()
    {
        var ai = new FakeAiProvider();
        var result = await MakeCommand(ai: ai).ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "" });
        Assert.True(result.Success);
        Assert.Equal(string.Empty, result.Message);
        Assert.True(ai.WasCalled);
        Assert.Contains("viewer1", ai.LastPrompt);
    }

    [Fact]
    public async Task WithUnavailableAi_ReturnsFallback()
    {
        var ai = new FakeAiProvider(available: false);
        var result = await MakeCommand(ai: ai).ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "" });
        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
        Assert.False(ai.WasCalled);
    }

    [Fact]
    public async Task FallbackReplacesUser()
    {
        var result = await MakeCommand().ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "" });
        Assert.True(result.Success);
        Assert.DoesNotContain("{user}", result.Message);
    }

    private class FakeAiProvider(bool available = true) : IAiProvider
    {
        public bool IsAvailable => available;
        public bool WasCalled { get; private set; }
        public string LastPrompt { get; private set; } = string.Empty;

        public Task<string?> EnhanceAsync(string prompt, string? systemPrompt = null, int maxTokens = 300, double temperature = 0.7, CancellationToken cancellationToken = default)
        {
            WasCalled = true;
            LastPrompt = prompt;
            return Task.FromResult<string?>(null);
        }
    }
}
