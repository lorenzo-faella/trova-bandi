"""Segnalazioni automatiche sulle regole estratte (pipeline/sospette.py, decisione 64)."""
from pipeline.citazioni import forme
from pipeline.sospette import DATA, GEOGRAFIA, INVERTITE, LAVORO, SOGLIA, SOLO_NM, data_nel_testo, segnalazioni


def regola(requisiti, titolo="Contributo affitto", **altro):
    return {"id": "prova", "titolo": titolo, "link": "x", "requisiti": requisiti, **altro}


def tipi(r, testo):
    return {t for t, _ in segnalazioni(r, testo)}


def test_date_nelle_forme_italiane():
    assert data_nel_testo("2027-01-31", "domande entro il 31/01/2027 alle 12")
    assert data_nel_testo("2027-01-31", "scade il 31 gennaio")
    assert data_nel_testo("2026-02-01", "dal 1° febbraio")
    assert not data_nel_testo("2027-01-31", "scade il 30/01/2027")


def test_decimali_con_il_punto_delle_migliaia():
    assert "19.837,92" in forme(19837.92) and "77.010,60" in forme(77010.6)


def test_segnalazioni():
    testo = "ISEE non superiore a 20.000 euro. Domande dal 1/10/2026 al 31/10/2026."
    ok = regola([{"campo": "isee", "operatore": "<=", "valore": 20000}], apertura="2026-10-01", chiusura="2026-10-31")
    assert tipi(ok, testo) == set()
    inventata = regola([{"campo": "isee", "operatore": "<=", "valore": 25000}], chiusura="2026-11-30")
    assert tipi(inventata, testo) == {SOGLIA, DATA}
    assert INVERTITE in tipi(regola([], apertura="2026-11-01", chiusura="2026-10-01"), "")
    assert LAVORO in tipi(regola([{"campo": "isee", "operatore": "<=", "valore": 1}], titolo="Congedo parentale"), "")
    assert tipi(regola([{"non_modellabile": "x", "citazione": "y"}]), "") == {SOLO_NM}


def test_nomi_geografici_fuori_elenco():
    """Decisione 73: "Trentino-Alto Adige" senza la parte bilingue non è mai soddisfatto; va segnalato."""
    sbagliata = regola([{"campo": "regione", "operatore": "in", "valori": ["Trentino-Alto Adige"]},
                        {"campo": "comune_ateneo", "operatore": "in", "valori": ["Bolzano/Bozen"]}])
    assert GEOGRAFIA in tipi(sbagliata, "")
    giusta = regola([{"campo": "regione", "operatore": "in", "valori": ["Trentino-Alto Adige/Südtirol"]},
                     {"campo": "provincia_ateneo", "operatore": "in", "valori": ["Catania"]}])
    assert GEOGRAFIA not in tipi(giusta, "")
