<script setup lang="ts">
import AppSkeletonBox from '../../../../../shared/app/components/ui/skeleton/box/component.vue';
</script>

<template>
  <div class="grid gap-6">
    <AppSkeletonBox class-name="h-7 w-40" />
    <div class="grid gap-3">
      <AppSkeletonBox class-name="h-10 w-64" />
      <AppSkeletonBox class-name="h-4 w-full" />
      <AppSkeletonBox class-name="h-4 w-5/6" />
    </div>
    <div class="grid gap-2">
      <AppSkeletonBox class-name="h-4 w-20" />
      <AppSkeletonBox class-name="h-12 w-full" />
    </div>
    <div class="grid gap-2">
      <AppSkeletonBox class-name="h-4 w-28" />
      <AppSkeletonBox class-name="h-12 w-full" />
    </div>
    <AppSkeletonBox class-name="h-12 w-full rounded-2xl" />
  </div>
</template>
