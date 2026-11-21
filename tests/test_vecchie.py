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
