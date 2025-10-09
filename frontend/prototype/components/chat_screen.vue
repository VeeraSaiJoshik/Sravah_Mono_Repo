<template>
  <div class="h-full w-full py-6 overflow-y-scroll scrollbar-hide rounded-xl bg-gradient-to-b from-white to-gray-50/50">
    <div class="flex flex-col space-y-6 px-4">
      <div
        v-for="chat in chats"
        :key="chat.message"
        class="flex w-full"
        :class="chat.human ? 'justify-end' : 'justify-start'"
      >
        <div v-if="!chat.human" class="flex items-end space-x-3">
          <img
            src="/images/logo.png"
            alt="Bot Avatar"
            class="h-10 w-10 rounded-full border-2 border-blue-200 object-cover shadow-md bg-white p-1"
          />
          <div class="max-w-[75%] px-4 py-3 rounded-2xl rounded-bl-md bg-white text-sm font-medium text-gray-800 shadow-md border border-gray-100 hover:shadow-lg transition-shadow duration-200">
            {{ chat.message }}
          </div>
        </div>

        <div v-else class="flex items-end space-x-3 flex-row-reverse">
          <img
            src="https://t4.ftcdn.net/jpg/06/08/55/73/360_F_608557356_ELcD2pwQO9pduTRL30umabzgJoQn5fnd.jpg"
            alt="User Avatar"
            class="h-10 w-10 rounded-full border-2 border-blue-300 object-cover shadow-md"
          />
          <div class="max-w-[75%] px-4 py-3 rounded-2xl rounded-br-md bg-gradient-to-r from-blue-500 to-blue-600 text-sm font-medium text-white shadow-md hover:shadow-lg transition-all duration-200 hover:from-blue-600 hover:to-blue-700">
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
