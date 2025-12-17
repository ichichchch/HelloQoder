<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()

const inputMessage = ref('')
const messageListRef = ref<HTMLElement>()
const inputRef = ref()

// 危机资源
const crisisResources = [
  { name: '全国心理援助热线', phone: '400-161-9995' },
  { name: '北京心理危机研究与干预中心', phone: '010-82951332' },
  { name: '生命热线', phone: '400-821-1215' }
]

// 加载会话
onMounted(async () => {
  const sessionId = route.params.sessionId as string
  if (sessionId) {
    try {
      await chatStore.loadSession(sessionId)
      scrollToBottom()
    } catch {
      ElMessage.error('会话不存在')
      router.replace('/chat')
    }
  }
})

// 监听消息变化，自动滚动
watch(() => chatStore.messages.length, () => {
  nextTick(scrollToBottom)
})

function scrollToBottom() {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

async function sendMessage() {
  const content = inputMessage.value.trim()
  if (!content) return

  inputMessage.value = ''
  
  try {
    await chatStore.sendMessage(content)
    
    // 如果是新会话，更新URL
    if (chatStore.currentSession && !route.params.sessionId) {
      router.replace(`/chat/${chatStore.currentSession.id}`)
    }
  } catch (error) {
    ElMessage.error('发送失败，请重试')
  }
}

function goBack() {
  router.push('/home')
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function checkIsCrisis(message: any) {
  return message.metadata?.isCrisis === true
}
</script>

<template>
  <div class="chat-container safe-area-top safe-area-bottom">
    <!-- 顶部栏 -->
    <header class="chat-header">
      <el-button circle text @click="goBack">
        <el-icon :size="20"><ArrowLeft /></el-icon>
      </el-button>
      <div class="header-title">
        <h2>心灵对话</h2>
        <span v-if="chatStore.isTyping" class="typing-indicator">正在输入...</span>
      </div>
      <div class="header-right">
        <el-icon :size="20"><ChatDotRound /></el-icon>
      </div>
    </header>

    <!-- 消息列表 -->
    <main ref="messageListRef" class="message-list">
      <!-- 欢迎消息 -->
      <div v-if="chatStore.messages.length === 0" class="welcome-message">
        <div class="ai-avatar">
          <el-icon :size="32"><ChatDotRound /></el-icon>
        </div>
        <div class="welcome-bubble">
          <p>你好！我是MindMates，您的心理健康AI伴侣。</p>
          <p>无论您正在经历什么，我都在这里倾听。请放心地分享您的想法和感受。</p>
          <p class="hint">💡 提示：我们的对话是私密的，但如果您正在经历严重困扰，请寻求专业帮助。</p>
        </div>
      </div>

      <!-- 消息列表 -->
      <template v-for="message in chatStore.messages" :key="message.id">
        <div :class="['message-item', message.role === 'user' ? 'user-message' : 'ai-message']">
          <!-- AI头像 -->
          <div v-if="message.role === 'assistant'" class="ai-avatar small">
            <el-icon :size="20"><ChatDotRound /></el-icon>
          </div>
          
          <!-- 消息气泡 -->
          <div :class="['chat-bubble', message.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai']">
            <p class="message-content">{{ message.content }}</p>
            <span class="message-time">{{ formatTime(message.createdAt) }}</span>
          </div>
        </div>

        <!-- 危机资源卡片 -->
        <div v-if="checkIsCrisis(message)" class="crisis-card">
          <el-alert type="warning" :closable="false" show-icon>
            <template #title>
              <strong>我们注意到您可能需要帮助</strong>
            </template>
            <p>如果您正在经历危机，请立即寻求专业帮助：</p>
            <ul class="crisis-list">
              <li v-for="resource in crisisResources" :key="resource.phone">
                <strong>{{ resource.name }}：</strong>
                <a :href="`tel:${resource.phone}`">{{ resource.phone }}</a>
              </li>
            </ul>
          </el-alert>
        </div>
      </template>

      <!-- AI正在输入 -->
      <div v-if="chatStore.isTyping" class="message-item ai-message">
        <div class="ai-avatar small">
          <el-icon :size="20"><ChatDotRound /></el-icon>
        </div>
        <div class="chat-bubble chat-bubble-ai typing-bubble">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </main>

    <!-- 输入区域 -->
    <footer class="chat-footer">
      <div class="input-wrapper">
        <el-input
          ref="inputRef"
          v-model="inputMessage"
          type="textarea"
          :rows="1"
          :autosize="{ minRows: 1, maxRows: 4 }"
          placeholder="说说您的想法..."
          :disabled="chatStore.isTyping"
          @keydown.enter.exact.prevent="sendMessage"
        />
        <el-button
          type="primary"
          circle
          :disabled="!inputMessage.trim() || chatStore.isTyping"
          @click="sendMessage"
        >
          <el-icon><Promotion /></el-icon>
        </el-button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.chat-container {
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #ebeef5;
}

.header-title {
  text-align: center;
}

.header-title h2 {
  font-size: 17px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.typing-indicator {
  font-size: 12px;
  color: #909399;
}

.header-right {
  width: 40px;
  display: flex;
  justify-content: center;
  color: #667eea;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.ai-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.ai-avatar.small {
  width: 36px;
  height: 36px;
}

.welcome-bubble {
  background: white;
  border-radius: 16px;
  border-top-left-radius: 4px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  flex: 1;
}

.welcome-bubble p {
  margin: 0 0 10px;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}

.welcome-bubble p:last-child {
  margin-bottom: 0;
}

.welcome-bubble .hint {
  color: #909399;
  font-size: 13px;
}

.message-item {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: flex-start;
}

.chat-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
}

.chat-bubble-user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.chat-bubble-ai {
  background: white;
  color: #303133;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-content {
  margin: 0;
  font-size: 15px;
  line-height: 1.5;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-time {
  display: block;
  font-size: 11px;
  opacity: 0.7;
  margin-top: 6px;
  text-align: right;
}

/* 危机资源卡片 */
.crisis-card {
  margin: 8px 0;
}

.crisis-list {
  margin: 8px 0 0;
  padding-left: 20px;
}

.crisis-list li {
  margin: 4px 0;
}

.crisis-list a {
  color: #409eff;
  text-decoration: none;
}

/* 正在输入动画 */
.typing-bubble {
  padding: 16px 20px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: #909399;
  border-radius: 50%;
  animation: typing 1.4s infinite both;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 输入区域 */
.chat-footer {
  padding: 12px 16px;
  background: white;
  border-top: 1px solid #ebeef5;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.input-wrapper :deep(.el-textarea__inner) {
  border-radius: 20px;
  padding: 10px 16px;
  resize: none;
  font-size: 15px;
}

.input-wrapper .el-button {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
}
</style>
