from pipeline.normalizza import ateco, chiave_comune, lista, stato


def test_lista_entita_html_non_spezza_i_nomi():
    assert lista("Sant&apos;Agata Feltria; Rimini") == ["Sant'Agata Feltria", "Rimini"]


def test_lista_valori_vuoti():
    assert lista(None) == []
    assert lista(["None", " ", "Lazio"]) == ["Lazio"]


def test_ateco_tutti():
    assert ateco("Tutti i settori economici ammissibili a ricevere aiuti;", "2024-01-01")["tutti"]


def test_ateco_versione_dichiarata():
    a = ateco("ATECO 2025: 56.10; 56.21;", "2020-01-01")
    assert a["codici"] == {"2025": ["56.10", "56.21"]}


def test_ateco_senza_etichetta_usa_la_data_di_apertura():
    assert ateco("90.01; 90.02;", "2024-06-01")["codici"] == {"2007": ["90.01", "90.02"]}
    assert ateco("90.01; 90.02;", "2025-05-01")["codici"] == {"2025": ["90.01", "90.02"]}


def test_ateco_due_versioni_e_duplicati():
    a = ateco("ATECO 2007: 55.90; 55.90; ATECO 2025: 55.90; 56.1", "2025-06-01")
    assert a["codici"] == {"2007": ["55.90"], "2025": ["55.90", "56.1"]}


def test_ateco_testo_senza_codici_non_viene_perso():
    a = ateco("Non applicabile", "2025-06-01")
    assert a["tutti"] and a["non_riconosciuti"] == ["Non applicabile"]


def test_ateco_codice_con_descrizione():
    assert ateco("13.10.00 Industrie tessili", "2023-01-01")["codici"] == {"2007": ["13.10.00"]}


def test_stato_estremi_inclusi():
    assert stato("2026-10-27", "2026-12-01", "2026-10-27") == "aperto"
    assert stato("2026-01-01", "2026-10-27", "2026-10-27") == "aperto"
    assert stato("2026-01-01", "2026-10-26", "2026-10-27") == "chiuso"
    assert stato("2026-10-28", None, "2026-10-27") == "non ancora aperto"
    assert stato(None, None, "2026-10-27") == "aperto (senza scadenza)"


def test_chiave_comune():
    assert chiave_comune("Forlì") == chiave_comune("FORLI'") == chiave_comune("forli")
    assert chiave_comune("Bolzano/Bozen") == chiave_comune("Bolzano")
    assert chiave_comune("Sant'Agata Feltria") == chiave_comune("Sant Agata Feltria")


def test_link_del_vecchio_sito_del_ministero():
    from pipeline.normalizza import link
    assert link("https://www.mise.gov.it/index.php/it/incentivi/credito-d-imposta-r-s") == \
        "https://www.mimit.gov.it/index.php/it/incentivi/credito-d-imposta-r-s"
    assert link("http://mise.gov.it/it/incentivi") == "https://www.mimit.gov.it/it/incentivi"
    assert link("https://uibm.mise.gov.it/index.php/it/") == "https://uibm.mise.gov.it/index.php/it/"  # altro sito
    assert link("https://www.comune.torino.it/bandi ") == "https://www.comune.torino.it/bandi"
    assert link("") is None and link(None) is None
