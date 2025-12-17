import request from './request'
import type { ChatSession, ChatMessage, SendMessageResponse } from '@/types'

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
  }
}
