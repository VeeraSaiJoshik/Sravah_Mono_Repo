import type { Config } from 'tailwindcss'
import colors from 'tailwindcss/colors'

export default <Partial<Config>>{
    theme: {
    extend: {
      colors: {
        background: "#EBF5EE",
        accent: '#B7C4B8',
        primary: '#6C63EE', 
        black: '#020402'
      },
      fontFamily: {
        'open-sans': ['"Open Sans"', 'sans-serif'],
        canela: ['Canela', 'serif'],
      },
    }
  }
}
