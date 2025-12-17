namespace MindMates.Domain.Interfaces;

public interface IAiService
{
    Task<AiResponse> GetResponseAsync(string message, IEnumerable<(string Role, string Content)> history);
}

public record AiResponse(
    string Content,
    string? Intent,
    bool IsCrisis
);
