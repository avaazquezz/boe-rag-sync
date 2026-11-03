Spanish Laws for RAG turns Spanish consolidated legislation into clean, structure-aware chunks ready to
embed, and keeps your vector store in sync as the laws change. It is built for developers of RAG
assistants on Spanish law: legaltech products, AI agencies, and in-house HR, tax and compliance teams.
The official open data XML holds every wording each article ever had, mixed with editorial notes and
repealed text. Turning it into current, well-cut chunks, and then tracking every reform in your store,
is days of work plus ongoing maintenance. This Actor does both: the first run emits every chunk, later
runs emit only what changed plus the deletes you need to apply.

Data source: the consolidated legislation open data API of the Agencia Estatal Boletín Oficial del
Estado. This Actor is not affiliated with or endorsed by the Agencia Estatal Boletín Oficial del Estado.

## Resumen en español

Convierte la legislación consolidada española (datos abiertos del BOE) en fragmentos listos para RAG y
mantiene sincronizada tu base vectorial:

- Un artículo por fragmento si cabe; si no, se divide por párrafos y solo si hace falta por frases. Las
  tablas se conservan en Markdown.
- Cada fragmento lleva su ruta (ley > título > capítulo > artículo) y la redacción vigente en la fecha
  que elijas, sin notas editoriales ni texto derogado.
- La primera ejecución lo emite todo; las siguientes, solo lo que cambió y los borrados (`delete`).
- Identificadores estables y `point_id` UUID listo para Qdrant; con pgvector funciona igual.
- Gratis durante el lanzamiento. El texto consolidado es informativo y no tiene valor jurídico.

## What you get

- **Structure-aware chunks.** One article per chunk when it fits in `maxChunkChars`. A longer article is
  split at paragraph boundaries, and only a paragraph that alone exceeds the limit is split by
  sentences. Tables are kept as Markdown; an oversized table is split by rows, repeating the header in
  every chunk.
- **Where each chunk sits.** `hierarchy` lists the enclosing headings (book, title, chapter, section)
  and `context_header` gives the whole path in one line, e.g.
  `[Estatuto de los Trabajadores > … > TÍTULO I. De la relación individual de trabajo > … > Artículo 4]`.
- **The wording in force at a date.** The source XML holds every wording an article ever had, not in
  date order. The Actor picks the one in force at `asOfDate` the way boe.es does: among the wordings
  already in force, the one from the most recently published norm (lex posterior). Taking the latest
  effective date instead would serve the wrong text whenever a later reform takes effect before an
  earlier one's deferred date.
- **Clean text.** Editorial notes (footnotes and "Téngase en cuenta…" boxes, which often quote the
  previous wording) are removed, and repealed articles ("(Suprimido)", "(Derogada)", "(Sin
  contenido)"…) produce no chunks.
- **Stable ids.** `chunk_id` is `{law_id}:{block_id}:{chunk_index}`, and `point_id` is a UUID derived
  from it, ready to use as a Qdrant point id.
- **Incremental sync with deletes**, explained below.

## How sync works

1. The first run emits an `upsert` for every chunk of every law in `laws`.
2. The Actor remembers what it sent: for each `syncId` and law, the `chunk_id` and `content_hash` of
   every chunk, in a named key-value store called `boe-rag-sync-state` in your own Apify account.
3. Later runs compare the current chunks with that state and emit only:
   - `upsert` for chunks that are new or whose content changed;
   - `delete` for chunks no longer produced, with `reason` `superseded` (the article still exists but
     now has fewer chunks) or `repealed` (the article has no text in force at `asOfDate`; when a whole
     law is repealed, all its chunks).

   Unchanged chunks are not emitted. The records of one article come together, deletes first, and an
   article is emitted whole or not at all.

### Tips

