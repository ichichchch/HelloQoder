using NovelTTSApp.Core.Entities;

namespace NovelTTSApp.Core.Interfaces;

/// <summary>
/// 文本分段器接口
/// </summary>
public interface ITextSegmenter
{
    /// <summary>
    /// 将小说内容分割为多个段落
    /// </summary>
    Task<List<TextSegment>> SegmentAsync(string content, int maxSegmentLength = 500, CancellationToken cancellationToken = default);

    /// <summary>
    /// 清洗文本（去除特殊字符等）
    /// </summary>
    string CleanText(string text);
}
