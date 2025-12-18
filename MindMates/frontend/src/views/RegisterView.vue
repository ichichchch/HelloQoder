<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, UserFilled, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const formRef = ref()

const form = reactive({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  nickname: [
    { max: 30, message: '昵称最多30个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度为6-30个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

async function handleRegister() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    loading.value = true
    try {
      const result = await userStore.register(form.username, form.password, form.nickname || undefined)
      if (result.success) {
        ElMessage.success('注册成功')
        router.push('/home')
      } else {
        ElMessage.error(result.message || '注册失败')
      }
    } finally {
      loading.value = false
    }
  })
}

function goToLogin() {
  router.push('/login')
}
</script>

<template>
  <div class="register-container safe-area-top safe-area-bottom">
    <div class="register-content">
      <!-- Logo 区域 -->
      <div class="logo-section">
        <div class="logo-icon">
          <el-icon :size="48"><ChatDotRound /></el-icon>
        </div>
        <h1 class="app-title">MindMates</h1>
        <p class="app-subtitle">开启您的心灵之旅</p>
      </div>

      <!-- 注册表单 -->
      <el-card class="register-card" shadow="always">
        <template #header>
          <h2 class="card-title">创建账号</h2>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          size="large"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item label="昵称 (可选)" prop="nickname">
            <el-input
              v-model="form.nickname"
              placeholder="请输入昵称"
              :prefix-icon="UserFilled"
              clearable
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleRegister"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              class="register-button"
              @click="handleRegister"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-link">
          已有账号？
          <el-link type="primary" @click="goToLogin">立即登录</el-link>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-content {
  width: 100%;
  max-width: 400px;
}

.logo-section {
  text-align: center;
  margin-bottom: 24px;
}

.logo-icon {
  width: 72px;
  height: 72px;
  background: white;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  color: #667eea;
}

.app-title {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.app-subtitle {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 6px;
}

.register-card {
  border-radius: 16px;
  border: none;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  text-align: center;
  margin: 0;
  color: #303133;
}

.register-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  border-radius: 10px;
}

.login-link {
  text-align: center;
  margin-top: 16px;
  color: #909399;
}
</style>
