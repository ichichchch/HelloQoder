// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .MinimumLevel.Override("System", LogEventLevel.Warning)
    .Enrich.FromLogContext()
    .WriteTo.Console(
        outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
    .CreateLogger();

try
{
    Log.Information("Starting NovelTTS Application");

    // Find project root directory (where data folder exists)
    var baseDir = FindProjectRoot(AppContext.BaseDirectory) ?? Environment.CurrentDirectory;
    Log.Information("Using base directory: {BaseDir}", baseDir);
    Environment.CurrentDirectory = baseDir;

    // Build configuration
    var configuration = new ConfigurationBuilder()
        .SetBasePath(AppContext.BaseDirectory)
        .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
        .AddJsonFile($"appsettings.{Environment.GetEnvironmentVariable("DOTNET_ENVIRONMENT") ?? "Production"}.json", optional: true)
        .AddEnvironmentVariables()
        .Build();

    // Configure services
    var services = new ServiceCollection();

    //Add configuration
    services.AddSingleton<IConfiguration>(configuration);

    // Add logging
    services.AddLogging(builder => builder.AddSerilog(dispose: true));
    
    // Add infrastructure services
    services.AddInfrastructureServices(configuration);
    
    // Add application services
    services.AddScoped<INovelProcessor, NovelProcessor>();

    var serviceProvider = services.BuildServiceProvider();

    // Run the application
    await RunApplicationAsync(serviceProvider, args);
}
catch (Exception ex)
{
    Log.Fatal(ex, "Application terminated unexpectedly");
    Environment.ExitCode = 1;
}
finally
{
    await Log.CloseAndFlushAsync();
}

async Task RunApplicationAsync(IServiceProvider serviceProvider, string[] args)
{
    var processor = serviceProvider.GetRequiredService<INovelProcessor>();
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    
    var inputFolder = configuration["Paths:InputFolder"] ?? "./data/novels";
    var outputFolder = configuration["Paths:OutputFolder"] ?? "./data/output";

    // Ensure directories exist
    Directory.CreateDirectory(inputFolder);
    Directory.CreateDirectory(outputFolder);

    // Parse command line arguments or use defaults
    string? inputPath = null;
    string? outputPath = null;
    string? voiceRefUrl = null;
    string? chapterFilter = null;
    bool listChapters = false;

    for (var i = 0; i < args.Length; i++)
    {
        switch (args[i])
        {
            case "-i" or "--input":
                inputPath = args.Length > i + 1 ? args[++i] : null;
                break;
            case "-o" or "--output":
                outputPath = args.Length > i + 1 ? args[++i] : null;
                break;
            case "-v" or "--voice":
                voiceRefUrl = args.Length > i + 1 ? args[++i] : null;
                break;
            case "-c" or "--chapter":
                chapterFilter = args.Length > i + 1 ? args[++i] : null;
                break;
            case "-l" or "--list":
                listChapters = true;
                break;
            case "-h" or "--help":
                PrintHelp();
                return;
        }
    }

    // List available chapters
    if (listChapters)
    {
        ListChapters(inputFolder);
        return;
    }

    if (string.IsNullOrEmpty(inputPath))
    {
        // Determine search path based on chapter filter
        var searchPath = inputFolder;
        if (!string.IsNullOrEmpty(chapterFilter))
        {
            // Find chapter directory matching the filter
            var chapterDirs = Directory.GetDirectories(inputFolder, "*", SearchOption.AllDirectories)
                .Where(d => Path.GetFileName(d).Contains(chapterFilter, StringComparison.OrdinalIgnoreCase))
                .ToList();
            
            if (chapterDirs.Count == 0)
            {
                Log.Warning("No chapter matching '{Filter}' found", chapterFilter);
                ListChapters(inputFolder);
                return;
            }
            
            searchPath = chapterDirs[0];
            Log.Information("Processing chapter: {Chapter}", Path.GetFileName(searchPath));
        }

        // Process novels in the search path
        var novelFiles = Directory.GetFiles(searchPath, "*.txt", SearchOption.AllDirectories)
            .Concat(Directory.GetFiles(searchPath, "*.md", SearchOption.AllDirectories))
            .OrderBy(f => f)
            .ToList();

        if (novelFiles.Count == 0)
        {
            Log.Warning("No novel files found in {InputFolder}", inputFolder);
            Log.Information("Place .txt or .md files in the input folder, or use -i to specify a file");
            PrintHelp();
            return;
        }

        Log.Information("Found {Count} novel files to process", novelFiles.Count);

        // Create voice reference from Bilibili video if provided
        VoiceReference? voiceReference = null;
        if (!string.IsNullOrEmpty(voiceRefUrl))
        {
            var bilibiliDownloader = serviceProvider.GetRequiredService<IBilibiliDownloader>();
            Log.Information("Creating voice reference from Bilibili video: {Url}", voiceRefUrl);
            voiceReference = await bilibiliDownloader.CreateVoiceReferenceAsync(
                voiceRefUrl,
                "custom_voice",
                TimeSpan.FromSeconds(5),
                TimeSpan.FromSeconds(10));
            Log.Information("Voice reference created: {Name}", voiceReference.Name);
        }

        var progress = new Progress<ProcessingProgress>(p =>
        {
            Log.Information("[{Stage}] {Percent:F1}% - {Message}", 
                p.Stage, p.PercentComplete, p.Message);
        });

        var results = await processor.ProcessBatchAsync(
            novelFiles,
            outputFolder,
            voiceReference: voiceReference,
            progress: progress);

        Log.Information("Batch processing completed: {Count} audiobooks generated", results.Count());
    }
    else
    {
        // Process single novel
        outputPath ??= Path.Combine(outputFolder, Path.GetFileNameWithoutExtension(inputPath) + ".mp3");

        // Create voice reference from Bilibili video if provided
        VoiceReference? voiceReference = null;
        if (!string.IsNullOrEmpty(voiceRefUrl))
        {
            var bilibiliDownloader = serviceProvider.GetRequiredService<IBilibiliDownloader>();
            Log.Information("Creating voice reference from Bilibili video: {Url}", voiceRefUrl);
            voiceReference = await bilibiliDownloader.CreateVoiceReferenceAsync(
                voiceRefUrl,
                "custom_voice",
                TimeSpan.FromSeconds(5),
                TimeSpan.FromSeconds(10));
            Log.Information("Voice reference created: {Name}", voiceReference.Name);
        }

        var progress = new Progress<ProcessingProgress>(p =>
        {
            Log.Information("[{Stage}] {Percent:F1}% - {Message}", 
                p.Stage, p.PercentComplete, p.Message);
        });

        var result = await processor.ProcessNovelAsync(
            inputPath,
            outputPath,
            voiceReference: voiceReference,
            progress: progress);

        Log.Information("Audiobook generated: {Output}", result);
    }
}

void PrintHelp()
{
    Console.WriteLine(@"
NovelTTS - Convert novels to audiobooks using AI

Usage:
    NovelTTSApp [options]

Options:
    -i, --input <path>     Input novel file path (.txt or .md)
    -o, --output <path>    Output audio file path (.mp3)
    -c, --chapter <name>   Process only the specified chapter (partial match)
    -l, --list             List all available chapters
    -v, --voice <url>      Bilibili video URL for voice cloning (optional)
    -h, --help             Show this help message

Examples:
    # List all chapters
    NovelTTSApp -l

    # Process only chapter 1 (partial match)
    NovelTTSApp -c 第一章

    # Process a single file
    NovelTTSApp -i ./mynovel.txt -o ./mynovel.mp3

    # Process with voice cloning from Bilibili video
    NovelTTSApp -i ./novel.txt -v https://www.bilibili.com/video/BV1xxxxxxxx

Configuration:
    Edit appsettings.json to configure:
    - AI:ApiKey       Your Zhipu AI API key
    - Paths:InputFolder   Default input folder for novels
    - Paths:OutputFolder  Default output folder for audiobooks
");
}

void ListChapters(string inputFolder)
{
    Console.WriteLine("\nAvailable chapters:");
    Console.WriteLine(new string('=', 60));
    
    var novelDirs = Directory.GetDirectories(inputFolder);
    foreach (var novelDir in novelDirs.OrderBy(d => d))
    {
        var novelName = Path.GetFileName(novelDir);
        Console.WriteLine($"\n[{novelName}]");
        
        var chapters = Directory.GetDirectories(novelDir)
            .OrderBy(d => d)
            .ToList();
        
        foreach (var chapter in chapters)
        {
            var chapterName = Path.GetFileName(chapter);
            var fileCount = Directory.GetFiles(chapter, "*.txt").Length + 
                           Directory.GetFiles(chapter, "*.md").Length;
            Console.WriteLine($"  {chapterName} ({fileCount} files)");
        }
    }
    Console.WriteLine();
}

string? FindProjectRoot(string startDir)
{
    var dir = new DirectoryInfo(startDir);
    
    // Walk up the directory tree to find project root
    while (dir != null)
    {
        // Check if this directory contains the data folder or .sln file
        if (Directory.Exists(Path.Combine(dir.FullName, "data")) ||
            Directory.GetFiles(dir.FullName, "*.sln").Length > 0)
        {
            return dir.FullName;
        }
        dir = dir.Parent;
    }
    
    return null;
}
