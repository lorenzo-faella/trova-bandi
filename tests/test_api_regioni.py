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


def test_bandi_lombardia_legge_le_schede_e_scarta_concorsi_e_gare(monkeypatch):
    def scheda(destinatari, tipologia, href, titolo, chiusura):
        return (f'<div class="card card-bg card-big"><span class="categoria" ><svg class="icon"><use xlink:href="/s.svg#it-aria-{ {'Cittadini': 'citizen', 'Imprese': 'factory'}[destinatari] }"></use></svg> {destinatari} </span>'
                f'<input class="checkCloseDate" type="hidden" value="{chiusura} 12:00" /><p class="mt-1" >{tipologia}</p>'
                f'<a class="text-decoration-none" href="/servizi/servizio/catalogo/dettaglio/{href}"><img src="x.jpg" alt="{titolo}"></a></div>')
    pagina = ("Pagina 1 di 1" + scheda("Cittadini", "Bando", "casa/sap-RLH1", "Domande di alloggi SAP", "2026-12-31")
              + scheda("Cittadini", "Concorsi Pubblici e Avvisi sul Personale", "x/borse-RLA1", "Borse di studio", "2026-12-09")
              + scheda("Imprese", "Bando", "x/fec-RLF1", "FEC 38 - Acquisizione del servizio di pulizia", "2026-12-01")
              + scheda("Imprese", "Bando", "x/nuova-impresa-RLF2", "Nuova Impresa 2026", "2026-11-30"))
    monkeypatch.setattr(ar, "post_form", lambda url, campi, giorno: pagina)
    bandi = ar.bandi_lombardia("2026-11-07")
    assert [(b["titolo"], b["pubblico"], b["scadenza"]) for b in bandi] == [
        ("Domande di alloggi SAP", "persone", "2026-12-31"), ("Nuova Impresa 2026", "imprese", "2026-11-30")]
    assert bandi[0]["url"] == "https://www.bandi.regione.lombardia.it/servizi/servizio/catalogo/dettaglio/casa/sap-RLH1"
