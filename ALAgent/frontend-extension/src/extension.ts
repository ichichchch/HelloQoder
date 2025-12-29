import * as vscode from 'vscode';
import { ChatViewProvider } from './core/ChatViewProvider';
import { AgentClient } from './services/AgentClient';
import { FileSystemService } from './services/FileSystemService';
import { TerminalService } from './services/TerminalService';

let agentClient: AgentClient;
let fileSystemService: FileSystemService;
let terminalService: TerminalService;

export function activate(context: vscode.ExtensionContext) {
  console.log('AL Agent extension is now active!');

  // Initialize services
  const config = vscode.workspace.getConfiguration('alagent');
  const agentApiUrl = config.get<string>('agentApiUrl') || 'http://localhost:5000';
  const ragApiUrl = config.get<string>('ragApiUrl') || 'http://localhost:8000';

  agentClient = new AgentClient(agentApiUrl, ragApiUrl);
  fileSystemService = new FileSystemService();
  terminalService = new TerminalService();

  // Register the webview provider
  const chatViewProvider = new ChatViewProvider(
    context.extensionUri,
    agentClient,
    fileSystemService,
    terminalService
  );

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      'al-agent.chatView',
      chatViewProvider,
      {
        webviewOptions: {
          retainContextWhenHidden: true,
        },
      }
    )
  );

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('al-agent.openChat', () => {
      vscode.commands.executeCommand('workbench.view.extension.al-agent-sidebar');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('al-agent.clearHistory', () => {
      chatViewProvider.clearHistory();
      vscode.window.showInformationMessage('Chat history cleared');
    })
  );

  // Watch for configuration changes
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration('alagent')) {
        const newConfig = vscode.workspace.getConfiguration('alagent');
        agentClient.updateConfig(
          newConfig.get<string>('agentApiUrl') || 'http://localhost:5000',
          newConfig.get<string>('ragApiUrl') || 'http://localhost:8000'
        );
      }
    })
  );
}

export function deactivate() {
  terminalService?.dispose();
}
