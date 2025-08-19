import type { Config } from 'tailwindcss'
import colors from 'tailwindcss/colors'
import scrollbarHide from 'tailwind-scrollbar-hide'

export default <Partial<Config>>{
    theme: {
    extend: {
      colors: {
        background: "#EBF5EE",
        passive_background: "#F5F5F5",
        custom_red: "#FF2D55",
        accent: '#B7C4B8',
        primary: '#696EB3', 
        dark_primary: '#6155F5',
        black: '#020402'
      },
      fontFamily: {
        'open-sans': ['"Open Sans"', 'sans-serif'],
        canela: ['Canela', 'serif'],
      },
    }
  },
  plugins: [scrollbarHide]
}
