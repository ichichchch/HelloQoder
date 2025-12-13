namespace EpubToSplitTxt.Services;

/// <summary>
/// 文本切分器：负责按章节切分文本文件（按第一节分章）
/// </summary>
public class TextSplitter
{
    private readonly Regex _sectionRegex;
    private readonly Regex _firstSectionRegex;
    private readonly int _minChapterLength;

    /// <summary>
    /// 构造函数
    /// </summary>
    /// <param name="chapterRegexPattern">章匹配正则表达式（未使用，保留兼容）</param>
    /// <param name="sectionRegexPattern">节匹配正则表达式</param>
    /// <param name="minChapterLength">最小章节长度</param>
    public TextSplitter(string chapterRegexPattern, string sectionRegexPattern, int minChapterLength)
    {
        _sectionRegex = new Regex(sectionRegexPattern, RegexOptions.Compiled | RegexOptions.Multiline, TimeSpan.FromSeconds(1));
        // 第一节作为新章的开始标志
        _firstSectionRegex = new Regex(@"^第一节[：:]", RegexOptions.Compiled);
        _minChapterLength = minChapterLength;
    }

    /// <summary>
    /// 切分文本文件为多个章节文件（按第一节分章）
    /// </summary>
    public async Task<(int FileCount, int AvgChapterLength)> SplitTextAsync(string textFilePath, string outputFolder, string bookName)
    {
        Console.WriteLine($"[INFO] 开始章节切分（按第一节分章）");
        Console.WriteLine($"[INFO] 节正则: {_sectionRegex}");

        // 为每本书创建独立子文件夹
        string cleanBookName = SanitizeFileName(bookName);
        string bookOutputFolder = Path.Combine(outputFolder, cleanBookName);
        
        if (Directory.Exists(bookOutputFolder))
        {
            Directory.Delete(bookOutputFolder, true);
        }
        Directory.CreateDirectory(bookOutputFolder);

        var chapters = new List<ChapterInfo>();
        string? currentChapterTitle = null;
        string? currentSectionTitle = null;
        var currentSectionContent = new StringBuilder();
        var currentChapterSections = new List<SectionInfo>();
        int prologueIndex = 0;

        // 使用 StreamReader 逐行流式处理
        using (var reader = new StreamReader(textFilePath, Encoding.UTF8))
        {
            string? line;
            while ((line = await reader.ReadLineAsync()) != null)
            {
                string trimmedLine = line.Trim();
                bool isSection = !string.IsNullOrWhiteSpace(trimmedLine) && _sectionRegex.Match(trimmedLine).Success;
                bool isFirstSection = !string.IsNullOrWhiteSpace(trimmedLine) && _firstSectionRegex.Match(trimmedLine).Success;

                if (isFirstSection)
                {
                    // 遇到"第一节"，开始新章
                    // 先保存当前节
                    SaveCurrentSection(currentSectionTitle, currentSectionContent, currentChapterSections, ref prologueIndex);
                    
                    // 保存当前章
                    if (currentChapterSections.Count > 0)
                    {
                        chapters.Add(new ChapterInfo
                        {
                            Title = currentChapterTitle ?? "前言",
                            Sections = new List<SectionInfo>(currentChapterSections)
                        });
                    }

                    // 使用第一节标题冒号后的内容作为章标题
                    currentChapterTitle = ExtractChapterTitle(trimmedLine);
                    currentSectionTitle = trimmedLine;
                    currentSectionContent.Clear();
                    currentSectionContent.AppendLine(trimmedLine);
                    currentChapterSections.Clear();
                    prologueIndex = 0;
                }
                else if (isSection)
                {
                    // 保存当前节
                    SaveCurrentSection(currentSectionTitle, currentSectionContent, currentChapterSections, ref prologueIndex);

                    // 开始新节
                    currentSectionTitle = trimmedLine;
                    currentSectionContent.Clear();
                    currentSectionContent.AppendLine(trimmedLine);
                }
                else
                {
                    // 普通内容
                    currentSectionContent.AppendLine(line);
                }
            }

            // 保存最后一节
            SaveCurrentSection(currentSectionTitle, currentSectionContent, currentChapterSections, ref prologueIndex);
            
            // 保存最后一章
            if (currentChapterSections.Count > 0)
            {
                chapters.Add(new ChapterInfo
                {
                    Title = currentChapterTitle ?? "前言",
                    Sections = new List<SectionInfo>(currentChapterSections)
                });
            }
        }

        if (chapters.Count == 0)
        {
            Console.WriteLine("[WARN] 未检测到任何章节");
            return (0, 0);
        }

        // 写入文件
        int totalFiles = 0;
        int totalChars = 0;
        var utf8WithoutBom = new UTF8Encoding(false);
        int chapterIndex = 0;
        int globalSectionIndex = 0;
        
        foreach (var chapter in chapters)
        {
            chapterIndex++;
            // 章文件夹名：01.第X章：标题
            string chapterFolderName = $"{chapterIndex:D2}.第{ConvertToChineseNumber(chapterIndex)}章：{SanitizeFileName(chapter.Title)}";
            string chapterFolder = Path.Combine(bookOutputFolder, chapterFolderName);
            
            if (chapter.Sections.Count == 0)
            {
                continue;
            }

            Directory.CreateDirectory(chapterFolder);

            foreach (var section in chapter.Sections)
            {
                globalSectionIndex++;
                string content = section.Content.Trim();
                if (string.IsNullOrWhiteSpace(content))
                {
                    continue;
                }

                if (content.Length < _minChapterLength)
                {
                    Console.WriteLine($"[WARN] 节文件过小: {section.Title}");
                }

                // 文件名：001.第X节：标题
                string fileName = $"{globalSectionIndex:D3}.{SanitizeFileName(section.Title)}.txt";
                string filePath = Path.Combine(chapterFolder, fileName);
                await File.WriteAllTextAsync(filePath, section.Content, utf8WithoutBom);

                totalFiles++;
                totalChars += content.Length;
            }
        }

        int avgLength = totalFiles > 0 ? totalChars / totalFiles : 0;
        Console.WriteLine($"[INFO] 切分完成：共 {chapters.Count} 章，{totalFiles} 节，平均每节 {avgLength} 字");

        return (totalFiles, avgLength);
    }

