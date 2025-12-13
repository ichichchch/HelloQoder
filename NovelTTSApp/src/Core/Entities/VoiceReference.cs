namespace NovelTTSApp.Core.Entities;

/// <summary>
/// 声音参考实体，用于声音克隆
/// </summary>
public class VoiceReference
{
    /// <summary>
    /// 唯一标识符
    /// </summary>
    public string Id { get; init; } = Guid.NewGuid().ToString();

    /// <summary>
    /// 声音名称/角色名
    /// </summary>
    public required string Name { get; init; }

    /// <summary>
    /// 参考音频文件路径
    /// </summary>
    public required string AudioFilePath { get; init; }

    /// <summary>
    /// 来源URL（如B站视频链接）
    /// </summary>
    public string? SourceUrl { get; set; }

    /// <summary>
    /// 音频时长（秒）
    /// </summary>
    public double DurationSeconds { get; set; }

    /// <summary>
    /// 描述信息
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; init; } = DateTime.UtcNow;
}
