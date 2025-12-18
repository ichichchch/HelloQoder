import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatSession, ChatMessage, MemoryStats } from '@/types'
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

  /**
   * 结束当前会话并生成记忆摘要
   * 在用户离开对话页面时调用
   */
  async function endCurrentSession() {
    if (messages.value.length === 0) return
    
    try {
      const formattedMessages = messages.value.map(m => ({
        role: m.role,
        content: m.content
      }))
      await chatApi.endSession(formattedMessages)
      console.log('会话已结束，记忆已保存')
    } catch (error) {
      console.error('结束会话失败:', error)
    }
  }

  /**
   * 获取记忆统计信息
   */
  async function getMemoryStats(): Promise<MemoryStats | null> {
    try {
      return await chatApi.getMemoryStats()
    } catch (error) {
      console.error('获取记忆统计失败:', error)
      return null
    }
  }

  /**
   * 清除所有记忆
   */
  async function clearMemories(): Promise<number> {
    try {
      const result = await chatApi.clearMemories()
      return result.deletedCount
    } catch (error) {
      console.error('清除记忆失败:', error)
      return 0
    }
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
    clearCurrentSession,
    endCurrentSession,
    getMemoryStats,
    clearMemories
  }
})
