"""Le 5 regole INPS di prova, con gli esiti calcolati a mano leggendo le schede."""
import copy

import pytest

from pipeline.citazioni import problemi, carica_testi_inps
from pipeline.motore import DA_VERIFICARE, IDONEO, IDONEO_SALVO, MANCANO_DATI, NON_IDONEO, NON_SO, valuta, verifica
from pipeline.regole import DIR_PERSONE, VALIDATORE, carica


@pytest.fixture(scope="module")
def R():
    return {r["id"]: r for r in carica(DIR_PERSONE)}


def adi(**extra):
    """Madre italiana con un figlio piccolo e pochi mezzi: passa tutto ciò che il motore può controllare."""
    return {"cittadinanza": "italiana", "anni_residenza_italia": 10, "anni_residenza_continuativa_italia": 10,
            "isee": 8000, "patrimonio_immobiliare": 0, "veicoli_esclusi": False, "permesso_casi_speciali": False,
            "nucleo": [{"eta": 35, "disabile": False, "svantaggio_certificato": False},
                       {"eta": 3, "disabile": False, "svantaggio_certificato": False}], **extra}


def test_cinque_regole_valide(R):
    assert len(R) == 5
    assert all(r["pubblico"] == "persone" and r["ultimo_controllo"] for r in R.values())


def test_adi_chi_passa_i_controlli_resta_da_verificare(R):
    e = valuta(R["inps-adi"], adi())
    assert e.stato == DA_VERIFICARE and not e.falliti


@pytest.mark.parametrize("extra", [
    {"isee": 10141},
    {"anni_residenza_italia": 4},
    {"anni_residenza_continuativa_italia": 1},
    {"cittadinanza": "altro_titolo"},
    {"patrimonio_immobiliare": 30001},
    {"veicoli_esclusi": True},
    {"nucleo": [{"eta": 35, "disabile": False, "svantaggio_certificato": False}]},
])
def test_adi_non_idoneo(R, extra):
    assert valuta(R["inps-adi"], adi(**extra)).stato == NON_IDONEO


def test_adi_soglia_isee_inclusa(R):
    assert valuta(R["inps-adi"], adi(isee=10140)).stato == DA_VERIFICARE


def test_adi_isee_non_noto_non_e_un_no(R):
    assert valuta(R["inps-adi"], adi(isee=NON_SO)).stato == MANCANO_DATI
    p = adi()
    del p["isee"]
    assert valuta(R["inps-adi"], p).stato == MANCANO_DATI


def test_adi_casi_speciali_esenti_dai_requisiti_economici(R):
    p = adi(permesso_casi_speciali=True, isee=50000, cittadinanza="altro_titolo", anni_residenza_italia=0,
            nucleo=[{"eta": 35, "disabile": False, "svantaggio_certificato": False}])
    assert valuta(R["inps-adi"], p).stato == DA_VERIFICARE  # resta il requisito non modellabile sulle condanne
    assert valuta(R["inps-adi"], {**p, "veicoli_esclusi": True}).stato == NON_IDONEO


def test_adi_componente_con_almeno_60_anni(R):
    nonno = [{"eta": 60, "disabile": False, "svantaggio_certificato": False}]
    assert valuta(R["inps-adi"], adi(nucleo=nonno)).stato == DA_VERIFICARE


def test_nuovi_nati_soglie(R):
    r = R["inps-bonus-nuovi-nati"]
    assert valuta(r, {"giorni_da_evento_figlio": 120, "isee": 40000}).stato == DA_VERIFICARE
    assert valuta(r, {"giorni_da_evento_figlio": 121, "isee": 40000}).stato == NON_IDONEO
    assert valuta(r, {"giorni_da_evento_figlio": 10, "isee": 40001}).stato == NON_IDONEO
    assert valuta(r, {"giorni_da_evento_figlio": 10}).stato == MANCANO_DATI


def auu(*figli_, **extra):
    return {"cittadinanza": "italiana", "soggetto_irpef_italia": True, "residente_italia": True,
            "nucleo": list(figli_), **extra}


