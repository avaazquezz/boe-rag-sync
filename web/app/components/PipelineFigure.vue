<script setup lang="ts">
import gsap from "gsap"
import { Flip } from "gsap/Flip"
import { ARTICLE_37 } from "~/content/data"
import type { Copy } from "~/content/types"
import { MOTION } from "~/utils/motion"

type Step = 0 | 1 | 2 | 3
type Role = "ann" | "old" | "early" | "late" | "memo" | "name" | "stamp" | "chunk"

const props = defineProps<{ copy: Copy; step: Step; still?: boolean }>()
const root = ref<HTMLElement | null>(null)

const { heading, wordings, notes, tie, chunkChars } = ARTICLE_37
const last = wordings.length - 1
const maxChars = Math.max(...chunkChars)
const chunks = chunkChars.map((chars, k) => ({
  id: `a37:${k}`,
  chars,
  tokens: Math.ceil(chars / 4), // the Actor's approx_tokens
  ratio: chars / maxChars,
  before: chunkChars.slice(0, k).reduce((a, b) => a + b, 0) / maxChars,
}))
const sum = chunkChars.reduce((a, b) => a + b, 0) / maxChars
const dmy = (iso: string) => iso.split("-").reverse().join("-")
const role = (normId: string): Role =>
  normId === tie.later.normId ? "late" : normId === tie.earlier.normId ? "early" : "old"

// When each element starts moving towards a state, so the change reads in order.
const DELAY: Record<Step, Partial<Record<Role, number>>> = {
  0: { ann: 0.2 },
  1: { ann: 0.2, memo: 0.3 },
  2: { early: 0.1, late: 0.1, name: 0.45, stamp: 0.45 },
  3: { chunk: 0.15, ann: 0.5 },
}
const delayOf = (to: Step, el: HTMLElement) =>
  (DELAY[to][el.dataset.role as Role] ?? 0) + Number(el.dataset.k ?? 0) * 0.06

let go: ((to: Step) => Promise<void>) | undefined

// Every state is a CSS layout keyed on data-state (not data-step: the section's triggers select
// [data-step]); GSAP only animates between them. Flip owns the figure's direct children (position
// and opacity), the flourishes only play on their insides and always end on the CSS values, so an
// interrupted change can be reverted without leaving residue.
useGsap(root, ({ motion }, ctx) => {
  const el = root.value
  if (props.still || !el) return
  gsap.registerPlugin(Flip)
  const q = gsap.utils.selector(el)
  let flourish: gsap.core.Timeline | undefined
  let latest = 0

  go = async (to) => {
    const id = ++latest
    flourish?.revert()
    const targets = [...el.children] as HTMLElement[]
    // Measures where everything is right now, mid-flight included, then completes running flips.
    const state = Flip.getState(targets, { props: "opacity" })
    await nextTick()
    if (id !== latest || ctx.isReverted) return
    ctx.add(() => {
      if (!motion) {
        gsap.from(targets, {
          opacity: (_i: number, t: HTMLElement) => state.getProperty(t, "opacity"),
          duration: 0.2,
          ease: "none",
          overwrite: "auto",
          clearProps: "opacity",
        })
        return
      }
      Flip.from(state, {
        duration: MOTION.dur.reveal,
        ease: "brand",
        scale: true,
        stagger: (_i: number, t: HTMLElement) => delayOf(to, t),
      })
      flourish = gsap.timeline()
      if (to === 1) {
        flourish
          .fromTo(
            q(".pf__strike"),
            { clipPath: "inset(0 100% 0 0)" },
            { clipPath: "inset(0 0% 0 0)", duration: 0.35, ease: "power2.inOut", stagger: 0.15, clearProps: "clipPath" },
            0.8,
          )
          // Struck, the note fades back to its CSS opacity.
          .from(
            q(".pf__memo-text"),
            { opacity: 1, duration: MOTION.dur.ui, ease: "none", stagger: 0.15, clearProps: "opacity" },
            "<0.3",
          )
      } else if (to === 2) {
        flourish.from(
          q(".pf__ink"),
          { autoAlpha: 0, scale: 1.6, duration: 0.24, ease: "power4.in", stagger: 0.3, clearProps: "all" },
          0.85,
        )
      }
    })
  }
  return () => {
    go = undefined
  }
})

