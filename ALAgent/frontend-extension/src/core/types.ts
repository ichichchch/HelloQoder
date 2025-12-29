import { z } from 'zod';

// ==================== State Machine ====================
export type AgentState = 'Idle' | 'Thinking' | 'Executing' | 'WaitingForUser' | 'Error';

// ==================== Message Protocol ====================
// Messages from Webview to Extension
export const WebviewToExtensionMessageSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('sendPrompt'),
    payload: z.object({
      prompt: z.string(),
      context: z.string().optional(),
    }),
  }),
  z.object({
    type: z.literal('cancelRequest'),
  }),
  z.object({
    type: z.literal('approveToolCall'),
    payload: z.object({
      callId: z.string(),
      approved: z.boolean(),
    }),
  }),
  z.object({
    type: z.literal('ready'),
  }),
]);

export type WebviewToExtensionMessage = z.infer<typeof WebviewToExtensionMessageSchema>;

// Messages from Extension to Webview
export const ExtensionToWebviewMessageSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('stateChange'),
    payload: z.object({
      state: z.enum(['Idle', 'Thinking', 'Executing', 'WaitingForUser', 'Error']),
    }),
  }),
  z.object({
    type: z.literal('thought'),
    payload: z.object({
      content: z.string(),
      timestamp: z.number(),
    }),
  }),
  z.object({
    type: z.literal('toolCall'),
    payload: z.object({
      callId: z.string(),
      tool: z.string(),
      args: z.record(z.unknown()),
      requiresApproval: z.boolean(),
    }),
  }),
  z.object({
    type: z.literal('toolResult'),
    payload: z.object({
      callId: z.string(),
      success: z.boolean(),
      result: z.unknown(),
      error: z.string().optional(),
    }),
  }),
  z.object({
    type: z.literal('response'),
    payload: z.object({
      content: z.string(),
      timestamp: z.number(),
    }),
  }),
  z.object({
    type: z.literal('error'),
    payload: z.object({
      message: z.string(),
      code: z.string().optional(),
    }),
  }),
  z.object({
    type: z.literal('historyLoaded'),
    payload: z.object({
      messages: z.array(z.object({
        role: z.enum(['user', 'assistant', 'system']),
        content: z.string(),
        timestamp: z.number(),
      })),
    }),
  }),
]);

export type ExtensionToWebviewMessage = z.infer<typeof ExtensionToWebviewMessageSchema>;

// ==================== Tool Definitions ====================
export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
  requiresApproval: boolean;
}

export interface ToolResult {
  callId: string;
  success: boolean;
  result?: unknown;
  error?: string;
}

// ==================== Agent API Types ====================
export interface AgentRequest {
  prompt: string;
  context?: string;
  workspacePath: string;
  conversationHistory: ConversationMessage[];
}

export interface AgentResponse {
  thought: string;
  toolCalls?: ToolCall[];
  response?: string;
  done: boolean;
}

export interface ConversationMessage {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp: number;
  toolCallId?: string;
  toolName?: string;
}

// ==================== RAG API Types ====================
export interface RagQueryRequest {
  query: string;
  workspacePath: string;
  topK?: number;
}

export interface RagQueryResponse {
  chunks: CodeChunk[];
}

export interface CodeChunk {
  content: string;
  filePath: string;
  startLine: number;
  endLine: number;
  score: number;
  metadata?: Record<string, unknown>;
}
