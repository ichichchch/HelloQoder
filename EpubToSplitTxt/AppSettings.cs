namespace EpubToSplitTxt.Config;

/// <summary>
/// 应用程序配置模型
/// </summary>
public class AppSettings
{
    /// <summary>
    /// 文本切分配置
    /// </summary>
    public SplitterConfig Splitter { get; set; } = new();

    /// <summary>
    /// 路径配置
    /// </summary>
    public PathsConfig Paths { get; set; } = new();
}

/// <summary>
/// 文本切分器配置
/// </summary>
public class SplitterConfig
{
    /// <summary>
    /// 章标题匹配正则表达式
    /// </summary>
    public string ChapterRegex { get; set; } = string.Empty;

    /// <summary>
    /// 节标题匹配正则表达式
    /// </summary>
    public string SectionRegex { get; set; } = string.Empty;

    /// <summary>
    /// 最小章节长度（字符数）
    /// </summary>
    public int MinChapterLength { get; set; } = 100;
}

/// <summary>
/// 路径配置
/// </summary>
public class PathsConfig
{
    /// <summary>
    /// 原始 Epub 文件存放目录
    /// </summary>
    public string RawEpubFolder { get; set; } = string.Empty;

    /// <summary>
    /// 全本文本中间文件目录
    /// </summary>
    public string IntermediateTxtFolder { get; set; } = string.Empty;

    /// <summary>
    /// 章节切分输出目录
    /// </summary>
    public string SplitOutputFolder { get; set; } = string.Empty;
}
