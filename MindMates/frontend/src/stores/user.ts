import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'

export const useUserStore = defineStore('user', () => {
  // 默认用户（已移除登录认证）
  const user = ref<User | null>({
    id: '00000000-0000-0000-0000-000000000001',
    username: 'user',
    nickname: '用户'
  })

  const userName = computed(() => user.value?.nickname || user.value?.username || '用户')

  return {
    user,
    userName
  }
})
