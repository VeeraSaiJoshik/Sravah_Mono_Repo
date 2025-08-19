<template>
  <div class="h-full w-full py-4 overflow-y-scroll scrollbar-hide bg-white rounded-sm">
    <div class="flex flex-col space-y-4">
      <div
        v-for="chat in chats"
        :key="chat.message"
        class="flex w-full"
        :class="chat.human ? 'justify-end' : 'justify-start'"
      >
        <div v-if="!chat.human" class="flex items-end space-x-2">
          <img
            src="/images/logo.png"
            alt="Bot Avatar"
            class="h-8 w-8 rounded-full border border-accent object-cover"
          />
          <div class="max-w-[80%] px-[10px] py-2 rounded-md bg-passive_background text-[12px] font-gotham text-black shadow-sm">
            {{ chat.message }}
          </div>
        </div>

        <div v-else class="flex items-end space-x-2 flex-row-reverse">
          <img
            src="https://t4.ftcdn.net/jpg/06/08/55/73/360_F_608557356_ELcD2pwQO9pduTRL30umabzgJoQn5fnd.jpg"
            alt="User Avatar"
            class="h-8 w-8 rounded-full border-2 border-dark_primary object-cover ml-2"
          />
          <div class="max-w-[80%] px-[10px] py-2 rounded-md bg-dark_primary text-[12px] font-gotham text-white shadow-md">
            {{ chat.message }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ComputedRef } from 'vue';
import { Chat } from '../models/call_models';

const props = defineProps<{
  chats: Chat[]
}>()

const chats: ComputedRef<Chat[]> = computed(() => props.chats)
</script>
