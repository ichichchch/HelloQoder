using ALAgent.Agent.Models;
using ALAgent.Agent.Services;
using Microsoft.AspNetCore.Mvc;

namespace ALAgent.Agent.Controllers;

[ApiController]
[Route("api")]
public class ChatController : ControllerBase
{
    private readonly IAgentService _agentService;
    private readonly ILogger<ChatController> _logger;

    public ChatController(IAgentService agentService, ILogger<ChatController> logger)
    {
        _agentService = agentService;
        _logger = logger;
    }

    [HttpPost("chat")]
    public async Task<ActionResult<ChatResponse>> Chat(
        [FromBody] ChatRequest request,
        CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Received chat request: {Prompt}", request.Prompt[..Math.Min(100, request.Prompt.Length)]);
            
            var response = await _agentService.ChatAsync(request, cancellationToken);
            
            return Ok(response);
        }
        catch (OperationCanceledException)
        {
            _logger.LogInformation("Request was cancelled");
            return StatusCode(499, new { error = "Request cancelled" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing chat request");
            return StatusCode(500, new { error = ex.Message });
        }
    }
}
