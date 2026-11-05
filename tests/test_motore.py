"""Bandi inventati con l'esito scritto a mano: è qui che si verifica la logica, non sui dati reali."""
import pytest

from pipeline.motore import IDONEO, MANCANO_DATI, NON_IDONEO, QUASI, aperta, valuta, verifica


def req(campo, operatore, valori, **extra):
    return {"campo": campo, "operatore": operatore, "valori": valori, "fonte": "test", **extra}


def bando(*requisiti, apertura=None, chiusura=None):
    return {"id": "t", "titolo": "t", "link": None, "apertura": apertura, "chiusura": chiusura,
            "fonte": "test", "requisiti": list(requisiti)}


LOMBARDIA = req("regione", "in", ["Lombardia"])
PMI = req("dimensione", "in", ["Microimpresa", "Piccola Impresa", "Media Impresa"])
GIOVANI = req("tipologia", "interseca", ["Impresa - prevalenza giovanile"])
RISTORAZIONE = req("ateco_2025", "prefisso", ["56.1", "56.3"])

PIZZERIA = {"regione": "Lombardia", "dimensione": "Microimpresa", "tipologia": ["Impresa"], "ateco_2025": "56.11"}


@pytest.mark.parametrize("codice, atteso", [
    ("56.11", True), ("56.30", True), ("56.21", False), ("47.11", False),
    ("56", None),  # troppo generico per dire se è nel gruppo 56.1
])
def test_prefisso_ateco(codice, atteso):
    assert verifica(RISTORAZIONE, {"ateco_2025": codice}) is atteso


def test_prefisso_non_confonde_codici_simili():
    assert verifica(req("ateco_2025", "prefisso", ["01.1"]), {"ateco_2025": "10.11"}) is False


def test_interseca():
    assert verifica(GIOVANI, {"tipologia": ["Impresa", "Impresa - prevalenza giovanile"]}) is True
    assert verifica(GIOVANI, {"tipologia": ["Impresa"]}) is False
    assert verifica(GIOVANI, {"tipologia": []}) is False


def test_comune_in_elenco_con_comuni_soppressi():
    r = req("comune", "in", ["Rimini"], incerto_fuori_elenco=True)
    assert verifica(r, {"comune": "Rimini"}) is True
    assert verifica(r, {"comune": "Cesena"}) is None
    assert verifica(req("comune", "in", ["Rimini"]), {"comune": "Cesena"}) is False


def test_idoneo():
    assert valuta(bando(LOMBARDIA, PMI, RISTORAZIONE), PIZZERIA).stato == IDONEO


def test_dato_mancante():
    e = valuta(bando(LOMBARDIA, RISTORAZIONE), {"regione": "Lombardia"})
    assert e.stato == MANCANO_DATI and e.mancanti == [RISTORAZIONE]


def test_un_no_basta_anche_con_dati_mancanti():
    assert valuta(bando(LOMBARDIA, RISTORAZIONE), {"regione": "Sicilia"}).stato == NON_IDONEO


def test_quasi_idoneo_solo_su_requisiti_modificabili():
    e = valuta(bando(LOMBARDIA, PMI, GIOVANI), PIZZERIA)
    assert e.stato == QUASI and e.falliti == [GIOVANI]
    # la sede non si cambia: un bando di un'altra regione non è "quasi"
    assert valuta(bando(LOMBARDIA, PMI), {**PIZZERIA, "regione": "Sicilia"}).stato == NON_IDONEO


def test_quasi_richiede_che_il_resto_sia_verificato():
    assert valuta(bando(LOMBARDIA, GIOVANI), {"tipologia": ["Impresa"]}).stato == NON_IDONEO


def test_bando_senza_requisiti():
    assert valuta(bando(), {}).stato == IDONEO


def test_aperta():
    assert aperta(bando(apertura="2026-10-27", chiusura="2026-10-27"), "2026-10-27")
    assert not aperta(bando(chiusura="2026-10-26"), "2026-10-27")
    assert aperta(bando(), "2026-10-27")
