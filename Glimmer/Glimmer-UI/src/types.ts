// GLIMMER Type Definitions

export type ActionType = 
  | 'click' | 'double_click' | 'right_click' | 'drag'
  | 'type' | 'key' | 'hotkey'
  | 'scroll' 
  | 'wait' | 'screenshot'
  | 'navigate' | 'launch'

export type StatusType = 'WORKING' | 'DONE' | 'FAIL'

export interface Operation {
  action: ActionType
  params: Record<string, unknown>
}

export interface GlimmerResponse {
  ui_thought: string
  ui_focus_box: [number, number, number, number] | null
  status: StatusType
  error_message?: string
  operation: Operation | null
  progress?: number
  screenshot?: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  status?: StatusType
  action?: ActionType
}

export interface AgentState {
  status: 'idle' | 'working' | 'done' | 'error'
  currentTask: string
  progress: number
}

export interface HistoryEntry {
  step: number
  action: ActionType
  params: Record<string, unknown>
  result: 'success' | 'failure'
  screenshot?: string
}
