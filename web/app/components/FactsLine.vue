<script setup lang="ts">
import type { Copy } from "~/content/types"

defineProps<{ copy: Copy }>()
</script>

<template>
  <section class="facts wrap" :aria-label="copy.facts.label">
    <ul class="facts__list">
      <li v-for="item in copy.facts.items" :key="item">{{ item }}</li>
    </ul>
  </section>
</template>

<style scoped>
.facts__list {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.35rem 2rem;
  padding: 0.9rem 0;
  border-block: 1px solid var(--rule);
  list-style: none;
  color: var(--ink-faded);
  font-size: var(--step--1);
  font-variant-caps: all-small-caps;
  letter-spacing: 0.04em;
}

@media (max-width: 40rem) {
  .facts__list {
    flex-direction: column;
  }
}
</style>
