<script setup lang="ts">
import gsap from "gsap"
import type { Copy } from "~/content/types"
import { MOTION } from "~/utils/motion"

defineProps<{ copy: Copy }>()
const root = ref<HTMLElement | null>(null)

// The columns are inked top to bottom, in reading order, once.
useGsap(root, ({ motion }) => {
  if (!motion) return
  gsap.fromTo(
    ".build__item",
    { clipPath: "inset(0 0 100% 0)" },
    {
      clipPath: "inset(0 0 0% 0)",
      duration: MOTION.dur.reveal,
      stagger: MOTION.stagger.text * 2,
      ease: "brand-out",
      scrollTrigger: { trigger: ".build__columns", start: "top 75%", once: true },
    },
  )
})
</script>

<template>
  <section ref="root" class="build wrap" aria-labelledby="build-title">
    <hr class="rule-double" />
    <h2 id="build-title" class="build__title">{{ copy.build.title }}</h2>
    <div class="build__columns">
      <p v-for="item in copy.build.items" :key="item.head" class="build__item">
        <span class="run-in">{{ item.head }}</span>
        {{ item.body }}
      </p>
    </div>
    <p class="build__links">
      <template v-for="(link, i) in copy.build.links" :key="link.href">
        <a :href="link.href" target="_blank" rel="noopener">{{ link.text }}</a>
        <span v-if="i < copy.build.links.length - 1" aria-hidden="true"> · </span>
      </template>
    </p>
  </section>
</template>

<style scoped>
.build {
  padding-block: var(--space-m) var(--space-l);
}

.build__title {
  margin-top: var(--space-s);
  font-size: var(--step-3);
}

/* Gazette columns divided by a hairline rule. */
.build__columns {
  margin-top: var(--space-m);
  column-width: 22rem;
  column-gap: calc(var(--gap) * 2);
  column-rule: 1px solid var(--rule);
}

.build__item {
  break-inside: avoid;
  margin-bottom: 1.1em;
  hyphens: auto;
}

.build__links {
  margin-top: var(--space-s);
}
</style>
