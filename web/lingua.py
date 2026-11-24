"""Lingua della demo (decisione 105): italiano o inglese. Il server lavora in italiano; per una richiesta in inglese i
testi fissi (domande, etichette, aiuti, avvertenze, profili, colonne del grafico) si traducono con il dizionario di
data/traduzioni_en.yaml, e le frasi composte (requisiti, risposte) usano modelli inglesi in web/domande.py.
Non si traducono i contenuti delle fonti: titoli dei bandi, citazioni e testi scritti nelle regole restano come sono.
"""
import contextvars
from functools import lru_cache

import yaml

from pipeline.regole import ROOT

LINGUE = ("it", "en")
LINGUA = contextvars.ContextVar("lingua", default="it")
FILE = ROOT / "data" / "traduzioni_en.yaml"
# chiavi i cui valori sono codici, link o parole delle fonti (titoli dei bandi, enti): non si traducono mai, anche quando
# coincidono con una voce del dizionario (un bando intitolato "Ristorazione"). I titoli scritti da noi usano tr().
INTOCCABILI = {"id", "link", "url", "citazione", "titolo", "titoli", "ente", "chiave", "campo", "valore", "valori", "fonte", "regione", "comune",
               "stato", "gruppo", "stato_temporale", "origine", "icona", "faccina", "colore", "ramo", "note",
               "non_modellabile", "regione_da", "giorno", "giorno_folla", "versione_regola", "hash_file_originale",
               "identita_misura", "provenienza", "versioni_precedenti", "profilo", "conferme", "tipo", "esito"}


def inglese():
    return LINGUA.get() == "en"


@lru_cache(maxsize=None)
def dizionario():
    return yaml.safe_load(FILE.read_text(encoding="utf-8")) or {} if FILE.exists() else {}


def tr(testo):
    """Il testo nella lingua della richiesta: invariato in italiano, o se il dizionario non lo conosce."""
    if not inglese() or not isinstance(testo, str):
        return testo
    return dizionario().get(testo, testo)


def L(italiano, inglese_):
    """Un pezzo di frase composta: la versione nella lingua della richiesta."""
    return inglese_ if inglese() else italiano


def traduci(obj, chiave=None):
    """Una risposta JSON nella lingua della richiesta: si traducono le stringhe note, si saltano codici e fonti."""
    if not inglese() or chiave in INTOCCABILI:
        return obj
    if isinstance(obj, str):
        return dizionario().get(obj, obj)
    if isinstance(obj, list):
        return [traduci(x, chiave) for x in obj]
    if isinstance(obj, dict):
        return {k: traduci(v, k) for k, v in obj.items()}
    return obj
