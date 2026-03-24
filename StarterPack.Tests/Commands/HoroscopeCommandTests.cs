using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class HoroscopeCommandTests
{
    private static HoroscopeCommand MakeCommand(IAiProvider? ai = null) =>
        new(
            styles: ["Horoscope for {user}: {text}"],
            fallback: ["The stars refuse to align.", "No vision today."],
            noInput: "@{user} ... what is your sign?",
            aiProvider: ai
        );

    [Fact]
    public void Name_IsHoroscope() =>
        Assert.Equal("horoscope", MakeCommand().Name);

    [Fact]
    public async Task EmptyInput_ReturnsNoInputMessage()
    {
        var result = await MakeCommand().ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "" });
        Assert.True(result.Success);
        Assert.Contains("viewer1", result.Message);
    }

    [Fact]
    public async Task WhitespaceInput_ReturnsNoInputMessage()
    {
        var result = await MakeCommand().ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "   " });
        Assert.True(result.Success);
        Assert.Contains("viewer1", result.Message);
    }

    [Fact]
    public async Task NoAi_WithInput_ReturnsFallback()
    {
        var result = await MakeCommand(ai: null).ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "Scorpio" });
        Assert.True(result.Success);
        Assert.True(result.Message == "The stars refuse to align." || result.Message == "No vision today.");
    }

    [Fact]
    public async Task WithAi_WithInput_TriggersAiAndReturnsEmpty()
    {
        var ai = new FakeAiProvider();
        var result = await MakeCommand(ai: ai).ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "Scorpio" });
        Assert.True(result.Success);
        Assert.Equal(string.Empty, result.Message);
        Assert.True(ai.WasCalled);
        Assert.Contains("viewer1", ai.LastPrompt);
        Assert.Contains("Scorpio", ai.LastPrompt);
    }

    [Fact]
    public async Task WithUnavailableAi_WithInput_ReturnsFallback()
    {
        var ai = new FakeAiProvider(available: false);
        var result = await MakeCommand(ai: ai).ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "Scorpio" });
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
