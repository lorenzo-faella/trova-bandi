"""Sezioni dei bandi sui requisiti, sui tre stili trovati nei PDF veri (Toscana, Lombardia, Genova)."""
from pipeline import estrai_documenti as ed
from pipeline.fonti import sezioni as sz

TOSCANA = {"pagine": [
    "BANDO BIOTRITURATORI 2026\nART. 1 – OGGETTO DEL BANDO\nContributi nei seguenti 31 comuni: Firenze, Prato.",
    "ART. 2 – SOGGETTI BENEFICIARI E REQUISITI\nPersone fisiche proprietarie di terreni nei comuni di cui all’articolo 1.1.\n"
    "ART. 3 – SPESE AMMISSIBILI\nContributo massimo 1.200 euro.\n"
    "ART. 4 – MODALITÀ DI PRESENTAZIONE\nDomande dal 25/05/2026 al 30/04/2027.",
    "ART. 8 – OBBLIGHI DEI BENEFICIARI\nConservare la fattura per 5 anni.\n"
    "ART. 11 – TRATTAMENTO DEI DATI PERSONALI\nI dati sono trattati ai sensi del GDPR."]}

LOMBARDIA = {"pagine": [
    "Allegato A\nPremessa\nIl Sistema Dote Scuola è rivolto direttamente alla persona.\nBeneficiari\n"
    "Studenti residenti in Lombardia, iscritti a scuole paritarie\nRisorse disponibili\nLo stanziamento è di 30 milioni.\n"
    "Requisiti di reddito e valore economico del contributo\nISEE fino a 40.000 euro",
    "Allegato A\nsecondo la tabella seguente.\nModalità di erogazione\nTramite il soggetto incaricato.\n"
    "Beneficiari\nAlunni con disabilità certificata residenti in Lombardia"]}

GENOVA = {"pagine": [
    "BANDO ANNO 2026 FONDO SOCIALE AFFITTI\nPossono partecipare i conduttori di alloggi in locazione.\n"
    "Il richiedente deve essere in possesso dei seguenti requisiti:\na) Residenza nel Comune di Genova.",
    "Contributi\nIl contributo massimo è 2.400 euro.\nDomanda di partecipazione e termine di presentazione\n"
    "Entro il 31 marzo 2026.\nAllegati obbligatori\n1. Copia del documento di identità."]}


def titoli(doc):
    e = sz.estratto(doc)
    return e and e["titoli"]


def test_riconosce_i_titoli_nei_tre_stili():
    assert sz.e_titolo("ART. 2 – SOGGETTI BENEFICIARI E REQUISITI") == (True, 2)
    assert sz.e_titolo("Articolo 5 - Cause di esclusione") == (True, 5)
    assert sz.e_titolo("Requisiti di reddito e valore economico del contributo") == (True, None)
    assert sz.e_titolo("2. REQUISITI DI ACCESSO")[0]
    # frasi del testo, non titoli: troppo lunghe, con punteggiatura finale, o che non cominciano come un titolo
    assert not sz.e_titolo("Destinatari diretti della misura sono le Scuole paritarie di ogni Ordine e Grado, aventi")[0]
    assert not sz.e_titolo("Il richiedente deve essere in possesso dei seguenti requisiti:")[0]
    assert not sz.e_titolo("a) Residenza nel Comune di Genova.")[0]


def test_toscana_requisiti_termini_e_articolo_richiamato():
    t = titoli(TOSCANA)
    assert "ART. 2 – SOGGETTI BENEFICIARI E REQUISITI" in t
    assert "ART. 4 – MODALITÀ DI PRESENTAZIONE" in t          # le date
    assert "ART. 1 – OGGETTO DEL BANDO" in t                   # richiamato dall'art. 2: contiene l'elenco dei comuni
    assert "ART. 8 – OBBLIGHI DEI BENEFICIARI" not in t        # dice "beneficiari", ma riguarda il dopo
    assert not any("TRATTAMENTO" in x or "SPESE" in x for x in t)


def test_lombardia_intestazione_di_pagina_non_taglia_la_sezione():
    e = sz.estratto(LOMBARDIA)
    assert e["titoli"] == ["Beneficiari", "Requisiti di reddito e valore economico del contributo", "Beneficiari"]
    testo = "\n".join(t for _, t in e["pezzi"])
    assert "secondo la tabella seguente." in testo   # continua a pagina 2 dopo "Allegato A"
    assert "Lo stanziamento" not in testo and "Tramite il soggetto incaricato" not in testo


