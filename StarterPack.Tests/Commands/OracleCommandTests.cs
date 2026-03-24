using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class OracleCommandTests
{
    private static OracleCommand MakeCommand(IAiProvider? ai = null) =>
        new(
            styles: ["Oracle style: {user} asks {text}"],
            fallback: ["The Oracle is silent.", "No vision today."],
            noInput: "@{user} ... ask something.",
            aiProvider: ai
        );

    [Fact]
    public void Name_IsOracle() =>
        Assert.Equal("oracle", MakeCommand().Name);

    [Fact]
    public async Task EmptyInput_ReturnsNoInputMessage()
    {
        var cmd = MakeCommand();
        var result = await cmd.ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "" });
        Assert.True(result.Success);
        Assert.Contains("viewer1", result.Message);
    }

    [Fact]
    public async Task WhitespaceInput_ReturnsNoInputMessage()
    {
        var cmd = MakeCommand();
        var result = await cmd.ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "   " });
        Assert.True(result.Success);
        Assert.Contains("viewer1", result.Message);
    }

    [Fact]
    public async Task NoAi_WithInput_ReturnsFallback()
    {
        var cmd = MakeCommand(ai: null);
        var result = await cmd.ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "will I survive?" });
        Assert.True(result.Success);
        Assert.True(result.Message == "The Oracle is silent." || result.Message == "No vision today.");
    }

    [Fact]
    public async Task WithAi_WithInput_TriggersAiAndReturnsEmpty()
    {
        var ai = new FakeAiProvider();
        var cmd = MakeCommand(ai: ai);
        var result = await cmd.ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "will I survive?" });
        Assert.True(result.Success);
        Assert.Equal(string.Empty, result.Message);
        Assert.True(ai.WasCalled);
        Assert.Contains("viewer1", ai.LastPrompt);
        Assert.Contains("will I survive?", ai.LastPrompt);
    }

    [Fact]
    public async Task WithUnavailableAi_WithInput_ReturnsFallback()
    {
        var ai = new FakeAiProvider(available: false);
        var cmd = MakeCommand(ai: ai);
        var result = await cmd.ExecuteAsync(new CommandContext { UserName = "viewer1", Input = "will I survive?" });
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
            var r = await cmd.ExecuteAsync(new CommandContext { UserName = "u", Input = "test" });
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
