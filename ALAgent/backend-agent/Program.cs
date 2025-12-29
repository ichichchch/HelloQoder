using ALAgent.Agent.Services;
using ALAgent.Agent.Tools;
using Microsoft.SemanticKernel;
using Refit;

var builder = WebApplication.CreateBuilder(args);

// Add configuration
builder.Services.Configure<AgentSettings>(builder.Configuration.GetSection("Agent"));

// Add CORS for frontend communication
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins("http://localhost:*", "vscode-webview://*")
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

// Register RAG client
builder.Services
    .AddRefitClient<IRagClient>()
    .ConfigureHttpClient(c =>
    {
        var ragUrl = builder.Configuration.GetValue<string>("Agent:RagApiUrl") ?? "http://localhost:8000";
        c.BaseAddress = new Uri(ragUrl);
        c.Timeout = TimeSpan.FromSeconds(30);
    });

// Register Semantic Kernel
builder.Services.AddSingleton<Kernel>(sp =>
{
    var config = builder.Configuration.GetSection("Agent").Get<AgentSettings>() ?? new AgentSettings();
    
    var kernelBuilder = Kernel.CreateBuilder();
    
    kernelBuilder.AddOpenAIChatCompletion(
        modelId: config.ModelId,
        apiKey: config.OpenAIApiKey
    );
    
    // Register tools as plugins
    kernelBuilder.Plugins.AddFromType<FileSystemTools>();
    kernelBuilder.Plugins.AddFromType<CodeAnalysisTools>();
    
    return kernelBuilder.Build();
});

// Register services
builder.Services.AddScoped<IAgentService, AgentService>();

// Add controllers
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

var app = builder.Build();

app.UseCors();
app.MapControllers();

// Health check endpoint
app.MapGet("/health", () => Results.Ok(new { status = "healthy", timestamp = DateTime.UtcNow }));

app.Run();
