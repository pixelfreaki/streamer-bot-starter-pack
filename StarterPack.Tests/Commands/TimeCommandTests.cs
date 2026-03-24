using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class TimeCommandTests
{
    private static CommandContext ContextFor(string user) => new() { UserName = user };

    [Fact]
    public void Name_IsTime()
    {
        Assert.Equal("time", new TimeCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new TimeCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_WithCustomMessages_ReturnsSuccess()
    {
        var command = new TimeCommand(
            twitch:  "/me @%user% time test",
            kick:    "@%user% time test",
            youtube: "@%user% time test");

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
    }
}
