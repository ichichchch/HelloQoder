<script setup lang="ts">
import { computed } from 'vue'
import type { AgentState } from '../types'

const props = defineProps<{ state: AgentState }>()

const statusInfo = computed(() => {
  switch (props.state.status) {
    case 'idle': return { icon: '💤', text: '待命', color: '#6e7681' }
    case 'working': return { icon: '⏳', text: '执行中', color: '#3b82f6' }
    case 'done': return { icon: '✅', text: '完成', color: '#22c55e' }
    case 'error': return { icon: '❌', text: '错误', color: '#ef4444' }
    default: return { icon: '💤', text: '待命', color: '#6e7681' }
  }
})
</script>

<template>
  <div class="status-indicator">
    <div class="status-dot" :class="state.status" :style="{ '--status-color': statusInfo.color }" />
    <div class="status-content">
      <span class="status-icon">{{ statusInfo.icon }}</span>
      <span class="status-text">{{ statusInfo.text }}</span>
    </div>
    <div v-if="state.status === 'working'" class="progress-bar">
      <div class="progress-fill" :style="{ width: `${state.progress}%` }" />
    </div>
    <div v-if="state.currentTask" class="current-task">
      {{ state.currentTask.length > 30 ? state.currentTask.slice(0, 30) + '...' : state.currentTask }}
    </div>
  </div>
</template>

<style scoped>
.status-indicator {
  display: flex; align-items: center; gap: 12px;
  padding: 8px 16px; background: rgba(255, 255, 255, 0.05); border-radius: 20px;
}

.status-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--status-color); box-shadow: 0 0 8px var(--status-color);
}

.status-dot.working { animation: pulse 1.5s ease-in-out infinite; }

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.9); }
}

.status-content { display: flex; align-items: center; gap: 4px; }
.status-icon { font-size: 14px; }
.status-text { font-size: 13px; font-weight: 500; color: #ccc; }

.progress-bar {
  width: 60px; height: 4px;
  background: rgba(255, 255, 255, 0.1); border-radius: 2px; overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.current-task {
  font-size: 12px; color: #6e7681;
  max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
</style>
