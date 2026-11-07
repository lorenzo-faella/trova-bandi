"""Bandi raccolti due volte: lo stesso bando pubblicato su due siti (es. Lazio Europa e Lazio Innova).

Non si cancella niente: sono due pagine vere, e una può avere il PDF che l'altra non ha. Si scrive l'elenco dei gruppi
in data/raw/elenchi/doppioni_<giorno>.json; per ogni gruppo il primo id è quello da tenere (quello con il PDF, se c'è).
Due bandi sono lo stesso bando se hanno lo stesso titolo normalizzato (minuscole, senza accenti né punteggiatura) e la
stessa regione. Titoli troppo generici ("Avviso pubblico") non bastano: servono almeno 4 parole.

Uso: python -m pipeline.fonti.doppioni
"""
import datetime as dt
import json
import re
import unicodedata
from collections import defaultdict

from pipeline.fonti import documenti as dc
from pipeline.fonti.elenchi import DIR_ELENCHI

MIN_PAROLE = 4


def chiave(titolo):
    t = unicodedata.normalize("NFKD", titolo or "").encode("ascii", "ignore").decode().lower()
    parole = re.sub(r"[^a-z0-9]+", " ", t).split()
    return " ".join(parole) if len(parole) >= MIN_PAROLE else None


def gruppi(documenti):
    per_chiave = defaultdict(list)
    for d in documenti:
        k = chiave(d.get("titolo"))
        if k:
            per_chiave[(d.get("regione"), k)].append(d)
    out = []
    for (regione, k), ds in per_chiave.items():
        if len({d["url"] for d in ds}) > 1:
            ds = sorted(ds, key=lambda d: (not d.get("allegato") and d.get("tipo") != "pdf", d["id"]))
            out.append({"regione": regione, "titolo": ds[0]["titolo"], "ids": [d["id"] for d in ds]})
    return sorted(out, key=lambda g: (g["regione"] or "", g["titolo"]))


def main():
    documenti = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(dc.USCITA.glob("*.json"))]
    g = gruppi(documenti)
    giorno = dt.date.today().isoformat()
    DIR_ELENCHI.mkdir(parents=True, exist_ok=True)
    (DIR_ELENCHI / f"doppioni_{giorno}.json").write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
    doppi = sum(len(x["ids"]) - 1 for x in g)
    print(f"{len(documenti)} documenti, {len(g)} bandi raccolti più volte, {doppi} doppioni: {len(documenti) - doppi} bandi diversi")


if __name__ == "__main__":
    main()
