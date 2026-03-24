using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class InfoCommandTests
{
    private static CommandContext ContextFor(string user) => new() { UserName = user };

    [Theory]
    [InlineData("pc")]
    [InlineData("gear")]
    [InlineData("peripherals")]
    public void Name_ReflectsConstructorArg(string name)
    {
        Assert.Equal(name, new InfoCommand(name, "msg").Name);
    }

    [Fact]
    public async Task Execute_ReturnsMessage()
    {
        var cmd = new InfoCommand("pc", "CPU: Ryzen 9 9950X3D");

        var result = await cmd.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.Equal("CPU: Ryzen 9 9950X3D", result.Message);
    }

    [Fact]
    public async Task Execute_ReplacesUserPlaceholder()
    {
        var cmd = new InfoCommand("test", "@{user} here is the info!");

        var result = await cmd.ExecuteAsync(ContextFor("pixelfreaki"));

        Assert.Equal("@pixelfreaki here is the info!", result.Message);
        Assert.DoesNotContain("{user}", result.Message);
    }
}
