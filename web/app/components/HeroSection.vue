<script setup lang="ts">
import gsap from "gsap"
import { APIFY_URL, ARTICLE_4, GITHUB_URL } from "~/content/data"
import type { Copy } from "~/content/types"
import { MOTION } from "~/utils/motion"

const props = defineProps<{ copy: Copy }>()
const { short } = useEditionDate(props.copy.dateLocale)
const root = ref<HTMLElement | null>(null)

// The headline is the LCP element and never moves; the pencil works around it.
useGsap(root, ({ motion }) => {
  if (!motion) return
  const tl = gsap.timeline({ delay: 0.25, defaults: { ease: "brand-out" } })
  tl.from(".hero__sheet", { y: 24, autoAlpha: 0, duration: MOTION.dur.reveal })
    .fromTo(
      ".hero__note",
      { clipPath: "inset(0 100% 0 0)", autoAlpha: 1 },
      { clipPath: "inset(0 0% 0 0)", duration: MOTION.dur.ui, stagger: 0.18, ease: "power2.inOut" },
      "-=0.45",
    )
    .fromTo(".hero__bracket path", { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.6, ease: "power1.inOut" }, "<0.1")
    .fromTo(
      ".hero__stamp",
      { autoAlpha: 0, scale: 1.7, rotate: -14 },
      { autoAlpha: 1, scale: 1, rotate: 0, duration: 0.24, ease: "power4.in" },
      "-=0.1",
    )
    .to(".hero__sheet", { y: 2, duration: 0.08, yoyo: true, repeat: 1, ease: "power1.out" })
})
</script>

<template>
  <section ref="root" class="hero wrap" aria-labelledby="hero-title">
    <h1 id="hero-title" class="hero__title">{{ copy.hero.title }}</h1>

    <div class="hero__intro">
      <p class="hero__lede">{{ copy.hero.lede }}</p>
      <p class="hero__actions">
        <a class="button" :href="APIFY_URL" target="_blank" rel="noopener">{{ copy.hero.cta }}</a>
        <a class="hero__secondary" :href="GITHUB_URL" target="_blank" rel="noopener">{{ copy.hero.secondary }}</a>
      </p>
    </div>

    <figure class="hero__figure">
      <p class="hero__note hero__note--path mono">
        <span class="hero__label">{{ copy.hero.notePath }}</span>
        <template v-for="(step, i) in ARTICLE_4.path" :key="step">
          <span class="hero__crumb">{{ step }}</span>
          <span v-if="i < ARTICLE_4.path.length - 1" aria-hidden="true"> › </span>
        </template>
      </p>

      <div class="hero__sheet" lang="es">
        <svg class="hero__bracket" viewBox="0 0 16 400" preserveAspectRatio="none" aria-hidden="true" focusable="false">
          <path d="M14 2C6 3 4 6 4 14v372c0 8 2 11 10 12" pathLength="1" />
        </svg>
        <p class="hero__heading">{{ ARTICLE_4.heading }}</p>
        <p>{{ ARTICLE_4.lead }}</p>
        <ul class="hero__items">
          <li v-for="item in ARTICLE_4.items" :key="item">{{ item }}</li>
        </ul>
        <p class="hero__fade" aria-hidden="true">{{ ARTICLE_4.next }}</p>
        <div class="hero__stamp">
          <RubberStamp :text="copy.hero.stamp" :date="short" />
        </div>
      </div>

      <dl class="hero__meta mono">
        <div class="hero__note">
          <dt class="visually-hidden">chunk_id</dt>
          <dd class="hero__id">{{ ARTICLE_4.chunkId }}</dd>
          <dd v-for="line in copy.hero.noteChunk" :key="line">{{ line }}</dd>
        </div>
        <div class="hero__note">
          <dt class="visually-hidden">in_force_from</dt>
          <dd v-for="line in copy.hero.noteVersion" :key="line">{{ line }}</dd>
        </div>
      </dl>

      <figcaption class="hero__caption">{{ copy.hero.caption }}</figcaption>
    </figure>
  </section>
</template>

<style scoped>
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--space-s) var(--gap);
  padding-block: var(--space-s) var(--space-l);
}

.hero__title {
  font-size: var(--step-hero);
  font-weight: 500;
  line-height: 0.98;
  letter-spacing: -0.022em;
  max-width: 22ch;
}

