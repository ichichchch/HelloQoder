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
      <el-button circle text @click="goBack">
        <el-icon :size="20"><ArrowLeft /></el-icon>
      </el-button>
      <h2 class="header-title">对话历史</h2>
      <div class="header-right" style="width: 40px;"></div>
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
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #ebeef5;
}

.header-title {
  font-size: 17px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.history-main {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.session-card {
  border-radius: 14px;
  cursor: pointer;
  border: none;
  transition: transform 0.2s;
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
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 14px;
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
  margin: 0 0 4px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-preview {
  font-size: 13px;
  color: #909399;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 12px;
  color: #c0c4cc;
}
</style>
