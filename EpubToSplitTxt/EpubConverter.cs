namespace EpubToSplitTxt.Services;

/// <summary>
/// Epub 转换器：负责解析 Epub 文件并提取纯文本
/// </summary>
public class EpubConverter
{
    /// <summary>
    /// 转换 Epub 文件为纯文本并保存
    /// </summary>
    /// <param name="epubPath">Epub 文件路径</param>
    /// <param name="outputPath">输出文本文件路径</param>
    /// <returns>统计信息（总章节数，总字符数）</returns>
    public async Task<(int ChapterCount, int TotalChars)> ConvertToTextAsync(string epubPath, string outputPath)
    {
        Console.WriteLine($"[INFO] 开始解析 Epub: {Path.GetFileName(epubPath)}");
        
        // 使用 EpubReader 读取 Epub 文件
        EpubBook book = await EpubReader.ReadBookAsync(epubPath);
        
        var textBuilder = new StringBuilder();
        int chapterCount = 0;

        // 优先使用 ReadingOrder
        var readingOrder = book.ReadingOrder;
        
        if (readingOrder != null && readingOrder.Count > 0)
        {
            foreach (var contentFile in readingOrder)
            {
                string htmlContent = contentFile.Content;
                string cleanText = SanitizeHtml(htmlContent);
                
                if (!string.IsNullOrWhiteSpace(cleanText))
                {
                    textBuilder.AppendLine(cleanText);
                    textBuilder.AppendLine();
                    chapterCount++;
                }
            }
        }
        else
        {
            // 备用方案：从 Content.Html 读取所有 HTML 文件
            Console.WriteLine("[INFO] ReadingOrder 为空，尝试从 HTML 内容读取...");
            
            var htmlFiles = book.Content.Html.Local;
            if (htmlFiles != null)
            {
                foreach (var htmlFile in htmlFiles)
                {
                    string htmlContent = htmlFile.Value.Content;
                    string cleanText = SanitizeHtml(htmlContent);
                    
                    if (!string.IsNullOrWhiteSpace(cleanText))
                    {
                        textBuilder.AppendLine(cleanText);
                        textBuilder.AppendLine();
                        chapterCount++;
                    }
                }
            }
        }

        // 确保输出目录存在
        var outputDir = Path.GetDirectoryName(outputPath);
        if (!string.IsNullOrEmpty(outputDir) && !Directory.Exists(outputDir))
        {
            Directory.CreateDirectory(outputDir);
        }

        // 保存为 UTF-8 无 BOM 编码的文本文件
        var utf8WithoutBom = new UTF8Encoding(false);
        await File.WriteAllTextAsync(outputPath, textBuilder.ToString(), utf8WithoutBom);

        int totalChars = textBuilder.Length;
        Console.WriteLine($"[INFO] Epub 解析完成，共包含 {chapterCount} 个 HTML 章节，总字符数: {totalChars}");
        
        return (chapterCount, totalChars);
    }

    /// <summary>
    /// 清洗 HTML 内容，去除标签并转换实体
    /// </summary>
    /// <param name="html">HTML 内容</param>
    /// <returns>纯文本内容</returns>
    private string SanitizeHtml(string html)
    {
        if (string.IsNullOrWhiteSpace(html))
        {
            return string.Empty;
        }

        var doc = new HtmlDocument();
        doc.LoadHtml(html);

        // 直接使用 InnerText 提取所有文本
        string text = doc.DocumentNode.InnerText;
        
        // 转换 HTML 实体
        text = HtmlEntity.DeEntitize(text);

        // 清理多余的空白字符
        text = CleanWhitespace(text);

        return text;
    }

    /// <summary>
    /// 递归提取节点中的文本
    /// </summary>
    private void ExtractTextFromNode(HtmlNode node, StringBuilder textBuilder)
    {
        if (node.NodeType == HtmlNodeType.Text)
        {
            // 文本节点直接添加
            string text = node.InnerText;
            if (!string.IsNullOrWhiteSpace(text))
            {
                textBuilder.Append(text);
            }
        }
        else if (node.NodeType == HtmlNodeType.Element)
        {
            // 对于某些块级元素，添加换行
            if (IsBlockElement(node.Name))
            {
                textBuilder.AppendLine();
            }

            // 递归处理子节点
            foreach (var child in node.ChildNodes)
            {
                ExtractTextFromNode(child, textBuilder);
            }

            // 块级元素后再添加换行
            if (IsBlockElement(node.Name))
            {
                textBuilder.AppendLine();
            }
        }
    }

    /// <summary>
    /// 判断是否为块级元素
    /// </summary>
    private bool IsBlockElement(string tagName)
    {
        var blockElements = new HashSet<string>
        {
            "p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
            "br", "hr", "blockquote", "pre", "ul", "ol", "li"
        };
        return blockElements.Contains(tagName.ToLower());
    }

    /// <summary>
    /// 清理多余的空白字符
    /// </summary>
    private string CleanWhitespace(string text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return string.Empty;
        }

        // 移除零宽字符和控制字符
        var sb = new StringBuilder();
        foreach (char c in text)
        {
            // 保留正常字符、中英文标点、换行符
            if (!char.IsControl(c) || c == '\n' || c == '\r' || c == '\t')
            {
                sb.Append(c);
            }
        }

        // 规范化换行符
        text = sb.ToString().Replace("\r\n", "\n").Replace("\r", "\n");

        // 移除连续的空行（保留最多一个空行）
        while (text.Contains("\n\n\n"))
        {
            text = text.Replace("\n\n\n", "\n\n");
        }

        return text.Trim();
    }
}
