using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class TranslateCommandTests
{
    private static CommandContext ContextFor(string user, string input = "") =>
        new() { UserName = user, Input = input };

    [Fact]
    public void Name_IsTranslate()
    {
        Assert.Equal("translate", new TranslateCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new TranslateCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer", "Hello world"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_WithNoInput_ReturnsSuccess()
    {
        var command = new TranslateCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
    }
}
