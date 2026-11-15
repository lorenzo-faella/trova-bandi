"""Demo web: domande delle persone, esiti leggibili e API, senza rete (TestClient chiama l'app in memoria)."""
import datetime as dt

import pytest

from pipeline.motore import DA_VERIFICARE, IDONEO, IDONEO_SALVO, MANCANO_DATI, NON_IDONEO, NON_SO, valuta_tutte
from web import domande as d

GIORNO = "2026-11-08"
PERSONA = {"cittadinanza": "italiana", "residente_italia": True, "nucleo": [{"eta": 34}, {"eta": 1}],
           "condizione_lavorativa": "disoccupato", "isee": 9000, "ultimo_lavoro_subordinato": True,
           "causa_fine_lavoro": "licenziamento", "giorni_da_cessazione_lavoro": 30, "settimane_contributi_4_anni": 100,
           "data_evento_figlio": "2026-09-20", "anni_residenza_italia": 34, "anni_residenza_continuativa_italia": 34,
           "patrimonio_immobiliare": 0, "veicoli_esclusi": False, "permesso_casi_speciali": False,
           "lavora_in_italia": False, "soggetto_irpef_italia": True}
COMPONENTI = {"disabile": False, "svantaggio_certificato": False, "reddito_annuo": 0, "attivita": "nessuna"}
MINORE = {"figlio", "figlio_a_carico"}  # valgono sì per i minori di PERSONA


def rispondi_a_tutto(ramo, risposte, componenti=None, massimo=40):
    """Simula chi usa la demo: risponde a ogni domanda finché il questionario non si ferma."""
    p, chieste = {}, []
    for _ in range(massimo):
        out = d.passo(ramo, p, GIORNO)
        q = out["domanda"]
        if q is None:
            return out, chieste, p
        chieste.append(q["campo"])
        if q.get("per_componente"):
            campo = q["campo"].split(".")[1]
            for c in q["componenti"]:
                p["nucleo"][c["indice"]][campo] = componenti(campo, p["nucleo"][c["indice"]])
        else:
            p[q["campo"]] = risposte.get(q["campo"], NON_SO)
    raise AssertionError(f"il questionario non si ferma: {chieste}")


def componente(campo, c):
    return c["eta"] < 18 if campo in MINORE else COMPONENTI[campo]


def test_persona_completa_arriva_agli_esiti_attesi():
    out, chieste, _ = rispondi_a_tutto("persone", PERSONA, componente)
    esiti = {r["id"]: r["stato"] for r in out["risultati"]}
    assert esiti == {"inps-assegno-unico": IDONEO, "inps-naspi": IDONEO_SALVO, "inps-adi": DA_VERIFICARE,
                     "inps-assegno-maternita-stato": DA_VERIFICARE, "inps-bonus-nuovi-nati": DA_VERIFICARE}
    assert len(chieste) == len(set(chieste))  # nessuna domanda ripetuta
    assert "regione" not in chieste  # nessuna delle 5 regole la usa: non si chiede


def test_ogni_domanda_del_file_si_puo_mostrare():
    for chiave in d.domande():
        q = d.domanda_persone(chiave, 1, {"nucleo": [{"eta": 40}], "regione": "Lombardia"})
        assert q["testo"] and q["tipo"] in {"scelta", "comune", "si_no", "numero", "data", "nucleo"}, chiave
        if q["tipo"] == "scelta":
            assert q["opzioni"], chiave
            assert "_" not in " ".join(o["etichetta"] for o in q["opzioni"]), chiave  # niente codici grezzi


def test_ogni_campo_delle_persone_ha_un_nome_leggibile():
    import json
    defs = json.loads((d.ROOT / "schema" / "regola.schema.json").read_text(encoding="utf-8"))["$defs"]
    campi = {c for k in ("elenco", "numero", "booleano") for c in defs[k]["properties"]["campo"]["enum"]}
    imprese = {"tipologia", "dimensione", "regione", "comune", "settore", "ateco_2025", "ateco_2007", "ambito"}
    assert not {c for c in campi - imprese if c not in d.NOMI}


def test_solo_se_apre_chiude_e_chiede_prima_la_domanda_da_cui_dipende():
    assert d.da_porre("crediti_conseguiti", {}) == "iscrizione"  # prima se è iscritto
    assert d.da_porre("crediti_conseguiti", {"iscrizione": "universita"}) == "anno_di_corso"
    assert d.da_porre("crediti_conseguiti", {"iscrizione": "universita", "anno_di_corso": 2}) == "crediti_conseguiti"
    assert d.da_porre("crediti_conseguiti", {"iscrizione": "universita", "anno_di_corso": 1}) is None
    assert d.da_porre("crediti_conseguiti", {"iscrizione": "nessuna"}) is None
    assert d.da_porre("canone_annuo", {"abitazione": NON_SO}) is None  # "non lo so" non apre i dettagli


