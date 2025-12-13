using System.Text.RegularExpressions;
using Microsoft.Extensions.Logging;

namespace NovelTTSApp.Infrastructure.Services;

/// <summary>
/// 文本分段器实现
/// </summary>
public partial class TextSegmenter(ILogger<TextSegmenter> logger) : ITextSegmenter
{
    /// <inheritdoc/>
    public Task<List<TextSegment>> SegmentAsync(string content, int maxSegmentLength = 500, CancellationToken cancellationToken = default)
    {
        logger.LogInformation("Segmenting text with max length: {MaxLength}", maxSegmentLength);

        var cleanedContent = CleanText(content);
        var segments = new List<TextSegment>();

        // Split by paragraphs first
        var paragraphs = ParagraphSplit().Split(cleanedContent)
            .Where(p => !string.IsNullOrWhiteSpace(p))
            .ToList();

        var currentText = new System.Text.StringBuilder();
        var segmentIndex = 0;

        foreach (var paragraph in paragraphs)
        {
            cancellationToken.ThrowIfCancellationRequested();

            // If current paragraph alone exceeds max length, split by sentences
            if (paragraph.Length > maxSegmentLength)
            {
                // Save current accumulated text first
                if (currentText.Length > 0)
                {
                    segments.Add(new TextSegment
                    {
                        Index = segmentIndex++,
                        Text = currentText.ToString().Trim()
                    });
                    currentText.Clear();
                }

                // Split long paragraph by sentences
                var sentences = SentenceSplit().Split(paragraph);
                foreach (var sentence in sentences)
                {
                    var trimmedSentence = sentence.Trim();
                    if (string.IsNullOrEmpty(trimmedSentence)) continue;

                    if (currentText.Length + trimmedSentence.Length > maxSegmentLength && currentText.Length > 0)
                    {
                        segments.Add(new TextSegment
                        {
                            Index = segmentIndex++,
                            Text = currentText.ToString().Trim()
                        });
                        currentText.Clear();
                    }
                    currentText.Append(trimmedSentence);
                }
            }
            else
            {
                // Check if adding this paragraph exceeds max length
                if (currentText.Length + paragraph.Length > maxSegmentLength && currentText.Length > 0)
                {
                    segments.Add(new TextSegment
                    {
                        Index = segmentIndex++,
                        Text = currentText.ToString().Trim()
                    });
                    currentText.Clear();
                }
                currentText.AppendLine(paragraph);
            }
        }

        // Don't forget the last segment
        if (currentText.Length > 0)
        {
            segments.Add(new TextSegment
            {
                Index = segmentIndex,
                Text = currentText.ToString().Trim()
            });
        }

        logger.LogInformation("Text segmented into {Count} segments", segments.Count);
        return Task.FromResult(segments);
    }

    /// <inheritdoc/>
    public string CleanText(string text)
    {
        if (string.IsNullOrWhiteSpace(text))
            return string.Empty;

        // Remove HTML tags
        text = HtmlTags().Replace(text, " ");
        
        // Normalize whitespace
        text = MultipleSpaces().Replace(text, " ");
        text = MultipleNewLines().Replace(text, "\n\n");
        
        // Remove special characters that might affect TTS
        text = SpecialChars().Replace(text, "");
        
        return text.Trim();
    }

    [GeneratedRegex(@"\n\s*\n")]
    private static partial Regex ParagraphSplit();

    [GeneratedRegex(@"(?<=[。！？.!?])\s*")]
    private static partial Regex SentenceSplit();

    [GeneratedRegex(@"<[^>]+>")]
    private static partial Regex HtmlTags();

    [GeneratedRegex(@"[ \t]+")]
    private static partial Regex MultipleSpaces();

    [GeneratedRegex(@"\n{3,}")]
    private static partial Regex MultipleNewLines();

    [GeneratedRegex(@"[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？、；：""''（）【】《》\-—…,.!?;:'()\[\]<>]")]
    private static partial Regex SpecialChars();
}
