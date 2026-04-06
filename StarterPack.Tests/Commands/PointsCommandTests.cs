using Moq;
using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class PointsCommandTests
{
    private static CommandContext ContextFor(string user, string input = "") =>
        new() { UserName = user, Input = input };

    private static PointsCommand BuildCommand(IStreamElementsService? se = null) =>
        new("⭐ {target} has {points} points (rank #{rank})", "StreamElements not configured", "Could not find points for {target}", se);

    [Fact]
    public void Name_IsPoints()
    {
        Assert.Equal("points", BuildCommand().Name);
    }

    [Fact]
    public async Task Execute_WithoutService_ReturnsFail()
    {
        var result = await BuildCommand().ExecuteAsync(ContextFor("viewer"));

        Assert.False(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_WithUnavailableService_ReturnsFail()
    {
        var mock = new Mock<IStreamElementsService>();
        mock.Setup(s => s.IsAvailable).Returns(false);

        var result = await BuildCommand(mock.Object).ExecuteAsync(ContextFor("viewer"));

        Assert.False(result.Success);
    }

    [Fact]
    public async Task Execute_WithNoInput_UsesCallerUsername()
    {
        var mock = new Mock<IStreamElementsService>();
        mock.Setup(s => s.IsAvailable).Returns(true);
        mock.Setup(s => s.GetUserPointsAsync("viewer", default)).ReturnsAsync((1500L, 3L));

        var result = await BuildCommand(mock.Object).ExecuteAsync(ContextFor("viewer"));

        Assert.True(result.Success);
        Assert.Contains("viewer", result.Message);
        Assert.Contains("1500", result.Message);
        Assert.Contains("3", result.Message);
    }

    [Fact]
    public async Task Execute_WithInputUsername_UsesTargetUsername()
    {
        var mock = new Mock<IStreamElementsService>();
        mock.Setup(s => s.IsAvailable).Returns(true);
        mock.Setup(s => s.GetUserPointsAsync("someuser", default)).ReturnsAsync((800L, 10L));

        var result = await BuildCommand(mock.Object).ExecuteAsync(ContextFor("mod", "someuser"));

        Assert.True(result.Success);
        Assert.Contains("someuser", result.Message);
        Assert.Contains("800", result.Message);
    }

    [Fact]
    public async Task Execute_WhenApiReturnsNull_ReturnsNotFoundMessage()
    {
        var mock = new Mock<IStreamElementsService>();
        mock.Setup(s => s.IsAvailable).Returns(true);
        mock.Setup(s => s.GetUserPointsAsync(It.IsAny<string>(), default)).ReturnsAsync((ValueTuple<long, long>?)null);

        var result = await BuildCommand(mock.Object).ExecuteAsync(ContextFor("viewer"));

        Assert.False(result.Success);
        Assert.Contains("viewer", result.Message);
    }
}
