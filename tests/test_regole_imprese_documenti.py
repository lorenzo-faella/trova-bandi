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
    """Le regole aggiunte restano; nessun requisito viene fabbricato dalla provenienza geografica. Unica aggiunta: il
    comune per i bandi delle Camere di commercio il cui testo nomina già la provincia (decisione 109)."""
    from web import domande as d
    originali = {r['id']: r for r in d.leggi_cartella(CARTELLA, 'estratta')}
    caricate = d.regole_imprese_documenti()
    assert len(caricate) == len(list(CARTELLA.glob("*.yaml")))
    for r in caricate:
        prima = originali[r['id']]['requisiti']
        assert r['requisiti'][:len(prima)] == prima
        assert all(q['campo'] == 'comune' and q['fonte'].startswith('ente del bando') for q in r['requisiti'][len(prima):])
    out = d.passo("imprese", {"tipologia": ["Impresa"], "regione": "Lombardia", "comune": "Bergamo"}, "2026-11-21")
    assert any(x["origine"] == "estratta" for x in out["risultati"])
