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
    assert doc["id"] == "prova-contributo-affitti-2026" and doc["pubblico"] == "persone"
    assert "ISEE fino a 15.000 euro" in doc["pagine"][0] and doc["fonte_elenco"] == "prova"


def test_slug_e_titoli_puliti():
    assert el.slug("Contributo per l’acquisto della prima casa – 2026") == "contributo-per-lacquisto-della-prima-casa-2026"
    assert el.link('<a href="/x">Per saperne di più su Bonus nidi</a>', "https://a.it/") == [("https://a.it/x", "Bonus nidi")]
