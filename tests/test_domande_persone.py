"""Il questionario adattivo per le persone (data/domande_persone.yaml) è coerente con lo schema e con sé stesso."""
import json
from pathlib import Path

import yaml

from pipeline.motore import verifica

ROOT = Path(__file__).resolve().parent.parent
DOMANDE = yaml.safe_load((ROOT / "data" / "domande_persone.yaml").read_text(encoding="utf-8"))["domande"]
SCHEMA = json.loads((ROOT / "schema" / "regola.schema.json").read_text(encoding="utf-8"))["$defs"]
CAMPI_SCHEMA = {c for d in ("elenco", "numero", "booleano") for c in SCHEMA[d]["properties"]["campo"]["enum"]}
PERSONE_NO = {"tipologia", "dimensione", "settore", "ateco_2025", "ateco_2007", "ambito"}  # solo imprese


def test_ogni_campo_delle_persone_ha_una_domanda_e_viceversa():
    campi = {d["campo"] for d in DOMANDE} - {"nucleo"}
    assert campi <= CAMPI_SCHEMA, campi - CAMPI_SCHEMA
    assert CAMPI_SCHEMA - PERSONE_NO <= campi, CAMPI_SCHEMA - PERSONE_NO - campi


def test_le_condizioni_usano_campi_chiesti_prima():
    visti = set()
    for d in DOMANDE:
        for campo in (d.get("solo_se") or {}):
            assert campo in visti or any(x["campo"] == campo and x.get("ricavato") for x in DOMANDE), (d["campo"], campo)
        visti.add(d["campo"])


def test_i_campi_nuovi_funzionano_nel_motore():
    profilo = {"abitazione": "affitto", "contratto_locazione_registrato": True, "anni_residenza_regione": 6,
               "iscrizione": "universita", "crediti_conseguiti": 40, "numero_figli": 3, "tipo_lavoro": "autonomo"}
    assert verifica({"campo": "abitazione", "operatore": "in", "valori": ["affitto"]}, profilo) is True
    assert verifica({"campo": "contratto_locazione_registrato", "operatore": "vero"}, profilo) is True
    assert verifica({"campo": "anni_residenza_regione", "operatore": ">=", "valore": 5}, profilo) is True
    assert verifica({"campo": "numero_figli", "operatore": ">=", "valore": 4}, profilo) is False
    assert verifica({"campo": "ispe", "operatore": "<=", "valore": 50000}, profilo) is None  # non chiesto: mancano dati
