using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

namespace StarterPack.Commands;

/// <summary>
/// !translate — sets fromLanguage/toLanguage variables, then C# inline calls Google Translate,
/// then platform-switch sends %translationText%.
/// This stub exists for local testing and runner registration.
/// </summary>
public class TranslateCommand : ICommand
{
    public string Name => "translate";

    public Task<CommandResult> ExecuteAsync(CommandContext context, CancellationToken cancellationToken = default)
    {
        string text = string.IsNullOrWhiteSpace(context.Input) ? "(no text)" : context.Input.Trim();
        return Task.FromResult(CommandResult.Ok($"[translate] Translating: {text} (native Streamer.bot action)"));
    }
}
