<script setup lang="ts">
definePageMeta({
  layout: 'legal',
  title: 'Политика cookie',
  subtitle: 'Какие файлы cookie использует платформа и зачем.',
});
</script>

<template>
  <div class="grid gap-4 text-sm leading-6 text-slate-600">
    <h1 class="text-2xl font-semibold text-slate-900">Политика использования cookie</h1>
    <LegalEntityInfo compact :show-title="false" />
    <p>
      Cookie — небольшие текстовые файлы, которые браузер сохраняет на устройстве пользователя.
      Платформа gcloude использует их для работы кабинета и сохранения ваших настроек.
    </p>

    <section class="grid gap-2">
      <h2 class="text-base font-semibold text-slate-900">Обязательные cookie</h2>
      <ul class="list-disc space-y-1 pl-5">
        <li><strong>platform_session</strong> — сессия входа в кабинет (email, роль, токен).</li>
        <li><strong>gcloude_cookie_consent</strong> — ваш выбор по cookie-баннеру.</li>
      </ul>
      <p>Без них вход и навигация по защищённым разделам невозможны.</p>
    </section>

    <section class="grid gap-2">
      <h2 class="text-base font-semibold text-slate-900">Аналитические cookie</h2>
      <p>
        Используются только если вы нажали «Принять все». В текущей версии платформы
        аналитика минимальна и не передаётся сторонним рекламным сетям.
      </p>
    </section>

    <section class="grid gap-2">
      <h2 class="text-base font-semibold text-slate-900">Как управлять</h2>
      <p>
        При первом визите отображается баннер с выбором «Только необходимые» или «Принять все».
        Cookie можно удалить в настройках браузера — после этого потребуется войти снова.
      </p>
    </section>

    <LegalFooterLinks centered />
  </div>
</template>
