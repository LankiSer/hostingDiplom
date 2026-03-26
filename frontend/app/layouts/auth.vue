<template>
  <main class="grid min-h-screen place-items-center px-4 py-8">
    <div class="w-full max-w-md">
      <div class="mb-8 text-center">
        <div class="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500 text-sm font-bold text-white">G</div>
        <h1 class="text-xl font-bold text-white">gcloude</h1>
        <p class="mt-1 text-sm text-slate-500">Платформа микросервисного хостинга</p>
      </div>
      <div class="rounded-2xl border border-white/8 bg-slate-900/60 p-6">
        <slot />
      </div>
    </div>
  </main>
</template>
