using StarterPack.Commands;
using StarterPack.Core.Interfaces;
using StarterPack.Core.Models;

var commands = new Dictionary<string, ICommand>(StringComparer.OrdinalIgnoreCase)
{
    ["8ball"] = new EightBallCommand()
};

Console.WriteLine("Streamer.bot Runner — type !<command> [input] or 'exit' to quit");
Console.WriteLine($"Available commands: {string.Join(", ", commands.Keys.Select(k => $"!{k}"))}");
Console.WriteLine();

while (true)
{
    Console.Write("> ");
    string? line = Console.ReadLine();

    if (line is null || line.Equals("exit", StringComparison.OrdinalIgnoreCase))
        break;

    if (!line.StartsWith('!'))
    {
        Console.WriteLine("Commands must start with !");
        continue;
    }

    string[] parts = line[1..].Split(' ', 2);
    string name = parts[0];
    string input = parts.Length > 1 ? parts[1] : string.Empty;

    if (!commands.TryGetValue(name, out ICommand? command))
    {
        Console.WriteLine($"Unknown command: !{name}");
        continue;
    }

    var context = new CommandContext { UserName = "local", Input = input };
    var result = await command.ExecuteAsync(context);

    Console.WriteLine(result.Success ? result.Message : $"[error] {result.Message}");
}
