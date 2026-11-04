<script setup lang="ts">
import { CURL, RECORD } from "~/content/data"
import type { Copy } from "~/content/types"

defineProps<{ copy: Copy }>()
</script>

<template>
  <section class="usage wrap" aria-labelledby="usage-title">
    <hr class="rule-double" />
    <h2 id="usage-title" class="usage__title">{{ copy.usage.title }}</h2>
    <p class="usage__intro">{{ copy.usage.intro }}</p>
    <div class="usage__blocks">
      <CodeBlock :code="CURL" :caption="copy.usage.curlCaption" :copy-label="copy.usage.copy" :copied-label="copy.usage.copied" />
      <CodeBlock :code="RECORD" :caption="copy.usage.recordCaption" :copy-label="copy.usage.copy" :copied-label="copy.usage.copied" />
    </div>
    <p class="usage__loader"><a :href="copy.usage.loaderHref" target="_blank" rel="noopener">{{ copy.usage.loader }}</a></p>
  </section>
</template>

<style scoped>
.usage {
  padding-block: var(--space-l) var(--space-m);
}

.usage__title {
  margin-top: var(--space-s);
  font-size: var(--step-3);
}

.usage__intro {
  margin-top: var(--space-s);
  max-width: 52ch;
}

.usage__blocks {
  display: grid;
  gap: var(--space-s) var(--gap);
  margin-top: var(--space-m);
}

.usage__loader {
  margin-top: var(--space-s);
}

.usage__blocks {
  max-width: 60rem;
}
</style>
