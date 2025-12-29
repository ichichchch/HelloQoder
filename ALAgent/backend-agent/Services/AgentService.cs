using ALAgent.Agent.Models;
using Microsoft.Extensions.Options;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;

namespace ALAgent.Agent.Services;

public class AgentService : IAgentService
{
    private readonly Kernel _kernel;
    private readonly IRagClient _ragClient;
    private readonly AgentSettings _settings;
    private readonly ILogger<AgentService> _logger;

    private const string SystemPrompt = """
        You are an expert coding assistant. You help users understand and modify code.
        
        When analyzing code or answering questions:
        1. First think through the problem step by step
        2. Use the available tools to gather information when needed
        3. Provide clear, actionable responses
        
        Available tools:
        - list_files: List files in a directory
        - read_file: Read the contents of a file
        - write_file: Write content to a file (requires user approval)
        - execute_command: Execute a shell command (requires user approval)
        - search_code: Search for code patterns in the workspace
        
        Always explain your reasoning before taking actions.
        """;

    public AgentService(
        Kernel kernel,
        IRagClient ragClient,
        IOptions<AgentSettings> settings,
        ILogger<AgentService> logger)
    {
        _kernel = kernel;
        _ragClient = ragClient;
        _settings = settings.Value;
        _logger = logger;
    }

    public async Task<ChatResponse> ChatAsync(ChatRequest request, CancellationToken cancellationToken = default)
    {
        try
        {
            // Build chat history
            var chatHistory = new ChatHistory();
            chatHistory.AddSystemMessage(SystemPrompt);

            // Add context from RAG if available
            var ragContext = await GetRagContextAsync(request.Prompt, request.WorkspacePath, cancellationToken);
            if (!string.IsNullOrEmpty(ragContext))
            {
                chatHistory.AddSystemMessage($"Relevant code context:\n{ragContext}");
            }

            // Add conversation history
            foreach (var msg in request.ConversationHistory)
            {
                switch (msg.Role.ToLowerInvariant())
                {
                    case "user":
                        chatHistory.AddUserMessage(msg.Content);
                        break;
                    case "assistant":
                        chatHistory.AddAssistantMessage(msg.Content);
                        break;
                    case "tool":
                        // Add tool results as system messages for context
                        chatHistory.AddSystemMessage($"Tool result ({msg.ToolName}): {msg.Content}");
                        break;
                }
            }

            // Add current user message
            chatHistory.AddUserMessage(request.Prompt);

            // Configure execution settings
            var executionSettings = new OpenAIPromptExecutionSettings
            {
                MaxTokens = _settings.MaxTokens,
                Temperature = _settings.Temperature,
                ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions
            };

            // Get chat completion service
            var chatService = _kernel.GetRequiredService<IChatCompletionService>();
            
            // Execute with function calling
            var result = await chatService.GetChatMessageContentAsync(
                chatHistory,
                executionSettings,
                _kernel,
                cancellationToken);

            // Parse response
            var thought = ExtractThought(result.Content ?? string.Empty);
            var toolCalls = ExtractToolCalls(result);
            var response = ExtractResponse(result.Content ?? string.Empty);

            return new ChatResponse(
                Thought: thought,
                ToolCalls: toolCalls,
                Response: response,
                Done: toolCalls == null || toolCalls.Count == 0
            );
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing chat request");
            throw;
        }
    }

    private async Task<string?> GetRagContextAsync(string query, string workspacePath, CancellationToken cancellationToken)
    {
        try
        {
            var response = await _ragClient.QueryAsync(
                new RagQueryRequest(query, workspacePath, TopK: 5),
                cancellationToken);

            if (response.Chunks == null || response.Chunks.Count == 0)
                return null;

            var contextBuilder = new System.Text.StringBuilder();
            foreach (var chunk in response.Chunks)
            {
                contextBuilder.AppendLine($"// File: {chunk.FilePath} (lines {chunk.StartLine}-{chunk.EndLine})");
                contextBuilder.AppendLine(chunk.Content);
                contextBuilder.AppendLine();
            }

            return contextBuilder.ToString();
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to get RAG context");
            return null;
        }
    }

    private static string ExtractThought(string content)
    {
        // Extract thinking/reasoning from the response
        if (content.Contains("<think>") && content.Contains("</think>"))
        {
            var start = content.IndexOf("<think>") + 7;
            var end = content.IndexOf("</think>");
            return content[start..end].Trim();
        }
        
        // If no explicit thinking tags, return first part of response as thought
        var lines = content.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        return lines.Length > 0 ? lines[0] : string.Empty;
    }

    private static List<ToolCallInfo>? ExtractToolCalls(ChatMessageContent result)
    {
        // Tool calls are handled automatically by Semantic Kernel with AutoInvokeKernelFunctions
        // This method is for manual tool call extraction if needed
        return null;
    }

    private static string? ExtractResponse(string content)
    {
        // Remove thinking section if present
        if (content.Contains("</think>"))
        {
            var end = content.IndexOf("</think>") + 8;
            return content[end..].Trim();
        }
        return content;
    }
}
