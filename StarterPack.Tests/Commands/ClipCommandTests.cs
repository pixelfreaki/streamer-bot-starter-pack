using Xunit;
using StarterPack.Commands;
using StarterPack.Core.Models;

namespace StarterPack.Tests.Commands;

public class ClipCommandTests
{
    private static CommandContext ContextFor(string user) => new() { UserName = user };

    [Fact]
    public void Name_IsClip()
    {
        Assert.Equal("clip", new ClipCommand().Name);
    }

    [Fact]
    public async Task Execute_WhenClipSucceeds_ReturnsSuccessMessage()
    {
        var command = new ClipCommand(
            success: "🎬 {user} got {clipUrl}",
            createClip: () => "https://clips.twitch.tv/abc123");

        var result = await command.ExecuteAsync(ContextFor("pixelfreaki"));

        Assert.True(result.Success);
        Assert.Equal("🎬 pixelfreaki got https://clips.twitch.tv/abc123", result.Message);
    }

    [Fact]
    public async Task Execute_WhenClipFails_ReturnsFailureMessage()
    {
        var command = new ClipCommand(
            failure: "❌ Failed for {user}",
            createClip: () => null);

        var result = await command.ExecuteAsync(ContextFor("pixelfreaki"));

        Assert.True(result.Success);
        Assert.Equal("❌ Failed for pixelfreaki", result.Message);
    }

    [Fact]
    public async Task Execute_WhenClipReturnsEmpty_ReturnsFailureMessage()
    {
        var command = new ClipCommand(
            failure: "❌ Empty for {user}",
            createClip: () => "");

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.Contains("Empty for streamer", result.Message);
    }

    [Fact]
    public async Task Execute_ReplacesUserAndClipUrlPlaceholders()
    {
        var command = new ClipCommand(
            success: "{user} → {clipUrl}",
            createClip: () => "https://clips.twitch.tv/xyz");

        var result = await command.ExecuteAsync(ContextFor("alice"));

        Assert.Equal("alice → https://clips.twitch.tv/xyz", result.Message);
        Assert.DoesNotContain("{user}", result.Message);
        Assert.DoesNotContain("{clipUrl}", result.Message);
    }

    [Fact]
    public async Task Execute_WithDefaultMessages_ReturnsValidMessage()
    {
        var command = new ClipCommand(createClip: () => "https://clips.twitch.tv/test");

        var result = await command.ExecuteAsync(ContextFor("streamer"));

        Assert.True(result.Success);
        Assert.Contains("https://clips.twitch.tv/test", result.Message);
        Assert.DoesNotContain("{user}", result.Message);
        Assert.DoesNotContain("{clipUrl}", result.Message);
    }
}
