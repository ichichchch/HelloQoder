namespace EpubToSplitTxt.Services;

/// <summary>
/// 文本切分器：负责按章节切分文本文件
/// </summary>
public class TextSplitter
{
    private readonly Regex _chapterRegex;
    private readonly int _minChapterLength;

    /// <summary>
    /// 构造函数
    /// </summary>
    /// <param name="chapterRegexPattern">章节匹配正则表达式</param>
    /// <param name="minChapterLength">最小章节长度</param>
    public TextSplitter(string chapterRegexPattern, int minChapterLength)
    {
        // 使用 Compiled 选项提升性能，使用 Multiline 处理多行模式
        _chapterRegex = new Regex(chapterRegexPattern, RegexOptions.Compiled | RegexOptions.Multiline, TimeSpan.FromSeconds(1));
        _minChapterLength = minChapterLength;
    }

    /// <summary>
    /// 切分文本文件为多个章节文件
    /// </summary>
    /// <param name="textFilePath">全本文本文件路径</param>
    /// <param name="outputFolder">输出目录</param>
    /// <param name="bookName">书名（用于创建子文件夹）</param>
    /// <returns>统计信息（生成文件数，平均章节长度）</returns>
    public async Task<(int FileCount, int AvgChapterLength)> SplitTextAsync(string textFilePath, string outputFolder, string bookName)
    {
        Console.WriteLine($"[INFO] 开始章节切分，使用正则: {_chapterRegex}");

        // 为每本书创建独立子文件夹
        string cleanBookName = SanitizeFileName(bookName);
        string bookOutputFolder = Path.Combine(outputFolder, cleanBookName);
        
        if (!Directory.Exists(bookOutputFolder))
        {
            Directory.CreateDirectory(bookOutputFolder);
        }

        var chapters = new List<ChapterInfo>();
        var currentChapter = new StringBuilder();
        string? currentChapterTitle = null;
        int lineNumber = 0;
        bool hasPrologue = false; // 是否有前言/楔子

        // 使用 StreamReader 逐行流式处理，避免大文件内存溢出
        using (var reader = new StreamReader(textFilePath, Encoding.UTF8))
        {
            string? line;
            while ((line = await reader.ReadLineAsync()) != null)
            {
                lineNumber++;

                // 尝试匹配章节标题
                var match = _chapterRegex.Match(line.Trim());
                
                if (match.Success && !string.IsNullOrWhiteSpace(line.Trim()))
                {
                    // 匹配到新章节标题
                    string newChapterTitle = line.Trim();

                    // 保存上一个章节（如果有内容）
                    if (currentChapter.Length > 0)
                    {
                        string title = currentChapterTitle ?? (hasPrologue ? "前言" : "楔子");
                        chapters.Add(new ChapterInfo
                        {
                            Title = title,
                            Content = currentChapter.ToString()
                        });

                        if (currentChapterTitle == null)
                        {
                            hasPrologue = true;
                        }
                    }

                    // 开始新章节
                    currentChapterTitle = newChapterTitle;
                    currentChapter.Clear();
                    currentChapter.AppendLine(newChapterTitle); // 章节标题也包含在内容中
                }
                else
                {
                    // 非章节标题，追加到当前章节
                    currentChapter.AppendLine(line);
                }
            }

            // 保存最后一个章节
            if (currentChapter.Length > 0)
            {
                string title = currentChapterTitle ?? "全文";
                chapters.Add(new ChapterInfo
                {
                    Title = title,
                    Content = currentChapter.ToString()
                });
            }
        }

        // 如果没有检测到任何章节
        if (chapters.Count == 0)
        {
            Console.WriteLine("[WARN] 全本文本中未检测到任何章节标题");
            return (0, 0);
        }

        // 写入章节文件
        int totalChars = 0;
        int fileIndex = 0;
        var utf8WithoutBom = new UTF8Encoding(false);

        foreach (var chapter in chapters)
        {
            int chapterLength = chapter.Content.Length;

            // 如果章节过小，记录警告但仍然保存
            if (chapterLength < _minChapterLength)
            {
                Console.WriteLine($"[WARN] 章节文件过小 (< {_minChapterLength} 字): {chapter.Title}，可能是正则误判");
            }

            // 生成文件名：序列号_章节标题.txt
            string sanitizedTitle = SanitizeFileName(chapter.Title);
            string fileName = $"{fileIndex:D3}_{sanitizedTitle}.txt";
            string filePath = Path.Combine(bookOutputFolder, fileName);

            // 写入文件（UTF-8 无 BOM）
            await File.WriteAllTextAsync(filePath, chapter.Content, utf8WithoutBom);

            totalChars += chapterLength;
            fileIndex++;
        }

        int avgChapterLength = chapters.Count > 0 ? totalChars / chapters.Count : 0;
        Console.WriteLine($"[INFO] 切分完成：共生成 {chapters.Count} 个 TXT 文件，平均每章 {avgChapterLength} 字");

        return (chapters.Count, avgChapterLength);
    }

    /// <summary>
    /// 清洗文件名，移除非法字符
    /// </summary>
    private string SanitizeFileName(string fileName)
    {
        if (string.IsNullOrWhiteSpace(fileName))
        {
            return "未命名";
        }

        // 移除文件系统非法字符
        char[] invalidChars = Path.GetInvalidFileNameChars();
        var sanitized = new StringBuilder();

        foreach (char c in fileName)
        {
            if (Array.IndexOf(invalidChars, c) >= 0 || c == '\\' || c == '/' || c == ':' || 
                c == '*' || c == '?' || c == '"' || c == '<' || c == '>' || c == '|')
            {
                sanitized.Append('_');
            }
            else
            {
                sanitized.Append(c);
            }
        }

        string result = sanitized.ToString().Trim();

        // 限制文件名长度
        if (result.Length > 50)
        {
            result = result.Substring(0, 50);
        }

        return string.IsNullOrWhiteSpace(result) ? "未命名" : result;
    }
}

/// <summary>
/// 章节信息
/// </summary>
internal class ChapterInfo
{
    public string Title { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
}
