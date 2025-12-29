using Refit;
using ALAgent.Agent.Models;

namespace ALAgent.Agent.Services;

public interface IRagClient
{
    [Post("/api/query")]
    Task<RagQueryResponse> QueryAsync([Body] RagQueryRequest request, CancellationToken cancellationToken = default);
    
    [Get("/health")]
    Task<object> HealthCheckAsync(CancellationToken cancellationToken = default);
}
