using Moq;
using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class EightBallCommandTests
{
    private static readonly HashSet<string> ValidResponses =
    [
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes \u2013 definitely",
        "You may rely on it",
        "As I see it, yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",
        "Reply hazy, try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful"
    ];

    private static CommandContext EmptyContext => new();

    [Fact]
    public async Task Execute_WithNoAiProvider_ReturnsValidResponse()
    {
        var command = new EightBallCommand();

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.Contains(result.Message, ValidResponses);
    }

    [Fact]
    public async Task Execute_WithUnavailableAiProvider_ReturnsLocalResponse()
    {
        var ai = new Mock<IAiProvider>();
        ai.Setup(x => x.IsAvailable).Returns(false);

        var command = new EightBallCommand(aiProvider: ai.Object);

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.Contains(result.Message, ValidResponses);
        ai.Verify(x => x.EnhanceAsync(It.IsAny<string>(), It.IsAny<string?>(), It.IsAny<CancellationToken>()), Times.Never);
    }

    [Fact]
    public async Task Execute_WithAvailableAiProvider_ReturnsEnhancedResponse()
    {
        var ai = new Mock<IAiProvider>();
        ai.Setup(x => x.IsAvailable).Returns(true);
        ai.Setup(x => x.EnhanceAsync(It.IsAny<string>(), It.IsAny<string?>(), It.IsAny<CancellationToken>()))
          .ReturnsAsync("The stars align in your favor!");

        var command = new EightBallCommand(aiProvider: ai.Object);

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.Equal("The stars align in your favor!", result.Message);
    }

    [Fact]
    public async Task Execute_WhenAiReturnsNull_FallsBackToLocalResponse()
    {
        var ai = new Mock<IAiProvider>();
        ai.Setup(x => x.IsAvailable).Returns(true);
        ai.Setup(x => x.EnhanceAsync(It.IsAny<string>(), It.IsAny<string?>(), It.IsAny<CancellationToken>()))
          .ReturnsAsync((string?)null);

        var command = new EightBallCommand(aiProvider: ai.Object);

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.Contains(result.Message, ValidResponses);
    }
}
