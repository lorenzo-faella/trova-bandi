"""Bandi salvati a mano: testo estratto come per gli altri documenti, e segnati come "manuale"."""
from pipeline.fonti import manuali as ma


def test_documento_da_una_pagina_salvata(tmp_path):
    (tmp_path / "affitto.html").write_text("<html><head><title>Contributo affitto</title></head><body><main>"
                                           "<h1>Contributo affitto under 35</h1><p>Possono fare domanda i residenti a Milano "
                                           "con meno di 35 anni e un contratto di locazione registrato.</p></main></body></html>",
                                           encoding="utf-8")
    voce = {"id": "milano-affitto-under-35", "titolo": "Contributo affitto under 35", "ente": "Comune di Milano",
            "livello": "comunale", "regione": "Lombardia", "comune": "Milano", "pubblico": "persone",
            "url": "https://www.comune.milano.it/prova", "file": "affitto.html", "salvato": "2026-11-09"}
    doc = ma.documento(voce, tmp_path)
    assert doc["fonte_elenco"] == "manuale" and doc["scaricato"] == "2026-11-09" and doc["comune"] == "Milano"
    assert "contratto di locazione registrato" in " ".join(doc["pagine"])


def test_inventario_non_conta_i_manuali_come_sito_sorvegliato():
    from pipeline.fonti import inventario as inv
    export = [{"Regioni": ["Lombardia"], "Soggetto_Concedente": ["Comune di Milano"], "Link_istituzionale": "https://www.comune.milano.it/a",
               "Data_apertura": "2026-01-01", "Data_chiusura": "2026-12-31"}]
    documenti = [{"regione": "Lombardia", "url": "https://www.comune.milano.it/a", "fonte_elenco": "manuale"}]
    [e] = inv.inventario(export, documenti, "2026-11-09")[0]["Lombardia"]
    assert (e["aperti_coperti"], e["aperti_dal_portale"]) == (0, 1)
