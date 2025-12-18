<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useChatStore } from '@/stores/chat'

const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()

// 根据时间获取问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return { text: '夜深了', sub: '还没休息吗？' }
  if (hour < 9) return { text: '早上好', sub: '新的一天开始了' }
  if (hour < 12) return { text: '上午好', sub: '今天精神怎么样？' }
  if (hour < 14) return { text: '中午好', sub: '记得休息一下' }
  if (hour < 18) return { text: '下午好', sub: '这会儿感觉如何？' }
  if (hour < 22) return { text: '晚上好', sub: '轻松一下吧' }
  return { text: '夜已深', sub: '有什么心事吗？' }
})

onMounted(() => {
  chatStore.fetchSessions()
})

function startNewChat() {
  chatStore.clearCurrentSession()
  router.push('/chat')
}

function goToHistory() {
  router.push('/history')
}
</script>

<template>
  <div class="home-container safe-area-top safe-area-bottom">
    <!-- 顶部区域 -->
    <header class="home-header">
      <div class="header-content">
        <div class="brand-icon">
          <el-icon :size="28"><ChatDotRound /></el-icon>
        </div>
        <div class="greeting">
          <h2 class="greeting-title">{{ greeting.text }} 👋</h2>
          <p class="greeting-text">{{ greeting.sub }}</p>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="home-main">
      <!-- 开始对话卡片 -->
      <div class="start-section">
        <el-card class="start-card" shadow="always" @click="startNewChat">
          <div class="start-content">
            <div class="start-icon">
              <el-icon :size="32"><ChatLineSquare /></el-icon>
            </div>
            <div class="start-text">
              <h3>开始新对话</h3>
              <p>和心理委员分享您的想法</p>
            </div>
            <el-icon class="start-arrow"><ArrowRight /></el-icon>
          </div>
        </el-card>
      </div>

      <!-- 最近对话 -->
      <div class="recent-section">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon><Clock /></el-icon>
            最近对话
          </h3>
          <el-button v-if="chatStore.sortedSessions.length > 0" class="view-all-btn" text @click="goToHistory">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        
        <div v-if="chatStore.sortedSessions.length === 0" class="empty-hint">
          <el-icon :size="40"><Document /></el-icon>
          <p>还没有对话记录</p>
          <span>开始您的第一次对话吧</span>
        </div>

        <div v-else class="session-list">
          <div
            v-for="session in chatStore.sortedSessions.slice(0, 4)"
            :key="session.id"
            class="session-item"
            @click="router.push(`/chat/${session.id}`)"
          >
            <div class="session-dot"></div>
            <div class="session-info">
              <h4>{{ session.title || '新对话' }}</h4>
              <p>{{ session.lastMessage || '暂无消息' }}</p>
            </div>
            <el-icon class="session-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 底部提示 -->
      <div class="tips-section">
        <div class="tips-content">
          <el-icon :size="18"><InfoFilled /></el-icon>
          <span>如遇紧急情况，请拨打心理援助热线：<strong>400-161-9995</strong></span>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #FF9A6C 0%, #FFE8E0 25%, #FFF8F5 50%);
  display: flex;
  flex-direction: column;
}

.home-header {
  padding: 24px 20px 32px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.greeting {
  color: white;
}

.greeting-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 4px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.greeting-text {
  font-size: 14px;
  opacity: 0.85;
  margin: 0;
}

.home-main {
  flex: 1;
  padding: 0 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 开始对话卡片 */
.start-section {
  margin-top: -16px;
}

.start-card {
  border-radius: 20px;
  border: none;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.start-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 107, 107, 0.2);
}

.start-card:active {
  transform: scale(0.98);
}

.start-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.start-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #FF9A6C 0%, #FF6B6B 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.start-text {
  flex: 1;
}

.start-text h3 {
  font-size: 17px;
  font-weight: 600;
  margin: 0 0 4px;
  color: #303133;
}

.start-text p {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.start-arrow {
  color: #FF8C6B;
  font-size: 18px;
}

/* 最近对话 */
.recent-section {
  flex: 1;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-title .el-icon {
  color: #FF8C6B;
}

.view-all-btn {
  color: #FF8C6B !important;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 12px !important;
  border-radius: 16px;
  background: rgba(255, 140, 107, 0.1) !important;
  transition: all 0.2s;
}

.view-all-btn:hover {
  background: rgba(255, 140, 107, 0.2) !important;
}

.view-all-btn .el-icon {
  margin-left: 2px;
  font-size: 12px;
}

.empty-hint {
  text-align: center;
  padding: 40px 20px;
  color: #c0c4cc;
}

.empty-hint .el-icon {
  margin-bottom: 12px;
}

.empty-hint p {
  font-size: 15px;
  margin: 0 0 4px;
  color: #909399;
}

.empty-hint span {
  font-size: 13px;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: white;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.session-item:hover {
  background: #FFF5F0;
}

.session-item:active {
  transform: scale(0.98);
}

.session-dot {
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #FF9A6C 0%, #FF6B6B 100%);
  border-radius: 50%;
  flex-shrink: 0;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-info h4 {
  font-size: 15px;
  font-weight: 500;
  margin: 0 0 3px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-info p {
  font-size: 13px;
  color: #909399;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-arrow {
  color: #c0c4cc;
  flex-shrink: 0;
}

/* 底部提示 */
.tips-section {
  margin-top: auto;
}

.tips-content {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #FFF5E6 0%, #FFE8D9 100%);
  border-radius: 12px;
  font-size: 13px;
  color: #8B5A2B;
}

.tips-content .el-icon {
  color: #E6A23C;
  flex-shrink: 0;
}

.tips-content strong {
  color: #FF8C6B;
}
</style>
