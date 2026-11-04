# Landing brief — spanish-laws.vazquezlabs.com

Approved by the owner on 2026-11-04. The landing lives in `web/` and is the spec for anyone building it.

## Brief

- **Goal:** one action, "Try it free on Apify" (Apify Store page). Secondary, lower weight: the code on GitHub.
  No analytics in v1: LinkedIn post clicks and Apify Console users/runs cover both ends of the funnel.
- **Audience:** recruiters and CTOs arriving from a LinkedIn post, mostly on mobile. The recruiter must see
  craft in 10 s; the CTO must understand the mechanism and be able to try it in 2 minutes.
- **Positioning:** the consolidated text is already free elsewhere; what nobody offers is clean chunks with
  the wording in force and a sync that emits deletes.
- **Proof:** no testimonials or logos. Only verifiable facts: published on Apify Store, MIT source, tests on
  real BOE XML of four laws, weekly live canary, five ADRs.
- **Languages:** Spanish at `/`, English at `/en`.
- **Copy:** written from the README and verified numbers; anything not provable is marked `[REVISAR]`.

## Concept: the annotated gazette

The page is a printed gazette that an engineer works on with a red-and-blue pencil: **blue annotates and
adds (upsert), red strikes out (delete, repealed)**. Hook: the Gaceta de Madrid of 25 July 1889 printed the
Civil Code, whose art. 5 read "Las leyes sólo se derogan por otras leyes posteriores"; today it is art. 2.2,
"Las leyes sólo se derogan por otras posteriores", the lex posterior rule the Actor uses to pick the wording
in force.

Touch points:
1. **Edition masthead:** "Año I · Núm. 1 · <weekday, date> · Texto vigente a fecha de hoy". The date is today
   in Europe/Madrid, the Actor's default `asOfDate`.
2. **Marginal annotations** in mono, blue: `chunk_id`, tokens, effective date next to real article text.
3. **Two inks with a fixed meaning** everywhere: blue adds, red removes.
4. **Rubber stamps** VIGENTE / DEROGADO that land with ink pressure.

## Art direction

| Token | Hex (approx.; contrast measured at build) | Role |
|---|---|---|
| paper | `#ECEDEA` | Background. Grey newsprint, deliberately not cream (first `#F1F0EB` read as cream) |
| sheet | `#FAFAF7` | Cut-out chunk surface |
| ink | `#17191E` | Text and rules, blue-tinted black |
| ink-faded | `#5A5D66` | Metadata |
| pencil-blue | `#2347C5` | Annotation, upsert, primary CTA, focus |
| stamp-red | `#C2352B` | Delete, repealed. Never on a CTA |

- Gazette grammar: double rules, run-in bold heads ("**Art. 5.º** Las leyes…"), hierarchy by small caps
  and centring, no boxes. One shadow in the whole site: the cut-out sheet.
- No photos and nothing AI-generated. Everything is drawn in code: gazette column with real BOE text, SVG
  stamps with a static texture, OG image made in code.
- **Legal:** evoke the genre, never the BOE's identity. No coat of arms, no "Boletín Oficial del Estado"
  masthead; attribution and the no-affiliation notice in the footer.

## Typography

- **Ibarra Real Nova** (Google Fonts, OFL, variable wght 400–700 + italic) for display and text: a revival of
  the types Jerónimo Gil cut for the Real Academia's 1780 *Quijote*, printed by Joaquín Ibarra. Spanish print
  for Spanish law.
- **Martian Mono** (Google Fonts, OFL, variable wght 100–800, wdth 75–112.5) for annotations, JSON and ids;
  at wdth 75 / wght 800 in caps it is the stamp lettering.
- Scale: base 18 → 20 px, ratio 1.2 (mobile) → 1.333 (desktop); hero
  `clamp(2.75rem, 1.6rem + 5.2vw, 6.5rem)`. Self-hosted with `@nuxt/fonts`, preload Ibarra roman only.
- Discarded: Newsreader + JetBrains Mono (interchangeable with any news or legaltech site); Old Standard TT
  (true to 1889 but static, single width, rough at reading sizes).
- Risk: Ibarra's small x-height at body size. Checked in the type proof at 375 px; fallback body face
  Source Serif 4.

## Motion: level 3, no Lenis

A gazette is read, not glided: native scroll (better in LinkedIn's in-app browser, one dependency fewer).

| Section | Question it answers | Motion |
|---|---|---|
| Hero | What is this, is it for me? | Headline static from first paint (LCP). Annotations drawn in pencil, VIGENTE stamp lands |
| Summary line | Can I trust it? | Verifiable facts. No motion |
| **Set-piece 1: From XML to chunk** | What does it solve that I can't do in an afternoon? | Desktop pin + scrub, ≤ 2.5 screens: art. 2.2 epigraph → editorial notes struck in red → lex posterior stamps old wordings DEROGADO and the chosen one VIGENTE → the article splits into annotated chunks (Flip) |
| **Set-piece 2: Redline** | How does it stay up to date? | A reform as red strike + blue insertion, the op ledger and real counters (first run 273 upserts, second run 0 ops). Fires once, no pin |
| Usage | Can I try it in 2 minutes? | Real `curl` and loader, copy button. No motion |
| How it is built | Who made it, with what craft? | Gazette index (functional core, real fixtures, strict mypy, canary, ADRs); lines enter in reading order |
| Price + FAQ | How much? What if…? | Native `<details>`. No motion |
| Closing CTA | What now? | The promise reworded, stamp with today's date |
| Footer | — | BOE attribution, no affiliation, VazquezDev signature → vazquezdev.pro |

| Set-piece | Argues | Cost | Mobile | Reduced motion |
|---|---|---|---|---|
| From XML to chunk | The hard part is solved | GSAP + ScrollTrigger + Flip + SplitText lazy-loaded; DOM only | 4 stacked steps, no pin | Crossfade between states, all visible |
| Redline | Sync with deletes | Low | Same, shorter | Final state directly |
| Stamp + pencil underline | The concept, repeated on links and CTAs | Very low (CSS/SVG) | Same | Stamp appears without pressure |

Budgets: initial JS < 300 KB compressed, LCP ≤ 2.5 s, CLS ≤ 0.1, INP ≤ 200 ms on mobile.

## References (compared against at the final gate)

1. **Gaceta de Madrid, 25 July 1889** (boe.es PDF A00249-00259): edition masthead, double rules, run-in
   heads, hierarchy without boxes. Not its coat of arms or masthead.
2. **Proofs marked with a red-and-blue pencil:** two inks with a fixed meaning.
3. **Bartosz Ciechanowski, "Mechanical Watch":** explain a mechanism by showing it work, text and figure in
   lockstep.

## Stack

Nuxt (static generation) + GSAP + `@nuxt/fonts` in `web/`, excluded from the Actor's Docker context. No
i18n module: two routes with one copy file per language. Deployed as a static image behind Traefik on the
owner's Hetzner server at `spanish-laws.vazquezlabs.com`.
