namespace NovelTTSApp.Core.Interfaces;

/// <summary>
/// Bilibili音频下载器接口
/// </summary>
public interface IBilibiliDownloader
{
    /// <summary>
    /// 从B站视频提取音频
    /// </summary>
    Task<string> ExtractAudioAsync(
        string videoUrl, 
        string outputDirectory,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// 从B站视频创建声音参考
    /// </summary>
    Task<VoiceReference> CreateVoiceReferenceAsync(
        string videoUrl,
        string voiceName,
        TimeSpan? startTime = null,
        TimeSpan? duration = null,
        CancellationToken cancellationToken = default);
}
