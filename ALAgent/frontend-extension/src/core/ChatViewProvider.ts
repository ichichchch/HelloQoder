import * as vscode from 'vscode';
import {
  WebviewToExtensionMessage,
  WebviewToExtensionMessageSchema,
  ExtensionToWebviewMessage,
  ConversationMessage,
  AgentState,
  ToolCall,
  ToolResult,
} from './types';
import { AgentClient } from '../services/AgentClient';
import { FileSystemService } from '../services/FileSystemService';
import { TerminalService } from '../services/TerminalService';

export class ChatViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'al-agent.chatView';

  private _view?: vscode.WebviewView;
  private _conversationHistory: ConversationMessage[] = [];
  private _state: AgentState = 'Idle';
  private _pendingToolCalls: Map<string, ToolCall> = new Map();
  private _abortController?: AbortController;

  constructor(
    private readonly _extensionUri: vscode.Uri,
    private readonly _agentClient: AgentClient,
    private readonly _fileSystemService: FileSystemService,
    private readonly _terminalService: TerminalService
  ) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    _context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri],
    };

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

    webviewView.webview.onDidReceiveMessage(async (message: unknown) => {
      try {
        const parsed = WebviewToExtensionMessageSchema.parse(message);
        await this._handleMessage(parsed);
      } catch (error) {
        console.error('Invalid message from webview:', error);
      }
    });
  }

  private async _handleMessage(message: WebviewToExtensionMessage) {
    switch (message.type) {
      case 'ready':
        this._sendMessage({
          type: 'historyLoaded',
          payload: { messages: this._conversationHistory },
        });
        this._sendMessage({
          type: 'stateChange',
          payload: { state: this._state },
        });
        break;

      case 'sendPrompt':
        await this._handleUserPrompt(message.payload.prompt, message.payload.context);
        break;

      case 'cancelRequest':
        this._abortController?.abort();
        this._setState('Idle');
        break;

      case 'approveToolCall':
        await this._handleToolApproval(message.payload.callId, message.payload.approved);
        break;
    }
  }

  private async _handleUserPrompt(prompt: string, context?: string) {
    // Add user message to history
    this._conversationHistory.push({
      role: 'user',
      content: prompt,
      timestamp: Date.now(),
    });

    this._setState('Thinking');
    this._abortController = new AbortController();

    try {
      const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '';

      const response = await this._agentClient.chat({
        prompt,
        context,
        workspacePath,
        conversationHistory: this._conversationHistory,
      });

      // Send thought to webview
      if (response.thought) {
        this._sendMessage({
          type: 'thought',
          payload: {
            content: response.thought,
            timestamp: Date.now(),
          },
        });
      }

      // Handle tool calls
      if (response.toolCalls && response.toolCalls.length > 0) {
        this._setState('Executing');
        for (const toolCall of response.toolCalls) {
          await this._executeToolCall(toolCall);
        }
      }

      // Send final response
      if (response.response) {
        this._conversationHistory.push({
          role: 'assistant',
          content: response.response,
          timestamp: Date.now(),
        });

        this._sendMessage({
          type: 'response',
          payload: {
            content: response.response,
            timestamp: Date.now(),
          },
        });
      }

      this._setState('Idle');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this._sendMessage({
        type: 'error',
        payload: { message: errorMessage },
      });
      this._setState('Error');
    }
  }

  private async _executeToolCall(toolCall: ToolCall): Promise<ToolResult> {
    this._sendMessage({
      type: 'toolCall',
      payload: {
        callId: toolCall.id,
        tool: toolCall.name,
        args: toolCall.arguments,
        requiresApproval: toolCall.requiresApproval,
      },
    });

    if (toolCall.requiresApproval) {
      this._pendingToolCalls.set(toolCall.id, toolCall);
      this._setState('WaitingForUser');
      return { callId: toolCall.id, success: false, error: 'Awaiting approval' };
    }

    return await this._runTool(toolCall);
  }

  private async _runTool(toolCall: ToolCall): Promise<ToolResult> {
    try {
      let result: unknown;

      switch (toolCall.name) {
        case 'list_files':
          result = await this._fileSystemService.listFiles(
            toolCall.arguments['path'] as string,
            toolCall.arguments['recursive'] as boolean
          );
          break;

        case 'read_file':
          result = await this._fileSystemService.readFile(
            toolCall.arguments['path'] as string
          );
          break;

        case 'write_file':
          result = await this._fileSystemService.writeFile(
            toolCall.arguments['path'] as string,
            toolCall.arguments['content'] as string
          );
          break;

        case 'execute_command':
          result = await this._terminalService.executeCommand(
            toolCall.arguments['command'] as string,
            toolCall.arguments['cwd'] as string | undefined
          );
          break;

        default:
          throw new Error(`Unknown tool: ${toolCall.name}`);
      }

      const toolResult: ToolResult = {
        callId: toolCall.id,
        success: true,
        result,
      };

      this._sendMessage({
        type: 'toolResult',
        payload: toolResult,
      });

      // Add to conversation history
      this._conversationHistory.push({
        role: 'tool',
        content: JSON.stringify(result),
        timestamp: Date.now(),
        toolCallId: toolCall.id,
        toolName: toolCall.name,
      });

      return toolResult;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      const toolResult: ToolResult = {
        callId: toolCall.id,
        success: false,
        error: errorMessage,
      };

      this._sendMessage({
        type: 'toolResult',
        payload: toolResult,
      });

      return toolResult;
    }
  }

  private async _handleToolApproval(callId: string, approved: boolean) {
    const toolCall = this._pendingToolCalls.get(callId);
    if (!toolCall) return;

    this._pendingToolCalls.delete(callId);

    if (approved) {
      this._setState('Executing');
      await this._runTool(toolCall);
    } else {
      this._sendMessage({
        type: 'toolResult',
        payload: {
          callId,
          success: false,
          error: 'User rejected tool execution',
        },
      });
    }

    if (this._pendingToolCalls.size === 0) {
      this._setState('Idle');
    }
  }

  private _setState(state: AgentState) {
    this._state = state;
    this._sendMessage({
      type: 'stateChange',
      payload: { state },
    });
  }

  private _sendMessage(message: ExtensionToWebviewMessage) {
    this._view?.webview.postMessage(message);
  }

  public clearHistory() {
    this._conversationHistory = [];
    this._sendMessage({
      type: 'historyLoaded',
      payload: { messages: [] },
    });
  }

  private _getHtmlForWebview(webview: vscode.Webview): string {
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, 'dist', 'webview', 'webview.js')
    );
    const styleUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, 'dist', 'webview', 'webview.css')
    );

    const nonce = this._getNonce();

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
  <link href="${styleUri}" rel="stylesheet">
  <title>AL Agent</title>
</head>
<body>
  <div id="root"></div>
  <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
  }

  private _getNonce(): string {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  }
}
