import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 默认用户（已移除登录认证）
  const user = ref<User | null>({
    id: '00000000-0000-0000-0000-000000000001',
    username: 'user',
    nickname: '用户'
  })

  const userName = computed(() => user.value?.nickname || user.value?.username || '用户')

  async function login(username: string, password: string) {
    try {
      const response = await authApi.login({ username, password })
      user.value = response.user
      localStorage.setItem('token', response.token)
      return { success: true }
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : '登录失败'
      return { success: false, message }
    }
  }

  async function register(username: string, password: string, nickname?: string) {
    try {
      const response = await authApi.register({ username, password, nickname })
      user.value = response.user
      localStorage.setItem('token', response.token)
      return { success: true }
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : '注册失败'
      return { success: false, message }
    }
  }

  function logout() {
    user.value = null
    localStorage.removeItem('token')
  }

  return {
    user,
    userName,
    login,
    register,
    logout
  }
})
