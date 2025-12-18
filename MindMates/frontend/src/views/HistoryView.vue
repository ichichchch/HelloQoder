<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const chatStore = useChatStore()

onMounted(() => {
  chatStore.fetchSessions()
})

function goBack() {
  router.push('/home')
}

function openSession(sessionId: string) {
  router.push(`/chat/${sessionId}`)
}

async function deleteSession(sessionId: string, event: Event) {
  event.stopPropagation()
  
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await chatStore.deleteSession(sessionId)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return '今天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
}
</script>

<template>
  <div class="history-container safe-area-top safe-area-bottom">
    <!-- 顶部栏 -->
    <header class="history-header">
      <el-button class="back-btn" circle text @click="goBack">
        <el-icon :size="20"><ArrowLeft /></el-icon>
      </el-button>
      <div class="header-title">
        <el-icon :size="18"><Document /></el-icon>
        <h2>对话历史</h2>
      </div>
      <div class="header-right"></div>
    </header>

    <!-- 会话列表 -->
    <main class="history-main">
      <div v-if="chatStore.sortedSessions.length === 0" class="empty-state">
        <el-empty description="暂无对话记录">
          <el-button type="primary" @click="router.push('/chat')">
            开始新对话
          </el-button>
        </el-empty>
      </div>

      <div v-else class="session-list">
        <el-card
          v-for="session in chatStore.sortedSessions"
          :key="session.id"
          class="session-card"
          shadow="hover"
          @click="openSession(session.id)"
        >
          <div class="session-content">
            <div class="session-icon">
              <el-icon :size="24"><ChatDotRound /></el-icon>
            </div>
            <div class="session-info">
              <h4 class="session-title">{{ session.title || '新对话' }}</h4>
              <p class="session-preview">{{ session.lastMessage || '暂无消息' }}</p>
              <span class="session-time">{{ formatDate(session.updatedAt) }}</span>
            </div>
            <el-button
              type="danger"
              text
              circle
              @click="deleteSession(session.id, $event)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </el-card>
      </div>
    </main>
  </div>
</template>

<style scoped>
.history-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #FF9A6C 0%, #FFF8F5 20%);
  display: flex;
  flex-direction: column;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  color: white;
}

.back-btn {
  color: white !important;
  background: rgba(255,255,255,0.15) !important;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title h2 {
  font-size: 17px;
  font-weight: 600;
  margin: 0;
}

.header-right {
  width: 40px;
}

.history-main {
  flex: 1;
  padding: 0 16px 16px;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60vh;
  background: white;
  border-radius: 20px;
  margin-top: 8px;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.session-card {
  border-radius: 16px;
  cursor: pointer;
  border: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.session-card:hover {
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}

.session-card:active {
  transform: scale(0.98);
}

.session-content {
  display: flex;
  align-items: center;
  gap: 14px;
}

.session-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #FFB088 0%, #FF8C6B 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 3px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-preview {
  font-size: 13px;
  color: #909399;
  margin: 0 0 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 11px;
  color: #c0c4cc;
}
</style>