- **Schedule it.** Run it on an [Apify Schedule](https://docs.apify.com/platform/schedules), for
  example weekly, with the same input. Do not let two runs with the same `syncId` overlap: they
  would race on the saved state.
- **Wiped your store?** The state records what the Actor emitted, not what your store ingested. After
  wiping the store, or if your loader failed, run once with `fullReload: true`: every current chunk is
  emitted again and stale ones are deleted.
- **Changing `maxChunkChars`** needs nothing special: the old ids are deleted and the new ones upserted.
- **Point-in-time runs.** A fixed `asOfDate` keeps its own state, so a one-off historical run never
  disturbs the store you keep up to date. Leave `asOfDate` empty to follow the laws as they change.
- **One `syncId` per vector store** you keep in sync.
- Delivery is at least once: a run interrupted before saving its state emits those records again next
  time. Upserts and deletes are idempotent, so applying them twice is harmless.

## How much does it cost?

Free during launch: there is no Actor fee, only the Apify platform usage your runs consume.

Later the Actor will move to pay-per-event pricing with one event per article synced, that is, per
article (or disposition, preamble…) with at least one new or changed chunk. Unchanged articles and
deletes are never charged; a `fullReload` emits every article again, so it counts every article.

If a run reaches the spending limit you set, the laws that did not fit end as
`stopped_by_spending_limit` (their deletes are still emitted) and the next run continues where this
one stopped. Records are delivered before they are charged, so an interrupted run never bills the same
article twice.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `laws` | array of strings | required | Laws to sync. Each item is a BOE id (`BOE-A-2015-11430`), any boe.es URL containing the id, or one of the aliases below. |
| `asOfDate` | string `YYYY-MM-DD` | today in Spain (Europe/Madrid) | Emit the text in force on this date. A fixed date keeps its own sync state. |
| `maxChunkChars` | integer, 500–20000 | `2000` | Articles longer than this are split by paragraphs, then by sentences. About 4 characters per token. |
| `syncId` | string, `A-Z a-z 0-9 _ -`, up to 40 | `default` | Names the sync state kept between runs. Use one per vector store. |
| `fullReload` | boolean | `false` | Emit every chunk again (and delete stale ones), e.g. after wiping your vector store. |

```json
{
  "laws": ["estatuto-trabajadores", "lopdgdd", "https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565"],
  "maxChunkChars": 2000,
  "syncId": "hr-assistant"
}
```

### Law aliases

Aliases are case-insensitive. For these laws `context_header` starts with the short name; for any other
law, with its official title.

| Alias | BOE id | Short name |
|---|---|---|
| `constitucion` | BOE-A-1978-31229 | Constitución Española |
| `codigo-civil` | BOE-A-1889-4763 | Código Civil |
| `codigo-penal` | BOE-A-1995-25444 | Código Penal |
| `estatuto-trabajadores` | BOE-A-2015-11430 | Estatuto de los Trabajadores |
| `lopdgdd` | BOE-A-2018-16673 | Ley Orgánica de Protección de Datos (LOPDGDD) |
| `ley-general-tributaria` | BOE-A-2003-23186 | Ley General Tributaria |
| `irpf` | BOE-A-2006-20764 | Ley del IRPF |
| `iva` | BOE-A-1992-28740 | Ley del IVA |
| `enjuiciamiento-civil` | BOE-A-2000-323 | Ley de Enjuiciamiento Civil |
| `enjuiciamiento-criminal` | BOE-A-1882-6036 | Ley de Enjuiciamiento Criminal |
| `sociedades-capital` | BOE-A-2010-10544 | Ley de Sociedades de Capital |
| `procedimiento-administrativo` | BOE-A-2015-10565 | Ley del Procedimiento Administrativo Común |
| `regimen-juridico-sector-publico` | BOE-A-2015-10566 | Ley de Régimen Jurídico del Sector Público |
| `seguridad-social` | BOE-A-2015-11724 | Ley General de la Seguridad Social |
| `arrendamientos-urbanos` | BOE-A-1994-26003 | Ley de Arrendamientos Urbanos |
| `concursal` | BOE-A-2020-4859 | Ley Concursal |
| `prevencion-riesgos-laborales` | BOE-A-1995-24292 | Ley de Prevención de Riesgos Laborales |
| `impuesto-sociedades` | BOE-A-2014-12328 | Ley del Impuesto sobre Sociedades |
| `contratos-sector-publico` | BOE-A-2017-12902 | Ley de Contratos del Sector Público |
| `codigo-comercio` | BOE-A-1885-6627 | Código de Comercio |

## Output

Each dataset item is one operation for your vector store: an `upsert` or a `delete`. The values below
are illustrative and `text` is shortened.

```json
{
  "op": "upsert",
  "chunk_id": "BOE-A-2015-11430:a4:0",
  "point_id": "d29a273d-7c0c-57d6-8e33-5a06157d5991",
  "law_id": "BOE-A-2015-11430",
  "law_title": "Real Decreto Legislativo 2/2015, de 23 de octubre, por el que se aprueba el texto refundido de la Ley del Estatuto de los Trabajadores",
  "block_id": "a4",
  "block_type": "precepto",
  "hierarchy": [
    "TEXTO REFUNDIDO DE LA LEY DEL ESTATUTO DE LOS TRABAJADORES",
    "TÍTULO I. De la relación individual de trabajo",
    "CAPÍTULO I. Disposiciones generales",
    "Sección 2.ª Derechos y deberes laborales básicos"
  ],
  "context_header": "[Estatuto de los Trabajadores > TEXTO REFUNDIDO DE LA LEY DEL ESTATUTO DE LOS TRABAJADORES > TÍTULO I. De la relación individual de trabajo > CAPÍTULO I. Disposiciones generales > Sección 2.ª Derechos y deberes laborales básicos > Artículo 4]",
  "text": "**Artículo 4. Derechos laborales.**\n\n1. Los trabajadores tienen como derechos básicos, con el contenido y alcance que para cada uno de los mismos disponga su específica normativa, los de:\n\na) Trabajo y libre elección de profesión u oficio.\n\nb) Libre sindicación.\n\n…",
  "chunk_index": 0,
  "chunk_count": 1,
  "version_norm_id": "BOE-A-2023-15135",
  "in_force_from": "2023-06-30",
  "in_force_until": null,
  "law_updated_at": "2026-10-29T08:21:56+00:00",
  "chars": 1981,
  "approx_tokens": 496,
  "content_hash": "sha256:2e2e600e5f2bee86ec88756332b2e8155a50bd76745c3d83954825f6097da6b2",
  "source_url": "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430#a4",
  "attribution": "Basado en datos de la Agencia Estatal Boletín Oficial del Estado",
  "disclaimer": "Texto consolidado de carácter meramente informativo, sin valor jurídico."
}
```

```json
{
  "op": "delete",
  "chunk_id": "BOE-A-2015-11430:a37:2",
  "point_id": "0683f0c4-1831-55d9-97f2-18e28da31d45",
  "law_id": "BOE-A-2015-11430",
  "reason": "superseded"
}
```

| Field | Meaning |
|---|---|
| `op` | `upsert`: write this chunk under its id, replacing any previous version. `delete`: remove the chunk with this id. |
| `chunk_id` | `{law_id}:{block_id}:{chunk_index}`. Stable across runs: a reform overwrites the same ids and deletes the surplus ones. Use it as the primary key in SQL stores. |
| `point_id` | UUID derived from `chunk_id` with a fixed namespace (Qdrant only accepts unsigned integers or UUIDs as point ids). Same `chunk_id`, same `point_id`, in every run. |
| `law_id`, `law_title` | BOE id and official title of the law. |
| `block_id`, `block_type` | BOE id and type of the block (article, disposition, preamble…) within the law, e.g. `a4` and `precepto`. Treat `block_id` as opaque. |
| `hierarchy` | Enclosing headings, outermost first. |
| `context_header` | Law name, headings and article title in one line. Kept apart from `text` so you decide whether to embed it; a common choice is to embed `context_header` + `text` and show `text`. |
| `text` | The chunk in Markdown. The article heading, in bold, opens its first chunk. |
| `chunk_index`, `chunk_count` | Position of the chunk within its article, and how many chunks the article has. |
| `version_norm_id` | BOE id of the norm that gave the article this wording. |
| `in_force_from` | Date this wording took effect. |
| `in_force_until` | Date a later-published wording replaces this one, if the source already has one (a reform with a deferred effective date, or any later reform when `asOfDate` is in the past); otherwise `null`. |
| `law_updated_at` | When the BOE last updated the consolidated text of the law, as of the run that last emitted this chunk. It is left out of `content_hash`, otherwise a reform of one article would re-emit every chunk of the law; for the law's current update date, read its most recent records. |
| `chars`, `approx_tokens` | Length of `text`, and tokens estimated as characters / 4. |
| `content_hash` | `sha256:` hash of the record without `op`, `content_hash` and `law_updated_at`. It changes whenever anything else in the record changes. |
| `source_url` | The article on boe.es. |
| `attribution`, `disclaimer` | Source attribution and the informative-only notice of the consolidated text (see Legal below). |
| `reason` | Deletes only: `superseded` or `repealed` (see How sync works above). |

## Load into a vector store

The Actor does not compute embeddings or write to your store: a short loader applies each run's records.
This one uses [`apify-client`](https://pypi.org/project/apify-client/) and
[`qdrant-client`](https://pypi.org/project/qdrant-client/) (`pip install apify-client qdrant-client`):

```python
from apify_client import ApifyClient
from qdrant_client import QdrantClient, models

apify = ApifyClient("<APIFY_TOKEN>")
qdrant = QdrantClient(url="http://localhost:6333")  # add api_key="..." for Qdrant Cloud
COLLECTION = "spanish-laws"  # create it first with your embedding's size and distance


def embed(text: str) -> list[float]:
    # Placeholder: call your own embedding model here.
    raise NotImplementedError


def apply_run(run_id: str, batch_size: int = 256) -> None:
    batch: list[models.PointStruct] = []
    for record in apify.run(run_id).dataset().iterate_items():
        if record["op"] == "delete":
            qdrant.delete(COLLECTION, points_selector=[record["point_id"]])
            continue
        vector = embed(f"{record['context_header']}\n\n{record['text']}")
        batch.append(models.PointStruct(id=record["point_id"], vector=vector, payload=record))
        if len(batch) == batch_size:
            qdrant.upsert(COLLECTION, points=batch)
            batch = []
    if batch:
        qdrant.upsert(COLLECTION, points=batch)
```

Call `apply_run` with the id of every run (shown in Apify Console and in API and webhook payloads), in
order and **whatever its final status**: a run that ends as failed
because one law failed has still delivered, and recorded as delivered, the records of the other laws.

pgvector works the same way with `chunk_id` as the primary key: `INSERT … ON CONFLICT (chunk_id) DO
UPDATE` for upserts and `DELETE … WHERE chunk_id = …` for deletes.

## Run summary

Each run writes an `OUTPUT` record to its default key-value store (values illustrative):

```json
{
  "as_of": "2026-11-03",
  "state": "hr-assistant",
  "laws": [
    {
      "law_id": "BOE-A-2015-11430",
      "status": "synced",
      "upserts": 3,
      "deletes": 1,
      "articles_charged": 0,
      "articles_left_for_later": 0,
      "chunks_in_force": 273
    },
    {
      "law_id": "BOE-A-2018-16673",
      "status": "failed",
      "error": "ReadTimeout('The read operation timed out')"
    }
  ]
}
```

- `as_of`: the date whose wording was used. `state`: the sync state used (the `syncId`, plus the date
  when `asOfDate` is set).
- Per law: `upserts` and `deletes` emitted, `articles_charged` (0 while the Actor is free),
  `articles_left_for_later` (articles that did not fit the spending limit) and `chunks_in_force` (the
  law's current chunk count).
- `status` is one of:

| Status | Meaning |
|---|---|
| `synced` | Everything that changed was emitted. |
| `stopped_by_spending_limit` | The spending limit was reached; run again to sync the rest. |
| `failed` | The law could not be fetched or processed (`error` says why). Its state is untouched and nothing was charged for it; the next run retries it. |

One failing law does not stop the others: they are synced, and the run then ends as failed, listing the
laws that failed.

## Limits and scope

- Only consolidated legislation from the BOE open data API (laws and regulations with a `BOE-A-…` id).
  No case law and no daily gazette.
- No embeddings are included: you embed the chunks with the model of your choice.
- One wording per article, the one in force at `asOfDate`; no version history.
- Headings (titles, chapters, sections) use their latest wording, whatever `asOfDate`.
- Laws removed from `laws` are not cleaned up automatically: their chunks stay in your store until you
  delete them yourself (every record carries `law_id`).

## Legal

- Basado en datos de la Agencia Estatal Boletín Oficial del Estado. Every upsert record carries this
  attribution and `law_updated_at`, the date of the last update of the consolidated text.
- The consolidated text is informative only and has no legal validity; the official text is the one
  published in the BOE. Every upsert record carries this notice in `disclaimer`.
- This Actor is not affiliated with or endorsed by the Agencia Estatal Boletín Oficial del Estado.
- Reuse conditions of the BOE data: https://www.boe.es/informacion/aviso_legal
- The Actor's source code is licensed under the MIT License.
