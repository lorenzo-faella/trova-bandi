import copy

import jsonschema
import pytest

from pipeline.regole import VALIDATORE


def test_almeno_una_regola_per_bando_aperto(regole):
    assert len(regole) > 500
    assert len({r["id"] for r in regole}) == len(regole)


def test_ogni_regola_ha_la_tipologia(regole):
    # è il filtro che definisce il nostro pubblico: deve esserci sempre
    assert all(any(q["campo"] == "tipologia" for q in r["requisiti"]) for r in regole)


def test_elenco_di_soli_comuni_soppressi_non_perde_il_vincolo():
    from pipeline.regole import regola
    b = {"id": "1", "titolo": "t", "ente": None, "link": None, "apertura": None, "chiusura": None,
         "nazionale": False, "regioni": ["Lombardia"], "comuni": [], "comuni_non_riconosciuti": ["Cavallasca"],
         "tipologie": ["Impresa"], "dimensioni": [], "settori": [], "ambiti": [],
         "ateco": {"tutti": True, "codici": {}, "non_riconosciuti": []}}
    comune = [q for q in regola(b, "test")["requisiti"] if q["campo"] == "comune"]
    assert comune and comune[0]["incerto_fuori_elenco"]


def test_al_massimo_una_versione_ateco(regole):
    for r in regole:
        assert sum(q["campo"].startswith("ateco") for q in r["requisiti"]) <= 1


@pytest.mark.parametrize("guasto", [
    lambda r: r["requisiti"].append({"campo": "ateco_2025", "operatore": "in", "valori": ["56.10"], "fonte": "x"}),
    lambda r: r["requisiti"].append({"campo": "ateco_2025", "operatore": "prefisso", "valori": ["5610"], "fonte": "x"}),
    lambda r: r["requisiti"].append({"campo": "eta", "operatore": "in", "valori": ["30"], "fonte": "x"}),
    lambda r: r["requisiti"].append({"campo": "regione", "operatore": "in", "valori": [], "fonte": "x"}),
    lambda r: r.update(apertura="27/10/2026"),
])
def test_lo_schema_rifiuta_regole_sbagliate(regole, guasto):
    r = copy.deepcopy(regole[0])
    guasto(r)
    with pytest.raises(jsonschema.ValidationError):
        VALIDATORE.validate(r)
