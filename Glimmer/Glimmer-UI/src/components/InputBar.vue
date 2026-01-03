<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ disabled?: boolean }>()
const emit = defineEmits<{ send: [text: string] }>()

const inputText = ref('')

const handleSend = () => {
  const text = inputText.value.trim()
  if (text && !props.disabled) {
    emit('send', text)
    inputText.value = ''
  }
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="input-bar">
    <div class="input-wrapper">
      <textarea v-model="inputText" @keydown="handleKeydown" :disabled="disabled"
        placeholder="输入你想完成的任务..." rows="1" class="input-field" />
      <button @click="handleSend" :disabled="disabled || !inputText.trim()" class="send-button">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" />
        </svg>
      </button>
    </div>
    <div class="input-hint">
      <span v-if="disabled">⏳ 正在执行任务...</span>
      <span v-else>按 Enter 发送，Shift+Enter 换行</span>
    </div>
  </div>
</template>

<style scoped>
.input-bar { padding: 16px; border-top: 1px solid rgba(255, 255, 255, 0.1); background: rgba(0, 0, 0, 0.2); }
.input-wrapper { display: flex; gap: 8px; align-items: flex-end; }

.input-field {
  flex: 1; padding: 12px 16px; border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px; background: rgba(255, 255, 255, 0.05);
  color: #fff; font-size: 14px; resize: none;
  min-height: 44px; max-height: 120px; transition: all 0.2s; font-family: inherit;
}

.input-field:focus {
  outline: none; border-color: #667eea;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.input-field::placeholder { color: #6e7681; }
.input-field:disabled { opacity: 0.5; cursor: not-allowed; }

.send-button {
  width: 44px; height: 44px; border: none; border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; cursor: pointer; display: flex;
  align-items: center; justify-content: center;
  transition: all 0.2s; flex-shrink: 0;
}

.send-button:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
.send-button:disabled { opacity: 0.5; cursor: not-allowed; }
.send-button svg { width: 20px; height: 20px; }
.input-hint { margin-top: 8px; font-size: 11px; color: #6e7681; text-align: center; }
</style>
