<script setup lang="ts">
// Renders copy text, turning `backticked` spans into <code> without v-html.
const props = defineProps<{ text: string }>()
const parts = computed(() => props.text.split("`").map((value, i) => ({ value, code: i % 2 === 1 })))
</script>

<template>
  <template v-for="(part, i) in parts" :key="i">
    <code v-if="part.code">{{ part.value }}</code>
    <template v-else>{{ part.value }}</template>
  </template>
</template>
