"""Stadio 3: bandi normalizzati -> un file di regole YAML per bando, validato con schema/regola.schema.json.

Solo i bandi non chiusi e aperti ad almeno un tipo di impresa. Un requisito viene scritto solo se esclude
qualcuno: un bando aperto a tutte le regioni non ha il requisito "regione".
Uso: python -m pipeline.regole
"""
import csv
import io
import json
import re
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

import jsonschema
import yaml

from pipeline.normalizza import REGIONI

ROOT = Path(__file__).resolve().parent.parent
DIR_REGOLE = ROOT / "data" / "regole"
# Queste si scrivono e si rivedono a mano, quindi stanno in git; quelle delle imprese sono generate.
DIR_PERSONE = ROOT / "data" / "regole_persone"
SCHEMA = json.loads((ROOT / "schema" / "regola.schema.json").read_text(encoding="utf-8"))
# jsonschema.validate() ricostruisce il validatore a ogni chiamata: su 750 file costava 13 s
# il parser YAML in C (libyaml) è circa 10 volte più veloce di quello in Python puro
LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
DUMPER = getattr(yaml, "CSafeDumper", yaml.SafeDumper)
VALIDATORE = jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.FormatChecker())
TUTTE_DIMENSIONI = {"Microimpresa", "Piccola Impresa", "Media Impresa", "Grande Impresa",
                    "Non classificabile/classificato"}


# Le Camere di commercio sono provinciali: un loro bando è per le imprese della provincia (o delle province, se
# accorpate), ma l'open data scrive solo la regione. La provincia si ricava dal nome dell'ente. Nomi che non
# contengono quelli delle province:
CAMERE_ACCORPATE = {
    "maremma e del tirreno": ["Grosseto", "Livorno"], "venezia giulia": ["Trieste", "Gorizia"],
    "gran sasso": ["L'Aquila", "Teramo"], "irpinia sannio": ["Avellino", "Benevento"],
    "dell emilia": ["Parma", "Piacenza", "Reggio nell'Emilia"], "monza": ["Monza e della Brianza"],
    "reggio emilia": ["Reggio nell'Emilia"], "bolzano": ["Bolzano/Bozen"],
}


# Condizioni che incentivi.gov.it non scrive, trovate nella revisione a mano delle imprese (decisioni 106 e 109): senza,
# il bando risulta "compatibile" a imprese che non possono chiederlo. La demo le aggiunge come requisiti da verificare a
# mano, con la frase del bando riportata da chi l'ha rivisto (web/domande.py, ramo_imprese). Non stanno nei file
# generati, che hanno solo i campi del portale: su quelli lavorano questionario, profili e misure. Solo bandi rivisti.
CONDIZIONI_RIVISTE = {
    "90": [{  # Fondo Salvaguardia imprese
        "non_modellabile": "Solo imprese in difficoltà economico-finanziaria che soddisfano anche almeno una delle "
                           "altre condizioni del Fondo (elencate nella pagina del bando)",
        "citazione": "Il Fondo si rivolge alle imprese che presentano le seguenti due caratteristiche",
        "fonte": "pagina del bando, revisione a mano di Edoardo del 24/11 (decisione 106)"}],
    "813": [{  # CLLD progetti medi, Strategia Dolomiti Live
        "non_modellabile": "Il progetto deve coinvolgere almeno un partner italiano e uno austriaco (programma Interreg "
                           "VI-A Italia-Austria)",
        "citazione": "è necessario che ogni progetto coinvolga almeno un partner di entrambi gli Stati membri del "
                     "Programma di cooperazione Interreg VI-A Italia - Austria.",
        "fonte": "avviso del bando, revisione a mano di Edoardo del 24/11 (decisione 106)"}],
}


def semplice(testo):
    testo = unicodedata.normalize("NFKD", testo or "").encode("ascii", "ignore").decode().lower()
    return " " + re.sub(r"[^a-z]+", " ", testo).strip() + " "


@lru_cache(maxsize=None)
def province_istat():
    """Provincia (unità sovracomunale ISTAT) -> (regione, comuni)."""
    istat = sorted((ROOT / "data" / "raw").glob("istat_comuni_*.csv"))[-1]
    righe = csv.DictReader(io.StringIO(istat.read_bytes().decode("latin-1")), delimiter=";")
    prov = next(k for k in righe.fieldnames if k.startswith("Denominazione dell'Unità territoriale sovracomunale"))
    out = {}
    for r in righe:
        out.setdefault(r[prov], (r["Denominazione Regione"], []))[1].append(r["Denominazione in italiano"])
    return out


def province_della_camera(ente, regioni):
    """Le province di una Camera di commercio, fra quelle delle regioni del bando; [] se non si ricavano o se
    sono tutte quelle delle regioni (allora il vincolo di regione basta già). Le unioni regionali non hanno provincia."""
    nome = semplice(ente)
    if " camer" not in nome or " unione regionale " in nome:
        return []
    candidate = {p: r for p, (r, _) in province_istat().items() if r in regioni}
    trovate = {p for p in candidate if semplice(p.split("/")[0]) in nome}
    for chiave, province in CAMERE_ACCORPATE.items():
        if f" {chiave} " in nome:
            trovate |= {p for p in province if p in candidate}
    if not trovate or trovate == set(candidate):
        return []
    return sorted(trovate)


