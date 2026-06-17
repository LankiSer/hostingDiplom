<script setup lang="ts">
import type { AppInputProps } from './interface';

defineProps<AppInputProps>();
const emit = defineEmits<{ 'update:modelValue': [value: string] }>();

function handleInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value);
}
</script>

<template>
  <label class="grid gap-1.5">
    <span class="text-sm font-medium text-slate-700">{{ label }}</span>
    <input
      :type="type ?? 'text'"
      :value="modelValue"
      :placeholder="placeholder"
      class="rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
      @input="handleInput"
    >
  </label>
</template>
