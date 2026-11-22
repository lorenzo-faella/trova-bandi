"""Le regole probabilmente scadute (decisione 91)."""
import datetime as dt

from pipeline.vecchie import anno_piu_recente, segnalazioni

OGGI = dt.date(2026, 11, 21)


def test_anno_piu_recente():
    assert anno_piu_recente("Bando 2023-2024") == 2024
    assert anno_piu_recente("Borse a.a. 2025/2026") == 2026
    assert anno_piu_recente("Borse a.a. 2025-26") == 2026
    assert anno_piu_recente("Contributo affitto") is None


def test_segnala_solo_le_vecchie_senza_chiusura_futura():
    regole = [{"titolo": "Bando 2024", "chiusura": None},
              {"titolo": "Bando 2024", "chiusura": "2026-12-31"},  # prorogato: aperto
              {"titolo": "Borse a.a. 2025/2026", "chiusura": None},
              {"titolo": "Servizio", "apertura": "2019-01-01", "chiusura": None}]
    fuori, _ = segnalazioni(regole, OGGI)
    assert [r["titolo"] for r, _ in fuori] == ["Bando 2024", "Servizio"]


def test_scadenza_scritta_nel_testo():
    from pipeline.vecchie import scadenza_nel_testo
    assert scadenza_nel_testo("Data pubblicazione: 11/12/2024 Data scadenza: 31/12/2025 entro le 23:59") == dt.date(2025, 12, 31)
    assert scadenza_nel_testo("DATA DI CHIUSURA Ore 12:00 del 15/06/2021") == dt.date(2021, 6, 15)
    assert scadenza_nel_testo("Data scadenza: 24 ottobre 2026") == dt.date(2026, 10, 24)
    assert scadenza_nel_testo("domande entro il 2027") is None


def test_segnala_la_scadenza_del_testo_e_salta_le_controllate():
    regole = [{"id": "a", "titolo": "Contributo lavastoviglie", "chiusura": None, "_testo": "Data scadenza: 31/12/2025"},
              {"id": "b", "titolo": "Contributo", "chiusura": None, "_testo": "Data scadenza: 31/12/2027"},
              {"id": "c", "titolo": "L.R. 34/2004 Consulenza", "chiusura": None},
              {"id": "d", "titolo": "Bando 2024", "chiusura": "2024-06-30"}]  # chiusa: la demo la nasconde già
    fuori, _ = segnalazioni(regole, OGGI, controllate={"c"})
    assert [r["id"] for r, _ in fuori] == ["a"]