def requisito(campo, operatore, valori, campo_open_data, **extra):
    return {"campo": campo, "operatore": operatore, "valori": list(dict.fromkeys(valori)),
            "fonte": f"incentivi.gov.it, campo {campo_open_data}", **extra}


def regola(b, export):
    req, note = [], []
    if not b["nazionale"]:
        req.append(requisito("regione", "in", b["regioni"], "Regioni"))
    if b["comuni"] or b["comuni_non_riconosciuti"]:
        # Se l'elenco contiene nomi che non esistono più (comuni fusi), chi è fuori dall'elenco riconosciuto
        # non è escluso con certezza: il motore risponde "mancano dati" invece di "non idoneo".
        # I nomi soppressi restano nei valori: se l'elenco è fatto solo di quelli, il vincolo non deve sparire.
        req.append(requisito("comune", "in", b["comuni"] + b["comuni_non_riconosciuti"], "Comuni",
                             incerto_fuori_elenco=bool(b["comuni_non_riconosciuti"])))
    elif province_della_camera(b["ente"], [] if b["nazionale"] else b["regioni"]):
        province = province_della_camera(b["ente"], b["regioni"])
        comuni = sorted({c for p in province for c in province_istat()[p][1]})
        req.append({"campo": "comune", "operatore": "in", "valori": comuni,
                    "fonte": "incentivi.gov.it, campo Soggetto_Concedente: la Camera di commercio finanzia le imprese "
                             "con sede nella sua provincia (" + ", ".join(province) + ")"})
    if b["comuni_non_riconosciuti"]:
        note.append("comuni non presenti nell'elenco ISTAT: " + "; ".join(b["comuni_non_riconosciuti"]))
    req.append(requisito("tipologia", "interseca", b["tipologie"], "Tipologia_Soggetto"))
    if b["dimensioni"] and set(b["dimensioni"]) != TUTTE_DIMENSIONI:
        req.append(requisito("dimensione", "in", b["dimensioni"], "Dimensioni"))
    if b["settori"] and len(b["settori"]) < 21:
        req.append(requisito("settore", "interseca", b["settori"], "Settore_Attivita"))
    codici = b["ateco"]["codici"]
    # Con entrambe le versioni basta quella 2025, che è quella che le imprese hanno oggi.
    for versione in ("2025", "2007"):
        if codici.get(versione):
            req.append(requisito(f"ateco_{versione}", "prefisso", codici[versione], "Codici_ATECO"))
            break
    if b["ateco"]["non_riconosciuti"]:
        note.append("testo ATECO non interpretato: " + " | ".join(b["ateco"]["non_riconosciuti"]))
    if b["ambiti"]:
        req.append(requisito("ambito", "interseca", b["ambiti"], "Ambito_territoriale"))
    out = {"id": b["id"], "titolo": b["titolo"], "ente": b["ente"], "link": b["link"],
           "apertura": b["apertura"], "chiusura": b["chiusura"],
           "fonte": f"incentivi.gov.it open data (IODL 2.0), {export}", "requisiti": req}
    if note:
        out["note"] = note
    return out


def carica(cartella=DIR_REGOLE):
    """Tutte le regole, validate: un file che non rispetta lo schema ferma tutto."""
    regole = []
    for f in sorted(cartella.glob("*.yaml"), key=lambda p: int(p.stem) if p.stem.isdigit() else p.stem):
        r = yaml.load(f.read_text(encoding="utf-8"), Loader=LOADER)
        VALIDATORE.validate(r)
        regole.append(r)
    return regole


def main():
    dati = json.loads((ROOT / "data" / "processed" / "bandi.json").read_text(encoding="utf-8"))
    bandi = [b for b in dati["bandi"] if b["stato"] != "chiuso" and b["per_imprese"]]
    DIR_REGOLE.mkdir(parents=True, exist_ok=True)
    for vecchio in DIR_REGOLE.glob("*.yaml"):  # i file sono generati: si riscrivono da capo
        vecchio.unlink()
    for b in bandi:
        r = regola(b, dati["fonte"])
        VALIDATORE.validate(r)
        testo = yaml.dump(r, Dumper=DUMPER, allow_unicode=True, sort_keys=False, width=120)
        (DIR_REGOLE / f"{b['id']}.yaml").write_text(testo, encoding="utf-8")
    n = len(carica())
    print(f"{n} regole in {DIR_REGOLE.relative_to(ROOT)}, tutte valide rispetto allo schema")
    if n != len(bandi):
        sys.exit(f"attese {len(bandi)} regole, rilette {n}")


if __name__ == "__main__":
    main()
