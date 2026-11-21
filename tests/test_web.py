"""Demo web: domande delle persone, esiti leggibili e API, senza rete (TestClient chiama l'app in memoria)."""
import datetime as dt

import pytest

from pipeline.motore import DA_VERIFICARE, IDONEO, IDONEO_SALVO, MANCANO_DATI, NON_IDONEO, NON_SO, valuta, valuta_tutte, verifica
from web import domande as d

GIORNO = "2026-11-08"
PERSONA = {"contributi_agricoli_presenti": False, "lavoro_terminato": True, "esclusione_naspi": False, "altri_lavori_in_essere": False,
           "disponibilita_lavoro_naspi": True, "dimissioni_indeterminato_12_mesi": False,
           "termine_naspi_particolare": False,"cittadinanza": "italiana", "residente_italia": True, "nucleo": [{"eta": 34}, {"eta": 1}],
           "condizione_lavorativa": "disoccupato", "isee": 9000, "isee_prestazioni_familiari_2026": 9000, "ultimo_lavoro_subordinato": True,
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
        if q["tipo"] == "pagina":  # residenza e domicilio: più domande in una pagina (decisione 80)
            for parte in q["parti"]:
                if all(p.get(c) == v for c, v in (parte.get("se") or {}).items()):
                    p[parte["campo"]] = risposte.get(parte["campo"], NON_SO)
        elif q.get("per_componente"):
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
    attesi = {"inps-assegno-unico": IDONEO, "inps-naspi": IDONEO, "inps-adi": DA_VERIFICARE,
              "inps-assegno-maternita-stato": DA_VERIFICARE, "inps-bonus-nuovi-nati": DA_VERIFICARE}
    assert {k: esiti[k] for k in attesi} == attesi
    assert len(esiti) == 5 + len(d.etichette())  # più le etichette scritte a mano (decisione 78)
    assert len(chieste) == len(set(chieste))  # nessuna domanda ripetuta
    assert "regione" not in chieste  # nessuna delle 5 regole la usa: non si chiede


def test_ogni_domanda_del_file_si_puo_mostrare():
    for chiave in d.domande():
        q = d.domanda_persone(chiave, 1, {"nucleo": [{"eta": 40}], "regione": "Lombardia"})
        assert q["testo"] and q["tipo"] in {"scelta", "multipla", "comune", "si_no", "numero", "data", "nucleo", "pagina"}, chiave
        if q["tipo"] in ("scelta", "multipla"):
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


def test_evento_figlio_indipendente_dalla_composizione_attuale_del_nucleo():
    # Un figlio può non essere nel nucleo attuale: il numero di figli ISEE non prova l'assenza di eventi recenti.
    assert d.da_porre("data_evento_figlio", {}) == "data_evento_figlio"
    p = d.completa({"nucleo": [{"eta": 40}, {"eta": 70, "figlio": False}]}, GIORNO)
    assert p["numero_figli"] == 0 and "giorni_da_evento_figlio" not in p
    assert p["nucleo"][1]["figlio_a_carico"] is False
    assert p["nucleo"][0]["figlio"] is False
    p = d.completa({"nucleo": [{"eta": 40}], "data_evento_figlio": "nessuno"}, GIORNO)
    assert p["giorni_da_evento_figlio"] == d.NESSUN_EVENTO["giorni_da_evento_figlio"]


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
    p.update(residente_italia=True, regione="Lazio", domicilio_diverso=False)  # le due pagine iniziali (decisione 80)
    # solo le 5 regole scritte per la demo: le etichette aggiungono benefici con altre domande (decisione 78)
    esiti = valuta_tutte(d.leggi_cartella(d.DIR_PERSONE, "riferimento"), d.completa(p, GIORNO))
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


def test_domande_che_non_riguardano_la_persona():
    """Decisione 64: una domanda chiusa da una risposta vera ha una risposta ovvia, e il requisito non resta senza dati."""
    p = d.completa({"condizione_lavorativa": "disoccupato", "disabile": False, "abitazione": "proprieta",
                    "cittadinanza": "italiana"}, GIORNO)
    assert p["tipo_lavoro"] == d.NON_APPLICABILE and p["lavora_in_italia"] is False
    assert p["percentuale_invalidita"] == 0 and "contratto_locazione_registrato" not in p
    assert p["permesso_casi_speciali"] is False and "reddito_richiedente" not in p
    regola = {"id": "prova", "titolo": "prova", "requisiti": [{"campo": "tipo_lavoro", "operatore": "in", "valori": ["dipendente"]}]}
    assert valuta_tutte([regola], p)[0].stato == NON_IDONEO
    # chiusa da "non lo so": resta senza dati
    p = d.completa({"condizione_lavorativa": NON_SO, "disabile": NON_SO}, GIORNO)
    assert "tipo_lavoro" not in p and "percentuale_invalidita" not in p
    assert "tipo_lavoro" not in d.completa({"condizione_lavorativa": "occupato"}, GIORNO)


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
    assert lungo.startswith("comune di residenza: uno dei 300 elencati")
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
    r = client.post("/api/passo", json={"ramo": "persone", "profilo": {}, "estratte": False})
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["giorno"] == GIORNO and corpo["domanda"]["campo"] and len(corpo["risultati"]) == 5 + len(d.etichette())
    # di default anche le regole estratte, ognuna con la sua origine per il badge (decisione 68)
    tutte = client.post("/api/passo", json={"ramo": "persone", "profilo": {}}).json()["risultati"]
    assert len(tutte) > 5 and {r["origine"] for r in tutte} == {"riferimento", "estratta"}
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


# --- Nuova demo (decisione 68) ---

def test_api_statistiche(client, monkeypatch):
    monkeypatch.setenv("TROVA_BANDI_GIORNO", GIORNO)
    s = client.get("/api/statistiche").json()
    assert s["giorno"] == GIORNO and s["persone"] > s["persone_aperte"] > 0 and s["persone_riferimento"] == 5 + len(d.etichette())
    assert s["schede_inps"] > 400 and s["documenti"] > 2000 and s["fonti"] > 100


def test_profili_del_caro_vita_validi(client, monkeypatch):
    """Ogni profilo di esempio usa solo campi del questionario, non lascia domande aperte e dà esiti diversi dagli altri."""
    monkeypatch.setenv("TROVA_BANDI_GIORNO", GIORNO)
    profili = client.get("/api/profili").json()
    assert len(profili) == 4
    campi = {k.split(".")[-1] for k in d.domande()} | {"nucleo"}
    esiti = []
    for p in profili:
        assert set(p["profilo"]) <= campi, set(p["profilo"]) - campi
        assert all(set(c) <= campi for c in p["profilo"]["nucleo"])
        out = client.post("/api/passo", json={"ramo": "persone", "profilo": p["profilo"]}).json()
        assert out["conteggi"]["da verificare"] + out["conteggi"]["idoneo"] + out["conteggi"]["idoneo, salvo eccezioni"] > 0
        esiti.append(tuple(sorted((r["id"], r["stato"]) for r in out["risultati"])))
    assert len(set(esiti)) == 4


def test_avviso_isee(client):
    out = client.post("/api/passo", json={"ramo": "persone", "profilo": {"isee": NON_SO}}).json()
    assert out["isee"]["decide"] > 0 and out["isee"]["link"].startswith("https://www.inps.it/")
    assert "isee" not in client.post("/api/passo", json={"ramo": "persone", "profilo": {"isee": 9000}}).json()


def test_regione_del_bando():
    """La regione della fonte serve solo a raggruppare: INPS è nazionale, un comune ha la sua regione."""
    assert d.territorio({"id": "inps-assegno-unico"}) is None
    assert d.territorio({"id": "comune-grosseto-e-pubblicato-il-bando-contributi-affitti-9c5"}) == "Toscana"
    # fonti raccolte con le API regionali (pipeline/fonti/api_regioni.py), che non sono in elenchi.yaml
    assert d.territorio({"id": "lombardia-dote-unica-lavoro-quinta-fase-9aa8f9"}) == "Lombardia"
    assert d.territorio({"id": "emilia-gal-delta-2000-start-up-non-agricole-ii-0abfa7"}) == "Emilia-Romagna"
    assert d.territorio({"id": "trento-contributo-prima-casa-2026"}) == "Trentino-Alto Adige/Südtirol"


def test_studio_e_lavoro_insieme():
    """Decisione 69: la situazione lavorativa ammette più risposte; il motore e le domande successive le accettano tutte."""
    q = d.domanda_persone("condizione_lavorativa", 1, {})
    assert q["tipo"] == "multipla" and q["almeno_una"] and len(q["opzioni"]) == 5
    p = d.completa({"condizione_lavorativa": ["studente", "occupato"]}, GIORNO)
    assert "tipo_lavoro" not in p  # chi lavora: la domanda sul tipo di lavoro resta aperta
    assert d.da_porre("tipo_lavoro", p) == "tipo_lavoro"
    assert verifica({"campo": "condizione_lavorativa", "operatore": "in", "valori": ["occupato"]}, p) is True
    assert verifica({"campo": "condizione_lavorativa", "operatore": "in", "valori": ["disoccupato"]}, p) is False
    solo_studio = d.completa({"condizione_lavorativa": ["studente"]}, GIORNO)
    assert "tipo_lavoro" not in solo_studio  # Studio da solo non dimostra l’assenza di altri lavori.


def test_a_favore_distingue_possibile_da_non_sappiamo():
    """Decisione 70: un "da verificare" senza requisiti già soddisfatti non è un indizio a favore."""
    out = d.passo("persone", d.profili_demo()[0]["profilo"], GIORNO, True)
    dv = [r for r in out["risultati"] if r["stato"] == DA_VERIFICARE]
    assert all(isinstance(r["a_favore"], int) for r in out["risultati"])
    assert any(r["a_favore"] == 0 for r in dv) and any(r["a_favore"] > 0 for r in dv)
    soddisfatto = {"id": "x", "titolo": "x", "requisiti": [{"campo": "isee", "operatore": "<=", "valore": 20000},
                                                            {"non_modellabile": "y", "citazione": "z"}]}
    e = valuta_tutte([soddisfatto], {"isee": 10000})[0]
    assert e.stato == DA_VERIFICARE and d.risultato(e, {"isee": 10000})["a_favore"] == 1


def test_situazioni_particolari_e_interseca():
    """Decisione 70: "nessuna di queste" esclude dai benefici per gruppi ristretti; interseca accetta anche una stringa."""
    q = {"campo": "situazioni_particolari", "operatore": "interseca", "valori": ["superstite"]}
    assert verifica(q, {"situazioni_particolari": ["nessuna"]}) is False
    assert verifica(q, {"situazioni_particolari": ["superstite", "lavoro_agricolo"]}) is True
    assert verifica({"campo": "tipo_lavoro", "operatore": "interseca", "valori": ["dipendente"]}, {"tipo_lavoro": "dipendente"}) is True
    d_sp = d.domanda_persone("situazioni_particolari", 1, {})
    assert d_sp["tipo"] == "multipla" and any(o["valore"] == "nessuna" for o in d_sp["opzioni"])
    # decisione 73: la sede del corso si chiede come comune; provincia e regione si ricavano dall'ISTAT
    assert d.domanda_persone("comune_ateneo", 1, {"iscrizione": "universita"})["tipo"] == "pagina"
    p = d.completa({"iscrizione": "universita", "comune_ateneo": "Acireale"}, GIORNO)
    assert (p["provincia_ateneo"], p["regione_ateneo"]) == ("Catania", "Sicilia")
    assert d.da_porre("regione_ateneo", {"iscrizione": "universita"}) == "comune_ateneo"
    livelli = {o["valore"] for o in d.domanda_persone("livello_corso", 1, {})["opzioni"]}
    assert {"laurea_magistrale", "dottorato", "its"} <= livelli


def test_residenza_domicilio_e_riepilogo():
    """Decisione 71: il comune si chiede dopo la regione; il domicilio segue la residenza se la persona vive lì;
    il riepilogo delle risposte è leggibile."""
    assert d.da_porre("comune", {}) == "regione"
    assert d.da_porre("comune_domicilio", {"regione": "Sicilia", "comune": "Palermo"}) == "domicilio_diverso"
    p = d.completa({"regione": "Sicilia", "comune": "Palermo", "domicilio_diverso": False}, GIORNO)
    assert (p["regione_domicilio"], p["comune_domicilio"]) == ("Sicilia", "Palermo")
    p = d.completa({"regione": "Sicilia", "domicilio_diverso": True}, GIORNO)
    assert "regione_domicilio" not in p  # da chiedere, non "non applicabile"
    righe = d.riepilogo({"regione": "Sicilia", "isee": 12000, "condizione_lavorativa": ["studente", "occupato"],
                         "nucleo": [{"eta": 22}]})
    testo = {r["voce"]: r["valore"] for r in righe}
    assert testo["ISEE"] == "12.000 euro" and testo["Situazione lavorativa"] == "Studio, Lavoro" and testo["Tu"] == "22 anni"


def test_chiusi_di_recente():
    """Decisione 72: i bandi chiusi negli ultimi 12 mesi arrivano a parte, senza i "non ti spetta"."""
    out = d.passo("persone", {"iscrizione": "universita", "regione_ateneo": "Lombardia"}, GIORNO, True)
    chiusi = out["chiusi_di_recente"]
    assert chiusi and all(r["chiusura"] < GIORNO and r["stato"] != NON_IDONEO for r in chiusi)
    assert not {r["id"] for r in chiusi} & {r["id"] for r in out["risultati"]}


def test_regione_della_fonte_col_nome_ufficiale():
    """Decisione 73: le fonti che scrivono "Trentino-Alto Adige" danno la regione col nome dell'elenco ISTAT."""
    assert d.regione_ufficiale("Trentino-Alto Adige") == "Trentino-Alto Adige/Südtirol"
    assert d.regione_ufficiale("Valle d'Aosta") == "Valle d'Aosta/Vallée d'Aoste"
    assert d.territorio({"id": "trento-contributo-prima-casa-2026"}) == "Trentino-Alto Adige/Südtirol"


def test_requisiti_generici_non_rendono_possibile():
    """Chi lavora e non ha figli: "sei occupato" da solo non fa diventare "possibile" una maternità con la gravidanza non
    modellabile; un requisito che distingue la persona (l'ISEE) sì (decisione 78)."""
    lavoro = {"campo": "condizione_lavorativa", "operatore": "in", "valori": ["occupato"]}
    regola = {"id": "prova", "titolo": "prova", "requisiti": [{"non_modellabile": "gravidanza in corso"}, lavoro]}
    p = {"condizione_lavorativa": ["occupato"], "isee": 9000}
    assert d.risultato(valuta(regola, p), p)["a_favore"] == 0
    regola["requisiti"].append({"almeno_uno_di": [lavoro, {"campo": "isee", "operatore": "<=", "valore": 15000}]})
    assert d.risultato(valuta(regola, p), p)["a_favore"] == 1


def test_la_parentela_non_si_deduce_dalla_differenza_di_eta():
    """Adozione e affidamento non consentono una soglia universale: occorre la risposta."""
    p = d.completa({"nucleo": [{"eta": 22}, {"eta": 21}, {"eta": 50}, {"eta": 51}, {"eta": 3}]}, GIORNO)
    assert [c.get("figlio") for c in p["nucleo"]] == [False, None, None, None, None]
    q = d.domanda_persone("nucleo.figlio", 1, p)
    assert [c["eta"] for c in q["componenti"]] == [21, 50, 51, 3]
    assert p["numero_componenti"] == 5
    assert d.completa({"nucleo": NON_SO}, GIORNO)["numero_componenti"] == NON_SO


def test_pagine_di_residenza_e_domicilio():
    """Residenza e domicilio vengono per primi, in una pagina ciascuno; chi è sempre vissuto in Italia non risponde
    sugli anni, chi non risiede in Italia non ha regione di residenza (decisione 80)."""
    assert d.prossima_persone([], d.completa({}, GIORNO))[0] == "residenza"
    q = d.domanda_persone("residenza", 0, {})
    assert q["tipo"] == "pagina" and [x["campo"] for x in q["parti"]][:3] == ["residente_italia", "regione", "comune"]
    p = d.completa({"residente_italia": True, "regione": "Lazio", "sempre_in_italia": True, "nucleo": [{"eta": 30}]}, GIORNO)
    assert d.prossima_persone([], p)[0] == "domicilio"
    assert p["anni_residenza_italia"] == p["anni_residenza_continuativa_italia"] == 30
    estero = d.completa({"residente_italia": False}, GIORNO)
    assert estero["regione"] == estero["comune"] == d.NON_APPLICABILE
    assert d.prossima_persone([], estero)[0] == "domicilio"


def test_audit_del_20_11():
    """I casi trovati dall'audit indipendente del 20/11 (docs/audit-2026-11-20, decisione 83)."""
    # "almeno 67 anni" decide l'Assegno sociale: conta a favore; "maggiorenne" no
    vecchio, adulto = {"eta": 70}, {"eta": 40}
    assert d.a_favore({"campo": "eta", "operatore": ">=", "valore": 67}, vecchio)
    assert not d.a_favore({"campo": "eta", "operatore": ">=", "valore": 18}, adulto)
    # con un figlio "non lo so" il numero dei figli resta in sospeso
    p = d.completa({"nucleo": [{"eta": 40}, {"eta": 10, "figlio": True}, {"eta": 8, "figlio": NON_SO}]}, GIORNO)
    assert p["numero_figli"] == NON_SO
    # valori impossibili: errore, non un esito
    for sbagliato in ({"isee": -5}, {"nucleo": [{"eta": 999}]}, {"percentuale_invalidita": 140}, {"disabile": "false"},
                      {"nucleo": "io e mia moglie"}):
        with pytest.raises(ValueError):
            d.completa(sbagliato, GIORNO)
    assert "inps-carta-europea-della-disabilita-disability-car" not in {r["id"] for r in d.etichette()}


def test_api_rifiuta_valori_impossibili(client):
    assert client.post("/api/passo", json={"ramo": "persone", "profilo": {"nucleo": "testo"}}).status_code == 422
    assert client.post("/api/passo", json={"ramo": "persone", "profilo": {"isee": -1}}).status_code == 422
