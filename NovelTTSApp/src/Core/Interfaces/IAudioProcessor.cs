using NovelTTSApp.Core.Entities;

namespace NovelTTSApp.Core.Interfaces;

/// <summary>
/// 音频处理器接口
/// </summary>
public interface IAudioProcessor
{
    /// <summary>
    /// 合并多个音频片段
    /// </summary>
    Task<string> MergeAudioSegmentsAsync(
        IEnumerable<AudioSegment> segments, 
        string outputPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// 转换音频格式
    /// </summary>
    Task<string> ConvertFormatAsync(
        string inputPath, 
        AudioFormat targetFormat,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// 获取音频时长
    /// </summary>
    Task<double> GetDurationAsync(string audioPath, CancellationToken cancellationToken = default);

    /// <summary>
    /// 截取音频片段
    /// </summary>
    Task<string> TrimAudioAsync(
        string inputPath, 
        TimeSpan startTime, 
        TimeSpan duration,
        string outputPath,
        CancellationToken cancellationToken = default);
}
