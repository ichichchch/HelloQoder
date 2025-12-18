using Microsoft.AspNetCore.Mvc;
using MindMates.Application.DTOs;
using MindMates.Application.Services;

namespace MindMates.Api.Controllers;

[ApiController]
[Route("api/chat")]
public class ChatController : ControllerBase
{
    private readonly IChatService _chatService;
    // 默认用户ID（已移除登录认证）
    private static readonly Guid DefaultUserId = Guid.Parse("00000000-0000-0000-0000-000000000001");

    public ChatController(IChatService chatService)
    {
        _chatService = chatService;
    }

    [HttpGet("sessions")]
    public async Task<ActionResult<IEnumerable<ChatSessionDto>>> GetSessions()
    {
        var userId = GetUserId();
        var sessions = await _chatService.GetSessionsAsync(userId);
        return Ok(sessions);
    }

    [HttpGet("sessions/{sessionId:guid}")]
    public async Task<ActionResult<ChatSessionDto>> GetSession(Guid sessionId)
    {
        var userId = GetUserId();
        try
        {
            var session = await _chatService.GetSessionAsync(sessionId, userId);
            return Ok(session);
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
    }

    [HttpPost("sessions")]
    public async Task<ActionResult<ChatSessionDto>> CreateSession()
    {
        var userId = GetUserId();
        var session = await _chatService.CreateSessionAsync(userId);
        return Ok(session);
    }

    [HttpDelete("sessions/{sessionId:guid}")]
    public async Task<ActionResult> DeleteSession(Guid sessionId)
    {
        var userId = GetUserId();
        try
        {
            await _chatService.DeleteSessionAsync(sessionId, userId);
            return NoContent();
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
    }

    [HttpGet("sessions/{sessionId:guid}/messages")]
    public async Task<ActionResult<IEnumerable<ChatMessageDto>>> GetMessages(Guid sessionId)
    {
        var userId = GetUserId();
        try
        {
            var messages = await _chatService.GetMessagesAsync(sessionId, userId);
            return Ok(messages);
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
    }

    [HttpPost("sessions/{sessionId:guid}/messages")]
    public async Task<ActionResult<SendMessageResponse>> SendMessage(Guid sessionId, [FromBody] SendMessageRequest request)
    {
        var userId = GetUserId();
        try
        {
            var response = await _chatService.SendMessageAsync(sessionId, userId, request);
            return Ok(response);
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
    }

    private Guid GetUserId()
    {
        return DefaultUserId;
    }
}
