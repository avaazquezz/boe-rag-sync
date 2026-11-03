import dataclasses
import hashlib
import itertools
import json
import uuid
from datetime import date

import pytest

from boe_rag_sync.boe import Block, Law, Table, Version
from boe_rag_sync.chunking import (
    ATTRIBUTION,
    DISCLAIMER,
    NAMESPACE,
    build_records,
    split,
    version_at,
)

LAW_ID = "BOE-A-2015-11430"
LAW_TITLE = (
    "Real Decreto Legislativo 2/2015, texto refundido de la Ley del Estatuto de los Trabajadores"
)
HIERARCHY = (
    "TÍTULO I. De la relación individual de trabajo",
    "CAPÍTULO II. Contenido del contrato",
)

# Written for these tests in the style of the BOE consolidated text (not a verbatim copy): heading,
# numbered paragraphs, abbreviations, a quoted paragraph and a long sentence with no boundary.
ARTICLE = tuple(
    " ".join(paragraph.split())
    for paragraph in """
**Artículo 34. Jornada.**

1. La duración de la jornada de trabajo será la pactada en los convenios colectivos o contratos de
trabajo. La duración máxima de la jornada ordinaria de trabajo será de cuarenta horas semanales de
trabajo efectivo de promedio en cómputo anual. Mediante convenio colectivo o, en su defecto, por
acuerdo entre la empresa y los representantes de los trabajadores, se podrá establecer la
distribución irregular de la jornada a lo largo del año. Dicha distribución deberá respetar en todo
caso los periodos mínimos de descanso diario y semanal previstos en esta ley; el trabajador deberá
conocer con un preaviso mínimo de cinco días el día y la hora de la prestación de trabajo resultante
de aquella. La compensación de las diferencias, por exceso o por defecto, entre la jornada realizada
y la duración máxima de la jornada ordinaria de trabajo legal o pactada será exigible según lo
acordado en convenio colectivo o, a falta de previsión al respecto, por acuerdo entre la empresa y
los representantes de los trabajadores: en defecto de pacto, las diferencias derivadas de la
distribución irregular de la jornada deberán quedar compensadas en el plazo de doce meses desde que
se produzcan.

2. Entre el final de una jornada y el comienzo de la siguiente mediarán, como mínimo, doce horas. El
número de horas ordinarias de trabajo efectivo no podrá ser superior a nueve diarias, salvo que por
convenio colectivo o, en su defecto, acuerdo entre la empresa y los representantes de los
trabajadores, se establezca otra distribución del tiempo de trabajo diario, respetando en todo caso
el descanso entre jornadas. Los trabajadores menores de dieciocho años no podrán realizar más de
ocho horas diarias de trabajo efectivo, incluyendo, en su caso, el tiempo dedicado a la formación y,
si trabajasen para varios empleadores, las horas realizadas con cada uno de ellos.

3. Siempre que la duración de la jornada diaria continuada exceda de seis horas, deberá establecerse
un periodo de descanso durante la misma de duración no inferior a quince minutos. Este periodo de
descanso se considerará tiempo de trabajo efectivo cuando así esté establecido o se establezca por
convenio colectivo o contrato de trabajo, conforme al art. 37 y al apdo. 2 del art. 38 de esta ley.
En el caso de los trabajadores menores de dieciocho años, el periodo de descanso tendrá una duración
mínima de treinta minutos, y deberá establecerse siempre que la duración de la jornada diaria
continuada exceda de cuatro horas y media. Véanse los arts. 23 y ss. del presente texto, así como el
núm. 3 de la disposición adicional segunda, etc. Todo ello sin perjuicio de lo previsto en la
normativa de prevención de riesgos laborales.

> Uno. Se modifica el apartado 4, que queda redactado como sigue: «4. El tiempo de trabajo se
computará de modo que tanto al comienzo como al final de la jornada diaria el trabajador se
encuentre en su puesto de trabajo.» Dos. Se suprime el apartado 5.

4. Las personas trabajadoras tienen derecho a solicitar las adaptaciones de la duración y
distribución de la jornada de trabajo, en la ordenación del tiempo de trabajo y en la forma de
prestación, incluida la prestación de su trabajo a distancia, para hacer efectivo su derecho a la
conciliación de la vida familiar y laboral, adaptaciones que deberán ser razonables y proporcionadas
en relación con las necesidades de la persona trabajadora y con las necesidades organizativas o
productivas de la empresa, y que podrán referirse, entre otras, a la reordenación de los turnos, a
la flexibilidad de entrada y salida, a la jornada continuada o a la concentración del tiempo de
trabajo en determinados días de la semana, siempre que ello no impida el normal funcionamiento del
servicio ni perjudique los derechos de otras personas trabajadoras que hubieran solicitado con
anterioridad adaptaciones similares por motivos equivalentes.

5. El Gobierno, a propuesta del Ministerio de Trabajo y Economía Social y previa consulta a las
organizaciones sindicales y empresariales más representativas, podrá establecer ampliaciones o
limitaciones en la ordenación y duración de la jornada de trabajo y de los descansos para aquellos
sectores y trabajos que por sus peculiaridades así lo requieran.
""".strip().split("\n\n")
)


