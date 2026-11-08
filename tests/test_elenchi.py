"""Raccolta dalle pagine elenco, con un sito finto: paginazione, filtri sui link, PDF principale."""
from pipeline.fonti import elenchi as el

FONTE = {"id": "prova", "ente": "Regione Prova", "livello": "regionale", "regione": "Prova", "pubblico": "persone",
         "pagine": "https://regione.prova.it/bandi?page={n}", "prima_pagina": 0,
         "link_bando": r"^https://regione\.prova\.it/bandi/[a-z0-9-]+$", "escludi": r"/bandi/archivio",
         "allegato": [r"^bando\b", r"^allegato a\b"]}

PAGINE = {
    "https://regione.prova.it/bandi?page=0": '<a href="/bandi/affitti-2026">Per saperne di più su Contributo affitti 2026</a>'
                                             '<a href="/bandi/archivio">Archivio</a><a href="/chi-siamo">Chi siamo</a>',
    "https://regione.prova.it/bandi?page=1": '<a href="/bandi/nidi-2026">Bonus nidi 2026</a>'
                                             '<a href="/bandi/affitti-2026">Contributo affitti 2026</a>',
    "https://regione.prova.it/bandi?page=2": '<a href="/bandi/affitti-2026">Contributo affitti 2026</a>',  # niente di nuovo
    "https://regione.prova.it/bandi/affitti-2026": '<main><h1>Contributo affitti 2026</h1><p>Requisiti: ISEE fino a 15.000 euro.</p>'
                                                   '<a href="/files/modulo.pdf">Modulo di domanda</a>'
                                                   '<a href="/files/allegato-a.pdf">Allegato A - criteri</a>'
                                                   '<a href="/files/bando.pdf">Bando affitti 2026</a></main>',
}


def finto(richieste):
    def scarica(url, giorno=None):
        richieste.append(url)
        return PAGINE.get(url, "").encode(), "text/html", ""
    return scarica


def test_legge_tutte_le_pagine_e_si_ferma_senza_link_nuovi(monkeypatch):
    monkeypatch.setattr(el.time, "sleep", lambda s: None)
    richieste = []
    bandi = el.bandi_in_elenco(FONTE, "2026-11-07", finto(richieste))
    assert bandi == {"https://regione.prova.it/bandi/affitti-2026": "Contributo affitti 2026",
                     "https://regione.prova.it/bandi/nidi-2026": "Bonus nidi 2026"}
    assert richieste[-1].endswith("page=2")  # la pagina 2 non porta niente di nuovo: ci si ferma lì


def test_allegato_principale_segue_l_ordine_di_preferenza():
    pagina = PAGINE["https://regione.prova.it/bandi/affitti-2026"]
    assert el.allegato_principale(pagina, "https://regione.prova.it/bandi/affitti-2026", FONTE) == \
        "https://regione.prova.it/files/bando.pdf"
    solo_allegato = {**FONTE, "allegato": [r"^allegato a\b"]}
    assert el.allegato_principale(pagina, "https://regione.prova.it/", solo_allegato).endswith("allegato-a.pdf")
    assert el.allegato_principale(pagina, "https://regione.prova.it/", {**FONTE, "allegato": None}) is None


def test_raccogli_bando_produce_un_documento_completo(monkeypatch):
    monkeypatch.setattr(el.time, "sleep", lambda s: None)
    doc = el.raccogli_bando({**FONTE, "allegato": None}, "https://regione.prova.it/bandi/affitti-2026",
                            "Contributo affitti 2026", "2026-11-07", finto([]))
    assert doc["id"].startswith("prova-contributo-affitti-2026-") and len(doc["id"]) == len("prova-contributo-affitti-2026-") + 6 and doc["pubblico"] == "persone"
    assert "ISEE fino a 15.000 euro" in doc["pagine"][0] and doc["fonte_elenco"] == "prova"


def test_slug_e_titoli_puliti():
    assert el.slug("Contributo per l’acquisto della prima casa – 2026") == "contributo-per-lacquisto-della-prima-casa-2026"
    assert el.link('<a href="/x">Per saperne di più su Bonus nidi</a>', "https://a.it/") == [("https://a.it/x", "Bonus nidi")]


