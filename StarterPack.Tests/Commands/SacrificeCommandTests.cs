using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class SacrificeCommandTests
{
    private static CommandContext ContextFor(string user) => new() { UserName = user };

    [Fact]
    public void Name_IsSacrifice()
    {
        Assert.Equal("sacrifice", new SacrificeCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new SacrificeCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_WithCustomMessage_ReplacesUserPlaceholder()
    {
        var command = new SacrificeCommand(twitch: "%user% was sacrificed!");

        var result = await command.ExecuteAsync(ContextFor("pixelfreaki"));

        Assert.Contains("pixelfreaki", result.Message);
        Assert.DoesNotContain("%user%", result.Message);
    }
}
