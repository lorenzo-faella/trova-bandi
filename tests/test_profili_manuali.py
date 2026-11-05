"""Test differenziale: gli idonei calcolati dalla pipeline (normalizza -> regole -> motore) devono coincidere
con quelli di una seconda implementazione minima che legge direttamente l'export grezzo.
La seconda implementazione è volutamente ingenua e non importa nulla dalla pipeline.
"""
import html
import json
import re

import pytest
import yaml

from pipeline.motore import IDONEO, valuta_tutte
from pipeline.normalizza import REGIONI
from pipeline.profili import DISTRIBUZIONI, Generatore
from tests.conftest import GIORNO


def idonei_dal_grezzo(docs, p):
    out = set()
    for d in docs:
        a, c = (d.get("Data_apertura") or "")[:10], (d.get("Data_chiusura") or "")[:10]
        if (a and a > GIORNO) or (c and c < GIORNO):
            continue
        if p["regione"] not in d["Regioni"] or p["dimensione"] not in d["Dimensioni"]:
            continue
        if not set(p["tipologia"]) & set(d["Tipologia_Soggetto"]):
            continue
        if d.get("Settore_Attivita") and not set(p["settore"]) & set(d["Settore_Attivita"]):
            continue
        testo = d.get("Codici_ATECO") or ""
        codici = re.findall(r"\b\d{2}(?:\.\d{1,2}){0,2}\b", testo)
        if codici and not testo.startswith("Tutti"):
            if "ATECO 2025" not in testo and ("ATECO 2007" in testo or a < "2025-04-01"):
                continue  # codici 2007: con un codice 2025 non si può dire, quindi non è "idoneo"
            if not any(p["ateco_2025"].replace(".", "").startswith(k.replace(".", "")) for k in codici):
                continue
        comuni = [x.strip().lower() for x in html.unescape(d.get("Comuni") or "").split(";") if x.strip()]
        if comuni and not comuni[0].startswith("tutti") and p["comune"].lower() not in comuni:
            continue
        ambiti = [x for x in (d.get("Ambito_territoriale") or []) if x != "Non applicabile"]
        if ambiti and not set(p["ambito"]) & set(ambiti):
            continue
        out.add(str(d["ID_Incentivo"]))
    return out


@pytest.fixture(scope="module")
def docs(export_grezzo):
    return json.loads(export_grezzo.read_text(encoding="utf-8"))


def test_valori_dei_profili_esistono(manuali):
    # Un errore di battitura (o una virgola in una lista YAML) creerebbe un'impresa che non esiste
    d = yaml.safe_load(DISTRIBUZIONI.read_text(encoding="utf-8"))
    settori = set(d["settori"]) | {"Artigianato"}
    for nome, p in manuali.items():
        assert p["regione"] in REGIONI, nome
        assert set(p["settore"]) <= settori, nome
        assert set(p["ambito"]) <= set(d["ambiti"]), nome
        assert p["dimensione"] in set(d["dimensione"]) | {"Non classificabile/classificato"}, nome
        assert re.fullmatch(r"\d{2}\.\d{2}", p["ateco_2025"]), nome


def test_profili_manuali_coincidono_col_grezzo(regole, manuali, docs):
    for nome, p in manuali.items():
        motore = {e.regola["id"] for e in valuta_tutte(regole, p, GIORNO) if e.stato == IDONEO}
        assert motore == idonei_dal_grezzo(docs, p), nome


def test_profili_casuali_coincidono_col_grezzo(regole, docs):
    for p in Generatore(regole, seed=5).campione(40):
        motore = {e.regola["id"] for e in valuta_tutte(regole, p, GIORNO) if e.stato == IDONEO}
        assert motore == idonei_dal_grezzo(docs, p), p
