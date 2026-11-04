<script setup lang="ts">
import type { Copy } from "~/content/types"

const props = defineProps<{ copy: Copy }>()
const { long, iso } = useEditionDate(props.copy.dateLocale)
const home = computed(() => (props.copy.lang === "es" ? "/" : "/en"))
</script>

<template>
  <header class="masthead wrap">
    <div class="masthead__row">
      <NuxtLink :to="home" class="masthead__name" :aria-label="copy.masthead.home">Spanish Laws for RAG</NuxtLink>
      <NuxtLink
        :to="copy.masthead.switchHref"
        class="masthead__lang"
        :hreflang="copy.lang === 'es' ? 'en' : 'es'"
        :lang="copy.lang === 'es' ? 'en' : 'es'"
        :aria-label="copy.masthead.switchLabel"
        >{{ copy.masthead.switchText }}</NuxtLink
      >
    </div>
    <p class="masthead__edition">
      <span>{{ copy.masthead.edition }}</span>
      <time :datetime="iso">{{ long }}</time>
      <span>{{ copy.masthead.inForce }}</span>
    </p>
    <hr class="rule-double" />
  </header>
</template>

<style scoped>
.masthead {
  padding-top: clamp(1rem, 0.7rem + 1vw, 1.6rem);
}

.masthead__row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
}

.masthead__name {
  font-size: var(--step-1);
  font-weight: 700;
  letter-spacing: 0.06em;
  font-variant-caps: all-small-caps;
  text-decoration: none;
}

.masthead__lang {
  font-family: var(--mono);
  font-stretch: 87.5%;
  font-size: var(--step--1);
}

.masthead__edition {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.25rem 1.5rem;
  margin-top: 0.5rem;
  padding-bottom: 0.45rem;
  color: var(--ink-faded);
  font-size: var(--step--1);
  font-variant-numeric: oldstyle-nums;
}

.masthead__edition time {
  display: inline-block;
}

.masthead__edition time::first-letter {
  text-transform: uppercase;
}

@media (max-width: 40rem) {
  .masthead__edition span:last-child {
    display: none;
  }
}
</style>
