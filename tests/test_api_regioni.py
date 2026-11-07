"""Fonti con ricerca interna (Sardegna): scelta del PDF principale, gare escluse, nessuna rete."""
from pipeline.fonti import api_regioni as ar

DOCUMENTI = [{"titolo": "Modello A in formato PDF", "formato": "pdf", "urlFinale": "x/modello-a.pdf"},
             {"titolo": "Determinazione n. 2222 - Approvazione", "formato": "pdf", "urlFinale": "x/det.pdf"},
             {"titolo": "Bando permanente 2026", "formato": "pdf", "urlFinale": "x/bando.pdf"},
             {"titolo": "Modello A in formato xlsx", "formato": "xlsx", "urlFinale": "x/modello.xlsx"}]


def test_sceglie_il_bando_e_non_il_modulo():
    assert ar.scegli_pdf(DOCUMENTI)["urlFinale"] == "x/bando.pdf"
    senza_bando = [d for d in DOCUMENTI if "bando" not in d["urlFinale"]]
    assert ar.scegli_pdf(senza_bando)["urlFinale"] == "x/det.pdf"   # meglio un atto che un modulo
    assert ar.scegli_pdf([DOCUMENTI[3]]) is None                     # niente PDF


def test_riconosce_le_gare_d_appalto():
    for t in ["AVVISO SUI RISULTATI DELLA PROCEDURA NEGOZIATA per l'appalto dei lavori",
              "Affidamento diretto ai sensi dell'art. 50", "PROCEDURA APERTA PER L'AFFIDAMENTO DEI LAVORI"]:
        assert ar.GARA.search(t)
    for t in ["Fondo per il sostegno all'accesso alle abitazioni in locazione", "Avviso SO.LA.RE. Sostegno Lavoro"]:
        assert not ar.GARA.search(t)


def test_bandi_sardegna_su_una_risposta_finta(monkeypatch):
    risposta = {"hits": {"hits": [
        {"_source": {"titolo": "Bando  affitti 2026", "slug": "123", "dataScadenza": "2026-12-31T23:59:00",
                     "documentiList": DOCUMENTI, "tipoSoggetto": "Comune"}},
        {"_source": {"titolo": "Lavori stradali", "slug": "456", "cig": "B1234", "documentiList": []}}]}}
    monkeypatch.setattr(ar, "post_json", lambda url, corpo, giorno: risposta)
    [b] = ar.bandi_sardegna("2026-11-07")
    assert b["titolo"] == "Bando affitti 2026" and b["scadenza"] == "2026-12-31"
    assert b["pdf"] == "https://files.regione.sardegna.it/x/bando.pdf"
    assert b["url"].endswith("/bandi/123") and b["pubblicato_da"] == "Comune"
