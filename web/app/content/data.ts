// Real data, computed with boe_rag_sync (build_records, diff) on the live XML of the Workers' Statute
// (BOE-A-2015-11430) on 2026-11-04. Law text stays in Spanish on both pages: it is the source.

export const SITE_URL = "https://spanish-laws.vazquezlabs.com"
export const LAW_ID = "BOE-A-2015-11430"
export const APIFY_URL = "https://apify.com/vazquezdev/spanish-laws-rag"
export const GITHUB_URL = "https://github.com/avaazquezz/boe-rag-sync"
export const AUTHOR_URL = "https://vazquezdev.pro"

export const ARTICLE_4 = {
  chunkId: `${LAW_ID}:a4:0`,
  chars: 1981,
  tokens: 496,
  inForceFrom: "2023-06-30",
  versionNormId: "BOE-A-2023-15135",
  versionNormName: "Real Decreto-ley 5/2023",
  path: ["Estatuto de los Trabajadores", "Título I", "Capítulo I", "Sección 2.ª", "Artículo 4"],
  heading: "Artículo 4. Derechos laborales.",
  lead: "1. Los trabajadores tienen como derechos básicos, con el contenido y alcance que para cada uno de los mismos disponga su específica normativa, los de:",
  items: [
    "a) Trabajo y libre elección de profesión u oficio.",
    "b) Libre sindicación.",
    "c) Negociación colectiva.",
    "d) Adopción de medidas de conflicto colectivo.",
    "e) Huelga.",
    "f) Reunión.",
    "g) Información, consulta y participación en la empresa.",
  ],
  next: "2. En la relación de trabajo, los trabajadores tienen derecho:",
} as const

export type Wording = { normId: string; published: string; inForceFrom: string }

// Article 37 holds every wording it has had since 2015, in the order of the XML.
export const ARTICLE_37 = {
  heading: "Artículo 37. Descanso semanal, fiestas y permisos.",
  wordings: [
    { normId: "BOE-A-2015-11430", published: "2015-10-24", inForceFrom: "2015-11-13" },
    { normId: "BOE-A-2019-3244", published: "2019-03-07", inForceFrom: "2019-03-08" },
    { normId: "BOE-A-2020-11043", published: "2020-09-23", inForceFrom: "2020-10-13" },
    { normId: "BOE-A-2021-11472", published: "2021-07-10", inForceFrom: "2021-07-11" },
    { normId: "BOE-A-2021-21653", published: "2021-12-29", inForceFrom: "2022-01-01" },
    { normId: "BOE-A-2022-14630", published: "2022-09-07", inForceFrom: "2022-10-07" },
    { normId: "BOE-A-2023-5366", published: "2023-03-01", inForceFrom: "2023-03-02" },
    { normId: "BOE-A-2023-6967", published: "2023-03-17", inForceFrom: "2023-04-01" },
    { normId: "BOE-A-2023-15135", published: "2023-06-29", inForceFrom: "2023-06-30" },
    { normId: "BOE-A-2023-25759", published: "2023-12-20", inForceFrom: "2023-12-21" },
    { normId: "BOE-A-2024-664", published: "2024-01-12", inForceFrom: "2024-01-12" },
    { normId: "BOE-A-2024-10235", published: "2024-05-22", inForceFrom: "2024-05-23" },
    { normId: "BOE-A-2024-15936", published: "2024-08-02", inForceFrom: "2024-08-22" },
    { normId: "BOE-A-2024-24840", published: "2024-11-29", inForceFrom: "2024-11-30" },
    { normId: "BOE-A-2024-26693", published: "2024-12-21", inForceFrom: "2025-03-03" },
    { normId: "BOE-A-2026-20528", published: "2026-10-03", inForceFrom: "2026-10-23" },
    { normId: "BOE-A-2026-21872", published: "2026-10-21", inForceFrom: "2026-10-23" },
  ] satisfies Wording[],
  // A sample of the editorial notes in the XML of the current wording.
  notes: [
    "Se modifica el apartado 6 por el art. 7 del Real Decreto-ley 31/2026, de 20 de octubre.",
    "Se modifica el apartado 6 por la disposición final 10 de la Ley 4/2026, de 1 de octubre.",
    "Téngase en cuenta que esta actualización entra en vigor el 3 de marzo de 2025, según determina la disposición final 4 de la citada Ley.",
    "Se deja sin efecto la modificación del apartado 4 por Resolución de 10 de enero de 2024, que publica el Acuerdo del Congreso…",
  ],
  // Two reforms of paragraph 6 took effect the same day: the later-published one wins.
  tie: {
    inForceFrom: "2026-10-23",
    earlier: { normId: "BOE-A-2026-20528", name: "Ley 4/2026", published: "2026-10-03" },
    later: { normId: "BOE-A-2026-21872", name: "Real Decreto-ley 31/2026", published: "2026-10-21" },
  },
  // Characters of each chunk of the wording in force, at maxChunkChars 2000.
  chunkChars: [1929, 1971, 1766, 1570, 1128, 1967, 1601, 1945, 1186],
} as const

export type Segment = { text: string; op?: "del" | "ins" }

// Article 12.6 before and after Real Decreto-ley 11/2024 (in force 2025-04-01), word diff.
export const ARTICLE_12_REFORM = {
  normId: "BOE-A-2024-26917",
  normName: "Real Decreto-ley 11/2024, de 23 de diciembre",
  inForceFrom: "2025-04-01",
  segments: [
    { text: "6. Para que el trabajador pueda acceder a la jubilación parcial" },
    { text: " antes de alcanzar la edad ordinaria de jubilación", op: "ins" },
    {
      text: ", en los términos establecidos en el texto refundido de la Ley General de la Seguridad Social y demás disposiciones concordantes, ",
    },
    {
      text: "deberá acordar con su empresa una reducción de jornada y de salario de entre un mínimo del veinticinco por ciento y un máximo del cincuenta por ciento y ",
      op: "del",
    },
    { text: "la empresa deberá concertar simultáneamente un contrato de relevo" },
    {
      text: ", de acuerdo con lo establecido en el apartado siguiente, con objeto de sustituir la jornada de trabajo dejada vacante por el trabajador que se jubila parcialmente",
      op: "del",
    },
    { text: " indefinido y a tiempo completo", op: "ins" },
    { text: "." },
  ] satisfies Segment[],
  // What a sync of the whole law emitted that day: the article went from 8 chunks to 7.
  ops: [
    ...Array.from({ length: 7 }, (_, i) => ({ op: "upsert" as const, chunkId: `${LAW_ID}:a12:${i}` })),
    { op: "delete" as const, chunkId: `${LAW_ID}:a12:7`, reason: "superseded" },
  ],
  unchanged: 261,
} as const

// Two runs of the Workers' Statute on Apify with the same syncId (2026-11-03).
export const RUNS = { firstUpserts: 273, secondOps: 0 } as const

export const CURL = `curl -X POST "https://api.apify.com/v2/acts/VazquezDev~spanish-laws-rag/run-sync-get-dataset-items" \\
  -H "Authorization: Bearer $APIFY_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"laws": ["estatuto-trabajadores"]}'`

export const RECORD = `{
  "op": "upsert",
  "chunk_id": "BOE-A-2015-11430:a4:0",
  "point_id": "d29a273d-7c0c-57d6-8e33-5a06157d5991",
  "context_header": "[Estatuto de los Trabajadores > … > Artículo 4]",
  "text": "**Artículo 4. Derechos laborales.**\\n\\n1. Los trabajadores…",
  "in_force_from": "2023-06-30",
  "approx_tokens": 496,
  "source_url": "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430#a4"
}`
