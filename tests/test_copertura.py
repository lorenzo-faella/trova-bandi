"""Misura della copertura (pipeline/copertura.py): le parti pure, senza rete e senza i file raccolti."""
import pytest

from pipeline import copertura as cp


def test_normalizza_toglie_accenti_maiuscole_punteggiatura_ed_entita():
    assert cp.normalizza("Re-IMPRESA: più&nbsp;Città!") == "re impresa piu citta"
    assert cp.normalizza(None) == ""


def test_parole_vuote_e_nomi_della_regione_non_contano():
    assert cp.parole("Avviso pubblico per le imprese della Regione Lombardia") == ("imprese",)


@pytest.mark.parametrize("a, b", [
    ("Dote Impresa Asse I - Provincia di Bergamo", "Dote Impresa Asse I - Provincia di Como"),   # luoghi
    ("Brevetti 2021", "Brevetti 2023"),                                                          # anni
    ("Dote Impresa Asse I", "Dote Impresa Asse II"),                                             # assi
    ("Formazione continua terza edizione", "Formazione continua quarta edizione"),               # ordinali
])
def test_segni_diversi_danno_zero(a, b):
    assert cp.incompatibili(a, b)
    assert cp.somiglianza(a, b) == 0.0


def test_il_periodo_di_programmazione_non_e_un_anno():
    assert not cp.incompatibili("Bando X - PR FESR 2021-2027", "Bando X")
    assert cp.segni("Bando X - PR FESR 2021-2027")["anni"] == frozenset()


def test_assi_basta_uno_in_comune_e_il_luogo_si_legge_anche_dall_ente():
    assert not cp.incompatibili("Dote Impresa Collocamento Mirato Assi I II III", "Dote Impresa Asse II")
    assert cp.incompatibili("Dote Impresa", "Dote Impresa", ente_a="Provincia di Pavia", ente_b="Provincia di Varese")


def test_titoli_uguali_abbinati_e_ordine_delle_parole_non_conta():
    assert cp.esito(cp.somiglianza("Bando Rafforza Innova", "Rafforza & Innova - Bando")) == "sì"
    assert cp.somiglianza("Pacchetto investimenti linea sviluppo aziendale",
                          "Investimenti - linea sviluppo aziendale pacchetto") >= cp.SOGLIA


def test_titolo_contenuto_o_stessa_azione_vanno_almeno_in_zona_grigia():
    s = cp.somiglianza("Re-Impresa", "Avviso Re-Impresa - Sostegno alle imprese in crisi per la ripartenza produttiva")
    assert cp.esito(s) == "grigio"
    s = cp.somiglianza("Azione 2.1.2 - progetti innovativi di efficientamento",
                       "Sicilia efficiente: meno consumi - Azione 2.1.2 del programma")
    assert s >= cp.GRIGIA


def test_luogo_in_un_titolo_solo_non_si_abbina_da_solo():
    s = cp.somiglianza("Dote Impresa Collocamento Mirato Fondo 2024", "Dote Impresa Collocamento Mirato Fondo 2024 Varese")
    assert cp.GRIGIA <= s < cp.SOGLIA


def test_migliore_a_parita_vince_il_primo():
    candidati = [{"titolo": "Bando fiere"}, {"titolo": "Bando fiere"}]
    s, c = cp.migliore("Bando fiere", candidati)
    assert s == 1.0 and c is candidati[0]


@pytest.mark.parametrize("titolo, tipo, atteso", [
    ("Contributi alle imprese per la digitalizzazione", None, "rilevante"),
    ("Graduatoria definitiva del bando digitalizzazione", None, "non è un bando"),
    ("Procedura negoziata per la fornitura di arredi", None, "gara o fornitura"),
    ("Concorso pubblico per 10 istruttori", None, "personale o concorso"),
    ("Qualsiasi titolo", "Concorsi Pubblici e Avvisi sul Personale", "personale o concorso"),
    ("Contributi agli enti locali per le scuole", None, "solo enti pubblici"),
    ("Contributi agli enti locali e alle imprese per le scuole", None, "rilevante"),  # nomina anche privati
    ("Leggi e scarica l'avviso", None, "titolo senza informazioni"),
])
def test_filtro_di_rilevanza(titolo, tipo, atteso):
    assert cp.rilevanza(titolo, tipo) == atteso


def test_wilson():
    p, lo, hi = cp.wilson(27, 109)
    assert round(p, 3) == 0.248 and (round(lo, 2), round(hi, 2)) == (0.18, 0.34)
    assert cp.wilson(0, 10)[1] == 0.0 and 0.27 < cp.wilson(0, 10)[2] < 0.29  # mai sotto zero, anche con 0 successi
    assert cp.wilson(10, 10)[2] == 1.0
    assert cp.wilson(0, 0) == (None, None, None)


def test_chapman_sicilia_e_casi_limite():
    stima, lo, hi, osservati = cp.chapman(45, 7, 2)
    assert round(stima) == 122 and osservati == 50
    assert osservati <= lo < stima < hi  # l'intervallo di Chao non scende sotto i bandi visti
    # le due fonti coincidono: nessun bando non visto, intervallo degenere
    assert cp.chapman(10, 10, 10) == (10.0, 10.0, 10.0, 10)


@pytest.mark.parametrize("apertura, chiusura, atteso", [
    (None, None, True), ("2026-10-01", None, True), ("2026-10-28", "2026-12-31", False),  # aperto dopo il portale
    ("2026-01-01", "2026-11-01", False), ("2026-01-01", "2026-11-07T23:59:00", True),
])
def test_aperto_in_tutte_e_due_le_date(apertura, chiusura, atteso):
    assert cp.aperto_in_tutte(apertura, chiusura) is atteso


def test_codice_lombardia_dall_indirizzo():
    assert cp.codice_lombardia("https://www.bandi.regione.lombardia.it/servizi/servizio/bandi/dettaglio/x/bando-RLO12023036183/") \
        == "RLO12023036183"
    assert cp.codice_lombardia("https://www.regione.sicilia.it/bandi/123") is None


def test_abbina_codice_prima_poi_titolo_e_revisione_per_la_zona_grigia():
    rif = [{"codice": "RLO1", "titolo": "Bando A"}, {"codice": None, "titolo": "Re-Impresa"},
           {"codice": None, "titolo": "Contributi per le fiere"}]
    cand = [{"codice": "RLO1", "titolo": "Titolo diverso"},
            {"codice": None, "titolo": "Avviso Re-Impresa - Sostegno alle imprese in crisi per la ripartenza produttiva"}]
    revisione = {"coppie": {("Re-Impresa", cand[1]["titolo"]): True}}
    a = cp.abbina(rif, cand, revisione)
    assert a[0]["metodo"] == "codice" and a[0]["finale"]
    assert a[1]["esito"] == "grigio" and a[1]["finale"]  # deciso a mano
    assert not cp.abbina(rif, cand, {"coppie": {}})[1]["finale"]  # zona grigia non decisa = non trovato
    assert a[2]["esito"] == "no" and not a[2]["finale"]


def test_unisci_non_trova_mai_meno_della_fonte_migliore():
    portale = [{"finale": True, "punteggio": 0.8}, {"finale": False, "punteggio": 0.3}]
    raccolta = [{"finale": False, "punteggio": 0.5}, {"finale": True, "punteggio": 1.0}]
    assert [x["finale"] for x in cp.unisci(portale, raccolta)] == [True, True]
