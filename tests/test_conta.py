"""Controllo dopo la raccolta: voci dell'elenco contro documenti salvati."""
from pipeline.fonti import conta


def test_trova_mancanti_doppi_e_fuori_elenco():
    elenco = {"fonte": "f", "bandi": [{"url": "u1"}, {"url": "u2"}, {"url": "u3"}]}
    documenti = [{"id": "f-a", "url": "u1"}, {"id": "f-a-vecchio", "url": "u1"}, {"id": "f-b", "url": "u2"},
                 {"id": "f-chiuso", "url": "u9"}]
    r = conta.controlla(elenco, documenti)
    assert (r["voci"], r["salvati"], r["mancanti"]) == (3, 2, ["u3"])
    assert r["doppi"] == {"u1": ["f-a", "f-a-vecchio"]} and r["fuori_elenco"] == ["f-chiuso"]
