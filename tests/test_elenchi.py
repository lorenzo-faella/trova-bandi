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