def version(
    day: date, *content: str | Table, norm_id: str = LAW_ID, repealed: bool = False
) -> Version:
    return Version(
        norm_id=norm_id, published=day, in_force_from=day, content=content, repealed=repealed
    )


def block(
    *versions: Version,
    block_id: str = "a4",
    title: str = "Artículo 4",
    hierarchy: tuple[str, ...] = HIERARCHY,
) -> Block:
    return Block(id=block_id, type="precepto", title=title, hierarchy=hierarchy, versions=versions)


def law(*blocks: Block, updated_at: str = "20261023", repealed: bool = False) -> Law:
    return Law(id=LAW_ID, title=LAW_TITLE, updated_at=updated_at, repealed=repealed, blocks=blocks)


def normalized(texts: list[str]) -> str:
    return " ".join(" ".join(texts).split())


# version_at


def test_version_at_returns_none_before_the_first_version() -> None:
    a4 = block(version(date(2015, 11, 13)))
    assert version_at(a4, date(2015, 11, 12)) is None


def test_version_at_switches_on_the_exact_entry_into_force_date() -> None:
    a4 = block(version(date(2015, 11, 13), norm_id="old"), version(date(2023, 3, 2), norm_id="new"))
    assert version_at(a4, date(2023, 3, 1)) == a4.versions[0]
    assert version_at(a4, date(2023, 3, 2)) == a4.versions[1]
    assert version_at(a4, date(2026, 11, 3)) == a4.versions[1]


def test_version_at_breaks_date_ties_by_document_order() -> None:
    day = date(2026, 10, 23)
    a37 = block(version(day, norm_id="first"), version(day, norm_id="second"))
    assert version_at(a37, day) == a37.versions[1]


# split


def test_split_rejects_a_non_positive_limit() -> None:
    with pytest.raises(ValueError, match="max_chars"):
        split(["Texto."], 0)


def test_split_keeps_content_that_fits_in_one_chunk_with_tables_as_markdown() -> None:
    table = Table(header=("Grupo", "Cuantía"), rows=(("1", "100"), ("2", "200")))
    chunks = split(["**Artículo 1. Ámbito.**", "1. Texto breve.", table], 2000)
    assert chunks == [
        (
            "**Artículo 1. Ámbito.**\n\n1. Texto breve.\n\n"
            "| Grupo | Cuantía |\n| --- | --- |\n| 1 | 100 |\n| 2 | 200 |"
        )
    ]


def test_split_renders_tables_escaping_pipes_and_padding_short_rows() -> None:
    table = Table(header=("Concepto",), rows=(("a|b", "c"),))
    assert split([table], 100) == ["| Concepto |  |\n| --- | --- |\n| a\\|b | c |"]


def test_split_never_produces_empty_chunks() -> None:
    assert split(["", " "], 10) == []
    assert split(["", "Texto.", ""], 100) == ["Texto."]


