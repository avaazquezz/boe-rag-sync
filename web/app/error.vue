<script setup lang="ts">
import type { NuxtError } from "#app"

const props = defineProps<{ error: NuxtError }>()
const route = useRoute()
const en = route.path.startsWith("/en")
const notFound = props.error.statusCode === 404

useHead({ htmlAttrs: { lang: en ? "en" : "es" }, title: "Spanish Laws for RAG", meta: [{ name: "robots", content: "noindex" }] })
</script>

<template>
  <main class="error wrap">
    <p class="error__name"><NuxtLink :to="en ? '/en' : '/'">Spanish Laws for RAG</NuxtLink></p>
    <hr class="rule-double" />
    <h1 class="error__title">
      {{ notFound ? (en ? "This page is not in force." : "Esta página no está en vigor.") : (en ? "Something failed." : "Algo ha fallado.") }}
    </h1>
    <div class="error__stamp" aria-hidden="true"><RubberStamp text="No vigente" tone="red" /></div>
    <p><NuxtLink :to="en ? '/en' : '/'">{{ en ? "Back to the current edition" : "Volver a la edición vigente" }}</NuxtLink></p>
  </main>
</template>

<style scoped>
.error {
  display: grid;
  gap: var(--space-s);
  padding-block: var(--space-s) var(--space-l);
}

.error__name {
  font-size: var(--step-1);
  font-weight: 700;
  letter-spacing: 0.06em;
  font-variant-caps: all-small-caps;
}

.error__name a {
  text-decoration: none;
}

.error__title {
  margin-top: var(--space-m);
  font-size: var(--step-hero);
  max-width: 14ch;
}

.error__stamp {
  justify-self: end;
  font-size: clamp(1.8rem, 1.3rem + 2vw, 3rem);
}
</style>
