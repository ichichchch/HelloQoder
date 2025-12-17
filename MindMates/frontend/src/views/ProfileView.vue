<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const editMode = ref(false)
const formRef = ref()

const form = reactive({
  nickname: userStore.user?.nickname || '',
  email: userStore.user?.email || ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const showPasswordDialog = ref(false)

function goBack() {
  router.push('/home')
}

function toggleEditMode() {
  if (editMode.value) {
    // 取消编辑，恢复原值
    form.nickname = userStore.user?.nickname || ''
    form.email = userStore.user?.email || ''
  }
  editMode.value = !editMode.value
}

async function saveProfile() {
  loading.value = true
  try {
    const updatedUser = await authApi.updateProfile({
      nickname: form.nickname,
      email: form.email
    })
    userStore.user = updatedUser
    editMode.value = false
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

async function changePassword() {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  if (passwordForm.newPassword.length < 6) {
    ElMessage.error('新密码长度至少6位')
    return
  }

  loading.value = true
  try {
    await authApi.changePassword(passwordForm.oldPassword, passwordForm.newPassword)
    ElMessage.success('密码修改成功')
    showPasswordDialog.value = false
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch {
    ElMessage.error('密码修改失败，请检查原密码是否正确')
  } finally {
    loading.value = false
  }
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    userStore.logout()
    router.push('/login')
  } catch {
    // 用户取消
  }
}

const displayName = computed(() => {
  return userStore.user?.nickname || userStore.user?.username || '用户'
})
</script>

<template>
  <div class="profile-container safe-area-top safe-area-bottom">
    <!-- 顶部栏 -->
    <header class="profile-header">
      <el-button circle text @click="goBack">
        <el-icon :size="20"><ArrowLeft /></el-icon>
      </el-button>
      <h2 class="header-title">个人中心</h2>
      <el-button text @click="toggleEditMode">
        {{ editMode ? '取消' : '编辑' }}
      </el-button>
    </header>

    <main class="profile-main">
      <!-- 头像区域 -->
      <div class="avatar-section">
        <div class="avatar-wrapper">
          <el-avatar :size="80" :icon="UserFilled" />
        </div>
        <h3 class="user-name">{{ displayName }}</h3>
        <p class="user-id">@{{ userStore.user?.username }}</p>
      </div>

      <!-- 基本信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <h4 class="card-title">基本信息</h4>
        </template>

        <el-form label-position="left" label-width="80px">
          <el-form-item label="用户名">
            <span class="info-value">{{ userStore.user?.username }}</span>
          </el-form-item>

          <el-form-item label="昵称">
            <el-input
              v-if="editMode"
              v-model="form.nickname"
              placeholder="请输入昵称"
              clearable
            />
            <span v-else class="info-value">{{ userStore.user?.nickname || '未设置' }}</span>
          </el-form-item>

          <el-form-item label="邮箱">
            <el-input
              v-if="editMode"
              v-model="form.email"
              placeholder="请输入邮箱"
              clearable
            />
            <span v-else class="info-value">{{ userStore.user?.email || '未设置' }}</span>
          </el-form-item>

          <el-form-item label="注册时间">
            <span class="info-value">
              {{ userStore.user?.createdAt ? new Date(userStore.user.createdAt).toLocaleDateString('zh-CN') : '未知' }}
            </span>
          </el-form-item>
        </el-form>

        <el-button
          v-if="editMode"
          type="primary"
          :loading="loading"
          class="save-btn"
          @click="saveProfile"
        >
          保存修改
        </el-button>
      </el-card>

      <!-- 安全设置 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <h4 class="card-title">安全设置</h4>
        </template>

        <div class="setting-item" @click="showPasswordDialog = true">
          <div class="setting-info">
            <el-icon><Lock /></el-icon>
            <span>修改密码</span>
          </div>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </el-card>

      <!-- 关于 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <h4 class="card-title">关于</h4>
        </template>

        <div class="about-item">
          <span>版本</span>
          <span class="about-value">1.0.0</span>
        </div>
        <div class="about-item">
          <span>开发者</span>
          <span class="about-value">MindMates Team</span>
        </div>
      </el-card>

      <!-- 退出登录 -->
      <el-button
        type="danger"
        plain
        class="logout-btn"
        @click="handleLogout"
      >
        <el-icon><SwitchButton /></el-icon>
        退出登录
      </el-button>
    </main>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="90%"
      :max-width="400"
    >
      <el-form label-position="top">
        <el-form-item label="原密码">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            placeholder="请输入原密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="changePassword">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.profile-header {
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

.profile-main {
  flex: 1;
  padding: 20px 16px;
  overflow-y: auto;
}

.avatar-section {
  text-align: center;
  margin-bottom: 24px;
}

.avatar-wrapper {
  width: 88px;
  height: 88px;
  margin: 0 auto 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
}

.avatar-wrapper :deep(.el-avatar) {
  background: white;
  color: #667eea;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 4px;
  color: #303133;
}

.user-id {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.info-card {
  margin-bottom: 16px;
  border-radius: 14px;
  border: none;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.info-value {
  color: #606266;
}

.save-btn {
  width: 100%;
  margin-top: 8px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  cursor: pointer;
}

.setting-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #303133;
}

.about-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.about-item:last-child {
  border-bottom: none;
}

.about-value {
  color: #909399;
}

.logout-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  margin-top: 8px;
}
</style>
