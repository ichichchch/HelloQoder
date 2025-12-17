using MindMates.Application.DTOs;
using MindMates.Application.Services;
using MindMates.Domain.Entities;
using MindMates.Domain.Interfaces;

namespace MindMates.Infrastructure.Services;

public class ChatService : IChatService
{
    private readonly IChatRepository _chatRepository;
    private readonly IAiService _aiService;

    public ChatService(IChatRepository chatRepository, IAiService aiService)
    {
        _chatRepository = chatRepository;
        _aiService = aiService;
    }

    public async Task<IEnumerable<ChatSessionDto>> GetSessionsAsync(Guid userId)
    {
        var sessions = await _chatRepository.GetSessionsByUserIdAsync(userId);
        return sessions.Select(MapSessionToDto);
    }

    public async Task<ChatSessionDto> GetSessionAsync(Guid sessionId, Guid userId)
    {
        var session = await _chatRepository.GetSessionByIdAsync(sessionId);
        if (session == null || session.UserId != userId)
        {
            throw new KeyNotFoundException("会话不存在");
        }
        return MapSessionToDto(session);
    }

    public async Task<ChatSessionDto> CreateSessionAsync(Guid userId)
    {
        var session = new ChatSession
        {
            UserId = userId,
            Title = "新对话"
        };

        await _chatRepository.CreateSessionAsync(session);
        return MapSessionToDto(session);
    }

    public async Task DeleteSessionAsync(Guid sessionId, Guid userId)
    {
        var session = await _chatRepository.GetSessionByIdAsync(sessionId);
        if (session == null || session.UserId != userId)
        {
            throw new KeyNotFoundException("会话不存在");
        }

        await _chatRepository.DeleteSessionAsync(sessionId);
    }

    public async Task<IEnumerable<ChatMessageDto>> GetMessagesAsync(Guid sessionId, Guid userId)
    {
        var session = await _chatRepository.GetSessionByIdAsync(sessionId);
        if (session == null || session.UserId != userId)
        {
            throw new KeyNotFoundException("会话不存在");
        }

        var messages = await _chatRepository.GetMessagesBySessionIdAsync(sessionId);
        return messages.Select(MapMessageToDto);
    }

    public async Task<SendMessageResponse> SendMessageAsync(Guid sessionId, Guid userId, SendMessageRequest request)
    {
        var session = await _chatRepository.GetSessionByIdAsync(sessionId);
        if (session == null || session.UserId != userId)
        {
            throw new KeyNotFoundException("会话不存在");
        }

        // Save user message
        var userMessage = new ChatMessage
        {
            SessionId = sessionId,
            Role = "user",
            Content = request.Content
        };
        await _chatRepository.CreateMessageAsync(userMessage);

        // Get chat history for context
        var history = await _chatRepository.GetMessagesBySessionIdAsync(sessionId);
        var historyTuples = history.Select(m => (m.Role, m.Content));

        // Get AI response
        var aiResponse = await _aiService.GetResponseAsync(request.Content, historyTuples);

        // Save AI message
        var aiMessage = new ChatMessage
        {
            SessionId = sessionId,
            Role = "assistant",
            Content = aiResponse.Content,
            Intent = aiResponse.Intent,
            IsCrisis = aiResponse.IsCrisis
        };
        await _chatRepository.CreateMessageAsync(aiMessage);

        // Update session
        session.LastMessage = aiResponse.Content.Length > 50 
            ? aiResponse.Content[..50] + "..." 
            : aiResponse.Content;
        
        // Generate title from first user message
        if (session.Title == "新对话")
        {
            session.Title = request.Content.Length > 20 
                ? request.Content[..20] + "..." 
                : request.Content;
        }
        
        await _chatRepository.UpdateSessionAsync(session);

        return new SendMessageResponse(
            MapMessageToDto(userMessage),
            MapMessageToDto(aiMessage)
        );
    }

    private static ChatSessionDto MapSessionToDto(ChatSession session) => new(
        session.Id,
        session.UserId,
        session.Title,
        session.LastMessage,
        session.CreatedAt,
        session.UpdatedAt
    );

    private static ChatMessageDto MapMessageToDto(ChatMessage message) => new(
        message.Id,
        message.SessionId,
        message.Role,
        message.Content,
        message.CreatedAt,
        message.IsCrisis || message.Intent != null 
            ? new MessageMetadata(message.Intent, message.IsCrisis) 
            : null
    );
}
