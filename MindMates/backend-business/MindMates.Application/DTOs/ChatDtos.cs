namespace MindMates.Application.DTOs;

// Session DTOs
public record ChatSessionDto(
    Guid Id,
    Guid UserId,
    string Title,
    string? LastMessage,
    DateTime CreatedAt,
    DateTime UpdatedAt
);

// Message DTOs
public record ChatMessageDto(
    Guid Id,
    Guid SessionId,
    string Role,
    string Content,
    DateTime CreatedAt,
    MessageMetadata? Metadata
);

public record MessageMetadata(string? Intent, bool IsCrisis);

public record SendMessageRequest(string Content);

public record SendMessageResponse(ChatMessageDto UserMessage, ChatMessageDto AiMessage);
