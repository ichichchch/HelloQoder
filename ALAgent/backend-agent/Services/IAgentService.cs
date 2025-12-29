using ALAgent.Agent.Models;

namespace ALAgent.Agent.Services;

public interface IAgentService
{
    Task<ChatResponse> ChatAsync(ChatRequest request, CancellationToken cancellationToken = default);
}
