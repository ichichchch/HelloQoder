import request from './request'
import type { ChatSession, ChatMessage, SendMessageResponse, MemoryStats } from '@/types'

// AI后端直接调用（记忆系统功能）
const AI_API_URL = import.meta.env.VITE_AI_API_URL || 'http://localhost:8000'

export const chatApi = {
  // 会话管理
  getSessions(): Promise<ChatSession[]> {
    return request.get('/api/chat/sessions')
  },

  getSession(sessionId: string): Promise<ChatSession> {
    return request.get(`/api/chat/sessions/${sessionId}`)
  },

  createSession(): Promise<ChatSession> {
    return request.post('/api/chat/sessions')
  },

  deleteSession(sessionId: string): Promise<void> {
    return request.delete(`/api/chat/sessions/${sessionId}`)
  },

  // 消息管理
  getMessages(sessionId: string): Promise<ChatMessage[]> {
    return request.get(`/api/chat/sessions/${sessionId}/messages`)
  },

  sendMessage(sessionId: string, content: string): Promise<SendMessageResponse> {
    return request.post(`/api/chat/sessions/${sessionId}/messages`, { content })
  },

  // ===================
  // 记忆系统 API
  // ===================

  /**
   * 结束会话并生成摘要
   * 在用户关闭对话页面时调用
   * user_id 由后端自动从客户端IP获取
   */
  async endSession(messages: Array<{ role: string; content: string }>): Promise<void> {
    await fetch(`${AI_API_URL}/api/session/end`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages })
    })
  },

  /**
   * 获取记忆统计信息
   * user_id 由后端自动从客户端IP获取
   */
  async getMemoryStats(): Promise<MemoryStats> {
    const response = await fetch(`${AI_API_URL}/api/memory/stats`)
    return response.json()
  },

  /**
   * 清除用户所有记忆
   * user_id 由后端自动从客户端IP获取
   */
  async clearMemories(): Promise<{ deletedCount: number }> {
    const response = await fetch(`${AI_API_URL}/api/memory`, {
      method: 'DELETE'
    })
    return response.json()
  }
}