def test_link_senza_virgolette_come_in_sicilia():
    pagina = '<a class="x" href=/system/files/2026-06/determina%20112.pdf title="Scarica Allegato">Scarica Allegato</a>'
    assert el.link(pagina, "https://www.regione.sicilia.it/bandi/x") == \
        [("https://www.regione.sicilia.it/system/files/2026-06/determina%20112.pdf", "Scarica Allegato")]


def test_escludi_contesto_stato_scritto_prima_del_link(monkeypatch):
    monkeypatch.setattr(el.time, "sleep", lambda s: None)
    pagina = ('FSE Aperto <a href="/avvisi/fse/dote-giovani">Dote Lavoro Giovani</a> Scadenza 31/12/2026 '
              'FESR Chiuso <a href="/avvisi/fesr/valanghe">Rischio valanghivo</a> Scadenza 09/10/2026')
    fonte = {"pagine": "https://r.it/avvisi", "link_bando": r"/avvisi/(fse|fesr)/", "escludi_contesto": r"\bChiuso\b"}
    bandi = el.bandi_in_elenco(fonte, "2026-11-07", lambda u, g: (pagina.encode(), "text/html", ""))
    assert bandi == {"https://r.it/avvisi/fse/dote-giovani": "Dote Lavoro Giovani"}


def test_piu_pagine_elenco_fisse(monkeypatch):
    monkeypatch.setattr(el.time, "sleep", lambda s: None)
    pagine = {"https://r.it/a": '<a href="/b/uno">Bando uno</a>', "https://r.it/b": '<a href="/b/due">Bando due</a>'}
    fonte = {"pagine": ["https://r.it/a", "https://r.it/b"], "link_bando": r"/b/"}
    assert len(el.bandi_in_elenco(fonte, "2026-11-07", lambda u, g: (pagine[u].encode(), "text/html", ""))) == 2


def test_testi_generici_non_sono_titoli():
    pagina = ('<a href="/b/uno">DETTAGLI</a><a href="/b/due">Per maggiori informazioni</a><a href="/b/tre">:</a>'
              '<a href="/b/quattro">Microimprese Approfondisci</a><a href="/b/cinque">https://r.it/b/cinque</a>')
    assert [t for _, t in el.link(pagina, "https://r.it/")] == ["", "", "", "Microimprese", ""]


def test_vale_il_testo_piu_lungo_tra_i_link_allo_stesso_bando(monkeypatch):
    # Finpiemonte: ogni misura ha il link col titolo e poi "DETTAGLI"; prima vinceva l'ultimo.
    monkeypatch.setattr(el.time, "sleep", lambda s: None)
    pagina = '<a href="/agevolazioni/fuc">Fondo unico commercio 2025</a><a href="/agevolazioni/fuc">DETTAGLI</a>'
    fonte = {"pagine": "https://r.it/agevolazioni", "link_bando": r"/agevolazioni/\w+$"}
    assert el.bandi_in_elenco(fonte, "2026-11-07", lambda u, g: (pagina.encode(), "text/html", "")) == \
        {"https://r.it/agevolazioni/fuc": "Fondo unico commercio 2025"}


def test_link_solo_generici_con_titolo_dalla_pagina(monkeypatch):
    # Gepafin: il link dice solo "Per maggiori informazioni"; senza titolo_dalla_pagina il bando non si vede.
    monkeypatch.setattr(el.time, "sleep", lambda s: None)
    pagina = '<a href="/servizi/bando-step-2026/">Per maggiori informazioni</a>'
    fonte = {"pagine": "https://g.it/servizi/", "link_bando": r"/servizi/[a-z0-9-]+/$"}
    scarica = lambda u, g: (pagina.encode(), "text/html", "")
    assert el.bandi_in_elenco(fonte, "2026-11-07", scarica) == {}
    assert el.bandi_in_elenco({**fonte, "titolo_dalla_pagina": True}, "2026-11-07", scarica) == \
        {"https://g.it/servizi/bando-step-2026/": ""}


