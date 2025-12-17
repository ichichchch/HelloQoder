using MindMates.Application.DTOs;

namespace MindMates.Application.Services;

public interface IChatService
{
    Task<IEnumerable<ChatSessionDto>> GetSessionsAsync(Guid userId);
    Task<ChatSessionDto> GetSessionAsync(Guid sessionId, Guid userId);
    Task<ChatSessionDto> CreateSessionAsync(Guid userId);
    Task DeleteSessionAsync(Guid sessionId, Guid userId);
    Task<IEnumerable<ChatMessageDto>> GetMessagesAsync(Guid sessionId, Guid userId);
    Task<SendMessageResponse> SendMessageAsync(Guid sessionId, Guid userId, SendMessageRequest request);
}
