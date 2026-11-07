"""Controllo dopo una raccolta: i documenti salvati sono quanti le voci dell'elenco del giorno?

Per ogni fonte confronta data/raw/elenchi/<fonte>_<giorno>.json con i documenti di data/raw/documenti/ che hanno
quella fonte_elenco, e segnala:
  - mancanti: voci dell'elenco senza documento (download fallito, oppure due bandi con lo stesso id: il secondo ha
    sovrascritto il primo, com'è successo con i titoli tagliati, decisione 33);
  - più file per una voce: lo stesso indirizzo salvato con due id (per esempio perché il titolo è cambiato);
  - fuori elenco: documenti della fonte il cui indirizzo oggi non è nell'elenco (bando chiuso, o id vecchio).

Uso: python -m pipeline.fonti.conta [fonte ...] [--giorno AAAA-MM-GG]     senza fonti, tutte quelle del giorno
"""
import collections
import datetime as dt
import json
import sys

from pipeline.fonti import documenti as dc
from pipeline.fonti.elenchi import DIR_ELENCHI


def controlla(elenco, documenti):
    """{voci, salvati, mancanti, doppi, fuori_elenco} per una fonte; documenti = quelli con la sua fonte_elenco."""
    voci = {b["url"] for b in elenco["bandi"]}
    per_url = collections.defaultdict(list)
    for d in documenti:
        per_url[d["url"]].append(d["id"])
    return {"voci": len(voci), "salvati": sum(1 for u in voci if u in per_url),
            "mancanti": sorted(u for u in voci if u not in per_url),
            "doppi": {u: sorted(ids) for u, ids in per_url.items() if u in voci and len(ids) > 1},
            "fuori_elenco": sorted(i for u, ids in per_url.items() if u not in voci for i in ids)}


def main(fonti, giorno):
    documenti = collections.defaultdict(list)
    for f in dc.USCITA.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:  # file a metà: una raccolta lo sta scrivendo adesso
            print(f"?   {f.name}: non leggibile, forse in scrittura")
            continue
        documenti[d.get("fonte_elenco")].append(d)
    file_elenchi = sorted(f for f in DIR_ELENCHI.glob(f"*_{giorno}.json") if not f.name.startswith("doppioni_"))
    problemi = 0
    for f in file_elenchi:
        elenco = json.loads(f.read_text(encoding="utf-8"))
        if fonti and elenco["fonte"] not in fonti:
            continue
        r = controlla(elenco, documenti[elenco["fonte"]])
        segno = "ok " if r["salvati"] == r["voci"] and not r["doppi"] else "!! "
        problemi += segno == "!! "
        extra = f", {len(r['fuori_elenco'])} fuori elenco" if r["fuori_elenco"] else ""
        print(f"{segno} {elenco['fonte']}: {r['salvati']}/{r['voci']} salvati, {len(r['doppi'])} con più file{extra}")
        for u in r["mancanti"]:
            print(f"      manca: {u}")
        for u, ids in r["doppi"].items():
            print(f"      più file: {u} -> {', '.join(ids)}")
    return problemi


if __name__ == "__main__":
    a = sys.argv[1:]
    giorno = a[a.index("--giorno") + 1] if "--giorno" in a else dt.date.today().isoformat()
    fonti = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] != "--giorno")]
    main(fonti, giorno)
