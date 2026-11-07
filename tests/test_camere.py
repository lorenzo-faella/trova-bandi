"""Pagine elenco delle Camere di commercio ricavate dai link del portale: cartelle buone, scartate, controlli."""
from pipeline.fonti import camere as cc


def voce(url, ente="Camera di Commercio di Modena", anno="2026", regione="Emilia-Romagna"):
    return {"Soggetto_Concedente": [ente], "Link_istituzionale": url, "Data_apertura": f"{anno}-03-01", "Regioni": [regione]}


def test_cartella_piu_frequente_con_un_nome_da_bandi():
    export = [voce("https://www.mo.camcom.it/promozione/contributi-camerali/bandi/bando-a"),
              voce("https://www.mo.camcom.it/promozione/contributi-camerali/bandi/bando-b"),
              voce("https://www.mo.camcom.it/notizie/una-notizia"),                                   # non è una cartella da bandi
              voce("https://www.mo.camcom.it/amministrazione-trasparente/bandi/x"),                     # trasparenza: no
              voce("https://www.mo.camcom.it/promozione/contributi-camerali/bandi/vecchio", anno="2021"),  # troppo vecchio
              voce("https://www.comune.it/bandi/x", ente="Comune di Modena")]                           # non è una Camera
    c = cc.candidati(export)
    assert list(c) == ["www.mo.camcom.it"]
    assert c["www.mo.camcom.it"]["cartelle"].most_common() == [("/promozione/contributi-camerali/bandi", 2)]


def test_pagine_di_un_singolo_bando_e_concorsi_non_sono_elenchi():
    for percorso in ["/x/bando-temporary-shop_886", "/servizio/bando-pid-voucher-2022", "/pagina199048_bando-turismo.html"]:
        assert cc.SINGOLO.search(percorso)
    assert not cc.SINGOLO.search("/promozione/bandi")
    assert cc.CARTELLA_NO.search("/bandi-di-concorso") and cc.CARTELLA_NO.search("/avvisi-gare-e-contratti")


def test_siti_camerali_soltanto():
    assert cc.SITO_CAMERALE.search("www.bs.camcom.it") and cc.SITO_CAMERALE.search("www.handelskammer.bz.it")
    assert not cc.SITO_CAMERALE.search("www.confindustriabrescia.it") and not cc.SITO_CAMERALE.search("www.promositalia.com")
