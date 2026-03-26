import type { Config } from 'tailwindcss';

export default <Partial<Config>>{
  theme: {
    extend: {
      colors: {
        brand: {
          400: '#38bdf8',
          500: '#0ea5e9'
        }
      }
    }
  }
};
