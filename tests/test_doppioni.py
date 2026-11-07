"""Doppioni tra fonti: stesso titolo normalizzato e stessa regione, titoli generici esclusi."""
from pipeline.fonti import doppioni as dp


def doc(i, titolo, url, regione="Lazio", pdf=False):
    return {"id": i, "titolo": titolo, "url": url, "regione": regione, "tipo": "html", "allegato": "x.pdf" if pdf else None}


def test_stesso_bando_su_due_siti_tiene_quello_con_il_pdf():
    g = dp.gruppi([doc("europa-valore", "Valore Artigiano 2026 – contributi", "https://a.it/1"),
                   doc("innova-valore", "Valore artigiano 2026 contributi", "https://b.it/2", pdf=True),
                   doc("altro", "Contributi allo spettacolo dal vivo 2027", "https://b.it/3")])
    assert g == [{"regione": "Lazio", "titolo": "Valore artigiano 2026 contributi", "ids": ["innova-valore", "europa-valore"]}]


def test_titoli_generici_e_regioni_diverse_non_sono_doppioni():
    assert dp.gruppi([doc("a", "Avviso pubblico", "https://a.it/1"), doc("b", "Avviso pubblico", "https://a.it/2")]) == []
    assert dp.gruppi([doc("a", "Bando affitti anno 2026", "https://a.it/1", "Lazio"),
                      doc("b", "Bando affitti anno 2026", "https://b.it/1", "Puglia")]) == []
