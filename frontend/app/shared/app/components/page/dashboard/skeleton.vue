<script setup lang="ts">
import AppCard from '../../ui/card/component.vue';
import AppSkeletonBox from '../../ui/skeleton/box/component.vue';
</script>

<template>
  <div class="app-page-grid">
    <AppCard>
      <div class="grid gap-6">
        <div class="grid gap-3">
          <AppSkeletonBox class-name="h-7 w-32" />
          <AppSkeletonBox class-name="h-4 w-full max-w-2xl" />
          <AppSkeletonBox class-name="h-4 w-4/5" />
        </div>

        <div class="app-page-columns">
          <AppCard v-for="card in 3" :key="card">
            <div class="grid gap-3">
              <AppSkeletonBox class-name="h-6 w-40" />
              <AppSkeletonBox class-name="h-4 w-full" />
              <AppSkeletonBox class-name="h-4 w-3/4" />
            </div>
          </AppCard>
        </div>
      </div>
    </AppCard>
  </div>
</template>
