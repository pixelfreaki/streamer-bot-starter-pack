using Moq;
using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class JokeCommandTests
{
    private static readonly string[] TestFallbacks = ["Fallback joke A.", "Fallback joke B."];

    private static CommandContext EmptyContext => new();
    private static CommandContext ContextWith(string input) => new() { Input = input };

    [Fact]
    public void Name_IsJoke()
    {
        Assert.Equal("joke", new JokeCommand().Name);
    }

    [Fact]
    public async Task Execute_WithNoAiProvider_ReturnsFallback()
    {
        var command = new JokeCommand(fallbacks: TestFallbacks);

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.Contains(result.Message, TestFallbacks);
    }

    [Fact]
    public async Task Execute_WithUnavailableAi_ReturnsFallback()
    {
        var ai = new Mock<IAiProvider>();
        ai.Setup(x => x.IsAvailable).Returns(false);

        var command = new JokeCommand(fallbacks: TestFallbacks, aiProvider: ai.Object);

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.Contains(result.Message, TestFallbacks);
        ai.Verify(x => x.EnhanceAsync(It.IsAny<string>(), It.IsAny<string?>(), It.IsAny<int>(), It.IsAny<double>(), It.IsAny<CancellationToken>()), Times.Never);
    }

    [Fact]
    public async Task Execute_WithAvailableAi_ParsesListAndReturnsOneJoke()
    {
        const string jokeList =
            "1. Por que X? Porque Y.\n" +
            "2. Por que A? Porque B.\n" +
            "3. Por que C? Porque D.";

        var ai = new Mock<IAiProvider>();
        ai.Setup(x => x.IsAvailable).Returns(true);
        ai.Setup(x => x.EnhanceAsync(It.IsAny<string>(), It.IsAny<string?>(), It.IsAny<int>(), It.IsAny<double>(), It.IsAny<CancellationToken>()))
          .ReturnsAsync(jokeList);

        var command = new JokeCommand(fallbacks: TestFallbacks, aiProvider: ai.Object);

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.True(
            result.Message is "Por que X? Porque Y." or
                              "Por que A? Porque B." or
                              "Por que C? Porque D.");
    }

    [Fact]
    public async Task Execute_WhenAiReturnsUnparseable_ReturnsRawResponse()
    {
        var ai = new Mock<IAiProvider>();
        ai.Setup(x => x.IsAvailable).Returns(true);
        ai.Setup(x => x.EnhanceAsync(It.IsAny<string>(), It.IsAny<string?>(), It.IsAny<int>(), It.IsAny<double>(), It.IsAny<CancellationToken>()))
          .ReturnsAsync("Unparseable response.");

        var command = new JokeCommand(fallbacks: TestFallbacks, aiProvider: ai.Object);

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.Equal("Unparseable response.", result.Message);
    }

    [Fact]
    public async Task Execute_WhenAiReturnsNull_FallsBackToLocal()
    {
        var ai = new Mock<IAiProvider>();
        ai.Setup(x => x.IsAvailable).Returns(true);
        ai.Setup(x => x.EnhanceAsync(It.IsAny<string>(), It.IsAny<string?>(), It.IsAny<int>(), It.IsAny<double>(), It.IsAny<CancellationToken>()))
          .ReturnsAsync((string?)null);

        var command = new JokeCommand(fallbacks: TestFallbacks, aiProvider: ai.Object);

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.Contains(result.Message, TestFallbacks);
    }

    [Fact]
    public async Task Execute_WithTopic_PassesTopicToAi()
    {
        string? capturedPrompt = null;
        var ai = new Mock<IAiProvider>();
        ai.Setup(x => x.IsAvailable).Returns(true);
        ai.Setup(x => x.EnhanceAsync(It.IsAny<string>(), It.IsAny<string?>(), It.IsAny<int>(), It.IsAny<double>(), It.IsAny<CancellationToken>()))
          .Callback<string, string?, int, double, CancellationToken>((prompt, _, _, _, _) => capturedPrompt = prompt)
          .ReturnsAsync("joke about cats");

        var command = new JokeCommand(aiProvider: ai.Object, topicPrompt: "Topic: ");

        await command.ExecuteAsync(ContextWith("cats"));

        Assert.NotNull(capturedPrompt);
        Assert.Contains("cats", capturedPrompt);
    }

    [Fact]
    public async Task Execute_WithNoInput_UsesEmptyPrompt()
    {
        string? capturedPrompt = null;
        var ai = new Mock<IAiProvider>();
        ai.Setup(x => x.IsAvailable).Returns(true);
        ai.Setup(x => x.EnhanceAsync(It.IsAny<string>(), It.IsAny<string?>(), It.IsAny<int>(), It.IsAny<double>(), It.IsAny<CancellationToken>()))
          .Callback<string, string?, int, double, CancellationToken>((prompt, _, _, _, _) => capturedPrompt = prompt)
          .ReturnsAsync("random joke");

        var command = new JokeCommand(aiProvider: ai.Object, emptyPrompt: "EMPTY_SENTINEL");

        await command.ExecuteAsync(EmptyContext);

        Assert.Equal("EMPTY_SENTINEL", capturedPrompt);
    }

    [Fact]
    public async Task Execute_WithDefaultResponses_ReturnsValidMessage()
    {
        var command = new JokeCommand();

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }
}
