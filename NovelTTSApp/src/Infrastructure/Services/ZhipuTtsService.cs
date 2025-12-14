namespace NovelTTSApp.Infrastructure.Services;

/// <summary>
/// 智谱 GLM-4-Voice TTS服务实现
/// 使用 chat/completions 端点进行语音生成
/// 支持音色复刻功能
/// </summary>
public class ZhipuTtsService(
    ILogger<ZhipuTtsService> logger,
    HttpClient httpClient,
    IOptions<AISettings> aiSettings,
    IOptions<PathSettings> pathSettings) : ITtsService
{
    private readonly AISettings _aiSettings = aiSettings.Value;
    private readonly PathSettings _pathSettings = pathSettings.Value;
    
    // 缓存已克隆的音色ID，避免重复克隆
    private string? _cachedVoiceId;
    private bool _cloneAttempted = false;

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

            // Save audio to file (WAV format from GLM-4-Voice)
            var fileName = $"segment_{segmentIndex:D4}_{Guid.NewGuid():N}.wav";
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

        // Get cloned voice ID if voice reference is provided
        string? voiceId = null;
        if (voiceReference != null && File.Exists(voiceReference.AudioFilePath))
        {
            voiceId = await GetOrCreateClonedVoiceAsync(voiceReference, cancellationToken);
        }

        // GLM-TTS streaming via audio/speech endpoint
        var ttsRequest = new
        {
            model = "glm-tts",
            input = text,
            voice = string.IsNullOrEmpty(voiceId) ? "female" : voiceId,
            speed = 1.0,
            volume = 1.0,
            response_format = "pcm",
            encode_format = "base64",
            stream = true
        };
        
        using var requestMessage = new HttpRequestMessage(HttpMethod.Post, $"{_aiSettings.Endpoint}audio/speech");
        requestMessage.Headers.Add("Authorization", $"Bearer {_aiSettings.ApiKey}");
        requestMessage.Content = new StringContent(JsonSerializer.Serialize(ttsRequest), Encoding.UTF8, "application/json");

        using var response = await httpClient.SendAsync(requestMessage, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
        response.EnsureSuccessStatusCode();

        await using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
        using var reader = new StreamReader(stream);

        while (!reader.EndOfStream)
        {
            var line = await reader.ReadLineAsync(cancellationToken);
            if (string.IsNullOrEmpty(line) || !line.StartsWith("data:"))
                continue;

            var jsonData = line[5..].Trim();
            if (string.IsNullOrEmpty(jsonData))
                continue;

            var streamResponse = JsonSerializer.Deserialize<GlmTtsStreamResponse>(jsonData);
            var content = streamResponse?.Choices?.FirstOrDefault()?.Delta?.Content;
            
            if (!string.IsNullOrEmpty(content))
            {
                yield return Convert.FromBase64String(content);
            }

            if (streamResponse?.Choices?.FirstOrDefault()?.FinishReason == "stop")
                break;
        }
    }

    private async Task<byte[]> CallZhipuTtsApiAsync(
        string text, 
        VoiceReference? voiceReference,
        CancellationToken cancellationToken)
    {
        // Step 1: If voice reference is provided and not yet cloned, call voice clone API first
        string? voiceId = null;
        if (voiceReference != null && File.Exists(voiceReference.AudioFilePath))
        {
            voiceId = await GetOrCreateClonedVoiceAsync(voiceReference, cancellationToken);
        }

        // Step 2: Call GLM-TTS API (audio/speech endpoint)
        var ttsRequest = new
        {
            model = "glm-tts",
            input = text,
            voice = string.IsNullOrEmpty(voiceId) ? "female" : voiceId,
            speed = 1.0,
            volume = 1.0,
            response_format = "wav"
        };

        if (!string.IsNullOrEmpty(voiceId))
        {
            logger.LogInformation("Using cloned voice_id: {VoiceId}", voiceId);
        }

        using var requestMessage = new HttpRequestMessage(HttpMethod.Post, $"{_aiSettings.Endpoint}audio/speech");
        requestMessage.Headers.Add("Authorization", $"Bearer {_aiSettings.ApiKey}");
        requestMessage.Content = new StringContent(JsonSerializer.Serialize(ttsRequest), Encoding.UTF8, "application/json");

        using var response = await httpClient.SendAsync(requestMessage, cancellationToken);
        
        if (!response.IsSuccessStatusCode)
        {
            var errorContent = await response.Content.ReadAsStringAsync(cancellationToken);
            logger.LogError("TTS API error: {StatusCode} - {Content}", response.StatusCode, errorContent);
            throw new HttpRequestException($"TTS API returned {response.StatusCode}: {errorContent}");
        }

        // Response is binary audio data (WAV format)
        var audioData = await response.Content.ReadAsByteArrayAsync(cancellationToken);
        return audioData;
    }

    /// <summary>
    /// 获取或创建克隆音色
    /// </summary>
    private async Task<string> GetOrCreateClonedVoiceAsync(
        VoiceReference voiceReference,
        CancellationToken cancellationToken)
    {
        // Return cached voice ID if available
        if (!string.IsNullOrEmpty(_cachedVoiceId))
        {
            logger.LogInformation("Using cached cloned voice: {VoiceId}", _cachedVoiceId);
            return _cachedVoiceId;
        }

        // If we already tried and failed, don't retry
        if (_cloneAttempted)
        {
            return string.Empty;
        }
        _cloneAttempted = true;

        logger.LogInformation("Creating cloned voice from reference audio: {Path}", voiceReference.AudioFilePath);

        // Step 1: Upload audio file to get file_id
        var fileId = await UploadAudioFileAsync(voiceReference.AudioFilePath, cancellationToken);
        if (string.IsNullOrEmpty(fileId))
        {
            logger.LogWarning("Failed to upload audio file. Falling back to default voice.");
            return string.Empty;
        }

        // Step 2: Call voice clone API with file_id
        var uniqueVoiceName = $"v{DateTime.UtcNow:yyMMddHHmmss}{Guid.NewGuid():N}"[..30];
        var cloneRequest = new
        {
            model = "glm-tts-clone",
            voice_name = uniqueVoiceName,
            file_id = fileId,
            text = "你好，这是一段示例音频的文本内容，用于音色复刻参考。",
            input = "欢迎使用我们的音色复刻服务，这将生成与示例音频相同音色的语音。"
        };

        using var requestMessage = new HttpRequestMessage(HttpMethod.Post, $"{_aiSettings.Endpoint}voice/clone");
        requestMessage.Headers.Add("Authorization", $"Bearer {_aiSettings.ApiKey}");
        requestMessage.Content = new StringContent(JsonSerializer.Serialize(cloneRequest), Encoding.UTF8, "application/json");

        using var response = await httpClient.SendAsync(requestMessage, cancellationToken);
        var responseContent = await response.Content.ReadAsStringAsync(cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            logger.LogWarning("Voice clone API failed: {StatusCode} - {Content}. Falling back to default voice.", 
                response.StatusCode, responseContent);
            return string.Empty;
        }

        // Parse response to get voice_id
        var cloneResponse = JsonSerializer.Deserialize<VoiceCloneResponse>(responseContent);
        var voiceId = cloneResponse?.Voice ?? cloneResponse?.VoiceId ?? cloneResponse?.Id;

        if (string.IsNullOrEmpty(voiceId))
        {
            logger.LogWarning("Voice clone response did not contain voice_id. Response: {Content}", responseContent);
            return string.Empty;
        }

        logger.LogInformation("Voice cloned successfully: {VoiceId}", voiceId);
        _cachedVoiceId = voiceId;
        return voiceId;
    }

    /// <summary>
    /// 上传音频文件获取 file_id
    /// </summary>
    private async Task<string?> UploadAudioFileAsync(string audioFilePath, CancellationToken cancellationToken)
    {
        logger.LogInformation("Uploading audio file: {Path}", audioFilePath);

        using var content = new MultipartFormDataContent();
        var fileBytes = await File.ReadAllBytesAsync(audioFilePath, cancellationToken);
        var fileContent = new ByteArrayContent(fileBytes);
        fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/wav");
        content.Add(fileContent, "file", Path.GetFileName(audioFilePath));
        content.Add(new StringContent("voice-clone-input"), "purpose");

        using var requestMessage = new HttpRequestMessage(HttpMethod.Post, $"{_aiSettings.Endpoint}files");
        requestMessage.Headers.Add("Authorization", $"Bearer {_aiSettings.ApiKey}");
        requestMessage.Content = content;

        using var response = await httpClient.SendAsync(requestMessage, cancellationToken);
        var responseContent = await response.Content.ReadAsStringAsync(cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            logger.LogWarning("File upload failed: {StatusCode} - {Content}", response.StatusCode, responseContent);
            return null;
        }

        var uploadResponse = JsonSerializer.Deserialize<FileUploadResponse>(responseContent);
        var fileId = uploadResponse?.Id;

        logger.LogInformation("Audio file uploaded: {FileId}", fileId);
        return fileId;
    }

    private static double EstimateDuration(int audioByteSize)
    {
        // WAV at 24000Hz, 16bit mono = 48000 bytes per second (GLM-TTS uses 24kHz)
        return audioByteSize / 48000.0;
    }
}

