using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class SetGameCommandTests
{
    private static CommandContext ContextFor(string user, string input = "") =>
        new() { UserName = user, Input = input };

    [Fact]
    public void Name_IsSetGame()
    {
        Assert.Equal("setgame", new SetGameCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new SetGameCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer", "Minecraft"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_IncludesGameInMessage()
    {
        var command = new SetGameCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer", "Elden Ring"));

        Assert.Contains("Elden Ring", result.Message);
    }
}
