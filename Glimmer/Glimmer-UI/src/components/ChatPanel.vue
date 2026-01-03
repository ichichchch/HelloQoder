<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import type { ChatMessage } from '../types'

const props = defineProps<{ messages: ChatMessage[] }>()
const chatContainer = ref<HTMLDivElement | null>(null)

watch(() => props.messages.length, async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
})

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const getStatusIcon = (status?: string) => {
  switch (status) {
    case 'WORKING': return '⏳'
    case 'DONE': return '✅'
    case 'FAIL': return '❌'
    default: return ''
  }
}

const getActionIcon = (action?: string) => {
  const icons: Record<string, string> = {
    click: '👆', double_click: '👆👆', right_click: '🖱️',
    type: '⌨️', scroll: '📜', key: '⌨️',
    wait: '⏱️', navigate: '🌐', launch: '🚀', drag: '✋'
  }
  return action ? icons[action] || '🔧' : ''
}
</script>

<template>
  <div class="chat-panel" ref="chatContainer">
    <div class="messages">
      <div v-for="message in messages" :key="message.id" class="message" :class="message.role">
        <div class="avatar">
          <span v-if="message.role === 'assistant'">✨</span>
          <span v-else>👤</span>
        </div>
        <div class="content">
          <div class="bubble">
            <span v-if="message.status" class="status-badge" :class="message.status.toLowerCase()">
              {{ getStatusIcon(message.status) }} {{ message.status }}
            </span>
            <span v-if="message.action" class="action-badge">
              {{ getActionIcon(message.action) }} {{ message.action }}
            </span>
            <p class="text">{{ message.content }}</p>
          </div>
          <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-panel { flex: 1; overflow-y: auto; padding: 16px; scroll-behavior: smooth; }
.messages { display: flex; flex-direction: column; gap: 16px; }
.message { display: flex; gap: 12px; }
.message.user { flex-direction: row-reverse; }

.avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
}

.message.assistant .avatar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }

.content { display: flex; flex-direction: column; gap: 4px; max-width: 85%; }
.message.user .content { align-items: flex-end; }

.bubble {
  padding: 12px 16px; border-radius: 16px;
  background: rgba(255, 255, 255, 0.1); position: relative;
}

.message.assistant .bubble { border-bottom-left-radius: 4px; background: rgba(102, 126, 234, 0.15); }
.message.user .bubble { border-bottom-right-radius: 4px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }

.status-badge, .action-badge {
  display: inline-block; padding: 2px 8px; border-radius: 12px;
  font-size: 11px; font-weight: 600; margin-right: 8px; margin-bottom: 8px;
}

.status-badge { background: rgba(255, 255, 255, 0.15); }
.status-badge.working { background: rgba(59, 130, 246, 0.3); color: #93c5fd; }
.status-badge.done { background: rgba(34, 197, 94, 0.3); color: #86efac; }
.status-badge.fail { background: rgba(239, 68, 68, 0.3); color: #fca5a5; }
.action-badge { background: rgba(168, 85, 247, 0.3); color: #d8b4fe; }

.text { margin: 0; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
.timestamp { font-size: 11px; color: #6e7681; padding: 0 4px; }
</style>
