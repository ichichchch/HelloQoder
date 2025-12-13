namespace NovelTTSApp.Infrastructure.Configuration;

/// <summary>
/// AI服务配置
/// </summary>
public class AISettings
{
    public const string SectionName = "AI";

    /// <summary>
    /// API端点地址
    /// </summary>
    public string Endpoint { get; set; } = "https://open.bigmodel.cn/api/paas/v4/";

    /// <summary>
    /// API密钥
    /// </summary>
    public string ApiKey { get; set; } = string.Empty;

    /// <summary>
    /// 模型ID
    /// </summary>
    public string ModelId { get; set; } = "glm-4-voice";
}

/// <summary>
/// Bilibili配置
/// </summary>
public class BilibiliSettings
{
    public const string SectionName = "Bilibili";

    /// <summary>
    /// Cookie用于获取高清音频
    /// </summary>
    public string? Cookie { get; set; }
}

/// <summary>
/// 路径配置
/// </summary>
public class PathSettings
{
    public const string SectionName = "Paths";

    /// <summary>
    /// 输入文件夹
    /// </summary>
    public string InputFolder { get; set; } = "./data/novels";

    /// <summary>
    /// 输出文件夹
    /// </summary>
    public string OutputFolder { get; set; } = "./data/output";

    /// <summary>
    /// 参考音频文件夹
    /// </summary>
    public string ReferenceAudioFolder { get; set; } = "./data/reference_audio";

    /// <summary>
    /// 临时文件夹
    /// </summary>
    public string TempFolder { get; set; } = "./data/temp";
}
