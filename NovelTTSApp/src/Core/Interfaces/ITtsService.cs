using NovelTTSApp.Core.Entities;

namespace NovelTTSApp.Core.Interfaces;

/// <summary>
/// 文本转语音服务接口
/// </summary>
public interface ITtsService
{
    /// <summary>
    /// 将文本转换为语音
    /// </summary>
    Task<AudioSegment> GenerateSpeechAsync(
        string text, 
        int segmentIndex,
        VoiceReference? voiceReference = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// 流式生成语音（实时写入）
    /// </summary>
    IAsyncEnumerable<byte[]> StreamSpeechAsync(
        string text,
        VoiceReference? voiceReference = null,
        CancellationToken cancellationToken = default);
}
