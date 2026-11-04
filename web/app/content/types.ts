// Copy of one page. Text between backticks renders as code (see InlineText.vue).
export type RunIn = { head: string; body: string }

export interface Copy {
  lang: "es" | "en"
  dateLocale: string
  meta: { title: string; description: string; ogLocale: string; ogImageAlt: string }
  skip: string
  masthead: { home: string; edition: string; inForce: string; switchHref: string; switchText: string; switchLabel: string }
  hero: {
    title: string
    lede: string
    cta: string
    secondary: string
    caption: string
    notePath: string
    noteChunk: string[]
    noteVersion: string[]
    stamp: string
  }
  facts: { label: string; items: string[] }
  pipeline: {
    title: string
    intro: string
    epigraph: { quote: string; translation?: string; source: string }
    steps: [RunIn, RunIn, RunIn, RunIn]
    figure: {
      label: string
      wordings: string
      notes: string
      chunks: string
      chars: string
      tokens: string
      repealed: string
      inForce: string
    }
  }
  redline: {
    title: string
    intro: string
    caption: string
    ledgerCaption: string
    unchanged: string
    runsCaption: string
    firstRun: string
    secondRun: string
  }
  usage: { title: string; intro: string; curlCaption: string; recordCaption: string; copy: string; copied: string; loader: string; loaderHref: string }
  build: { title: string; items: RunIn[]; links: { text: string; href: string }[] }
  price: RunIn
  faq: { title: string; items: { q: string; a: string }[] }
  closing: { title: string; cta: string }
  footer: {
    attribution: string
    noAffiliation: string
    disclaimer: string
    madeBy: string
    license: string
    source: string
    colophon: string
  }
}
