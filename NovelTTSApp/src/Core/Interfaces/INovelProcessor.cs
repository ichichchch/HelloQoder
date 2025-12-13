using NovelTTSApp.Core.Entities;

namespace NovelTTSApp.Core.Interfaces;

/// <summary>
/// 小说处理器接口 - 主业务流程编排
/// </summary>
public interface INovelProcessor
{
    /// <summary>
    /// 处理小说，生成有声书
    /// </summary>
    Task<string> ProcessNovelAsync(
        string inputPath,
        string outputPath,
        VoiceReference? voiceReference = null,
        IProgress<ProcessingProgress>? progress = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// 批量处理小说
    /// </summary>
    Task<IEnumerable<string>> ProcessBatchAsync(
        IEnumerable<string> inputPaths,
        string outputDirectory,
        VoiceReference? voiceReference = null,
        IProgress<ProcessingProgress>? progress = null,
        CancellationToken cancellationToken = default);
}

/// <summary>
/// 处理进度信息
/// </summary>
public class ProcessingProgress
{
    /// <summary>
    /// 当前处理阶段
    /// </summary>
    public required string Stage { get; init; }

    /// <summary>
    /// 当前进度百分比 (0-100)
    /// </summary>
    public double PercentComplete { get; init; }

    /// <summary>
    /// 当前处理项的索引
    /// </summary>
    public int CurrentItem { get; init; }

    /// <summary>
    /// 总项数
    /// </summary>
    public int TotalItems { get; init; }

    /// <summary>
    /// 消息
    /// </summary>
    public string? Message { get; init; }
}
