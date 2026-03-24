using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class SetTitleCommandTests
{
    private static CommandContext ContextFor(string user, string input = "") =>
        new() { UserName = user, Input = input };

    [Fact]
    public void Name_IsSetTitle()
    {
        Assert.Equal("settitle", new SetTitleCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new SetTitleCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer", "My Stream Title"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_IncludesTitleInMessage()
    {
        var command = new SetTitleCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer", "Playing Minecraft"));

        Assert.Contains("Playing Minecraft", result.Message);
    }
}
