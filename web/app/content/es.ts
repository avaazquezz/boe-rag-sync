import type { Copy } from "./types"
import { GITHUB_URL } from "./data"

export const es: Copy = {
  lang: "es",
  dateLocale: "es-ES",
  meta: {
    title: "Spanish Laws for RAG · La ley española, lista para RAG y al día",
    description:
      "Actor de Apify que convierte la legislación consolidada del BOE en fragmentos listos para RAG y mantiene tu base vectorial sincronizada con upserts y deletes.",
    ogLocale: "es_ES",
    ogImageAlt: "El titular «La ley española, artículo a artículo, en su redacción vigente» con un sello azul VIGENTE.",
  },
  skip: "Saltar al contenido",
  masthead: {
    home: "Spanish Laws for RAG, inicio",
    edition: "Año I.—Núm. 1",
    inForce: "Texto vigente a fecha de hoy",
    switchHref: "/en",
    switchText: "English",
    switchLabel: "Read this page in English",
  },
  hero: {
    title: "La ley española, artículo a artículo, en su redacción vigente.",
    lede: "Un Actor de Apify que convierte la legislación consolidada del BOE en fragmentos listos para RAG y mantiene tu base vectorial al día: en cada reforma, solo lo que cambió y los borrados.",
    cta: "Probar gratis en Apify",
    secondary: "Leer el código en GitHub",
    caption:
      "Así llega a tu índice el artículo 4 del Estatuto de los Trabajadores: un fragmento, con su ruta en la ley y la versión que está en vigor.",
    notePath: "ruta",
    noteChunk: ["1 fragmento", "496 tokens"],
    noteVersion: ["vigente desde", "el 30-06-2023", "Real Decreto-ley 5/2023"],
    stamp: "Vigente",
  },
  facts: {
    label: "Sumario",
    items: [
      "Publicado en Apify Store",
      "Código abierto, licencia MIT",
      "Probado con el XML real de cuatro leyes",
      "Revisado cada lunes contra la API del BOE",
    ],
  },
  pipeline: {
    title: "Diecisiete redacciones, un artículo vigente.",
    intro:
      "El artículo 37 del Estatuto de los Trabajadores llega en los datos abiertos con las diecisiete redacciones que ha tenido desde 2015 y las notas de cada reforma. Así se convierte en fragmentos:",
    epigraph: {
      quote: "Las leyes sólo se derogan por otras posteriores.",
      source: "Código Civil, art. 2.2. En la Gaceta de Madrid del 25 de julio de 1889 era el art. 5.º",
    },
    steps: [
      {
        head: "El XML.",
        body: "Cada redacción trae la norma que la dictó y sus fechas de publicación y de entrada en vigor.",
      },
      {
        head: "Fuera las notas.",
        body: "«Se modifica el apartado 6 por…», «Téngase en cuenta…». Las notas editoriales suelen citar la redacción anterior: se quitan antes de trocear para que el texto derogado no acabe en tu índice.",
      },
      {
        head: "Gana la ley posterior.",
        body: "Dos reformas del apartado 6 entraron en vigor el mismo día, el 23 de octubre de 2026: la Ley 4/2026 y el Real Decreto-ley 31/2026. Vale la publicada después, como manda el Código Civil y como resuelve boe.es.",
      },
      {
        head: "Nueve fragmentos.",
        body: "La redacción vigente se corta por párrafos hasta 2.000 caracteres. Cada fragmento lleva su ruta en la ley, un `chunk_id` estable y un `point_id` listo para Qdrant.",
      },
    ],
    figure: {
      label: "Del XML del artículo 37 a sus fragmentos",
      wordings: "redacciones",
      notes: "notas editoriales",
      chunks: "fragmentos",
      chars: "car.",
      tokens: "tokens",
      repealed: "No vigente",
      inForce: "Vigente",
    },
  },
  redline: {
    title: "En cada reforma, solo lo que cambió.",
    intro:
      "El 1 de abril de 2025 entró en vigor el Real Decreto-ley 11/2024, que reescribió la jubilación parcial en el artículo 12 del Estatuto. El artículo quedó más corto: pasó de ocho fragmentos a siete.",
    caption: "Art. 12.6, antes y después. En rojo, lo que se quita; en azul, lo que se añade.",
    ledgerCaption:
      "Lo que habría emitido una sincronización ese día, calculado con el código del Actor sobre el XML real:",
    unchanged: "261 fragmentos sin cambios: ni se emiten ni se cobran.",
    runsCaption: "En Apify, con el Estatuto entero y el mismo `syncId`:",
    firstRun: "upserts en la primera ejecución",
    secondRun: "operaciones en la segunda, sin reformas de por medio",
  },
  usage: {
    title: "Pruébalo con una petición.",
    intro:
      "Con tu token de Apify, una llamada ejecuta el Actor y devuelve los registros. Sin código: abre el Actor en la consola, deja el Estatuto que viene precargado y pulsa Start.",
    curlCaption: "Ejecutar y recibir los registros",
    recordCaption: "Cada registro es una operación para tu base vectorial",
    copy: "Copiar",
    copied: "Copiado",
    loader: "El loader para Qdrant y pgvector está en el README",
    loaderHref: `${GITHUB_URL}#load-into-a-vector-store`,
  },
  build: {
    title: "Hecho para mantenerse.",
    items: [
      {
        head: "Núcleo funcional.",
        body: "Solo la descarga y la cáscara de Apify hacen E/S; el parser, el troceado y el diff son funciones puras.",
      },
      {
        head: "Datos reales, sin red.",
        body: "Los tests corren sobre XML real recortado de cuatro leyes: Estatuto de los Trabajadores, Código Civil, Código Penal y Ley del IRPF.",
      },
      {
        head: "Verificado en cada commit.",
        body: "mypy en modo estricto, Ruff con todas las reglas y pytest, en pre-commit y en CI.",
      },
      {
        head: "Un canario cada lunes.",
        body: "Comprueba contra la API del BOE que los veinte alias siguen apuntando a leyes en vigor y que una ley real se sigue troceando bien.",
      },
      {
        head: "Decisiones por escrito.",
        body: "Cinco ADRs explican lo que es caro de cambiar: el manifiesto de sincronización, el contrato de los registros y por qué el hash no incluye la fecha de actualización.",
      },
    ],
    links: [
      { text: "Notas de diseño", href: `${GITHUB_URL}/blob/main/docs/design.md` },
      { text: "Decisiones (ADR)", href: `${GITHUB_URL}/tree/main/docs/adr` },
    ],
  },
  price: {
    head: "Precio.",
    body: "Gratis durante el lanzamiento: solo pagas el consumo de la plataforma Apify. Más adelante, un cargo por artículo sincronizado; los artículos sin cambios y los borrados no se cobran nunca.",
  },
  faq: {
    title: "Preguntas frecuentes",
    items: [
      {
        q: "¿El texto tiene valor jurídico?",
        a: "No. El texto consolidado es informativo; el oficial es el publicado en el BOE. Cada fragmento lleva ese aviso y la atribución de la fuente.",
      },
      {
        q: "¿Incluye embeddings?",
        a: "No: los calculas con el modelo que elijas. El Actor entrega texto, ruta y metadatos, y el loader del README los lleva a Qdrant o pgvector.",
      },
      {
        q: "¿Qué leyes puedo pedir?",
        a: "Cualquier norma consolidada con identificador `BOE-A-…`, por id o por su URL de boe.es, y veinte leyes frecuentes por alias: `constitucion`, `codigo-civil`, `irpf`…",
      },
      { q: "¿Y la jurisprudencia o el diario del BOE?", a: "Quedan fuera: solo legislación consolidada." },
      {
        q: "¿Y si vacío mi base vectorial?",
        a: "Ejecuta una vez con `fullReload`: vuelve a emitir todos los fragmentos vigentes y borra los obsoletos.",
      },
    ],
  },
  closing: { title: "Que tu asistente cite la ley que está en vigor hoy.", cta: "Probar gratis en Apify" },
  footer: {
    attribution: "Basado en datos de la Agencia Estatal Boletín Oficial del Estado.",
    noAffiliation:
      "Este proyecto no está afiliado a la Agencia Estatal Boletín Oficial del Estado ni cuenta con su respaldo.",
    disclaimer: "El texto consolidado es informativo y no tiene valor jurídico.",
    madeBy: "Hecho por",
    license: "Código abierto, licencia MIT",
    source: "Código fuente",
    colophon: "Compuesto en Ibarra Real Nova, revival de los tipos del Quijote de 1780, y Martian Mono.",
  },
}
