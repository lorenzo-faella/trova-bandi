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


def test_camera_di_commercio_vale_per_la_sua_provincia():
    from pipeline.regole import province_della_camera as province
    lombardia = ["Lombardia"]
    assert province("Camera di Commercio, Industria, Artigianato e Agricoltura di Bergamo", lombardia) == ["Bergamo"]
    assert province("Camera di Commercio Metropolitana di Milano-Monza-Brianza-Lodi", lombardia) == \
        ["Lodi", "Milano", "Monza e della Brianza"]
    assert province("Camera di Commercio della Maremma e del Tirreno", ["Toscana"]) == ["Grosseto", "Livorno"]
    assert province("Camera di Commercio Industria Artigianato e Agricoltura Venezia Giulia", ["Friuli-Venezia Giulia"]) == \
        ["Gorizia", "Trieste"]
    # unione regionale, camera regionale o ente che non è una camera: nessuna provincia, basta la regione
    assert province("Unione Regionale Delle Camere di Commercio Industria Artigianato Agricoltura della Lombardia", lombardia) == []
    assert province("Camera di Commercio Industria Artigianato e Agricoltura della Basilicata", ["Basilicata"]) == []
    assert province("Regione Lombardia", lombardia) == []


def test_regola_della_camera_ha_i_comuni_della_provincia():
    from pipeline.regole import regola
    b = {"id": "1", "titolo": "Voucher", "ente": "Camera di Commercio, Industria, Artigianato e Agricoltura di Brescia",
         "link": None, "apertura": None, "chiusura": None, "nazionale": False, "regioni": ["Lombardia"], "comuni": [],
         "comuni_non_riconosciuti": [], "tipologie": ["Impresa"], "dimensioni": [], "settori": [],
         "ateco": {"codici": {}, "non_riconosciuti": []}, "ambiti": []}
    r = regola(b, "export.json")
    VALIDATORE.validate(r)
    comune = next(q for q in r["requisiti"] if q["campo"] == "comune")
    assert "Brescia" in comune["valori"] and "Bergamo" not in comune["valori"] and len(comune["valori"]) > 200
    assert "Soggetto_Concedente" in comune["fonte"]


def test_condizioni_trovate_nella_revisione_a_mano():
    """Fondo Salvaguardia e CLLD Dolomiti Live (revisione a mano delle imprese, decisione 109): il portale non scrive la
    condizione principale. La demo la aggiunge come requisito da verificare a mano, quindi il bando resta "da
    verificare" invece di risultare compatibile a ogni impresa. I file generati restano con i soli campi del portale."""
    from pipeline.motore import DA_VERIFICARE, IDONEO, valuta
    from pipeline.regole import CONDIZIONI_RIVISTE, regola
    from web.domande import con_condizioni_riviste
    b = {"id": "90", "titolo": "Fondo Salvaguardia imprese", "ente": "Ministero delle Imprese e del Made in Italy",
         "link": None, "apertura": None, "chiusura": None, "nazionale": True, "regioni": [], "comuni": [],
         "comuni_non_riconosciuti": [], "tipologie": ["Impresa"], "dimensioni": [], "settori": [],
         "ateco": {"codici": {}, "non_riconosciuti": []}, "ambiti": []}
    generata = regola(b, "export.json")
    assert all("campo" in q for q in generata["requisiti"])
    assert valuta(generata, {"tipologia": ["Impresa"]}).stato == IDONEO
    r = con_condizioni_riviste(dict(generata))
    VALIDATORE.validate(r)
    assert r["requisiti"][-1] == CONDIZIONI_RIVISTE["90"][0] and r["requisiti"][-1]["citazione"]
    assert valuta(r, {"tipologia": ["Impresa"]}).stato == DA_VERIFICARE
    assert len(generata["requisiti"]) == len(r["requisiti"]) - 1  # la regola generata non cambia
    assert con_condizioni_riviste(dict(generata, id="91"))["requisiti"] == generata["requisiti"]
    assert set(CONDIZIONI_RIVISTE) == {"90", "813"}
