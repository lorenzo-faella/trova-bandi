"""Controllo delle citazioni: ogni requisito di una regola per persone deve citare la fonte parola per parola.

È la difesa principale contro le regole inventate da un LLM: un requisito che cita un testo inesistente viene scartato
senza bisogno di leggerlo. Non dimostra che la regola sia giusta, solo che il testo citato esiste.

Uso: python -m pipeline.citazioni [cartella ...]    controlla schema e citazioni dei file YAML, anche nelle sottocartelle
"""
import json
import re
import sys
from pathlib import Path

import yaml

from pipeline.motore import figli
from pipeline.regole import DIR_PERSONE, LOADER, ROOT, VALIDATORE


def normalizza(testo):
    return re.sub(r"\s+", " ", testo).strip()


def nodi(req):
    yield req
    for q in figli(req):
        yield from nodi(q)


def problemi(regola, testo_fonte):
    """Lista vuota se la regola è a posto. Un requisito non modellabile può non citare: spesso segnala un'assenza."""
    fonte = normalizza(testo_fonte)
    out = []
    for i, req in enumerate(regola["requisiti"]):
        if "citazione" not in req and "non_modellabile" not in req:
            out.append(f"requisito {i}: manca la citazione")
        for nodo in nodi(req):
            citata = nodo.get("citazione")
            if citata and normalizza(citata) not in fonte:
                out.append(f"requisito {i}: citazione assente dalla fonte: {citata!r}")
    return out


def carica_testi_inps():
    """URL della scheda -> testo, dall'ultimo scarico."""
    files = sorted(f for f in (ROOT / "data" / "raw").glob("inps_schede_*.json") if not f.name.endswith(".meta.json"))
    if not files:
        sys.exit("manca lo scarico: python -m pipeline.fonti.inps")
    schede = json.loads(files[-1].read_text(encoding="utf-8"))
    return {s["url"]: "\n".join(s["sezioni"].values()) for s in schede}


def main(cartelle):
    testi = carica_testi_inps()
    buoni, vuoti, cattivi = 0, 0, 0
    for cartella in cartelle:
        for f in sorted(Path(cartella).rglob("*.yaml")):
            r = yaml.load(f.read_text(encoding="utf-8"), Loader=LOADER)
            errori = [e.message[:150] for e in VALIDATORE.iter_errors(r)]
            if r.get("link") not in testi:
                errori.append("la fonte non è tra le schede scaricate")
            elif not errori:
                errori = problemi(r, testi[r["link"]])
            if errori:
                cattivi += 1
                print(f"ERRORE {f}")
                for e in errori:
                    print(f"  {e}")
            elif not r["requisiti"]:
                vuoti += 1
            else:
                buoni += 1
    print(f"{buoni} regole valide, {vuoti} ancora da compilare, {cattivi} con errori")
    return cattivi


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:] or [DIR_PERSONE]) else 0)
