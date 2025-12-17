<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useChatStore } from '@/stores/chat'

const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()

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

function goToProfile() {
  router.push('/profile')
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="home-container safe-area-top safe-area-bottom">
    <!-- 顶部导航 -->
    <header class="home-header">
      <div class="header-left">
        <div class="avatar-wrapper">
          <el-avatar :size="42" :icon="UserFilled" />
        </div>
        <div class="greeting">
          <p class="greeting-text">你好，</p>
          <h2 class="user-name">{{ userStore.userName }}</h2>
        </div>
      </div>
      <div class="header-right">
        <el-button circle @click="goToProfile">
          <el-icon><Setting /></el-icon>
        </el-button>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="home-main">
      <!-- 欢迎卡片 -->
      <el-card class="welcome-card" shadow="always">
        <div class="welcome-content">
          <div class="welcome-icon">
            <el-icon :size="40"><ChatDotRound /></el-icon>
          </div>
          <h3 class="welcome-title">今天感觉怎么样？</h3>
          <p class="welcome-desc">
            我是您的心理健康AI伴侣，随时准备倾听您的心声。
            无论是压力、焦虑还是任何困扰，我都在这里陪伴您。
          </p>
          <el-button type="primary" size="large" class="start-chat-btn" @click="startNewChat">
            <el-icon><ChatLineSquare /></el-icon>
            开始倾诉
          </el-button>
        </div>
      </el-card>

      <!-- 功能入口 -->
      <div class="feature-grid">
        <el-card class="feature-card" shadow="hover" @click="goToHistory">
          <div class="feature-icon history-icon">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <h4 class="feature-title">对话历史</h4>
          <p class="feature-desc">查看过往的对话记录</p>
        </el-card>

        <el-card class="feature-card" shadow="hover" @click="goToProfile">
          <div class="feature-icon profile-icon">
            <el-icon :size="28"><User /></el-icon>
          </div>
          <h4 class="feature-title">个人中心</h4>
          <p class="feature-desc">管理您的个人信息</p>
        </el-card>
      </div>

      <!-- 最近对话 -->
      <div v-if="chatStore.sortedSessions.length > 0" class="recent-section">
        <div class="section-header">
          <h3 class="section-title">最近对话</h3>
          <el-link type="primary" @click="goToHistory">查看全部</el-link>
        </div>
        <div class="session-list">
          <el-card
            v-for="session in chatStore.sortedSessions.slice(0, 3)"
            :key="session.id"
            class="session-card"
            shadow="hover"
            @click="router.push(`/chat/${session.id}`)"
          >
            <div class="session-info">
              <h4 class="session-title">{{ session.title || '新对话' }}</h4>
              <p class="session-preview">{{ session.lastMessage || '暂无消息' }}</p>
            </div>
            <el-icon class="session-arrow"><ArrowRight /></el-icon>
          </el-card>
        </div>
      </div>

      <!-- 心理健康提示 -->
      <el-card class="tips-card" shadow="hover">
        <div class="tips-content">
          <el-icon :size="24" class="tips-icon"><InfoFilled /></el-icon>
          <div class="tips-text">
            <h4>温馨提示</h4>
            <p>如果您正在经历严重的心理困扰，请及时寻求专业帮助。
            全国心理援助热线：<strong>400-161-9995</strong></p>
          </div>
        </div>
      </el-card>
    </main>

    <!-- 底部导航 -->
    <footer class="home-footer">
      <el-button type="danger" text @click="handleLogout">
        <el-icon><SwitchButton /></el-icon>
        退出登录
      </el-button>
    </footer>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #667eea 0%, #f5f7fa 30%);
  display: flex;
  flex-direction: column;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-wrapper {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  padding: 2px;
}

.greeting-text {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.home-main {
  flex: 1;
  padding: 0 20px 20px;
  overflow-y: auto;
}

.welcome-card {
  border-radius: 20px;
  margin-bottom: 20px;
  border: none;
}

.welcome-content {
  text-align: center;
  padding: 20px 0;
}

.welcome-icon {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: white;
}

.welcome-title {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 12px;
  color: #303133;
}

.welcome-desc {
  font-size: 14px;
  color: #909399;
  line-height: 1.6;
  margin: 0 0 20px;
}

.start-chat-btn {
  height: 48px;
  padding: 0 32px;
  font-size: 16px;
  border-radius: 24px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.feature-card {
  border-radius: 16px;
  cursor: pointer;
  transition: transform 0.2s;
  border: none;
}

.feature-card:active {
  transform: scale(0.98);
}

.feature-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  color: white;
}

.history-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.profile-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px;
  color: #303133;
}

.feature-desc {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.recent-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.session-card {
  border-radius: 14px;
  cursor: pointer;
  border: none;
}

.session-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  padding: 14px 16px;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 15px;
  font-weight: 500;
  margin: 0 0 4px;
  color: #303133;
}

.session-preview {
  font-size: 13px;
  color: #909399;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-arrow {
  color: #c0c4cc;
}

.tips-card {
  border-radius: 16px;
  background: #fff9e6;
  border: 1px solid #ffeeba;
}

.tips-content {
  display: flex;
  gap: 12px;
}

.tips-icon {
  color: #e6a23c;
  flex-shrink: 0;
  margin-top: 2px;
}

.tips-text h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 6px;
  color: #856404;
}

.tips-text p {
  font-size: 13px;
  color: #856404;
  margin: 0;
  line-height: 1.5;
}

.home-footer {
  padding: 16px 20px;
  text-align: center;
  background: white;
  border-top: 1px solid #ebeef5;
}
</style>
