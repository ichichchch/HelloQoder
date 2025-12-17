import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => user.value?.nickname || user.value?.username || '用户')

  async function login(username: string, password: string) {
    try {
      const response = await authApi.login({ username, password })
      token.value = response.token
      user.value = response.user
      localStorage.setItem('token', response.token)
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '登录失败' }
    }
  }

  async function register(username: string, password: string, nickname?: string) {
    try {
      const response = await authApi.register({ username, password, nickname })
      token.value = response.token
      user.value = response.user
      localStorage.setItem('token', response.token)
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '注册失败' }
    }
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      const response = await authApi.getProfile()
      user.value = response
    } catch (error) {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  // 初始化时获取用户信息
  if (token.value) {
    fetchProfile()
  }

  return {
    user,
    token,
    isLoggedIn,
    userName,
    login,
    register,
    fetchProfile,
    logout
  }
})
