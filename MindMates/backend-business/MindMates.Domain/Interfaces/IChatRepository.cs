using MindMates.Domain.Entities;

namespace MindMates.Domain.Interfaces;

public interface IChatRepository
{
    // Sessions
    Task<IEnumerable<ChatSession>> GetSessionsByUserIdAsync(Guid userId);
    Task<ChatSession?> GetSessionByIdAsync(Guid sessionId);
    Task<ChatSession> CreateSessionAsync(ChatSession session);
    Task<ChatSession> UpdateSessionAsync(ChatSession session);
    Task DeleteSessionAsync(Guid sessionId);

    // Messages
    Task<IEnumerable<ChatMessage>> GetMessagesBySessionIdAsync(Guid sessionId);
    Task<ChatMessage> CreateMessageAsync(ChatMessage message);
}
