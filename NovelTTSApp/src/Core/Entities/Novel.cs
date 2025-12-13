namespace NovelTTSApp.Core.Entities;

/// <summary>
/// 小说实体，表示待转换的文本内容
/// </summary>
public class Novel
{
    /// <summary>
    /// 唯一标识符
    /// </summary>
    public string Id { get; init; } = Guid.NewGuid().ToString();

    /// <summary>
    /// 小说标题
    /// </summary>
    public required string Title { get; init; }

    /// <summary>
    /// 小说源文件路径
    /// </summary>
    public required string SourcePath { get; init; }

    /// <summary>
    /// 小说文本内容
    /// </summary>
    public string Content { get; set; } = string.Empty;

    /// <summary>
    /// 文本段落列表
    /// </summary>
    public List<TextSegment> Segments { get; set; } = [];

    /// <summary>
    /// 处理状态
    /// </summary>
    public ProcessingStatus Status { get; set; } = ProcessingStatus.Pending;

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; init; } = DateTime.UtcNow;

    /// <summary>
    /// 最后更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// 文本段落
/// </summary>
public class TextSegment
{
    /// <summary>
    /// 段落索引
    /// </summary>
    public int Index { get; init; }

    /// <summary>
    /// 段落文本内容
    /// </summary>
    public required string Text { get; init; }

    /// <summary>
    /// 段落字符数
    /// </summary>
    public int CharacterCount => Text.Length;
}

/// <summary>
/// 处理状态枚举
/// </summary>
public enum ProcessingStatus
{
    Pending,
    Processing,
    Completed,
    Failed
}