def test_genova_senza_titolo_usa_l_inizio_del_testo():
    assert titoli(GENOVA) == ["(inizio del documento)", "Domanda di partecipazione e termine di presentazione"]


def test_senza_sezione_sui_requisiti_si_usa_tutto():
    doc = {"pagine": ["Premessa\nUn testo qualsiasi.\nContributi\nFino a 500 euro.\nModalità di presentazione\nOnline."]}
    assert sz.estratto(doc) is None
    scelti, t = ed.pezzi({**doc, "id": "x", "titolo": "x", "ente": "x"})
    assert t is None and scelti == [(1, doc["pagine"][0])]


def test_le_sezioni_tengono_il_numero_di_pagina_giusto():
    e = sz.estratto(TOSCANA)
    assert [p for p, _ in e["pezzi"]] == [1, 2]
    assert e["caratteri"] < e["totale"]


def test_prompt_dice_quali_sezioni_ha_ricevuto():
    doc = {**TOSCANA, "id": "t", "titolo": "Biotrituratori", "ente": "Regione Toscana"}
    p = ed.prompt(doc)
    assert "ART. 2 – SOGGETTI BENEFICIARI E REQUISITI" in p and "Conservare la fattura" not in p
    assert "Conservare la fattura" in ed.prompt(doc, tutto=True)


# Decisione 62: frasi andate a capo nei PDF scambiate per titoli (il bando del Comune di Lucca perdeva l'articolo 1).
LUCCA = {"pagine": [
    "Bando caro energia\nDescrizione\nIl Comune ha pubblicato un bando.\n"
    "ARTICOLO 1. DESTINATARI E REQUISITI\n"
    "Possono partecipare al bando per l’erogazione dei contributi i nuclei\n"
    "familiari che risultino essere in possesso dei seguenti requisiti:\n"
    "• avere un indicatore ISEE non superiore a € 28.000,00;\n"
    "ARTICOLO 2 . TERMINI E MODALITA’ DI PRESENTAZIONE\nDal 04/11/2026 al 23/11/2026.\n"
    "ARTICOLO 3 . COMUNICAZIONE ESITO ISTANZA\nL'esito si vede nella pagina della\n"
    "presentazione della domanda, nei dati dell'istanza.\n"
    "ARTICOLO 5 . ALTRE DISPOSIZIONI\nNessuna."]}


def test_lucca_la_frase_andata_a_capo_non_taglia_l_articolo():
    e = sz.estratto(LUCCA)
    assert e["titoli"] == ["ARTICOLO 1. DESTINATARI E REQUISITI", "ARTICOLO 2 . TERMINI E MODALITA’ DI PRESENTAZIONE"]
    testo = "\n".join(t for _, t in e["pezzi"])
    assert "28.000,00" in testo
    assert "nei dati dell'istanza" not in testo   # "presentazione della domanda, ..." in minuscolo non è un titolo


def test_titoli_veri_che_vanno_a_capo_o_aprono_un_elenco():
    doc = {"pagine": [
        "Premessa\nTesto.\n4.2 REQUISITI DI AMMISSIBILITÀ\na) Forma giuridica\nb) Sede in Toscana\n"
        "1. Requisiti del soggetto proponente e dell’eventuale\naderente\nIscrizione al registro.\n"
        "ART. 6\nREQUISITI DI PARTECIPAZIONE\nResidenza in Lombardia.\n"
        "Chi può\npartecipare: i residenti.\nRisorse\nDue milioni."]}
    t = sz.estratto(doc)["titoli"]
    assert "4.2 REQUISITI DI AMMISSIBILITÀ" in t                       # seguito da un elenco "a)"
    assert "1. Requisiti del soggetto proponente e dell’eventuale" in t  # numerata, anche se va a capo
    assert "ART. 6 REQUISITI DI PARTECIPAZIONE" in t                   # il sottotitolo si unisce all'articolo
    assert "Chi può" in t
    assert "Risorse" not in t


