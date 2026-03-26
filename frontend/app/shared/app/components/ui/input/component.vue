<script setup lang="ts">
import type { AppInputProps } from './interface';

defineProps<AppInputProps>();
const emit = defineEmits<{ 'update:modelValue': [value: string] }>();

function handleInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value);
}
</script>

<template>
  <label class="grid gap-2">
    <span class="text-sm text-slate-300">{{ label }}</span>
    <input
      :value="modelValue"
      :placeholder="placeholder"
      class="rounded-xl border border-white/10 bg-slate-950/70 px-3.5 py-2.5 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-sky-400/40"
      @input="handleInput"
    >
  </label>
</template>
