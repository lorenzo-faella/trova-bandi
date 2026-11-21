"""Bandi per imprese ed enti raccolti dai siti (non da incentivi.gov.it): estrazione leggera e import (decisione 87).

La demo delle imprese legge solo l'open data del portale (`pipeline/regole.py`, `data/regole/`). Circa 230 bandi per
imprese e 170 per enti raccolti dai siti di regioni, finanziarie e Camere di commercio non ci sono. Per loro un LLM
legge le sezioni su beneficiari e termini (al massimo 5.000 caratteri) e scrive i requisiti con i campi delle imprese
(tipologia, dimensione, settore, regione, comune, ambito, ATECO 2025), ognuno con la sua citazione. Le istruzioni date
agli agenti sono in `docs/estrazione-imprese.md`.

Gli enti (comuni, associazioni, università) usano le tipologie del portale "Ente Pubblico", "Cooperative/Associazioni
Non Profit", "Università/Ente di Ricerca": per lo schema il pubblico resta "imprese".

Uso:
  python -m pipeline.estrai_imprese importa <risposte.json> [...]   scrive data/regole_imprese_documenti/<id>.yaml
                                                                     (o documenti-senza-requisiti se non ne ha)
  python -m pipeline.estrai_imprese controlla                       schema e citazioni delle regole già scritte
"""
import json
import sys
import time
from pathlib import Path

import yaml

from pipeline.estrai_documenti import documenti, errori
from pipeline.regole import DUMPER, ROOT
from pipeline.provenienza import registra, salva_snapshot

USCITA = ROOT / "data" / "regole_imprese_documenti"
SENZA = USCITA / "senza-requisiti"
AUTORE = "Claude Code, claude-opus-5-5"


def regola(doc, r):
    nuova = {"id": doc["id"], "titolo": doc["titolo"], "ente": doc["ente"], "link": doc["url"],
            "apertura": r.get("apertura"), "chiusura": r.get("chiusura"),
            "fonte": f"documento {doc['ente']}, estrazione leggera per imprese ed enti con LLM ({AUTORE}), non rivista",
            "pubblico": "imprese", "ultimo_controllo": time.strftime("%Y-%m-%d"),
            "requisiti": r.get("requisiti") or [],
            **({"note": r["note"]} if r.get("note") else {})}
    return registra(nuova, doc, None, AUTORE)  # prompt originale non fornito all'import: resta ignoto


def importa(file_risposte):
    risposte = {}
    for f in file_risposte:
        risposte.update(json.loads(Path(f).read_text(encoding="utf-8")))
    docs = {d["id"]: d for d in documenti(set(risposte))}
    USCITA.mkdir(parents=True, exist_ok=True)
    SENZA.mkdir(parents=True, exist_ok=True)
    conti = {"con requisiti": 0, "senza": 0, "altro pubblico": 0, "rifiutate": 0}
    for i, r in sorted(risposte.items()):
        if r.get("pubblico") in ("persone", "non_bando"):
            conti["altro pubblico"] += 1  # da rivedere: per le persone va estratto con pipeline.estrai_documenti
            print(f"  {r['pubblico']:9} {i}")
            continue
        reg = regola(docs[i], r)
        trovati = errori(reg, docs[i])
        if trovati:
            conti["rifiutate"] += 1
            print(f"RIFIUTATA {i}:\n  " + "\n  ".join(trovati))
            continue
        dove = USCITA if reg["requisiti"] else SENZA
        salva_snapshot(reg, docs[i], USCITA / "fonti")
        (dove / f"{i}.yaml").write_text(yaml.dump(reg, Dumper=DUMPER, allow_unicode=True, sort_keys=False, width=120),
                                        encoding="utf-8")
        conti["con requisiti" if reg["requisiti"] else "senza"] += 1
    print(conti)
    return conti["rifiutate"]


def controlla():
    docs = {d["url"]: d for d in documenti()}
    sbagliate = 0
    for f in sorted(USCITA.rglob("*.yaml")):
        reg = yaml.safe_load(f.read_text(encoding="utf-8"))
        trovati = errori(reg, docs[reg["link"]]) if reg["link"] in docs else ["link senza documento"]
        if trovati:
            sbagliate += 1
            print(f"ERRORE {f}\n  " + "\n  ".join(trovati))
    print(f"{len(list(USCITA.rglob('*.yaml'))) - sbagliate} regole valide, {sbagliate} con errori")
    return sbagliate


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["importa"] and len(a) > 1:
        sys.exit(1 if importa(a[1:]) else 0)
    if a == ["controlla"]:
        sys.exit(1 if controlla() else 0)
    sys.exit(__doc__)
