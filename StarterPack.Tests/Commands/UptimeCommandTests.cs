using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class UptimeCommandTests
{
    private static CommandContext ContextFor(string user) => new() { UserName = user };

    [Fact]
    public void Name_IsUptime()
    {
        Assert.Equal("uptime", new UptimeCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new UptimeCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }
}
