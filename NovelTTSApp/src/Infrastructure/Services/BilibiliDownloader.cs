using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using NovelTTSApp.Infrastructure.Configuration;

namespace NovelTTSApp.Infrastructure.Services;

/// <summary>
/// Bilibili音频下载器实现
/// </summary>
public partial class BilibiliDownloader(
    ILogger<BilibiliDownloader> logger,
    HttpClient httpClient,
    IAudioProcessor audioProcessor,
    IOptions<BilibiliSettings> bilibiliSettings,
    IOptions<PathSettings> pathSettings) : IBilibiliDownloader
{
    private readonly BilibiliSettings _bilibiliSettings = bilibiliSettings.Value;
    private readonly PathSettings _pathSettings = pathSettings.Value;

    /// <inheritdoc/>
    public async Task<string> ExtractAudioAsync(
        string videoUrl,
        string outputDirectory,
        CancellationToken cancellationToken = default)
    {
        logger.LogInformation("Extracting audio from Bilibili video: {Url}", videoUrl);

        // Extract BV number from URL
        var bvMatch = BvIdPattern().Match(videoUrl);
        if (!bvMatch.Success)
        {
            throw new ArgumentException($"Invalid Bilibili URL: {videoUrl}");
        }
        var bvId = bvMatch.Value;

        // Ensure output directory exists
        Directory.CreateDirectory(outputDirectory);

        // Get video info
        var videoInfo = await GetVideoInfoAsync(bvId, cancellationToken);
        
        // Get audio stream URL
        var audioUrl = await GetAudioStreamUrlAsync(videoInfo.Cid, videoInfo.Bvid, cancellationToken);
        
        // Download audio
        var outputPath = Path.Combine(outputDirectory, $"{bvId}.m4a");
        await DownloadAudioAsync(audioUrl, outputPath, cancellationToken);

        logger.LogInformation("Audio extracted successfully: {Path}", outputPath);
        return outputPath;
    }

    /// <inheritdoc/>
    public async Task<VoiceReference> CreateVoiceReferenceAsync(
        string videoUrl,
        string voiceName,
        TimeSpan? startTime = null,
        TimeSpan? duration = null,
        CancellationToken cancellationToken = default)
    {
        logger.LogInformation("Creating voice reference from Bilibili video: {Url}", videoUrl);

        // Download the full audio first
        var audioPath = await ExtractAudioAsync(videoUrl, _pathSettings.ReferenceAudioFolder, cancellationToken);

        // If start time and duration specified, trim the audio
        if (startTime.HasValue && duration.HasValue)
        {
            var trimmedPath = Path.Combine(
                _pathSettings.ReferenceAudioFolder, 
                $"{voiceName}_{Guid.NewGuid():N}.wav");
            
            audioPath = await audioProcessor.TrimAudioAsync(
                audioPath, 
                startTime.Value, 
                duration.Value, 
                trimmedPath, 
                cancellationToken);
        }

        var audioDuration = await audioProcessor.GetDurationAsync(audioPath, cancellationToken);

        var voiceReference = new VoiceReference
        {
            Name = voiceName,
            AudioFilePath = audioPath,
            SourceUrl = videoUrl,
            DurationSeconds = audioDuration,
            Description = $"Voice reference from Bilibili video: {videoUrl}"
        };

        logger.LogInformation("Voice reference created: {Name} ({Duration}s)", voiceName, audioDuration);
        return voiceReference;
    }

    private async Task<BilibiliVideoInfo> GetVideoInfoAsync(string bvId, CancellationToken cancellationToken)
    {
        var apiUrl = $"https://api.bilibili.com/x/web-interface/view?bvid={bvId}";
        
        using var request = new HttpRequestMessage(HttpMethod.Get, apiUrl);
        AddBilibiliHeaders(request);

        var response = await httpClient.SendAsync(request, cancellationToken);
        response.EnsureSuccessStatusCode();

        var json = await response.Content.ReadAsStringAsync(cancellationToken);
        using var doc = JsonDocument.Parse(json);
        
        var data = doc.RootElement.GetProperty("data");
        
        return new BilibiliVideoInfo
        {
            Bvid = data.GetProperty("bvid").GetString() ?? bvId,
            Cid = data.GetProperty("cid").GetInt64(),
            Title = data.GetProperty("title").GetString() ?? "Unknown"
        };
    }

    private async Task<string> GetAudioStreamUrlAsync(long cid, string bvid, CancellationToken cancellationToken)
    {
        var apiUrl = $"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&fnval=16";
        
        using var request = new HttpRequestMessage(HttpMethod.Get, apiUrl);
        AddBilibiliHeaders(request);

        var response = await httpClient.SendAsync(request, cancellationToken);
        response.EnsureSuccessStatusCode();

        var json = await response.Content.ReadAsStringAsync(cancellationToken);
        using var doc = JsonDocument.Parse(json);

        var data = doc.RootElement.GetProperty("data");
        var dash = data.GetProperty("dash");
        var audio = dash.GetProperty("audio");
        
        // Get highest quality audio
        var audioStreams = audio.EnumerateArray().ToList();
        var bestAudio = audioStreams.OrderByDescending(a => a.GetProperty("bandwidth").GetInt32()).First();
        
        return bestAudio.GetProperty("baseUrl").GetString() 
            ?? throw new InvalidOperationException("Audio URL not found");
    }

    private async Task DownloadAudioAsync(string audioUrl, string outputPath, CancellationToken cancellationToken)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, audioUrl);
        request.Headers.Add("Referer", "https://www.bilibili.com");
        request.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");

        using var response = await httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
        response.EnsureSuccessStatusCode();

        await using var contentStream = await response.Content.ReadAsStreamAsync(cancellationToken);
        await using var fileStream = new FileStream(outputPath, FileMode.Create, FileAccess.Write, FileShare.None);
        
        await contentStream.CopyToAsync(fileStream, cancellationToken);
    }

    private void AddBilibiliHeaders(HttpRequestMessage request)
    {
        request.Headers.Add("Referer", "https://www.bilibili.com");
        request.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
        
        if (!string.IsNullOrEmpty(_bilibiliSettings.Cookie))
        {
            request.Headers.Add("Cookie", _bilibiliSettings.Cookie);
        }
    }

    [GeneratedRegex(@"BV[\w]+")]
    private static partial Regex BvIdPattern();
}

internal class BilibiliVideoInfo
{
    public required string Bvid { get; init; }
    public required long Cid { get; init; }
    public required string Title { get; init; }
}
