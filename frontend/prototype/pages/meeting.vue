<script setup lang="ts">
import Side_bar from '../components/side_bar.vue';

</script>

<template>
    <div class="w-screen h-screen bg-passive_background flex flex-col overflow-x-hidden overscroll-x-none touch-pan-y">
        <div class="w-full h-14 bg-white shadow-md flex justify-between items-center">
            <button class="
                h-10 rounded-md bg-custom_red px-5 ml-2
                font-open-sans font-medium text-white
            ">
                End Meeting
            </button>
            <div class="
                font-canela leading-none text-[22px] text-primary flex items-center
            ">
                <img src="/images/logo.png" class="h-[32px] mr-2"></img>
                <div class="mt-1">Sravah Daily Standup</div>
            </div>
            <div class="h-10 rounded-md bg-custom_red px-5 mr-2 font-open-sans font-medium text-white invisible">End Meeting</div>
        </div>
        <div class="h-full w-full">
            <Side_bar></Side_bar>
        </div>
    </div>
</template>