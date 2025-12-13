namespace NovelTTSApp.Infrastructure;

/// <summary>
/// 依赖注入扩展方法
/// </summary>
public static class DependencyInjection
{
    /// <summary>
    /// 添加Infrastructure层服务
    /// </summary>
    public static IServiceCollection AddInfrastructureServices(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        // 注册配置
        services.Configure<AISettings>(configuration.GetSection(AISettings.SectionName));
        services.Configure<BilibiliSettings>(configuration.GetSection(BilibiliSettings.SectionName));
        services.Configure<PathSettings>(configuration.GetSection(PathSettings.SectionName));

        // 注册HttpClient
        services.AddHttpClient<INovelReader, NovelReader>();
        services.AddHttpClient<ITtsService, ZhipuTtsService>();
        services.AddHttpClient<IBilibiliDownloader, BilibiliDownloader>();

        // 注册服务
        services.AddScoped<ITextSegmenter, TextSegmenter>();
        services.AddScoped<IAudioProcessor, AudioProcessor>();

        return services;
    }
}
