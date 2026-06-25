import tailwindcss from '@tailwindcss/vite';

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['./app/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL ?? '',
      legalCompanyName: process.env.NUXT_PUBLIC_LEGAL_COMPANY_NAME ?? '',
      legalInn: process.env.NUXT_PUBLIC_LEGAL_INN ?? '',
      legalOgrn: process.env.NUXT_PUBLIC_LEGAL_OGRN ?? '',
      legalKpp: process.env.NUXT_PUBLIC_LEGAL_KPP ?? '',
      legalAddress: process.env.NUXT_PUBLIC_LEGAL_ADDRESS ?? '',
      legalEmail: process.env.NUXT_PUBLIC_LEGAL_EMAIL ?? '',
      legalPhone: process.env.NUXT_PUBLIC_LEGAL_PHONE ?? '',
    }
  },
  vite: {
    plugins: [tailwindcss()]
  }
})