watch(
  () => props.step,
  (to) => void go?.(to),
)
</script>

<template>
  <div
    ref="root"
    class="pf"
    :class="{ 'pf--still': still }"
    :data-state="step"
    :style="{ '--last': last, '--sum': sum }"
  >
    <p class="pf__ann pf__ann--0 mono" data-role="ann">{{ wordings.length }} {{ copy.pipeline.figure.wordings }}</p>
    <p class="pf__ann pf__ann--1 mono" data-role="ann">{{ copy.pipeline.figure.notes }}</p>
    <p class="pf__ann pf__ann--3 mono" data-role="ann">{{ chunks.length }} {{ copy.pipeline.figure.chunks }}</p>

    <div
      v-for="(w, i) in wordings"
      :key="w.normId"
      class="pf__slip"
      :class="`pf__slip--${role(w.normId)}`"
      :data-role="role(w.normId)"
      :style="{ '--i': i }"
    >
      <p class="pf__line">
        <span class="pf__id">{{ w.normId }}</span>
        <span>{{ dmy(w.published) }}</span>
        <span>{{ dmy(w.inForceFrom) }}</span>
      </p>
      <p v-if="i === last" class="pf__heading" lang="es">{{ heading }}</p>
    </div>
    <!-- Dims the older wordings as one layer: fading each slip would let them show through each other. -->
    <div class="pf__veil" data-role="old" />

    <p v-for="(note, k) in notes" :key="note" class="pf__memo" data-role="memo" :data-k="k" :style="{ '--k': k }" lang="es">
      <span class="pf__memo-text">{{ note }}</span>
      <span class="pf__strike" />
    </p>

    <p class="pf__name pf__name--early" data-role="name" lang="es">{{ tie.earlier.name }}</p>
    <p class="pf__name pf__name--late" data-role="name" lang="es">{{ tie.later.name }}</p>
    <div class="pf__stamp pf__stamp--early" data-role="stamp">
      <span class="pf__ink"><RubberStamp :text="copy.pipeline.figure.repealed" tone="red" /></span>
    </div>
    <div class="pf__stamp pf__stamp--late" data-role="stamp">
      <span class="pf__ink"><RubberStamp :text="copy.pipeline.figure.inForce" tone="blue" /></span>
    </div>

    <div
      v-for="(c, k) in chunks"
      :key="c.id"
      class="pf__chunk mono"
      data-role="chunk"
      :data-k="k"
      :style="{ '--k': k, '--r': c.ratio, '--cum': c.before }"
    >
      <span class="pf__chunk-id">{{ c.id }}</span>
      <span>{{ c.chars }} {{ copy.pipeline.figure.chars }}</span>
      <span>{{ c.tokens }} {{ copy.pipeline.figure.tokens }}</span>
    </div>
  </div>
</template>

<style scoped>
/* Geometry. Custom properties keep their cq units unresolved until a child uses them, so every
   length below is measured against the figure itself (a size container), whatever its parent. */
.pf {
  --slip-w: min(100cqw, 20rem);
  --band: clamp(0.95rem, (100cqh - 11rem) / (var(--last) + 1), 1.6rem);
  --dy: calc(var(--band) - 1px);
  --dx: min((100cqw - var(--slip-w)) / var(--last), 1.25rem);
  --top: 2.5rem;
  --front-h: calc(var(--band) + 3.5rem);
  --memo-h: 1.5rem;
  --name-h: 1.75rem;
  --pile-step: 0.18rem;
  --pile: calc((var(--last) - 2) * var(--pile-step) + var(--band));
  --cgap: 0.375rem;
  --hmax: clamp(1.75rem, (100cqh - var(--top) - 8 * var(--cgap) - 1rem) / var(--sum), 4.75rem);
  /* Height of each state's content, to centre it vertically. */
  --h0: calc(var(--last) * var(--dy) + var(--front-h));
  --h1: calc(var(--h0) + 4 * var(--memo-h));
  --h2: calc(var(--pile) + 1.5rem + 2 * var(--name-h) + var(--band) + 3rem + var(--front-h) + 2rem);
  --h3: calc(var(--sum) * var(--hmax) + 8 * var(--cgap));
  position: relative;
  height: 100%;
  container-type: size;
  overflow-x: clip;
}

