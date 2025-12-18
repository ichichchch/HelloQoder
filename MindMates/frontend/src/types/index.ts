// 用户相关类型
export interface User {
  id: string
  username: string
  nickname?: string
  avatar?: string
  email?: string
  createdAt?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  nickname?: string
}

export interface AuthResponse {
  token: string
  user: User
}

// 聊天相关类型
export interface ChatSession {
  id: string
  userId: string
  title: string
  lastMessage?: string
  createdAt: string
  updatedAt: string
}

export interface ChatMessage {
  id: string
  sessionId: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt: string
  metadata?: {
    intent?: string
    isCrisis?: boolean
  }
}

export interface SendMessageResponse {
  userMessage: ChatMessage
  aiMessage: ChatMessage
  memoriesCreated?: number  // 本次对话提取的记忆数量
}

// 记忆系统相关类型
export interface MemoryStats {
  total: number
  byType: Record<string, number>
  avgImportance: number
  recentTopics: string[]
}

export interface EndSessionRequest {
  messages: Array<{ role: string; content: string }>
}

// API 响应类型
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 危机资源类型
export interface CrisisResource {
  name: string
  phone: string
  description: string
}
