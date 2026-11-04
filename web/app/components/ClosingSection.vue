<script setup lang="ts">
import gsap from "gsap"
import { APIFY_URL } from "~/content/data"
import type { Copy } from "~/content/types"

const props = defineProps<{ copy: Copy }>()
const { short } = useEditionDate(props.copy.dateLocale)
const root = ref<HTMLElement | null>(null)

// The last stamp of the page lands when the closing comes into view.
useGsap(root, ({ motion }) => {
  if (!motion) return
  gsap.fromTo(
    ".closing__stamp",
    { autoAlpha: 0, scale: 1.7, rotate: -14 },
    {
      autoAlpha: 1,
      scale: 1,
      rotate: 0,
      duration: 0.24,
      ease: "power4.in",
      scrollTrigger: { trigger: root.value, start: "top 60%", once: true },
    },
  )
})
</script>

<template>
  <section ref="root" class="closing wrap" aria-labelledby="closing-title">
    <hr class="rule-double" />
    <div class="closing__body">
      <h2 id="closing-title" class="closing__title">{{ copy.closing.title }}</h2>
      <p class="closing__action"><a class="button" :href="APIFY_URL" target="_blank" rel="noopener">{{ copy.closing.cta }}</a></p>
      <div class="closing__stamp" aria-hidden="true">
        <RubberStamp :text="copy.hero.stamp" :date="short" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.closing {
  padding-block: var(--space-m) var(--space-l);
}

.closing__body {
  position: relative;
  display: grid;
  gap: var(--space-s);
  padding-top: var(--space-m);
}

.closing__title {
  font-size: var(--step-hero);
  line-height: 1;
  letter-spacing: -0.02em;
  max-width: 17ch;
}

.closing__stamp {
  justify-self: end;
  margin-top: calc(var(--space-s) * -1);
  font-size: clamp(1.8rem, 1.3rem + 2vw, 3rem);
}

@media (min-width: 1024px) {
  .closing__stamp {
    position: absolute;
    right: 4%;
    bottom: 10%;
    margin: 0;
  }
}
</style>
