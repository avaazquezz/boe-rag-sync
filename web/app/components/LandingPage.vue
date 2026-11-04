<script setup lang="ts">
import { SITE_URL } from "~/content/data"
import type { Copy } from "~/content/types"

const props = defineProps<{ copy: Copy }>()
const path = props.copy.lang === "es" ? "/" : "/en"

useHead({
  htmlAttrs: { lang: props.copy.lang },
  link: [
    { rel: "canonical", href: `${SITE_URL}${path}` },
    { rel: "alternate", hreflang: "es", href: `${SITE_URL}/` },
    { rel: "alternate", hreflang: "en", href: `${SITE_URL}/en` },
    { rel: "alternate", hreflang: "x-default", href: `${SITE_URL}/` },
  ],
  // Lets CSS hide what the pencil is about to draw before hydration, only when JS runs.
  script: [{ innerHTML: "document.documentElement.classList.add('js')", tagPosition: "head" }],
})
useSeoMeta({
  title: props.copy.meta.title,
  description: props.copy.meta.description,
  ogTitle: props.copy.meta.title,
  ogDescription: props.copy.meta.description,
  ogType: "website",
  ogUrl: `${SITE_URL}${path}`,
  ogLocale: props.copy.meta.ogLocale,
  ogImage: `${SITE_URL}/og.png`,
  ogImageWidth: 1200,
  ogImageHeight: 630,
  ogImageAlt: props.copy.meta.ogImageAlt,
  twitterCard: "summary_large_image",
})
</script>

<template>
  <a class="skip-link" href="#main">{{ copy.skip }}</a>
  <TheMasthead :copy="copy" />
  <main id="main" class="main">
    <HeroSection :copy="copy" />
    <FactsLine :copy="copy" />
    <PipelineSection :copy="copy" />
    <RedlineSection :copy="copy" />
    <UsageSection :copy="copy" />
    <BuildSection :copy="copy" />
    <FaqSection :copy="copy" />
    <ClosingSection :copy="copy" />
  </main>
  <TheFooter :copy="copy" />
</template>
