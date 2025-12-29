import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ExtensionToWebviewMessage, AgentState } from '../core/types';

// VS Code API
declare const acquireVsCodeApi: () => {
  postMessage: (message: unknown) => void;
  getState: () => unknown;
  setState: (state: unknown) => void;
};

const vscode = acquireVsCodeApi();

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'thought' | 'tool';
  content: string;
  timestamp: number;
  toolCall?: {
    callId: string;
    tool: string;
    args: Record<string, unknown>;
    requiresApproval: boolean;
  };
  toolResult?: {
    success: boolean;
    result?: unknown;
    error?: string;
  };
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [state, setState] = useState<AgentState>('Idle');
  const [pendingApprovals, setPendingApprovals] = useState<Set<string>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    const handleMessage = (event: MessageEvent<ExtensionToWebviewMessage>) => {
      const message = event.data;

      switch (message.type) {
        case 'stateChange':
          setState(message.payload.state);
          break;

        case 'thought':
          setMessages((prev) => [
            ...prev,
            {
              id: `thought-${Date.now()}`,
              role: 'thought',
              content: message.payload.content,
              timestamp: message.payload.timestamp,
            },
          ]);
          break;

        case 'toolCall':
          setMessages((prev) => [
            ...prev,
            {
              id: `tool-${message.payload.callId}`,
              role: 'tool',
              content: `Calling ${message.payload.tool}`,
              timestamp: Date.now(),
              toolCall: message.payload,
            },
          ]);
          if (message.payload.requiresApproval) {
            setPendingApprovals((prev) => new Set([...prev, message.payload.callId]));
          }
          break;

        case 'toolResult':
          setMessages((prev) =>
            prev.map((msg) =>
              msg.toolCall?.callId === message.payload.callId
                ? { ...msg, toolResult: message.payload }
                : msg
            )
          );
          setPendingApprovals((prev) => {
            const next = new Set(prev);
            next.delete(message.payload.callId);
            return next;
          });
          break;

        case 'response':
          setMessages((prev) => [
            ...prev,
            {
              id: `assistant-${Date.now()}`,
              role: 'assistant',
              content: message.payload.content,
              timestamp: message.payload.timestamp,
            },
          ]);
          break;

        case 'error':
          setMessages((prev) => [
            ...prev,
            {
              id: `error-${Date.now()}`,
              role: 'system',
              content: `Error: ${message.payload.message}`,
              timestamp: Date.now(),
            },
          ]);
          break;

        case 'historyLoaded':
          setMessages(
            message.payload.messages.map((msg, idx) => ({
              id: `history-${idx}`,
              role: msg.role,
              content: msg.content,
              timestamp: msg.timestamp,
            }))
          );
          break;
      }
    };

    window.addEventListener('message', handleMessage);

    // Signal ready
    vscode.postMessage({ type: 'ready' });

    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || state !== 'Idle') return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);

    vscode.postMessage({
      type: 'sendPrompt',
      payload: { prompt: inputValue.trim() },
    });

    setInputValue('');
  };

  const handleCancel = () => {
    vscode.postMessage({ type: 'cancelRequest' });
  };

  const handleApproval = (callId: string, approved: boolean) => {
    vscode.postMessage({
      type: 'approveToolCall',
      payload: { callId, approved },
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const getStateLabel = (s: AgentState): string => {
    switch (s) {
      case 'Idle':
        return '';
      case 'Thinking':
        return 'Thinking...';
      case 'Executing':
        return 'Executing...';
      case 'WaitingForUser':
        return 'Waiting for approval...';
      case 'Error':
        return 'Error occurred';
      default:
        return '';
    }
  };

  return (
    <div className="app">
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>AL Agent</h2>
            <p>Ask me to help with your code!</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`message message-${msg.role}`}>
            <div className="message-header">
              <span className="message-role">
                {msg.role === 'user'
                  ? 'You'
                  : msg.role === 'assistant'
                  ? 'Agent'
                  : msg.role === 'thought'
                  ? 'Thinking'
                  : msg.role === 'tool'
                  ? 'Tool'
                  : 'System'}
              </span>
              <span className="message-time">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div className="message-content">
              {msg.role === 'tool' && msg.toolCall ? (
                <div className="tool-call">
                  <div className="tool-name">{msg.toolCall.tool}</div>
                  <pre className="tool-args">
                    {JSON.stringify(msg.toolCall.args, null, 2)}
                  </pre>
                  {msg.toolResult && (
                    <div
                      className={`tool-result ${
                        msg.toolResult.success ? 'success' : 'error'
                      }`}
                    >
                      {msg.toolResult.success
                        ? 'Completed'
                        : `Failed: ${msg.toolResult.error}`}
                    </div>
                  )}
                  {msg.toolCall.requiresApproval &&
                    pendingApprovals.has(msg.toolCall.callId) && (
                      <div className="approval-buttons">
                        <button
                          className="btn btn-approve"
                          onClick={() =>
                            handleApproval(msg.toolCall!.callId, true)
                          }
                        >
                          Approve
                        </button>
                        <button
                          className="btn btn-reject"
                          onClick={() =>
                            handleApproval(msg.toolCall!.callId, false)
                          }
                        >
                          Reject
                        </button>
                      </div>
                    )}
                </div>
              ) : (
                <div className="text-content">{msg.content}</div>
              )}
            </div>
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      {state !== 'Idle' && (
        <div className="state-indicator">
          <span className="spinner" />
          <span>{getStateLabel(state)}</span>
          <button className="btn btn-cancel" onClick={handleCancel}>
            Cancel
          </button>
        </div>
      )}

      <form className="input-container" onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          className="input-field"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={state !== 'Idle'}
          rows={3}
        />
        <button
          type="submit"
          className="btn btn-send"
          disabled={!inputValue.trim() || state !== 'Idle'}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default App;
