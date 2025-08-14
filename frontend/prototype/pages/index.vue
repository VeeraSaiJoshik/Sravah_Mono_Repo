<template>
  <client-only>
    <div class="relative w-screen h-screen overflow-hidden bg-gray-50">
      <img 
        src="/images/background.png" 
        class="absolute inset-0 w-full h-full object-cover z-0" 
      />
      
      <div class="relative z-20 w-screen h-screen flex flex-col items-center justify-center overflow-scroll space-y-20">
            <div class="flex flex-col items-center">
                <img src="/images/logo.png" class="lg:h-32 mb-3 transition-all ease-in-out duration-300 lg:hover:h-36 cursor-pointer "/>
                <div class="
                    font-canela font-primary text-7xl
                    bg-gradient-to-tr from-primary to-primary/80
                    bg-clip-text text-transparent
                ">
                    Stravah.AI
                </div>
                <div class="font-open-sans text-black/30 font-medium">
                    Where Conversations Become Actions
                </div>
            </div>
            <button class="
                py-3 px-5 bg-primary/90 border-4 border-primary rounded-md
                hover:shadow-2xl
                transition-all ease-in-out duration-300
                font-open-sans font-semibold text-lg text-gray-50
            ">
                Check It Out!
            </button>
      </div>
    </div>
  </client-only>
</template>