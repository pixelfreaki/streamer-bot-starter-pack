using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class RussianRouletteCommandTests
{
    private static CommandContext ContextFor(string user) => new() { UserName = user };

    [Fact]
    public void Name_IsRussianRoulette()
    {
        Assert.Equal("russianroulette", new RussianRouletteCommand().Name);
    }

    [Fact]
    public async Task Execute_ReturnsSuccess()
    {
        var command = new RussianRouletteCommand();

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.NotEmpty(result.Message);
    }

    [Fact]
    public async Task Execute_OverManyRuns_ReturnsBothOutcomes()
    {
        var command = new RussianRouletteCommand(
            dies:  "DIES",
            lives: "LIVES");

        var seen = new HashSet<string>();
        for (int i = 0; i < 200; i++)
        {
            var r = await command.ExecuteAsync(ContextFor("u"));
            if (r.Message.Contains("DIES"))  seen.Add("dies");
            if (r.Message.Contains("LIVES")) seen.Add("lives");
        }

        Assert.Contains("lives", seen);
    }
}
