namespace NovelTTSApp.Core.Entities;

/// <summary>
/// 音频片段实体
/// </summary>
public class AudioSegment
{
    /// <summary>
    /// 唯一标识符
    /// </summary>
    public string Id { get; init; } = Guid.NewGuid().ToString();

    /// <summary>
    /// 对应的文本段落索引
    /// </summary>
    public int SegmentIndex { get; init; }

    /// <summary>
    /// 原始文本内容
    /// </summary>
    public required string SourceText { get; init; }

    /// <summary>
    /// 音频文件路径
    /// </summary>
    public string? AudioFilePath { get; set; }

    /// <summary>
    /// 音频时长（秒）
    /// </summary>
    public double DurationSeconds { get; set; }

    /// <summary>
    /// 音频格式
    /// </summary>
    public AudioFormat Format { get; set; } = AudioFormat.Mp3;

    /// <summary>
    /// 生成状态
    /// </summary>
    public AudioGenerationStatus Status { get; set; } = AudioGenerationStatus.Pending;

    /// <summary>
    /// 错误信息
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; init; } = DateTime.UtcNow;
}

/// <summary>
/// 音频格式
/// </summary>
public enum AudioFormat
{
    Wav,
    Mp3,
    Ogg
}

/// <summary>
/// 音频生成状态
/// </summary>
public enum AudioGenerationStatus
{
    Pending,
    Generating,
    Completed,
    Failed
}