def test_data_del_figlio_dipende_dai_figli_contati_dal_nucleo():
    assert d.da_porre("data_evento_figlio", {}) == "nucleo"
    p = d.completa({"nucleo": [{"eta": 40}, {"eta": 3}]}, GIORNO)
    assert "numero_figli" not in p and d.da_porre("data_evento_figlio", p) == "nucleo.figlio"
    p = d.completa({"nucleo": [{"eta": 40}, {"eta": 3, "figlio": True}]}, GIORNO)
    assert p["numero_figli"] == 1 and d.da_porre("data_evento_figlio", p) == "data_evento_figlio"


def test_senza_figli_non_si_chiede_la_data_e_i_termini_non_valgono():
    p = d.completa({"nucleo": [{"eta": 40}, {"eta": 70, "figlio": False}]}, GIORNO)
    assert p["numero_figli"] == 0 and p["giorni_da_evento_figlio"] == d.NESSUN_EVENTO["giorni_da_evento_figlio"]
    assert p["nucleo"][1]["figlio_a_carico"] is False  # chi non è figlio non è un figlio a carico
    assert p["nucleo"][0]["figlio"] is False           # chi fa domanda non è figlio di sé stesso


def test_figli_non_lo_so_resta_non_lo_so():
    assert d.completa({"nucleo": [{"eta": 40}, {"eta": 3, "figlio": NON_SO}]}, GIORNO)["numero_figli"] == NON_SO
    assert d.completa({"nucleo": NON_SO}, GIORNO)["numero_figli"] == NON_SO


def test_domanda_sui_componenti_solo_per_chi_ha_la_condizione_aperta():
    p = d.completa({"nucleo": [{"eta": 40}, {"eta": 3, "figlio": True}, {"eta": 70, "figlio": False}]}, GIORNO)
    assert d.domanda_persone("nucleo.figlio_a_carico", 1, p)["componenti"] == [{"indice": 1, "eta": 3}]


@pytest.mark.parametrize("cittadinanza, atteso", [("italiana", False), ("ue", False), ("altro_titolo", None), (NON_SO, None)])
def test_permesso_casi_speciali_si_deduce_solo_quando_e_certo(cittadinanza, atteso):
    assert d.completa({"cittadinanza": cittadinanza}, GIORNO).get("permesso_casi_speciali") is atteso


def test_non_lo_so_chiude_la_domanda_e_lascia_mancano_dati():
    out, chieste, _ = rispondi_a_tutto("persone", {}, lambda campo, c: NON_SO)
    assert len(chieste) == len(set(chieste))
    assert all(r["stato"] in (MANCANO_DATI, DA_VERIFICARE) for r in out["risultati"])


def test_un_no_ferma_le_domande_di_quel_beneficio():
    """Chi non ha avuto figli: bonus nuovi nati e maternità diventano 'non idoneo' e le loro domande spariscono."""
    p = {"data_evento_figlio": "nessuno", "nucleo": [{"eta": 40}]}
    out = d.passo("persone", p, GIORNO)
    esiti = {r["id"]: r["stato"] for r in out["risultati"]}
    assert esiti["inps-bonus-nuovi-nati"] == NON_IDONEO and esiti["inps-assegno-maternita-stato"] == NON_IDONEO


def test_la_domanda_che_decide_viene_prima():
    """A NASpI manca solo la causa della fine del lavoro: quella domanda vale un beneficio intero e passa davanti."""
    p = {k: PERSONA[k] for k in ("ultimo_lavoro_subordinato", "condizione_lavorativa", "giorni_da_cessazione_lavoro",
                                 "settimane_contributi_4_anni")}
    p["data_evento_figlio"] = "nessuno"
    p["nucleo"] = [{"eta": 40}]
    esiti = valuta_tutte(d.regole_persone(), d.completa(p, GIORNO))
    assert d.prossima_persone(esiti, d.completa(p, GIORNO))[0] == "causa_fine_lavoro"


