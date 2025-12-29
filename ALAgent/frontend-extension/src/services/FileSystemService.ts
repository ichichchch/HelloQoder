import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface FileInfo {
  name: string;
  path: string;
  isDirectory: boolean;
  size?: number;
  modifiedTime?: number;
}

export class FileSystemService {
  public async listFiles(dirPath: string, recursive: boolean = false): Promise<FileInfo[]> {
    const absolutePath = this._resolveWorkspacePath(dirPath);
    
    if (!fs.existsSync(absolutePath)) {
      throw new Error(`Directory not found: ${dirPath}`);
    }

    const stats = fs.statSync(absolutePath);
    if (!stats.isDirectory()) {
      throw new Error(`Path is not a directory: ${dirPath}`);
    }

    return this._listFilesInternal(absolutePath, recursive);
  }

  private _listFilesInternal(dirPath: string, recursive: boolean): FileInfo[] {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    const files: FileInfo[] = [];

    for (const entry of entries) {
      // Skip hidden files and common ignored directories
      if (entry.name.startsWith('.') || 
          entry.name === 'node_modules' || 
          entry.name === '__pycache__' ||
          entry.name === 'bin' ||
          entry.name === 'obj') {
        continue;
      }

      const fullPath = path.join(dirPath, entry.name);
      const stat = fs.statSync(fullPath);

      const fileInfo: FileInfo = {
        name: entry.name,
        path: fullPath,
        isDirectory: entry.isDirectory(),
        size: stat.size,
        modifiedTime: stat.mtimeMs,
      };

      files.push(fileInfo);

      if (recursive && entry.isDirectory()) {
        const subFiles = this._listFilesInternal(fullPath, true);
        files.push(...subFiles);
      }
    }

    return files;
  }

  public async readFile(filePath: string): Promise<string> {
    const absolutePath = this._resolveWorkspacePath(filePath);
    
    if (!fs.existsSync(absolutePath)) {
      throw new Error(`File not found: ${filePath}`);
    }

    const stats = fs.statSync(absolutePath);
    if (stats.isDirectory()) {
      throw new Error(`Path is a directory, not a file: ${filePath}`);
    }

    // Check file size (limit to 1MB)
    if (stats.size > 1024 * 1024) {
      throw new Error(`File too large (max 1MB): ${filePath}`);
    }

    return fs.readFileSync(absolutePath, 'utf-8');
  }

  public async writeFile(filePath: string, content: string): Promise<void> {
    const absolutePath = this._resolveWorkspacePath(filePath);
    
    // Ensure directory exists
    const dir = path.dirname(absolutePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(absolutePath, content, 'utf-8');
  }

  public async deleteFile(filePath: string): Promise<void> {
    const absolutePath = this._resolveWorkspacePath(filePath);
    
    if (!fs.existsSync(absolutePath)) {
      throw new Error(`File not found: ${filePath}`);
    }

    fs.unlinkSync(absolutePath);
  }

  public async createDirectory(dirPath: string): Promise<void> {
    const absolutePath = this._resolveWorkspacePath(dirPath);
    
    if (!fs.existsSync(absolutePath)) {
      fs.mkdirSync(absolutePath, { recursive: true });
    }
  }

  public async fileExists(filePath: string): Promise<boolean> {
    const absolutePath = this._resolveWorkspacePath(filePath);
    return fs.existsSync(absolutePath);
  }

  private _resolveWorkspacePath(relativePath: string): string {
    if (path.isAbsolute(relativePath)) {
      return relativePath;
    }

    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
      throw new Error('No workspace folder open');
    }

    return path.join(workspaceFolder.uri.fsPath, relativePath);
  }
}
