<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'

const props = defineProps<{
  screenshot: string
  focusBox: [number, number, number, number] | null
}>()

const containerRef = ref<HTMLDivElement | null>(null)
const containerSize = ref({ width: 0, height: 0 })

const updateSize = () => {
  if (containerRef.value) {
    containerSize.value = {
      width: containerRef.value.clientWidth,
      height: containerRef.value.clientHeight
    }
  }
}

onMounted(() => {
  updateSize()
  window.addEventListener('resize', updateSize)
})

const focusBoxStyle = computed(() => {
  if (!props.focusBox || !containerSize.value.width) return null
  
  const [y1, x1, y2, x2] = props.focusBox
  const { width, height } = containerSize.value
  
  const left = (x1 / 1000) * width
  const top = (y1 / 1000) * height
  const boxWidth = ((x2 - x1) / 1000) * width
  const boxHeight = ((y2 - y1) / 1000) * height
  
  return {
    left: `${left}px`,
    top: `${top}px`,
    width: `${boxWidth}px`,
    height: `${boxHeight}px`
  }
})

const isAnimating = ref(false)

watch(() => props.focusBox, (newVal, oldVal) => {
  if (newVal && JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
    isAnimating.value = true
    setTimeout(() => { isAnimating.value = false }, 500)
  }
})
</script>

<template>
  <div class="screenshot-viewer" ref="containerRef">
    <div v-if="!screenshot" class="placeholder">
      <div class="placeholder-icon">🖥️</div>
      <div class="placeholder-text">等待截图...</div>
      <div class="placeholder-hint">输入任务后，将在此显示屏幕截图</div>
    </div>
    
    <img v-else :src="`data:image/png;base64,${screenshot}`" alt="Screen capture" class="screenshot-image" />
    
    <div v-if="focusBoxStyle" class="focus-box" :class="{ animating: isAnimating }" :style="focusBoxStyle">
      <div class="focus-corner tl"></div>
      <div class="focus-corner tr"></div>
      <div class="focus-corner bl"></div>
      <div class="focus-corner br"></div>
    </div>
    
    <div v-if="focusBox" class="coordinate-info">📍 {{ focusBox.join(', ') }}</div>
  </div>
</template>

<style scoped>
.screenshot-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  background: #0d1117;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #6e7681;
}

.placeholder-icon { font-size: 64px; opacity: 0.5; }
.placeholder-text { font-size: 18px; font-weight: 500; }
.placeholder-hint { font-size: 14px; opacity: 0.7; }

.screenshot-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.focus-box {
  position: absolute;
  border: 3px solid #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 4px;
  pointer-events: none;
  transition: all 0.3s ease;
  box-shadow: 0 0 20px rgba(255, 107, 107, 0.4);
}

.focus-box.animating { animation: pulse 0.5s ease-out; }

@keyframes pulse {
  0% { transform: scale(1.1); opacity: 0; }
  50% { opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}

.focus-corner {
  position: absolute;
  width: 12px;
  height: 12px;
  border: 3px solid #ff6b6b;
}

.focus-corner.tl { top: -3px; left: -3px; border-right: none; border-bottom: none; }
.focus-corner.tr { top: -3px; right: -3px; border-left: none; border-bottom: none; }
.focus-corner.bl { bottom: -3px; left: -3px; border-right: none; border-top: none; }
.focus-corner.br { bottom: -3px; right: -3px; border-left: none; border-top: none; }

.coordinate-info {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
  color: #ccc;
}
</style>