def test_eta_di_chi_fa_domanda_dal_primo_componente():
    """Assegno sociale e SFL chiedono l'età di chi fa domanda: è quella data per "Tu" nel nucleo, senza un'altra domanda."""
    assert d.completa({"nucleo": [{"eta": 67}, {"eta": 70}]}, GIORNO)["eta"] == 67
    assert d.completa({"nucleo": NON_SO}, GIORNO)["eta"] == NON_SO
    assert d.completa({"nucleo": [{"eta": NON_SO}]}, GIORNO)["eta"] == NON_SO
    assert d.da_porre("eta", {}) == "nucleo"
    regola = {"id": "prova", "titolo": "prova", "requisiti": [{"campo": "eta", "operatore": ">=", "valore": 67}]}
    p = d.completa({"nucleo": [{"eta": 70}]}, GIORNO)
    assert valuta_tutte([regola], p)[0].stato == IDONEO


@pytest.mark.parametrize("data, giorni, mesi", [
    ("2026-09-20", 49, 1), ("2026-09-08", 61, 2), ("2026-09-09", 60, 1), ("2026-11-08", 0, 0)])
def test_data_del_figlio_diventa_giorni_e_mesi_interi(data, giorni, mesi):
    p = d.completa({"data_evento_figlio": data}, GIORNO)
    assert (p["giorni_da_evento_figlio"], p["mesi_da_evento_figlio"]) == (giorni, mesi)
    assert "data_evento_figlio" not in p


def test_domanda_per_componente_elenca_solo_chi_non_ha_risposto():
    p = {"nucleo": [{"eta": 34, "disabile": False}, {"eta": 1}]}
    q = d.domanda_persone("nucleo.disabile", 1, p)
    assert q["per_componente"] and q["componenti"] == [{"indice": 1, "eta": 1}]
    assert q["testo"] == "Ha una disabilità?"  # il testo viene da data/domande_persone.yaml


def test_descrivi_requisiti():
    assert d.descrivi({"campo": "isee", "operatore": "<=", "valore": 40000}) == "ISEE al massimo 40.000"
    assert d.descrivi({"campo": "eta", "operatore": "tra", "valore": [18, 35]}) == "età tra 18 e 35"
    lungo = d.descrivi({"campo": "comune", "operatore": "in", "valori": [f"C{i}" for i in range(300)]})
    assert lungo.startswith("comune: uno dei 300 elencati")
    assert d.descrivi({"non_modellabile": "Serve la circolare."}) == "Serve la circolare."


def test_regole_estratte_solo_a_richiesta():
    base = d.passo("persone", {}, GIORNO)["risultati"]
    tutte = d.passo("persone", {}, GIORNO, estratte=True)["risultati"]
    assert {r["origine"] for r in base} == {"riferimento"}
    assert len(tutte) > len(base) and "estratta" in {r["origine"] for r in tutte}


# --- imprese: servono le regole generate da `make dati` ---

@pytest.fixture
def imprese(regole):  # la fixture `regole` di conftest salta il test se mancano
    return d


def test_impresa_completa(imprese):
    risposte = {"regione": "Lombardia", "tipologia": ["Impresa"], "dimensione": "Microimpresa",
                "settore": ["Ristorazione"], "ateco_2025": "56.10", "ambito": [], "comune": "Milano"}
    out, chieste, _ = rispondi_a_tutto("imprese", risposte)
    assert set(chieste) <= set(risposte) and chieste[0] == "regione"
    assert out["conteggi"][IDONEO] > 0
    idoneo = next(r for r in out["risultati"] if r["stato"] == IDONEO)
    assert idoneo["requisiti"] or idoneo["perche"] is not None


# --- API ---

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from web.server import app
    return TestClient(app)


def test_api_passo_e_pagina(client, monkeypatch):
    monkeypatch.setenv("TROVA_BANDI_GIORNO", GIORNO)
    r = client.post("/api/passo", json={"ramo": "persone", "profilo": {}})
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["giorno"] == GIORNO and corpo["domanda"]["campo"] and len(corpo["risultati"]) == 5
    assert client.get("/").status_code == 200 and "trova-bandi" in client.get("/").text


def test_api_rifiuta_ramo_sconosciuto_e_tipi_sbagliati(client):
    assert client.post("/api/passo", json={"ramo": "enti", "profilo": {}}).status_code == 422
    assert client.post("/api/passo", json={"ramo": "persone", "profilo": {"isee": "tanto"}}).status_code == 422


def test_api_comuni(client):
    r = client.get("/api/comuni", params={"regione": "Valle d'Aosta/Vallée d'Aoste"})
    assert r.status_code == 200 and "Aosta" in r.json()
    assert client.get("/api/comuni", params={"regione": "Atlantide"}).status_code == 404


def test_oggi_di_default(client, monkeypatch):
    monkeypatch.delenv("TROVA_BANDI_GIORNO", raising=False)
    assert client.post("/api/passo", json={"ramo": "persone"}).json()["giorno"] == dt.date.today().isoformat()
