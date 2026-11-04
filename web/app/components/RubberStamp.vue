<script setup lang="ts">
// A rubber stamp: condensed heavy mono in caps, double frame, ink that does not reach every corner.
// Blue for what is in force, red for what is not.
withDefaults(defineProps<{ text: string; tone?: "blue" | "red"; date?: string }>(), { tone: "blue", date: undefined })
const filterId = `stamp-ink-${useId()}`
</script>

<template>
  <span class="stamp" :class="`stamp--${tone}`">
    <svg class="stamp__ink" aria-hidden="true" focusable="false">
      <filter :id="filterId" x="-5%" y="-5%" width="110%" height="110%">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="noise" />
        <feColorMatrix in="noise" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.5 1.6" result="holes" />
        <feComposite in="SourceGraphic" in2="holes" operator="in" />
      </filter>
    </svg>
    <span class="stamp__body" :style="{ filter: `url(#${filterId})` }">
      <span class="stamp__text">{{ text }}</span>
      <span v-if="date" class="stamp__date">{{ date }}</span>
    </span>
  </span>
</template>

<style scoped>
.stamp {
  --stamp-color: var(--pencil);
  display: inline-block;
  rotate: -7deg;
  pointer-events: none;
}

.stamp--red {
  --stamp-color: var(--stamp-red);
}

.stamp__ink {
  position: absolute;
  width: 0;
  height: 0;
}

.stamp__body {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15em;
  padding: 0.3em 0.7em 0.35em;
  border: 3px double var(--stamp-color);
  outline: 2px solid var(--stamp-color);
  outline-offset: 3px;
  color: var(--stamp-color);
  font-family: var(--mono);
  font-stretch: 75%;
  font-weight: 800;
  text-transform: uppercase;
  line-height: 1;
  mix-blend-mode: multiply;
}

.stamp__text {
  font-size: 1em;
  letter-spacing: 0.08em;
}

.stamp__date {
  font-size: 0.48em;
  font-weight: 600;
  letter-spacing: 0.12em;
}
</style>
