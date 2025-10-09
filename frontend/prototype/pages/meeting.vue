<script setup lang="ts">
import Memory_view_grid from '../components/memory_view_grid.vue';
import Side_bar from '../components/side_bar.vue';

</script>

<template>
  <div class="flex flex-col w-screen h-screen overflow-hidden bg-gray-50">
    <!-- Header -->
    <div class="flex justify-between items-center py-2 px-6 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm flex-shrink-0">
      <button
        class="h-11 rounded-lg bg-gradient-to-r from-red-500 to-red-600 px-6 font-open-sans font-semibold text-white hover:from-red-600 hover:to-red-700 transform hover:scale-105 transition-all duration-200 shadow-md hover:shadow-red-500/20"
      >
        End Meeting
      </button>

      <div class="font-canela text-[24px] text-gray-800 flex items-center">
        <img src="/images/logo.png" class="h-[36px] mr-3 drop-shadow-sm" />
        <div class="mt-1 bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
          Sravah Daily Standup
        </div>
      </div>

      <div class="h-11 rounded-xl bg-gradient-to-r from-red-500 to-red-600 px-6 font-open-sans font-medium text-white invisible">
        End Meeting
      </div>
    </div>

    <!-- Body -->
    <div class="flex-1 flex p-3 space-x-3 overflow-hidden min-h-0">
      <div class="w-[30%] min-w-[300px] max-w-[500px] h-full min-h-0">
        <Side_bar />
      </div>
      <div class="flex-1 h-full min-h-0 overflow-hidden">
        <Memory_view_grid />
      </div>
    </div>
  </div>
</template>
