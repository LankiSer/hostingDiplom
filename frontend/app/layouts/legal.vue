<template>
  <main class="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_20%_0%,rgba(14,165,233,0.12),transparent_35%),radial-gradient(circle_at_80%_100%,rgba(245,158,11,0.1),transparent_30%),#f8fafc] px-4 py-10">
    <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(15,23,42,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(15,23,42,0.03)_1px,transparent_1px)] bg-[size:32px_32px]" />
    <div class="relative mx-auto w-full max-w-2xl">
      <div class="mb-8 text-center">
        <NuxtLink to="/" class="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#0284c7_0%,#0369a1_100%)] text-xl font-bold text-white shadow-[0_12px_30px_-12px_rgba(2,132,199,0.9)]">
          G
        </NuxtLink>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900">gcloude</h1>
        <p class="mt-1 text-sm text-slate-500">Деплой приложений из Git за минуты</p>
      </div>
      <div class="rounded-2xl border border-slate-200/80 bg-white/95 p-6 shadow-[0_20px_50px_-30px_rgba(15,23,42,0.35)] backdrop-blur-sm sm:p-8">
        <slot />
      </div>
      <div class="mt-6">
        <LegalFooter centered />
      </div>
    </div>
  </main>
</template>
