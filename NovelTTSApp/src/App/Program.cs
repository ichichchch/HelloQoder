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

    // Build configuration
    var configuration = new ConfigurationBuilder()
        .SetBasePath(Directory.GetCurrentDirectory())
        .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
        .AddJsonFile($"appsettings.{Environment.GetEnvironmentVariable("DOTNET_ENVIRONMENT") ?? "Production"}.json", optional: true)
        .AddEnvironmentVariables()
        .Build();

    // Configure services
    var services = new ServiceCollection();
    
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
            case "-h" or "--help":
                PrintHelp();
                return;
        }
    }

    if (string.IsNullOrEmpty(inputPath))
    {
        // Process all novels in input folder
        var novelFiles = Directory.GetFiles(inputFolder, "*.txt")
            .Concat(Directory.GetFiles(inputFolder, "*.md"))
            .ToList();

        if (novelFiles.Count == 0)
        {
            Log.Warning("No novel files found in {InputFolder}", inputFolder);
            Log.Information("Place .txt or .md files in the input folder, or use -i to specify a file");
            PrintHelp();
            return;
        }

        Log.Information("Found {Count} novel files to process", novelFiles.Count);

        var progress = new Progress<ProcessingProgress>(p =>
        {
            Log.Information("[{Stage}] {Percent:F1}% - {Message}", 
                p.Stage, p.PercentComplete, p.Message);
        });

        var results = await processor.ProcessBatchAsync(
            novelFiles,
            outputFolder,
            voiceReference: null,
            progress: progress);

        Log.Information("Batch processing completed: {Count} audiobooks generated", results.Count());
    }
    else
    {
        // Process single novel
        outputPath ??= Path.Combine(outputFolder, Path.GetFileNameWithoutExtension(inputPath) + ".mp3");

        var progress = new Progress<ProcessingProgress>(p =>
        {
            Log.Information("[{Stage}] {Percent:F1}% - {Message}", 
                p.Stage, p.PercentComplete, p.Message);
        });

        var result = await processor.ProcessNovelAsync(
            inputPath,
            outputPath,
            voiceReference: null,
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
    -v, --voice <url>      Bilibili video URL for voice cloning (optional)
    -h, --help             Show this help message

Examples:
    # Process all novels in the default input folder
    NovelTTSApp

    # Process a single novel
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
