using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class SceneCommandTests
{
    private static CommandContext ContextFor(string user, string input = "") =>
        new() { UserName = user, Input = input };

    [Fact]
    public void Name_IsScene()
    {
        Assert.Equal("scene", new SceneCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new SceneCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer", "Game"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_IncludesSceneNameInMessage()
    {
        var command = new SceneCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer", "BRB"));

        Assert.Contains("BRB", result.Message);
    }
}
