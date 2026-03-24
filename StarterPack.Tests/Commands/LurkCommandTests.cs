using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class LurkCommandTests
{
    private static readonly string[] TestMessages =
    [
        "{user} lurk A",
        "{user} lurk B",
        "{user} lurk C",
    ];

    private static CommandContext ContextFor(string user) => new() { UserName = user };

    [Fact]
    public void Name_IsLurk()
    {
        Assert.Equal("lurk", new LurkCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new LurkCommand(TestMessages);

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_ReplacesUserPlaceholder()
    {
        var command = new LurkCommand(TestMessages);

        var result = await command.ExecuteAsync(ContextFor("pixelfreaki"));

        Assert.Contains("pixelfreaki", result.Message);
        Assert.DoesNotContain("{user}", result.Message);
    }

    [Fact]
    public async Task Execute_MessageIsFromPool()
    {
        var command = new LurkCommand(TestMessages);
        var expected = TestMessages.Select(m => m.Replace("{user}", "streamer")).ToHashSet();

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.Contains(result.Message, expected);
    }

    [Fact]
    public async Task Execute_OverManyRuns_ReturnsAllPoolEntries()
    {
        var command = new LurkCommand(TestMessages);
        var seen = new HashSet<string>();

        for (int i = 0; i < 200; i++)
            seen.Add((await command.ExecuteAsync(ContextFor("u"))).Message);

        Assert.Equal(TestMessages.Length, seen.Count);
    }

    [Fact]
    public async Task Execute_WithDefaultMessages_ReturnsValidMessage()
    {
        var command = new LurkCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
        Assert.DoesNotContain("{user}", result.Message);
    }
}
