namespace EpubToSplitTxt;

class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("=== Epub 转文本与章节切分系统 ===");
        Console.WriteLine();

        try
        {
            // 加载配置
            var config = LoadConfiguration();
            
            // 确保目录存在
            EnsureDirectoriesExist(config.Paths);

            // 查找所有 Epub 文件
            var epubFiles = Directory.GetFiles(config.Paths.RawEpubFolder, "*.epub", SearchOption.TopDirectoryOnly);
            
            if (epubFiles.Length == 0)
            {
                Console.WriteLine($"[WARN] 在 {config.Paths.RawEpubFolder} 中未找到任何 .epub 文件");
                Console.WriteLine("请将 Epub 文件放入该目录后重试。");
                return;
            }

            Console.WriteLine($"[INFO] 找到 {epubFiles.Length} 个 Epub 文件");
            Console.WriteLine();

            // 初始化组件
            var converter = new EpubConverter();
            var splitter = new TextSplitter(
                config.Splitter.ChapterRegex, 
                config.Splitter.SectionRegex,
                config.Splitter.MinChapterLength);

            // 处理每个 Epub 文件
            foreach (var epubPath in epubFiles)
            {
                await ProcessEpubFile(epubPath, converter, splitter, config);
                Console.WriteLine();
            }

            Console.WriteLine("[INFO] 所有文件处理完成！");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[ERROR] 发生错误: {ex.Message}");
            Console.WriteLine($"详细信息: {ex.StackTrace}");
        }
    }

    /// <summary>
    /// 加载配置文件
    /// </summary>
    private static AppSettings LoadConfiguration()
    {
        var basePath = AppContext.BaseDirectory;
        
        var configuration = new ConfigurationBuilder()
            .SetBasePath(basePath)
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: false)
            .Build();

        var settings = new AppSettings();
        configuration.Bind(settings);

        // 将相对路径转换为绝对路径（基于程序所在目录）
        settings.Paths.RawEpubFolder = GetAbsolutePath(basePath, settings.Paths.RawEpubFolder);
        settings.Paths.IntermediateTxtFolder = GetAbsolutePath(basePath, settings.Paths.IntermediateTxtFolder);
        settings.Paths.SplitOutputFolder = GetAbsolutePath(basePath, settings.Paths.SplitOutputFolder);

        return settings;
    }

    /// <summary>
    /// 将相对路径转换为绝对路径
    /// </summary>
    private static string GetAbsolutePath(string basePath, string path)
    {
        if (Path.IsPathRooted(path))
        {
            return path;
        }
        return Path.GetFullPath(Path.Combine(basePath, path));
    }

    /// <summary>
    /// 确保所有必要的目录存在
    /// </summary>
    private static void EnsureDirectoriesExist(PathsConfig paths)
    {
        Directory.CreateDirectory(paths.RawEpubFolder);
        Directory.CreateDirectory(paths.IntermediateTxtFolder);
        Directory.CreateDirectory(paths.SplitOutputFolder);
    }

    /// <summary>
    /// 处理单个 Epub 文件
    /// </summary>
    private static async Task ProcessEpubFile(
        string epubPath, 
        EpubConverter converter, 
        TextSplitter splitter, 
        AppSettings config)
    {
        var startTime = DateTime.Now;
        string fileName = Path.GetFileNameWithoutExtension(epubPath);
        
        Console.WriteLine($"[INFO] ========== 处理: {fileName} ==========");

        try
        {
            // 阶段 1: Epub 转纯文本
            string intermediatePath = Path.Combine(config.Paths.IntermediateTxtFolder, $"{fileName}_全本.txt");
            var (chapterCount, totalChars) = await converter.ConvertToTextAsync(epubPath, intermediatePath);

            // 阶段 2: 章节切分
            var (fileCount, avgChapterLength) = await splitter.SplitTextAsync(
                intermediatePath, 
                config.Paths.SplitOutputFolder, 
                fileName);

            var elapsed = DateTime.Now - startTime;
            Console.WriteLine($"[INFO] 处理完成，耗时: {elapsed.TotalSeconds:F2} 秒");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[ERROR] Epub 文件处理失败: {epubPath}");
            Console.WriteLine($"[ERROR] 原因: {ex.Message}");
        }
    }
}
