namespace NovelTTSApp.Infrastructure.Services;

/// <summary>
/// 智谱 GLM-4-Voice TTS服务实现
/// </summary>
public class ZhipuTtsService(
    ILogger<ZhipuTtsService> logger,
    HttpClient httpClient,
    IOptions<AISettings> aiSettings,
    IOptions<PathSettings> pathSettings) : ITtsService
{
    private readonly AISettings _aiSettings = aiSettings.Value;
    private readonly PathSettings _pathSettings = pathSettings.Value;

    // Polly重试策略 - 包含 HTTP 429 处理
    private readonly ResiliencePipeline _resiliencePipeline = new ResiliencePipelineBuilder()
        .AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(2),
            BackoffType = DelayBackoffType.Exponential,
            ShouldHandle = new PredicateBuilder()
                .Handle<HttpRequestException>()
                .Handle<TaskCanceledException>()
        })
        .Build();

    /// <inheritdoc/>
    public async Task<AudioSegment> GenerateSpeechAsync(
        string text,
        int segmentIndex,
        VoiceReference? voiceReference = null,
        CancellationToken cancellationToken = default)
    {
        logger.LogInformation("Generating speech for segment {Index}, text length: {Length}", segmentIndex, text.Length);

        var audioSegment = new AudioSegment
        {
            SegmentIndex = segmentIndex,
            SourceText = text,
            Status = AudioGenerationStatus.Generating
        };

        try
        {
            // Ensure temp directory exists
            Directory.CreateDirectory(_pathSettings.TempFolder);

            var audioData = await _resiliencePipeline.ExecuteAsync(async ct =>
            {
                return await CallZhipuTtsApiAsync(text, voiceReference, ct);
            }, cancellationToken);

            // Save audio to file
            var fileName = $"segment_{segmentIndex:D4}_{Guid.NewGuid():N}.mp3";
            var filePath = Path.Combine(_pathSettings.TempFolder, fileName);
            
            await File.WriteAllBytesAsync(filePath, audioData, cancellationToken);

            audioSegment.AudioFilePath = filePath;
            audioSegment.Status = AudioGenerationStatus.Completed;
            audioSegment.DurationSeconds = EstimateDuration(audioData.Length);

            logger.LogInformation("Speech generated successfully for segment {Index}, saved to {Path}", 
                segmentIndex, filePath);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to generate speech for segment {Index}", segmentIndex);
            audioSegment.Status = AudioGenerationStatus.Failed;
            audioSegment.ErrorMessage = ex.Message;
        }

        return audioSegment;
    }

    /// <inheritdoc/>
    public async IAsyncEnumerable<byte[]> StreamSpeechAsync(
        string text,
        VoiceReference? voiceReference = null,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        logger.LogInformation("Streaming speech generation for text length: {Length}", text.Length);

        var request = await CreateTtsRequestAsync(text, voiceReference, stream: true, cancellationToken);
        
        using var requestMessage = new HttpRequestMessage(HttpMethod.Post, $"{_aiSettings.Endpoint}audio/speech");
        requestMessage.Headers.Add("Authorization", $"Bearer {_aiSettings.ApiKey}");
        requestMessage.Content = new StringContent(JsonSerializer.Serialize(request), Encoding.UTF8, "application/json");

        using var response = await httpClient.SendAsync(requestMessage, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
        response.EnsureSuccessStatusCode();

        await using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
        var buffer = new byte[8192];
        int bytesRead;

        while ((bytesRead = await stream.ReadAsync(buffer, cancellationToken)) > 0)
        {
            var chunk = new byte[bytesRead];
            Array.Copy(buffer, chunk, bytesRead);
            yield return chunk;
        }
    }

    private async Task<byte[]> CallZhipuTtsApiAsync(
        string text, 
        VoiceReference? voiceReference,
        CancellationToken cancellationToken)
    {
        var request = await CreateTtsRequestAsync(text, voiceReference, cancellationToken: cancellationToken);

        using var requestMessage = new HttpRequestMessage(HttpMethod.Post, $"{_aiSettings.Endpoint}audio/speech");
        requestMessage.Headers.Add("Authorization", $"Bearer {_aiSettings.ApiKey}");
        requestMessage.Content = new StringContent(JsonSerializer.Serialize(request), Encoding.UTF8, "application/json");

        using var response = await httpClient.SendAsync(requestMessage, cancellationToken);
        
        if (!response.IsSuccessStatusCode)
        {
            var errorContent = await response.Content.ReadAsStringAsync(cancellationToken);
            logger.LogError("TTS API error: {StatusCode} - {Content}", response.StatusCode, errorContent);
            throw new HttpRequestException($"TTS API returned {response.StatusCode}: {errorContent}");
        }

        return await response.Content.ReadAsByteArrayAsync(cancellationToken);
    }

    private async Task<ZhipuTtsRequest> CreateTtsRequestAsync(string text, VoiceReference? voiceReference, bool stream = false, CancellationToken cancellationToken = default)
    {
        var request = new ZhipuTtsRequest
        {
            Model = _aiSettings.ModelId,
            Input = text,
            Stream = stream
        };

        // If voice reference is provided, use voice cloning
        if (voiceReference != null && File.Exists(voiceReference.AudioFilePath))
        {
            var audioBytes = await File.ReadAllBytesAsync(voiceReference.AudioFilePath, cancellationToken);
            request.ReferenceAudio = Convert.ToBase64String(audioBytes);
        }

        return request;
    }

    private static double EstimateDuration(int audioByteSize)
    {
        // Rough estimation: MP3 at 128kbps = 16KB per second
        return audioByteSize / 16000.0;
    }
}

/// <summary>
/// 智谱TTS请求模型
/// </summary>
public class ZhipuTtsRequest
{
    [JsonPropertyName("model")]
    public string Model { get; set; } = "glm-4-voice";

    [JsonPropertyName("input")]
    public string Input { get; set; } = string.Empty;

    [JsonPropertyName("voice")]
    public string Voice { get; set; } = "alloy";

    [JsonPropertyName("response_format")]
    public string ResponseFormat { get; set; } = "mp3";

    [JsonPropertyName("speed")]
    public double Speed { get; set; } = 1.0;

    [JsonPropertyName("stream")]
    public bool Stream { get; set; }

    [JsonPropertyName("reference_audio")]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? ReferenceAudio { get; set; }
}