@pytest.mark.parametrize("figlio, atteso", [
    ({"figlio_a_carico": True, "eta": 5, "disabile": False}, IDONEO),
    ({"figlio_a_carico": True, "eta": 20, "disabile": False, "reddito_annuo": 5000, "attivita": "studio"}, IDONEO),
    ({"figlio_a_carico": True, "eta": 20, "disabile": False, "reddito_annuo": 8000, "attivita": "studio"}, NON_IDONEO),
    ({"figlio_a_carico": True, "eta": 20, "disabile": False, "reddito_annuo": 5000, "attivita": "nessuna"}, NON_IDONEO),
    ({"figlio_a_carico": True, "eta": 21, "disabile": False, "reddito_annuo": 5000, "attivita": "studio"}, NON_IDONEO),
    ({"figlio_a_carico": True, "eta": 30, "disabile": True}, IDONEO),
    ({"figlio_a_carico": False, "eta": 5, "disabile": False}, NON_IDONEO),
])
def test_assegno_unico_figli(R, figlio, atteso):
    assert valuta(R["inps-assegno-unico"], auu(figlio)).stato == atteso


def test_assegno_unico_basta_un_figlio_idoneo(R):
    grande = {"figlio_a_carico": True, "eta": 30, "disabile": False, "reddito_annuo": 20000, "attivita": "nessuna"}
    piccolo = {"figlio_a_carico": True, "eta": 2, "disabile": False}
    assert valuta(R["inps-assegno-unico"], auu(grande, piccolo)).stato == IDONEO


def test_assegno_unico_senza_nucleo_e_altro_titolo(R):
    r = R["inps-assegno-unico"]
    assert valuta(r, auu()).stato == NON_IDONEO  # famiglia senza figli
    assert valuta(r, {"cittadinanza": "italiana", "soggetto_irpef_italia": True, "residente_italia": True}).stato \
        == MANCANO_DATI  # nucleo non ancora chiesto
    figlio = {"figlio_a_carico": True, "eta": 5, "disabile": False}
    assert valuta(r, auu(figlio, cittadinanza="altro_titolo")).stato == DA_VERIFICARE
    # chi lavora qui senza risiedere deve avere anche iscrizione e regolarità contributiva, che non chiediamo
    assert valuta(r, auu(figlio, residente_italia=False, lavora_in_italia=True)).stato == DA_VERIFICARE
    assert valuta(r, auu(figlio, residente_italia=False, lavora_in_italia=False)).stato == NON_IDONEO


NASPI = {"ultimo_lavoro_subordinato": True, "condizione_lavorativa": "disoccupato", "causa_fine_lavoro": "licenziamento",
         "settimane_contributi_4_anni": 13, "giorni_da_cessazione_lavoro": 68}


@pytest.mark.parametrize("extra, atteso", [
    ({}, IDONEO_SALVO),  # resta solo la prevalenza di contributi non agricoli, segnata rara (decisione 52)
    ({"causa_fine_lavoro": "dimissioni"}, NON_IDONEO),
    ({"causa_fine_lavoro": "dimissioni_giusta_causa"}, IDONEO_SALVO),
    ({"settimane_contributi_4_anni": 12}, NON_IDONEO),
    ({"giorni_da_cessazione_lavoro": 69}, NON_IDONEO),
    ({"ultimo_lavoro_subordinato": False}, NON_IDONEO),
    ({"condizione_lavorativa": "occupato"}, DA_VERIFICARE),  # chi conserva un part-time può avere diritto: non è rara
])
def test_naspi(R, extra, atteso):
    assert valuta(R["inps-naspi"], {**NASPI, **extra}).stato == atteso


def test_naspi_mostra_l_eccezione_con_la_citazione(R):
    e = valuta(R["inps-naspi"], NASPI)
    assert [x["citazione"] for x in e.eccezioni] == [
        "purché nel quadriennio di osservazione risulti prevalente la contribuzione non agricola"]


