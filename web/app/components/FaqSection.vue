<script setup lang="ts">
import type { Copy } from "~/content/types"

defineProps<{ copy: Copy }>()
</script>

<template>
  <section class="faq wrap" aria-labelledby="faq-title">
    <p class="faq__price">
      <span class="run-in">{{ copy.price.head }}</span>
      {{ copy.price.body }}
    </p>
    <h2 id="faq-title" class="faq__title">{{ copy.faq.title }}</h2>
    <div class="faq__list">
      <details v-for="item in copy.faq.items" :key="item.q" class="faq__item">
        <summary>{{ item.q }}</summary>
        <p><InlineText :text="item.a" /></p>
      </details>
    </div>
  </section>
</template>

<style scoped>
.faq {
  padding-block: 0 var(--space-l);
}

.faq__price {
  max-width: 60ch;
  padding: var(--space-s) 0;
  border-block: 1px solid var(--rule);
  font-size: var(--step-1);
  line-height: 1.45;
}

.faq__title {
  margin-top: var(--space-m);
  font-size: var(--step-2);
}

.faq__list {
  margin-top: var(--space-s);
  max-width: 50rem;
  border-top: 1px solid var(--ink);
}

.faq__item {
  border-bottom: 1px solid var(--rule);
}

.faq__item summary {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0;
  cursor: pointer;
  list-style: none;
  font-size: var(--step-1);
}

.faq__item summary::-webkit-details-marker {
  display: none;
}

.faq__item summary::after {
  content: "+";
  flex: none;
  color: var(--pencil);
  font-family: var(--mono);
  transition: rotate var(--dur-micro) var(--ease-brand-out);
}

.faq__item[open] summary::after {
  rotate: 45deg;
}

.faq__item p {
  padding-bottom: 1.1rem;
  max-width: 60ch;
}
</style>
