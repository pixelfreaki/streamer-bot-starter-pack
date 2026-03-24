using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class FollowAgeCommandTests
{
    private static CommandContext ContextFor(string user, string input = "") =>
        new() { UserName = user, Input = input };

    [Fact]
    public void Name_IsFollowAge()
    {
        Assert.Equal("followage", new FollowAgeCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new FollowAgeCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_WithTarget_IncludesTargetInMessage()
    {
        var command = new FollowAgeCommand();

        var result = await command.ExecuteAsync(ContextFor("mod", "pixelfreaki"));

        Assert.Contains("pixelfreaki", result.Message);
    }
}
