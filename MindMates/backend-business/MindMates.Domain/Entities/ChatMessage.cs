namespace MindMates.Domain.Entities;

public class ChatMessage
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid SessionId { get; set; }
    public required string Role { get; set; } // "user", "assistant", "system"
    public required string Content { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    // Metadata for crisis detection
    public string? Intent { get; set; }
    public bool IsCrisis { get; set; } = false;

    // Navigation properties
    public ChatSession? Session { get; set; }
}
