import type { Copy } from "./types"
import { GITHUB_URL } from "./data"

export const en: Copy = {
  lang: "en",
  dateLocale: "en-GB",
  meta: {
    title: "Spanish Laws for RAG · Spanish law, ready for RAG and kept current",
    description:
      "Apify Actor that turns Spain's consolidated legislation into RAG-ready chunks and keeps your vector store in sync with upserts and deletes.",
    ogLocale: "en_GB",
    ogImageAlt: "The headline «La ley española, artículo a artículo, en su redacción vigente» with a blue VIGENTE (in force) stamp.",
  },
  skip: "Skip to content",
  masthead: {
    home: "Spanish Laws for RAG, home",
    edition: "Year I.—No. 1",
    inForce: "Text in force as of today",
    switchHref: "/",
    switchText: "Español",
    switchLabel: "Leer esta página en español",
  },
  hero: {
    title: "Spanish law, article by article, as it stands today.",
    lede: "An Apify Actor that turns Spain's consolidated legislation into RAG-ready chunks and keeps your vector store current: after every reform, only what changed, deletes included.",
    cta: "Try it free on Apify",
    secondary: "Read the code on GitHub",
    caption:
      "Article 4 of the Workers' Statute as it reaches your index: one chunk, with its path in the law and the version in force.",
    notePath: "path",
    noteChunk: ["1 chunk", "496 tokens"],
    noteVersion: ["in force since", "2023-06-30", "Real Decreto-ley 5/2023"],
    stamp: "Vigente",
  },
  facts: {
    label: "Summary",
    items: [
      "Published on Apify Store",
      "Open source, MIT licence",
      "Tested on the real XML of four laws",
      "Checked every Monday against the BOE API",
    ],
  },
  pipeline: {
    title: "Seventeen wordings, one article in force.",
    intro:
      "Article 37 of the Workers' Statute comes out of the open data with all seventeen wordings it has had since 2015, plus the notes of every reform. This is how it becomes chunks:",
    epigraph: {
      quote: "Las leyes sólo se derogan por otras posteriores.",
      translation: "Laws are only repealed by later laws.",
      source: "Spanish Civil Code, art. 2.2. In the Gaceta de Madrid of 25 July 1889 it was art. 5.",
    },
    steps: [
      {
        head: "The XML.",
        body: "Each wording carries the norm that enacted it, its publication date and the date it took effect.",
      },
      {
        head: "Notes out.",
        body: "«Se modifica el apartado 6 por…», «Téngase en cuenta…». Editorial notes often quote the previous wording, so they are removed before splitting and repealed text never reaches your index.",
      },
      {
        head: "The later law wins.",
        body: "Two reforms of paragraph 6 took effect on the same day, 23 October 2026: Ley 4/2026 and Real Decreto-ley 31/2026. The one published later prevails, as the Civil Code rules and as boe.es resolves it.",
      },
      {
        head: "Nine chunks.",
        body: "The wording in force is split by paragraphs up to 2,000 characters. Every chunk carries its path in the law, a stable `chunk_id` and a `point_id` ready for Qdrant.",
      },
    ],
    figure: {
      label: "From the XML of article 37 to its chunks",
      wordings: "wordings",
      notes: "editorial notes",
      chunks: "chunks",
      chars: "chars",
      tokens: "tokens",
      repealed: "No vigente",
      inForce: "Vigente",
    },
  },
  redline: {
    title: "After every reform, only what changed.",
    intro:
      "On 1 April 2025, Real Decreto-ley 11/2024 took effect and rewrote partial retirement in article 12 of the Statute. The article got shorter: it went from eight chunks to seven.",
    caption: "Art. 12.6, before and after. Red is removed; blue is added.",
    ledgerCaption: "What a sync would have emitted that day, computed with the Actor's code on the real XML:",
    unchanged: "261 unchanged chunks: neither emitted nor charged.",
    runsCaption: "On Apify, with the whole Statute and the same `syncId`:",
    firstRun: "upserts on the first run",
    secondRun: "operations on the second, with no reform in between",
  },
  usage: {
    title: "Try it with one request.",
    intro:
      "With your Apify token, one call runs the Actor and returns its records. No code: open the Actor in the console, keep the prefilled Workers' Statute and press Start.",
    curlCaption: "Run it and get the records",
    recordCaption: "Each record is one operation for your vector store",
    copy: "Copy",
    copied: "Copied",
    loader: "The loader for Qdrant and pgvector is in the README",
    loaderHref: `${GITHUB_URL}#load-into-a-vector-store`,
  },
  build: {
    title: "Built to be maintained.",
    items: [
      {
        head: "Functional core.",
        body: "Only the download and the Apify shell do I/O; the parser, the splitter and the diff are pure functions.",
      },
      {
        head: "Real data, no network.",
        body: "Tests run on real XML trimmed from four laws: the Workers' Statute, the Civil Code, the Penal Code and the income tax law.",
      },
      {
        head: "Checked on every commit.",
        body: "Strict mypy, Ruff with every rule and pytest, in a pre-commit hook and in CI.",
      },
      {
        head: "A canary every Monday.",
        body: "It checks against the BOE API that the twenty aliases still point to laws in force and that a real law still splits correctly.",
      },
      {
        head: "Decisions in writing.",
        body: "Five ADRs explain what is expensive to change: the sync manifest, the record contract and why the hash leaves out the update date.",
      },
    ],
    links: [
      { text: "Design notes", href: `${GITHUB_URL}/blob/main/docs/design.md` },
      { text: "Decision records", href: `${GITHUB_URL}/tree/main/docs/adr` },
    ],
  },
  price: {
    head: "Price.",
    body: "Free during launch: you only pay for your Apify platform usage. Later, one charge per article synced; unchanged articles and deletes are never charged.",
  },
  faq: {
    title: "Questions",
    items: [
      {
        q: "Does the text have legal validity?",
        a: "No. The consolidated text is informative only; the official text is the one published in the BOE. Every chunk carries that notice and the source attribution.",
      },
      {
        q: "Are embeddings included?",
        a: "No: you compute them with the model of your choice. The Actor delivers text, path and metadata, and the README's loader takes them to Qdrant or pgvector.",
      },
      {
        q: "Which laws can I ask for?",
        a: "Any consolidated norm with a `BOE-A-…` id, by id or by its boe.es URL, and twenty common laws by alias: `constitucion`, `codigo-civil`, `irpf`…",
      },
      { q: "What about case law or the daily gazette?", a: "Out of scope: consolidated legislation only." },
      {
        q: "What if I wipe my vector store?",
        a: "Run once with `fullReload`: it emits every chunk in force again and deletes the stale ones.",
      },
    ],
  },
  closing: { title: "Make your assistant cite the law in force today.", cta: "Try it free on Apify" },
  footer: {
    attribution: "Basado en datos de la Agencia Estatal Boletín Oficial del Estado (based on data from the BOE).",
    noAffiliation:
      "This project is not affiliated with or endorsed by the Agencia Estatal Boletín Oficial del Estado.",
    disclaimer: "The consolidated text is informative only and has no legal validity.",
    madeBy: "Made by",
    license: "Open source, MIT licence",
    source: "Source code",
    colophon: "Set in Ibarra Real Nova, a revival of the types of the 1780 Quijote, and Martian Mono.",
  },
}
