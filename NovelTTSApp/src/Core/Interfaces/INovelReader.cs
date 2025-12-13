using NovelTTSApp.Core.Entities;

namespace NovelTTSApp.Core.Interfaces;

/// <summary>
/// 小说阅读器接口
/// </summary>
public interface INovelReader
{
    /// <summary>
    /// 从文件读取小说
    /// </summary>
    Task<Novel> ReadFromFileAsync(string filePath, CancellationToken cancellationToken = default);

    /// <summary>
    /// 从URL抓取小说内容
    /// </summary>
    Task<Novel> FetchFromUrlAsync(string url, CancellationToken cancellationToken = default);
}
