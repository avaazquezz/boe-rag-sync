<script setup lang="ts">
// Source of public/og.png: a screenshot of this page at 1200×630. Not linked and not prerendered.
useHead({ htmlAttrs: { lang: "es" }, meta: [{ name: "robots", content: "noindex" }] })
</script>

<template>
  <div class="og">
    <p class="og__name">Spanish Laws for RAG</p>
    <hr class="rule-double" />
    <p class="og__title">La ley española, artículo a artículo, en su redacción vigente.</p>
    <p class="og__note mono">upsert · <span class="og__delete">delete</span> · spanish-laws.vazquezlabs.com</p>
    <div class="og__stamp"><RubberStamp text="Vigente" /></div>
  </div>
</template>

<style scoped>
.og {
  position: relative;
  width: 1200px;
  height: 630px;
  padding: 56px 72px;
  overflow: hidden;
  background: var(--paper);
}

.og__name {
  font-size: 30px;
  font-weight: 700;
  letter-spacing: 0.06em;
  font-variant-caps: all-small-caps;
  margin-bottom: 14px;
}

.og__title {
  margin-top: 48px;
  max-width: 15ch;
  font-size: 88px;
  line-height: 0.98;
  letter-spacing: -0.02em;
}

.og__note {
  position: absolute;
  left: 72px;
  bottom: 52px;
  color: var(--pencil);
  font-size: 20px;
}

.og__delete {
  color: var(--stamp-red);
}

.og__stamp {
  position: absolute;
  right: 80px;
  bottom: 120px;
  font-size: 64px;
}
</style>
