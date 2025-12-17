namespace MindMates.Application.DTOs;

// Auth DTOs
public record LoginRequest(string Username, string Password);
public record RegisterRequest(string Username, string Password, string? Nickname);
public record AuthResponse(string Token, UserDto User);
public record ChangePasswordRequest(string OldPassword, string NewPassword);

// User DTOs
public record UserDto(
    Guid Id,
    string Username,
    string? Nickname,
    string? Email,
    string? Avatar,
    DateTime CreatedAt
);

public record UpdateUserRequest(string? Nickname, string? Email);
