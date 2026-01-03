<script setup lang="ts">
import { ref } from 'vue'
import ScreenshotViewer from './components/ScreenshotViewer.vue'
import ChatPanel from './components/ChatPanel.vue'
import InputBar from './components/InputBar.vue'
import StatusIndicator from './components/StatusIndicator.vue'
import type { GlimmerResponse, ChatMessage, AgentState } from './types'

const agentState = ref<AgentState>({
  status: 'idle',
  currentTask: '',
  progress: 0
})

const screenshot = ref<string>('')
const focusBox = ref<[number, number, number, number] | null>(null)

const messages = ref<ChatMessage[]>([
  {
    id: '1',
    role: 'assistant',
    content: '👋 你好！我是 GLIMMER，你的 GUI 自动化助手。告诉我你想完成什么任务吧！',
    timestamp: new Date()
  }
])

const handleSendMessage = async (text: string) => {
  const userMessage: ChatMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: text,
    timestamp: new Date()
  }
  messages.value.push(userMessage)
  
  agentState.value = {
    status: 'working',
    currentTask: text,
    progress: 10
  }
  
  try {
    const response = await fetch('/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal: text })
    })
    
    if (!response.ok) throw new Error('API request failed')
    
    const data: GlimmerResponse = await response.json()
    
    focusBox.value = data.ui_focus_box
    if (data.screenshot) {
      screenshot.value = data.screenshot
    }
    
    const assistantMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: data.ui_thought,
      timestamp: new Date(),
      status: data.status,
      action: data.operation?.action
    }
    messages.value.push(assistantMessage)
    
    agentState.value = {
      status: data.status === 'DONE' ? 'done' : 
              data.status === 'FAIL' ? 'error' : 'working',
      currentTask: text,
      progress: data.progress || (data.status === 'DONE' ? 100 : 50)
    }
    
  } catch (error) {
    console.error('Error:', error)
    messages.value.push({
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '抱歉，执行过程中出现了错误。请检查后端服务是否正常运行。',
      timestamp: new Date(),
      status: 'FAIL'
    })
    agentState.value = { status: 'error', currentTask: text, progress: 0 }
  }
}

const handleDemoMode = () => {
  screenshot.value = ''
  focusBox.value = [100, 300, 200, 700]
  
  setTimeout(() => {
    messages.value.push({
      id: Date.now().toString(),
      role: 'assistant',
      content: '我在屏幕中央找到了搜索框，正在点击它...',
      timestamp: new Date(),
      status: 'WORKING',
      action: 'click'
    })
    agentState.value = { status: 'working', currentTask: '搜索示例', progress: 30 }
  }, 500)
  
  setTimeout(() => {
    focusBox.value = [100, 300, 200, 700]
    messages.value.push({
      id: Date.now().toString(),
      role: 'assistant',
      content: '正在输入搜索内容...',
      timestamp: new Date(),
      status: 'WORKING',
      action: 'type'
    })
    agentState.value = { status: 'working', currentTask: '搜索示例', progress: 60 }
  }, 2000)
  
  setTimeout(() => {
    focusBox.value = null
    messages.value.push({
      id: Date.now().toString(),
      role: 'assistant',
      content: '✅ 搜索完成！结果已显示在页面上。',
      timestamp: new Date(),
      status: 'DONE'
    })
    agentState.value = { status: 'done', currentTask: '搜索示例', progress: 100 }
  }, 3500)
}

const handleClear = () => {
  messages.value = [{
    id: '1',
    role: 'assistant',
    content: '👋 聊天已清空。有什么我可以帮助你的吗？',
    timestamp: new Date()
  }]
  focusBox.value = null
  screenshot.value = ''
  agentState.value = { status: 'idle', currentTask: '', progress: 0 }
}
</script>

<template>
  <div class="glimmer-app">
    <header class="app-header">
      <div class="logo">
        <span class="logo-icon">✨</span>
        <span class="logo-text">GLIMMER</span>
      </div>
      <StatusIndicator :state="agentState" />
      <div class="header-actions">
        <button class="btn-demo" @click="handleDemoMode">演示模式</button>
        <button class="btn-clear" @click="handleClear">清空</button>
      </div>
    </header>
    
    <main class="app-main">
      <div class="screenshot-panel">
        <ScreenshotViewer :screenshot="screenshot" :focusBox="focusBox" />
      </div>
      
      <div class="chat-panel">
        <ChatPanel :messages="messages" />
        <InputBar @send="handleSendMessage" :disabled="agentState.status === 'working'" />
      </div>
    </main>
  </div>
</template>

<style scoped>
.glimmer-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-demo, .btn-clear {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-demo {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-demo:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-clear {
  background: rgba(255, 255, 255, 0.1);
  color: #ccc;
}

.btn-clear:hover {
  background: rgba(255, 255, 255, 0.2);
}

.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.screenshot-panel {
  flex: 1;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
}

.chat-panel {
  width: 400px;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.03);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