def test_titolo_da_prende_il_titolo_nella_pagina(monkeypatch):
    # Sardegna Ricerche: la prima riga lunga è "Vai al contenuto della pagina", il titolo sta dopo "Oggetto:".
    monkeypatch.setattr(el.time, "sleep", lambda s: None)
    pagina = (b"<p>Vai al contenuto della pagina</p><p>Bandi</p><p>Oggetto: Programma PoC in Biomedicina - NEXT</p>"
              b"<p>Scadenza: 31/12/2027</p>")
    fonte = {**FONTE, "allegato": None, "titolo_da": r"^Oggetto:\s*(.+)$"}
    doc = el.raccogli_bando(fonte, "https://r.it/bandi?id=1", "", "2026-11-07", lambda u, g: (pagina, "text/html", ""))
    assert doc["titolo"] == "Programma PoC in Biomedicina - NEXT"
    senza = el.raccogli_bando({**fonte, "titolo_da": None}, "https://r.it/bandi?id=1", "", "2026-11-07",
                              lambda u, g: (pagina, "text/html", ""))
    assert senza["titolo"] == "Vai al contenuto della pagina"  # il comportamento di prima, per le altre fonti


def test_titolo_da_cerca_anche_nel_title_della_pagina(monkeypatch):
    monkeypatch.setattr(el.time, "sleep", lambda s: None)
    pagina = b"<title>BANDO STEP 2026 - Gepafin</title><p>Per qualsiasi richiesta di info scrivere a info@g.it</p>"
    fonte = {**FONTE, "allegato": None, "titolo_da": r"^(.+?) - Gepafin$"}
    doc = el.raccogli_bando(fonte, "https://g.it/servizi/step/", "", "2026-11-07", lambda u, g: (pagina, "text/html", ""))
    assert doc["titolo"] == "BANDO STEP 2026"


def test_allegato_nome_file_quando_i_link_dicono_download():
    pagina = ('<a href="/components/x/download.php?id=1:domanda.pdf">Download</a>'
              '<a href="/components/x/download.php?id=2:edifici-pubblici-v-bando.pdf">Download</a>'
              '<a href="/files/avviso-hub.pdf">Download</a>')
    fonte = {"allegato": ["bando", "avviso"], "allegato_nome_file": True}
    assert el.allegato_principale(pagina, "https://f.it/", fonte) == \
        "https://f.it/components/x/download.php?id=2:edifici-pubblici-v-bando.pdf"  # FILSE: il nome sta dopo "?"
    assert el.allegato_principale(pagina, "https://f.it/", {**fonte, "allegato": ["avviso"]}) == "https://f.it/files/avviso-hub.pdf"
    assert el.allegato_principale(pagina, "https://f.it/", {"allegato": ["bando"]}) is None  # senza l'opzione, come prima


def test_allegati_finlombarda_sono_documenti():
    pagina = '<a href="/it/attachments/file/view?hash=abc&inLine=1">01. Avviso alle imprese</a>'
    assert el.allegato_principale(pagina, "https://www.finlombarda.it/x", {"allegato": [r"\bavviso\b"]}) == \
        "https://www.finlombarda.it/it/attachments/file/view?hash=abc&inLine=1"


def test_testo_bando_tiene_solo_i_link_che_parlano_di_contributi(monkeypatch):
    # FVG: le pagine di settore elencano anche foglie solo informative ("Affittacamere").
    monkeypatch.setattr(el.time, "sleep", lambda s: None)
    pagina = ('<a href="/turismo/FOGLIA205/">Affittacamere Strutture con non più di sei camere</a>'
              '<a href="/turismo/FOGLIA83/">Contributi per le unità abitative ammobiliate</a>')
    fonte = {"pagine": "https://r.it/turismo/", "link_bando": r"/FOGLIA\d+/$", "testo_bando": r"contribut|incentiv"}
    assert list(el.bandi_in_elenco(fonte, "2026-11-07", lambda u, g: (pagina.encode(), "text/html", ""))) == \
        ["https://r.it/turismo/FOGLIA83/"]


