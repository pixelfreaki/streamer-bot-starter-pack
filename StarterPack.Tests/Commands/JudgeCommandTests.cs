using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class JudgeCommandTests
{
    private static JudgeCommand MakeCommand(IAiProvider? ai = null) =>
        new(
            styles: ["{judge} judges {target}."],
            fallback: ["{judge} raises the gavel... but no name was spoken.", "Court is in session, {judge}."],
            noInput: "@{judge} ... who should be judged?",
            aiProvider: ai
        );

    [Fact]
    public void Name_IsJudge() =>
        Assert.Equal("judge", MakeCommand().Name);

    [Fact]
    public async Task EmptyInput_ReturnsNoInputWithJudge()
    {
        var result = await MakeCommand().ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "" });
        Assert.True(result.Success);
        Assert.Contains("viewer1", result.Message);
    }

    [Fact]
    public async Task NoAi_WithTarget_ReturnsFallback()
    {
        var result = await MakeCommand(ai: null).ExecuteAsync(new CommandContext { UserName = "judge1", Input = "target1" });
        Assert.True(result.Success);
        Assert.Contains("judge1", result.Message);
    }

    [Fact]
    public async Task WithAi_WithTarget_TriggersAiAndReturnsEmpty()
    {
        var ai = new FakeAiProvider();
        var result = await MakeCommand(ai: ai).ExecuteAsync(new CommandContext { UserName = "judge1", Input = "target1" });
        Assert.True(result.Success);
        Assert.Equal(string.Empty, result.Message);
        Assert.True(ai.WasCalled);
        Assert.Contains("judge1", ai.LastPrompt);
        Assert.Contains("target1", ai.LastPrompt);
    }

    [Fact]
    public async Task TargetWithAtSign_IsStripped()
    {
        var ai = new FakeAiProvider();
        var result = await MakeCommand(ai: ai).ExecuteAsync(new CommandContext { UserName = "judge1", Input = "@target1" });
        Assert.True(result.Success);
        Assert.Equal(string.Empty, result.Message);
        Assert.Contains("target1", ai.LastPrompt);
        Assert.DoesNotContain("@target1", ai.LastPrompt);
    }

    [Fact]
    public async Task WithUnavailableAi_WithTarget_ReturnsFallback()
    {
        var ai = new FakeAiProvider(available: false);
        var result = await MakeCommand(ai: ai).ExecuteAsync(new CommandContext { UserName = "judge1", Input = "target1" });
        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
        Assert.False(ai.WasCalled);
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
