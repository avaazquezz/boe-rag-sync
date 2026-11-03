"""Aliases and short names of the most used laws; any other law works by BOE id or URL."""

from .boe import LAW_ID

# alias -> (BOE id, short name used in context headers). Ids checked against the API on 2026-11-03;
# the weekly live canary (tests/test_live.py) checks them again.
LAWS: dict[str, tuple[str, str]] = {
    "constitucion": ("BOE-A-1978-31229", "Constitución Española"),
    "codigo-civil": ("BOE-A-1889-4763", "Código Civil"),
    "codigo-penal": ("BOE-A-1995-25444", "Código Penal"),
    "estatuto-trabajadores": ("BOE-A-2015-11430", "Estatuto de los Trabajadores"),
    "lopdgdd": ("BOE-A-2018-16673", "Ley Orgánica de Protección de Datos (LOPDGDD)"),
    "ley-general-tributaria": ("BOE-A-2003-23186", "Ley General Tributaria"),
    "irpf": ("BOE-A-2006-20764", "Ley del IRPF"),
    "iva": ("BOE-A-1992-28740", "Ley del IVA"),
    "enjuiciamiento-civil": ("BOE-A-2000-323", "Ley de Enjuiciamiento Civil"),
    "enjuiciamiento-criminal": ("BOE-A-1882-6036", "Ley de Enjuiciamiento Criminal"),
    "sociedades-capital": ("BOE-A-2010-10544", "Ley de Sociedades de Capital"),
    "procedimiento-administrativo": (
        "BOE-A-2015-10565",
        "Ley del Procedimiento Administrativo Común",
    ),
    "regimen-juridico-sector-publico": (
        "BOE-A-2015-10566",
        "Ley de Régimen Jurídico del Sector Público",
    ),
    "seguridad-social": ("BOE-A-2015-11724", "Ley General de la Seguridad Social"),
    "arrendamientos-urbanos": ("BOE-A-1994-26003", "Ley de Arrendamientos Urbanos"),
    "concursal": ("BOE-A-2020-4859", "Ley Concursal"),
    "prevencion-riesgos-laborales": ("BOE-A-1995-24292", "Ley de Prevención de Riesgos Laborales"),
    "impuesto-sociedades": ("BOE-A-2014-12328", "Ley del Impuesto sobre Sociedades"),
    "contratos-sector-publico": ("BOE-A-2017-12902", "Ley de Contratos del Sector Público"),
    "codigo-comercio": ("BOE-A-1885-6627", "Código de Comercio"),
}
SHORT_NAMES = dict(LAWS.values())


def resolve(ref: str) -> str:
    """The BOE id of an id, of any boe.es URL that contains one, or of an alias."""
    # Only the matched id is returned, never the raw input, so a crafted URL cannot reach the
    # API path.
    if found := LAW_ID.search(ref):
        return found.group()
    if (key := ref.strip().lower()) in LAWS:
        return LAWS[key][0]
    msg = (
        f"Unknown law {ref!r}: use a BOE id (BOE-A-YYYY-N), a boe.es URL "
        f"or one of {', '.join(LAWS)}"
    )
    raise ValueError(msg)