def test_solo_mancanti_riprova_le_voci_senza_documento(tmp_path):
    import json
    elenchi, documenti = tmp_path / "elenchi", tmp_path / "documenti"
    elenchi.mkdir(); documenti.mkdir()
    (elenchi / "fvg_2026-11-06.json").write_text(json.dumps({"bandi": [{"url": "u0", "titolo": "vecchio"}]}))
    (elenchi / "fvg_2026-11-07.json").write_text(json.dumps({"bandi": [{"url": "u1", "titolo": "A"}, {"url": "u2", "titolo": "B"}]}))
    (documenti / "fvg-a-123456.json").write_text(json.dumps({"fonte_elenco": "fvg", "url": "u1"}))
    assert el.mancanti("fvg", elenchi, documenti) == {"u2": "B"}  # vale l'ultimo elenco; u1 è già salvato


def test_link_js_legge_l_indirizzo_dal_comando_javascript(monkeypatch):
    monkeypatch.setattr(el.time, "sleep", lambda s: None)
    pagina = ('<a class="x" href="#" onclick="ApriSchedaBando(event, &#39;iniziative-in-atto/voucher-formativi&#39;);">'
              'Voucher formativi a favore delle piccole imprese</a><a href="#">Torna su</a>')
    fonte = {"pagine": "https://lavoro.r.it/bandi-e-avvisi/bandi-e-avvisi", "link_bando": r"/iniziative-in-atto/",
             "link_js": r"ApriSchedaBando\(event,\s*'([^']+)'\)"}
    assert el.bandi_in_elenco(fonte, "2026-11-08", lambda u, g: (pagina.encode(), "text/html", "")) == \
        {"https://lavoro.r.it/iniziative-in-atto/voucher-formativi": "Voucher formativi a favore delle piccole imprese"}


def test_dal_portale_prende_i_bandi_aperti_di_quel_sito():
    export = [
        {"Titolo": "Contributo prima casa", "Link_istituzionale": "https://www.provincia.tn.it/Servizi/Prima-casa#accedere",
         "Data_apertura": "2026-01-01T00:00:00", "Data_chiusura": "2026-12-31T00:00:00"},
        {"Titolo": "Contributo prima casa (doppione)", "Link_istituzionale": "https://www.provincia.tn.it/Servizi/Prima-casa",
         "Data_apertura": "2026-01-01", "Data_chiusura": None},
        {"Titolo": "Bando chiuso", "Link_istituzionale": "https://www.provincia.tn.it/Servizi/Vecchio",
         "Data_apertura": "2025-01-01", "Data_chiusura": "2026-10-30"},
        {"Titolo": "Non ancora aperto", "Link_istituzionale": "https://www.provincia.tn.it/Servizi/Futuro",
         "Data_apertura": "2027-01-01", "Data_chiusura": None},
        {"Titolo": "Altro sito", "Link_istituzionale": "https://civis.bz.it/it/servizi/servizio.html?id=1",
         "Data_apertura": None, "Data_chiusura": None},
    ]
    fonte = {**FONTE, "dal_portale": r"^https://www\.provincia\.tn\.it/Servizi/"}
    # il frammento "#accedere" si toglie, così le due voci dello stesso servizio diventano una
    assert el.bandi_dal_portale(fonte, "2026-11-08", export) == {
        "https://www.provincia.tn.it/Servizi/Prima-casa": "Contributo prima casa"}


def test_la_pausa_della_fonte_vale_solo_se_si_scarica(monkeypatch, tmp_path):
    attese = []
    monkeypatch.setattr(el.time, "sleep", attese.append)
    monkeypatch.setattr(el.dc, "attesa", lambda url, minimo=None: max(3, minimo or 0))
    monkeypatch.setattr(el.dc, "file_cache", lambda url, giorno: tmp_path / ("c" if "copia" in url else "x"))
    (tmp_path / "c").write_text("già scaricato")
    el.pausa("https://lento.it/nuovo", "2026-11-08", 10)
    el.pausa("https://lento.it/copia", "2026-11-08", 10)
    assert attese == [10]


def test_vai_alla_notizia_non_e_un_titolo():
    assert el.GENERICO.match("Vai alla notizia")
