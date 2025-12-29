namespace ALAgent.Agent.Services;

public class AgentSettings
{
    public string OpenAIApiKey { get; set; } = string.Empty;
    public string ModelId { get; set; } = "gpt-4o";
    public string RagApiUrl { get; set; } = "http://localhost:8000";
    public int MaxTokens { get; set; } = 4096;
    public double Temperature { get; set; } = 0.7;
}
