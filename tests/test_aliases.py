import pytest

from boe_rag_sync.aliases import LAWS, SHORT_NAMES, resolve
from boe_rag_sync.boe import LAW_ID


@pytest.mark.parametrize(
    "ref",
    [
        "BOE-A-2015-11430",
        "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430&p=20261023",
        "https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/BOE-A-2015-11430/texto",
        "estatuto-trabajadores",
        "  Estatuto-Trabajadores ",
    ],
)
def test_resolve_accepts_ids_urls_and_aliases(ref: str) -> None:
    assert resolve(ref) == "BOE-A-2015-11430"


def test_resolve_returns_only_the_id_never_the_raw_input() -> None:
    assert resolve("BOE-A-2015-11430/../metadatos") == "BOE-A-2015-11430"


def test_resolve_lists_the_aliases_on_a_typo() -> None:
    with pytest.raises(ValueError, match="estatuto-trabajadores"):
        resolve("estatuto")


def test_alias_table_is_consistent() -> None:
    ids = [law_id for law_id, _ in LAWS.values()]
    assert all(LAW_ID.fullmatch(law_id) for law_id in ids)
    assert len(set(ids)) == len(ids) == len(SHORT_NAMES)
    assert all(alias == alias.lower() and " " not in alias for alias in LAWS)
