using System.ComponentModel;
using System.Text;
using Microsoft.SemanticKernel;

namespace ALAgent.Agent.Tools;

public class FileSystemTools
{
    [KernelFunction("list_files")]
    [Description("List files and directories in a specified path")]
    public async Task<string> ListFilesAsync(
        [Description("The directory path to list")] string path,
        [Description("Whether to list recursively")] bool recursive = false)
    {
        try
        {
            if (!Directory.Exists(path))
            {
                return $"Error: Directory not found: {path}";
            }

            var options = new EnumerationOptions
            {
                RecurseSubdirectories = recursive,
                IgnoreInaccessible = true
            };

            var entries = new List<string>();
            
            foreach (var entry in Directory.EnumerateFileSystemEntries(path, "*", options))
            {
                var relativePath = Path.GetRelativePath(path, entry);
                
                // Skip common ignored directories
                if (ShouldIgnore(relativePath))
                    continue;

                var isDir = Directory.Exists(entry);
                entries.Add($"{(isDir ? "[D] " : "[F] ")}{relativePath}");
            }

            return entries.Count > 0 
                ? string.Join("\n", entries.Take(100)) 
                : "Directory is empty";
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    [KernelFunction("read_file")]
    [Description("Read the contents of a file")]
    public async Task<string> ReadFileAsync(
        [Description("The file path to read")] string path)
    {
        try
        {
            if (!File.Exists(path))
            {
                return $"Error: File not found: {path}";
            }

            var info = new FileInfo(path);
            if (info.Length > 1024 * 1024) // 1MB limit
            {
                return $"Error: File too large (max 1MB): {path}";
            }

            var content = await File.ReadAllTextAsync(path);
            return content;
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    [KernelFunction("write_file")]
    [Description("Write content to a file. This operation requires user approval.")]
    public async Task<string> WriteFileAsync(
        [Description("The file path to write to")] string path,
        [Description("The content to write")] string content)
    {
        try
        {
            var directory = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }

            await File.WriteAllTextAsync(path, content);
            return $"Successfully wrote {content.Length} characters to {path}";
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    [KernelFunction("delete_file")]
    [Description("Delete a file. This operation requires user approval.")]
    public Task<string> DeleteFileAsync(
        [Description("The file path to delete")] string path)
    {
        try
        {
            if (!File.Exists(path))
            {
                return Task.FromResult($"Error: File not found: {path}");
            }

            File.Delete(path);
            return Task.FromResult($"Successfully deleted: {path}");
        }
        catch (Exception ex)
        {
            return Task.FromResult($"Error: {ex.Message}");
        }
    }

    [KernelFunction("file_exists")]
    [Description("Check if a file or directory exists")]
    public Task<string> FileExistsAsync(
        [Description("The path to check")] string path)
    {
        var fileExists = File.Exists(path);
        var dirExists = Directory.Exists(path);

        if (fileExists)
            return Task.FromResult($"File exists: {path}");
        if (dirExists)
            return Task.FromResult($"Directory exists: {path}");
        
        return Task.FromResult($"Path does not exist: {path}");
    }

    private static bool ShouldIgnore(string path)
    {
        var ignoredPatterns = new[]
        {
            "node_modules", ".git", "__pycache__", "bin", "obj",
            ".vs", ".idea", ".vscode", "dist", "build", ".next"
        };

        return ignoredPatterns.Any(pattern => 
            path.Contains(pattern, StringComparison.OrdinalIgnoreCase));
    }
}
