using System.Net.Http.Json;
using Microsoft.Extensions.Configuration;
using MindMates.Domain.Interfaces;

namespace MindMates.Infrastructure.Services;

public class AiServiceClient : IAiService
{
    private readonly HttpClient _httpClient;
    private readonly string _aiServiceUrl;

    public AiServiceClient(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _aiServiceUrl = configuration["AiService:Url"] ?? "http://localhost:8000";
    }

    public async Task<AiResponse> GetResponseAsync(string message, IEnumerable<(string Role, string Content)> history)
    {
        var request = new
        {
            message,
            history = history.Select(h => new { role = h.Role, content = h.Content }).ToList()
        };

        try
        {
            var response = await _httpClient.PostAsJsonAsync($"{_aiServiceUrl}/api/chat", request);
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<AiServiceResponse>();
            
            return new AiResponse(
                result?.Content ?? "抱歉，我暂时无法回应，请稍后再试。",
                result?.Intent,
                result?.IsCrisis ?? false
            );
        }
        catch (Exception)
        {
            // Fallback response if AI service is unavailable
            return new AiResponse(
                "抱歉，我暂时无法连接到服务，请稍后再试。如果您正在经历困难，请拨打心理援助热线：400-161-9995。",
                null,
                false
            );
        }
    }

    private record AiServiceResponse(string Content, string? Intent, bool IsCrisis);
}
