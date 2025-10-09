<template>
  <div class="w-full h-full bg-white rounded-xl border border-gray-200 shadow-lg p-2 flex flex-col items-start">
    <!-- Scrollable Pages -->
    <div
      ref="scrollContainer"
      class="flex overflow-hidden transition-all duration-300 w-full h-full"
      style="scroll-behavior: smooth;"
    >
      <!-- Each Page -->
      <div class="w-full shrink-0 h-full">
        <Summary_screen />
      </div>
      <div class="w-full shrink-0 h-full">
        <Chat_screen :chats="chat"/>
      </div>
      <div class="w-full shrink-0 h-full">
        <Actions_screen />
      </div>
    </div>
    <div class="flex font-sans font-[600] space-x-2 p-[3px] bg-gray-100 rounded-md transition-all ease-in-out duration-300">
      <button
        :class="tabClass(SideBarState.CHAT)"
        @click="() => changeTab(SideBarState.CHAT)">
        💬
      </button>
      <button
        :class="tabClass(SideBarState.ACTIONS)"
        @click="() => changeTab(SideBarState.ACTIONS)">
        ✏️
      </button>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, watch } from 'vue';
import { SideBarState } from '../models/meeting_state';
import Summary_screen from './summary_screen.vue';
import Chat_screen from './chat_screen.vue';
import Actions_screen from './actions_screen.vue';
import { Chat } from '../models/call_models';

const sideBarState = ref<SideBarState>(SideBarState.SUMMARY)
const scrollContainer = ref<HTMLElement | null>(null)

const tabClass = (tab: SideBarState) => [
  'py-1 px-2 rounded-[4px] transition-all ease-in-out duration-300',
  sideBarState.value === tab
    ? 'bg-dark_primary text-gray-100'
    : 'text-black hover:text-dark_primary'
]

watch(sideBarState, (newVal) => {
  const index = {
    [SideBarState.SUMMARY]: 0,
    [SideBarState.CHAT]: 1,
    [SideBarState.ACTIONS]: 2
  }[newVal]

  if (scrollContainer.value) {
    scrollContainer.value.scrollLeft = index * scrollContainer.value.clientWidth
  }
})

const changeTab = (tab: SideBarState) => {
  sideBarState.value = tab
}

const chat = ref<Chat[]>([
  {
    human: false, 
    message: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris ut finibus lorem, non interdum tortor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Aliquam vestibulum cursus orci eu gravida. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Phasellus id turpis faucibus, aliquet mi vel, cursus nisi. Aenean faucibus volutpat porttitor. Interdum et malesuada fames ac ante ipsum"
  },
  {
    human: true, 
    message: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris ut finibus lorem, non interdum tortor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Aliquam vestibulum cursus orci eu gravida. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Phasellus id turpis faucibus, aliquet mi vel, cursus nisi. Aenean faucibus volutpat porttitor. Interdum et malesuada fames ac ante ipsum"
  },
  {
    human: true, 
    message: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris ut finibus lorem, non interdum tortor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Aliquam vestibulum cursus orci eu gravida. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Phasellus id turpis faucibus, aliquet mi vel, cursus nisi. Aenean faucibus volutpat porttitor. Interdum et malesuada fames ac ante ipsum"
  }
])

</script>