.pf--still {
  --band: 0.95rem;
  height: 23rem;
}

.pf--still[data-state="1"] {
  height: 28.5rem;
}

.pf--still[data-state="2"] {
  height: 21rem;
}

.pf--still[data-state="3"] {
  height: 28rem;
}

.pf > * {
  --y0: max(var(--top), (100cqh - var(--h0)) / 2);
  --y1: max(var(--top), (100cqh - var(--h1)) / 2);
  --y2: max(1rem, (100cqh - var(--h2)) / 2);
  --y3: max(var(--top), (100cqh - var(--h3)) / 2);
  --t2: calc(var(--y2) + var(--pile) + 1.5rem + var(--name-h));
  --late-x: 0px;
  --late-y: calc(var(--t2) + var(--band) + 3rem + var(--name-h));
  position: absolute;
  top: 0;
  left: 0;
  margin: 0;
}

/* Wide enough for the two tied wordings side by side. */
@container (min-width: 41.25rem) {
  .pf > * {
    --h2: calc(var(--pile) + 1.5rem + var(--name-h) + var(--front-h) + 2rem);
    --late-x: calc(var(--slip-w) + 1.25rem);
    --late-y: var(--t2);
  }
}

/* Pencil annotations. */
.pf__ann {
  z-index: 40;
  color: var(--pencil);
  font-size: var(--step--2);
  font-weight: 600;
  line-height: 1.5;
  opacity: 0;
}

.pf__ann--0 {
  top: calc(var(--y0) - 1.9rem);
}

.pf__ann--1 {
  top: calc(var(--y1) - 1.9rem);
}

.pf__ann--3 {
  top: calc(var(--y3) - 1.9rem);
}

.pf[data-state="0"] .pf__ann--0,
.pf[data-state="1"] .pf__ann--1,
.pf[data-state="3"] .pf__ann--3 {
  opacity: 1;
}

/* Wordings: thin printed slips, flat, hairline edge. */
.pf__slip {
  z-index: calc(var(--i) + 1);
  top: calc(var(--y0) + var(--i) * var(--dy));
  left: calc(var(--i) * var(--dx));
  width: var(--slip-w);
  height: var(--band);
  background: var(--sheet);
  border: 1px solid var(--rule);
}

.pf__slip--early,
.pf__slip--late {
  z-index: calc(var(--i) + 2);
}

.pf__slip--late {
  height: var(--front-h);
}

.pf__veil {
  z-index: var(--last);
  inset: 0;
  background: var(--paper);
  opacity: 0;
}

.pf[data-state="2"] .pf__veil,
.pf[data-state="3"] .pf__veil {
  opacity: 0.7;
}

.pf__line {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  gap: 1.1em;
  height: calc(var(--band) - 2px);
  padding-inline: 0.6rem;
  color: var(--ink-faded);
  font-family: var(--mono);
  font-stretch: 87.5%;
  font-size: 0.72rem;
  font-variant-ligatures: none;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  white-space: nowrap;
}

.pf__id {
  color: var(--ink);
}

/* A fixed size so it always sets in the two lines --front-h makes room for. */
.pf__heading {
  padding: 0.35rem 0.6rem 0;
  font-size: 0.95rem;
  font-weight: 700;
  line-height: 1.2;
}

.pf[data-state="1"] .pf__slip {
  top: calc(var(--y1) + var(--i) * var(--dy));
}

.pf[data-state="2"] .pf__slip--old,
.pf[data-state="3"] .pf__slip--old {
  top: calc(var(--y2) + var(--i) * var(--pile-step));
  left: calc(var(--i) * min(0.2rem, var(--dx)));
}

