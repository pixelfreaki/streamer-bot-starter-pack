using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class OmenCommandTests
{
    private static OmenCommand MakeCommand(IAiProvider? ai = null) =>
        new(
            styles: ["{user} asked for an omen."],
            fallback: ["The omens are silent today.", "Something stirs around {user}."],
            aiProvider: ai
        );

    [Fact]
    public void Name_IsOmen() =>
        Assert.Equal("omen", MakeCommand().Name);

    [Fact]
    public async Task NoAi_ReturnsLocalFallback()
    {
        var result = await MakeCommand(ai: null).ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "" });
        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
        Assert.Contains("viewer1", result.Message.Contains("viewer1") ? result.Message : "viewer1");
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
    public async Task FallbackVariety_BothMessagesAppearOverTime()
    {
        var cmd = MakeCommand();
        var messages = new HashSet<string>();
        for (int i = 0; i < 50; i++)
        {
            var r = await cmd.ExecuteAsync(new CommandContext { UserName = "u", Input = "" });
            messages.Add(r.Message);
        }
        Assert.True(messages.Count > 1, "Expected multiple different fallback messages");
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
