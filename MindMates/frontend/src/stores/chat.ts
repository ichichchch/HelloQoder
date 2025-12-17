import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatSession, ChatMessage } from '@/types'
import { chatApi } from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<ChatSession[]>([])
  const currentSession = ref<ChatSession | null>(null)
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const isTyping = ref(false)

  const sortedSessions = computed(() => {
    return [...sessions.value].sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )
  })

  async function fetchSessions() {
    try {
      const response = await chatApi.getSessions()
      sessions.value = response
    } catch (error) {
      console.error('获取会话列表失败:', error)
    }
  }

  async function createSession() {
    try {
      const session = await chatApi.createSession()
      sessions.value.unshift(session)
      currentSession.value = session
      messages.value = []
      return session
    } catch (error) {
      console.error('创建会话失败:', error)
      throw error
    }
  }

  async function loadSession(sessionId: string) {
    try {
      isLoading.value = true
      const [session, sessionMessages] = await Promise.all([
        chatApi.getSession(sessionId),
        chatApi.getMessages(sessionId)
      ])
      currentSession.value = session
      messages.value = sessionMessages
    } catch (error) {
      console.error('加载会话失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function sendMessage(content: string) {
    if (!currentSession.value) {
      await createSession()
    }
    
    const sessionId = currentSession.value!.id

    // 添加用户消息
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      sessionId,
      role: 'user',
      content,
      createdAt: new Date().toISOString()
    }
    messages.value.push(userMessage)

    // 显示AI正在输入
    isTyping.value = true

    try {
      const response = await chatApi.sendMessage(sessionId, content)
      
      // 更新用户消息ID
      const userIndex = messages.value.findIndex(m => m.id === userMessage.id)
      if (userIndex !== -1) {
        messages.value[userIndex] = response.userMessage
      }

      // 添加AI回复
      messages.value.push(response.aiMessage)

      // 更新会话
      if (currentSession.value) {
        currentSession.value.updatedAt = new Date().toISOString()
        currentSession.value.lastMessage = response.aiMessage.content.slice(0, 50)
      }

      return response
    } catch (error) {
      // 移除临时消息
      messages.value = messages.value.filter(m => m.id !== userMessage.id)
      throw error
    } finally {
      isTyping.value = false
    }
  }

  async function deleteSession(sessionId: string) {
    try {
      await chatApi.deleteSession(sessionId)
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
        messages.value = []
      }
    } catch (error) {
      console.error('删除会话失败:', error)
      throw error
    }
  }

  function clearCurrentSession() {
    currentSession.value = null
    messages.value = []
  }

  return {
    sessions,
    currentSession,
    messages,
    isLoading,
    isTyping,
    sortedSessions,
    fetchSessions,
    createSession,
    loadSession,
    sendMessage,
    deleteSession,
    clearCurrentSession
  }
})