/// <summary>
/// GLM-TTS 流式响应模型
/// </summary>
public class GlmTtsStreamResponse
{
    [JsonPropertyName("id")]
    public string? Id { get; set; }

    [JsonPropertyName("created")]
    public long? Created { get; set; }

    [JsonPropertyName("model")]
    public string? Model { get; set; }

    [JsonPropertyName("choices")]
    public List<GlmTtsStreamChoice>? Choices { get; set; }
}

public class GlmTtsStreamChoice
{
    [JsonPropertyName("index")]
    public int Index { get; set; }

    [JsonPropertyName("delta")]
    public GlmTtsStreamDelta? Delta { get; set; }

    [JsonPropertyName("finish_reason")]
    public string? FinishReason { get; set; }
}

public class GlmTtsStreamDelta
{
    [JsonPropertyName("role")]
    public string? Role { get; set; }

    [JsonPropertyName("content")]
    public string? Content { get; set; }

    [JsonPropertyName("return_sample_rate")]
    public int? ReturnSampleRate { get; set; }
}

/// <summary>
/// 音色复刻 API 响应模型
/// </summary>
public class VoiceCloneResponse
{
    [JsonPropertyName("id")]
    public string? Id { get; set; }

    [JsonPropertyName("voice_id")]
    public string? VoiceId { get; set; }

    [JsonPropertyName("voice")]
    public string? Voice { get; set; }

    [JsonPropertyName("name")]
    public string? Name { get; set; }

    [JsonPropertyName("status")]
    public string? Status { get; set; }

    [JsonPropertyName("file_id")]
    public string? FileId { get; set; }
}

/// <summary>
/// 文件上传 API 响应模型
/// </summary>
public class FileUploadResponse
{
    [JsonPropertyName("id")]
    public string? Id { get; set; }

    [JsonPropertyName("object")]
    public string? Object { get; set; }

    [JsonPropertyName("bytes")]
    public long? Bytes { get; set; }

    [JsonPropertyName("created_at")]
    public long? CreatedAt { get; set; }

    [JsonPropertyName("filename")]
    public string? Filename { get; set; }

    [JsonPropertyName("purpose")]
    public string? Purpose { get; set; }
}