.pf[data-state="2"] .pf__slip--early,
.pf[data-state="3"] .pf__slip--early {
  top: var(--t2);
  left: 0;
}

/* The wording in force stays put in state 3 and fades while its chunks come out of it. */
.pf[data-state="2"] .pf__slip--late,
.pf[data-state="3"] .pf__slip--late {
  top: var(--late-y);
  left: var(--late-x);
}

.pf[data-state="3"] .pf__slip {
  opacity: 0;
}

/* Editorial notes, set under the current wording and struck out in red. */
.pf__memo {
  z-index: 20;
  top: calc(var(--y1) + var(--last) * var(--dy) + var(--front-h) - 1px + var(--k) * (var(--memo-h) - 1px));
  left: calc(var(--last) * var(--dx));
  display: flex;
  align-items: center;
  width: min(100cqw - var(--last) * var(--dx), 28rem);
  height: var(--memo-h);
  padding-inline: 0.6rem;
  background: var(--sheet);
  border: 1px solid var(--rule);
  font-size: 0.84rem;
  font-style: italic;
  line-height: 1;
  opacity: 0;
}

.pf[data-state="1"] .pf__memo {
  opacity: 1;
}

.pf__memo-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  opacity: 0.6;
}

.pf__strike {
  position: absolute;
  top: 46%;
  right: 0.45rem;
  left: 0.45rem;
  height: 1.5px;
  background: var(--stamp-red);
  border-radius: 1px;
  transform: rotate(-0.4deg);
}

/* The tie: two wordings in force the same day. */
.pf__name {
  z-index: 20;
  display: flex;
  align-items: flex-end;
  height: var(--name-h);
  padding-bottom: 0.3rem;
  font-size: var(--step--1);
  font-weight: 700;
  line-height: 1;
  white-space: nowrap;
  opacity: 0;
}

.pf__name--early {
  top: calc(var(--t2) - var(--name-h));
}

.pf__name--late {
  top: calc(var(--late-y) - var(--name-h));
  left: var(--late-x);
}

.pf__stamp {
  z-index: 40;
  font-size: 1.05rem;
  opacity: 0;
}

.pf__stamp--early {
  top: calc(var(--t2) + var(--band) + 0.7rem);
  left: 1.5rem;
}

.pf__stamp--late {
  top: calc(var(--late-y) + var(--front-h) - 0.4rem);
  left: calc(var(--late-x) + var(--slip-w) - 8rem);
}

.pf__ink {
  display: inline-block;
}

.pf[data-state="2"] .pf__name,
.pf[data-state="2"] .pf__stamp {
  opacity: 1;
}

/* Chunks: the one cut-out sheet of the site, so the one shadow. Height is proportional to characters. */
.pf__chunk {
  z-index: 30;
  top: calc(var(--y0) + var(--last) * var(--dy));
  left: calc(var(--last) * var(--dx));
  display: flex;
  align-items: flex-start;
  gap: 1.25em;
  width: var(--slip-w);
  height: calc(var(--r) * var(--hmax));
  padding: 0.45rem 0.6rem;
  background: var(--sheet);
  box-shadow:
    0 1px 0 var(--rule),
    0 14px 28px -18px color-mix(in oklab, var(--ink) 45%, transparent);
  color: var(--ink-faded);
  font-size: 0.72rem;
  line-height: 1.2;
  white-space: nowrap;
  opacity: 0;
}

.pf__chunk-id {
  margin-right: auto;
  color: var(--pencil);
  font-weight: 600;
}

.pf[data-state="1"] .pf__chunk {
  top: calc(var(--y1) + var(--last) * var(--dy));
}

.pf[data-state="2"] .pf__chunk {
  top: var(--late-y);
  left: var(--late-x);
}

.pf[data-state="3"] .pf__chunk {
  top: calc(var(--y3) + var(--cum) * var(--hmax) + var(--k) * var(--cgap));
  left: 0;
  opacity: 1;
}
</style>
