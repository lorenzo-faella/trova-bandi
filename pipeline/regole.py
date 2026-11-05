"""Stadio 3: bandi normalizzati -> un file di regole YAML per bando, validato con schema/regola.schema.json.

Solo i bandi non chiusi e aperti ad almeno un tipo di impresa. Un requisito viene scritto solo se esclude
qualcuno: un bando aperto a tutte le regioni non ha il requisito "regione".
Uso: python -m pipeline.regole
"""
import json
import sys
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
