import { library } from '@fortawesome/fontawesome-svg-core'
import { faCog, faBug, faB } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { defineNuxtPlugin } from 'nuxt/app'

library.add(faCog)
library.add(faBug)

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.component('font-awesome-icon', FontAwesomeIcon)
})
