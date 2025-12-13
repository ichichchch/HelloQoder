using Microsoft.Extensions.Logging;
using NovelTTSApp.Core.Entities;
using NovelTTSApp.Core.Interfaces;

namespace NovelTTSApp.App.Services;

/// <summary>
/// 小说处理器 - 主业务流程编排
/// </summary>
public class NovelProcessor(
    ILogger<NovelProcessor> logger,
    INovelReader novelReader,
    ITextSegmenter textSegmenter,
    ITtsService ttsService,
    IAudioProcessor audioProcessor) : INovelProcessor
{
    /// <inheritdoc/>
    public async Task<string> ProcessNovelAsync(
        string inputPath,
        string outputPath,
        VoiceReference? voiceReference = null,
        IProgress<ProcessingProgress>? progress = null,
        CancellationToken cancellationToken = default)
    {
        logger.LogInformation("Starting novel processing: {Input} -> {Output}", inputPath, outputPath);

        try
        {
            // Stage 1: Read novel
            ReportProgress(progress, "Reading Novel", 0, 0, 4, "Loading novel file...");
            var novel = await novelReader.ReadFromFileAsync(inputPath, cancellationToken);
            logger.LogInformation("Novel loaded: {Title}, {Length} characters", novel.Title, novel.Content.Length);

            // Stage 2: Segment text
            ReportProgress(progress, "Segmenting Text", 25, 1, 4, "Splitting text into segments...");
            var segments = await textSegmenter.SegmentAsync(novel.Content, 500, cancellationToken);
            novel.Segments = segments;
            logger.LogInformation("Text segmented into {Count} segments", segments.Count);

            // Stage 3: Generate audio for each segment
            ReportProgress(progress, "Generating Audio", 30, 2, 4, $"Generating speech for {segments.Count} segments...");
            var audioSegments = new List<AudioSegment>();

            for (var i = 0; i < segments.Count; i++)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var segment = segments[i];
                var segmentProgress = 30 + (50.0 * (i + 1) / segments.Count);
                ReportProgress(progress, "Generating Audio", segmentProgress, i + 1, segments.Count, 
                    $"Processing segment {i + 1}/{segments.Count}");

                var audioSegment = await ttsService.GenerateSpeechAsync(
                    segment.Text,
                    segment.Index,
                    voiceReference,
                    cancellationToken);

                audioSegments.Add(audioSegment);

                if (audioSegment.Status == AudioGenerationStatus.Failed)
                {
                    logger.LogWarning("Failed to generate audio for segment {Index}: {Error}", 
                        i, audioSegment.ErrorMessage);
                }
            }

            // Stage 4: Merge audio segments
            ReportProgress(progress, "Merging Audio", 80, 3, 4, "Combining audio segments...");
            var successfulSegments = audioSegments.Where(s => s.Status == AudioGenerationStatus.Completed).ToList();
            
            if (successfulSegments.Count == 0)
            {
                throw new InvalidOperationException("No audio segments were generated successfully");
            }

            logger.LogInformation("Merging {Count} audio segments", successfulSegments.Count);
            var finalOutputPath = await audioProcessor.MergeAudioSegmentsAsync(
                successfulSegments, 
                outputPath, 
                cancellationToken);

            // Update novel status
            novel.Status = ProcessingStatus.Completed;
            novel.UpdatedAt = DateTime.UtcNow;

            // Cleanup temp files
            await CleanupTempFilesAsync(audioSegments, cancellationToken);

            ReportProgress(progress, "Complete", 100, 4, 4, "Processing completed successfully!");
            logger.LogInformation("Novel processing completed: {Output}", finalOutputPath);

            return finalOutputPath;
        }
        catch (OperationCanceledException)
        {
            logger.LogWarning("Novel processing was cancelled");
            throw;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error processing novel: {Input}", inputPath);
            throw;
        }
    }

    /// <inheritdoc/>
    public async Task<IEnumerable<string>> ProcessBatchAsync(
        IEnumerable<string> inputPaths,
        string outputDirectory,
        VoiceReference? voiceReference = null,
        IProgress<ProcessingProgress>? progress = null,
        CancellationToken cancellationToken = default)
    {
        var inputs = inputPaths.ToList();
        logger.LogInformation("Starting batch processing: {Count} novels", inputs.Count);

        var results = new List<string>();
        
        for (var i = 0; i < inputs.Count; i++)
        {
            cancellationToken.ThrowIfCancellationRequested();

            var inputPath = inputs[i];
            var fileName = Path.GetFileNameWithoutExtension(inputPath);
            var outputPath = Path.Combine(outputDirectory, $"{fileName}.mp3");

            ReportProgress(progress, "Batch Processing", (100.0 * i) / inputs.Count, i, inputs.Count,
                $"Processing novel {i + 1}/{inputs.Count}: {fileName}");

            try
            {
                var result = await ProcessNovelAsync(
                    inputPath,
                    outputPath,
                    voiceReference,
                    null, // Don't pass progress to individual processing
                    cancellationToken);

                results.Add(result);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Failed to process novel: {Input}", inputPath);
                // Continue with next novel
            }
        }

        ReportProgress(progress, "Batch Complete", 100, inputs.Count, inputs.Count,
            $"Batch processing completed: {results.Count}/{inputs.Count} successful");

        return results;
    }

    private static void ReportProgress(
        IProgress<ProcessingProgress>? progress, 
        string stage, 
        double percent, 
        int current, 
        int total,
        string? message = null)
    {
        progress?.Report(new ProcessingProgress
        {
            Stage = stage,
            PercentComplete = percent,
            CurrentItem = current,
            TotalItems = total,
            Message = message
        });
    }

    private async Task CleanupTempFilesAsync(
        IEnumerable<AudioSegment> segments, 
        CancellationToken cancellationToken)
    {
        foreach (var segment in segments)
        {
            if (!string.IsNullOrEmpty(segment.AudioFilePath) && File.Exists(segment.AudioFilePath))
            {
                try
                {
                    await Task.Run(() => File.Delete(segment.AudioFilePath), cancellationToken);
                }
                catch (Exception ex)
                {
                    logger.LogWarning(ex, "Failed to cleanup temp file: {Path}", segment.AudioFilePath);
                }
            }
        }
    }
}
