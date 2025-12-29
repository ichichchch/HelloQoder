using System.ComponentModel;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.SemanticKernel;

namespace ALAgent.Agent.Tools;

public class CodeAnalysisTools
{
    [KernelFunction("search_code")]
    [Description("Search for code patterns in files using regex")]
    public async Task<string> SearchCodeAsync(
        [Description("The directory to search in")] string directory,
        [Description("The regex pattern to search for")] string pattern,
        [Description("File extension filter (e.g., '.cs', '.ts')")] string? fileExtension = null)
    {
        try
        {
            if (!Directory.Exists(directory))
            {
                return $"Error: Directory not found: {directory}";
            }

            var regex = new Regex(pattern, RegexOptions.IgnoreCase | RegexOptions.Multiline);
            var results = new StringBuilder();
            var matchCount = 0;
            const int maxResults = 20;

            var searchPattern = string.IsNullOrEmpty(fileExtension) ? "*" : $"*{fileExtension}";
            var files = Directory.EnumerateFiles(directory, searchPattern, new EnumerationOptions
            {
                RecurseSubdirectories = true,
                IgnoreInaccessible = true
            });

            foreach (var file in files)
            {
                if (ShouldIgnore(file))
                    continue;

                try
                {
                    var content = await File.ReadAllTextAsync(file);
                    var matches = regex.Matches(content);

                    foreach (Match match in matches)
                    {
                        if (matchCount >= maxResults)
                        {
                            results.AppendLine($"\n... and more matches (showing first {maxResults})");
                            return results.ToString();
                        }

                        var lineNumber = GetLineNumber(content, match.Index);
                        var lineContent = GetLineContent(content, match.Index);
                        
                        results.AppendLine($"{Path.GetRelativePath(directory, file)}:{lineNumber}");
                        results.AppendLine($"  {lineContent.Trim()}");
                        results.AppendLine();
                        
                        matchCount++;
                    }
                }
                catch
                {
                    // Skip files that can't be read
                }
            }

            return matchCount > 0 
                ? results.ToString() 
                : "No matches found";
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    [KernelFunction("get_file_structure")]
    [Description("Get the structure of a code file (classes, methods, etc.)")]
    public async Task<string> GetFileStructureAsync(
        [Description("The file path to analyze")] string path)
    {
        try
        {
            if (!File.Exists(path))
            {
                return $"Error: File not found: {path}";
            }

            var content = await File.ReadAllTextAsync(path);
            var extension = Path.GetExtension(path).ToLowerInvariant();

            return extension switch
            {
                ".cs" => AnalyzeCSharpStructure(content),
                ".ts" or ".tsx" => AnalyzeTypeScriptStructure(content),
                ".py" => AnalyzePythonStructure(content),
                _ => "Structure analysis not supported for this file type"
            };
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    [KernelFunction("execute_command")]
    [Description("Execute a shell command. This operation requires user approval.")]
    public async Task<string> ExecuteCommandAsync(
        [Description("The command to execute")] string command,
        [Description("The working directory")] string? workingDirectory = null)
    {
        try
        {
            var isWindows = OperatingSystem.IsWindows();
            var shell = isWindows ? "powershell.exe" : "/bin/bash";
            var shellArgs = isWindows ? $"-Command \"{command}\"" : $"-c \"{command}\"";

            var process = new System.Diagnostics.Process
            {
                StartInfo = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = shell,
                    Arguments = shellArgs,
                    WorkingDirectory = workingDirectory ?? Environment.CurrentDirectory,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                }
            };

            process.Start();

            var output = await process.StandardOutput.ReadToEndAsync();
            var error = await process.StandardError.ReadToEndAsync();

            await process.WaitForExitAsync();

            var result = new StringBuilder();
            result.AppendLine($"Exit Code: {process.ExitCode}");
            
            if (!string.IsNullOrEmpty(output))
            {
                result.AppendLine("Output:");
                result.AppendLine(output);
            }
            
            if (!string.IsNullOrEmpty(error))
            {
                result.AppendLine("Error:");
                result.AppendLine(error);
            }

            return result.ToString();
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    private static int GetLineNumber(string content, int index)
    {
        return content[..index].Count(c => c == '\n') + 1;
    }

    private static string GetLineContent(string content, int index)
    {
        var start = content.LastIndexOf('\n', Math.Max(0, index - 1)) + 1;
        var end = content.IndexOf('\n', index);
        if (end == -1) end = content.Length;
        return content[start..end];
    }

    private static bool ShouldIgnore(string path)
    {
        var ignoredPatterns = new[]
        {
            "node_modules", ".git", "__pycache__", "bin", "obj",
            ".vs", ".idea", ".vscode", "dist", "build"
        };

        return ignoredPatterns.Any(pattern => 
            path.Contains(pattern, StringComparison.OrdinalIgnoreCase));
    }

    private static string AnalyzeCSharpStructure(string content)
    {
        var sb = new StringBuilder();
        
        // Simple regex-based analysis (for production, use Roslyn)
        var namespaceMatch = Regex.Match(content, @"namespace\s+([\w.]+)");
        if (namespaceMatch.Success)
            sb.AppendLine($"Namespace: {namespaceMatch.Groups[1].Value}");

        var classMatches = Regex.Matches(content, @"(public|internal|private)?\s*(class|interface|record|struct)\s+(\w+)");
        foreach (Match match in classMatches)
        {
            sb.AppendLine($"  {match.Groups[2].Value}: {match.Groups[3].Value}");
        }

        var methodMatches = Regex.Matches(content, @"(public|private|protected|internal)\s+[\w<>\[\],\s]+\s+(\w+)\s*\(");
        foreach (Match match in methodMatches)
        {
            sb.AppendLine($"    Method: {match.Groups[2].Value}");
        }

        return sb.Length > 0 ? sb.ToString() : "No structure found";
    }

    private static string AnalyzeTypeScriptStructure(string content)
    {
        var sb = new StringBuilder();

        var classMatches = Regex.Matches(content, @"(export\s+)?(class|interface|type)\s+(\w+)");
        foreach (Match match in classMatches)
        {
            sb.AppendLine($"{match.Groups[2].Value}: {match.Groups[3].Value}");
        }

        var functionMatches = Regex.Matches(content, @"(export\s+)?(async\s+)?function\s+(\w+)");
        foreach (Match match in functionMatches)
        {
            sb.AppendLine($"  Function: {match.Groups[3].Value}");
        }

        return sb.Length > 0 ? sb.ToString() : "No structure found";
    }

    private static string AnalyzePythonStructure(string content)
    {
        var sb = new StringBuilder();

        var classMatches = Regex.Matches(content, @"class\s+(\w+)");
        foreach (Match match in classMatches)
        {
            sb.AppendLine($"Class: {match.Groups[1].Value}");
        }

        var functionMatches = Regex.Matches(content, @"def\s+(\w+)\s*\(");
        foreach (Match match in functionMatches)
        {
            sb.AppendLine($"  Function: {match.Groups[1].Value}");
        }

        return sb.Length > 0 ? sb.ToString() : "No structure found";
    }
}
