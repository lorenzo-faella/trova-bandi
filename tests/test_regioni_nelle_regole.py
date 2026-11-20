"""Le regioni scritte nelle regole devono essere quelle del questionario (pipeline.normalizza.REGIONI).

Le fonti scrivono "Trentino-Alto Adige" e "Valle d'Aosta", il questionario offre solo "Trentino-Alto Adige/Südtirol"
e "Valle d'Aosta/Vallée d'Aoste": una regola con il nome breve non sarebbe mai soddisfatta (decisioni 73 e 76).
"""
from pathlib import Path

import pytest
import yaml

from pipeline.normalizza import REGIONI

ROOT = Path(__file__).resolve().parent.parent
CARTELLE = ["data/regole_estratte", "data/regole_persone"]


def regioni_usate(nodo):
    if isinstance(nodo, dict):
        if nodo.get("campo") == "regione":
            v = nodo.get("valori", nodo.get("valore"))
            yield from (v if isinstance(v, list) else [v])
        for figlio in nodo.values():
            yield from regioni_usate(figlio)
    elif isinstance(nodo, list):
        for figlio in nodo:
            yield from regioni_usate(figlio)




@pytest.mark.parametrize("cartella", CARTELLE)
def test_le_regioni_delle_regole_sono_quelle_del_questionario(cartella):
    sbagliate = {}
    for f in (ROOT / cartella).rglob("*.yaml"):
        for r in regioni_usate(yaml.safe_load(f.read_text(encoding="utf-8"))):
            if r not in REGIONI:
                sbagliate.setdefault(str(f.relative_to(ROOT)), []).append(r)
    assert not sbagliate, sbagliate
