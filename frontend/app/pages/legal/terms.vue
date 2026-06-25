<script setup lang="ts">
definePageMeta({
  layout: 'legal',
  title: 'Пользовательское соглашение',
  subtitle: 'Условия использования платформы gcloude.',
});
</script>

<template>
  <div class="grid gap-4 text-sm leading-6 text-slate-600">
    <h1 class="text-2xl font-semibold text-slate-900">Пользовательское соглашение</h1>
    <LegalEntityInfo compact :show-title="false" />
    <p>
      Настоящее соглашение регулирует доступ к платформе gcloude: кабинету, API, деплою
      приложений из Git и связанным сервисам.
    </p>

    <section class="grid gap-2">
      <h2 class="text-base font-semibold text-slate-900">1. Регистрация и аккаунт</h2>
      <p>
        Пользователь указывает достоверный email и пароль, принимает политику конфиденциальности
        и согласие на обработку персональных данных. Ответственность за сохранность пароля лежит на пользователе.
      </p>
    </section>

    <section class="grid gap-2">
      <h2 class="text-base font-semibold text-slate-900">2. Деплой приложений</h2>
      <p>
        Пользователь самостоятельно загружает код в Git-репозиторий и запускает деплой.
        Запрещено размещать вредоносное ПО, нарушать законодательство РФ и права третьих лиц.
      </p>
    </section>

    <section class="grid gap-2">
      <h2 class="text-base font-semibold text-slate-900">3. Домены и SSL</h2>
      <p>
        Платформа выдаёт поддомены вида <code class="rounded bg-slate-100 px-1">&lt;slug&gt;.apps.&lt;домен&gt;</code>
        и может автоматически запрашивать сертификаты Let's Encrypt при корректной DNS-настройке.
      </p>
    </section>

    <section class="grid gap-2">
      <h2 class="text-base font-semibold text-slate-900">4. Ограничение ответственности</h2>
      <p>
        Платформа предоставляется «как есть» в рамках учебного/пилотного проекта.
        Оператор не несёт ответственности за простои, потерю данных в пользовательских контейнерах
        без резервного копирования со стороны клиента.
      </p>
    </section>

    <LegalFooterLinks centered />
  </div>
</template>
