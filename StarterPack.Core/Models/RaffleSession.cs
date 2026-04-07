namespace StarterPack.Core.Models;

public record RaffleSession(
    string Title,
    DateTime Date,
    int JoinedCount,
    string? Top5Winner,
    string? RankedWinner,
    string? ExtraWinner
);