def test_requisiti_per_l_erogazione_non_e_una_sezione_del_dopo():
    doc = {"pagine": ["Art. 3 Requisiti per l'erogazione del contributo\nISEE fino a 20.000 euro.\n"
                      "Art. 9 Obblighi dei beneficiari\nConservare le fatture."]}
    assert sz.estratto(doc)["titoli"] == ["Art. 3 Requisiti per l'erogazione del contributo"]


# Decisione 66: il sommario dei bandi lunghi preso per titoli (LazioDisco: il modello ha visto solo l'indice) e le
# tabelle in appendice richiamate dagli articoli (ERSU Catania: i limiti ISEE e ISPE stanno nella tab. 6).
DSU = {"pagine": [
    "BANDO DIRITTO ALLO STUDIO 2026/2027\nINDICE\n"
    "Art. 1 Finalità ................................ 3\n"
    "Art.4 Destinatari dei benefici 14\n"
    "Art.8 Requisiti economici 33\n"
    "Art.9 Requisiti di merito 35\n"
    "Art.21 Criteri di determinazione degli importi 40\n",
    "Art. 1 Finalità\nIl bando assegna borse di studio.\n"
    "Art. 4 Destinatari dei benefici\nGli studenti iscritti alle istituzioni della tab. 1.\n"
    "Art. 8 Requisiti economici\nSono esclusi gli studenti con ISEE o ISPE oltre i limiti della tab.6 in appendice.\n"
    "Art. 21 Criteri di determinazione degli importi\nGli importi sono nella tabella 9.\n",
    "Tab. 1 – Elenco istituzioni universitarie afferenti l’ERSU\nUniversità di Catania\nAccademia di Belle Arti\n"
    "Tab. 6 – Requisito economico-patrimoniale\nISEE € 25.000,00\nISPE € 60.000,00\n"
    "Tab. 9 – Importi della borsa di studio\nIn sede € 2.000,00"]}


def test_il_sommario_non_apre_sezioni_e_non_si_manda():
    assert len(sz.sommario(DSU)) == 5
    e = sz.estratto(DSU)
    testo = "\n".join(t for _, t in e["pezzi"])
    assert "....." not in testo and "Destinatari dei benefici 14" not in testo
    assert "Art. 4 Destinatari dei benefici" in e["titoli"] and "Art. 8 Requisiti economici" in e["titoli"]
    assert "(inizio del documento)" not in e["titoli"]   # l'indice non basta a far scegliere l'inizio
    assert "Art. 1 Finalità" not in e["titoli"]          # e non richiama più tutti gli articoli


def test_un_titolo_che_finisce_con_un_numero_da_solo_non_e_sommario():
    doc = {"pagine": ["Art. 2 Requisiti previsti dalla legge regionale 15\nResidenza in Liguria."]}
    assert sz.sommario(doc) == set()
    assert sz.estratto(doc)["titoli"] == ["Art. 2 Requisiti previsti dalla legge regionale 15"]


def test_le_tabelle_richiamate_arrivano_al_modello():
    e = sz.estratto(DSU)
    assert e["titoli"][-2:] == ["Tab. 1 – Elenco istituzioni universitarie afferenti l’ERSU",
                                "Tab. 6 – Requisito economico-patrimoniale"]
    testo = "\n".join(t for _, t in e["pezzi"])
    assert "ISPE € 60.000,00" in testo and "Università di Catania" in testo
    assert "In sede € 2.000,00" not in testo   # tab. 9: la richiama solo l'articolo sugli importi, che non si manda


def test_tab_5_richiama_le_sottotabelle_e_tabella_a_inizio_frase_non_e_un_titolo():
    doc = {"pagine": ["Art. 9 Requisiti di merito\nI crediti minimi sono nella tab. 5, come da\n"
                      "tabella 4 in appendice.\nArt. 10 Trattamento dei dati\nGDPR.\n",
                      "Tab. 5.1 - Requisito di merito laurea triennale\n2° anno: 25 crediti\n"
                      "Tabella 5.2 - Requisito di merito laurea magistrale\n2° anno: 30 crediti\n"
                      "Tab. 7 – Nucleo familiare\nTesto."]}
    assert set(sz.tabelle(doc)) == {"5.1", "5.2", "7"}
    e = sz.estratto(doc)
    testo = "\n".join(t for _, t in e["pezzi"])
    assert "25 crediti" in testo and "30 crediti" in testo and "Nucleo familiare" not in testo
