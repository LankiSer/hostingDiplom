<script setup lang="ts">
import type { AppCheckboxProps } from './interface';

defineProps<AppCheckboxProps>();
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>();

function handleChange(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).checked);
}
</script>

<template>
  <label class="flex items-start gap-3 text-sm text-slate-600">
    <input
      :checked="modelValue"
      class="mt-0.5 h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500"
      type="checkbox"
      @change="handleChange"
    >
    <span class="leading-5">
      <slot>{{ label }}</slot>
    </span>
  </label>
</template>
