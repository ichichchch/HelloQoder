import * as vscode from 'vscode';

export interface CommandResult {
  exitCode: number;
  stdout: string;
  stderr: string;
}

export class TerminalService {
  private _terminals: Map<string, vscode.Terminal> = new Map();
  private _outputBuffers: Map<string, string> = new Map();

  public async executeCommand(command: string, cwd?: string): Promise<CommandResult> {
    return new Promise((resolve, reject) => {
      const { spawn } = require('child_process');
      
      const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      const workingDirectory = cwd || workspaceFolder || process.cwd();

      // Use shell based on platform
      const isWindows = process.platform === 'win32';
      const shell = isWindows ? 'powershell.exe' : '/bin/bash';
      const shellArgs = isWindows ? ['-Command', command] : ['-c', command];

      const child = spawn(shell, shellArgs, {
        cwd: workingDirectory,
        env: { ...process.env },
        shell: false,
      });

      let stdout = '';
      let stderr = '';

      child.stdout.on('data', (data: Buffer) => {
        stdout += data.toString();
      });

      child.stderr.on('data', (data: Buffer) => {
        stderr += data.toString();
      });

      child.on('close', (exitCode: number) => {
        resolve({
          exitCode: exitCode ?? 0,
          stdout,
          stderr,
        });
      });

      child.on('error', (error: Error) => {
        reject(error);
      });

      // Set timeout (30 seconds)
      setTimeout(() => {
        child.kill();
        reject(new Error('Command timed out after 30 seconds'));
      }, 30000);
    });
  }

  public createInteractiveTerminal(name: string): vscode.Terminal {
    const existing = this._terminals.get(name);
    if (existing) {
      return existing;
    }

    const terminal = vscode.window.createTerminal({
      name: `AL Agent: ${name}`,
      cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
    });

    this._terminals.set(name, terminal);
    return terminal;
  }

  public sendToTerminal(name: string, text: string) {
    const terminal = this._terminals.get(name);
    if (terminal) {
      terminal.sendText(text);
      terminal.show();
    }
  }

  public showTerminal(name: string) {
    const terminal = this._terminals.get(name);
    if (terminal) {
      terminal.show();
    }
  }

  public dispose() {
    for (const terminal of this._terminals.values()) {
      terminal.dispose();
    }
    this._terminals.clear();
    this._outputBuffers.clear();
  }
}