.hero__lede {
  font-size: var(--step-1);
  line-height: 1.4;
  max-width: 34ch;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem 1.5rem;
  margin-top: var(--space-s);
}

.hero__secondary {
  font-size: var(--step-0);
}

.hero__figure {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.9rem;
  margin-top: var(--space-s);
}

.hero__note {
  color: var(--pencil);
}

.hero__figure .mono {
  font-size: var(--step--2);
  line-height: 1.55;
}

.hero__label {
  margin-right: 0.6em;
  padding: 0.05em 0.35em;
  border: 1px solid currentColor;
  border-radius: 2px;
}

.hero__note--path {
  line-height: 1.7;
}

.hero__crumb {
  white-space: nowrap;
}

/* The cut-out chunk: the one sheet in the site that floats, so the one shadow. */
.hero__sheet {
  position: relative;
  padding: clamp(1.25rem, 0.9rem + 1.5vw, 2rem) clamp(1.25rem, 0.8rem + 2vw, 2.5rem) 1.25rem;
  background: var(--sheet);
  box-shadow:
    0 1px 0 var(--rule),
    0 14px 28px -18px color-mix(in oklab, var(--ink) 45%, transparent);
  font-size: var(--step--1);
  line-height: 1.5;
  hyphens: auto;
}

.hero__sheet > p + p,
.hero__sheet > ul,
.hero__sheet > ul + p {
  margin-top: 0.6em;
}

.hero__heading {
  font-weight: 700;
}

.hero__items {
  padding: 0;
  list-style: none;
}

.hero__fade {
  -webkit-mask-image: linear-gradient(to bottom, #000 0%, transparent 90%);
  mask-image: linear-gradient(to bottom, #000 0%, transparent 90%);
}

.hero__bracket {
  position: absolute;
  top: 1rem;
  bottom: 1rem;
  left: -0.85rem;
  width: 0.7rem;
  height: calc(100% - 2rem);
  overflow: visible;
}

.hero__bracket path {
  fill: none;
  stroke: var(--pencil);
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-dasharray: 1;
  vector-effect: non-scaling-stroke;
}

.hero__stamp {
  position: absolute;
  top: -1.4rem;
  right: clamp(-0.5rem, -2vw, -1.5rem);
  font-size: clamp(1.6rem, 1.2rem + 1.6vw, 2.4rem);
}

.hero__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 2rem;
}

.hero__meta dd {
  white-space: nowrap;
}

.hero__id {
  font-weight: 600;
}

.hero__caption {
  color: var(--ink-faded);
  font-size: var(--step--1);
  font-style: italic;
  max-width: 48ch;
}

@media (min-width: 1024px) {
  .hero {
    grid-template-columns: repeat(12, minmax(0, 1fr));
    align-items: start;
  }

  .hero__title {
    grid-column: 1 / -1;
  }

  .hero__intro {
    grid-column: 1 / span 5;
    padding-top: var(--space-s);
    border-top: 1px solid var(--rule);
  }

  /* Marginalia: the pencil notes sit in the sheet's left margin, set flush right against it. */
  .hero__figure {
    grid-column: 6 / -1;
    grid-template-columns: 12.75rem minmax(0, 1fr);
    column-gap: 1.6rem;
    margin-top: 0;
  }

  .hero__note--path,
  .hero__sheet,
  .hero__caption {
    grid-column: 2;
  }

  .hero__meta {
    grid-column: 1;
    grid-row: 2;
    flex-direction: column;
    align-self: start;
    gap: 1.75rem;
    padding-top: 1.6rem;
    text-align: right;
  }

  .hero__meta dd {
    display: block;
  }
}

/* Before hydration, keep what the pencil will draw hidden; a failsafe shows it if JS never runs.
   Plain `.js …`, not `:global(.js) …`: Vue compiles the latter to a bare `.js`, which hid the page. */
@media (prefers-reduced-motion: no-preference) {
  .js .hero__note,
  .js .hero__stamp,
  .js .hero__sheet {
    visibility: hidden;
    animation: hero-failsafe 0s 2.6s forwards;
  }
}

@keyframes hero-failsafe {
  to {
    visibility: visible;
  }
}
</style>
