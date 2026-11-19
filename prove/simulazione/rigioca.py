"""Replay the demo questionnaire through /api/passo answering only from a frozen persona file, exactly like the UI does
(one question at a time). Usage: python rigioca.py <persona.yaml | persone.yaml> <base url> <out.json> [<id>]
docs/simulazione-demo.md, decisione 70."""
import json
import sys
import urllib.request

import yaml

NON_SO = "non lo so"
persona = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
if "persone" in persona:  # il file con tutte le persone: si sceglie per id
    persona = next(p for p in persona["persone"] if p["id"] == sys.argv[4])
base, uscita = sys.argv[2], sys.argv[3]
R = persona["risposte"]


def passo(profilo):
    req = urllib.request.Request(f"{base}/api/passo", data=json.dumps({"ramo": "persone", "profilo": profilo}).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))


profilo, domande = {}, []
for _ in range(80):
    out = passo(profilo)
    d = out["domanda"]
    if not d:
        break
    campo = d["campo"]
    domande.append(campo)
    if campo == "nucleo":
        profilo["nucleo"] = [{"eta": c["eta"]} for c in R["nucleo"]]
    elif campo.startswith("nucleo."):
        nome = campo.split(".")[1]
        profilo["nucleo"] = [dict(c) for c in profilo["nucleo"]]
        for c in d["componenti"]:
            profilo["nucleo"][c["indice"]][nome] = R["nucleo"][c["indice"]].get(nome, NON_SO)
    else:
        v = R.get(campo, NON_SO)
        if d["tipo"] in ("scelta", "comune", "si_no", "data") and isinstance(v, list):
            v = v[0]  # il codice di prima chiedeva una risposta sola
        profilo[campo] = v
json.dump({"persona": persona["id"], "domande": domande, "profilo": profilo, "conteggi": out["conteggi"],
           "risultati": out["risultati"], "giorno": out["giorno"]}, open(uscita, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(domande)} domande: {domande}")
print({k: v for k, v in out["conteggi"].items() if v})
