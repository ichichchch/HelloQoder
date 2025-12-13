namespace NovelTTSApp.Infrastructure.Services;

/// <summary>
/// 小说阅读器实现
/// </summary>
public partial class NovelReader(
    ILogger<NovelReader> logger,
    HttpClient httpClient) : INovelReader
{
    /// <inheritdoc/>
    public async Task<Novel> ReadFromFileAsync(string filePath, CancellationToken cancellationToken = default)
    {
        logger.LogInformation("Reading novel from file: {FilePath}", filePath);

        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException($"Novel file not found: {filePath}");
        }

        var content = await File.ReadAllTextAsync(filePath, Encoding.UTF8, cancellationToken);
        var title = Path.GetFileNameWithoutExtension(filePath);

        var novel = new Novel
        {
            Title = title,
            SourcePath = filePath,
            Content = content
        };

        logger.LogInformation("Successfully read novel '{Title}' with {Length} characters", novel.Title, content.Length);
        return novel;
    }

    /// <inheritdoc/>
    public async Task<Novel> FetchFromUrlAsync(string url, CancellationToken cancellationToken = default)
    {
        logger.LogInformation("Fetching novel from URL: {Url}", url);

        var response = await httpClient.GetAsync(url, cancellationToken);
        response.EnsureSuccessStatusCode();

        var html = await response.Content.ReadAsStringAsync(cancellationToken);
        
        var doc = new HtmlDocument();
        doc.LoadHtml(html);

        // Extract title
        var titleNode = doc.DocumentNode.SelectSingleNode("//title");
        var title = titleNode?.InnerText?.Trim() ?? "Unknown Novel";
        title = CleanTitle().Replace(title, "");

        // Extract content - try common content selectors
        var content = ExtractContent(doc);

        var novel = new Novel
        {
            Title = title,
            SourcePath = url,
            Content = content
        };

        logger.LogInformation("Successfully fetched novel '{Title}' with {Length} characters", novel.Title, content.Length);
        return novel;
    }

    private static string ExtractContent(HtmlDocument doc)
    {
        // Try common content selectors
        var selectors = new[]
        {
            "//div[@id='content']",
            "//div[@class='content']",
            "//article",
            "//div[@class='chapter-content']",
            "//div[@class='novel-content']",
            "//div[@id='chaptercontent']"
        };

        foreach (var selector in selectors)
        {
            var node = doc.DocumentNode.SelectSingleNode(selector);
            if (node != null)
            {
                var text = node.InnerText;
                // Clean up the text
                text = System.Net.WebUtility.HtmlDecode(text);
                text = text.Replace("<br>", "\n").Replace("<br/>", "\n").Replace("<br />", "\n");
                text = MultipleNewLines().Replace(text, "\n\n");
                return text.Trim();
            }
        }

        // Fallback: get body text
        var bodyNode = doc.DocumentNode.SelectSingleNode("//body");
        return bodyNode?.InnerText?.Trim() ?? string.Empty;
    }

    [GeneratedRegex(@"[\s\-_]+.*$")]
    private static partial Regex CleanTitle();

    [GeneratedRegex(@"\n{3,}")]
    private static partial Regex MultipleNewLines();
}
