using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class AccountAgeCommandTests
{
    private static CommandContext ContextFor(string user, string input = "") =>
        new() { UserName = user, Input = input };

    [Fact]
    public void Name_IsAccountAge()
    {
        Assert.Equal("accountage", new AccountAgeCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new AccountAgeCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_WithTarget_IncludesTargetInMessage()
    {
        var command = new AccountAgeCommand();

        var result = await command.ExecuteAsync(ContextFor("mod", "pixelfreaki"));

        Assert.Contains("pixelfreaki", result.Message);
    }

    [Fact]
    public async Task Execute_WithNoInput_FallsBackToUser()
    {
        var command = new AccountAgeCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.Contains("streamer", result.Message);
    }
}
