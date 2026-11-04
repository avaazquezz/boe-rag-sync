<script setup lang="ts">
const props = defineProps<{ code: string; caption: string; copyLabel: string; copiedLabel: string }>()
const copied = ref(false)
let timer: ReturnType<typeof setTimeout> | undefined

async function copy() {
  await navigator.clipboard.writeText(props.code)
  copied.value = true
  clearTimeout(timer)
  timer = setTimeout(() => (copied.value = false), 2000)
}

onUnmounted(() => clearTimeout(timer))
</script>

<template>
  <figure class="code">
    <figcaption class="code__bar">
      <span>{{ caption }}</span>
      <button type="button" class="code__copy mono" @click="copy">
        <span aria-live="polite">{{ copied ? copiedLabel : copyLabel }}</span>
      </button>
    </figcaption>
    <pre class="code__pre"><code>{{ code }}</code></pre>
  </figure>
</template>

<style scoped>
.code {
  min-width: 0;
  border-top: 1px solid var(--ink);
}

.code__bar {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  padding-block: 0.6rem;
  color: var(--ink-faded);
  font-size: var(--step--1);
  font-style: italic;
}

.code__copy {
  min-height: 2.25rem;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--rule);
  border-radius: 2px;
  background: transparent;
  color: var(--ink);
  font-style: normal;
  cursor: pointer;
  transition:
    border-color var(--dur-micro) linear,
    color var(--dur-micro) linear;
}

@media (hover: hover) {
  .code__copy:hover {
    border-color: var(--pencil);
    color: var(--pencil);
  }
}

.code__copy:active {
  transform: translateY(1px);
}

/* A typed insert pasted into the gazette: flat paper, a shade darker, no shadow. */
.code__pre {
  margin: 0;
  padding: 1rem 1.1rem;
  overflow-x: auto;
  background: color-mix(in oklab, var(--paper) 94%, var(--ink));
  font-size: var(--step--2);
  line-height: 1.7;
  scrollbar-color: var(--ink-faded) transparent;
  scrollbar-width: thin;
}

.code__pre code {
  font-size: 1em;
}
</style>
