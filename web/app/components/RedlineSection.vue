<script setup lang="ts">
import gsap from "gsap"
import { ARTICLE_12_REFORM, RUNS } from "~/content/data"
import type { Copy } from "~/content/types"
import { MOTION } from "~/utils/motion"

defineProps<{ copy: Copy }>()
// Spaces at the edges of an edit stay outside it, so the pencil marks only the words.
const segments = ARTICLE_12_REFORM.segments.map((s) => {
  const [, lead = "", core = "", trail = ""] = /^(\s*)(.*?)(\s*)$/s.exec(s.text) ?? []
  return { ...s, lead, core, trail }
})
const root = ref<HTMLElement | null>(null)
const first = ref<HTMLElement | null>(null)

// The markup already holds the final state (struck, inserted, counted): without JS or with reduced
// motion that is what shows. With motion, the pencil redoes the edit once, when it comes into view.
useGsap(root, ({ motion }) => {
  if (!motion) return
  const counter = { value: 0 }
  if (first.value) first.value.textContent = "0"
  const tl = gsap.timeline({
    scrollTrigger: { trigger: ".redline__text", start: "top 70%", once: true },
    defaults: { ease: "brand-out" },
  })
  tl.fromTo(".redline__text del", { backgroundSize: "0% 2px" }, { backgroundSize: "100% 2px", duration: 0.9, stagger: 0.35, ease: "power1.inOut" })
    .fromTo(".redline__text ins", { opacity: 0, backgroundSize: "0% 2px" }, { opacity: 1, backgroundSize: "100% 2px", duration: 0.6, stagger: 0.25 }, "-=0.3")
    .from(".redline__ledger li", { opacity: 0, x: -8, duration: MOTION.dur.ui, stagger: MOTION.stagger.list }, "-=0.2")
    .from(".redline__unchanged", { opacity: 0, duration: MOTION.dur.ui }, "-=0.1")
    .to(
      counter,
      {
        value: RUNS.firstUpserts,
        duration: 1.2,
        ease: "power2.out",
        onUpdate: () => {
          if (first.value) first.value.textContent = String(Math.round(counter.value))
        },
      },
      "<",
    )
  return () => {
    if (first.value) first.value.textContent = String(RUNS.firstUpserts)
  }
})
</script>

<template>
  <section ref="root" class="redline wrap" aria-labelledby="redline-title">
    <hr class="rule-double" />
    <h2 id="redline-title" class="redline__title">{{ copy.redline.title }}</h2>
    <p class="redline__intro">{{ copy.redline.intro }}</p>

    <div class="redline__body">
      <figure class="redline__figure">
        <p class="redline__text" lang="es">
          <template v-for="(segment, i) in segments" :key="i">
            <template v-if="segment.op">{{ segment.lead }}</template>
            <del v-if="segment.op === 'del'">{{ segment.core }}</del>
            <ins v-else-if="segment.op === 'ins'">{{ segment.core }}</ins>
            <template v-else>{{ segment.text }}</template>
            <template v-if="segment.op">{{ segment.trail }}</template>
          </template>
        </p>
        <figcaption class="redline__caption">{{ copy.redline.caption }}</figcaption>
      </figure>

      <div class="redline__sync">
        <p class="redline__lead">{{ copy.redline.ledgerCaption }}</p>
        <ol class="redline__ledger mono">
          <li v-for="op in ARTICLE_12_REFORM.ops" :key="op.chunkId" :class="`redline__op--${op.op}`">
            <span class="redline__verb">{{ op.op }}</span>
            <span class="redline__id">{{ op.chunkId }}</span>
            <span v-if="'reason' in op" class="redline__reason">{{ op.reason }}</span>
          </li>
        </ol>
        <p class="redline__unchanged">{{ copy.redline.unchanged }}</p>

        <p class="redline__lead redline__lead--runs"><InlineText :text="copy.redline.runsCaption" /></p>
        <dl class="redline__runs">
          <div>
            <dt>{{ copy.redline.firstRun }}</dt>
            <dd ref="first" class="redline__count">{{ RUNS.firstUpserts }}</dd>
          </div>
          <div>
            <dt>{{ copy.redline.secondRun }}</dt>
            <dd class="redline__count">{{ RUNS.secondOps }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </section>
</template>

<style scoped>
.redline {
  padding-block: var(--space-l);
}

.redline__title {
  margin-top: var(--space-s);
  font-size: var(--step-3);
  max-width: 18ch;
}

.redline__intro {
  margin-top: var(--space-s);
  max-width: 52ch;
}

.redline__body {
  display: grid;
  gap: var(--space-m) var(--gap);
  margin-top: var(--space-m);
}

/* The two inks: red strikes out, blue writes in. Drawn as backgrounds so the pencil can sweep them
   line after line across a wrapped passage. */
.redline__text {
  font-size: var(--step-0);
  line-height: 1.6;
  hyphens: auto;
}

.redline__text del,
.redline__text ins {
  text-decoration: none;
  background-repeat: no-repeat;
  background-size: 100% 2px;
}

.redline__text del {
  color: color-mix(in oklab, var(--stamp-red) 70%, var(--ink));
  background-image: linear-gradient(var(--stamp-red), var(--stamp-red));
  background-position: 0 58%;
}

.redline__text ins {
  color: var(--pencil);
  background-image: linear-gradient(var(--pencil), var(--pencil));
  background-position: 0 100%;
}

.redline__caption {
  margin-top: var(--space-s);
  color: var(--ink-faded);
  font-size: var(--step--1);
  font-style: italic;
}

.redline__lead {
  font-size: var(--step--1);
  color: var(--ink-faded);
  max-width: 40ch;
}

.redline__ledger {
  display: grid;
  gap: 0.35rem;
  margin-top: 1rem;
  padding: 1rem 0;
  border-block: 1px solid var(--rule);
  list-style: none;
  font-size: var(--step--2);
}

.redline__ledger li {
  display: flex;
  flex-wrap: wrap;
  gap: 0 0.9em;
}

.redline__verb {
  min-width: 6ch;
  font-weight: 700;
}

.redline__op--upsert .redline__verb {
  color: var(--pencil);
}

.redline__op--delete {
  color: var(--stamp-red);
}

.redline__reason::before {
  content: "· ";
}

.redline__unchanged {
  margin-top: 0.75rem;
  font-size: var(--step--1);
}

.redline__lead--runs {
  margin-top: var(--space-m);
}

.redline__runs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--gap);
  margin-top: 1rem;
}

.redline__runs > div {
  display: flex;
  flex-direction: column-reverse;
  justify-content: flex-end;
  gap: 0.25rem;
}

.redline__runs dt {
  color: var(--ink-faded);
  font-size: var(--step--1);
  line-height: 1.35;
}

.redline__count {
  font-size: var(--step-3);
  line-height: 1;
  font-variant-numeric: lining-nums tabular-nums;
}

@media (min-width: 1024px) {
  .redline {
    display: grid;
    grid-template-columns: repeat(12, minmax(0, 1fr));
    column-gap: var(--gap);
  }

  .redline > * {
    grid-column: 1 / -1;
  }

  .redline__intro {
    grid-column: 1 / span 6;
  }

  .redline__body {
    grid-template-columns: subgrid;
    align-items: start;
  }

  .redline__figure {
    grid-column: 1 / span 7;
  }

  .redline__text {
    font-size: var(--step-1);
  }

  .redline__sync {
    grid-column: 9 / -1;
  }
}
</style>
