"""Eccezioni rare (`portata: rara`, decisione 52): "idoneo, salvo eccezioni" solo quando restano aperte soltanto loro."""
import pytest

from pipeline.citazioni import problemi
from pipeline.confronta import comportamento
from pipeline.motore import DA_VERIFICARE, IDONEO, IDONEO_SALVO, MANCANO_DATI, NON_IDONEO, valuta, verifica
from pipeline.regole import VALIDATORE

RARA = {"non_modellabile": "Chi ha anche contributi agricoli deve averli in minoranza.", "portata": "rara",
        "fonte": "scheda", "citazione": "purché prevalga la contribuzione non agricola"}
GENERALE = {"non_modellabile": "Cittadinanza: la scheda non la riporta.", "fonte": "scheda"}
ETA = {"campo": "eta", "operatore": ">=", "valore": 18, "fonte": "scheda", "citazione": "maggiorenni"}
TESTO = "Possono chiederlo i maggiorenni, purché prevalga la contribuzione non agricola."


def regola(*requisiti):
    return {"id": "prova", "titolo": "Prova", "link": None, "apertura": None, "chiusura": None,
            "fonte": "test", "pubblico": "persone", "requisiti": list(requisiti)}


def test_solo_eccezioni_rare_aperte_vuol_dire_idoneo_salvo_eccezioni():
    e = valuta(regola(ETA, RARA), {"eta": 30})
    assert e.stato == IDONEO_SALVO
    assert e.eccezioni == [RARA] and e.mancanti == [RARA]


@pytest.mark.parametrize("profilo, atteso", [
    ({"eta": 17}, NON_IDONEO),   # un requisito fallito vince sempre
    ({}, MANCANO_DATI),          # prima si chiede il dato che manca
])
def test_le_eccezioni_rare_non_cambiano_no_e_dati_mancanti(profilo, atteso):
    assert valuta(regola(ETA, RARA), profilo).stato == atteso


def test_basta_una_riserva_generale_per_restare_da_verificare():
    e = valuta(regola(ETA, RARA, GENERALE), {"eta": 30})
    assert e.stato == DA_VERIFICARE and e.eccezioni == []


def test_senza_portata_tutto_come_prima():
    senza = {k: v for k, v in RARA.items() if k != "portata"}
    assert valuta(regola(ETA, senza), {"eta": 30}).stato == DA_VERIFICARE


def test_rara_dentro_tutti_di_e_almeno_un_componente_si_presume():
    gruppo = {"tutti_di": [ETA, RARA], "fonte": "scheda"}
    assert valuta(regola(gruppo), {"eta": 30}).stato == IDONEO_SALVO
    figlio = {"almeno_un_componente": [{"campo": "eta", "operatore": "<", "valore": 18}, RARA], "fonte": "scheda"}
    e = valuta(regola(figlio), {"nucleo": [{"eta": 40}, {"eta": 5}]})
    assert e.stato == IDONEO_SALVO and e.eccezioni == [RARA]


def test_rara_dentro_almeno_uno_di_non_apre_la_via_alternativa():
    """Se la si presumesse vera, chiunque passerebbe per l'alternativa: un falso sì per tutti quelli che falliscono ETA."""
    alternativa = {"almeno_uno_di": [ETA, RARA], "fonte": "scheda"}
    assert verifica(alternativa, {"eta": 10}, presumi_rare=True) is None
    assert valuta(regola(alternativa), {"eta": 10}).stato == DA_VERIFICARE
    assert valuta(regola(alternativa), {"eta": 30}).stato == IDONEO  # la via principale basta, come prima


def test_schema_accetta_solo_rara():
    assert not list(VALIDATORE.iter_errors(regola(ETA, RARA)))
    assert list(VALIDATORE.iter_errors(regola(ETA, {**RARA, "portata": "frequente"})))
    assert list(VALIDATORE.iter_errors(regola({**ETA, "portata": "rara"})))  # solo sui non modellabili


def test_controllo_eccezione_rara_senza_citazione_o_in_alternativa():
    assert problemi(regola(ETA, RARA), TESTO) == []
    senza = {k: v for k, v in RARA.items() if k != "citazione"}
    assert any("deve avere la sua citazione" in p for p in problemi(regola(ETA, senza), TESTO))
    alternativa = {"almeno_uno_di": [ETA, RARA], "fonte": "scheda", "citazione": "maggiorenni"}
    assert any("dentro almeno_uno_di" in p for p in problemi(regola(alternativa), TESTO))


def test_confronto_conta_i_falsi_si_dovuti_alle_eccezioni_rare():
    """Un'eccezione segnata rara al posto di un requisito vero: il riferimento esclude, l'estrazione dice 'salvo eccezioni'."""
    riferimento = regola(ETA, {"campo": "disabile", "operatore": "vero", "fonte": "scheda", "citazione": "x"})
    estratta = regola(ETA, {**RARA, "non_modellabile": "Disabilità: manca il campo."})
    c = comportamento(riferimento, estratta, n=500)
    assert c["falsi_si_da_rare"] > 0 and c["falsi_si_da_rare"] <= c["falsi_si"]
    assert c["troppo_sicura"] == 0  # nessun caso in cui il riferimento sia meno sicuro
