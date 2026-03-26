<script setup lang="ts">
import AppCard from '../../../../shared/app/components/ui/card/component.vue';
import AppSkeletonBox from '../../../../shared/app/components/ui/skeleton/box/component.vue';
</script>

<template>
  <AppCard>
    <div class="grid gap-6">
      <div class="grid gap-3">
        <AppSkeletonBox class-name="h-7 w-40" />
        <AppSkeletonBox class-name="h-4 w-full max-w-2xl" />
      </div>

      <div class="app-page-grid">
        <AppCard v-for="card in 3" :key="card">
          <div class="grid gap-3">
            <AppSkeletonBox class-name="h-5 w-4/5" />
            <AppSkeletonBox class-name="h-4 w-full" />
          </div>
        </AppCard>
      </div>
    </div>
  </AppCard>
</template>
