using Moq;
using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class TopCommandTests
{
    private static CommandContext ContextFor(string user) =>
        new() { UserName = user };

    private static TopCommand BuildCommand(IStreamElementsService? se = null) =>
        new("top", "🏆 Top:", "#{rank} {username} — {points} pts", "StreamElements not configured", 5, se);

    [Fact]
    public void Name_IsTop()
    {
        Assert.Equal("top", BuildCommand().Name);
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
    public async Task Execute_WithTopUsers_ReturnsFormattedList()
    {
        var top = new List<(string, long)> { ("alice", 5000L), ("bob", 3000L), ("carol", 1000L) };

        var mock = new Mock<IStreamElementsService>();
        mock.Setup(s => s.IsAvailable).Returns(true);
        mock.Setup(s => s.GetTopAsync(5, default)).ReturnsAsync((IReadOnlyList<(string, long)>)top);

        var result = await BuildCommand(mock.Object).ExecuteAsync(ContextFor("viewer"));

        Assert.True(result.Success);
        Assert.Contains("alice", result.Message);
        Assert.Contains("5000", result.Message);
        Assert.Contains("bob", result.Message);
    }

    [Fact]
    public async Task Execute_WhenTopIsEmpty_ReturnsFail()
    {
        var mock = new Mock<IStreamElementsService>();
        mock.Setup(s => s.IsAvailable).Returns(true);
        mock.Setup(s => s.GetTopAsync(5, default)).ReturnsAsync((IReadOnlyList<(string, long)>)[]);

        var result = await BuildCommand(mock.Object).ExecuteAsync(ContextFor("viewer"));

        Assert.False(result.Success);
    }
}
