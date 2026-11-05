"""L'estrattore con un modello finto: si prova ciò che gli gira intorno, non la bravura del modello."""
import json

import pytest

from pipeline.estrai import ESEMPI, carica_schede, esempi, estrai, istruzioni, leggi_risposta, obiettivi, richiesta, vocabolario
from pipeline.regole import DIR_PERSONE

SCHEDA = {"titolo": "Bonus", "sezioni": {"destinatari": "Spetta a chi ha un ISEE non superiore a 40.000 euro."}}
OBIETTIVO = {"id": "prova", "titolo": "Bonus", "link": "https://esempio.it"}
BUONO = {"campo": "isee", "operatore": "<=", "valore": 40000, "fonte": "scheda INPS, A chi è rivolto",
         "citazione": "ISEE non superiore a 40.000 euro"}


class Finto:
    """Risponde con le risposte date, in ordine, e ricorda cosa ha ricevuto."""

    def __init__(self, *risposte):
        self.risposte, self.chiamate = list(risposte), []

    def __call__(self, system, messaggi):
        self.chiamate.append((system, [dict(m) for m in messaggi]))
        return self.risposte.pop(0)


def js(*requisiti):
    return json.dumps({"requisiti": list(requisiti)}, ensure_ascii=False)


def test_regola_buona_al_primo_tentativo():
    regola, n, errori = estrai(OBIETTIVO, SCHEDA, Finto(js(BUONO)), "finto")
    assert n == 1 and not errori and regola["requisiti"] == [BUONO]
    assert "estratta con LLM (finto), non rivista" in regola["fonte"]


def test_citazione_inventata_rifiutata_e_corretta():
    finto = Finto(js({**BUONO, "citazione": "ISEE fino a 40.000 euro"}), js(BUONO))
    regola, n, errori = estrai(OBIETTIVO, SCHEDA, finto, "finto")
    assert n == 2 and not errori and regola["requisiti"] == [BUONO]
    ultimo = finto.chiamate[1][1][-1]
    assert ultimo["role"] == "user" and "assente dalla fonte" in ultimo["content"]


def test_campo_inesistente_rifiutato():
    finto = Finto(js({**BUONO, "campo": "stipendio"}), js(BUONO))
    assert estrai(OBIETTIVO, SCHEDA, finto, "finto")[1] == 2


def test_dopo_troppi_tentativi_restano_gli_errori():
    male = js({**BUONO, "citazione": "inventata"})
    _, n, errori = estrai(OBIETTIVO, SCHEDA, Finto(male, male, male), "finto")
    assert n == 3 and "assente dalla fonte" in errori[0]


@pytest.mark.parametrize("testo", ["non è json", "[1, 2]", "42"])
def test_risposta_illeggibile_non_si_ferma(testo):
    regola, n, errori = estrai(OBIETTIVO, SCHEDA, Finto(testo, js(BUONO)), "finto")
    assert n == 2 and not errori and regola["requisiti"] == [BUONO]


def test_nessun_requisito_e_una_risposta_valida_con_le_note():
    risposta = json.dumps({"requisiti": [], "note": ["la scheda rimanda a un bando"]})
    regola, _, errori = estrai(OBIETTIVO, SCHEDA, Finto(risposta), "finto")
    assert not errori and regola["note"] == ["la scheda rimanda a un bando"]


def test_blocco_di_codice():
    assert leggi_risposta('Ecco:\n```json\n{"requisiti": []}\n```') == {"requisiti": []}


@pytest.mark.parametrize("beneficio", ESEMPI + ["inps-bonus-nuovi-nati"])
def test_gli_esempi_non_contengono_mai_la_soluzione(beneficio):
    testo = esempi(beneficio)
    assert f"id: {beneficio}\n" not in testo
    assert testo.count("\nrequisiti:") == 2
    assert f"id: {beneficio}\n" not in istruzioni(beneficio)


def test_il_vocabolario_non_suggerisce_quali_campi_usare():
    v = vocabolario()
    assert "Usato da" not in v and "NASpI |" not in v and "Scelte da discutere" not in v
    assert "`isee`" in v and "`figlio_a_carico`" in v


def test_il_prompt_non_contiene_i_benefici_da_etichettare():
    """I 15 benefici etichettati a mano devono restare fuori dagli esempi, o la misura non vale."""
    for persona in ("lorenzo", "edo"):
        for o in obiettivi(f"data/gold/{persona}"):
            assert o["id"] not in ESEMPI
            assert o["link"] not in istruzioni("nessuno")


def test_la_scheda_e_delimitata_come_dato():
    testo = richiesta({"titolo": 'Un "bonus"', "sezioni": {"cosa": "testo"}})
    assert testo.startswith("<scheda") and testo.endswith("</scheda>") and "## Cos'è" in testo


def test_ogni_obiettivo_ha_la_sua_scheda():
    schede = carica_schede()
    cartelle = [DIR_PERSONE, "data/gold/lorenzo", "data/gold/edo"]
    assert all(o["link"] in schede for c in cartelle for o in obiettivi(c))
