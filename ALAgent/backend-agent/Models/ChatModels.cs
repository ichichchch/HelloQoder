namespace ALAgent.Agent.Models;

public record ChatRequest(
    string Prompt,
    string? Context,
    string WorkspacePath,
    List<ConversationMessage> ConversationHistory
);

public record ChatResponse(
    string Thought,
    List<ToolCallInfo>? ToolCalls,
    string? Response,
    bool Done
);

public record ConversationMessage(
    string Role,
    string Content,
    long Timestamp,
    string? ToolCallId = null,
    string? ToolName = null
);

public record ToolCallInfo(
    string Id,
    string Name,
    Dictionary<string, object> Arguments,
    bool RequiresApproval
);

public record RagQueryRequest(
    string Query,
    string WorkspacePath,
    int TopK = 5
);

public record RagQueryResponse(
    List<CodeChunk> Chunks
);

public record CodeChunk(
    string Content,
    string FilePath,
    int StartLine,
    int EndLine,
    double Score,
    Dictionary<string, object>? Metadata = null
);
