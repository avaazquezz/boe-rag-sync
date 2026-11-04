export default defineNuxtConfig({
  compatibilityDate: "2026-11-04",
  modules: ["@nuxt/fonts"],
  css: ["~/assets/css/main.css"],
  devtools: { enabled: false },
  typescript: { strict: true },
  app: {
    head: {
      meta: [{ name: "theme-color", content: "#ECEDEA" }],
      link: [{ rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }],
    },
  },
  fonts: {
    defaults: { subsets: ["latin"] },
    families: [
      // Both families are used through CSS custom properties, which the module cannot detect:
      // global injects their @font-face anyway. The hero headline is the LCP element, so only
      // its upright face is preloaded.
      {
        name: "Ibarra Real Nova",
        provider: "google",
        global: true,
        weights: ["400 700"],
        styles: ["normal", "italic"],
        preload: { styles: ["normal"] },
      },
      {
        name: "Martian Mono",
        provider: "google",
        global: true,
        weights: ["100 800"],
        styles: ["normal"],
        // Google serves the width axis itself: 75 is the stamp lettering, 87.5 the annotations.
        providerOptions: { google: { experimental: { variableAxis: { wdth: [["75", "100"]] } } } },
      },
    ],
  },
  nitro: { prerender: { routes: ["/", "/en"], ignore: ["/og"] } },
})
