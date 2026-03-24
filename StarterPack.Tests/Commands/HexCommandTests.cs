using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class HexCommandTests
{
    private static HexCommand MakeCommand(IAiProvider? ai = null) =>
        new(
            styles: ["{caster} curses {target}."],
            fallback: ["A hex without a target dissolves, {user}.", "The ritual is incomplete, {user}."],
            noInput: "@{user} ... who are you hexing?",
            aiProvider: ai
        );

    [Fact]
    public void Name_IsHex() =>
        Assert.Equal("hex", MakeCommand().Name);

    [Fact]
    public async Task EmptyInput_ReturnsNoInputWithUser()
    {
        var result = await MakeCommand().ExecuteAsync(new CommandContext { UserName = "caster1", Input = "" });
        Assert.True(result.Success);
        Assert.Contains("caster1", result.Message);
    }

    [Fact]
    public async Task NoAi_WithTarget_ReturnsFallback()
    {
        var result = await MakeCommand(ai: null).ExecuteAsync(new CommandContext { UserName = "caster1", Input = "target1" });
        Assert.True(result.Success);
        Assert.Contains("caster1", result.Message);
    }

    [Fact]
    public async Task WithAi_WithTarget_TriggersAiAndReturnsEmpty()
    {
        var ai = new FakeAiProvider();
        var result = await MakeCommand(ai: ai).ExecuteAsync(new CommandContext { UserName = "caster1", Input = "target1" });
        Assert.True(result.Success);
        Assert.Equal(string.Empty, result.Message);
        Assert.True(ai.WasCalled);
        Assert.Contains("caster1", ai.LastPrompt);
        Assert.Contains("target1", ai.LastPrompt);
    }

    [Fact]
    public async Task TargetWithAtSign_IsStripped()
    {
        var ai = new FakeAiProvider();
        var result = await MakeCommand(ai: ai).ExecuteAsync(new CommandContext { UserName = "caster1", Input = "@target1" });
        Assert.True(result.Success);
        Assert.Equal(string.Empty, result.Message);
        Assert.Contains("target1", ai.LastPrompt);
        Assert.DoesNotContain("@target1", ai.LastPrompt);
    }

    [Fact]
    public async Task WithUnavailableAi_WithTarget_ReturnsFallback()
    {
        var ai = new FakeAiProvider(available: false);
        var result = await MakeCommand(ai: ai).ExecuteAsync(new CommandContext { UserName = "caster1", Input = "target1" });
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
