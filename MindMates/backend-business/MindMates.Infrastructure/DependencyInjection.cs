using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using MindMates.Application.Services;
using MindMates.Domain.Interfaces;
using MindMates.Infrastructure.Data;
using MindMates.Infrastructure.Repositories;
using MindMates.Infrastructure.Services;

namespace MindMates.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        // Database
        services.AddDbContext<AppDbContext>(options =>
            options.UseNpgsql(configuration.GetConnectionString("DefaultConnection")));

        // Repositories
        services.AddScoped<IUserRepository, UserRepository>();
        services.AddScoped<IChatRepository, ChatRepository>();

        // Services
        services.AddScoped<IAuthService, AuthService>();
        services.AddScoped<IChatService, ChatService>();

        // AI Service Client
        services.AddHttpClient<IAiService, AiServiceClient>();

        return services;
    }
}
