using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class FortuneCommandTests
{
    private static readonly string[] TestFortunes =
    [
        "Fortune A.",
        "Fortune B.",
        "Fortune C.",
    ];

    private static CommandContext EmptyContext => new();

    [Fact]
    public void Name_IsFortune()
    {
        Assert.Equal("fortune", new FortuneCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new FortuneCommand(TestFortunes);

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
    }

    [Fact]
    public async Task Execute_MessageIsFromPool()
    {
        var command = new FortuneCommand(TestFortunes);

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.Contains(result.Message, TestFortunes);
    }

    [Fact]
    public async Task Execute_WithDefaultFortunes_ReturnsNonEmpty()
    {
        var command = new FortuneCommand();

        var result = await command.ExecuteAsync(EmptyContext);

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_OverManyRuns_ReturnsAllPoolEntries()
    {
        var command = new FortuneCommand(TestFortunes);
        var seen = new HashSet<string>();

        for (int i = 0; i < 200; i++)
        {
            var result = await command.ExecuteAsync(EmptyContext);
            seen.Add(result.Message);
        }

        Assert.Equal(TestFortunes.Length, seen.Count);
    }
}
