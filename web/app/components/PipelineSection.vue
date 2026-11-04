<script setup lang="ts">
import { ScrollTrigger } from "gsap/ScrollTrigger"
import type { Copy } from "~/content/types"

defineProps<{ copy: Copy }>()
const root = ref<HTMLElement | null>(null)
const active = ref<0 | 1 | 2 | 3>(0)
const ordinals = ["1.º", "2.º", "3.º", "4.º"] as const

// Desktop: the figure stays in view while the four steps scroll past it, text and figure in
// lockstep. Mobile: each step carries its own still figure, nothing is pinned.
useGsap(root, ({ desktop }) => {
  if (!desktop) return
  root.value?.querySelectorAll<HTMLElement>("[data-step]").forEach((el, i) => {
    ScrollTrigger.create({
      trigger: el,
      start: "top 55%",
      end: "bottom 55%",
      onToggle: (self) => {
        if (self.isActive) active.value = i as 0 | 1 | 2 | 3
      },
    })
  })
})
</script>

<template>
  <section ref="root" class="pipeline" aria-labelledby="pipeline-title">
    <div class="wrap pipeline__head">
      <hr class="rule-double" />
      <h2 id="pipeline-title" class="pipeline__title">{{ copy.pipeline.title }}</h2>
      <p class="pipeline__intro">{{ copy.pipeline.intro }}</p>
      <blockquote class="pipeline__epigraph">
        <p lang="es">«{{ copy.pipeline.epigraph.quote }}»</p>
        <p v-if="copy.pipeline.epigraph.translation" class="pipeline__translation">
          {{ copy.pipeline.epigraph.translation }}
        </p>
        <footer>
          <cite>{{ copy.pipeline.epigraph.source }}</cite>
        </footer>
      </blockquote>
    </div>

    <div class="wrap pipeline__body">
      <ol class="pipeline__steps">
        <li v-for="(step, i) in copy.pipeline.steps" :key="step.head" class="pipeline__step" :data-step="i">
          <p class="pipeline__text">
            <span class="run-in">{{ ordinals[i] }} {{ step.head }}</span>{{ " " }}<InlineText :text="step.body" />
          </p>
          <div class="pipeline__still" aria-hidden="true">
            <PipelineFigure :copy="copy" :step="i as 0 | 1 | 2 | 3" still />
          </div>
        </li>
      </ol>
      <div class="pipeline__stage" aria-hidden="true">
        <PipelineFigure :copy="copy" :step="active" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.pipeline {
  padding-block: var(--space-l);
}

.pipeline__title {
  margin-top: var(--space-s);
  font-size: var(--step-3);
  max-width: 18ch;
}

.pipeline__intro {
  margin-top: var(--space-s);
  max-width: 52ch;
}

.pipeline__epigraph {
  margin-top: var(--space-m);
  padding-left: 1.25rem;
  border-left: 1px solid var(--ink);
  max-width: 36rem;
}

.pipeline__epigraph p:first-child {
  font-size: var(--step-2);
  font-style: italic;
  line-height: 1.2;
  hanging-punctuation: first;
}

.pipeline__translation {
  margin-top: 0.4rem;
  color: var(--ink-faded);
}

.pipeline__epigraph footer {
  margin-top: 0.75rem;
  color: var(--ink-faded);
  font-size: var(--step--1);
}

.pipeline__epigraph cite {
  font-style: normal;
}

.pipeline__body {
  margin-top: var(--space-m);
}

.pipeline__steps {
  display: grid;
  gap: var(--space-m);
  padding: 0;
  list-style: none;
}

.pipeline__text {
  max-width: 44ch;
}

.pipeline__still {
  margin-top: var(--space-s);
}

.pipeline__stage {
  display: none;
}

@media (min-width: 1024px) {
  .pipeline__body {
    display: grid;
    grid-template-columns: repeat(12, minmax(0, 1fr));
    column-gap: var(--gap);
  }

  .pipeline__steps {
    grid-column: 1 / span 4;
    gap: 0;
  }

  .pipeline__step {
    display: flex;
    align-items: center;
    min-height: 62vh;
  }

  .pipeline__still {
    display: none;
  }

  .pipeline__stage {
    display: block;
    grid-column: 6 / -1;
    position: sticky;
    top: 12vh;
    height: 76vh;
    align-self: start;
  }
}
</style>
