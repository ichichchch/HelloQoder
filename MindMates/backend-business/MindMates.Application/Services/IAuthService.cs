using MindMates.Application.DTOs;

namespace MindMates.Application.Services;

public interface IAuthService
{
    Task<AuthResponse> LoginAsync(LoginRequest request);
    Task<AuthResponse> RegisterAsync(RegisterRequest request);
    Task<UserDto> GetProfileAsync(Guid userId);
    Task<UserDto> UpdateProfileAsync(Guid userId, UpdateUserRequest request);
    Task ChangePasswordAsync(Guid userId, ChangePasswordRequest request);
}