def test_split_packs_paragraphs_greedily_up_to_the_limit() -> None:
    a, b, c = "A" * 40, "B" * 40, "C" * 40
    assert split([a, b, c], 82) == [f"{a}\n\n{b}", c]
    assert split([a, b, c], 81) == [a, b, c]


def test_split_breaks_an_oversize_paragraph_into_sentences() -> None:
    heading = "**Artículo 4. Derechos laborales.**"
    s1 = "1. Los trabajadores tienen como derechos básicos el trabajo y la libre elección."
    s2 = "Tendrán derecho a la ocupación efectiva."
    s3 = "Y a la promoción profesional."
    chunks = split([heading, f"{s1} {s2} {s3}"], len(heading) + 2 + len(s1))
    # The heading stays with the first sentence, the enumerator "1." is not a sentence of its own,
    # and the remaining sentences are packed together joined by a single space.
    assert chunks == [f"{heading}\n\n{s1}", f"{s2} {s3}"]


def test_split_never_leaves_the_article_heading_alone() -> None:
    # The paragraph fits alone but not after the heading: kept whole, the first chunk would be
    # just the heading, so it is split and its first sentence joins the heading.
    heading = "**Artículo 75. Rendimientos del capital mobiliario.**"
    s1 = "1. Estarán sujetos a retención los rendimientos del capital mobiliario."
    s2 = "Se aplicará el tipo general salvo en los supuestos previstos reglamentariamente."
    paragraph = f"{s1} {s2}"
    chunks = split([heading, paragraph], len(paragraph))
    assert chunks == [f"{heading}\n\n{s1}", s2]


def test_split_does_not_cut_after_a_paragraph_enumerator() -> None:
    before = "Texto previo."
    s1 = "1. Los trabajadores tienen derecho al descanso semanal."
    s2 = "El empresario lo respetará."
    assert split([before, f"{s1} {s2}"], len(s1)) == [before, s1, s2]


@pytest.mark.parametrize("end", [".", ";", ":"])
@pytest.mark.parametrize("opener", ["Los", "Él", "2", "«Cita»", '"Cita"', "(Véase)", "¿Cuándo?"])
def test_split_cuts_sentences_before_every_opener(end: str, opener: str) -> None:
    first = f"Regla general aplicable{end}"
    second = f"{opener} sigue la siguiente frase de la ley."
    assert split([f"{first} {second}"], len(second)) == [first, second]


def test_split_does_not_cut_before_a_lowercase_word() -> None:
    first = "Son derechos básicos:"
    second = "a) el trabajo y la libre elección de profesión."
    assert split([f"{first} {second}"], len(second))[0].startswith(f"{first} a)")


@pytest.mark.parametrize(
    "phrase",
    [
        "el art. 4",
        "el Art. 4",
        "los arts. 4 y 5",
        "el núm. 3",
        "el apdo. 2",
        "el aptdo. 2",
        "el párr. 2",
        "la pág. 7",
        "D. Juan",
        "Dña. María",
        "el Sr. Pérez",
        "la Sra. Gómez",
        "salarios, etc. Todo",
        "vid. Anexo",
        "cfr. Anexo",
        "los arts. 4 y ss. Del",
        "J. Pérez",
    ],
)
def test_split_never_cuts_after_an_abbreviation(phrase: str) -> None:
    first = "Regla general."
    second = f"Lo dispone {phrase} de la presente ley con carácter general."
    # Cutting after the abbreviation would let its first half join `first` in one chunk.
    assert split([f"{first} {second}"], len(second)) == [first, second]


def test_split_hard_splits_a_giant_sentence_at_whitespace() -> None:
    sentence = " ".join(f"palabra{i}" for i in range(60))
    chunks = split([sentence], 50)
    assert " ".join(chunks) == sentence
    assert all(len(c) <= 50 for c in chunks)
    # Greedy: the next word would not have fitted in the previous chunk.
    assert all(len(c) + 1 + len(n.split()[0]) > 50 for c, n in itertools.pairwise(chunks))