    /// <summary>
    /// 从第一节标题中提取章标题（冒号后的内容）
    /// </summary>
    private string ExtractChapterTitle(string firstSectionTitle)
    {
        // 第一节：纵身亡魔心仍不悔 -> 纵身亡魔心仍不悔
        int colonIndex = firstSectionTitle.IndexOfAny(new[] { '：', ':' });
        if (colonIndex >= 0 && colonIndex < firstSectionTitle.Length - 1)
        {
            return firstSectionTitle.Substring(colonIndex + 1).Trim();
        }
        return firstSectionTitle;
    }

    /// <summary>
    /// 将数字转换为中文数字
    /// </summary>
    private string ConvertToChineseNumber(int number)
    {
        if (number <= 0) return "零";
        
        string[] digits = { "零", "一", "二", "三", "四", "五", "六", "七", "八", "九" };
        string[] units = { "", "十", "百", "千", "万" };
        
        if (number < 10) return digits[number];
        if (number < 20) return (number == 10 ? "十" : "十" + digits[number % 10]);
        if (number < 100)
        {
            int tens = number / 10;
            int ones = number % 10;
            return digits[tens] + "十" + (ones > 0 ? digits[ones] : "");
        }
        if (number < 1000)
        {
            int hundreds = number / 100;
            int remainder = number % 100;
            string result = digits[hundreds] + "百";
            if (remainder > 0)
            {
                if (remainder < 10) result += "零" + digits[remainder];
                else result += ConvertToChineseNumber(remainder);
            }
            return result;
        }
        
        return number.ToString();
    }

    private void SaveCurrentSection(string? title, StringBuilder content, List<SectionInfo> sections, ref int prologueIndex)
    {
        if (content.Length > 0)
        {
            string sectionTitle = title ?? $"前言{(prologueIndex > 0 ? prologueIndex.ToString() : "")}"; 
            if (title == null) prologueIndex++;
            
            sections.Add(new SectionInfo
            {
                Title = sectionTitle,
                Content = content.ToString()
            });
        }
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
/// 章信息
/// </summary>
internal class ChapterInfo
{
    public string Title { get; set; } = string.Empty;
    public List<SectionInfo> Sections { get; set; } = new();
}

/// <summary>
/// 节信息
/// </summary>
internal class SectionInfo
{
    public string Title { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
}
