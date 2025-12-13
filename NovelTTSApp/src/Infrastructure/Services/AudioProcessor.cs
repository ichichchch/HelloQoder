namespace NovelTTSApp.Infrastructure.Services;

/// <summary>
/// 音频处理器实现 - 使用NAudio
/// </summary>
public class AudioProcessor(
    ILogger<AudioProcessor> logger,
    IOptions<PathSettings> pathSettings) : IAudioProcessor
{
    private readonly PathSettings _pathSettings = pathSettings.Value;

    /// <inheritdoc/>
    public async Task<string> MergeAudioSegmentsAsync(
        IEnumerable<AudioSegment> segments,
        string outputPath,
        CancellationToken cancellationToken = default)
    {
        var orderedSegments = segments
            .Where(s => s.Status == AudioGenerationStatus.Completed && !string.IsNullOrEmpty(s.AudioFilePath))
            .OrderBy(s => s.SegmentIndex)
            .ToList();

        if (orderedSegments.Count == 0)
        {
            throw new InvalidOperationException("No valid audio segments to merge");
        }

        logger.LogInformation("Merging {Count} audio segments to {OutputPath}", orderedSegments.Count, outputPath);

        // Ensure output directory exists
        var outputDir = Path.GetDirectoryName(outputPath);
        if (!string.IsNullOrEmpty(outputDir))
        {
            Directory.CreateDirectory(outputDir);
        }

        await Task.Run(() =>
        {
            using var outputStream = new MemoryStream();
            
            foreach (var segment in orderedSegments)
            {
                cancellationToken.ThrowIfCancellationRequested();

                if (!File.Exists(segment.AudioFilePath))
                {
                    logger.LogWarning("Audio file not found: {Path}", segment.AudioFilePath);
                    continue;
                }

                using var reader = new Mp3FileReader(segment.AudioFilePath);
                
                // For the first file, we need to write the complete MP3 including headers
                if (outputStream.Length == 0)
                {
                    reader.CopyTo(outputStream);
                }
                else
                {
                    // Skip MP3 headers for subsequent files
                    Mp3Frame? frame;
                    while ((frame = reader.ReadNextFrame()) != null)
                    {
                        outputStream.Write(frame.RawData, 0, frame.RawData.Length);
                    }
                }
            }

            // Write to output file
            File.WriteAllBytes(outputPath, outputStream.ToArray());
        }, cancellationToken);

        logger.LogInformation("Audio merge completed: {OutputPath}", outputPath);
        return outputPath;
    }

    /// <inheritdoc/>
    public async Task<string> ConvertFormatAsync(
        string inputPath,
        AudioFormat targetFormat,
        CancellationToken cancellationToken = default)
    {
        logger.LogInformation("Converting {Input} to {Format}", inputPath, targetFormat);

        var outputPath = Path.ChangeExtension(inputPath, targetFormat.ToString().ToLowerInvariant());

        await Task.Run(() =>
        {
            using var reader = new AudioFileReader(inputPath);
            
            switch (targetFormat)
            {
                case AudioFormat.Wav:
                    WaveFileWriter.CreateWaveFile(outputPath, reader);
                    break;
                case AudioFormat.Mp3:
                    // MP3 encoding requires additional library (NAudio.Lame)
                    // For now, just copy if already MP3
                    if (inputPath.EndsWith(".mp3", StringComparison.OrdinalIgnoreCase))
                    {
                        File.Copy(inputPath, outputPath, overwrite: true);
                    }
                    else
                    {
                        throw new NotSupportedException("MP3 encoding requires NAudio.Lame library");
                    }
                    break;
                default:
                    throw new NotSupportedException($"Format {targetFormat} is not supported");
            }
        }, cancellationToken);

        logger.LogInformation("Conversion completed: {OutputPath}", outputPath);
        return outputPath;
    }

    /// <inheritdoc/>
    public Task<double> GetDurationAsync(string audioPath, CancellationToken cancellationToken = default)
    {
        logger.LogDebug("Getting duration for: {Path}", audioPath);

        return Task.Run(() =>
        {
            using var reader = new AudioFileReader(audioPath);
            return reader.TotalTime.TotalSeconds;
        }, cancellationToken);
    }

    /// <inheritdoc/>
    public async Task<string> TrimAudioAsync(
        string inputPath,
        TimeSpan startTime,
        TimeSpan duration,
        string outputPath,
        CancellationToken cancellationToken = default)
    {
        logger.LogInformation("Trimming audio {Input} from {Start} for {Duration}", 
            inputPath, startTime, duration);

        await Task.Run(() =>
        {
            using var reader = new AudioFileReader(inputPath);
            
            // Calculate positions
            var startPos = (long)(reader.WaveFormat.AverageBytesPerSecond * startTime.TotalSeconds);
            var bytesToRead = (long)(reader.WaveFormat.AverageBytesPerSecond * duration.TotalSeconds);

            reader.Position = startPos;

            // Create a trimmed wave provider
            var trimmedProvider = new TrimmedWaveProvider(reader, bytesToRead);

            // Ensure output directory exists
            var outputDir = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrEmpty(outputDir))
            {
                Directory.CreateDirectory(outputDir);
            }

            WaveFileWriter.CreateWaveFile(outputPath, trimmedProvider);
        }, cancellationToken);

        logger.LogInformation("Audio trimmed: {OutputPath}", outputPath);
        return outputPath;
    }
}

/// <summary>
/// 用于裁剪音频的Wave Provider
/// </summary>
internal class TrimmedWaveProvider : IWaveProvider
{
    private readonly IWaveProvider _source;
    private readonly long _maxBytes;
    private long _bytesRead;

    public TrimmedWaveProvider(IWaveProvider source, long maxBytes)
    {
        _source = source;
        _maxBytes = maxBytes;
        WaveFormat = source.WaveFormat;
    }

    public WaveFormat WaveFormat { get; }

    public int Read(byte[] buffer, int offset, int count)
    {
        var bytesRemaining = _maxBytes - _bytesRead;
        if (bytesRemaining <= 0)
            return 0;

        var toRead = (int)Math.Min(count, bytesRemaining);
        var bytesActuallyRead = _source.Read(buffer, offset, toRead);
        _bytesRead += bytesActuallyRead;
        return bytesActuallyRead;
    }
}