def test_split_slices_only_a_token_longer_than_the_limit() -> None:
    assert split(["texto " + "x" * 120 + " fin"], 50) == [
        "texto",
        "x" * 50,
        "x" * 50,
        "x" * 20 + " fin",
    ]


def test_split_cuts_an_oversize_table_by_rows_repeating_the_header() -> None:
    table = Table(header=("Grupo", "Euros"), rows=(("1", "100"), ("2", "200"), ("3", "300")))
    head = "| Grupo | Euros |\n| --- | --- |"
    assert split([table], 55) == [f"{head}\n| 1 | 100 |\n| 2 | 200 |", f"{head}\n| 3 | 300 |"]


def test_split_keeps_every_table_row_once_and_in_order() -> None:
    rows = tuple((f"Grupo {i}", f"{i * 1000} euros") for i in range(50))
    table = Table(header=("Grupo profesional", "Salario base"), rows=rows)
    head = "| Grupo profesional | Salario base |\n| --- | --- |"
    chunks = split(["Texto previo.", table, "Texto posterior."], 200)
    assert all(len(c) <= 200 for c in chunks)
    tables = [part for c in chunks for part in c.split("\n\n") if part.startswith("|")]
    assert all(t.startswith(head + "\n") for t in tables)
    found = [line for t in tables for line in t.removeprefix(head + "\n").split("\n")]
    assert found == [f"| Grupo {i} | {i * 1000} euros |" for i in range(50)]


def test_split_gives_an_oversize_row_its_own_chunk() -> None:
    long_cell = "importe " * 10
    table = Table(
        header=("Concepto", "Importe"), rows=(("Salario", "1"), (long_cell, "2"), ("Plus", "3"))
    )
    head = "| Concepto | Importe |\n| --- | --- |"
    chunks = split([table], 60)
    assert chunks == [
        f"{head}\n| Salario | 1 |",
        f"{head}\n| {long_cell} | 2 |",
        f"{head}\n| Plus | 3 |",
    ]
    assert [len(c) > 60 for c in chunks] == [False, True, False]


def test_split_preserves_text_for_every_limit() -> None:
    expected = normalized(list(ARTICLE))
    for max_chars in range(80, 2001):
        chunks = split(ARTICLE, max_chars)
        assert normalized(chunks) == expected, max_chars
        assert all(0 < len(c) <= max_chars for c in chunks), max_chars


# build_records


def test_build_records_emits_the_full_record_contract() -> None:
    a4 = block(
        version(date(2015, 11, 13), "**Artículo 4. Derechos laborales.**", "1. Texto."),
        version(date(2023, 3, 2), "Texto reformado.", norm_id="BOE-A-2023-5366"),
    )
    [record] = build_records(law(a4), date(2020, 1, 1), 2000)
    expected = {
        "chunk_id": f"{LAW_ID}:a4:0",
        "point_id": "d29a273d-7c0c-57d6-8e33-5a06157d5991",
        "law_id": LAW_ID,
        "law_title": LAW_TITLE,
        "block_id": "a4",
        "block_type": "precepto",
        "hierarchy": list(HIERARCHY),
        "context_header": f"[{LAW_TITLE} > {HIERARCHY[0]} > {HIERARCHY[1]} > Artículo 4]",
        "text": "**Artículo 4. Derechos laborales.**\n\n1. Texto.",
        "chunk_index": 0,
        "chunk_count": 1,
        "version_norm_id": LAW_ID,
        "in_force_from": "2015-11-13",
        "in_force_until": "2023-03-02",
        "law_updated_at": "20261023",
        "chars": 46,
        "approx_tokens": 12,
        "source_url": f"https://www.boe.es/buscar/act.php?id={LAW_ID}#a4",
        "attribution": ATTRIBUTION,
        "disclaimer": DISCLAIMER,
    }
    hashed = {k: v for k, v in expected.items() if k != "law_updated_at"}
    canonical = json.dumps(hashed, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    assert record == {
        **expected,
        "content_hash": f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}",
    }
    assert json.loads(json.dumps(record)) == record


