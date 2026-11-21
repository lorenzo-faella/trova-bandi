"""Le regole dei bandi per imprese ed enti estratte dai documenti (decisione 87): schema e campi delle imprese.
Le citazioni si controllano con `python -m pipeline.estrai_imprese controlla`, che ha bisogno dei testi scaricati."""
from pathlib import Path

import yaml

from pipeline.regole import VALIDATORE

CARTELLA = Path(__file__).resolve().parent.parent / "data" / "regole_imprese_documenti"
CAMPI_IMPRESE = {"tipologia", "dimensione", "settore", "regione", "comune", "ambito", "ateco_2025"}


def campi(req):
    if "campo" in req:
        yield req["campo"]
    for q in req.get("almeno_uno_di", []) + req.get("tutti_di", []):
        yield from campi(q)


def test_regole_valide_e_solo_campi_delle_imprese():
    regole = [yaml.safe_load(f.read_text(encoding="utf-8")) for f in CARTELLA.rglob("*.yaml")]
    assert len(regole) > 100
    for r in regole:
        VALIDATORE.validate(r)
        assert r["pubblico"] == "imprese"
        assert {c for q in r["requisiti"] for c in campi(q)} <= CAMPI_IMPRESE, r["id"]


def test_la_demo_delle_imprese_le_legge():
    """La demo delle imprese le valuta insieme al portale; un bando locale ha sempre un vincolo di territorio, anche
    quando il testo non lo scrive (decisione 88)."""
    from pipeline.citazioni import nodi
    from web import domande as d
    regole, _ = d.ramo_imprese("2026-11-21")
    estratte = [r for r in regole if r["_origine"] == "estratta"]
    assert len(estratte) > 100
    for r in estratte:
        if d.territorio(r):
            assert any(n.get("campo") in ("regione", "comune") for q in r["requisiti"] for n in nodi(q)), r["id"]
    out = d.passo("imprese", {"tipologia": ["Impresa"], "regione": "Lombardia", "comune": "Bergamo"}, "2026-11-21")
    assert any(x["origine"] == "estratta" for x in out["risultati"])
