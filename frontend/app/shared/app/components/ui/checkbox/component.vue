<script setup lang="ts">
import type { AppCheckboxProps } from './interface';

defineProps<AppCheckboxProps>();
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>();

function handleChange(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).checked);
}
</script>

<template>
  <label class="flex items-start gap-3 text-sm text-slate-300">
    <input
      :checked="modelValue"
      class="mt-1 h-4 w-4 rounded border border-white/20 bg-slate-950/70"
      type="checkbox"
      @change="handleChange"
    >
    <span class="leading-5">{{ label }}</span>
  </label>
</template>