def test_build_records_numbers_chunks_with_deterministic_ids() -> None:
    a34 = block(version(date(2015, 11, 13), *ARTICLE), block_id="a34")
    records = build_records(law(a34), date(2026, 11, 3), 500)
    count = len(records)
    assert count > 1
    assert [r["chunk_index"] for r in records] == list(range(count))
    assert {r["chunk_count"] for r in records} == {count}
    assert [r["chunk_id"] for r in records] == [f"{LAW_ID}:a34:{i}" for i in range(count)]
    assert [r["point_id"] for r in records] == [
        str(uuid.uuid5(NAMESPACE, f"{LAW_ID}:a34:{i}")) for i in range(count)
    ]
    assert build_records(law(a34), date(2026, 11, 3), 500) == records


@pytest.mark.parametrize(
    ("hierarchy", "title", "expected"),
    [
        (
            ("TÍTULO I", "CAPÍTULO II"),
            "Artículo 4",
            f"[{LAW_TITLE} > TÍTULO I > CAPÍTULO II > Artículo 4]",
        ),
        ((), "Artículo 1", f"[{LAW_TITLE} > Artículo 1]"),
        (("TÍTULO PRELIMINAR",), "", f"[{LAW_TITLE} > TÍTULO PRELIMINAR]"),
        ((), "", f"[{LAW_TITLE}]"),
    ],
)
def test_build_records_context_header(
    hierarchy: tuple[str, ...], title: str, expected: str
) -> None:
    b = block(version(date(2015, 11, 13), "Texto."), title=title, hierarchy=hierarchy)
    [record] = build_records(law(b), date(2026, 11, 3), 2000)
    assert record["context_header"] == expected


def test_build_records_skips_blocks_without_text_in_force() -> None:
    blocks = (
        block(version(date(2015, 11, 13), "Vigente."), block_id="a1"),
        block(version(date(2030, 1, 1), "Futuro."), block_id="a2"),
        block(
            version(date(2015, 11, 13), "Antes de derogar."),
            version(date(2020, 1, 1), "(Derogado)", repealed=True),
            block_id="a3",
        ),
        block(version(date(2015, 11, 13)), block_id="a4"),
    )
    assert [r["block_id"] for r in build_records(law(*blocks), date(2026, 11, 3), 2000)] == ["a1"]
    assert [r["block_id"] for r in build_records(law(*blocks), date(2019, 1, 1), 2000)] == [
        "a1",
        "a3",
    ]


def test_build_records_returns_nothing_for_a_repealed_law() -> None:
    a1 = block(version(date(2015, 11, 13), "Texto."))
    assert build_records(law(a1, repealed=True), date(2026, 11, 3), 2000) == []


def test_build_records_in_force_until_is_the_next_later_version() -> None:
    a4 = block(
        version(date(2015, 11, 13), "Uno."),
        version(date(2023, 3, 2), "Dos."),
        version(date(2023, 3, 2), "Dos bis."),
        version(date(2024, 1, 1), "Tres."),
    )

    def until(day: date) -> str | None:
        return build_records(law(a4), day, 2000)[0]["in_force_until"]

    assert until(date(2020, 1, 1)) == "2023-03-02"
    assert until(date(2023, 3, 2)) == "2024-01-01"
    assert until(date(2026, 11, 3)) is None


def test_content_hash_ignores_law_updated_at_but_tracks_text() -> None:
    a4 = block(version(date(2015, 11, 13), "Texto."))
    [base] = build_records(law(a4), date(2026, 11, 3), 2000)
    [again] = build_records(law(a4), date(2026, 11, 3), 2000)
    [reformed_law] = build_records(law(a4, updated_at="20261103"), date(2026, 11, 3), 2000)
    changed = dataclasses.replace(a4, versions=(version(date(2015, 11, 13), "Texto nuevo."),))
    [changed_text] = build_records(law(changed), date(2026, 11, 3), 2000)
    assert again["content_hash"] == base["content_hash"]
    assert reformed_law["law_updated_at"] != base["law_updated_at"]
    assert reformed_law["content_hash"] == base["content_hash"]
    assert changed_text["content_hash"] != base["content_hash"]
