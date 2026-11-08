"""Fonti dei comuni ricavate dalla home: pagina "Avvisi", notizie leggibili, motivi quando non si può."""
from pipeline.fonti import comuni as co

HOME = '<a href="/servizi">Servizi</a><a href="/novita/avvisi">Avvisi</a><a href="https://altro.it/avvisi">Avvisi</a>'
AVVISI = ('<a href="/novita/avvisi">Avvisi</a>'
          '<a href="/novita/contributo-famiglie-numerose-2026/">Contributo famiglie numerose anno 2026</a>'
          '<a href="/novita/sciopero-generale-nazionale/">Sciopero generale nazionale del 14 novembre</a>'
          '<a href="/novita/bando-libri-di-testo-2026/">Bando contributo libri di testo 2026-2027</a>'
          '<a href="/servizi/anagrafe">Servizi della categoria anagrafe e stato civile</a>')


def finto(pagine):
    def scarica(url, giorno=None):
        if url not in pagine:
            raise OSError("404")
        return pagine[url].encode(), "text/html", ""
    return scarica


def test_trova_la_pagina_avvisi_nel_menu_dello_stesso_sito():
    assert co.pagina_avvisi(HOME, "https://www.comune.prova.it") == "https://www.comune.prova.it/novita/avvisi"


def test_fonte_con_filtri_sul_titolo(monkeypatch):
    monkeypatch.setattr(co.time, "sleep", lambda s: None)
    monkeypatch.setattr(co.dc, "attesa", lambda url, minimo=None: 0)
    pagine = {"https://www.comune.prova.it": HOME, "https://www.comune.prova.it/novita/avvisi": AVVISI}
    fonte, motivo = co.prova({"nome": "Prova Città", "regione": "Umbria", "home": "https://www.comune.prova.it"},
                             "2026-11-08", finto(pagine))
    assert motivo is None and fonte["id"] == "comune-prova-citta" and fonte["comune"] == "Prova Città"
    assert (fonte["notizie_in_pagina"], fonte["pertinenti_oggi"]) == (3, 2)  # lo sciopero non è un bando


def test_motivi_quando_non_si_puo(monkeypatch):
    monkeypatch.setattr(co.time, "sleep", lambda s: None)
    monkeypatch.setattr(co.dc, "attesa", lambda url, minimo=None: 0)
    c = {"nome": "Vuota", "regione": "Lazio", "home": "https://www.comune.vuota.it"}
    assert "non risponde" in co.prova(c, "2026-11-08", finto({}))[1]
    pagine = {"https://www.comune.vuota.it": HOME, "https://www.comune.vuota.it/novita/avvisi": '<div id="app"></div>'}
    assert "JavaScript" in co.prova(c, "2026-11-08", finto(pagine))[1]
