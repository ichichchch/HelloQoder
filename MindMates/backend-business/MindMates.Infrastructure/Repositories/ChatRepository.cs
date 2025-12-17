using Microsoft.EntityFrameworkCore;
using MindMates.Domain.Entities;
using MindMates.Domain.Interfaces;
using MindMates.Infrastructure.Data;

namespace MindMates.Infrastructure.Repositories;

public class ChatRepository : IChatRepository
{
    private readonly AppDbContext _context;

    public ChatRepository(AppDbContext context)
    {
        _context = context;
    }

    // Sessions
    public async Task<IEnumerable<ChatSession>> GetSessionsByUserIdAsync(Guid userId)
    {
        return await _context.ChatSessions
            .Where(s => s.UserId == userId)
            .OrderByDescending(s => s.UpdatedAt)
            .ToListAsync();
    }

    public async Task<ChatSession?> GetSessionByIdAsync(Guid sessionId)
    {
        return await _context.ChatSessions.FindAsync(sessionId);
    }

    public async Task<ChatSession> CreateSessionAsync(ChatSession session)
    {
        _context.ChatSessions.Add(session);
        await _context.SaveChangesAsync();
        return session;
    }

    public async Task<ChatSession> UpdateSessionAsync(ChatSession session)
    {
        session.UpdatedAt = DateTime.UtcNow;
        _context.ChatSessions.Update(session);
        await _context.SaveChangesAsync();
        return session;
    }

    public async Task DeleteSessionAsync(Guid sessionId)
    {
        var session = await _context.ChatSessions.FindAsync(sessionId);
        if (session != null)
        {
            _context.ChatSessions.Remove(session);
            await _context.SaveChangesAsync();
        }
    }

    // Messages
    public async Task<IEnumerable<ChatMessage>> GetMessagesBySessionIdAsync(Guid sessionId)
    {
        return await _context.ChatMessages
            .Where(m => m.SessionId == sessionId)
            .OrderBy(m => m.CreatedAt)
            .ToListAsync();
    }

    public async Task<ChatMessage> CreateMessageAsync(ChatMessage message)
    {
        _context.ChatMessages.Add(message);
        await _context.SaveChangesAsync();
        return message;
    }
}