def test_maternita(R):
    r = R["inps-assegno-maternita-stato"]
    p = {"residente_italia": True, "cittadinanza": "italiana", "mesi_da_evento_figlio": 5}
    assert valuta(r, p).stato == DA_VERIFICARE  # i requisiti contributivi non sono modellati
    assert valuta(r, {**p, "mesi_da_evento_figlio": 6}).stato == NON_IDONEO
    assert valuta(r, {**p, "residente_italia": False}).stato == NON_IDONEO


@pytest.mark.parametrize("req, profilo, atteso", [
    ({"almeno_uno_di": [{"non_modellabile": "x"}, {"campo": "disabile", "operatore": "vero"}]}, {"disabile": True}, True),
    ({"almeno_uno_di": [{"non_modellabile": "x"}, {"campo": "disabile", "operatore": "vero"}]}, {"disabile": False}, None),
    ({"tutti_di": [{"non_modellabile": "x"}, {"campo": "disabile", "operatore": "vero"}]}, {"disabile": False}, False),
    ({"tutti_di": [{"non_modellabile": "x"}, {"campo": "disabile", "operatore": "vero"}]}, {"disabile": True}, None),
    ({"campo": "eta", "operatore": "tra", "valore": [18, 20]}, {"eta": 18}, True),
    ({"campo": "eta", "operatore": "tra", "valore": [18, 20]}, {"eta": 21}, False),
    ({"campo": "disabile", "operatore": "falso"}, {"disabile": False}, True),
    ({"campo": "isee", "operatore": "<=", "valore": 10}, {"isee": 0}, True),  # ISEE zero è un valore, non un dato assente
    ({"almeno_un_componente": [{"campo": "eta", "operatore": "<", "valore": 18}]}, {"nucleo": []}, False),
    ({"almeno_un_componente": [{"campo": "eta", "operatore": "<", "valore": 18}]}, {"nucleo": [{}]}, None),
    ({"almeno_un_componente": [{"campo": "eta", "operatore": "<", "valore": 18}]}, {"nucleo": [{}, {"eta": 2}]}, True),
])
def test_logica_a_tre_valori(req, profilo, atteso):
    assert verifica(req, profilo) is atteso


@pytest.mark.parametrize("requisito", [
    {"campo": "isee", "operatore": "in", "valori": ["1"], "fonte": "x"},
    {"campo": "isee", "operatore": "<=", "valore": [1, 2], "fonte": "x"},
    {"campo": "isee", "operatore": "tra", "valore": 1, "fonte": "x"},
    {"campo": "disabile", "operatore": "<=", "valore": 1, "fonte": "x"},
    {"almeno_uno_di": [{"campo": "disabile", "operatore": "vero"}], "fonte": "x"},
    {"almeno_un_componente": [{"campo": "inventato", "operatore": "vero"}], "fonte": "x"},
    {"non_modellabile": "x"},
])
def test_schema_rifiuta(R, requisito):
    r = copy.deepcopy(R["inps-naspi"])
    r["requisiti"].append(requisito)
    assert not VALIDATORE.is_valid(r)


def test_citazioni_rifiuta_quelle_inventate(R):
    testo = "La NASpI è riconosciuta ai lavoratori\n subordinati"
    r = {"requisiti": [{"campo": "disabile", "operatore": "vero", "citazione": "La NASpI è riconosciuta ai lavoratori subordinati"}]}
    assert problemi(r, testo) == []
    r["requisiti"][0]["citazione"] = "La NASpI spetta a tutti"
    assert "assente dalla fonte" in problemi(r, testo)[0]
    r["requisiti"][0].pop("citazione")
    assert "manca la citazione" in problemi(r, testo)[0]


def test_citazione_inventata_annidata(R):
    r = {"requisiti": [{"citazione": "vera", "almeno_uno_di": [{"non_modellabile": "x"}, {"campo": "eta", "operatore": "<", "valore": 1, "citazione": "falsa"}]}]}
    assert len(problemi(r, "vera")) == 1


def test_ogni_citazione_esiste_nella_scheda_inps(R):
    testi = carica_testi_inps()
    for r in R.values():
        assert r["link"] in testi, r["id"]
        assert problemi(r, testi[r["link"]]) == [], r["id"]
