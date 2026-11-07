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


def test_bandi_veneto_legge_le_pagine_per_numero(monkeypatch):
    def pagina(titolo, scadenza, categoria, allegati):
        a = "".join(f'<a href="/Public/Download?idAllegato={i}">{t}</a>' for i, t in allegati)
        return (f"<main><p>{titolo}</p><p>Oggetto</p><p>testo</p><p>Scadenza:</p><p>{scadenza} 23:59</p>"
                f"<p>Categoria</p><p>{categoria}</p><p>Destinatari</p><p>Cittadino</p>{a}</main>").encode()
    pagine = {"Index": b'<a href="/Public/Dettaglio?idAtto=100">x</a>',
              "Dettaglio?idAtto=100": pagina("Contributi affitti 2026", "31/12/2026", "Finanziamento",
                                             [(1, "Modulo domanda"), (2, "Bando affitti 2026")]),
              "Dettaglio?idAtto=99": pagina("Concorso istruttori", "31/12/2026", "Concorso", []),
              "Dettaglio?idAtto=98": pagina("Bando scaduto", "01/01/2026", "Finanziamento", [])}
    monkeypatch.setattr(ar.dc, "scarica", lambda url, g: (pagine.get(url.replace(ar.VENETO_BASE, ""), b"<p>errore</p>"), "text/html", ""))
    monkeypatch.setattr(ar.dc, "file_cache", lambda url, g: type("C", (), {"exists": lambda self: True})())
    monkeypatch.setattr(ar, "VENETO_QUANTI", 30)
    [b] = ar.bandi_veneto("2026-11-07")
    assert (b["titolo"], b["scadenza"], b["pubblico"]) == ("Contributi affitti 2026", "2026-12-31", "persone")
    assert b["pdf"].endswith("idAllegato=2")  # il bando, non il modulo


def scheda_finlombarda(n, titolo, stato="Aperto"):
    return (f'<div class="card-prodotti-servizi"><div class="status status-aperto">{stato}</div>'
            f'<div class="info-destinatario"><span class="mdi"></span>Micro imprese <span></span>PMI </div>'
            f'<p class="h5"><a href="/it/prodotti-e-servizi/prodotti-servizi/{n}/x-{n}">{titolo}</a></p></div>')


def test_finlombarda_legge_le_schede_e_si_ferma_quando_le_pagine_si_ripetono(monkeypatch):
    import json
    # Oltre l'ultima pagina il sito ripete l'ultima: ci si ferma lì, per ogni pubblico e ogni stato.
    pagine = {1: scheda_finlombarda(80, "Re-IMPRESA") + scheda_finlombarda(81, "Gara servizi di pulizia - procedura aperta"),
              2: scheda_finlombarda(52, "MICROCREDITO")}
    richieste = []
    def get_xhr(url, giorno):
        richieste.append(url)
        pagina = int(url.rsplit("page=", 1)[1])
        return json.dumps(pagine.get(pagina, pagine[2]))
    monkeypatch.setattr(ar, "get_xhr", get_xhr)
    monkeypatch.setattr(ar.time, "sleep", lambda s: None)
    bandi = ar.bandi_finlombarda("2026-11-07")
    assert [b["titolo"] for b in bandi] == ["Re-IMPRESA", "MICROCREDITO"]  # la gara si scarta, niente doppioni
    assert bandi[0]["url"] == "https://www.finlombarda.it/it/prodotti-e-servizi/prodotti-servizi/80/x-80"
    assert bandi[0]["destinatari"] == "Micro imprese PMI" and bandi[0]["pubblico"] == "imprese"
    assert len(richieste) == 2 * 2 * 3  # 2 pubblici x 2 stati x (pagine 1, 2 e la 3 che ripete la 2)


def test_trentino_sviluppo_solo_attivi_e_pdf_della_risposta(monkeypatch):
    risposta = {"data": [
        {"title": "Bando Fare impresa", "url": "/it/bandi/attivi/fare-impresa", "active": True,
         "date": "Scade il 30 giugno 2027 Ore 12:00", "relatedDocumentUrl": "/doc/bando.pdf"},
        {"title": "Servizi alle imprese", "url": "/it/bandi/attivi/servizi", "active": True, "date": "",
         "relatedDocumentUrl": "/it/pagina"},
        {"title": "Bando vecchio", "url": "/it/bandi/scaduti/x", "active": False}]}
    monkeypatch.setattr(ar, "post_json", lambda url, corpo, giorno: risposta)
    a, b = ar.bandi_trentino_sviluppo("2026-11-07")
    assert (a["scadenza"], a["pdf"]) == ("2027-06-30", "https://www.trentinosviluppo.it/doc/bando.pdf")
    assert b["pdf"] is None and b["scadenza"] is None  # il documento collegato non è un PDF


def test_calabria_europa_stati_aperti_e_scarti(monkeypatch):
    def voce(titolo, stato, beneficiari=("Imprese",)):
        return {"titolo_wp": titolo, "url_wp": f"https://calabriaeuropa.regione.calabria.it/bando/{len(titolo)}/",
                "cem_status": stato, "deleted_at": None, "cem_department": "<p>Lavoro</p>",
                "tag_destinatari": ["Imprese"], "tag_beneficiari_ufficiali": list(beneficiari)}
    catalogo = {"bandi": [voce("FRI Calabria", "opened"), voce("Sezioni primavera", "prepublished", ("Cittadini",)),
                          voce("Avviso Caro Carburante", "published", ("Imprese", "Altro")),
                          voce("Avviso chiuso", "ended"), voce("Avviso Pubblico di selezione esperti", "published")]}
    monkeypatch.setattr(ar, "get_json", lambda url, giorno: catalogo)
    bandi = ar.bandi_calabria_europa("2026-11-07")
    assert [(b["titolo"], b["tipologia"], b["pubblico"]) for b in bandi] == [
        ("FRI Calabria", "aperto", "imprese"), ("Sezioni primavera", "pre-informazione", "persone"),
        ("Avviso Caro Carburante", "pubblicato", None)]
    assert bandi[0]["pubblicato_da"] == "Lavoro"


def test_documento_tiene_il_pdf_dato_dall_elenco(monkeypatch):
    # Se l'elenco dà già il PDF (Trentino Sviluppo), non lo si sostituisce con un link trovato nella pagina.
    pagine = {"https://t.it/bando": b'<main><p>Testo del bando</p><a href="/files/altro.pdf">Bando vecchio</a></main>',
              "https://t.it/giusto.pdf": b"%PDF-finto"}
    monkeypatch.setattr(ar.dc, "scarica", lambda url, g: (pagine[url], "text/html", ""))
    monkeypatch.setattr(ar.dc, "file_cache", lambda url, g: type("C", (), {"exists": lambda self: True})())
    monkeypatch.setattr(ar.dc, "testo_pdf", lambda dati: {"pagine": ["testo pdf"], "ocr_necessario": False})
    fonte = {"id": "t", "ente": "T", "livello": "regionale", "regione": "Trentino-Alto Adige", "allegato": [r"bando"]}
    doc = ar.documento(fonte, {"url": "https://t.it/bando", "titolo": "Bando", "testo": None,
                               "pdf": "https://t.it/giusto.pdf"}, "2026-11-07")
    assert doc["allegato"] == "https://t.it/giusto.pdf" and doc["pagine"][1] == "testo pdf"


def test_data_italiana():
    assert ar.data_italiana("Scade il 1 marzo 2027 Ore 12:00") == "2027-03-01"
    assert ar.data_italiana("Sempre aperto") is None
