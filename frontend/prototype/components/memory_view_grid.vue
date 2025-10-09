<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { MeetingNode } from '../models/node'

// --- Refs and state ---
const world = ref<HTMLDivElement>()
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })
const mouseStart = ref({ x: 0, y: 0 })

const pan = ref({ x: 0, y: 0 })
const scale = ref(1)
const gridSize = 20

const nodes = ref<MeetingNode[]>([
  { id: 1, label: 'Node A', x: 0, y: 0 },
]) 

// --- Panning ---
const handleMouseDown = (e: MouseEvent) => {
  isPanning.value = true
  mouseStart.value = { x: e.clientX, y: e.clientY }
  panStart.value = { ...pan.value }
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isPanning.value) return
  const dx = e.clientX - mouseStart.value.x
  const dy = e.clientY - mouseStart.value.y
  pan.value.x = panStart.value.x + dx
  pan.value.y = panStart.value.y + dy
}

const handleMouseUp = () => {
  isPanning.value = false
}

// --- Zooming ---
const handleWheel = (e: WheelEvent) => {
  return 
  
  // e.preventDefault()
  // const scaleFactor = e.deltaY > 0 ? 0.9 : 1.1
  // const newScale = Math.max(0.2, Math.min(4, scale.value * scaleFactor))
  // const rect = world.value?.getBoundingClientRect()
  // if (!rect) return

  // // Zoom around cursor
  // const mouseX = e.clientX - rect.left
  // const mouseY = e.clientY - rect.top
  // const worldX = (mouseX - pan.value.x) / scale.value
  // const worldY = (mouseY - pan.value.y) / scale.value

  // scale.value = newScale
  // pan.value.x = mouseX - worldX * scale.value
  // pan.value.y = mouseY - worldY * scale.value
}

// --- World transform utility ---
const worldTransform = () =>
  `translate(${pan.value.x}px, ${pan.value.y}px) scale(${scale.value})`

onMounted(() => {
  document.addEventListener('mouseup', handleMouseUp)
  document.addEventListener('mousemove', handleMouseMove)
})

onUnmounted(() => {
  document.removeEventListener('mouseup', handleMouseUp)
  document.removeEventListener('mousemove', handleMouseMove)
})
</script>

<template>
  <div
    class="relative w-full h-full overflow-hidden bg-white active:cursor-move rounded-xl border border-gray-200 shadow-lg"
    @mousedown="handleMouseDown"
    @wheel="handleWheel"
  >
    <div
      ref="world"
      class="absolute inset-0 origin-top-left"
      :style="{ transform: worldTransform(), transformOrigin: '0 0' }"
    >
      <div
        v-for="node in nodes"
        :key="node.id"
        :style="{
          transform: `translate(${node.x}px, ${node.y}px)`,
        }"
      >
        <div class="
          w-[400px]
          absolute
          text-white font-open-sans font-bold text-lg
          bg-gradient-to-br from-gray-50/50 to-gray-50/100 rounded-xl 
          active:from-gray-100/50 active:to-gray-200/50 active:scale-105 active:shadow-lg active:cursor-move
          flex flex-col shadow-md 
          border border-gray-300/30 select-none 
          transition-all duration-200 cursor-pointer"
        >
          <div class="bg-gradient-to-br from-purple-500/75 to-purple-500 p-3 rounded-t-xl">
            <p>🗓️ Monday, August 17</p>
            <div class="w-full flex mt-[6px] space-x-2">
              <div class="p-[7px] bg-gradient-to-br from-black/5 to-black/15 font-open-sans font-semibold leading-none text-sm rounded-md">
                Project ABC
              </div>
              <div class="p-[7px] bg-gradient-to-br from-black/5 to-black/15 font-open-sans font-semibold leading-none text-sm rounded-md">
                Project ABC
              </div>
              <div class="p-[7px] bg-gradient-to-br from-black/5 to-black/15 font-open-sans font-semibold leading-none text-sm rounded-md">
                Project ABC
              </div>
            </div>
          </div>
          <div class="px-3  flex flex-col items-start justify-start w-full h-full mb-2">
            <div class="w-full h-5 rounded-md bg-gray-200/60 mt-[10px]">
              <div class="w-[10%] h-5 rounded-md bg-gray-200/60 bg-gradient-to-br from-[#96dd97] to-[#38d65f]"></div>
            </div>
            <p class="font-semibold text-[10px] text-black">⏰ 1:15/15:00</p>
            <div class="w-full flex justify-center">
              <div v-if="false" class="p-[6px] rounded-md font-semibold text-xs leading-none text-white bg-gradient-to-br from-green-400 to-green-500 ">👂🏽 Listening</div>
              <div v-if="true" class="p-[6px] rounded-md font-semibold text-xs leading-none text-white bg-gradient-to-br from-orange-300 to-orange-400 ">🧠 Thinking</div>
              <div v-if="false" class="p-[6px] rounded-md font-semibold text-xs leading-none text-white bg-gradient-to-br from-red-400 to-red-500 ">🔈 Speaking</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
